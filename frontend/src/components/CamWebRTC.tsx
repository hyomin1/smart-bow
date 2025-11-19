import { forwardRef, useImperativeHandle } from 'react';
import { useWebRTC } from '../hooks/useWebRTC';

interface Props {
  camId: string;
  cover?: boolean;
  onError?: (error: string) => void;
  onConnectionStateChange?: (state: RTCIceConnectionState) => void;
  maxReconnectAttempts?: number;
  reconnectDelay?: number;
}

const CamWebRTC = forwardRef<HTMLVideoElement, Props>(
  (
    {
      camId,
      cover,
      onError,
      onConnectionStateChange,
      maxReconnectAttempts,
      reconnectDelay,
    },
    ref
  ) => {
    const { videoRef, connectionState, error, isConnecting } = useWebRTC({
      camId,
      onError,
      onConnectionStateChange,
      maxReconnectAttempts,
      reconnectDelay,
    });

    useImperativeHandle(ref, () => videoRef.current as HTMLVideoElement);

    const getStateLabel = () => {
      if (isConnecting) return '연결 중...';
      if (error) return '연결 오류';

      switch (connectionState) {
        case 'connected':
        case 'completed':
          return null;
        case 'checking':
          return '연결 확인 중...';
        case 'new':
          return '대기 중...';
        case 'disconnected':
          return '연결 끊김';
        case 'failed':
          return '연결 실패';
        case 'closed':
          return '연결 종료';
        default:
          return null;
      }
    };

    const stateLabel = getStateLabel();

    return (
      <div className='relative w-full h-full'>
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className={`w-full h-full bg-black ${
            cover ? 'object-cover' : 'object-contain'
          }`}
        />

        {error && (
          <div className='absolute inset-0 flex items-center justify-center bg-black bg-opacity-70 z-10'>
            <div className='text-center p-4'>
              <div className='text-red-500 text-lg font-mono mb-2'>
                ⚠️ 연결 오류
              </div>
              <div className='text-gray-300 text-sm font-mono'>{error}</div>
            </div>
          </div>
        )}

        {stateLabel && !error && (
          <div className='absolute top-2 right-2 bg-yellow-500 bg-opacity-80 px-3 py-1 rounded text-xs font-mono text-black z-10'>
            {stateLabel}
          </div>
        )}
      </div>
    );
  }
);

CamWebRTC.displayName = 'CamWebRTC';

export default CamWebRTC;
