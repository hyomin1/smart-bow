import { useEffect, useRef } from 'react';

interface Props {
  bbox: [number, number, number, number] | null;
  width: number;
  height: number;
}

export default function BBoxOverlay({ bbox, width, height }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = width;
    canvas.height = height;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (bbox) {
      const [x1, y1, x2, y2] = bbox;

      // bbox 그리기
      ctx.strokeStyle = '#00FF00';
      ctx.lineWidth = 3;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

      // 라벨
      ctx.fillStyle = '#00FF00';
      ctx.font = 'bold 16px Arial';
      ctx.fillText('Arrow', x1, y1 - 8);
    }
  }, [bbox, width, height]);

  return (
    <canvas
      ref={canvasRef}
      className='absolute inset-0 pointer-events-none'
      style={{ zIndex: 10 }}
    />
  );
}
