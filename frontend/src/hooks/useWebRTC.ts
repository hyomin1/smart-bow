import { useEffect, useRef, useState, useCallback } from 'react';
import { api } from '../api/axios';

interface UseWebRTCOptions {
  camId: string;
  onError?: (error: string) => void;
  onConnectionStateChange?: (state: RTCIceConnectionState) => void;
  maxReconnectAttempts?: number;
  reconnectDelay?: number;
}

interface UseWebRTCReturn {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  connectionState: RTCIceConnectionState;
  error: string | null;
  isConnecting: boolean;
  reconnect: () => void;
}

const DEFAULT_MAX_RECONNECT_ATTEMPTS = 3;
const DEFAULT_RECONNECT_DELAY = 2000;

export function useWebRTC({
  camId,
  onError,
  onConnectionStateChange,
  maxReconnectAttempts = DEFAULT_MAX_RECONNECT_ATTEMPTS,
  reconnectDelay = DEFAULT_RECONNECT_DELAY,
}: UseWebRTCOptions): UseWebRTCReturn {
  const videoRef = useRef<HTMLVideoElement>(null);
  const pcRef = useRef<RTCPeerConnection | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const isManualCloseRef = useRef(false);

  const [connectionState, setConnectionState] =
    useState<RTCIceConnectionState>('new');
  const [error, setError] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);

  const cleanup = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (pcRef.current) {
      pcRef.current.close();
      pcRef.current = null;
    }

    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
  }, []);

  const connect = useCallback(async () => {
    try {
      cleanup();

      if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
        const errorMsg = `연결 실패: 최대 재시도 횟수(${maxReconnectAttempts}회) 초과`;
        setError(errorMsg);
        onError?.(errorMsg);
        setIsConnecting(false);
        return;
      }

      setIsConnecting(true);
      setError(null);

      const pc = new RTCPeerConnection({
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun.cloudflare.com:3478' },
          {
            urls: [
              `turn:${import.meta.env.VITE_TURN_SERVER}:3478?transport=udp`,
              `turn:${import.meta.env.VITE_TURN_SERVER}:3478?transport=tcp`,
            ],
            username: import.meta.env.VITE_TURN_USERNAME,
            credential: import.meta.env.VITE_TURN_CREDENTIAL,
          },
        ],
        iceCandidatePoolSize: 10,
      });

      pcRef.current = pc;

      pc.oniceconnectionstatechange = () => {
        const state = pc.iceConnectionState;
        setConnectionState(state);
        onConnectionStateChange?.(state);

        if (state === 'connected' || state === 'completed') {
          reconnectAttemptsRef.current = 0;
          setError(null);
          setIsConnecting(false);
        } else if (state === 'failed' || state === 'disconnected') {
          if (
            !isManualCloseRef.current &&
            reconnectAttemptsRef.current < maxReconnectAttempts
          ) {
            reconnectAttemptsRef.current += 1;
            const delay = reconnectDelay * reconnectAttemptsRef.current;
            setError(`연결 문제 - ${delay / 1000}초 후 재시도`);

            reconnectTimeoutRef.current = setTimeout(() => {
              connect();
            }, delay);
          }
        }
      };

      pc.ontrack = (event) => {
        if (!videoRef.current || !event.streams[0]) return;

        videoRef.current.srcObject = event.streams[0];
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play().catch(() => {
            const errorMsg = '비디오 재생 실패';
            setError(errorMsg);
            onError?.(errorMsg);
          });
        };
      };

      pc.addTransceiver('video', { direction: 'recvonly' });

      const offer = await pc.createOffer();
      console.log('original', offer.sdp);
      let modifiedSdp = offer.sdp || '';
      modifiedSdp = modifiedSdp.replace(
        /(a=rtpmap:96 VP8\/90000\r?\n)/,
        '$1a=fmtp:96 x-google-max-bitrate=10000;x-google-min-bitrate=3000;x-google-start-bitrate=5000\r\n'
      );
      modifiedSdp = modifiedSdp.replace(
        /(m=video.*\r?\n)/,
        '$1b=AS:10000\r\nb=TIAS:10000000\r\n'
      );
      console.log('Modified SDP:', modifiedSdp);
      // await pc.setLocalDescription(offer);
      await pc.setLocalDescription({
        type: offer.type,
        sdp: modifiedSdp,
      });

      const resp = await api.post(
        `webrtc/offer/${camId}`,
        pc.localDescription,
        {
          timeout: 10000,
        }
      );

      const answer = resp.data;

      if (!answer || !answer.type) {
        throw new Error('Invalid answer from server');
      }

      await pc.setRemoteDescription(answer);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '알 수 없는 오류';
      setError(`연결 실패: ${errorMsg}`);
      onError?.(`연결 실패: ${errorMsg}`);
      setIsConnecting(false);

      if (
        !isManualCloseRef.current &&
        reconnectAttemptsRef.current < maxReconnectAttempts
      ) {
        reconnectAttemptsRef.current += 1;
        const delay = reconnectDelay * reconnectAttemptsRef.current;

        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, delay);
      }
    }
  }, [
    camId,
    cleanup,
    maxReconnectAttempts,
    reconnectDelay,
    onError,
    onConnectionStateChange,
  ]);

  const reconnect = useCallback(() => {
    reconnectAttemptsRef.current = 0;
    setError(null);
    connect();
  }, [connect]);

  useEffect(() => {
    isManualCloseRef.current = false;
    connect();

    return () => {
      isManualCloseRef.current = true;
      cleanup();
      reconnectAttemptsRef.current = 0;
    };
  }, [camId, connect, cleanup]);

  return {
    videoRef,
    connectionState,
    error,
    isConnecting,
    reconnect,
  };
}
