"""
Configuration module — all environment variables and thresholds.
Never hardcode model names or values elsewhere; always read from here.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Google Gemini ─────────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = "gemini-3.1-flash-lite"

# ── Local HF Models (sensitive data stays here, never sent to Gemini) ─────────
EMBEDDING_MODEL: str = r"C:\Python\local_models\BAAI__bge-small-en-v1.5"
RERANKER_MODEL: str = r"C:\Python\local_models\BAAI__bge-reranker-base"

# ── Chunking Strategy ─────────────────────────────────────────────────────────
CHUNK_SIZE: int = 512        # tokens (tiktoken cl100k_base)
CHUNK_OVERLAP: int = 50      # tokens

# ── Retrieval ─────────────────────────────────────────────────────────────────
TOP_K_RETRIEVE: int = 20     # initial vector search count
TOP_K_RERANK: int = 5        # keep after cross-encoder reranking

# ── Confidence & Escalation ───────────────────────────────────────────────────
CONFIDENCE_THRESHOLD: float = 0.75
ESCALATION_MESSAGE: str = (
    "⚠️ Confidence below threshold (< 0.75). This query has been escalated to a "
    "Compliance Officer for human review. Please contact compliance@bank.com."
)

# ── RAGAS Minimum Pass Thresholds ────────────────────────────────────────────
RAGAS_FAITHFULNESS_MIN: float = 0.90
RAGAS_ANSWER_RELEVANCY_MIN: float = 0.80
RAGAS_CONTEXT_RECALL_MIN: float = 0.80
RAGAS_CONTEXT_PRECISION_MIN: float = 0.80

# ── ChromaDB (local persistent, no Docker) ───────────────────────────────────
CHROMA_DB_PATH: str = str(BASE_DIR / "chroma_db")
CHROMA_COLLECTION_NAME: str = "compliance_docs"

# ── Data Paths ────────────────────────────────────────────────────────────────
DATA_DIR: str = str(BASE_DIR / "data")
SYNTHETIC_DATA_DIR: str = str(BASE_DIR / "backend" / "data" / "synthetic")
GOLDEN_SET_PATH: str = str(
    BASE_DIR / "backend" / "data" / "golden_set" / "golden_qa.json"
)
EVAL_RESULTS_PATH: str = str(BASE_DIR / "backend" / "data" / "eval_results.json")

# ── FastAPI Server ────────────────────────────────────────────────────────────
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS: list = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# ── DDD Bounded Contexts ──────────────────────────────────────────────────────
CONTEXTS: list = ["Policy", "Audit", "Regulation"]

# ── Source Document Context Mapping ──────────────────────────────────────────
CONTEXT_KEYWORDS: dict = {
    "Policy": ["policy", "procedure", "standard", "kyc", "aml", "credit", "data privacy", "it security"],
    "Audit": ["audit", "finding", "observation", "q1", "q2", "q3", "q4"],
    "Regulation": ["regulatory", "bulletin", "regulation", "compliance", "rule"],
}
