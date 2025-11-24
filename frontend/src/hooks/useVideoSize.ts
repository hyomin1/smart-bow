import { useLayoutEffect, useState, useRef } from 'react';

export function useVideoSize(ref: React.RefObject<HTMLVideoElement | null>) {
  const [rect, setRect] = useState<{ w: number; h: number } | null>(null);
  const timeoutRef = useRef<number | null>(null);

  useLayoutEffect(() => {
    if (!ref.current) return;

    const update = () => {
      if (!ref.current) return;
      const r = ref.current.getBoundingClientRect();

      setRect((prev) => {
        if (prev && prev.w === r.width && prev.h === r.height) {
          return prev;
        }
        return { w: r.width, h: r.height };
      });
    };

    const debouncedUpdate = () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = window.setTimeout(update, 100);
    };

    update();
    window.addEventListener('resize', debouncedUpdate);

    return () => {
      window.removeEventListener('resize', debouncedUpdate);
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [ref]);

  return rect;
}
