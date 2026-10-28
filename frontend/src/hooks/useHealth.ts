import { useState, useEffect, useCallback } from 'react';
import { healthService } from '../services/healthService';
import { HealthResponse } from '../types/health';

export function useHealth(pollIntervalMs: number = 10000) {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = useCallback(async () => {
    try {
      const data = await healthService.getHealth();
      setHealth(data);
      setError(null);
    } catch (err: any) {
      setError(err?.message || 'Failed to reach command backend');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, pollIntervalMs);
    return () => clearInterval(interval);
  }, [fetchHealth, pollIntervalMs]);

  return { health, loading, error, refetch: fetchHealth };
}
