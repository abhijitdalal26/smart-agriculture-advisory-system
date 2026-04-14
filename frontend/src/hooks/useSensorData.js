// Sensor data polling hook — polls /api/sensors/latest every 5 seconds
import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

export function useSensorData() {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetch = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/api/sensors/latest`, { timeout: 4000 });
      setData(res.data);
      setError(null);
      setLastUpdated(new Date());
    } catch (e) {
      setError('Sensor data unavailable');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
    const id = setInterval(fetch, 5000);
    return () => clearInterval(id);
  }, [fetch]);

  return { data, loading, error, lastUpdated, refetch: fetch };
}
