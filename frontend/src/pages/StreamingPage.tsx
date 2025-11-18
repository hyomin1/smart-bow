import { useParams } from 'react-router-dom';
import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import CamWebRTC from '../components/CamWebRTC';
import { useWebSocket } from '../hooks/useWebSocket';
import { useVideoSize } from '../hooks/useVideoSize';
import { useHit } from '../hooks/useHit';
import TargetOverlayView from '../components/TargetOverlayView';

export default function StreamingPage() {
  const { camId } = useParams<{ camId: string }>();

  const videoRef = useRef<HTMLVideoElement>(null);
  const [polygon, setPolygon] = useState<number[][] | null>(null);

  const { send, message, readyState } = useWebSocket(camId || '');
  const renderRect = useVideoSize(videoRef);
  const hit = useHit(message);

  useEffect(() => {
    if (!renderRect || !camId) return;
    if (readyState !== WebSocket.OPEN) return;

    send({
      type: 'video_size',
      width: renderRect.w,
      height: renderRect.h,
    });
    return () => {};
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

  const connectionStatus =
    readyState === WebSocket.OPEN
      ? '연결됨'
      : readyState === WebSocket.CONNECTING
      ? '연결중'
      : '연결 끊김';

  return (
    <div className='relative h-screen bg-black overflow-hidden'>
      {/* Animated background */}
      <div className='absolute inset-0 bg-gradient-to-br from-purple-950 via-black to-cyan-950 opacity-50' />

      {/* Grid overlay */}
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

      {/* Scanline effect */}
      <motion.div
        className='absolute inset-0 pointer-events-none'
        style={{
          background:
            'linear-gradient(0deg, transparent 0%, rgba(0, 255, 255, 0.03) 50%, transparent 100%)',
          backgroundSize: '100% 4px',
        }}
        animate={{ y: [0, 100] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
      />

      {/* Top HUD Bar */}
      <motion.div
        className='absolute top-0 left-0 right-0 z-20 h-12 bg-black bg-opacity-60 backdrop-blur-sm border-b border-cyan-500'
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        style={{ boxShadow: '0 0 15px rgba(0, 255, 255, 0.3)' }}
      >
        <div className='flex items-center justify-between h-full px-6'>
          <div className='flex items-center gap-4'>
            <motion.div
              className='w-2 h-2 rounded-full bg-cyan-400'
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 2, repeat: Infinity }}
              style={{ boxShadow: '0 0 10px #00ffff' }}
            />
            <span className='text-cyan-400 font-mono text-xl tracking-wider font-bold'>
              SMARTBOW SYSTEM
            </span>
          </div>

          <div className='flex items-center gap-6'>
            <div className='flex items-center gap-2'>
              <span className='text-gray-400 font-mono text-sm'>STATUS:</span>
              <motion.span
                className={`font-mono text-sm font-bold ${
                  connectionStatus === '연결됨'
                    ? 'text-green-400'
                    : connectionStatus === '연결중'
                    ? 'text-yellow-400'
                    : 'text-red-400'
                }`}
                animate={{
                  opacity: connectionStatus === '연결중' ? [0.5, 1, 0.5] : 1,
                }}
                transition={{
                  duration: 1,
                  repeat: connectionStatus === '연결중' ? Infinity : 0,
                }}
              >
                {connectionStatus}
              </motion.span>
            </div>

            <div className='flex items-center gap-2'>
              <span className='text-gray-400 font-mono text-sm'>CAM ID:</span>
              <span className='text-pink-400 font-mono text-sm font-bold'>
                {camId}
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Main content */}
      <div className='flex h-full py-12'>
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
                <CamWebRTC camId={camId} ref={videoRef} />

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
                      />
                    </motion.div>
                  </AnimatePresence>
                )}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Divider with glow */}
        <div
          className='relative w-1 bg-gradient-to-b from-transparent via-pink-500 to-transparent'
          style={{ boxShadow: '0 0 20px rgba(236, 72, 153, 0.6)' }}
        />

        {/* Right camera - Shooter view */}
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
              <CamWebRTC camId='shooter1' cover />
            </div>
          </div>
        </motion.div>
      </div>

      {/* Bottom HUD Bar */}
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
                className='w-2 h-2 bg-green-400 rounded-full animate-pulse'
                style={{ boxShadow: '0 0 10px #4ade80' }}
              />
              <span className='text-gray-400 font-mono text-xs'>
                SYSTEM ONLINE
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
                animate={{ scaleY: [0.5, 1, 0.5] }}
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
