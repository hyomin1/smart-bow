import { motion } from 'framer-motion';
import { getStateColor, getStateLabel } from '../utils/webrtc';

interface Props {
  isVisible: boolean;
  wsStatus: { label: string; color: string };
  retryCount: number;
  targetCamState: RTCIceConnectionState;
  shooterCamState: RTCIceConnectionState;
  camId: string;
  hasError: boolean;
  currentError: string | null;
  onManualReconnect: () => void;
}

export default function StreamingHeader({
  isVisible,
  wsStatus,
  retryCount,
  targetCamState,
  shooterCamState,
  camId,
  hasError,
  currentError,
  onManualReconnect,
}: Props) {
  return (
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
            {hasError && retryCount >= 5 && (
              <button
                onClick={onManualReconnect}
                className='px-3 py-1 bg-red-600 hover:bg-red-700 text-white font-mono text-xs rounded transition-colors'
              >
                수동 재연결
              </button>
            )}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
