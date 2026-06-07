"""
Triage Pipeline
===============
Routes compliance queries by confidence level and enforces escalation.

Triage levels:
  - auto     (confidence ≥ 0.90): High-confidence AI answer — return immediately
  - review   (0.75 ≤ conf < 0.90): AI answer — flag for human review
  - escalate (confidence < 0.75):  Low confidence — must escalate to human
"""
from __future__ import annotations

import logging
from enum import Enum
from typing import Optional

from pipelines.rag_pipeline import run_query

logger = logging.getLogger(__name__)


class TriageLevel(str, Enum):
    AUTO = "auto"
    REVIEW = "review"
    ESCALATE = "escalate"


_TRIAGE_LABELS = {
    TriageLevel.AUTO: "✅ AI Answer — High Confidence",
    TriageLevel.REVIEW: "⚠️ AI Answer — Requires Human Review",
    TriageLevel.ESCALATE: "🚨 Escalated — Compliance Officer Required",
}


def triage_query(question: str, context: Optional[str] = None) -> dict:
    """
    Route a compliance query through the full triage pipeline.

    Returns the RAG pipeline result enriched with triage metadata.
    """
    result = run_query(question, context=context)
    conf = result.get("confidence", 0.0)
    escalated = result.get("escalated", False)

    if escalated or conf < 0.75:
        level = TriageLevel.ESCALATE
    elif conf < 0.90:
        level = TriageLevel.REVIEW
    else:
        level = TriageLevel.AUTO

    result["triage_level"] = level.value
    result["triage_label"] = _TRIAGE_LABELS[level]

    logger.info(
        "Triage: level=%s  confidence=%.3f  question='%.60s'",
        level.value, conf, question,
    )
    return result
