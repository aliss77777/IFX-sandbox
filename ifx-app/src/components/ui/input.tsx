import React from 'react';

export function Input({ className, ...props }: { className?: string; [key: string]: any }) {
  return <input className={className} {...props} />;
}