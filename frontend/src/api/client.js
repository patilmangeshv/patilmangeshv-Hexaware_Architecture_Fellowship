import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 120_000, // 2 min — model inference can be slow
  headers: { 'Content-Type': 'application/json' },
});

// ── Response interceptor for unified error handling ───────────────────────────
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      err.message ||
      'Unknown error';
    return Promise.reject(new Error(msg));
  }
);

// ── Health ─────────────────────────────────────────────────────────────────────
export const getHealth = () => api.get('/health').then((r) => r.data);

// ── RAG Query ─────────────────────────────────────────────────────────────────
export const postQuery = (question, context = null) =>
  api.post('/query', { question, context }, { timeout: 0 }).then((r) => r.data);

// ── Evaluation ────────────────────────────────────────────────────────────────
export const runEvaluation = () =>
  api.post('/eval/run', {}, { timeout: 0 }).then((r) => r.data);
export const getEvalScores = () => api.get('/eval/scores').then((r) => r.data);
export const getGoldenSet = () => api.get('/golden-set').then((r) => r.data);

// ── Ingestion ─────────────────────────────────────────────────────────────────
export const triggerIngest = () => api.post('/ingest').then((r) => r.data);

// ── Trust Canvas ──────────────────────────────────────────────────────────────
export const getTrustCanvas = () => api.get('/trust-canvas').then((r) => r.data);

export default api;
