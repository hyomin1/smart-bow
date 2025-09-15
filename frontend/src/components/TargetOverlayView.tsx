import { useEffect, useRef, useState, useLayoutEffect, useMemo } from 'react';
import { api } from '../api/axios';

type Corner = [number, number];
type Size = { width: number; height: number };
type Hit = { x: number; y: number };

export default function TargetOverlayView() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState<Size>();
  const [corners, setCorners] = useState<Corner[] | null>(null);
  const [hits, setHits] = useState<Hit[]>([]);

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
      targetW: Math.round(size.width * 0.35),
      targetH: Math.round(size.height * 0.5),
    };
  }, [size]);

  useEffect(() => {
    if (!size) return;
    const fetchCorners = async () => {
      try {
        const { data } = await api.get(
          `target/target-corners?tw=${targetW}&th=${targetH}`
        );
        setCorners(data.corners);
      } catch (err) {
        console.error('좌표 가져오기 실패', err);
      }
    };
    const handler = setTimeout(fetchCorners, 1000);
    return () => clearTimeout(handler);
  }, [size, targetW, targetH]);

  useEffect(() => {
    if (!corners) return;

    const ws = new WebSocket(
      `ws://localhost:8000/ws/arrow?tw=${targetW}&th=${targetH}`
    );

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'hit' && data.corrected_hit) {
        const [x, y] = data.corrected_hit;
        setHits((prev) => [...prev, { x, y }]);
      }
    };
    return () => ws.close();
  }, [corners, targetW, targetH]);

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
          {hits.map((hit, idx) => (
            <circle
              key={idx}
              cx={hit.x}
              cy={hit.y}
              r={6}
              fill='red'
              stroke='white'
              strokeWidth={2}
            />
          ))}
        </svg>
      ) : (
        <span className='text-white'>스트림 중단</span>
      )}
    </div>
  );
}
