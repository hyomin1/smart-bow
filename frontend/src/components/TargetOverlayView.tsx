import { useEffect, useRef, useState, useLayoutEffect, useMemo } from 'react';
import { api } from '../api/axios';
import { motion } from 'framer-motion';

type Corner = [number, number];
type Size = { width: number; height: number };
type Hit = { x: number; y: number };

export default function TargetOverlayView({ camId }: { camId: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState<Size>();
  const [corners, setCorners] = useState<Corner[] | null>(null);
  const [hit, setHit] = useState<Hit | null>(null);

  useLayoutEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        if (size?.width !== width || size?.height !== height) {
          setSize({ width, height });
        }
      }
    };
    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, [size]);

  const { targetW, targetH } = useMemo(() => {
    if (!size) return { targetW: 400, targetH: 400 };
    return {
      targetW: Math.round(size.width * 0.35), // 전체화면에선 0.4
      targetH: Math.round(size.height * 0.5),
    };
  }, [size]);

  useEffect(() => {
    if (!size) return;
    const fetchCorners = async () => {
      try {
        const { data } = await api.get(
          `target/corners/${camId}?tw=${targetW}&th=${targetH}`
        );
        setCorners(data.corners);
      } catch (err) {
        console.error('좌표 가져오기 실패', err);
      }
    };
    const handler = setTimeout(fetchCorners, 1000);
    return () => clearTimeout(handler);
  }, [size, targetW, targetH, camId]);

  useEffect(() => {
    if (!corners) return;

    const ws = new WebSocket(
      `${
        import.meta.env.VITE_WEBSOCKET_URL
      }hit/${camId}?tw=${targetW}&th=${targetH}`
    );
    ws.onopen = () => console.log('ws open');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('수신 데이터:', data);
      if (data.type === 'hit' && data.corrected_hit) {
        const [x, y] = data.corrected_hit;
        setHit({ x, y });

        setTimeout(() => setHit(null), 10_000);
      }
    };
    ws.onclose = (event) => {
      console.warn(
        `WebSocket 닫힘 (code=${event.code}, reason=${event.reason})`
      );
      // 여기서 재연결
    };

    ws.onerror = (err) => {
      console.error('WebSocket 에러', err);
    };
    return () => ws.close();
  }, [corners, targetW, targetH, camId]);

  return (
    <div
      ref={containerRef}
      className='flex items-center justify-center w-full h-full bg-gradient-to-b from-black to-gray-900'
    >
      {corners ? (
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

          {/* 화살 적중 지점 */}
          {hit && (
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
      ) : (
        <span className='text-white'>스트림 중단</span>
      )}
    </div>
  );
}
