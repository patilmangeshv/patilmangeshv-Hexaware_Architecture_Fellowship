# 📚 Documentation Index

Quick navigation to all project documentation:

## 🚀 Start Here
- **[SETUP.md](SETUP.md)** ← **START HERE** (5-minute quick start)
- **[README.md](README.md)** ← Full technical documentation

## 📋 Project Overview
- **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** ← Complete delivery summary
- **[DELIVERY.md](DELIVERY.md)** ← What was built (with detailed feature list)
- **[ADR.md](ADR.md)** ← Architecture decisions (14 key decisions documented)

## 🔧 Backend

### Configuration
- `backend/config.py` — Central configuration (all settings here)
- `.env.example` → Copy to `.env` and add GEMINI_API_KEY

### Core Agents
- `backend/agents/retriever.py` — BGE-small embedding + ChromaDB + BGE-reranker
- `backend/agents/reasoning.py` — Gemini answer generation with citation enforcement
- `backend/agents/orchestrator.py` — Full RAG pipeline orchestration

### Evaluation
- `backend/eval/ragas_eval.py` — RAGAS evaluation (faithfulness ≥ 0.90 gate)
- `backend/data/golden_set/golden_qa.json` — 10 Q&A pairs for evaluation

### Data & Ingestion
- `ingest.py` — Document ingestion (PDF + DOCX from `./data/`)
- `backend/data/synthetic/generate_synthetic.py` — Faker test data

### Pipelines
- `pipelines/rag_pipeline.py` — Main RAG entry point
- `pipelines/triage_pipeline.py` — Confidence-based query routing

### API
- `backend/main.py` — FastAPI app (8 endpoints)
  - Docs: http://localhost:8000/api/docs (Swagger UI)

## 🎨 Frontend

### Setup
- `frontend/package.json` — Dependencies + scripts
- `frontend/vite.config.js` — Vite configuration (dev server, build)
- `frontend/tailwind.config.js` — Tailwind CSS theme
- `frontend/postcss.config.js` — PostCSS configuration

### Core
- `frontend/src/main.jsx` — React entry point
- `frontend/src/App.jsx` — Router setup
- `frontend/src/index.css` — Global styles

### API Integration
- `frontend/src/api/client.js` — Axios HTTP client + API wrappers

### Custom Hooks
- `frontend/src/hooks/useQuery.js` — Query execution hook
- `frontend/src/hooks/useEvaluation.js` — Evaluation hook

### Components

**Layout**
- `frontend/src/components/layout/Header.jsx` — Top bar + ingest button
- `frontend/src/components/layout/Sidebar.jsx` — Navigation
- `frontend/src/components/layout/Layout.jsx` — Main wrapper

**Metrics (Dashboard)**
- `frontend/src/components/metrics/MetricGauge.jsx` — SVG arc gauge visualization
- `frontend/src/components/metrics/MetricCard.jsx` — Metric card with gauge
- `frontend/src/components/metrics/AverageProgress.jsx` — Progress bars

**Trust & Architecture**
- `frontend/src/components/trust/TrustBoundaryCanvas.jsx` — 2×2 zones + 10-row failure mode table

**Query**
- `frontend/src/components/query/QueryInterface.jsx` — Question input + context selector
- `frontend/src/components/query/AnswerDisplay.jsx` — Answer + sources + chunks + escalation

**Evaluation**
- `frontend/src/components/eval/RagasScorecard.jsx` — Metric summary boxes
- `frontend/src/components/eval/FailureModeRegister.jsx` — Failure modes table

### Pages
- `frontend/src/pages/Dashboard.jsx` — RAGAS metrics + Trust Canvas
- `frontend/src/pages/QueryPage.jsx` — Ask questions
- `frontend/src/pages/EvaluationPage.jsx` — Run eval + view history

## 📊 Key Features

### RAG Pipeline
- Retrieval: BGE-small embeddings + ChromaDB (top-20)
- Reranking: BGE-reranker-base (mandatory, top-5)
- Generation: Gemini 1.5 Flash (citation-enforced)
- Confidence: Blended score (60% Gemini + 40% reranker)
- Escalation: < 0.75 → human review

### RAGAS Evaluation
- Metrics: Faithfulness, Answer Relevancy, Context Recall, Context Precision
- Golden Set: 10 Q&A pairs covering all DDD contexts
- Pass Gate: Faithfulness ≥ 0.90
- History: All eval runs stored in JSON

### Trust Boundary Canvas
- 4-Zone Matrix: AI Autonomous | AI-Assisted | Human-Required | Sensitive
- 10-Row Failure Mode Register: Regulatory Misstatement + 9 other critical risks

### DDD Contexts
- Policy: KYC, AML, Data Privacy, IT Security, Credit Risk
- Audit: Findings, observations, control gaps
- Regulation: Regulatory bulletins, compliance rules

## 🚀 Quick Start

```bash
# 1. Backend
cp .env.example .env           # Add your GEMINI_API_KEY
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python ingest.py               # Ingest 10 documents
python -m backend.main         # Start on :8000

# 2. Frontend (new terminal)
cd frontend
npm install
npm run dev                     # Start on :5173

# 3. Open browser
http://localhost:5173
```

## 📈 API Endpoints

```
GET  /api/health              — Health check
POST /api/query               — Ask compliance question
POST /api/eval/run            — Run RAGAS evaluation
GET  /api/eval/scores         — Fetch eval history
POST /api/ingest              — Trigger ingestion
GET  /api/trust-canvas        — Trust Canvas data
GET  /api/golden-set          — Golden Q&A set
```

Full docs: http://localhost:8000/api/docs

## ✅ Checklist

Before going live:
- [ ] Add GEMINI_API_KEY to `.env`
- [ ] Run `python ingest.py` (ingest documents)
- [ ] Run RAGAS eval (confirm faithfulness ≥ 0.90)
- [ ] Build frontend: `cd frontend && npm run build`
- [ ] Test queries at http://localhost:5173
- [ ] Review Trust Canvas for compliance sign-off
- [ ] Deploy backend + frontend to production
- [ ] Monitor Gemini API usage (free tier: 60 req/min)

## 🔗 Important Links

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **FastAPI Docs**: http://localhost:8000/api/docs
- **Gemini API**: https://ai.google.dev/

## 📞 Support

See **SETUP.md** for troubleshooting.

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: June 7, 2024
