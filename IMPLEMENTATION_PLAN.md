# HemaGrid AI - Engineering Implementation Plan

This document serves as the master engineering specification, architectural record, and project execution blueprint for HemaGrid AI. It governs the development phase leading up to the Qualcomm Snapdragon Multiverse Hackathon.

---

## 1. Executive Summary

HemaGrid AI is a smart, connected logistics and validation ecosystem designed to secure the blood supply chain. The system utilizes low-power edge microcontrollers to monitor blood conditions in transit, on-device biometric validation to prevent duplicate donor registrations, and centralized demand-forecasting models to optimize regional stock distribution. 

---

## 2. Project Vision

The project aims to solve critical logistics bottlenecks in blood supply management (specifically targeting regional constraints in India). By replacing siloed, independent tracking systems with a collaborative edge computing architecture, HemaGrid AI ensures that:
1.  No blood unit is silently compromised in transit.
2.  Biometric checks at donor desks block unsafe, over-frequent donations.
3.  Hospitals are alerted to forecasted stock demands before shortages occur.

---

## 3. System Architecture

```text
+-------------------------------------------------+
|          Smart Cold Box (Arduino UNO Q)        |
|  +--------------------+   Bridge   +---------+  |
|  | MPU: Linux (Python)|◄=========='| MCU: C++|  |
|  +---------┬----------+            +----+----+  |
+------------│----------------------------│-------+
             │                            │ Read Telemetry
             │ WiFi / WS (JSON)           ▼
             │                      [Sensors: Temp, Accel]
             v
+---------------------------------------+
|        Core Backend Hub (FastAPI)     |
+----┬──────────────────────┬─────────┬-+
     │                      │         │
     │ HTTP POST            │         │ HTTP POST
     v                      │         v
+-------------------+       │       +--------------------+
| Donor Verification|       │       | AI Intelligence    |
| - MediaPipe Mesh  |       │       | - LiteRT/ONNX (NPU)|
+-------------------+       │       +--------------------+
                            │ WebSocket
                            v
+---------------------------------------+
|        Frontend Dashboard (React)     |
+---------------------------------------+
```

---

## 4. High-Level Component Diagram

```text
[UNO Q: MCU] ───(Bridge RPC)───► [UNO Q: MPU] ───(WiFi WS/JSON)───► [Backend Hub] ◄───(WS)───► [Dashboard]
                                                                        │
                                                                        ├──(HTTP)──► [MediaPipe Face]
                                                                        └──(HTTP)──► [LiteRT/QNN NPU Engine]
```

---

## 5. Repository Structure

A clean mono-repo structure is used to prevent namespace collisions and cross-module git conflicts:

```text
snapdragon-hackathon-planning/
├── IMPLEMENTATION_PLAN.md    # Master planning (This Document)
├── README.md                 # Root developer landing guide
├── backend/                  # Mithun's workspace folder
│   └── README.md             # Core Backend Specifications
├── dashboard/                # Shaun's workspace folder
│   └── README.md             # Frontend Dashboard Specifications
├── ai-engine/                # Tejas's workspace folder
│   └── README.md             # AI Intelligence Specifications
├── face-recognition/         # Vignesh's workspace folder
│   └── README.md             # Donor Verification Specifications
└── hardware/                 # Hardware Team's workspace folder
    └── README.md             # Smart Cold Box Specifications
```

---

## 6. Module Responsibilities

1.  **Core Backend (Mithun):** Central routing hub, SQLite schema manager, WebSocket connection broker, and HTTP proxy clients.
2.  **Frontend Dashboard (Shaun):** React charting layouts, stateful alerts, and real-time inventory administration UI.
3.  **AI Intelligence (Tejas):** Dataset synthetics, Multi-Layer Perceptron (MLP) Neural Network regressor, ONNX conversion compile pipeline, and prediction endpoint.
4.  **Donor Verification (Vignesh):** MediaPipe Face Mesh landmark extraction, SQLite donor enrollment storage, and similarity search.
5.  **Smart Cold Box (Hardware):** Arduino C++ telemetry monitoring, state evaluation logic, LED alerts, and serial printer.

---

## 7. Communication Flow Between Modules

```text
1. Sensor Event:  Hardware -> Serial (JSON) -> Backend -> WebSocket -> Dashboard
2. Donor Check:   Dashboard -> HTTP POST -> Backend -> HTTP POST -> Face Module -> JSON response
3. Forecast Run:  Dashboard -> HTTP POST -> Backend -> HTTP POST -> AI Engine -> JSON response
```

