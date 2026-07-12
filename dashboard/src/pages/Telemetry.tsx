import React, { useState, useMemo } from "react";
import {
  LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from "recharts";
import { Thermometer, Battery, TrendingUp } from "lucide-react";
import { STATE, ACCENT, predictTimeToBreach } from "../types";
import { coldBoxes, telemetryData } from "../mocks/data";
import Glass from "../components/Glass";
import StatePill from "../components/StatePill";

/**
 * Cold Box Telemetry Viewer page showing real-time temperature, acceleration/shock logs and predictive breach estimates.
 */
export default function Telemetry() {
  const [active, setActive] = useState<string>("CB-021");
  const activeBox = coldBoxes.find((c) => c.id === active);
  const breachEta = useMemo(() => predictTimeToBreach(telemetryData, 6.0), [active]);

  return (
    <div className="space-y-6 p-6 animate-none">
      <div className="flex flex-wrap gap-2 animate-none">
        {coldBoxes.map((c) => (
          <button
            key={c.id}
            onClick={() => setActive(c.id)}
            className="rounded-full border px-3 py-1.5 text-xs font-mono transition-colors cursor-pointer border-solid"
            style={{
              borderColor: active === c.id ? ACCENT : "rgba(255,255,255,0.1)",
              color: active === c.id ? ACCENT : "#8A97A6",
              background: active === c.id ? "rgba(47,217,196,0.1)" : "transparent",
            }}
          >
            {c.id}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4 animate-none">
        <Glass className="p-5 lg:col-span-3 animate-none">
          <div className="mb-1 flex items-center justify-between animate-none">
            <h2 className="text-sm font-semibold text-white">Temperature — {active}</h2>
            <StatePill state={activeBox?.state ?? "safe"} />
          </div>
          <p className="mb-4 text-[11px]" style={{ color: "#5B6572" }}>Safe range: 2°C – 6°C · Threshold breach at 11:00–12:00</p>
          <div className="w-full h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={telemetryData}>
                <defs>
                  <linearGradient id="tempFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={ACCENT} stopOpacity={0.35} />
                    <stop offset="100%" stopColor={ACCENT} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="t" stroke="#5B6572" tick={{ fontSize: 11 }} />
                <YAxis stroke="#5B6572" tick={{ fontSize: 11 }} domain={[0, 9]} />
                <ReferenceLine y={6} stroke="#F5A524" strokeDasharray="4 4" />
                <Tooltip contentStyle={{ background: "#131820", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }} />
                <Area type="monotone" dataKey="temp" stroke={ACCENT} strokeWidth={2} fill="url(#tempFill)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Glass>

        <div className="space-y-4 animate-none">
          <Glass className="p-4 animate-none">
            <span className="text-xs" style={{ color: "#8A97A6" }}>Current Temp</span>
            <div className="text-2xl font-semibold" style={{ color: "#F87171", fontFamily: "'JetBrains Mono', monospace" }}>7.8°C</div>
          </Glass>

          {/* Predicted time-to-breach — derived client-side from the temp
              trend already in telemetryData, no new backend field. */}
          <Glass className="p-4 animate-none" style={{ borderColor: breachEta !== null && breachEta <= 10 ? STATE.warning.border : undefined }}>
            <div className="flex items-center gap-1.5 animate-none">
              <TrendingUp size={12} style={{ color: "#8A97A6" }} />
              <span className="text-xs" style={{ color: "#8A97A6" }}>Predicted Time-to-Breach</span>
            </div>
            <div className="text-2xl font-semibold" style={{ color: breachEta === 0 ? "#F87171" : breachEta !== null ? "#FBBF24" : "#4ADE80", fontFamily: "'JetBrains Mono', monospace" }}>
              {breachEta === 0 ? "Breached" : breachEta !== null ? `~${breachEta} min` : "Stable"}
            </div>
            <div className="mt-1 text-[10px]" style={{ color: "#5B6572" }}>projected from last 3 readings</div>
          </Glass>

          <Glass className="p-4 animate-none">
            <span className="text-xs" style={{ color: "#8A97A6" }}>Shock Events (24h)</span>
            <div className="text-2xl font-semibold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>3</div>
          </Glass>
          <Glass className="p-4 animate-none">
            <span className="text-xs" style={{ color: "#8A97A6" }}>Battery</span>
            <div className="text-2xl font-semibold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>{activeBox?.batt ?? 61}%</div>
          </Glass>
        </div>
      </div>

      <Glass className="p-5 animate-none">
        <h2 className="mb-4 text-sm font-semibold text-white">Acceleration / Shock Log</h2>
        <div className="w-full h-[140px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={telemetryData}>
              <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
              <XAxis dataKey="t" stroke="#5B6572" tick={{ fontSize: 11 }} />
              <YAxis stroke="#5B6572" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#131820", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }} />
              <Line type="monotone" dataKey="accel" stroke="#F5A524" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Glass>
    </div>
  );
}
