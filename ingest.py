"""
Document Ingestion Script
=========================
Run from project root:  python ingest.py

Loads all PDF + DOCX files from ./data/
Chunks at 512 tokens (tiktoken cl100k_base with 50-token overlap)
Embeds with BAAI/bge-small-en-v1.5
Stores in ChromaDB (local persistent, no Docker)

Context types (auto-detected from filename):
  - Audit      → files containing 'audit' or 'finding'
  - Regulation → files containing 'bulletin' or 'regulatory'
  - Policy     → everything else
"""
from __future__ import annotations

import hashlib
import logging
import re
import sys
import time
from pathlib import Path
from typing import List

# ── Add project root to path ──────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))


def _load_pdf(path: Path) -> str:
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages)


def _load_docx(path: Path) -> str:
    from docx import Document
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def load_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _load_pdf(path)
    if suffix in (".docx", ".doc"):
        return _load_docx(path)
    return path.read_text(encoding="utf-8", errors="ignore")


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """Token-aware chunking with tiktoken cl100k_base."""
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_str = enc.decode(tokens[start:end]).strip()
        if len(chunk_str) > 50:
            chunks.append(chunk_str)
        start += chunk_size - overlap
    return chunks


def _split_sentences(text: str) -> List[str]:
    """Simple sentence splitter for semantic chunking."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\(\[])", text)
    return [p.strip() for p in parts if p.strip()]


def semantic_chunk_text(
    text: str,
    embedder,
    max_tokens: int = 512,
    min_tokens: int = 120,
    similarity_threshold: float = 0.72,
) -> List[str]:
    """
    Semantic chunking by sentence cohesion.
    Splits when adjacent sentence similarity drops or max token size is reached.
    """
    import numpy as np
    import tiktoken

    sentences = _split_sentences(text)
    if not sentences:
        return []
    if len(sentences) == 1:
        return [sentences[0]] if len(sentences[0]) > 50 else []

    enc = tiktoken.get_encoding("cl100k_base")
    sent_vecs = embedder.encode(sentences, normalize_embeddings=True)
    sent_tokens = [len(enc.encode(s)) for s in sentences]

    chunks: List[str] = []
    current_sentences: List[str] = [sentences[0]]
    current_tokens = sent_tokens[0]

    for i in range(1, len(sentences)):
        sim = float(np.dot(sent_vecs[i - 1], sent_vecs[i]))
        next_tokens = sent_tokens[i]

        split_for_semantics = sim < similarity_threshold and current_tokens >= min_tokens
        split_for_size = (current_tokens + next_tokens) > max_tokens

        if split_for_semantics or split_for_size:
            chunk = " ".join(current_sentences).strip()
            if len(chunk) > 50:
                chunks.append(chunk)
            current_sentences = [sentences[i]]
            current_tokens = next_tokens
        else:
            current_sentences.append(sentences[i])
            current_tokens += next_tokens

    final_chunk = " ".join(current_sentences).strip()
    if len(final_chunk) > 50:
        chunks.append(final_chunk)
    return chunks


def infer_context_type(filename: str) -> str:
    name = filename.lower()
    if any(kw in name for kw in ["audit", "finding"]):
        return "Audit"
    if any(kw in name for kw in ["bulletin", "regulatory", "regulation"]):
        return "Regulation"
    return "Policy"


def ingest(data_dir: str = "./data", chroma_path: str = "./chroma_db") -> dict:
    """
    Ingest all compliance documents into ChromaDB.
    Returns { documents, chunks, duration }.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    log = logging.getLogger("ingest")

    from backend.config import (
        EMBEDDING_MODEL,
        CHROMA_COLLECTION_NAME,
        CHUNKING_MODE,
        CHUNK_SIZE,
        CHUNK_OVERLAP,
        SEMANTIC_SIMILARITY_THRESHOLD,
        SEMANTIC_MIN_CHUNK_TOKENS,
    )
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer

    data_path = Path(data_dir)
    doc_files = (
        list(data_path.glob("*.pdf"))
        + list(data_path.glob("*.docx"))
        + list(data_path.glob("*.doc"))
    )

    if not doc_files:
        log.error("No documents found in %s", data_dir)
        return {"documents": 0, "chunks": 0, "duration": 0}

    log.info("Found %d documents in %s", len(doc_files), data_dir)

    # ── Load embedding model ──────────────────────────────────────────────
    log.info("Loading embedding model: %s", EMBEDDING_MODEL)
    embedder = SentenceTransformer(EMBEDDING_MODEL)

    # ── Connect to ChromaDB ───────────────────────────────────────────────
    client = chromadb.PersistentClient(
        path=chroma_path,
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    total_chunks = 0
    start_time = time.time()

    for doc_path in doc_files:
        log.info("Processing: %s", doc_path.name)
        try:
            text = load_document(doc_path)
            if not text.strip():
                log.warning("  ⚠ Empty document — skipping: %s", doc_path.name)
                continue

            if CHUNKING_MODE.lower() == "semantic":
                chunks = semantic_chunk_text(
                    text,
                    embedder=embedder,
                    max_tokens=CHUNK_SIZE,
                    min_tokens=SEMANTIC_MIN_CHUNK_TOKENS,
                    similarity_threshold=SEMANTIC_SIMILARITY_THRESHOLD,
                )
            else:
                chunks = chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
            ctx_type = infer_context_type(doc_path.name)

            ids, embeddings, documents, metadatas = [], [], [], []
            for i, chunk in enumerate(chunks):
                chunk_id = hashlib.md5(
                    f"{doc_path.name}:{i}:{chunk[:40]}".encode()
                ).hexdigest()
                vec = embedder.encode(chunk, normalize_embeddings=True).tolist()
                ids.append(chunk_id)
                embeddings.append(vec)
                documents.append(chunk)
                metadatas.append(
                    {
                        "source": doc_path.name,
                        "chunk_index": i,
                        "context_type": ctx_type,
                        "total_chunks": len(chunks),
                        "doc_path": str(doc_path),
                    }
                )

            # Upsert in batches of 100 to avoid memory spikes
            batch = 100
            for b in range(0, len(ids), batch):
                collection.upsert(
                    ids=ids[b : b + batch],
                    embeddings=embeddings[b : b + batch],
                    documents=documents[b : b + batch],
                    metadatas=metadatas[b : b + batch],
                )

            total_chunks += len(chunks)
            log.info("  ✓ %d chunks  [%s]  %s", len(chunks), ctx_type, doc_path.name)

        except Exception as exc:
            log.error("  ✗ Failed %s: %s", doc_path.name, exc)

    elapsed = time.time() - start_time
    log.info(
        "\n✅ Ingestion complete — %d documents | %d chunks | %.1fs",
        len(doc_files), total_chunks, elapsed,
    )
    log.info("ChromaDB: %s  |  Collection: %s", chroma_path, CHROMA_COLLECTION_NAME)
    return {"documents": len(doc_files), "chunks": total_chunks, "duration": elapsed}


if __name__ == "__main__":
    ingest()
