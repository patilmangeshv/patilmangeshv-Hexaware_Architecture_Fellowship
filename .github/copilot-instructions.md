# Copilot Instructions

## Stack
- Python 3.12+ in a venv
- Hugging Face transformers library for any local LM inference with local models
- LLM: Gemini API Free Tier (google-generativeai)
- FastAPI + Streamlit for demo UI
- Embeddings: BAAI/bge-small-en-v1.5 (local)
- Vector store: ChromaDB (local) without Docker
- Reranker: BAAI/bge-reranker-base (local)
- UI: Streamlit with training and evaluation options.
- Eval: RAGAS

## Rules
- Always read config values from config.py — never hardcode model names
- Always run the reranker after retrieval — never skip it
- Sensitive data stays on the local HF model — do not send to Gemini
- Every write action needs a human approval gate
- If confidence < threshold, escalate — never silently return a bad answer
- Keep the UI simple with charts and informative — never overload with too much info
- Python + FastAPI for the API layer; DDD bounded contexts (Policy / Audit / Regulation)
- Prompt engineering for citation-required responses; cost & latency estimation under Gemini rate limits
- Heavy emphasis — RAG pipeline, hierarchical chunking(optional), reranker required, RAGAS faithfulness ≥ 0.90
- Stocks (golden eval set growth); R-loops (hallucinated policy interpretation); FMEA (regulatory misstatement); Trust Architecture (all answers AI-Recommend / Human-Approve)
- Working RAG pipeline on a sanitised 10-document subset (already generated in data folder)
- ADR pack — chunking, embedding, vector DB, reranker choices with rationale
- Trust Boundary Canvas — placing every capability in the right zone
- Failure Mode Register — minimum 8 rows, with regulatory misstatement as row 1
- RAGAS scorecard — golden set of 10 Q&A pairs, faithfulness ≥ 0.90 required to pass

## Folder layout
backend/agents/             <- orchestrator, retriever, reasoning agents
backend/data/synthetic/     <- Faker or Gemini-generated test data
backend/data/golden_set/    <- Q&A pairs for RAGAS evaluation
pipelines/                  <- rag_pipeline.py, triage_pipeline.py, architecture-review-pipeline.yaml
backend/eval/               <- ragas_eval.py
backend/config.py           <- all env vars and thresholds
frontend/ui/app.py          <- Streamlit dashboard