import React from "react";

export interface GlassProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

/**
 * Glassmorphic container panel.
 */
export default function Glass({ children, className = "", style = {} }: GlassProps) {
  return (
    <div
      className={`rounded-2xl border backdrop-blur-xl ${className}`}
      style={{
        background: "rgba(255,255,255,0.035)",
        borderColor: "rgba(255,255,255,0.08)",
        boxShadow: "0 8px 30px rgba(0,0,0,0.35)",
        ...style,
      }}
    >
      {children}
    </div>
  );
}
