import { ShieldAlert, X } from "lucide-react";
import { type DonorVerifyResponse, STATE, CONFIDENCE_THRESHOLD } from "../types";
import Glass from "./Glass";

export interface FraudAlertModalProps {
  onClose: () => void;
  data: DonorVerifyResponse;
}

/**
 * Biometric Lockout emergency modal popup shown when duplicate donor profile alerts are received.
 */
export default function FraudAlertModal({ onClose, data }: FraudAlertModalProps) {
  const s = STATE.breach;
  const { confidence, matched_donor, message } = data;
  const enrolledDate = matched_donor.enrolled_at
    ? new Date(matched_donor.enrolled_at).toLocaleString("en-IN", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })
    : "—";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(5,4,6,0.7)", backdropFilter: "blur(4px)" }}>
      <Glass className="w-full max-w-md p-6" style={{ borderColor: s.border, boxShadow: `0 0 60px rgba(239,68,68,0.25)` }}>
        <div className="mb-4 flex items-start justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-full" style={{ background: s.bg }}>
              <ShieldAlert size={18} style={{ color: s.text }} />
            </div>
            <div>
              <h3 className="text-sm font-semibold" style={{ color: s.text }}>Duplicate Donor Detected</h3>
              <p className="text-[11px]" style={{ color: "#8A97A6" }}>FRAUD_ALERT · biometric lockout engaged</p>
            </div>
          </div>
          <button className="cursor-pointer" onClick={onClose}><X size={16} style={{ color: "#8A97A6" }} /></button>
        </div>

        <div className="mb-4 space-y-2 rounded-lg border p-3 text-xs" style={{ borderColor: s.border, background: s.bg }}>
          <div className="flex justify-between"><span style={{ color: "#8A97A6" }}>Matched name</span><span className="text-white">{matched_donor.name}</span></div>
          <div className="flex justify-between"><span style={{ color: "#8A97A6" }}>Confidence</span><span style={{ color: s.text }}>{confidence}% (threshold {CONFIDENCE_THRESHOLD}%)</span></div>
          <div className="flex justify-between"><span style={{ color: "#8A97A6" }}>Prior registration</span><span className="text-white font-mono">{enrolledDate}</span></div>
          <div className="flex justify-between"><span style={{ color: "#8A97A6" }}>Donor ID</span><span className="text-white font-mono">#{matched_donor.id}</span></div>
        </div>

        <p className="mb-4 text-[11px] italic" style={{ color: "#8A97A6" }}>"{message}"</p>

        <div className="flex gap-2">
          <button onClick={onClose} className="flex-1 rounded-lg border py-2 text-xs font-medium cursor-pointer" style={{ borderColor: "rgba(255,255,255,0.1)", color: "#8A97A6" }}>Dismiss</button>
          <button onClick={onClose} className="flex-1 rounded-lg py-2 text-xs font-semibold text-black cursor-pointer" style={{ background: s.dot }}>Confirm lockout</button>
        </div>
      </Glass>
    </div>
  );
}
