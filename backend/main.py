"""
FastAPI Backend — Compliance Knowledge Agent
============================================
DDD bounded contexts: Policy | Audit | Regulation

Endpoints:
  POST /api/query          — Ask a compliance question
  POST /api/eval/run       — Run RAGAS evaluation on golden set
  GET  /api/eval/scores    — Fetch evaluation history
  POST /api/ingest         — Trigger document ingestion
  GET  /api/health         — Health check
  GET  /api/trust-canvas   — Trust Boundary Canvas + Failure Mode Register
  GET  /api/golden-set     — Return golden Q&A set

Start: uvicorn backend.main:app --reload --port 8000
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.config import (
    CORS_ORIGINS,
    CONTEXTS,
    DATA_DIR,
    CHROMA_DB_PATH,
    GOLDEN_SET_PATH,
    EVAL_RESULTS_PATH,
)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("main")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Compliance Knowledge Agent API",
    description="RAG-powered compliance Q&A with RAGAS evaluation — regional bank",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── State ─────────────────────────────────────────────────────────────────────
_eval_running: bool = False


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=2000,
                          description="Natural-language compliance question")
    context: Optional[str] = Field(
        None, description="DDD context filter: Policy | Audit | Regulation"
    )


class ChunkPreview(BaseModel):
    text: str
    source: str
    reranker_score: float
    context_type: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float
    escalated: bool
    context_type: str
    reasoning: str
    chunks_used: List[Dict[str, Any]]
    triage_level: str
    triage_label: Optional[str] = None


class EvalResponse(BaseModel):
    faithfulness: float
    answer_relevancy: float
    context_recall: float
    context_precision: float
    ragas_score: float
    num_questions: int
    run_at: str
    passed: bool
    method: str


class IngestResponse(BaseModel):
    documents_processed: int
    chunks_created: int
    duration_seconds: float
    status: str


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    collection_count: int
    version: str
    chroma_path: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check service health and ChromaDB document count."""
    try:
        from backend.agents.retriever import RetrieverAgent
        count = RetrieverAgent.get_instance().collection_count()
    except Exception:
        count = -1
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "collection_count": count,
        "version": "1.0.0",
        "chroma_path": CHROMA_DB_PATH,
    }


@app.post("/api/query", response_model=QueryResponse, tags=["RAG"])
async def query_compliance(req: QueryRequest):
    """
    Ask a compliance question.
    Returns a grounded answer with source citations and confidence score.
    Automatically escalates if confidence < 0.75.
    """
    if req.context and req.context not in CONTEXTS:
        raise HTTPException(
            status_code=400,
            detail=f"context must be one of {CONTEXTS}",
        )
    try:
        from pipelines.triage_pipeline import triage_query
        result = triage_query(question=req.question, context=req.context)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Query failed")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")


@app.post("/api/eval/run", response_model=EvalResponse, tags=["Evaluation"])
async def run_evaluation():
    """
    Run RAGAS evaluation on the 10-question golden set.
    Target: faithfulness ≥ 0.90 to pass.
    """
    global _eval_running
    if _eval_running:
        raise HTTPException(status_code=429, detail="Evaluation already in progress")
    _eval_running = True
    try:
        from backend.eval.ragas_eval import run_ragas_evaluation
        from pipelines.rag_pipeline import run_query
        scores = run_ragas_evaluation(
            pipeline_fn=run_query,
            golden_set_path=GOLDEN_SET_PATH,
            results_path=EVAL_RESULTS_PATH,
        )
        return scores
    except Exception as e:
        logger.exception("Evaluation failed")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        _eval_running = False


@app.get("/api/eval/scores", tags=["Evaluation"])
async def get_eval_scores():
    """Return the full evaluation history and the latest run."""
    p = Path(EVAL_RESULTS_PATH)
    if not p.exists():
        return {"history": [], "latest": None}
    with open(p, "r", encoding="utf-8") as f:
        history = json.load(f)
    return {"history": history, "latest": history[-1] if history else None}


@app.post("/api/ingest", response_model=IngestResponse, tags=["Data"])
async def trigger_ingestion():
    """
    Ingest all documents from ./data/ into ChromaDB.
    Chunks at 512 tokens, embeds with BGE-small-en-v1.5.
    """
    try:
        import ingest as ingest_module
        result = ingest_module.ingest(data_dir=DATA_DIR, chroma_path=CHROMA_DB_PATH)
        return {
            "documents_processed": result.get("documents", 0),
            "chunks_created": result.get("chunks", 0),
            "duration_seconds": round(result.get("duration", 0), 2),
            "status": "success",
        }
    except Exception as e:
        logger.exception("Ingestion failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trust-canvas", tags=["Architecture"])
