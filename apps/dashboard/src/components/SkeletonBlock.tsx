import React from "react";

export interface SkeletonBlockProps {
  className?: string;
  style?: React.CSSProperties;
}

/**
 * Basic block skeleton for loading state placeholders.
 */
export default function SkeletonBlock({ className = "", style = {} }: SkeletonBlockProps) {
  return (
    <div
      className={`animate-pulse rounded-xl ${className}`}
      style={{ background: "rgba(255,255,255,0.05)", ...style }}
    />
  );
}
