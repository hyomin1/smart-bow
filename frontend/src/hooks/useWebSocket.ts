import { useEffect, useRef, useCallback, useState } from 'react';
import type { ClientMessage, WsMessage } from '../types/wsTypes';

const MAX_RETRY_ATTEMPTS = 5;
const INITIAL_RETRY_DELAY = 1000;
const MAX_RETRY_DELAY = 30000;

export function useWebSocket(camId: string) {
  const wsRef = useRef<WebSocket | null>(null);
  const [message, setMessage] = useState<WsMessage | null>(null);
  const [readyState, setReadyState] = useState<WebSocket['readyState']>(
    WebSocket.CLOSED
  );

  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  const retryTimeoutRef = useRef<number | null>(null);
  const reconnectAttemptRef = useRef(0);
  const isManualCloseRef = useRef(false);
  const isConnectingRef = useRef(false);

  const connect = useCallback(() => {
    if (!camId) return;
    if (isConnectingRef.current) return;
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    if (wsRef.current) {
      const oldWs = wsRef.current;
      wsRef.current = null;
      oldWs.onopen = null;
      oldWs.onmessage = null;
      oldWs.onerror = null;
      oldWs.onclose = null;
      oldWs.close();
    }

    if (reconnectAttemptRef.current >= MAX_RETRY_ATTEMPTS) {
      setError(`연결 실패: 최대 재시도 횟수(${MAX_RETRY_ATTEMPTS}회) 초과`);
      setReadyState(WebSocket.CLOSED);
      return;
    }

    try {
      isConnectingRef.current = true;
      const url = `${import.meta.env.VITE_WEBSOCKET_URL}hit/${camId}`;

      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket 연결 성공');
        isConnectingRef.current = false;
        setReadyState(WebSocket.OPEN);
        setError(null);
        reconnectAttemptRef.current = 0;
        setRetryCount(0);
      };

      ws.onmessage = (event) => {
        try {
          setMessage(JSON.parse(event.data));
        } catch {
          setError('메시지 파싱 오류');
        }
      };

      ws.onerror = () => {
        isConnectingRef.current = false;
        setError('WebSocket 연결 오류');
      };

      ws.onclose = (event) => {
        isConnectingRef.current = false;
        console.log('❌ WebSocket 종료', {
          code: event.code,
          reason: event.reason,
          isManual: isManualCloseRef.current,
          retryCount: reconnectAttemptRef.current,
        });

        setReadyState(WebSocket.CLOSED);

        if (
          !isManualCloseRef.current &&
          reconnectAttemptRef.current < MAX_RETRY_ATTEMPTS
        ) {
          reconnectAttemptRef.current += 1;
          setRetryCount(reconnectAttemptRef.current);

          const delay = Math.min(
            INITIAL_RETRY_DELAY * 2 ** (reconnectAttemptRef.current - 1),
            MAX_RETRY_DELAY
          );

          setError(`연결 끊김 (${delay / 1000}초 후 재시도)`);

          retryTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };
    } catch {
      isConnectingRef.current = false;
      setError('WebSocket 연결 오류');
      setReadyState(WebSocket.CLOSED);
    }
  }, [camId]);

  useEffect(() => {
    isManualCloseRef.current = false;
    connect();

    return () => {
      isManualCloseRef.current = true;
      isConnectingRef.current = false;
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
        retryTimeoutRef.current = null;
      }
      if (wsRef.current) {
        const ws = wsRef.current;
        wsRef.current = null;
        ws.onopen = null;
        ws.onmessage = null;
        ws.onerror = null;
        ws.onclose = null;
        ws.close();
      }

      reconnectAttemptRef.current = 0;
    };
  }, [connect]);

  const send = useCallback((data: ClientMessage) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      try {
        ws.send(JSON.stringify(data));
      } catch {
        setError('메시지 전송 실패');
      }
    } else {
      setError('연결되지 않음');
    }
  }, []);

  const manualReconnect = useCallback(() => {
    reconnectAttemptRef.current = 0;
    setRetryCount(0);
    setError(null);
    connect();
  }, [connect]);

  return { send, message, readyState, error, retryCount, manualReconnect };
}
