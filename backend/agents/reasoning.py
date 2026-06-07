"""
Reasoning Agent
===============
Calls Gemini with the top-5 reranked compliance chunks as context.
Returns a grounded, citation-enforced answer in structured JSON.

Rules:
  - Sensitive data stays local — only chunk text sent to Gemini.
  - Response must include source document name.
  - Confidence < 0.75 triggers escalation — never silently return a bad answer.
"""
from __future__ import annotations

import json
import logging
import re
from typing import List, Optional

import google.generativeai as genai

from backend.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    CONFIDENCE_THRESHOLD,
    ESCALATION_MESSAGE,
)

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a compliance knowledge assistant for a regional bank.
You answer questions based ONLY on the provided regulatory and policy documents.

STRICT RULES:
1. Cite the EXACT source document filename for every claim.
2. Be precise and factual — no speculation or hallucination.
3. If context is insufficient, say "Insufficient context to answer."
4. Assign a confidence score (0.0–1.0) reflecting how well the context answers the question.
5. Return ONLY valid JSON — no markdown, no extra text.

Response JSON schema:
{
  "answer": "<detailed answer with inline citations like [Source: filename.pdf]>",
  "sources": ["<filename1>", "<filename2>"],
  "confidence": <float 0.0-1.0>,
  "reasoning": "<1-2 sentence reasoning chain>",
  "context_type": "<Policy|Audit|Regulation|Unknown>"
}"""


class ReasoningAgent:
    """
    Wraps Google Gemini for grounded compliance Q&A with citation enforcement.
    """

    def __init__(self) -> None:
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set. Add it to .env before starting."
            )
        genai.configure(api_key=GEMINI_API_KEY)
        self._model = genai.GenerativeModel(
            GEMINI_MODEL,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=1024,
            ),
        )
        logger.info("ReasoningAgent ready — model=%s", GEMINI_MODEL)

    def _build_context(self, chunks: List[dict]) -> str:
        parts = []
        for i, chunk in enumerate(chunks, 1):
            src = chunk.get("metadata", {}).get("source", "Unknown")
            score = chunk.get("reranker_score", 0)
            parts.append(
                f"[{i}] Source: {src} (relevance: {score:.3f})\n{chunk['text']}"
            )
        return "\n\n---\n\n".join(parts)

    def _parse_json(self, raw: str) -> dict:
        """Extract JSON from Gemini response, stripping any markdown fences."""
        cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if m:
                return json.loads(m.group())
            raise

    def generate(
        self,
        query: str,
        chunks: List[dict],
        reranker_confidence: float,
    ) -> dict:
        """
        Generate a grounded compliance answer.

        Returns:
            {answer, sources, confidence, escalated, context_type, reasoning}
        """
        context_block = self._build_context(chunks)
        user_message = (
            f"CONTEXT DOCUMENTS:\n{context_block}\n\n"
            f"QUESTION: {query}\n\n"
            "Answer based solely on the context documents above. "
            "Include source citations in your answer. Return valid JSON only."
        )

        try:
            response = self._model.generate_content(
                _SYSTEM_PROMPT + "\n\n" + user_message
            )
            parsed = self._parse_json(response.text)

            # Blend Gemini self-reported confidence with reranker score
            gemini_conf = float(parsed.get("confidence", 0.5))
            blended = round(0.6 * gemini_conf + 0.4 * reranker_confidence, 3)
            escalated = blended < CONFIDENCE_THRESHOLD

            return {
                "answer": ESCALATION_MESSAGE if escalated else parsed.get("answer", ""),
                "sources": parsed.get("sources", []),
                "confidence": blended,
                "escalated": escalated,
                "context_type": parsed.get("context_type", "Unknown"),
                "reasoning": parsed.get("reasoning", ""),
                "raw_answer": parsed.get("answer", "") if escalated else None,
            }

        except Exception as exc:
            logger.exception("Gemini generation failed: %s", exc)
            return {
                "answer": ESCALATION_MESSAGE,
                "sources": [],
                "confidence": 0.0,
                "escalated": True,
                "context_type": "Unknown",
                "reasoning": f"Generation error: {exc}",
                "raw_answer": None,
            }
