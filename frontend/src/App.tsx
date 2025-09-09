import { useEffect, useRef } from 'react';
import mpegts from 'mpegts.js';

export default function Player() {
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
      player.play();
      return () => player.destroy();
    }
  }, []);

  return (
    <video ref={videoRef} width={640} height={360} controls muted autoPlay />
  );
}
