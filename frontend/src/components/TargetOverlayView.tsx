import { useEffect, useRef, useState, useLayoutEffect, useMemo } from 'react';
import axios from 'axios';

type Corner = [number, number];
type Size = { width: number; height: number };

export default function TargetOverlayView() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState<Size>();
  const [corners, setCorners] = useState<Corner[] | null>(null);

  // 컨테이너 크기 측정
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

  // 📌 targetW / targetH 계산 (size 변할 때만 갱신)
  const { targetW, targetH } = useMemo(() => {
    if (!size) return { targetW: 400, targetH: 400 };
    return {
      targetW: Math.round(size.width * 0.5), // 반올림
      targetH: Math.round(size.height * 0.7), // 반올림
    };
  }, [size]);

  // 서버에서 보정된 코너 좌표 가져오기 (size 변할 때만 호출됨)
  useEffect(() => {
    if (!size) return;
    const fetchCorners = async () => {
      try {
        const { data } = await axios.get(
          `http://localhost:8000/target/target-corners?tw=${targetW}&th=${targetH}`
        );
        setCorners(data.corners);
      } catch (err) {
        console.error('좌표 가져오기 실패', err);
      }
    };
    fetchCorners();
  }, [size, targetW, targetH]);

  console.log('corners', corners);

  return (
    <div
      ref={containerRef}
      className='flex items-center justify-center w-full h-full bg-black'
    >
      {corners ? (
        <svg
          width={targetW}
          height={targetH}
          viewBox={`0 0 ${targetW} ${targetH}`}
          className='border-2 border-red-600'
        />
      ) : (
        <span className='text-white'>스트림 중단</span>
      )}
    </div>
  );
}
