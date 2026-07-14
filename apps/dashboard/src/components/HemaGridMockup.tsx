import { useState, useEffect } from "react";
import { useLocation, useNavigate, Outlet } from "react-router-dom";
import { Droplet, LayoutDashboard, Radio, Fingerprint, Settings } from "lucide-react";
import { STATE, ACCENT, type DonorVerifyResponse } from "../types";
import { verificationQueue } from "../mocks/data";
import TopBar from "./TopBar";
import NavItem from "./NavItem";
import FraudAlertModal from "./FraudAlertModal";
import AdjustModal from "./AdjustModal";

/**
 * HemaGridMockup layout shell acting as the page sidebar and topbar layout.
 */
export default function HemaGridMockup() {
  const location = useLocation();
  const navigate = useNavigate();
  const [showAlert, setShowAlert] = useState(false);
  const [showAdjust, setShowAdjust] = useState(false);
  const [connected, setConnected] = useState(true);
  const [secondsSinceSync, setSecondsSinceSync] = useState(0);

  // The fraud alert currently being reviewed — matches the real DonorVerifyResponse
  // schema so the modal never has to guess at field names.
  const activeFraudCase: DonorVerifyResponse = verificationQueue.find((v) => v.state === "breach")!.response;

  // Ticking "last sync" clock — purely frontend, drives the stale-data banner.
  useEffect(() => {
    const interval = setInterval(() => {
      setSecondsSinceSync((s) => (connected ? 0 : s + 1));
    }, 1000);
    return () => clearInterval(interval);
  }, [connected]);

  return (
    <>
      <style>{`
        @keyframes pulse-run { from { stroke-dashoffset: 620; } to { stroke-dashoffset: 0; } }
        .animate-pulse { animation: sk-pulse 1.4s ease-in-out infinite; }
        @keyframes sk-pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 0.25; } }
      `}</style>

      <div className="flex min-h-screen animate-none">
        {/* Sidebar */}
        <div className="hidden w-56 shrink-0 flex-col border-r p-4 md:flex animate-none" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
          <div className="mb-6 flex items-center gap-2 px-1 animate-none">
            <Droplet size={16} style={{ color: ACCENT }} />
            <span className="text-sm font-semibold text-white">HemaGrid AI</span>
          </div>
          <div className="space-y-1 animate-none">
            <NavItem icon={LayoutDashboard} label="Dashboard" active={location.pathname === "/dashboard"} onClick={() => navigate("/dashboard")} />
            <NavItem icon={Radio} label="Cold Box Telemetry" active={location.pathname === "/telemetry"} onClick={() => navigate("/telemetry")} />
            <NavItem icon={Fingerprint} label="Donor Verification" active={location.pathname === "/verify"} onClick={() => navigate("/verify")} />
            <NavItem icon={Settings} label="Diagnostics" active={location.pathname === "/diagnostics"} onClick={() => navigate("/diagnostics")} />
          </div>
          <div className="mt-auto space-y-2 rounded-xl border p-3 text-[11px] animate-none" style={{ borderColor: "rgba(255,255,255,0.08)", color: "#5B6572" }}>
            <p className="font-medium" style={{ color: "#8A97A6" }}>State legend</p>
            <div className="flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full" style={{ background: STATE.safe.dot }} /> Safe</div>
            <div className="flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full" style={{ background: STATE.warning.dot }} /> Warning</div>
            <div className="flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full" style={{ background: STATE.breach.dot }} /> Breach</div>
          </div>
        </div>

        {/* Main */}
        <div className="flex-1 animate-none">
          <TopBar hospital="HSP-0417 — St. Alphonsa" connected={connected} secondsSinceSync={secondsSinceSync} />

          <Outlet context={{
            openAlert: () => setShowAlert(true),
            openAdjust: () => setShowAdjust(true),
            connected,
            onToggleConnection: () => { setConnected((c) => !c); setSecondsSinceSync(0); },
            secondsSinceSync
          }} />
        </div>
      </div>

      {showAlert && <FraudAlertModal onClose={() => setShowAlert(false)} data={activeFraudCase} />}
      {showAdjust && <AdjustModal onClose={() => setShowAdjust(false)} />}
    </>
  );
}