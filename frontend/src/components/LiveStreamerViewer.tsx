import { useEffect, useRef } from 'react';
import JSMpeg from '@cycjimmy/jsmpeg-player';

export default function StreamCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (canvasRef.current) {
      new JSMpeg.Player('ws://localhost:9999', {
        canvas: canvasRef.current,
        autoplay: true,
        audio: false, // 오디오 안 쓸 거면 false
      });
    }
  }, []);

  return (
    // <canvas
    //   ref={canvasRef}
    //   className='h-full w-full'
    //   style={{ border: '1px solid black' }}
    // />

    <img
      src='http://localhost:8001/monitor'
      alt='Arrow Monitor'
      className='h-screen'
    />
  );
}
