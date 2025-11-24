import { useEffect, useState } from 'react';
import type { WsMessage } from '../types/wsTypes';

type Hit = [number, number];

export function useHit(message: WsMessage | null) {
  const [hit, setHit] = useState<Hit | null>(null);

  useEffect(() => {
    if (!message) return;
    if (message.type === 'hit') {
      setHit(message.tip);
    }
  }, [message]);

  useEffect(() => {
    if (!hit) return;
    const timer = setTimeout(() => setHit(null), 6000);
    return () => clearTimeout(timer);
  }, [hit]);

  return hit;
}