---

## 8. API Ownership & Schemas

### API Gateway Proxies (Mithun)
*   **Mithun (Backend Hub)** acts as the API Gateway. External clients (like the Dashboard) must interact through these proxy endpoints rather than calling the isolated microservices directly, preventing CORS issues and centralizing traffic:
    *   `POST /api/v1/donor/enroll-delegate` -> Proxies to Vignesh's `/api/v1/donor/enroll`
    *   `POST /api/v1/donor/verify-delegate` -> Proxies to Vignesh's `/api/v1/donor/verify`
    *   `POST /api/v1/predict/demand-delegate` -> Proxies to Tejas's `/api/v1/predict/demand`
*   **Mithun** also directly owns `/api/v1/inventory/*`, `/api/v1/telemetry/*`, and the real-time WebSocket channel `/ws/live`.
*   **Vignesh** owns the internal `/api/v1/donor/enroll` and `/api/v1/donor/verify` microservice endpoints.
*   **Tejas** owns the internal `/api/v1/predict/demand` microservice endpoint.

### Master Telemetry JSON Schema (`POST /api/v1/telemetry/report`)
The hardware module and backend must strictly conform to the following telemetry schema:
```json
{
  "device_id": "string",
  "uptime_ms": 12345,
  "telemetry": {
    "temperature": 4.5,
    "humidity": 45.2,
    "shock_g": 0.8
  },
  "status": "SAFE" // (SAFE, WARNING, or COMPROMISED)
}
```

---

## 9. Integration Strategy

All modules are developed locally in isolation using mock payload generators. During the 24-hour hackathon, we will:
1.  Deploy Arduino sketches and Python daemons using Arduino App Lab to compile and launch MPU/MCU code on the UNO Q.
2.  Configure ONNX Runtime QNN Execution Provider (using native libraries like `libQnnHtp.so` and `libQnnSystem.so`) to run Tejas's and Vignesh's models on the target Snapdragon Hexagon NPU.
3.  Deploy the React dashboard to local test environments.

---

## 10. Development Workflow & Git Branching

### Git Branching Strategy
*   No direct commits to `main`.
*   Feature branches name prefix conventions:
    *   `feature/backend-...`
    *   `feature/dashboard-...`
    *   `feature/ai-...`
    *   `feature/face-...`
    *   `feature/hardware-...`

### Code Review Process
*   All Pull Requests must pass automated unit tests (run in local actions).
*   Requires code review approval from at least one other module owner.

---

## 11. Coding & Documentation Standards

*   **Coding Standards:**
    *   Python: PEP8 compliance, strict typing inputs, and Pydantic validation schemas.
    *   C++: Non-blocking loops, F() macro string literals, and zero dynamic memory allocations.
    *   TypeScript: Strict prop interfaces and isolated state containers.
*   **Documentation Standards:**
    *   All endpoints must be documented inside FastAPI OpenAPI specs.
    *   Hardware pins and connections must be cataloged in circuit schematics.

---

## 12. Testing Strategy

*   Each module contains an isolated `/tests` folder.
*   Integration tests mock external network boundaries using standard Python/JS mock libraries.
*   Tests must be run locally before opening pull requests.

---

## 13. 24-Hour Hackathon Development Timeline

```text
H00 - H04: Parallel core scaffolding (FastAPI endpoints, React panels, Arduino breadboard, ML training).
H04 - H08: Local model completion (ONNX compilation, Face detection setup) & sensor state evaluation mapping.
H08 - H12: NPU Integration: Port AI demand models and face verification to Snapdragon Hexagon NPU libraries.
H12 - H16: System Integration: Link HTTP clients to backend proxies and establish WebSocket dashboard connections.
H16 - H20: End-to-end system testing, sensor threshold calibration, and edge case resolution.
H20 - H24: Demo UI polishing, presentation script practice, and active staging.
```

---

## 15. Risks and Mitigation Plan

| Risk Description | Severity | Mitigation Plan |
| :--- | :--- | :--- |
| **Snapdragon NPU compiler mismatch**| Critical | Fallback to ONNX Runtime CPU execution. |
| **Silent NPU Fallback** | High | Program verification checks using `get_ep_devices()` to ensure the QNN EP is active instead of silently falling back to CPU. |
| **Telemetry network drop** | High | Buffer sensor frames locally on MPU storage, or stream via secondary serial USB fallbacks. |
| **Face recognition false acceptance** | High | Tuned Euclidean threshold defaults inside SQLite. |
