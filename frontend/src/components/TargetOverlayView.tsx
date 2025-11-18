import { motion } from 'framer-motion';

interface Props {
  hit: [number, number];
  polygon: number[][];
  renderRect: { w: number; h: number };
}

export default function TargetOverlayView({ hit, polygon, renderRect }: Props) {
  if (!polygon || polygon.length < 4) return null;

  const lerp = (p1: number[], p2: number[], t: number) => [
    p1[0] + (p2[0] - p1[0]) * t,
    p1[1] + (p2[1] - p1[1]) * t,
  ];

  // 폴리곤의 중심 계산
  const centerX = polygon.reduce((sum, p) => sum + p[0], 0) / polygon.length;
  const centerY = polygon.reduce((sum, p) => sum + p[1], 0) / polygon.length;

  // 화면 중앙
  const screenCenterX = renderRect.w / 2;
  const screenCenterY = renderRect.h / 2;

  // 확대 비율
  const scale = 1.3;

  // 확대 + 중앙 이동
  const scaledPolygon = polygon.map(([x, y]) => [
    screenCenterX + (x - centerX) * scale,
    screenCenterY + (y - centerY) * scale,
  ]);

  const [sA, sB, sC, sD] = scaledPolygon;

  const verticalLines = [1 / 3, 2 / 3].map((t) => ({
    top: lerp(sA, sB, t),
    bottom: lerp(sD, sC, t),
  }));

  const horizontalLines = [1 / 3, 2 / 3].map((t) => ({
    left: lerp(sA, sD, t),
    right: lerp(sB, sC, t),
  }));

  // 히트 좌표도 변환
  const scaledHit = hit
    ? [
        screenCenterX + (hit[0] - centerX) * scale,
        screenCenterY + (hit[1] - centerY) * scale,
      ]
    : null;

  return (
    <svg
      width={renderRect.w}
      height={renderRect.h}
      viewBox={`0 0 ${renderRect.w} ${renderRect.h}`}
      className='absolute inset-0'
      preserveAspectRatio='none'
      style={{
        position: 'absolute',
        inset: 0,
      }}
    >
      <defs>
        <filter id='glow'>
          <feGaussianBlur stdDeviation='2' result='coloredBlur' />
          <feMerge>
            <feMergeNode in='coloredBlur' />
            <feMergeNode in='SourceGraphic' />
          </feMerge>
        </filter>

        <filter id='strongGlow'>
          <feGaussianBlur stdDeviation='4' result='coloredBlur' />
          <feMerge>
            <feMergeNode in='coloredBlur' />
            <feMergeNode in='SourceGraphic' />
          </feMerge>
        </filter>

        <linearGradient id='borderGradient' x1='0%' y1='0%' x2='100%' y2='100%'>
          <stop offset='0%' stopColor='#00ffff' stopOpacity='0.8' />
          <stop offset='50%' stopColor='#00ff88' stopOpacity='0.9' />
          <stop offset='100%' stopColor='#00ffff' stopOpacity='0.8' />
        </linearGradient>

        <radialGradient id='hitGradient'>
          <stop offset='0%' stopColor='#ffd700' stopOpacity='0.8' />
          <stop offset='70%' stopColor='#ffaa00' stopOpacity='0.4' />
          <stop offset='100%' stopColor='#ff8800' stopOpacity='0' />
        </radialGradient>
      </defs>

      {/* 배경 오버레이 */}
      <polygon
        points={scaledPolygon.map(([x, y]) => `${x},${y}`).join(' ')}
        fill='rgba(0,255,200,0.02)'
      />

      {/* 메인 테두리 - 애니메이션 */}
      <motion.polygon
        points={scaledPolygon.map(([x, y]) => `${x},${y}`).join(' ')}
        fill='none'
        stroke='url(#borderGradient)'
        strokeWidth={2}
        filter='url(#glow)'
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{
          pathLength: 1,
          opacity: 1,
          strokeWidth: [2, 2.5, 2],
        }}
        transition={{
          pathLength: { duration: 1.5, ease: 'easeInOut' },
          opacity: { duration: 0.5 },
          strokeWidth: { duration: 2, repeat: Infinity, ease: 'easeInOut' },
        }}
      />

      {/* 그리드 라인 - 세로 */}
      {verticalLines.map(({ top, bottom }, i) => (
        <motion.line
          key={`v${i}`}
          x1={top[0]}
          y1={top[1]}
          x2={bottom[0]}
          y2={bottom[1]}
          stroke='rgba(0,255,255,0.2)'
          strokeWidth={1}
          strokeDasharray='8 6'
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 1 }}
          transition={{ duration: 1, delay: 0.3 + i * 0.1 }}
        />
      ))}

      {/* 그리드 라인 - 가로 */}
      {horizontalLines.map(({ left, right }, i) => (
        <motion.line
          key={`h${i}`}
          x1={left[0]}
          y1={left[1]}
          x2={right[0]}
          y2={right[1]}
          stroke='rgba(0,255,255,0.2)'
          strokeWidth={1}
          strokeDasharray='8 6'
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 1 }}
          transition={{ duration: 1, delay: 0.5 + i * 0.1 }}
        />
      ))}

      {/* 격자 번호 */}
      {(() => {
        const cellNumbers = [
          [1, 2, 3],
          [4, 5, 6],
          [7, 8, 9],
        ];

        const getCellCenter = (row: number, col: number) => {
          const topLeft = lerp(
            lerp(sA, sB, col / 3),
            lerp(sD, sC, col / 3),
            row / 3
          );
          const bottomRight = lerp(
            lerp(sA, sB, (col + 1) / 3),
            lerp(sD, sC, (col + 1) / 3),
            (row + 1) / 3
          );
          return [
            (topLeft[0] + bottomRight[0]) / 2,
            (topLeft[1] + bottomRight[1]) / 2,
          ];
        };

        return cellNumbers.flatMap((row, rowIdx) =>
          row.map((num, colIdx) => {
            const [x, y] = getCellCenter(rowIdx, colIdx);
            return (
              <motion.text
                key={`cell-${num}`}
                x={x}
                y={y}
                textAnchor='middle'
                dominantBaseline='middle'
                fill='#00ffff'
                fontSize='32'
                fontWeight='normal'
                opacity={0.3}
                filter='url(#glow)'
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 0.3, scale: 1 }}
                transition={{
                  duration: 0.5,
                  delay: 0.8 + (rowIdx * 3 + colIdx) * 0.05,
                }}
                style={{ pointerEvents: 'none', userSelect: 'none' }}
              >
                {num}
              </motion.text>
            );
          })
        );
      })()}

      {/* 히트 마커 */}
      {scaledHit && (
        <g>
          {/* 외곽 펄스 링 1 */}
          <motion.circle
            cx={scaledHit[0]}
            cy={scaledHit[1]}
            r={20}
            fill='none'
            stroke='rgba(255,215,0,0.6)'
            strokeWidth={2}
            initial={{ r: 10, opacity: 0 }}
            animate={{
              r: [10, 40, 60],
              opacity: [0.8, 0.4, 0],
              strokeWidth: [3, 2, 1],
            }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeOut' }}
          />

          {/* 외곽 펄스 링 2 */}
          <motion.circle
            cx={scaledHit[0]}
            cy={scaledHit[1]}
            r={20}
            fill='none'
            stroke='rgba(255,170,0,0.8)'
            strokeWidth={2.5}
            initial={{ r: 10, opacity: 0 }}
            animate={{
              r: [10, 35, 50],
              opacity: [1, 0.5, 0],
            }}
            transition={{
              duration: 1.2,
              repeat: Infinity,
              ease: 'easeOut',
              delay: 0.3,
            }}
          />

          {/* 중간 글로우 */}
          <motion.circle
            cx={scaledHit[0]}
            cy={scaledHit[1]}
            r={18}
            fill='url(#hitGradient)'
            animate={{
              scale: [1, 1.15, 1],
              opacity: [0.4, 0.6, 0.4],
            }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />

          {/* 회전하는 크로스헤어 */}
          <motion.g
            animate={{ rotate: 360 }}
            transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
            style={{ transformOrigin: `${scaledHit[0]}px ${scaledHit[1]}px` }}
          >
            <line
              x1={scaledHit[0] - 15}
              y1={scaledHit[1]}
              x2={scaledHit[0] - 8}
              y2={scaledHit[1]}
              stroke='#ffaa00'
              strokeWidth={2}
              opacity={0.8}
            />
            <line
              x1={scaledHit[0] + 8}
              y1={scaledHit[1]}
              x2={scaledHit[0] + 15}
              y2={scaledHit[1]}
              stroke='#ffaa00'
              strokeWidth={2}
              opacity={0.8}
            />
            <line
              x1={scaledHit[0]}
              y1={scaledHit[1] - 15}
              x2={scaledHit[0]}
              y2={scaledHit[1] - 8}
              stroke='#ffaa00'
              strokeWidth={2}
              opacity={0.8}
            />
            <line
              x1={scaledHit[0]}
              y1={scaledHit[1] + 8}
              x2={scaledHit[0]}
              y2={scaledHit[1] + 15}
              stroke='#ffaa00'
              strokeWidth={2}
              opacity={0.8}
            />
          </motion.g>

          {/* 중앙 타겟 링 */}
          <motion.circle
            cx={scaledHit[0]}
            cy={scaledHit[1]}
            r={12}
            fill='none'
            stroke='#ffaa00'
            strokeWidth={2}
            filter='url(#strongGlow)'
            animate={{
              r: [10, 13, 10],
              opacity: [0.8, 1, 0.8],
            }}
            transition={{ duration: 1, repeat: Infinity }}
          />

          {/* 중앙 포인트 */}
          <motion.circle
            cx={scaledHit[0]}
            cy={scaledHit[1]}
            r={5}
            fill='#ffd700'
            filter='url(#strongGlow)'
            initial={{ scale: 0 }}
            animate={{
              scale: 1,
            }}
            transition={{
              type: 'spring',
              stiffness: 400,
              damping: 10,
            }}
          />

          {/* 중앙 하이라이트 */}
          <motion.circle
            cx={scaledHit[0]}
            cy={scaledHit[1]}
            r={2.5}
            fill='#ffffcc'
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{
              type: 'spring',
              stiffness: 500,
              damping: 15,
              delay: 0.05,
            }}
          />
        </g>
      )}
    </svg>
  );
}
