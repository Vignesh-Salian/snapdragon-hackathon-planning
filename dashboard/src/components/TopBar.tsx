import { Droplet, Building2, ChevronDown, Wifi, WifiOff, Bell, AlertTriangle } from "lucide-react";
import { ACCENT } from "../types";
import PulseTrace from "./PulseTrace";

export interface TopBarProps {
  hospital: string;
  connected: boolean;
  secondsSinceSync: number;
}

/**
 * TopBar component containing sync indicator, connection state, brand layout and notification bell.
 */
export default function TopBar({ hospital, connected, secondsSinceSync }: TopBarProps) {
  const syncLabel = secondsSinceSync < 60 ? `${secondsSinceSync}s ago` : `${Math.floor(secondsSinceSync / 60)}m ago`;
  const stale = secondsSinceSync > 15;
  return (
    <div className="border-b animate-none" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg" style={{ background: "rgba(47,217,196,0.15)" }}>
              <Droplet size={16} style={{ color: ACCENT }} />
            </div>
            <span className="text-sm font-semibold tracking-wide text-white" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
              HemaGrid <span style={{ color: ACCENT }}>AI</span>
            </span>
          </div>
          <PulseTrace connected={connected} />
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden items-center gap-2 rounded-lg border px-3 py-1.5 text-xs md:flex" style={{ borderColor: "rgba(255,255,255,0.08)", color: "#8A97A6" }}>
            <Building2 size={13} />
            {hospital}
            <ChevronDown size={13} />
          </div>
          <div
            className="flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs"
            style={{
              borderColor: connected ? "rgba(74,222,128,0.3)" : "rgba(248,113,113,0.4)",
              color: connected ? "#4ADE80" : "#F87171",
            }}
            title={`Last sync ${syncLabel}`}
          >
            {connected ? <Wifi size={13} /> : <WifiOff size={13} />}
            {connected ? "Live" : "Offline"}
            <span className="hidden font-mono text-[10px] opacity-70 sm:inline">· {syncLabel}</span>
          </div>
          <div className="relative">
            <Bell size={17} style={{ color: "#8A97A6" }} />
            <span className="absolute -right-1 -top-1 h-2 w-2 rounded-full" style={{ background: "#EF4444" }} />
          </div>
          <div className="h-8 w-8 rounded-full" style={{ background: "linear-gradient(135deg,#2FD9C4,#1F8F82)" }} />
        </div>
      </div>

      {/* Stale-data banner — appears when sync gets old or socket drops */}
      {(!connected || stale) && (
        <div
          className="flex items-center gap-2 px-6 py-2 text-xs"
          style={{ background: "rgba(245,165,36,0.1)", color: "#FBBF24", borderTop: "1px solid rgba(251,191,36,0.25)" }}
        >
          <AlertTriangle size={13} />
          {connected ? `Data may be stale — last update ${syncLabel}` : "Connection lost — attempting to reconnect… showing last known data"}
        </div>
      )}
    </div>
  );
}
