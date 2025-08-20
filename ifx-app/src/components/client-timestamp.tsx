'use client';

import { useEffect, useState } from 'react';

export default function ClientTimestamp({ timestamp }: { timestamp: Date }) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return null;
  }

  return (
    <>
      {timestamp.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
      })}
    </>
  );
}
