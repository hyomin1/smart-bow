import { useEffect, useRef } from 'react';
import Hls from 'hls.js';

export default function CamHlsPlayer() {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (!(videoRef.current && Hls.isSupported())) {
      return;
    }
    const hls = new Hls({
      maxBufferLength: 5,
      liveSyncDuration: 1,
    });
    hls.loadSource('http://localhost:8000/hls/index.m3u8');
    hls.attachMedia(videoRef.current);
  }, []);

  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted
      controls
      className='h-full w-full object-contain'
    />
  );
}
