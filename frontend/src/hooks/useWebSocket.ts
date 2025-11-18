import { useEffect, useRef, useCallback, useState } from 'react';
import type { ClientMessage, WsMessage } from '../types/wsTypes';

export function useWebSocket(camId: string) {
  const wsRef = useRef<WebSocket | null>(null);
  const [message, setMessage] = useState<WsMessage | null>(null);
  const [readyState, setReadyState] = useState<WebSocket['readyState']>(
    WebSocket.CLOSED
  );
  const url = `${import.meta.env.VITE_WEBSOCKET_URL}hit/${camId}`;

  useEffect(() => {
    if (!camId) return;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[WS] OPEN', url);
      setReadyState(WebSocket.OPEN);
    };
    ws.onmessage = (event) => {
      try {
        setMessage(JSON.parse(event.data));
      } catch (e) {
        console.error(e);
      }
    };

    ws.onerror = (err) => console.error('[WS] ERROR', err);
    ws.onclose = () => {
      console.log('[WS] CLOSED');
      setReadyState(WebSocket.CLOSED);
    };

    return () => ws.close();
  }, [url, camId]);

  const send = useCallback((data: ClientMessage) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data));
    }
  }, []);

  return { send, message, readyState };
}
