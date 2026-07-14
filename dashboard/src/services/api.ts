/**
 * REST client for the HemaGrid backend gateway (port 8002).
 *
 * Everything goes through the backend, which proxies AI (:8001) and face
 * (:8000) via its *-delegate routes — so the dashboard needs exactly one base
 * URL and never hits the microservices directly (avoids CORS + centralises traffic).
 */
import type {
  BloodInventoryItem,
  DonorVerifyResponse,
  PredictionResponse,
  StateKey,
} from "../types";

const BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8002";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new ApiError(res.status, body || res.statusText);
  }
  return res.json() as Promise<T>;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function unitsToState(units: number, cap: number): StateKey {
  const ratio = cap > 0 ? units / cap : 0;
  if (ratio < 0.2) return "breach";
  if (ratio < 0.4) return "warning";
  return "safe";
}

interface BackendInventoryRow {
  hospital_id: string;
  blood_type: string;
  units: number;
  capacity: number;
  updated_at: string;
}

export async function getInventory(hospitalId: string): Promise<BloodInventoryItem[]> {
  const data = await req<{ inventory: BackendInventoryRow[] }>(
    `/api/v1/inventory/${encodeURIComponent(hospitalId)}`,
  );
  return data.inventory.map((r) => ({
    type: r.blood_type,
    units: r.units,
    cap: r.capacity,
    state: unitsToState(r.units, r.capacity),
  }));
}

export async function updateInventory(
  hospitalId: string,
  bloodType: string,
  delta: number,
): Promise<void> {
  await req("/api/v1/inventory/update", {
    method: "POST",
    body: JSON.stringify({
      hospital_id: hospitalId,
      blood_type: bloodType,
      units_added_removed: delta,
    }),
  });
}

/** 16 fields: the 15 model features + current_inventory. */
export interface DemandFeatures {
  hospital_id: number;
  hospital_type: string;
  city_region: string;
  blood_type: string;
  season: string;
  temperature_c: number;
  rainfall_mm: number;
  dengue_cases_weekly: number;
  road_accidents: number;
  emergency_cases: number;
  scheduled_surgeries: number;
  holiday: number;
  blood_donation_camp: number;
  current_inventory: number;
  day_of_week: number;
  month: number;
}

export function predictDemand(features: DemandFeatures): Promise<PredictionResponse> {
  return req<PredictionResponse>("/api/v1/predict/demand-delegate", {
    method: "POST",
    body: JSON.stringify(features),
  });
}

/** Verify a donor face. Returns the match on 409, or a clean no-match on 200. */
export async function verifyDonor(imageB64: string): Promise<DonorVerifyResponse> {
  try {
    await req<{ duplicate_detected: false }>("/api/v1/donor/verify-delegate", {
      method: "POST",
      body: JSON.stringify({ image_b64: imageB64 }),
    });
    return {
      duplicate_detected: false,
      confidence: 0,
      matched_donor: { id: 0, name: "", enrolled_at: "" },
      message: "No matching donor in lockout window.",
    };
  } catch (e) {
    if (e instanceof ApiError && e.status === 409) {
      // FastAPI wraps our dict under { detail: {...} }
      const parsed = JSON.parse(e.message) as { detail: DonorVerifyResponse };
      return parsed.detail;
    }
    throw e;
  }
}

export function enrollDonor(name: string, imageB64: string): Promise<{ id: number }> {
  return req("/api/v1/donor/enroll-delegate", {
    method: "POST",
    body: JSON.stringify({ name, image_b64: imageB64 }),
  });
}

export function health(): Promise<{ status: string }> {
  return req("/health");
}
