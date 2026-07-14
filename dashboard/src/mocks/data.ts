import type { TelemetryPoint, BloodInventoryItem, ColdBox, AlertFeedItem, VerificationQueueItem, PredictionResponse } from "../types";

export const telemetryData: TelemetryPoint[] = [
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

export const bloodInventory: BloodInventoryItem[] = [
  { type: "O+", units: 142, cap: 200, state: "safe" },
  { type: "O-", units: 18, cap: 120, state: "breach" },
  { type: "A+", units: 96, cap: 150, state: "safe" },
  { type: "A-", units: 34, cap: 100, state: "warning" },
  { type: "B+", units: 71, cap: 120, state: "safe" },
  { type: "B-", units: 22, cap: 90, state: "warning" },
  { type: "AB+", units: 40, cap: 60, state: "safe" },
  { type: "AB-", units: 9, cap: 50, state: "breach" },
];

export const coldBoxes: ColdBox[] = [
  { id: "CB-014", loc: "Dispatch Bay 2", temp: 4.2, batt: 88, state: "safe" },
  { id: "CB-021", loc: "In Transit — NH44", temp: 7.8, batt: 61, state: "breach" },
  { id: "CB-009", loc: "Cold Room A", temp: 5.6, batt: 94, state: "warning" },
  { id: "CB-033", loc: "Cold Room B", temp: 4.0, batt: 73, state: "safe" },
];

export const alertFeed: AlertFeedItem[] = [
  { id: 1, state: "breach", msg: "CB-021 temperature exceeded 7.5°C threshold", time: "2 min ago" },
  { id: 2, state: "warning", msg: "CB-009 nearing upper temperature limit", time: "18 min ago" },
  { id: 3, state: "breach", msg: "Duplicate donor match — Anita R. (94.2%)", time: "41 min ago" },
  { id: 4, state: "safe", msg: "CB-014 recalibrated and back in range", time: "1 hr ago" },
];

export const verificationQueue: VerificationQueueItem[] = [
  {
    response: { duplicate_detected: false, confidence: 98.7, matched_donor: { id: 0, name: "Rahul Menon", enrolled_at: "" }, message: "New donor, no match found." },
    state: "safe",
  },
  {
    response: { duplicate_detected: true, confidence: 94.2, matched_donor: { id: 112, name: "Anita R.", enrolled_at: "2026-06-08T10:14:00" }, message: "Duplicate donor detected within 56-day lockout window." },
    state: "breach",
  },
  {
    response: { duplicate_detected: false, confidence: 61.0, matched_donor: { id: 0, name: "Devika S.", enrolled_at: "" }, message: "Low-confidence partial match, manual review recommended." },
    state: "warning",
  },
  {
    response: { duplicate_detected: false, confidence: 99.1, matched_donor: { id: 0, name: "Farhan Iqbal", enrolled_at: "" }, message: "New donor, no match found." },
    state: "safe",
  },
];

export const mockPrediction: PredictionResponse = {
  status: "success",
  prediction: {
    expected_demand_units: 43,
    recommended_inventory: 60,
    inventory_health_score: 84,
    alert_level: "SAFE",
  },
  top_contributors: ["High dengue cases", "Trauma hospital", "Increased emergency admissions"],
};
