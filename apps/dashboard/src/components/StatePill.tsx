import { type StateKey, STATE } from "../types";

export interface StatePillProps {
  state: StateKey;
}

/**
 * Status indicator pill displaying the current system/metric state (safe, warning, breach).
 */
export default function StatePill({ state }: StatePillProps) {
  const s = STATE[state];
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium tracking-wide"
      style={{ color: s.text, background: s.bg, borderColor: s.border }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ background: s.dot, boxShadow: `0 0 8px ${s.dot}` }} />
      {s.label}
    </span>
  );
}
