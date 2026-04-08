import { useEffect, useState } from 'react';
import type { RealtimeDemand } from '../types';

type Status = 'connecting' | 'connected' | 'disconnected';

export function useRealtime() {
  const [data, setData] = useState<RealtimeDemand[]>([]);
  const [status, setStatus] = useState<Status>('connecting');

  useEffect(() => {
    const baseURL = import.meta.env.VITE_API_URL || '';
    const url = `${baseURL}/api/realtime/stream`;
    const es = new EventSource(url);

    es.onopen = () => setStatus('connected');
    es.onerror = () => setStatus('disconnected');
    es.addEventListener('demand', (ev) => {
      try {
        setData(JSON.parse((ev as MessageEvent).data));
      } catch (e) {
        console.error('Failed to parse SSE payload', e);
      }
    });

    return () => es.close();
  }, []);

  return { data, status };
}
