import { motion } from 'framer-motion';

interface Props {
  hit?: { x: number; y: number; inside: boolean } | null;
  frameSize: { w: number; h: number };
  polygon?: number[][] | null;
}

export default function TargetOverlayView({ hit, frameSize, polygon }: Props) {
  if (!polygon || polygon.length < 4) return null;

  // 좌표 명시적 이름 지정
  const [A, B, C, D] = polygon; // 시계방향: 좌상, 우상, 우하, 좌하

  // linear interpolation helper
  const lerp = (p1: number[], p2: number[], t: number) => [
    p1[0] + (p2[0] - p1[0]) * t,
    p1[1] + (p2[1] - p1[1]) * t,
  ];

  // 🔹 세로선 (좌->우로 3등분)
  const verticalLines = [1 / 3, 2 / 3].map((t) => {
    const top = lerp(A, B, t);
    const bottom = lerp(D, C, t);
    return { top, bottom };
  });

  // 🔹 가로선 (상->하로 3등분)
  const horizontalLines = [1 / 3, 2 / 3].map((t) => {
    const left = lerp(A, D, t);
    const right = lerp(B, C, t);
    return { left, right };
  });

  // 🔹 번호 위치 (3x3 grid center)
  const numbers = Array.from({ length: 3 }).flatMap((_, row) =>
    Array.from({ length: 3 }).map((_, col) => {
      const topLeft = lerp(A, B, (col + 0) / 3);
      const topRight = lerp(A, B, (col + 1) / 3);
      const bottomLeft = lerp(D, C, (col + 0) / 3);
      const bottomRight = lerp(D, C, (col + 1) / 3);
      const leftMid = lerp(topLeft, bottomLeft, (row + 0.5) / 3);
      const rightMid = lerp(topRight, bottomRight, (row + 0.5) / 3);
      const center = lerp(leftMid, rightMid, 0.5);
      return { x: center[0], y: center[1], num: row * 3 + col + 1 };
    })
  );
  const SCALE = 1.5;
  return (
    <svg
      viewBox={`0 0 ${frameSize.w} ${frameSize.h}`}
      preserveAspectRatio='xMidYMid meet'
      className='absolute inset-0'
      style={{
        width: '100%',
        height: '100%',
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: `translate(-50%, -50%) scale(${SCALE})`,
        transformOrigin: 'center center',
      }}
    >
      {/* ✅ polygon 외곽 */}
      <polygon
        points={polygon.map(([x, y]) => `${x},${y}`).join(' ')}
        fill='rgba(0,255,0,0.08)'
        stroke='#0ff'
        strokeWidth={4}
        style={{ filter: 'drop-shadow(0 0 6px #0ff)' }}
      />

      {/* ✅ polygon 내부 격자선 */}
      {verticalLines.map(({ top, bottom }, i) => (
        <line
          key={`v${i}`}
          x1={top[0]}
          y1={top[1]}
          x2={bottom[0]}
          y2={bottom[1]}
          stroke='rgba(255,255,255,0.6)'
          strokeWidth={1}
          strokeDasharray='6 4'
        />
      ))}
      {horizontalLines.map(({ left, right }, i) => (
        <line
          key={`h${i}`}
          x1={left[0]}
          y1={left[1]}
          x2={right[0]}
          y2={right[1]}
          stroke='rgba(255,255,255,0.6)'
          strokeWidth={1}
          strokeDasharray='6 4'
        />
      ))}

      {/* ✅ 번호 */}
      {numbers.map(({ x, y, num }) => (
        <text
          key={num}
          x={x}
          y={y}
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
      ))}

      {/* 🎯 hit 애니메이션 */}
      {hit && (
        <g>
          {/* 외곽 펄스 링 (가장 큰 효과) */}
          <motion.circle
            cx={hit.x}
            cy={hit.y}
            r={20}
            fill='none'
            stroke={
              hit.inside ? 'rgba(255, 215, 0, 0.4)' : 'rgba(220, 50, 50, 0.4)'
            }
            strokeWidth={1}
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{
              scale: [0.8, 1.5, 0.8],
              opacity: [0.6, 0, 0.6],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeOut',
            }}
          />

          {/* 글로우 배경 */}
          <motion.circle
            cx={hit.x}
            cy={hit.y}
            r={16}
            fill={
              hit.inside ? 'rgba(255, 200, 50, 0.3)' : 'rgba(220, 50, 50, 0.3)'
            }
            style={{
              filter: `blur(12px)`,
            }}
            animate={{
              scale: [1, 1.15, 1],
              opacity: [0.6, 0.8, 0.6],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />

          {/* 중간 글로우 레이어 */}
          <motion.circle
            cx={hit.x}
            cy={hit.y}
            r={12}
            fill={
              hit.inside ? 'rgba(255, 190, 80, 0.4)' : 'rgba(200, 60, 60, 0.4)'
            }
            style={{
              filter: `blur(8px) drop-shadow(0 0 8px ${
                hit.inside ? 'rgba(255,215,0,0.6)' : 'rgba(220,50,50,0.6)'
              })`,
            }}
            animate={{
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 1.2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />

          {/* 회전하는 외곽 링 */}
          <motion.circle
            cx={hit.x}
            cy={hit.y}
            r={11}
            fill='none'
            stroke={
              hit.inside ? 'rgba(255,223,100,0.6)' : 'rgba(230,80,80,0.6)'
            }
            strokeWidth={1.5}
            strokeDasharray='3 3'
            animate={{
              rotate: 360,
              opacity: [0.4, 0.8, 0.4],
            }}
            transition={{
              rotate: { duration: 3, repeat: Infinity, ease: 'linear' },
              opacity: { duration: 1.5, repeat: Infinity, ease: 'easeInOut' },
            }}
          />

          {/* 중심 코어 - 그라디언트 효과 */}
          <defs>
            <radialGradient id={`hit-gradient-${hit.x}-${hit.y}`}>
              <stop
                offset='0%'
                stopColor={hit.inside ? '#fffef0' : '#ffe8e8'}
                stopOpacity={1}
              />
              <stop
                offset='60%'
                stopColor={hit.inside ? '#ffd700' : '#dc3232'}
                stopOpacity={1}
              />
              <stop
                offset='100%'
                stopColor={hit.inside ? '#daa520' : '#a01010'}
                stopOpacity={1}
              />
            </radialGradient>
          </defs>

          <motion.circle
            cx={hit.x}
            cy={hit.y}
            r={7.5}
            fill={`url(#hit-gradient-${hit.x}-${hit.y})`}
            style={{
              filter: `drop-shadow(0 0 10px ${
                hit.inside ? 'rgba(255,215,0,0.9)' : 'rgba(220,50,50,0.9)'
              }) drop-shadow(0 0 4px white)`,
            }}
            initial={{ scale: 0, rotate: 0 }}
            animate={{
              scale: 1,
              rotate: 360,
            }}
            transition={{
              scale: { type: 'spring', stiffness: 400, damping: 15 },
              rotate: { duration: 8, repeat: Infinity, ease: 'linear' },
            }}
          />

          {/* 하이라이트 */}
          <motion.circle
            cx={hit.x - 2}
            cy={hit.y - 2}
            r={2.5}
            fill='rgba(255, 255, 255, 0.9)'
            style={{
              filter: 'blur(1px)',
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: [0.6, 0.9, 0.6] }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />

          {/* 파티클 효과 */}
          {[0, 120, 240].map((angle, i) => (
            <motion.circle
              key={i}
              cx={hit.x}
              cy={hit.y}
              r={1.5}
              fill={hit.inside ? '#ffe066' : '#ff6666'}
              initial={{ opacity: 0 }}
              animate={{
                x: Math.cos((angle * Math.PI) / 180) * 15,
                y: Math.sin((angle * Math.PI) / 180) * 15,
                opacity: [0, 0.8, 0],
                scale: [0, 1, 0],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.2,
                ease: 'easeOut',
              }}
            />
          ))}

          {/* 메인 테두리 링 */}
          <motion.circle
            cx={hit.x}
            cy={hit.y}
            r={10}
            fill='none'
            stroke={
              hit.inside ? 'rgba(255,230,120,0.95)' : 'rgba(240,80,80,0.95)'
            }
            strokeWidth={2}
            style={{
              filter: `drop-shadow(0 0 6px ${
                hit.inside ? 'rgba(255,215,0,0.7)' : 'rgba(220,50,50,0.7)'
              })`,
            }}
            animate={{
              r: [9, 12, 9],
              opacity: [0.9, 0.5, 0.9],
            }}
            transition={{
              duration: 1.8,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        </g>
      )}
    </svg>
  );
}
