import { useState, useEffect, useMemo } from "react";
import { useOutletContext } from "react-router-dom";
import { Droplet, Thermometer, Fingerprint, HeartPulse, Plus, Battery } from "lucide-react";
import { STATE, ACCENT } from "../types";
import { bloodInventory as mockBloodInventory, coldBoxes, alertFeed, mockPrediction as mockPred } from "../mocks/data";
import { getInventory, predictDemand } from "../services/api";
import Glass from "../components/Glass";
import StatePill from "../components/StatePill";
import PredictionPanel from "../components/PredictionPanel";
import DashboardSkeleton from "../components/DashboardSkeleton";

export interface HomeProps {
  openAlert?: () => void;
  openAdjust?: () => void;
}

/**
 * Main dashboard overview page showing inventory status, recent alerts, demand predictions,
 * and cold boxes status.
 */
export default function Home({ openAlert, openAdjust }: HomeProps) {
  const context = useOutletContext<{ openAlert: () => void; openAdjust: () => void }>();
  const activeOpenAlert = openAlert || context?.openAlert;
  const activeOpenAdjust = openAdjust || context?.openAdjust;

  const [loading, setLoading] = useState(true);
  const [inventory, setInventory] = useState(mockBloodInventory);
  const [prediction, setPrediction] = useState(mockPred);

  useEffect(() => {
    // Fetch live inventory from gateway database
    getInventory("KMC-MANIPAL")
      .then((data) => {
        if (data && data.length > 0) {
          setInventory(data);
        }
      })
      .catch((err) => {
        console.error("Failed to load live inventory, falling back to mock:", err);
      });

    // Execute live prediction call through gateway delegate proxy to SFace/MLP on NPU
    const dummyFeatures = {
      hospital_id: 1,
      hospital_type: "Trauma",
      city_region: "Urban",
      blood_type: "O+",
      season: "Monsoon",
      temperature_c: 31.4,
      rainfall_mm: 112.0,
      dengue_cases_weekly: 52.0,
      road_accidents: 21.0,
      emergency_cases: 13.0,
      scheduled_surgeries: 9.0,
      holiday: 0,
      blood_donation_camp: 1,
      current_inventory: 80.0,
      day_of_week: 2,
      month: 7
    };

    predictDemand(dummyFeatures)
      .then((data) => {
        setPrediction(data);
      })
      .catch((err) => {
        console.error("Failed to fetch live prediction, falling back to mock:", err);
      });

    const t = setTimeout(() => setLoading(false), 700);
    return () => clearTimeout(t);
  }, []);

  // Fleet health — derived purely from existing coldBoxes / alertFeed mock arrays.
  const fleetStats = useMemo(() => {
    const breachToday = alertFeed.filter((a) => a.state === "breach").length;
    const healthyBoxes = coldBoxes.filter((c) => c.state !== "breach").length;
    const uptimePct = Math.round((healthyBoxes / coldBoxes.length) * 100);
    return { breachToday, uptimePct };
  }, []);

  if (loading) return <DashboardSkeleton />;

  return (
    <div className="space-y-6 p-6 animate-none">
      <style>{`
        @keyframes breach-pulse {
          0%, 100% { box-shadow: 0 0 0 rgba(239,68,68,0.0); }
          50% { box-shadow: 0 0 16px rgba(239,68,68,0.45); }
        }
      `}</style>

      {/* Stat row */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4 animate-none">
        {[
          { label: "Total Units", value: "432", icon: Droplet, note: "+18 today" },
          { label: "Active Cold Boxes", value: "4", icon: Thermometer, note: "1 in breach" },
          { label: "Pending Verifications", value: "3", icon: Fingerprint, note: "1 flagged" },
          { label: "Fleet Uptime", value: `${fleetStats.uptimePct}%`, icon: HeartPulse, note: `${fleetStats.breachToday} breach event(s) today` },
        ].map((s) => (
          <Glass key={s.label} className="p-4 animate-none">
            <div className="mb-2 flex items-center justify-between animate-none">
              <span className="text-xs" style={{ color: "#8A97A6" }}>{s.label}</span>
              <s.icon size={15} style={{ color: ACCENT }} />
            </div>
            <div className="text-2xl font-semibold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>{s.value}</div>
            <div className="mt-1 text-[11px]" style={{ color: "#5B6572" }}>{s.note}</div>
          </Glass>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3 animate-none">
        {/* Inventory grid */}
        <Glass className="p-5 lg:col-span-2 animate-none">
          <div className="mb-4 flex items-center justify-between animate-none">
            <h2 className="text-sm font-semibold text-white">Blood Inventory</h2>
            <button onClick={activeOpenAdjust} className="flex items-center gap-1 rounded-lg border px-2.5 py-1 text-xs cursor-pointer border-solid" style={{ borderColor: "rgba(255,255,255,0.1)", color: ACCENT }}>
              <Plus size={12} /> Adjust stock
            </button>
          </div>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 animate-none">
            {inventory.map((b) => {
              const s = STATE[b.state];
              const pct = Math.round((b.units / b.cap) * 100);
              return (
                <div key={b.type} className="rounded-xl border p-3 border-solid" style={{ borderColor: s.border, background: s.bg }}>
                  <div className="flex items-center justify-between animate-none">
                    <span className="text-sm font-bold text-white">{b.type}</span>
                    <span className="h-1.5 w-1.5 rounded-full" style={{ background: s.dot }} />
                  </div>
                  <div className="mt-2 text-lg font-semibold" style={{ color: s.text, fontFamily: "'JetBrains Mono', monospace" }}>{b.units}</div>
                  <div className="text-[10px]" style={{ color: "#8A97A6" }}>of {b.cap} units · {pct}%</div>
                  <div className="mt-2 h-1 w-full overflow-hidden rounded-full animate-none" style={{ background: "rgba(255,255,255,0.08)" }}>
                    <div className="h-full rounded-full" style={{ width: `${pct}%`, background: s.dot }} />
                  </div>
                </div>
              );
            })}
          </div>
        </Glass>

        {/* Alert feed */}
        <Glass className="p-5 animate-none">
          <h2 className="mb-4 text-sm font-semibold text-white">Recent Alerts</h2>
          <div className="space-y-3 animate-none">
            {alertFeed.map((a) => {
              const s = STATE[a.state];
              return (
                <button
                  key={a.id}
                  onClick={a.state === "breach" ? activeOpenAlert : undefined}
                  className="w-full rounded-lg border-l-2 py-1.5 pl-3 text-left transition-opacity hover:opacity-80 cursor-pointer border-y-0 border-r-0 border-solid"
                  style={{ borderColor: s.dot }}
                >
                  <p className="text-xs leading-snug text-white">{a.msg}</p>
                  <span className="text-[10px]" style={{ color: "#5B6572" }}>{a.time}</span>
                </button>
              );
            })}
          </div>
        </Glass>
      </div>

      {/* Explainable AI / demand forecast panel — new required section */}
      <PredictionPanel data={prediction} />

      {/* Cold box status row */}
      <Glass className="p-5 animate-none">
        <h2 className="mb-4 text-sm font-semibold text-white">Cold Box Fleet</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4 animate-none">
          {coldBoxes.map((c) => {
            const s = STATE[c.state];
            return (
              <div
                key={c.id}
                className="rounded-xl border p-3 border-solid"
                style={{
                  borderColor: "rgba(255,255,255,0.08)",
                  animation: c.state === "breach" ? "breach-pulse 1.8s ease-in-out infinite" : "none",
                }}
              >
                <div className="mb-2 flex items-center justify-between animate-none">
                  <span className="font-mono text-xs text-white">{c.id}</span>
                  <StatePill state={c.state} />
                </div>
                <p className="mb-2 text-[11px]" style={{ color: "#8A97A6" }}>{c.loc}</p>
                <div className="flex items-center justify-between text-xs animate-none">
                  <span className="flex items-center gap-1" style={{ color: s.text }}>
                    <Thermometer size={12} /> {c.temp}°C
                  </span>
                  <span className="flex items-center gap-1" style={{ color: "#8A97A6" }}>
                    <Battery size={12} /> {c.batt}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </Glass>
    </div>
  );
}
