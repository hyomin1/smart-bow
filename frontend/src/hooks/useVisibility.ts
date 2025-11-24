import { useEffect, useState } from 'react';

export default function useVisibility() {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const handleChange = () => {
      setIsVisible(document.visibilityState === 'visible');
    };
    document.addEventListener('visibilitychange', handleChange);
    return () => {
      document.removeEventListener('visibilitychange', handleChange);
    };
  }, []);

  return isVisible;
}
