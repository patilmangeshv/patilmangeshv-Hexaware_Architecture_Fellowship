# Setup Guide — Compliance Knowledge Agent

## Prerequisites

- Windows 10/11
- Python 3.12+
- Node.js 18+
- PowerShell
- Gemini API key

## 1) Configure environment

Create/update `.env` in project root:

```env
GEMINI_API_KEY=your_gemini_api_key
API_HOST=0.0.0.0
API_PORT=8000
```

## 2) Activate Python environment

From project root:

```powershell
.\venv\Scripts\Activate.ps1
```

If venv does not exist:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3) Local model paths (already configured)

The backend is configured to use local model directories from [backend/config.py](backend/config.py):

- `EMBEDDING_MODEL = C:\Python\local_models\BAAI__bge-reranker-base`
- `RERANKER_MODEL = C:\Python\local_models\BAAI__bge-small-en-v1.5`

Ensure both directories exist before starting services.

## 4) Ingest documents into local ChromaDB

```powershell
python ingest.py
```

Expected result: successful ingestion with document/chunk counts.

## 5) Start backend (FastAPI)

```powershell
python -m backend.main
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/api/docs
- Health: http://localhost:8000/api/health

## 6) Start frontend (Vite/React)

Open a second terminal in project root:

```powershell
cd .\frontend
npm install
npm run dev
```

Frontend URL: http://localhost:5173

## 7) Quick verification

1. Open frontend dashboard.
2. Run a query on the Query page.
3. Open Evaluation page and run RAGAS evaluation.
4. Confirm trust boundary canvas and metric cards render.

## Troubleshooting

### `SETUP.md` missing
Recreated at [SETUP.md](SETUP.md).

### Local model path errors
Verify both folders exist:

- `C:\Python\local_models\BAAI__bge-reranker-base`
- `C:\Python\local_models\BAAI__bge-small-en-v1.5`

### Backend cannot start
- Confirm virtual environment is active.
- Confirm `GEMINI_API_KEY` is set in `.env`.
- Reinstall dependencies: `pip install -r requirements.txt`.

### Frontend cannot reach backend
- Ensure backend runs on port `8000`.
- Ensure frontend runs on port `5173`.

## Useful commands

```powershell
# Re-ingest data
python ingest.py

# Start backend
python -m backend.main

# Frontend
cd .\frontend
npm run dev
```
