
export type StateKey = "safe" | "warning" | "breach";

export interface StateToken {
  text: string;
  bg: string;
  border: string;
  dot: string;
  label: string;
}

export const STATE: Record<StateKey, StateToken> = {
  safe: { text: "#4ADE80", bg: "rgba(34,197,94,0.12)", border: "rgba(74,222,128,0.35)", dot: "#22C55E", label: "Safe" },
  warning: { text: "#FBBF24", bg: "rgba(245,165,36,0.12)", border: "rgba(251,191,36,0.35)", dot: "#F5A524", label: "Warning" },
  breach: { text: "#F87171", bg: "rgba(239,68,68,0.14)", border: "rgba(248,113,113,0.4)", dot: "#EF4444", label: "Breach" },
};

export const ACCENT = "#2FD9C4";
export const CONFIDENCE_THRESHOLD = 90;

export interface MatchedDonor {
  id: number;
  name: string;
  enrolled_at: string;
}

export interface DonorVerifyResponse {
  duplicate_detected: boolean;
  confidence: number;
  matched_donor: MatchedDonor;
  message: string;
}

export type AlertLevel = "SAFE" | "WARNING" | "CRITICAL";

export interface DemandPrediction {
  expected_demand_units: number;
  recommended_inventory: number;
  inventory_health_score: number;
  alert_level: AlertLevel;
}

export interface PredictionResponse {
  status: string;
  prediction: DemandPrediction;
  top_contributors?: string[];
}

export interface TelemetryPoint {
  t: string;
  temp: number;
  accel: number;
}

export interface BloodInventoryItem {
  type: string;
  units: number;
  cap: number;
  state: StateKey;
}

export interface ColdBox {
  id: string;
  loc: string;
  temp: number;
  batt: number;
  state: StateKey;
}

export interface AlertFeedItem {
  id: number;
  state: StateKey;
  msg: string;
  time: string;
}

export interface VerificationQueueItem {
  response: DonorVerifyResponse;
  state: StateKey;
}

export type PageKey = "login" | "dashboard" | "telemetry" | "verify" | "diagnostics";

export function alertLevelToState(level: AlertLevel): StateKey {
  if (level === "SAFE") return "safe";
  if (level === "WARNING") return "warning";
  return "breach";
}

export function predictTimeToBreach(data: TelemetryPoint[], threshold = 6.0, intervalMinutes = 30): number | null {
  const recent = data.slice(-3);
  if (recent.length < 2) return null;
  const slope = (recent[recent.length - 1].temp - recent[0].temp) / (recent.length - 1);
  const current = recent[recent.length - 1].temp;
  if (slope <= 0 || current >= threshold) return current >= threshold ? 0 : null;
  const stepsAway = (threshold - current) / slope;
  return Math.round(stepsAway * intervalMinutes);
}

export interface WSTelemetryPayload {
  device_id: string;
  temp: number;
  batt: number;
  accel: number;
}

export type WSMessage =
  | { type: "TELEMETRY_UPDATE"; payload: WSTelemetryPayload }
  | { type: "FRAUD_ALERT"; payload: DonorVerifyResponse };

