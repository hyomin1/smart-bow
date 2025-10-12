import { useEffect, useRef } from 'react';
import mpegts from 'mpegts.js';

export default function CamMpeg() {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current && mpegts.getFeatureList().mseLivePlayback) {
      const player = mpegts.createPlayer({
        type: 'mpegts',
        isLive: true,
        url: 'http://localhost:8000/stream.ts',
      });

      player.attachMediaElement(videoRef.current);
      player.load();

      const videoEl = videoRef.current;
      const handleCanPlay = () => {
        videoEl.play().catch((err) => console.warn('자동재생 실패:', err));
      };
      videoEl.addEventListener('canplay', handleCanPlay);

      return () => {
        videoEl.removeEventListener('canplay', handleCanPlay);
        player.unload();
        player.detachMediaElement();
        player.destroy();
      };
    }
  }, []);

  return (
    <video
      ref={videoRef}
      controls
      muted
      autoPlay
      playsInline
      className='object-contain w-full h-full'
    />
  );
}
