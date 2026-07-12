import React, { useState, useEffect, useMemo } from "react";
import {
  LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from "recharts";
import {
  Activity, Droplet, ShieldAlert, LayoutDashboard, Radio, Bell,
  ChevronDown, Battery, Wifi, WifiOff, Thermometer, User, Fingerprint,
  CheckCircle2, AlertTriangle, XCircle, LogIn, Building2, Search, X, Plus, Minus,
  Settings, Server, Clock, TrendingUp, HeartPulse, SearchX
} from "lucide-react";

/* ---------------------------------------------------------
   DESIGN TOKENS
   bg-void   #0A0D12  base canvas
   bg-panel  rgba(255,255,255,0.035) glass fill
   border    rgba(255,255,255,0.08)
   accent    #2FD9C4  teal — brand / primary actions (kept
             separate from status colors so it never reads
             as a state)
   safe      #22C55E
   warning   #F5A524
   breach    #EF4444
--------------------------------------------------------- */

const STATE = {
  safe:    { text: "#4ADE80", bg: "rgba(34,197,94,0.12)",  border: "rgba(74,222,128,0.35)", dot: "#22C55E", label: "Safe" },
  warning: { text: "#FBBF24", bg: "rgba(245,165,36,0.12)", border: "rgba(251,191,36,0.35)", dot: "#F5A524", label: "Warning" },
  breach:  { text: "#F87171", bg: "rgba(239,68,68,0.14)",  border: "rgba(248,113,113,0.4)", dot: "#EF4444", label: "Breach" },
};

const ACCENT = "#2FD9C4";
const CONFIDENCE_THRESHOLD = 90; // frontend-defined flagging threshold, shown for transparency

function Glass({ children, className = "", style = {} }) {
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

function StatePill({ state }) {
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

/* Signature element: a live ECG / pulse trace across the top bar.
   Literal "blood" motif + functional live-connection indicator —
   freezes and turns red the moment the socket is considered down. */
function PulseTrace({ connected }) {
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

/* --------------------------- Skeletons --------------------------- */
function SkeletonBlock({ className = "", style = {} }) {
  return (
    <div
      className={`animate-pulse rounded-xl ${className}`}
      style={{ background: "rgba(255,255,255,0.05)", ...style }}
    />
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6 p-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => <SkeletonBlock key={i} style={{ height: 92 }} />)}
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <SkeletonBlock className="lg:col-span-2" style={{ height: 220 }} />
        <SkeletonBlock style={{ height: 220 }} />
      </div>
      <SkeletonBlock style={{ height: 160 }} />
    </div>
  );
}

/* --------------------------- Derived data helpers --------------------------- */
// Predicts minutes-to-breach using the slope of the last few readings —
// purely computed from telemetry already on screen, no new backend field.
function predictTimeToBreach(data, threshold = 6.0, intervalMinutes = 30) {
  const recent = data.slice(-3);
  if (recent.length < 2) return null;
  const slope = (recent[recent.length - 1].temp - recent[0].temp) / (recent.length - 1);
  const current = recent[recent.length - 1].temp;
  if (slope <= 0 || current >= threshold) return current >= threshold ? 0 : null;
  const stepsAway = (threshold - current) / slope;
  return Math.round(stepsAway * intervalMinutes);
}

const telemetryData = [
  { t: "09:00", temp: 4.1, accel: 0.02 },
  { t: "09:30", temp: 4.3, accel: 0.03 },
  { t: "10:00", temp: 4.2, accel: 0.01 },
  { t: "10:30", temp: 5.1, accel: 0.04 },
  { t: "11:00", temp: 6.4, accel: 0.09 },
  { t: "11:30", temp: 7.8, accel: 0.31 },
  { t: "12:00", temp: 6.9, accel: 0.12 },
  { t: "12:30", temp: 5.0, accel: 0.05 },
  { t: "13:00", temp: 4.4, accel: 0.02 },
];

const bloodInventory = [
  { type: "O+",  units: 142, cap: 200, state: "safe" },
  { type: "O-",  units: 18,  cap: 120, state: "breach" },
  { type: "A+",  units: 96,  cap: 150, state: "safe" },
  { type: "A-",  units: 34,  cap: 100, state: "warning" },
  { type: "B+",  units: 71,  cap: 120, state: "safe" },
  { type: "B-",  units: 22,  cap: 90,  state: "warning" },
  { type: "AB+", units: 40,  cap: 60,  state: "safe" },
  { type: "AB-", units: 9,   cap: 50,  state: "breach" },
];

const coldBoxes = [
  { id: "CB-014", loc: "Dispatch Bay 2", temp: 4.2, batt: 88, state: "safe" },
  { id: "CB-021", loc: "In Transit — NH44", temp: 7.8, batt: 61, state: "breach" },
  { id: "CB-009", loc: "Cold Room A", temp: 5.6, batt: 94, state: "warning" },
  { id: "CB-033", loc: "Cold Room B", temp: 4.0, batt: 73, state: "safe" },
];

const alertFeed = [
  { id: 1, state: "breach",  msg: "CB-021 temperature exceeded 7.5°C threshold", time: "2 min ago" },
  { id: 2, state: "warning", msg: "CB-009 nearing upper temperature limit",       time: "18 min ago" },
  { id: 3, state: "breach",  msg: "Duplicate donor match — Anita R. (94.2%)",     time: "41 min ago" },
  { id: 4, state: "safe",    msg: "CB-014 recalibrated and back in range",        time: "1 hr ago" },
];

const verificationQueue = [
  { name: "Rahul Menon",   conf: 98.7, state: "safe" },
  { name: "Anita R.",      conf: 94.2, state: "breach" },
  { name: "Devika S.",     conf: 61.0, state: "warning" },
  { name: "Farhan Iqbal",  conf: 99.1, state: "safe" },
];

function NavItem({ icon: Icon, label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className="flex w-full items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm transition-colors"
      style={{
        color: active ? "#E7FBF8" : "#8A97A6",
        background: active ? "rgba(47,217,196,0.10)" : "transparent",
        borderLeft: active ? `2px solid ${ACCENT}` : "2px solid transparent",
      }}
    >
      <Icon size={17} strokeWidth={2} />
      <span className="font-medium">{label}</span>
    </button>
  );
}

function TopBar({ hospital, connected, secondsSinceSync }) {
  const syncLabel = secondsSinceSync < 60 ? `${secondsSinceSync}s ago` : `${Math.floor(secondsSinceSync / 60)}m ago`;
  const stale = secondsSinceSync > 15;
  return (
    <div className="border-b" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
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

/* ---------------- PAGE: LOGIN / HOSPITAL SELECT ---------------- */
function LoginPage({ onEnter }) {
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
          <input defaultValue="HSP-0417 — St. Alphonsa Medical Center" className="w-full bg-transparent text-sm text-white outline-none" readOnly />
        </div>

        <label className="mb-1.5 block text-xs font-medium" style={{ color: "#8A97A6" }}>Operator PIN</label>
        <div className="mb-6 flex items-center gap-2 rounded-lg border px-3 py-2.5" style={{ borderColor: "rgba(255,255,255,0.1)", background: "rgba(255,255,255,0.03)" }}>
          <Fingerprint size={15} style={{ color: "#8A97A6" }} />
          <input defaultValue="••••••" className="w-full bg-transparent text-sm text-white outline-none" readOnly />
        </div>

        <button
          onClick={onEnter}
          className="flex w-full items-center justify-center gap-2 rounded-lg py-2.5 text-sm font-semibold text-black transition-opacity hover:opacity-90"
          style={{ background: ACCENT }}
        >
          <LogIn size={15} /> Enter dashboard
        </button>
        <p className="mt-4 text-center text-[11px]" style={{ color: "#5B6572" }}>Session syncs to ws://127.0.0.1:8002/ws/live</p>
      </Glass>
    </div>
  );
}

/* ---------------- PAGE: MAIN DASHBOARD ---------------- */
function DashboardPage({ openAlert, openAdjust }) {
  const [loading, setLoading] = useState(true);
  useEffect(() => {
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
    <div className="space-y-6 p-6">
      <style>{`
        @keyframes breach-pulse {
          0%, 100% { box-shadow: 0 0 0 rgba(239,68,68,0.0); }
          50% { box-shadow: 0 0 16px rgba(239,68,68,0.45); }
        }
      `}</style>

      {/* Stat row */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {[
          { label: "Total Units", value: "432", icon: Droplet, note: "+18 today" },
          { label: "Active Cold Boxes", value: "4", icon: Thermometer, note: "1 in breach" },
          { label: "Pending Verifications", value: "3", icon: Fingerprint, note: "1 flagged" },
          { label: "Fleet Uptime", value: `${fleetStats.uptimePct}%`, icon: HeartPulse, note: `${fleetStats.breachToday} breach event(s) today` },
        ].map((s) => (
          <Glass key={s.label} className="p-4">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs" style={{ color: "#8A97A6" }}>{s.label}</span>
              <s.icon size={15} style={{ color: ACCENT }} />
            </div>
            <div className="text-2xl font-semibold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>{s.value}</div>
            <div className="mt-1 text-[11px]" style={{ color: "#5B6572" }}>{s.note}</div>
          </Glass>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Inventory grid */}
        <Glass className="p-5 lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">Blood Inventory</h2>
            <button onClick={openAdjust} className="flex items-center gap-1 rounded-lg border px-2.5 py-1 text-xs" style={{ borderColor: "rgba(255,255,255,0.1)", color: ACCENT }}>
              <Plus size={12} /> Adjust stock
            </button>
          </div>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {bloodInventory.map((b) => {
              const s = STATE[b.state];
              const pct = Math.round((b.units / b.cap) * 100);
              return (
                <div key={b.type} className="rounded-xl border p-3" style={{ borderColor: s.border, background: s.bg }}>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-white">{b.type}</span>
                    <span className="h-1.5 w-1.5 rounded-full" style={{ background: s.dot }} />
                  </div>
                  <div className="mt-2 text-lg font-semibold" style={{ color: s.text, fontFamily: "'JetBrains Mono', monospace" }}>{b.units}</div>
                  <div className="text-[10px]" style={{ color: "#8A97A6" }}>of {b.cap} units · {pct}%</div>
                  <div className="mt-2 h-1 w-full overflow-hidden rounded-full" style={{ background: "rgba(255,255,255,0.08)" }}>
                    <div className="h-full rounded-full" style={{ width: `${pct}%`, background: s.dot }} />
                  </div>
                </div>
              );
            })}
          </div>
        </Glass>

        {/* Alert feed */}
        <Glass className="p-5">
          <h2 className="mb-4 text-sm font-semibold text-white">Recent Alerts</h2>
          <div className="space-y-3">
            {alertFeed.map((a) => {
              const s = STATE[a.state];
              return (
                <button
                  key={a.id}
                  onClick={a.state === "breach" ? openAlert : undefined}
                  className="w-full rounded-lg border-l-2 py-1.5 pl-3 text-left transition-opacity hover:opacity-80"
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

      {/* Cold box status row */}
      <Glass className="p-5">
        <h2 className="mb-4 text-sm font-semibold text-white">Cold Box Fleet</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {coldBoxes.map((c) => {
            const s = STATE[c.state];
            return (
              <div
                key={c.id}
                className="rounded-xl border p-3"
                style={{
                  borderColor: "rgba(255,255,255,0.08)",
                  animation: c.state === "breach" ? "breach-pulse 1.8s ease-in-out infinite" : "none",
                }}
              >
                <div className="mb-2 flex items-center justify-between">
                  <span className="font-mono text-xs text-white">{c.id}</span>
                  <StatePill state={c.state} />
                </div>
                <p className="mb-2 text-[11px]" style={{ color: "#8A97A6" }}>{c.loc}</p>
                <div className="flex items-center justify-between text-xs">
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

/* ---------------- PAGE: TELEMETRY ---------------- */
function TelemetryPage() {
  const [active, setActive] = useState("CB-021");
  const activeBox = coldBoxes.find((c) => c.id === active);
  const breachEta = useMemo(() => predictTimeToBreach(telemetryData, 6.0), [active]);

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-wrap gap-2">
        {coldBoxes.map((c) => (
          <button
            key={c.id}
            onClick={() => setActive(c.id)}
            className="rounded-full border px-3 py-1.5 text-xs font-mono transition-colors"
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

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        <Glass className="p-5 lg:col-span-3">
          <div className="mb-1 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">Temperature — {active}</h2>
            <StatePill state={activeBox?.state ?? "safe"} />
          </div>
          <p className="mb-4 text-[11px]" style={{ color: "#5B6572" }}>Safe range: 2°C – 6°C · Threshold breach at 11:00–12:00</p>
          <ResponsiveContainer width="100%" height={260}>
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
        </Glass>

        <div className="space-y-4">
          <Glass className="p-4">
            <span className="text-xs" style={{ color: "#8A97A6" }}>Current Temp</span>
            <div className="text-2xl font-semibold" style={{ color: "#F87171", fontFamily: "'JetBrains Mono', monospace" }}>7.8°C</div>
          </Glass>

          {/* Predicted time-to-breach — derived client-side from the temp
              trend already in telemetryData, no new backend field. */}
          <Glass className="p-4" style={{ borderColor: breachEta !== null && breachEta <= 10 ? STATE.warning.border : undefined }}>
            <div className="flex items-center gap-1.5">
              <TrendingUp size={12} style={{ color: "#8A97A6" }} />
              <span className="text-xs" style={{ color: "#8A97A6" }}>Predicted Time-to-Breach</span>
            </div>
            <div className="text-2xl font-semibold" style={{ color: breachEta === 0 ? "#F87171" : breachEta !== null ? "#FBBF24" : "#4ADE80", fontFamily: "'JetBrains Mono', monospace" }}>
              {breachEta === 0 ? "Breached" : breachEta !== null ? `~${breachEta} min` : "Stable"}
            </div>
            <div className="mt-1 text-[10px]" style={{ color: "#5B6572" }}>projected from last 3 readings</div>
          </Glass>

          <Glass className="p-4">
            <span className="text-xs" style={{ color: "#8A97A6" }}>Shock Events (24h)</span>
            <div className="text-2xl font-semibold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>3</div>
          </Glass>
          <Glass className="p-4">
            <span className="text-xs" style={{ color: "#8A97A6" }}>Battery</span>
            <div className="text-2xl font-semibold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>{activeBox?.batt ?? 61}%</div>
          </Glass>
        </div>
      </div>

      <Glass className="p-5">
        <h2 className="mb-4 text-sm font-semibold text-white">Acceleration / Shock Log</h2>
        <ResponsiveContainer width="100%" height={140}>
          <LineChart data={telemetryData}>
            <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis dataKey="t" stroke="#5B6572" tick={{ fontSize: 11 }} />
            <YAxis stroke="#5B6572" tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={{ background: "#131820", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }} />
            <Line type="monotone" dataKey="accel" stroke="#F5A524" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </Glass>
    </div>
  );
}

/* ---------------- PAGE: DONOR VERIFICATION ---------------- */
function VerificationPage({ openAlert }) {
  const [query, setQuery] = useState("");
  const filtered = verificationQueue.filter((v) => v.name.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="space-y-6 p-6">
      <Glass className="p-5">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-sm font-semibold text-white">Verification Queue</h2>
          <div className="flex items-center gap-2">
            <span
              className="rounded-full border px-2.5 py-1 text-[11px]"
              style={{ borderColor: "rgba(255,255,255,0.1)", color: "#8A97A6" }}
              title="Matches above this confidence are auto-flagged as potential duplicates"
            >
              Flag threshold: {CONFIDENCE_THRESHOLD}%
            </span>
            <div className="flex items-center gap-2 rounded-lg border px-2.5 py-1.5 text-xs" style={{ borderColor: "rgba(255,255,255,0.1)", color: "#8A97A6" }}>
              <Search size={12} />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search donor"
                className="w-28 bg-transparent text-white outline-none placeholder:text-[#5B6572]"
              />
            </div>
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-2 py-10 text-center">
            <SearchX size={22} style={{ color: "#5B6572" }} />
            <p className="text-sm text-white">No matching donor found</p>
            <p className="text-[11px]" style={{ color: "#5B6572" }}>Check the spelling, or clear the search to see the full queue.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {filtered.map((v) => {
              const s = STATE[v.state];
              const overThreshold = v.conf >= CONFIDENCE_THRESHOLD;
              return (
                <div key={v.name} className="flex items-center justify-between rounded-lg border p-3" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full" style={{ background: s.bg }}>
                      <User size={14} style={{ color: s.text }} />
                    </div>
                    <div>
                      <p className="text-sm text-white">{v.name}</p>
                      <p className="text-[11px]" style={{ color: overThreshold ? s.text : "#5B6572" }}>
                        Confidence match: {v.conf}%{overThreshold ? ` — above ${CONFIDENCE_THRESHOLD}% threshold` : ""}
                      </p>
                    </div>
                  </div>
                  {v.state === "breach" ? (
                    <button onClick={openAlert} className="flex items-center gap-1 rounded-lg border px-3 py-1.5 text-xs font-medium" style={{ borderColor: s.border, color: s.text }}>
                      <ShieldAlert size={12} /> Review lockout
                    </button>
                  ) : (
                    <StatePill state={v.state} />
                  )}
                </div>
              );
            })}
          </div>
        )}
      </Glass>
    </div>
  );
}

/* ---------------- PAGE: SYSTEM DIAGNOSTICS ---------------- */
function DiagnosticsPage({ connected, onToggleConnection, secondsSinceSync }) {
  const rows = [
    { label: "REST API — Inventory", value: "GET /api/v1/inventory/{hospital_id}", ok: connected },
    { label: "REST API — Inventory Update", value: "POST /api/v1/inventory/update", ok: connected },
    { label: "WebSocket — Live Feed", value: "ws://127.0.0.1:8002/ws/live", ok: connected },
    { label: "Dashboard Port", value: "localhost:3000", ok: true },
  ];
  return (
    <div className="space-y-6 p-6">
      <Glass className="p-5">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="flex items-center gap-2 text-sm font-semibold text-white"><Server size={15} style={{ color: ACCENT }} /> Connection Diagnostics</h2>
          <button
            onClick={onToggleConnection}
            className="rounded-lg border px-3 py-1.5 text-xs font-medium"
            style={{ borderColor: "rgba(255,255,255,0.1)", color: "#8A97A6" }}
          >
            {connected ? "Simulate disconnect" : "Simulate reconnect"}
          </button>
        </div>
        <div className="space-y-2">
          {rows.map((r) => (
            <div key={r.label} className="flex items-center justify-between rounded-lg border p-3 text-xs" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
              <div>
                <p className="text-white">{r.label}</p>
                <p className="font-mono text-[11px]" style={{ color: "#5B6572" }}>{r.value}</p>
              </div>
              {r.ok ? <CheckCircle2 size={16} style={{ color: STATE.safe.dot }} /> : <XCircle size={16} style={{ color: STATE.breach.dot }} />}
            </div>
          ))}
        </div>
      </Glass>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Glass className="p-4">
          <div className="flex items-center gap-1.5"><Clock size={12} style={{ color: "#8A97A6" }} /><span className="text-xs" style={{ color: "#8A97A6" }}>Last Heartbeat</span></div>
          <div className="mt-1 text-lg font-semibold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>{secondsSinceSync}s ago</div>
        </Glass>
        <Glass className="p-4">
          <div className="flex items-center gap-1.5"><Building2 size={12} style={{ color: "#8A97A6" }} /><span className="text-xs" style={{ color: "#8A97A6" }}>Hospital ID</span></div>
          <div className="mt-1 text-lg font-semibold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>HSP-0417</div>
        </Glass>
        <Glass className="p-4">
          <div className="flex items-center gap-1.5"><Activity size={12} style={{ color: "#8A97A6" }} /><span className="text-xs" style={{ color: "#8A97A6" }}>Session State</span></div>
          <div className="mt-1"><StatePill state={connected ? "safe" : "breach"} /></div>
        </Glass>
      </div>
    </div>
  );
}

/* ---------------- MODAL: BIOMETRIC LOCKOUT (Breach) ---------------- */
function FraudAlertModal({ onClose }) {
  const s = STATE.breach;
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
          <button onClick={onClose}><X size={16} style={{ color: "#8A97A6" }} /></button>
        </div>

        <div className="mb-4 space-y-2 rounded-lg border p-3 text-xs" style={{ borderColor: s.border, background: s.bg }}>
          <div className="flex justify-between"><span style={{ color: "#8A97A6" }}>Matched name</span><span className="text-white">Anita R.</span></div>
          <div className="flex justify-between"><span style={{ color: "#8A97A6" }}>Confidence</span><span style={{ color: s.text }}>94.2% (threshold {CONFIDENCE_THRESHOLD}%)</span></div>
          <div className="flex justify-between"><span style={{ color: "#8A97A6" }}>Prior registration</span><span className="text-white font-mono">08 Jun 2026, 10:14</span></div>
          <div className="flex justify-between"><span style={{ color: "#8A97A6" }}>Location</span><span className="text-white">HSP-0417 Kiosk 2</span></div>
        </div>

        <div className="flex gap-2">
          <button onClick={onClose} className="flex-1 rounded-lg border py-2 text-xs font-medium" style={{ borderColor: "rgba(255,255,255,0.1)", color: "#8A97A6" }}>Dismiss</button>
          <button onClick={onClose} className="flex-1 rounded-lg py-2 text-xs font-semibold text-black" style={{ background: s.dot }}>Confirm lockout</button>
        </div>
      </Glass>
    </div>
  );
}

/* ---------------- MODAL: INVENTORY ADJUSTMENT ---------------- */
function AdjustModal({ onClose }) {
  const [units, setUnits] = useState(12);
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(5,4,6,0.7)", backdropFilter: "blur(4px)" }}>
      <Glass className="w-full max-w-sm p-6">
        <div className="mb-4 flex items-start justify-between">
          <h3 className="text-sm font-semibold text-white">Adjust Inventory</h3>
          <button onClick={onClose}><X size={16} style={{ color: "#8A97A6" }} /></button>
        </div>
        <label className="mb-1.5 block text-xs" style={{ color: "#8A97A6" }}>Blood type</label>
        <div className="mb-4 rounded-lg border px-3 py-2 text-sm text-white" style={{ borderColor: "rgba(255,255,255,0.1)" }}>O-  (breach — 18 units)</div>
        <label className="mb-1.5 block text-xs" style={{ color: "#8A97A6" }}>Units to add</label>
        <div className="mb-6 flex items-center gap-3">
          <button onClick={() => setUnits(Math.max(0, units - 1))} className="flex h-8 w-8 items-center justify-center rounded-lg border" style={{ borderColor: "rgba(255,255,255,0.1)" }}><Minus size={13} style={{ color: "#8A97A6" }} /></button>
          <span className="w-12 text-center text-lg font-semibold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>{units}</span>
          <button onClick={() => setUnits(units + 1)} className="flex h-8 w-8 items-center justify-center rounded-lg border" style={{ borderColor: "rgba(255,255,255,0.1)" }}><Plus size={13} style={{ color: "#8A97A6" }} /></button>
        </div>
        <button onClick={onClose} className="w-full rounded-lg py-2.5 text-xs font-semibold text-black" style={{ background: ACCENT }}>Submit adjustment</button>
      </Glass>
    </div>
  );
}

/* ---------------- APP SHELL ---------------- */
export default function HemaGridMockup() {
  const [page, setPage] = useState("login");
  const [showAlert, setShowAlert] = useState(false);
  const [showAdjust, setShowAdjust] = useState(false);
  const [connected, setConnected] = useState(true);
  const [secondsSinceSync, setSecondsSinceSync] = useState(0);

  // Ticking "last sync" clock — purely frontend, drives the stale-data banner.
  useEffect(() => {
    const interval = setInterval(() => {
      setSecondsSinceSync((s) => (connected ? 0 : s + 1));
    }, 1000);
    return () => clearInterval(interval);
  }, [connected]);

  useEffect(() => {
    if (connected) return;
    const interval = setInterval(() => setSecondsSinceSync((s) => s + 1), 1000);
    return () => clearInterval(interval);
  }, [connected]);

  return (
    <div className="min-h-screen w-full" style={{ background: "#0A0D12", fontFamily: "'Inter', sans-serif" }}>
      <style>{`
        @keyframes pulse-run { from { stroke-dashoffset: 620; } to { stroke-dashoffset: 0; } }
        .animate-pulse { animation: sk-pulse 1.4s ease-in-out infinite; }
        @keyframes sk-pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 0.25; } }
      `}</style>

      {page === "login" ? (
        <LoginPage onEnter={() => setPage("dashboard")} />
      ) : (
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <div className="hidden w-56 shrink-0 flex-col border-r p-4 md:flex" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
            <div className="mb-6 flex items-center gap-2 px-1">
              <Droplet size={16} style={{ color: ACCENT }} />
              <span className="text-sm font-semibold text-white">HemaGrid AI</span>
            </div>
            <div className="space-y-1">
              <NavItem icon={LayoutDashboard} label="Dashboard" active={page === "dashboard"} onClick={() => setPage("dashboard")} />
              <NavItem icon={Radio} label="Cold Box Telemetry" active={page === "telemetry"} onClick={() => setPage("telemetry")} />
              <NavItem icon={Fingerprint} label="Donor Verification" active={page === "verify"} onClick={() => setPage("verify")} />
              <NavItem icon={Settings} label="Diagnostics" active={page === "diagnostics"} onClick={() => setPage("diagnostics")} />
            </div>
            <div className="mt-auto space-y-2 rounded-xl border p-3 text-[11px]" style={{ borderColor: "rgba(255,255,255,0.08)", color: "#5B6572" }}>
              <p className="font-medium" style={{ color: "#8A97A6" }}>State legend</p>
              <div className="flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full" style={{ background: STATE.safe.dot }} /> Safe</div>
              <div className="flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full" style={{ background: STATE.warning.dot }} /> Warning</div>
              <div className="flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full" style={{ background: STATE.breach.dot }} /> Breach</div>
            </div>
          </div>

          {/* Main */}
          <div className="flex-1">
            <TopBar hospital="HSP-0417 — St. Alphonsa" connected={connected} secondsSinceSync={secondsSinceSync} />
            {page === "dashboard" && <DashboardPage openAlert={() => setShowAlert(true)} openAdjust={() => setShowAdjust(true)} />}
            {page === "telemetry" && <TelemetryPage />}
            {page === "verify" && <VerificationPage openAlert={() => setShowAlert(true)} />}
            {page === "diagnostics" && (
              <DiagnosticsPage
                connected={connected}
                onToggleConnection={() => { setConnected((c) => !c); setSecondsSinceSync(0); }}
                secondsSinceSync={secondsSinceSync}
              />
            )}
          </div>
        </div>
      )}

      {showAlert && <FraudAlertModal onClose={() => setShowAlert(false)} />}
      {showAdjust && <AdjustModal onClose={() => setShowAdjust(false)} />}
    </div>
  );
}
