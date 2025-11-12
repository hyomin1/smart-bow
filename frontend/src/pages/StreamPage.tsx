import CamWebRTC from '../components/CamWebRTC';
import { useParams } from 'react-router-dom';
import TargetOverlayView from '../components/TargetOverlayView';
import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';

type Hit = { x: number; y: number; inside: boolean };
type Size = { width: number; height: number };
export default function StreamPage() {
  const [hit, setHit] = useState<Hit | null>(null);
  const targetContainerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState<Size>();
  const { camId } = useParams();
  const [polygon, setPolygon] = useState<number[][] | null>(null);
  const [frameSize, setFrameSize] = useState<{ w: number; h: number } | null>(
    null
  );

  useLayoutEffect(() => {
    const updateSize = () => {
      if (targetContainerRef.current) {
        const { width, height } =
          targetContainerRef.current.getBoundingClientRect();
        if (size?.width !== width || size?.height !== height) {
          setSize({ width, height });
        }
      }
    };
    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, [size]);

  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (!size) return;
    const ws = new WebSocket(
      `${import.meta.env.VITE_WEBSOCKET_URL}hit/${camId}`
    );
    ws.onopen = () => console.log('WebSocket opened');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('data', data);
      if (data.type === 'polygon') {
        const [w, h] = data.frame_size;
        setFrameSize({ w, h });
        setPolygon(data.points);
      }
      if (data.type === 'hit' && data.tip) {
        const [x, y] = data.tip;
        const inside = data.inside;

        setHit({ x, y, inside });
      }
    };

    ws.onclose = () => console.warn('WebSocket closed');
    ws.onerror = (err) => console.error('WebSocket error', err);

    return () => ws.close();
  }, [camId, size]);

  useEffect(() => {
    if (hit) {
      const timer = setTimeout(() => setHit(null), 10_000);
      return () => clearTimeout(timer);
    }
  }, [hit]);

  if (!camId) {
    return <span>잘못된 카메라 경로입니다</span>;
  }
  console.log('frame', frameSize);
  return (
    <div>
      <div className='flex h-screen'>
        <div
          ref={targetContainerRef}
          className='w-1/2 h-full relative bg-black'
        >
          <CamWebRTC camId={camId} ref={videoRef} />

          <AnimatePresence>
            {hit && frameSize && (
              <>
                <motion.div
                  key='overlay-bg'
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1.0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className='absolute inset-0 bg-black'
                />

                <motion.div
                  key={`overlay-${hit.x}-${hit.y}`}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 1.05 }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                  className='absolute inset-0 flex items-center justify-center'
                >
                  <TargetOverlayView
                    hit={hit}
                    frameSize={frameSize}
                    polygon={polygon}
                  />
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>

        <div className='w-1/2 h-full'>
          <CamWebRTC camId='shooter1' />
        </div>
      </div>
    </div>
  );
}