async def get_trust_canvas():
    """Return Trust Boundary Canvas zones and Failure Mode Register."""
    return {
        "zones": [
            {
                "id": "ai_autonomous",
                "label": "AI Autonomous",
                "quadrant": "top-left",
                "description": "Fully automated — no human decision needed",
                "color": "#10b981",
                "bg": "#052e16",
                "capabilities": [
                    "Document ingestion & parsing",
                    "Text chunking (512 tokens / 50 overlap)",
                    "BGE-small-en-v1.5 embedding generation",
                    "ChromaDB vector storage (local)",
                    "Top-20 semantic similarity search",
                    "BGE-reranker-base cross-encoding",
                ],
            },
            {
                "id": "ai_assisted",
                "label": "AI-Assisted",
                "quadrant": "top-right",
                "description": "AI recommends — human approves",
                "color": "#6366f1",
                "bg": "#1e1b4b",
                "capabilities": [
                    "Compliance query understanding",
                    "Answer generation (Gemini 1.5 Flash)",
                    "Source document citation enforcement",
                    "DDD context routing (Policy/Audit/Reg)",
                    "Blended confidence scoring",
                    "Risk flag identification",
                ],
            },
            {
                "id": "human_required",
                "label": "Human Required",
                "quadrant": "bottom-left",
                "description": "Must have human decision & sign-off",
                "color": "#f59e0b",
                "bg": "#1c1003",
                "capabilities": [
                    "Policy change approvals",
                    "Regulatory filing submissions",
                    "Escalated query resolution",
                    "Audit finding sign-off",
                    "SAR filing decisions",
                    "Compliance officer review",
                ],
            },
            {
                "id": "sensitive_protected",
                "label": "Sensitive / Protected",
                "quadrant": "bottom-right",
                "description": "Never sent to any external AI model",
                "color": "#ef4444",
                "bg": "#1f0505",
                "capabilities": [
                    "Customer PII & personal data",
                    "Authentication credentials",
                    "Financial transaction records",
                    "Account-level information",
                    "Beneficial owner private data",
                    "Internal audit workpapers",
                ],
            },
        ],
        "failure_modes": [
            {
                "id": 1,
                "mode": "Regulatory Misstatement",
                "description": "AI cites incorrect regulation number or provision text",
                "severity": "Critical",
                "likelihood": "Medium",
                "mitigation": "Citation enforcement in prompt; RAGAS faithfulness ≥ 0.90 gate",
                "zone": "ai_assisted",
            },
            {
                "id": 2,
                "mode": "Policy Hallucination",
                "description": "AI fabricates policy content not present in source documents",
                "severity": "Critical",
                "likelihood": "Low",
                "mitigation": "RAG grounding; top-5 context-only prompt; faithfulness check",
                "zone": "ai_assisted",
            },
            {
                "id": 3,
                "mode": "PII Data Leakage",
                "description": "Customer personal data inadvertently sent to Gemini external API",
                "severity": "Critical",
                "likelihood": "Low",
                "mitigation": "Trust boundary enforced; sensitive data never leaves local zone",
                "zone": "sensitive_protected",
            },
            {
                "id": 4,
                "mode": "Context Contamination",
                "description": "Outdated regulatory bulletin retrieved instead of current version",
                "severity": "High",
                "likelihood": "Medium",
                "mitigation": "Document metadata timestamps; scheduled re-ingestion pipeline",
                "zone": "ai_autonomous",
            },
            {
                "id": 5,
                "mode": "Escalation Bypass",
                "description": "Low-confidence answer returned to user without escalation",
                "severity": "High",
                "likelihood": "Low",
                "mitigation": "Hard confidence gate at 0.75; escalation cannot be bypassed",
                "zone": "ai_assisted",
            },
            {
                "id": 6,
                "mode": "Citation Error",
                "description": "Correct answer attributed to wrong source document",
                "severity": "High",
                "likelihood": "Low",
                "mitigation": "Source metadata embedded in chunks; prompt enforces exact filename citation",
                "zone": "ai_assisted",
            },
            {
                "id": 7,
                "mode": "Embedding Drift",
                "description": "Embedding model update causes inconsistency with stored vectors",
                "severity": "Medium",
                "likelihood": "Low",
                "mitigation": "Pin embedding model version; full re-ingest on any model update",
                "zone": "ai_autonomous",
            },
            {
                "id": 8,
                "mode": "Reranker Failure",
                "description": "Reranker scores all chunks equally — no quality differentiation",
                "severity": "Medium",
                "likelihood": "Low",
                "mitigation": "Monitor score distribution; fallback to cosine similarity rank",
                "zone": "ai_autonomous",
            },
            {
                "id": 9,
                "mode": "Gemini Rate Limiting",
                "description": "Free-tier API quota exhausted under concurrent load",
                "severity": "Medium",
                "likelihood": "Medium",
                "mitigation": "Request queuing; exponential backoff; usage dashboard alerts",
                "zone": "ai_assisted",
            },
            {
                "id": 10,
                "mode": "Stale Knowledge Base",
                "description": "New regulation published but not yet ingested into ChromaDB",
                "severity": "High",
                "likelihood": "Medium",
                "mitigation": "Scheduled nightly ingestion; document freshness monitoring",
                "zone": "ai_autonomous",
            },
        ],
    }


@app.get("/api/golden-set", tags=["Evaluation"])
async def get_golden_set():
    """Return the 10-question golden evaluation set."""
    p = Path(GOLDEN_SET_PATH)
    if not p.exists():
        return {"questions": []}
    with open(p, "r", encoding="utf-8") as f:
        return {"questions": json.load(f)}


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    from backend.config import API_HOST, API_PORT
    uvicorn.run("backend.main:app", host=API_HOST, port=API_PORT, reload=True)
