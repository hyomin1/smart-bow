import { useLayoutEffect, useState } from 'react';

export function useVideoSize(ref: React.RefObject<HTMLVideoElement | null>) {
  const [rect, setRect] = useState<{ w: number; h: number } | null>(null);

  useLayoutEffect(() => {
    if (!ref.current) return;

    const update = () => {
      const r = ref.current!.getBoundingClientRect();
      setRect({ w: r.width, h: r.height });
    };
    update();
    window.addEventListener('resize', update);
    return () => window.removeEventListener('resize', update);
  }, [ref]);
  return rect;
}
