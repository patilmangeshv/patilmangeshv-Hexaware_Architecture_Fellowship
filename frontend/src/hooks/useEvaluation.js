import { useState, useEffect, useCallback } from 'react';
import { runEvaluation, getEvalScores } from '../api/client.js';

export function useEvaluation() {
  const [scores, setScores] = useState(null);
  const [history, setHistory] = useState([]);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);

  const fetchScores = useCallback(async () => {
    try {
      const data = await getEvalScores();
      setHistory(data.history || []);
      setScores(data.latest || null);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    fetchScores();
  }, [fetchScores]);

  const runEval = useCallback(async () => {
    setRunning(true);
    setError(null);
    try {
      const result = await runEvaluation();
      setScores(result);
      setHistory((prev) => [...prev, result]);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setRunning(false);
    }
  }, []);

  return { scores, history, running, error, runEval, fetchScores };
}
