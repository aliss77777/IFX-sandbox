import React from 'react';

export function Label({ children, className }: { children?: React.ReactNode; className?: string }) {
  return <label className={className}>{children}</label>;
}