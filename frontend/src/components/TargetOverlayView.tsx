import axios from 'axios';
import { useEffect, useRef, useState } from 'react';

export default function TargetOverlayCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [corners, setCorners] = useState<number[][]>([]);
  const [hits, setHits] = useState<number[][]>([]); // ✅ 누적 히트 저장
  console.log('hit', hits.length);
  // 코너 fetch
  useEffect(() => {
    const fetchCorners = async () => {
      try {
        const { data } = await axios.get(
          'http://localhost:8001/target/target-corners'
        );
        setCorners(data.corners);
      } catch (error) {
        console.error('코너 검출 실패', error);
      }
    };
    fetchCorners();
    const interval = setInterval(fetchCorners, 1000 * 60 * 60);
    return () => clearInterval(interval);
  }, []);

  // WebSocket 이벤트 처리
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8001/ws/arrow-events');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'hit' && data.corrected_tip) {
        setHits((prev) => [...prev, data.corrected_tip]); // ✅ 누적 저장
      }
    };
    return () => ws.close();
  }, []);

  // 캔버스 그리기 (코너 + 히트들 전부)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 캔버스 전체 클리어
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 🎯 과녁 그리기
    if (corners.length === 4) {
      ctx.beginPath();
      ctx.moveTo(corners[0][0], corners[0][1]);
      ctx.lineTo(corners[1][0], corners[1][1]);
      ctx.lineTo(corners[2][0], corners[2][1]);
      ctx.lineTo(corners[3][0], corners[3][1]);
      ctx.closePath();

      ctx.strokeStyle = 'red';
      ctx.lineWidth = 3;
      ctx.stroke();
    }

    // 🏹 맞은 지점들 누적해서 다 그림
    hits.forEach(([x, y]) => {
      // 바깥쪽 투명한 원
      ctx.beginPath();
      ctx.arc(x, y, 20, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(0, 255, 0, 0.2)';
      ctx.fill();

      // 중심 진한 원
      ctx.beginPath();
      ctx.arc(x, y, 6, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(0, 128, 0, 0.9)';
      ctx.fill();
    });
  }, [corners, hits]); // ✅ 상태가 바뀔 때마다 다시 그림

  return (
    <canvas
      ref={canvasRef}
      width={1280}
      height={720}
      className='max-w-full max-h-full object-contain'
    />
  );
}
