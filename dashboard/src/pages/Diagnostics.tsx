import React from "react";
import { useOutletContext } from "react-router-dom";
import { Server, CheckCircle2, XCircle, Clock, Building2, Activity } from "lucide-react";
import { STATE, ACCENT } from "../types";
import Glass from "../components/Glass";
import StatePill from "../components/StatePill";

export interface DiagnosticsPageProps {
  connected?: boolean;
  onToggleConnection?: () => void;
  secondsSinceSync?: number;
}

/**
 * Diagnostics page component displaying API service connectivity logs, port map diagnostics,
 * and current session synchronization states.
 */
export default function Diagnostics({ connected, onToggleConnection, secondsSinceSync }: DiagnosticsPageProps) {
  const context = useOutletContext<{ connected: boolean; onToggleConnection: () => void; secondsSinceSync: number }>();
  
  const activeConnected = connected !== undefined ? connected : context?.connected;
  const activeOnToggleConnection = onToggleConnection || context?.onToggleConnection;
  const activeSecondsSinceSync = secondsSinceSync !== undefined ? secondsSinceSync : context?.secondsSinceSync;

  const rows = [
    { label: "REST API — Inventory (Mithun, :8002)", value: "GET /api/v1/inventory/{hospital_id}", ok: activeConnected },
    { label: "REST API — Inventory Update (:8002)", value: "POST /api/v1/inventory/update", ok: activeConnected },
    { label: "WebSocket — Live Feed (:8002)", value: "ws://127.0.0.1:8002/ws/live", ok: activeConnected },
    { label: "Donor Verify Proxy (Vignesh, :8000)", value: "POST /api/v1/donor/verify", ok: activeConnected },
    { label: "Demand Prediction Proxy (Tejas, :8001)", value: "POST /api/v1/predict/demand", ok: activeConnected },
    { label: "Dashboard Port (me)", value: "localhost:3000", ok: true },
  ];

  return (
    <div className="space-y-6 p-6 animate-none">
      <Glass className="p-5 animate-none">
        <div className="mb-4 flex items-center justify-between animate-none">
          <h2 className="flex items-center gap-2 text-sm font-semibold text-white"><Server size={15} style={{ color: ACCENT }} /> Connection Diagnostics</h2>
          <button
            onClick={activeOnToggleConnection}
            className="rounded-lg border px-3 py-1.5 text-xs font-medium cursor-pointer border-solid"
            style={{ borderColor: "rgba(255,255,255,0.1)", color: "#8A97A6" }}
          >
            {activeConnected ? "Simulate disconnect" : "Simulate reconnect"}
          </button>
        </div>
        <div className="space-y-2 animate-none">
          {rows.map((r) => (
            <div key={r.label} className="flex items-center justify-between rounded-lg border p-3 text-xs border-solid" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
              <div>
                <p className="text-white">{r.label}</p>
                <p className="font-mono text-[11px]" style={{ color: "#5B6572" }}>{r.value}</p>
              </div>
              {r.ok ? <CheckCircle2 size={16} style={{ color: STATE.safe.dot }} /> : <XCircle size={16} style={{ color: STATE.breach.dot }} />}
            </div>
          ))}
        </div>
      </Glass>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 animate-none">
        <Glass className="p-4 animate-none">
          <div className="flex items-center gap-1.5 animate-none"><Clock size={12} style={{ color: "#8A97A6" }} /><span className="text-xs" style={{ color: "#8A97A6" }}>Last Heartbeat</span></div>
          <div className="mt-1 text-lg font-semibold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>{activeSecondsSinceSync}s ago</div>
        </Glass>
        <Glass className="p-4 animate-none">
          <div className="flex items-center gap-1.5 animate-none"><Building2 size={12} style={{ color: "#8A97A6" }} /><span className="text-xs" style={{ color: "#8A97A6" }}>Hospital ID</span></div>
          <div className="mt-1 text-lg font-semibold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>HSP-0417</div>
        </Glass>
        <Glass className="p-4 animate-none">
          <div className="flex items-center gap-1.5 animate-none"><Activity size={12} style={{ color: "#8A97A6" }} /><span className="text-xs" style={{ color: "#8A97A6" }}>Session State</span></div>
          <div className="mt-1"><StatePill state={activeConnected ? "safe" : "breach"} /></div>
        </Glass>
      </div>
    </div>
  );
}
