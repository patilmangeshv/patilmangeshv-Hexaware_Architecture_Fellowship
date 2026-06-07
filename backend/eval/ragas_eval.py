"""
RAGAS Evaluation Module
=======================
Runs the golden Q&A set through the RAG pipeline and scores with RAGAS.

Target: faithfulness ≥ 0.90 (hard pass/fail gate).

Failure Mode Register row 1: Regulatory Misstatement — guarded by faithfulness check.
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)

# Evaluate only the first N questions from the golden set.
RAGAS_EVAL_QUESTION_COUNT: int = 5


# ── Helpers ────────────────────────────────────────────────────────────────────

def _load_golden_set(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_results(scores: dict, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    history: List[dict] = []
    if Path(path).exists():
        with open(path, "r", encoding="utf-8") as f:
            history = json.load(f)
    history.append(scores)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    logger.info("Eval results saved → %s  (total runs: %d)", path, len(history))


# ── Main evaluation entry-point ────────────────────────────────────────────────

def run_ragas_evaluation(
    pipeline_fn: Callable[[str], dict],
    golden_set_path: str,
    results_path: str,
) -> Dict[str, Any]:
    """
    Evaluate the RAG pipeline against the golden Q&A set using RAGAS.

    Args:
        pipeline_fn:       Callable(question: str) → {answer, chunks_used, ...}
        golden_set_path:   Path to golden_qa.json
        results_path:      Where to append/store eval history JSON

    Returns:
        dict with RAGAS metric scores + metadata
    """
    golden_all = _load_golden_set(golden_set_path)
    golden = golden_all[:RAGAS_EVAL_QUESTION_COUNT]
    logger.info(
        "Starting RAGAS evaluation — %d/%d questions",
        len(golden),
        len(golden_all),
    )

    questions, answers, contexts, ground_truths = [], [], [], []
    for item in golden:
        q = item["question"]
        gt = item["ground_truth"]
        try:
            result = pipeline_fn(q)
            ans = result.get("answer", "")
            ctx = [c["text"] for c in result.get("chunks_used", [])]
            if not ctx:
                ctx = ["No context retrieved."]
        except Exception as exc:
            logger.error("Pipeline error for q=%r: %s", q[:60], exc)
            ans = ""
            ctx = ["Pipeline error."]

        questions.append(q)
        answers.append(ans)
        contexts.append(ctx)
        ground_truths.append(gt)

    scores = _evaluate_with_ragas(questions, answers, contexts, ground_truths)
    scores["num_questions"] = len(golden)
    scores["run_at"] = datetime.utcnow().isoformat() + "Z"
    scores["passed"] = scores.get("faithfulness", 0.0) >= 0.90

    _save_results(scores, results_path)
    logger.info(
        "RAGAS done — faithfulness=%.3f  ragas_score=%.3f  passed=%s",
        scores.get("faithfulness", 0),
        scores.get("ragas_score", 0),
        scores.get("passed"),
    )
    return scores


# ── RAGAS backend ──────────────────────────────────────────────────────────────

def _evaluate_with_ragas(questions, answers, contexts, ground_truths) -> dict:
    """Try RAGAS with Gemini LLM; fall back to heuristics on failure."""
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_recall,
            context_precision,
        )
        from backend.config import GEMINI_API_KEY, GEMINI_MODEL

        # Provide a dummy OpenAI key so RAGAS doesn't crash before we swap LLM
        os.environ.setdefault("OPENAI_API_KEY", "not-needed-using-gemini")

        # Configure RAGAS to use Gemini via LangChain wrapper
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from ragas.llms import LangchainLLMWrapper

            llm = LangchainLLMWrapper(
                ChatGoogleGenerativeAI(
                    model=GEMINI_MODEL,
                    google_api_key=GEMINI_API_KEY,
                    temperature=0,
                )
            )
            for metric in [faithfulness, answer_relevancy, context_recall, context_precision]:
                metric.llm = llm
            logger.info("RAGAS configured with Gemini LLM.")
        except Exception as llm_exc:
            logger.warning("Could not set RAGAS LLM to Gemini (%s). Using default.", llm_exc)

        dataset = Dataset.from_dict(
            {
                "question": questions,
                "answer": answers,
                "contexts": contexts,
                "ground_truth": ground_truths,
            }
        )
        result = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
        )

        f  = round(float(result.get("faithfulness", 0)), 4)
        ar = round(float(result.get("answer_relevancy", 0)), 4)
        cr = round(float(result.get("context_recall", 0)), 4)
        cp = round(float(result.get("context_precision", 0)), 4)
        denom = f + ar + cr + cp
        ragas_score = round((4 * f * ar * cr * cp) / denom, 4) if denom > 0 else 0.0

        return {
            "faithfulness": f,
            "answer_relevancy": ar,
            "context_recall": cr,
            "context_precision": cp,
            "ragas_score": ragas_score,
            "method": "ragas",
        }

    except Exception as exc:
        logger.warning("RAGAS evaluation failed (%s) — falling back to heuristics.", exc)
        return _heuristic_scores(questions, answers, contexts, ground_truths)


# ── Heuristic fallback ────────────────────────────────────────────────────────

def _heuristic_scores(questions, answers, contexts, ground_truths) -> dict:
    """
    Simple Jaccard-overlap heuristic when RAGAS is unavailable.
    NOT a substitute for true RAGAS — for development/demo only.
    """
    def tokens(text: str):
        return set(re.findall(r"\w+", text.lower()))

    def jaccard(a: str, b: str) -> float:
        sa, sb = tokens(a), tokens(b)
        if not sa or not sb:
            return 0.0
        return len(sa & sb) / len(sa | sb)

    faith, relev, recall, prec = [], [], [], []
    for q, a, ctx_list, gt in zip(questions, answers, contexts, ground_truths):
        ctx = " ".join(ctx_list)
        faith.append(jaccard(a, ctx))
        relev.append(jaccard(a, q))
        recall.append(jaccard(ctx, gt))
        prec.append(jaccard(ctx, gt) * 0.9)

    def avg(lst):
        return round(sum(lst) / len(lst), 4) if lst else 0.0

    f, ar, cr, cp = avg(faith), avg(relev), avg(recall), avg(prec)
    denom = f + ar + cr + cp
    ragas_score = round((4 * f * ar * cr * cp) / denom, 4) if denom > 0 else 0.0

    return {
        "faithfulness": f,
        "answer_relevancy": ar,
        "context_recall": cr,
        "context_precision": cp,
        "ragas_score": ragas_score,
        "method": "heuristic",
    }
