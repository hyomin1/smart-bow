import { motion } from 'framer-motion';

interface Props {
  isVisible: boolean;
  isOnline: boolean;
}

export default function StreamingFooter({ isVisible, isOnline }: Props) {
  return (
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
                isOnline ? 'bg-green-400 animate-pulse' : 'bg-yellow-400'
              }`}
              style={{ boxShadow: '0 0 10px #4ade80' }}
            />
            <span className='text-gray-400 font-mono text-xs'>
              {isOnline ? 'SYSTEM ONLINE' : 'SYSTEM INITIALIZING'}
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
  );
}
