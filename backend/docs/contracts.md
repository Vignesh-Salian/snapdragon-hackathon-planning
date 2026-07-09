# HemaGrid AI - Subsystem Interface Contracts

This document contains payload schemas, types, and integration protocols for all subsystems within the HemaGrid AI ecosystem.

---

## 1. Smart Cold Box (Hardware -> Backend)

*   **Protocol:** Serial UART bridged to WebSockets (or HTTP POST)
*   **Update Rate:** 1 Hz (Every 1 second)

### Telemetry Packet Schema
```json
{
  "device_id": "cold_box_001",
  "uptime_ms": 124500,
  "telemetry": {
    "temperature_c": 4.2,
    "humidity_pct": 52.3,
    "acceleration_g": 0.12,
    "max_impact_g": 1.45
  },
  "status": {
    "state": "SAFE",
    "flags": {
      "temp_breached": false,
      "impact_breached": false
    }
  }
}
```

---

## 2. Donor Verification (Backend -> Face Recognition)

*   **Protocol:** HTTP REST POST (Multipart Form-Data upload)

### `/api/v1/donor/enroll` Request
*   **Fields:**
    *   `name` (string)
    *   `image` (binary upload)
*   **Response (JSON):**
    ```json
    {
      "status": "success",
      "donor_id": 105,
      "message": "Donor successfully enrolled"
    }
    ```

### `/api/v1/donor/verify` Request
*   **Fields:**
    *   `image` (binary upload)
*   **Response (Duplicate Flagged - 409 Conflict):**
    ```json
    {
      "duplicate_detected": true,
      "confidence": 0.95,
      "matched_donor": {
        "id": 12,
        "name": "Jane Doe",
        "enrolled_at": "2026-07-09T14:12:00Z"
      },
      "message": "Fraud Alert: This donor has already registered within the lockout window."
    }
    ```

---

## 3. AI Intelligence (Backend -> AI Engine)

*   **Protocol:** HTTP REST POST (JSON payload)

### `/api/v1/predict/demand` Request
```json
{
  "hospital_id": 4,
  "hospital_type": "Trauma",
  "blood_type": "O_NEG",
  "temperature_c": 31.5,
  "dengue_cases_weekly": 145,
  "day_of_week": 5,
  "month": 7
}
```

### Response
```json
{
  "status": "success",
  "predictions": {
    "expected_demand_units": 18.4,
    "recommended_min_inventory": 25,
    "alert_level": "WARNING"
  }
}
```

---

## 4. Dashboard (Backend -> React Dashboard)

*   **Protocol:** WebSockets Server Broadcast
*   **Channel:** `/ws/live`

### Real-Time Update Stream Payload
Every time a telemetry packet or duplicate donor event occurs, the backend broadcasts this payload to all active dashboard connections:

```json
{
  "event_type": "TELEMETRY_UPDATE",
  "timestamp": "2026-07-09T15:34:00Z",
  "data": {
    "device_id": "cold_box_001",
    "state": "SAFE",
    "temperature_c": 4.2,
    "max_impact_g": 1.45,
    "alert_flags": {
      "temp_breached": false,
      "impact_breached": false
    }
  }
}
```

If a duplicate donor is flagged at a registration desk, the backend broadcasts:

```json
{
  "event_type": "FRAUD_ALERT",
  "timestamp": "2026-07-09T15:34:05Z",
  "data": {
    "matched_donor_name": "Jane Doe",
    "match_confidence": 0.95,
    "location": "Hospital Registration Desk 1"
  }
}
```
