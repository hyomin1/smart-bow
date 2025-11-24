import { useParams } from 'react-router-dom';
import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import CamWebRTC from '../components/CamWebRTC';
import { useWebSocket } from '../hooks/useWebSocket';
import { useVideoSize } from '../hooks/useVideoSize';
import { useHit } from '../hooks/useHit';
import TargetOverlayView from '../components/TargetOverlayView';
import useVisibility from '../hooks/useVisibility';

export default function StreamingPage() {
  const { camId } = useParams<{ camId: string }>();

  const videoRef = useRef<HTMLVideoElement>(null);
  const [polygon, setPolygon] = useState<number[][] | null>(null);

  const {
    send,
    message,
    readyState,
    error: wsError,
    retryCount,
    manualReconnect,
  } = useWebSocket(camId || '');

  const [targetCamState, setTargetCamState] =
    useState<RTCIceConnectionState>('new');
  const [shooterCamState, setShooterCamState] =
    useState<RTCIceConnectionState>('new');
  const [targetCamError, setTargetCamError] = useState<string | null>(null);
  const [shooterCamError, setShooterCamError] = useState<string | null>(null);

  const renderRect = useVideoSize(videoRef);
  const hit = useHit(message);

  const isVisible = useVisibility();

  useEffect(() => {
    if (!renderRect || !camId || readyState !== WebSocket.OPEN) return;

    send({
      type: 'video_size',
      width: renderRect.w,
      height: renderRect.h,
    });
  }, [renderRect, camId, send, readyState]);

  useEffect(() => {
    if (!message) return;
    if (message.type === 'polygon') {
      setPolygon(message.points);
    }
  }, [message]);

  if (!camId) {
    return (
      <div className='flex items-center justify-center h-screen bg-black'>
        <span className='text-red-500 text-xl font-mono'>
          ERROR: INVALID CAMERA PATH
        </span>
      </div>
    );
  }

  const getWebSocketStatus = () => {
    if (readyState === WebSocket.OPEN)
      return { label: '연결됨', color: 'text-green-400' };
    if (readyState === WebSocket.CONNECTING)
      return { label: '연결중', color: 'text-yellow-400' };
    return { label: '연결 끊김', color: 'text-red-400' };
  };

  const getStateColor = (state: RTCIceConnectionState) => {
    switch (state) {
      case 'connected':
      case 'completed':
        return 'text-green-400';
      case 'checking':
      case 'new':
        return 'text-yellow-400';
      case 'disconnected':
      case 'failed':
      case 'closed':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getStateLabel = (state: RTCIceConnectionState) => {
    switch (state) {
      case 'connected':
      case 'completed':
        return '연결됨';
      case 'checking':
        return '연결중';
      case 'new':
        return '대기';
      case 'disconnected':
        return '끊김';
      case 'failed':
        return '실패';
      case 'closed':
        return '종료';
      default:
        return state;
    }
  };

  const isSystemOnline = () => {
    return (
      readyState === WebSocket.OPEN &&
      (targetCamState === 'connected' || targetCamState === 'completed') &&
      (shooterCamState === 'connected' || shooterCamState === 'completed')
    );
  };

  const wsStatus = getWebSocketStatus();
  const hasError = wsError || targetCamError || shooterCamError;
  const currentError = wsError || targetCamError || shooterCamError;

  return (
    <div className='relative h-screen bg-black overflow-hidden'>
      <div className='absolute inset-0 bg-gradient-to-br from-purple-950 via-black to-cyan-950 opacity-50' />

      <div
        className='absolute inset-0 opacity-10'
        style={{
          backgroundImage: `
            linear-gradient(0deg, transparent 24%, rgba(0, 255, 255, 0.3) 25%, rgba(0, 255, 255, 0.3) 26%, transparent 27%, transparent 74%, rgba(0, 255, 255, 0.3) 75%, rgba(0, 255, 255, 0.3) 76%, transparent 77%, transparent),
            linear-gradient(90deg, transparent 24%, rgba(0, 255, 255, 0.3) 25%, rgba(0, 255, 255, 0.3) 26%, transparent 27%, transparent 74%, rgba(0, 255, 255, 0.3) 75%, rgba(0, 255, 255, 0.3) 76%, transparent 77%, transparent)
          `,
          backgroundSize: '50px 50px',
        }}
      />

      <motion.div
        className='absolute inset-0 pointer-events-none'
        style={{
          background:
            'linear-gradient(0deg, transparent 0%, rgba(0, 255, 255, 0.03) 50%, transparent 100%)',
          backgroundSize: '100% 4px',
        }}
        animate={isVisible ? { y: [0, 100] } : { y: 0 }}
        transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
      />

      <motion.div
        className='absolute top-0 left-0 right-0 z-20 h-16 bg-black bg-opacity-60 backdrop-blur-sm border-b border-cyan-500'
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        style={{ boxShadow: '0 0 15px rgba(0, 255, 255, 0.3)' }}
      >
        <div className='flex items-center justify-between h-full px-6'>
          <div className='flex items-center gap-4'>
            <motion.div
              className='w-2 h-2 rounded-full bg-cyan-400'
              animate={isVisible ? { opacity: [0.3, 1, 0.3] } : { opacity: 1 }}
              transition={{ duration: 2, repeat: Infinity }}
              style={{ boxShadow: '0 0 10px #00ffff' }}
            />
            <span className='text-cyan-400 font-mono text-xl tracking-wider font-bold'>
              SMARTBOW SYSTEM
            </span>
          </div>

          <div className='flex items-center gap-6'>
            <div className='flex items-center gap-2'>
              <span className='text-gray-400 font-mono text-xs'>WS:</span>
              <motion.span
                className={`font-mono text-xs font-bold ${wsStatus.color}`}
                animate={{
                  opacity: wsStatus.label === '연결중' ? [0.5, 1, 0.5] : 1,
                }}
                transition={{
                  duration: 1,
                  repeat: wsStatus.label === '연결중' ? Infinity : 0,
                }}
              >
                {wsStatus.label}
              </motion.span>
              {retryCount > 0 && (
                <span className='text-yellow-400 font-mono text-xs'>
                  ({retryCount}/5)
                </span>
              )}
            </div>

            <div className='flex items-center gap-2'>
              <span className='text-gray-400 font-mono text-xs'>TARGET:</span>
              <span
                className={`font-mono text-xs font-bold ${getStateColor(
                  targetCamState
                )}`}
              >
                {getStateLabel(targetCamState)}
              </span>
            </div>

            <div className='flex items-center gap-2'>
              <span className='text-gray-400 font-mono text-xs'>SHOOTER:</span>
              <span
                className={`font-mono text-xs font-bold ${getStateColor(
                  shooterCamState
                )}`}
              >
                {getStateLabel(shooterCamState)}
              </span>
            </div>

            <div className='flex items-center gap-2'>
              <span className='text-gray-400 font-mono text-xs'>CAM:</span>
              <span className='text-pink-400 font-mono text-xs font-bold'>
                {camId}
              </span>
            </div>
          </div>
        </div>

        {hasError && (
          <motion.div
            className='absolute top-full left-0 right-0 bg-red-900 bg-opacity-90 border-b border-red-500 px-6 py-2'
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className='flex items-center justify-between'>
              <div className='flex items-center gap-3'>
                <span className='text-red-400 font-mono text-sm'>⚠️</span>
                <span className='text-red-200 font-mono text-sm'>
                  {currentError}
                </span>
              </div>
              {wsError && retryCount >= 5 && (
                <button
                  onClick={manualReconnect}
                  className='px-3 py-1 bg-red-600 hover:bg-red-700 text-white font-mono text-xs rounded transition-colors'
                >
                  수동 재연결
                </button>
              )}
            </div>
          </motion.div>
        )}
      </motion.div>

      <div className='flex h-full pt-16 pb-12'>
        <motion.div
          className='w-1/2 h-full relative p-3'
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <div className='relative h-full'>
            <motion.div
              className='absolute -top-3 left-8 px-4 py-1 bg-cyan-500 text-black font-mono text-xs font-bold z-10'
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.3, delay: 0.5 }}
              style={{ boxShadow: '0 0 20px rgba(0, 255, 255, 0.6)' }}
            >
              TARGET ZONE
            </motion.div>

            <div
              className='relative h-full bg-black border-2 border-cyan-500 overflow-hidden'
              style={{
                boxShadow:
                  'inset 0 0 30px rgba(0, 255, 255, 0.2), 0 0 30px rgba(0, 255, 255, 0.3)',
              }}
            >
              <div className='relative w-full h-full'>
                <CamWebRTC
                  camId={camId}
                  ref={videoRef}
                  onError={setTargetCamError}
                  onConnectionStateChange={setTargetCamState}
                />

                {hit && polygon && renderRect && (
                  <AnimatePresence>
                    <motion.div
                      key='overlay-bg'
                      className='absolute top-0 left-0 w-full h-full bg-black bg-opacity-80 z-10'
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.25 }}
                    />

                    <motion.div
                      key='overlay-popup'
                      className='absolute top-0 left-0 w-full h-full z-20'
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 1.05 }}
                      transition={{ duration: 0.35, ease: 'easeOut' }}
                    >
                      <TargetOverlayView
                        hit={hit}
                        polygon={polygon}
                        renderRect={renderRect}
                        isVisible={isVisible}
                      />
                    </motion.div>
                  </AnimatePresence>
                )}
              </div>
            </div>
          </div>
        </motion.div>

        <div
          className='relative w-1 bg-gradient-to-b from-transparent via-pink-500 to-transparent'
          style={{ boxShadow: '0 0 20px rgba(236, 72, 153, 0.6)' }}
        />

        <motion.div
          className='w-1/2 h-full relative p-3'
          initial={{ x: 100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <div className='relative h-full'>
            <motion.div
              className='absolute -top-3 left-8 px-4 py-1 bg-pink-500 text-black font-mono text-xs font-bold z-10'
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.3, delay: 0.5 }}
              style={{ boxShadow: '0 0 20px rgba(236, 72, 153, 0.6)' }}
            >
              SHOOTER CAM
            </motion.div>

            <div
              className='h-full bg-black border-2 border-pink-500'
              style={{
                boxShadow:
                  'inset 0 0 30px rgba(236, 72, 153, 0.2), 0 0 30px rgba(236, 72, 153, 0.3)',
              }}
            >
              <CamWebRTC
                camId='shooter1'
                cover
                onError={setShooterCamError}
                onConnectionStateChange={setShooterCamState}
              />
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div
        className='absolute bottom-0 left-0 right-0 z-20 h-12 bg-black bg-opacity-60 backdrop-blur-sm border-t-2 border-pink-500'
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut', delay: 0.3 }}
        style={{ boxShadow: '0 0 20px rgba(236, 72, 153, 0.3)' }}
      >
        <div className='flex items-center justify-between h-full px-6'>
          <div className='flex items-center gap-8'>
            <div className='flex items-center gap-2'>
              <div
                className={`w-2 h-2 rounded-full ${
                  isSystemOnline()
                    ? 'bg-green-400 animate-pulse'
                    : 'bg-yellow-400'
                }`}
                style={{ boxShadow: '0 0 10px #4ade80' }}
              />
              <span className='text-gray-400 font-mono text-xs'>
                {isSystemOnline() ? 'SYSTEM ONLINE' : 'SYSTEM INITIALIZING'}
              </span>
            </div>

            <div className='text-gray-500 font-mono text-xs'>
              © 2025 SmartBow. All rights reserved
            </div>
          </div>

          <div className='flex items-center gap-4'>
            {[...Array(5)].map((_, i) => (
              <motion.div
                key={i}
                className='w-1 h-4 bg-cyan-400'
                animate={isVisible ? { scaleY: [0.5, 1, 0.5] } : { scaleY: 1 }}
                transition={{ duration: 1, repeat: Infinity, delay: i * 0.1 }}
                style={{ boxShadow: '0 0 10px rgba(0, 255, 255, 0.5)' }}
              />
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
