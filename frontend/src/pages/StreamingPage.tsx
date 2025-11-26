import { useParams } from 'react-router-dom';
import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import CamWebRTC from '../components/CamWebRTC';
import { useWebSocket } from '../hooks/useWebSocket';
import { useVideoSize } from '../hooks/useVideoSize';
import { useHit } from '../hooks/useHit';
import TargetOverlayView from '../components/TargetOverlayView';
import useVisibility from '../hooks/useVisibility';
import { getWebSocketStatus, isSystemOnline } from '../utils/webrtc';
import StreamingHeader from '../components/StreamingHeader';
import StreamingFooter from '../components/StreamingFooter';

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

  const wsStatus = getWebSocketStatus(readyState);
  const hasError = wsError || targetCamError || shooterCamError;
  const currentError = wsError || targetCamError || shooterCamError;
  const systemOnline = isSystemOnline(
    readyState,
    targetCamState,
    shooterCamState
  );

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
          backgroundSize: '350px 50px',
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

      <StreamingHeader
        isVisible={isVisible}
        wsStatus={wsStatus}
        retryCount={retryCount}
        targetCamState={targetCamState}
        shooterCamState={shooterCamState}
        camId={camId}
        hasError={!!hasError}
        currentError={currentError}
        onManualReconnect={manualReconnect}
      />

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

      <StreamingFooter isVisible={isVisible} isOnline={systemOnline} />
    </div>
  );
}
