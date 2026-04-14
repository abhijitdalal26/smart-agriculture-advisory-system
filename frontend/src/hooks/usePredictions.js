// ML prediction hook — fetches /api/predict/all every 30 seconds
// also re-fetches on manual input submission
import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = import.meta.env.VITE_API_URL || "";

export function usePredictions(trigger = 0) {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/api/predict/all`, { timeout: 10000 });
      setData(res.data);
      setError(null);
    } catch (e) {
      setError('Prediction unavailable');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
    const id = setInterval(fetch, 30000);
    return () => clearInterval(id);
  }, [fetch, trigger]);

  return { data, loading, error, refetch: fetch };
}
