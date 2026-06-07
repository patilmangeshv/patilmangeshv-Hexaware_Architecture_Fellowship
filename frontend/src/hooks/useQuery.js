import { useState, useCallback } from 'react';
import { postQuery } from '../api/client.js';

export function useQuery() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const submitQuery = useCallback(async (question, context = null) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await postQuery(question, context);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return { result, loading, error, submitQuery };
}
