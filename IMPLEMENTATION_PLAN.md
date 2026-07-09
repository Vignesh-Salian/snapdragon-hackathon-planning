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
+---------------------------------------+
|        Smart Cold Box (Arduino)       |
+-------------------┬-------------------+
                    │ Serial JSON (USB)
                    v
+---------------------------------------+
|           Core Backend (FastAPI)      |
+----┬──────────────────────┬─────────┬-+
     │                      │         │
     │ HTTP POST            │         │ HTTP POST
     v                      │         v
+-------------------+       │       +--------------------+
| Donor Verification|       │       | AI Intelligence    |
| - MediaPipe Mesh  |       │       | - Demand Predictor |
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
[Hardware Node] ────(UART/USB JSON)───► [Core Backend Hub] ◄───(WS JSON)───► [React Dashboard]
                                                │
                                                ├──(HTTP POST)──► [MediaPipe Face Module]
                                                │
                                                └──(HTTP POST)──► [ONNX Prediction Engine]
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
3.  **AI Intelligence (Tejas):** Dataset synthetics, Random Forest regressor, ONNX conversion compile pipeline, and prediction endpoint.
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

## 8. API Ownership

*   **Mithun:** Owns `/api/v1/inventory/*`, `/api/v1/telemetry/*`, `/ws/live`, and proxy handlers `/api/v1/donor/verify-delegate` and `/api/v1/predict/demand-delegate`.
*   **Vignesh:** Owns `/api/v1/donor/enroll` and `/api/v1/donor/verify`.
*   **Tejas:** Owns `/api/v1/predict/demand`.

---

## 9. Integration Strategy

All modules are developed locally in isolation using mock payload generators. At week 3, local HTTP clients are pointed to the respective development hosts. During the 24-hour hackathon, we will:
1.  Flash the Arduino and verify USB Serial binding on host PCs.
2.  Configure QAIRT SDK bindings to execute Tejas's and Vignesh's models on Snapdragon NPUs.
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

## 13. Development Timeline (Pre-Hackathon)

```text
Week 1: Folder scoping, interface contracts frozen, and DB schemas declared.
Week 2: Core modules implemented with local test configurations.
Week 3: Integration checkpoints: HTTP clients connected across local hosts.
Week 4: Dry runs with simulated payloads and edge-case testing.
```

---

## 14. Hackathon Integration Timeline (24-Hour Event)

```text
H00 - H02: Environment configuration: QAIRT SDK setup and NPU validation.
H02 - H06: USB serial binding checks and physical sensor calibration.
H06 - H12: Compile AI models (ONNX -> QNN Hexagon NPU libraries).
H12 - H18: End-to-end telemetry system stress tests.
H18 - H22: Demo UI polishing and presentation scripting.
H22 - H24: Active presentation mode: Live evaluation run.
```

---

## 15. Risks and Mitigation Plan

| Risk Description | Severity | Mitigation Plan |
| :--- | :--- | :--- |
| **Snapdragon NPU compiler mismatch**| Critical | Fallback to ONNX Runtime CPU execution. |
| **Telemetry network drop** | High | Buffer sensor frames locally on Arduino flash. |
| **Face recognition false acceptance** | High | Tuned Euclidean threshold defaults inside SQLite. |
