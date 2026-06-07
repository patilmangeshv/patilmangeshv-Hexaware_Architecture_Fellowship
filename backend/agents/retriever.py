"""
Retriever Agent
===============
BGE-small-en-v1.5 embeddings → ChromaDB vector search → BGE-reranker-base.

Rules:
  - Always rerank after retrieval; never skip.
  - Sensitive data never leaves this module to an external API.
  - Models are lazy-loaded on first use (saves memory if not needed).
"""
from __future__ import annotations

import logging
from typing import List, Optional, Tuple

import chromadb
from chromadb.config import Settings
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from backend.config import (
    EMBEDDING_MODEL,
    RERANKER_MODEL,
    CHROMA_DB_PATH,
    CHROMA_COLLECTION_NAME,
    TOP_K_RETRIEVE,
    TOP_K_RERANK,
)

logger = logging.getLogger(__name__)


class RetrieverAgent:
    """
    Semantic search over the ChromaDB compliance knowledge base,
    followed by mandatory cross-encoder reranking.
    """

    _instance: Optional["RetrieverAgent"] = None

    def __init__(self) -> None:
        # ── ChromaDB (local, no Docker) ───────────────────────────────────
        self._client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "ChromaDB connected — path=%s  collection=%s  docs=%d",
            CHROMA_DB_PATH,
            CHROMA_COLLECTION_NAME,
            self._collection.count(),
        )

        # ── Lazy-loaded models ────────────────────────────────────────────
        self._embedder: Optional[SentenceTransformer] = None
        self._reranker_tok = None
        self._reranker_mdl = None

    # ── Singleton ────────────────────────────────────────────────────────────

    @classmethod
    def get_instance(cls) -> "RetrieverAgent":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── Private helpers ──────────────────────────────────────────────────────

    def _load_embedder(self) -> SentenceTransformer:
        if self._embedder is None:
            logger.info("Loading embedding model: %s", EMBEDDING_MODEL)
            self._embedder = SentenceTransformer(EMBEDDING_MODEL)
        return self._embedder

    def _load_reranker(self):
        if self._reranker_mdl is None:
            logger.info("Loading reranker model: %s", RERANKER_MODEL)
            self._reranker_tok = AutoTokenizer.from_pretrained(RERANKER_MODEL)
            self._reranker_mdl = AutoModelForSequenceClassification.from_pretrained(
                RERANKER_MODEL
            )
            self._reranker_mdl.eval()
        return self._reranker_tok, self._reranker_mdl

    def _embed(self, text: str) -> List[float]:
        return self._load_embedder().encode(text, normalize_embeddings=True).tolist()

    def _score_pairs(self, query: str, passages: List[str]) -> List[float]:
        tok, mdl = self._load_reranker()
        pairs = [[query, p] for p in passages]
        enc = tok(
            pairs,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )
        with torch.no_grad():
            logits = mdl(**enc).logits.view(-1).float()
        return torch.sigmoid(logits).cpu().numpy().tolist()

    # ── Public API ───────────────────────────────────────────────────────────

    def collection_count(self) -> int:
        return self._collection.count()

    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K_RETRIEVE,
        context_filter: Optional[str] = None,
    ) -> List[dict]:
        """
        Retrieve top-k semantically similar chunks.
        Optionally filter by DDD context: Policy | Audit | Regulation.
        """
        query_vec = self._embed(query)
        n = min(top_k, max(1, self._collection.count()))
        where = {"context_type": context_filter} if context_filter else None

        results = self._collection.query(
            query_embeddings=[query_vec],
            n_results=n,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        chunks: List[dict] = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append(
                {
                    "text": doc,
                    "metadata": meta,
                    "cosine_distance": dist,
                    "cosine_similarity": round(1.0 - dist, 4),
                }
            )
        logger.debug("Retrieved %d chunks for: %.60s", len(chunks), query)
        return chunks

    def rerank(
        self,
        query: str,
        chunks: List[dict],
        top_k: int = TOP_K_RERANK,
    ) -> List[dict]:
        """
        Cross-encoder reranking with BGE-reranker-base.
        ALWAYS called after retrieve() — never skipped.
        """
        if not chunks:
            return []

        passages = [c["text"] for c in chunks]
        scores = self._score_pairs(query, passages)
        for chunk, score in zip(chunks, scores):
            chunk["reranker_score"] = round(float(score), 4)

        reranked = sorted(chunks, key=lambda x: x["reranker_score"], reverse=True)
        top = reranked[:top_k]
        logger.debug(
            "Reranked → top-%d  best=%.3f",
            top_k,
            top[0]["reranker_score"] if top else 0,
        )
        return top

    def retrieve_and_rerank(
        self,
        query: str,
        top_k_retrieve: int = TOP_K_RETRIEVE,
        top_k_rerank: int = TOP_K_RERANK,
        context_filter: Optional[str] = None,
    ) -> Tuple[List[dict], float]:
        """
        Full pipeline: retrieve → rerank.

        Returns:
            (reranked_chunks, confidence)
            confidence = top reranker score (proxy for retrieval quality)
        """
        chunks = self.retrieve(query, top_k=top_k_retrieve, context_filter=context_filter)
        reranked = self.rerank(query, chunks, top_k=top_k_rerank)
        confidence = reranked[0]["reranker_score"] if reranked else 0.0
        return reranked, confidence
