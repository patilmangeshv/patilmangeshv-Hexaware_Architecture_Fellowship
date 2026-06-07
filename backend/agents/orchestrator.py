"""
Orchestrator Agent
==================
Routes compliance queries through the full RAG pipeline.
Enforces the human approval gate for all write operations.
DDD bounded contexts: Policy | Audit | Regulation
"""
from __future__ import annotations

import logging
from typing import Optional

from backend.agents.retriever import RetrieverAgent
from backend.agents.reasoning import ReasoningAgent
from backend.config import CONTEXTS, ESCALATION_MESSAGE

logger = logging.getLogger(__name__)

# ── DDD context auto-router ───────────────────────────────────────────────────

_POLICY_KW = frozenset(
    ["policy", "procedure", "standard", "requirement", "kyc", "aml",
     "credit", "privacy", "security", "limit", "threshold"]
)
_AUDIT_KW = frozenset(
    ["audit", "finding", "observation", "control", "q1", "q2", "q3", "q4",
     "remediation", "deficiency", "gap"]
)
_REGULATION_KW = frozenset(
    ["regulation", "regulatory", "bulletin", "rule", "law", "sar",
     "report", "filing", "guidance", "directive"]
)


def _infer_context(query: str) -> Optional[str]:
    """Heuristic DDD bounded-context router based on query keywords."""
    q = query.lower()
    words = set(q.split())
    if words & _AUDIT_KW:
        return "Audit"
    if words & _REGULATION_KW:
        return "Regulation"
    if words & _POLICY_KW:
        return "Policy"
    return None  # no filter — search all contexts


# ── Write operations that require human approval ──────────────────────────────

_WRITE_OPS = frozenset(
    [
        "update_policy",
        "add_regulation",
        "modify_audit_finding",
        "approve_change",
        "file_regulatory_report",
        "create_sar",
        "amend_procedure",
    ]
)


class OrchestratorAgent:
    """
    Coordinates retrieval + reasoning for a compliance query.

    Trust Architecture:
      - Read queries   → AI-Recommend / Human-Review
      - Write operations → ALWAYS require Human-Approve gate
    """

    def __init__(self) -> None:
        self._retriever = RetrieverAgent.get_instance()
        self._reasoner = ReasoningAgent()

    def query(self, question: str, context: Optional[str] = None) -> dict:
        """
        Full pipeline: retrieve → rerank → reason → escalate if needed.

        Args:
            question: Natural-language compliance question
            context:  Optional explicit DDD context override

        Returns:
            {answer, sources, confidence, escalated, context_type,
             reasoning, chunks_used, triage_level}
        """
        if context and context not in CONTEXTS:
            raise ValueError(f"context must be one of {CONTEXTS}, got {context!r}")

        effective_ctx = context or _infer_context(question)
        logger.info(
            "Orchestrator.query | ctx=%s | question='%.80s'",
            effective_ctx, question,
        )

        # ── Step 1: Retrieve + Rerank ─────────────────────────────────────
        chunks, reranker_confidence = self._retriever.retrieve_and_rerank(
            query=question,
            context_filter=effective_ctx,
        )

        if not chunks:
            logger.warning("No chunks retrieved — escalating.")
            return {
                "answer": (
                    "⚠️ No relevant documents found in the knowledge base. "
                    "Please contact compliance@bank.com for assistance."
                ),
                "sources": [],
                "confidence": 0.0,
                "escalated": True,
                "context_type": effective_ctx or "Unknown",
                "reasoning": "No chunks retrieved from knowledge base.",
                "chunks_used": [],
                "triage_level": "escalate",
            }

        # ── Step 2: Generate Answer ───────────────────────────────────────
        result = self._reasoner.generate(
            query=question,
            chunks=chunks,
            reranker_confidence=reranker_confidence,
        )

        # ── Step 3: Attach chunk preview ──────────────────────────────────
        result["chunks_used"] = [
            {
                "text": c["text"][:400] + ("…" if len(c["text"]) > 400 else ""),
                "source": c.get("metadata", {}).get("source", "Unknown"),
                "reranker_score": c.get("reranker_score", 0),
                "context_type": c.get("metadata", {}).get("context_type", "Unknown"),
            }
            for c in chunks
        ]

        # ── Step 4: Triage level ──────────────────────────────────────────
        conf = result["confidence"]
        if result["escalated"] or conf < 0.75:
            result["triage_level"] = "escalate"
        elif conf < 0.90:
            result["triage_level"] = "review"
        else:
            result["triage_level"] = "auto"

        logger.info(
            "Answer generated | confidence=%.3f | escalated=%s | triage=%s",
            conf, result["escalated"], result["triage_level"],
        )
        return result

    @staticmethod
    def requires_human_approval(operation: str) -> bool:
        """
        Human approval gate — every write operation must be approved.
        Returns True if the operation requires a human to approve it.
        """
        return operation in _WRITE_OPS
