import { motion } from 'framer-motion';

type Hit = { x: number; y: number; outside?: boolean };

export default function TargetOverlayView({
  hit,
  targetW,
  targetH,
  screenH,
  screenW,
}: {
  hit: Hit | null;
  targetW: number;
  targetH: number;
  screenW: number;
  screenH: number;
}) {
  return (
    <div className='relative'>
      {' '}
      {/* ✅ 상대 위치 컨테이너 */}
      {/* 과녁 SVG - 항상 표시 */}
      <svg
        width={targetW}
        height={targetH}
        viewBox={`0 0 ${targetW} ${targetH}`}
        className='shadow-lg'
      >
        {/* 테두리 */}
        <rect
          x={0}
          y={0}
          width={targetW}
          height={targetH}
          fill='rgba(255,255,255,0.02)'
          stroke='#0ff'
          strokeWidth={3}
          style={{ filter: 'drop-shadow(0 0 6px #0ff)' }}
        />

        {/* 세로선 */}
        {[1, 2].map((i) => (
          <line
            key={`v${i}`}
            x1={(targetW / 3) * i}
            y1={0}
            x2={(targetW / 3) * i}
            y2={targetH}
            stroke='rgba(255,255,255,0.6)'
            strokeWidth={1}
            strokeDasharray='6 4'
          />
        ))}

        {/* 가로선 */}
        {[1, 2].map((i) => (
          <line
            key={`h${i}`}
            x1={0}
            y1={(targetH / 3) * i}
            x2={targetW}
            y2={(targetH / 3) * i}
            stroke='rgba(255,255,255,0.6)'
            strokeWidth={1}
            strokeDasharray='6 4'
          />
        ))}

        {/* 번호 */}
        {Array.from({ length: 3 }).map((_, row) =>
          Array.from({ length: 3 }).map((_, col) => {
            const cx = (targetW / 3) * (col + 0.5);
            const cy = (targetH / 3) * (row + 0.5);
            const num = row * 3 + col + 1;
            return (
              <text
                key={num}
                x={cx}
                y={cy}
                fill='#0ff'
                fontSize={22}
                textAnchor='middle'
                dominantBaseline='middle'
                style={{
                  fontFamily: 'monospace',
                  textShadow: '0 0 6px #0ff',
                  fontWeight: 'bold',
                }}
              >
                {num}
              </text>
            );
          })
        )}

        {/* 과녁 내부 적중점 */}
        {hit && !hit.outside && (
          <g>
            <motion.circle
              cx={hit.x}
              cy={hit.y}
              r={0}
              fill='none'
              stroke='#0ff'
              strokeWidth={4}
              initial={{ r: 0, opacity: 1, strokeWidth: 4 }}
              animate={{ r: 50, opacity: 0, strokeWidth: 1 }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
            />
            <motion.circle
              cx={hit.x}
              cy={hit.y}
              r={0}
              fill='none'
              stroke='orange'
              strokeWidth={3}
              initial={{ r: 0, opacity: 1, strokeWidth: 3 }}
              animate={{ r: 35, opacity: 0, strokeWidth: 1 }}
              transition={{ duration: 0.6, ease: 'easeOut', delay: 0.1 }}
            />
            <circle
              cx={hit.x}
              cy={hit.y}
              r={18}
              fill='rgba(0,255,255,0.15)'
              style={{ filter: 'blur(8px)' }}
            />
            <motion.circle
              cx={hit.x}
              cy={hit.y}
              r={6}
              fill='orange'
              stroke='white'
              strokeWidth={2}
              style={{
                filter: 'drop-shadow(0 0 8px orange)',
              }}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 400, damping: 15 }}
            />
            <motion.circle
              cx={hit.x}
              cy={hit.y}
              r={6}
              fill='none'
              stroke='orange'
              strokeWidth={2}
              animate={{
                r: [6, 15, 6],
                opacity: [0.8, 0.2, 0.8],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          </g>
        )}
      </svg>
      {/* ✅ 과녁 외부 적중점 - SVG 위에 절대 위치로 표시 */}
      {hit?.outside && (
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className='absolute z-10'
          style={{
            left: (hit.x / screenW) * targetW,
            top: (hit.y / screenH) * targetH,
            transform: 'translate(-50%, -50%)',
          }}
        >
          <motion.div
            className='relative'
            animate={{
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          >
            <div className='w-12 h-12 bg-red-500 rounded-full opacity-20 blur-lg absolute -inset-2' />
            <div
              className='w-8 h-8 bg-red-500 rounded-full border-4 border-white relative z-10'
              style={{ filter: 'drop-shadow(0 0 8px red)' }}
            />
          </motion.div>

          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className='absolute top-12 left-1/2 -translate-x-1/2 whitespace-nowrap'
          >
            <span
              className='text-red-500 text-3xl font-bold'
              style={{ textShadow: '0 0 10px red' }}
            >
              MISS
            </span>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}
