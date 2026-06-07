"""
RAG Pipeline
============
End-to-end compliance query processing:
  1. Infer DDD context (Policy | Audit | Regulation)
  2. Retrieve top-20 chunks from ChromaDB (BGE-small-en-v1.5 embeddings)
  3. Rerank with BGE-reranker-base → keep top-5
  4. Call Gemini with top-5 as context (citation-enforced prompt)
  5. Escalate if confidence < 0.75

Output: { answer, sources, confidence, escalated, context_type, chunks_used, triage_level }
"""
from __future__ import annotations

import logging
from typing import Optional

from backend.agents.orchestrator import OrchestratorAgent

logger = logging.getLogger(__name__)

# ── Singleton orchestrator ────────────────────────────────────────────────────
_orchestrator: Optional[OrchestratorAgent] = None


def _get_orchestrator() -> OrchestratorAgent:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorAgent()
    return _orchestrator


# ── Public API ────────────────────────────────────────────────────────────────

def run_query(question: str, context: Optional[str] = None) -> dict:
    """
    Execute the full RAG pipeline for a compliance question.

    Args:
        question: Natural-language compliance question
        context:  Optional DDD context override (Policy | Audit | Regulation)

    Returns:
        {
            answer:       str   — grounded answer with citations (or escalation msg)
            sources:      list  — source document filenames
            confidence:   float — blended confidence (reranker + Gemini self-report)
            escalated:    bool  — True if confidence < 0.75
            context_type: str   — detected DDD context
            reasoning:    str   — Gemini reasoning chain
            chunks_used:  list  — top-5 chunk previews with source + reranker score
            triage_level: str   — 'auto' | 'review' | 'escalate'
        }
    """
    return _get_orchestrator().query(question=question, context=context)
