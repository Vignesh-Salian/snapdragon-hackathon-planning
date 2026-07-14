import { ACCENT } from "../types";

export interface PulseTraceProps {
  connected: boolean;
}

/**
 * Signature element: a live ECG / pulse trace across the top bar.
 * Literal "blood" motif + functional live-connection indicator.
 */
export default function PulseTrace({ connected }: PulseTraceProps) {
  return (
    <svg viewBox="0 0 400 40" className="h-8 w-40 md:w-56" preserveAspectRatio="none">
      <polyline
        points="0,20 40,20 55,20 65,5 75,35 85,20 100,20 140,20 155,20 165,5 175,35 185,20 200,20 240,20 255,20 265,5 275,35 285,20 300,20 340,20 355,20 365,5 375,35 385,20 400,20"
        fill="none"
        stroke={connected ? ACCENT : "#EF4444"}
        strokeWidth="2"
        strokeLinejoin="round"
        strokeLinecap="round"
        style={{
          filter: `drop-shadow(0 0 4px ${connected ? ACCENT : "#EF4444"})`,
          strokeDasharray: 620,
          animation: connected ? "pulse-run 2.6s linear infinite" : "none",
          opacity: connected ? 1 : 0.5,
        }}
      />
    </svg>
  );
}
