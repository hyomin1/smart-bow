import { useEffect, useRef } from 'react';
import Hls from 'hls.js';
const CAM = 'cam2';
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
    hls.loadSource(`http://localhost:8888/${CAM}/index.m3u8`);
    hls.attachMedia(videoRef.current);
  }, []);

  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted
      controls={false}
      className='h-full w-full object-cover'
    />
  );
}
