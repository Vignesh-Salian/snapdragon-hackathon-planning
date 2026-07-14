import { Droplet, Building2, Fingerprint, LogIn } from "lucide-react";
import { ACCENT } from "../types";
import Glass from "../components/Glass";

export interface LoginPageProps {
  onEnter: () => void;
}

/**
 * Login / Hospital Select page component.
 */
export default function Login({ onEnter }: LoginPageProps) {
  return (
    <div className="flex min-h-[560px] items-center justify-center p-6">
      <Glass className="w-full max-w-sm p-8">
        <div className="mb-6 flex flex-col items-center text-center">
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl" style={{ background: "rgba(47,217,196,0.15)" }}>
            <Droplet size={22} style={{ color: ACCENT }} />
          </div>
          <h1 className="text-lg font-semibold text-white" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>HemaGrid AI</h1>
          <p className="mt-1 text-xs" style={{ color: "#8A97A6" }}>Connected cold chain & donor verification</p>
        </div>

        <label className="mb-1.5 block text-xs font-medium" style={{ color: "#8A97A6" }}>Hospital ID</label>
        <div className="mb-4 flex items-center gap-2 rounded-lg border px-3 py-2.5" style={{ borderColor: "rgba(255,255,255,0.1)", background: "rgba(255,255,255,0.03)" }}>
          <Building2 size={15} style={{ color: "#8A97A6" }} />
          <input defaultValue="HSP-0417 — St. Alphonsa Medical Center" className="w-full bg-transparent text-sm text-white outline-none border-none" readOnly />
        </div>

        <label className="mb-1.5 block text-xs font-medium" style={{ color: "#8A97A6" }}>Operator PIN</label>
        <div className="mb-6 flex items-center gap-2 rounded-lg border px-3 py-2.5" style={{ borderColor: "rgba(255,255,255,0.1)", background: "rgba(255,255,255,0.03)" }}>
          <Fingerprint size={15} style={{ color: "#8A97A6" }} />
          <input defaultValue="••••••" className="w-full bg-transparent text-sm text-white outline-none border-none" readOnly />
        </div>

        <button
          onClick={onEnter}
          className="flex w-full items-center justify-center gap-2 rounded-lg py-2.5 text-sm font-semibold text-black transition-opacity hover:opacity-90 cursor-pointer"
          style={{ background: ACCENT }}
        >
          <LogIn size={15} /> Enter dashboard
        </button>
        <p className="mt-4 text-center text-[11px]" style={{ color: "#5B6572" }}>Session syncs to ws://127.0.0.1:8002/ws/live</p>
      </Glass>
    </div>
  );
}
