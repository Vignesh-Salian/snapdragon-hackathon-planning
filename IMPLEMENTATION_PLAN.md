# HemaGrid AI - Implementation Plan & Architecture Record

This document serves as the master planning and architectural layout for HemaGrid AI. It defines module boundaries, communication protocols, interface contracts, git workflows, and our pre-hackathon development roadmap.

---

## 1. Project Overview

HemaGrid AI is a distributed, connected cold chain monitoring and donor verification system. It secures and optimizes the blood supply network by detecting transport compromises in real time, preventing duplicate donor registrations, and predicting hospital demand spikes.

---

## 2. System Architecture

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

## 3. Module Breakdown & Ownership

| Module | Primary Owner | Technologies | Folder Scope |
| :--- | :--- | :--- | :--- |
| **01 Core Backend** | Mithun | FastAPI, SQLite, SQLAlchemy, WebSockets | `/backend` |
| **02 Frontend Dashboard** | Shaun | React, TypeScript, TailwindCSS, Chart.js | `/dashboard` |
| **03 AI Intelligence** | Tejas | Python, Scikit-Learn, ONNX Runtime | `/ai-engine` |
| **04 Donor Verification** | Vignesh | Python, OpenCV, MediaPipe | `/face-recognition` |
| **05 Smart Cold Box** | Hardware Team | Arduino C++, DHT22, ADXL345 | `/hardware` |

---

## 4. Repository Structure

The unified repository structure for development is laid out as follows:

```text
snapdragon-hackathon-planning/
├── IMPLEMENTATION_PLAN.md    # Master planning (This Document)
├── 01-MITHUN-README.md        # Core Backend Specifications
├── 02-SHAUN-README.md         # Frontend Dashboard Specifications
├── 03-TEJAS-README.md         # AI Intelligence Specifications
├── 04-VIGNESH-README.md       # Donor Verification Specifications
├── 05-HARDWARE-README.md      # Smart Cold Box Specifications
├── backend/                  # Managed by Mithun
├── dashboard/                # Managed by Shaun
├── ai-engine/                # Managed by Tejas
├── face-recognition/         # Managed by Vignesh
└── hardware/                 # Managed by Hardware Team
```

---

## 5. Module Communication & API Contracts

All interfaces must strictly adhere to the contracts defined below. Changes to these schemas require alignment from all owners.

### 5.1 Hardware to Core Backend
*   **Protocol:** Serial JSON over USB (Baud rate: `115200`)
*   **Format:**
    ```json
    {
      "device_id": "string",
      "uptime_ms": "integer",
      "telemetry": {
        "temperature_c": "float",
        "humidity_pct": "float",
        "acceleration_g": "float",
        "max_impact_g": "float"
      },
      "status": {
        "state": "SAFE | WARNING | COMPROMISED",
        "flags": {
          "temp_breached": "boolean",
          "impact_breached": "boolean"
        }
      }
    }
    ```

### 5.2 Core Backend to Donor Verification
*   **Protocol:** HTTP POST (Multipart Form-Data)
*   **Endpoint:** `/api/v1/donor/verify`
*   **Payload:** Binary Image
*   **Response (200 OK / 409 Conflict):**
    ```json
    {
      "duplicate_detected": "boolean",
      "confidence": "float",
      "matched_donor": {
        "id": "integer",
        "name": "string",
        "enrolled_at": "string"
      },
      "message": "string"
    }
    ```

### 5.3 Core Backend to AI Engine
*   **Protocol:** HTTP POST (JSON)
*   **Endpoint:** `/api/v1/predict/demand`
*   **Payload:**
    ```json
    {
      "hospital_id": "integer",
      "hospital_type": "string",
      "blood_type": "string",
      "temperature_c": "float",
      "dengue_cases_weekly": "integer",
      "day_of_week": "integer",
      "month": "integer"
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "status": "success",
      "predictions": {
        "expected_demand_units": "float",
        "recommended_min_inventory": "integer",
        "alert_level": "SAFE | WARNING | CRITICAL"
      }
    }
    ```

### 5.4 Core Backend to Frontend Dashboard
*   **Protocol:** WebSocket (`/ws/live`)
*   **Broadcast Frame:**
    ```json
    {
      "event_type": "TELEMETRY_UPDATE | FRAUD_ALERT",
      "timestamp": "string (ISO 8601)",
      "data": "object"
    }
    ```

---

## 6. Pre-Hackathon Development Roadmap & Milestones

The schedule is designed to establish working, independent modules prior to on-site assembly.

```text
Pre-Hackathon Milestones:
[Week 1] Code Repositories Initialized & Schemas Frozen
[Week 2] Isolated Module Implementations Completed (Local Mock Tests)
[Week 3] Local Integration Testing (Mocks replaced with client services)
[Week 4] Edge Case Resolution & Demo Scenarios Programmed

On-Site Hackathon Plan (24-Hour Sprint):
Hour 00-02: Setup Qualcomm Hardware Laptops & Flash Arduino
Hour 02-06: Connect Core Backend to Real Hardware USB Ports
Hour 06-12: Bind AI & Face Models to Snapdragon NPUs using QAIRT / AI Hub
Hour 12-18: Complete End-to-End System Testing & Calibration
Hour 18-22: Demo Rehearsals, Pitch Tuning, UI Accents
Hour 22-24: Grand Finale Presentation Mode Active
```

---

## 7. Git Workflow & Branching Strategy

To avoid merge conflicts, all developers operate in separate directories and check-in to feature branches.

*   **Main Branch Protection:** No developer commits directly to `main`.
*   **Branch Naming Convention:**
    *   Mithun: `feature/backend-[feature-name]`
    *   Shaun: `feature/dashboard-[feature-name]`
    *   Tejas: `feature/ai-[feature-name]`
    *   Vignesh: `feature/face-[feature-name]`
    *   Hardware: `feature/hardware-[feature-name]`
*   **Commit Message Convention:**
    *   `feat(scope): add new feature`
    *   `fix(scope): resolve issue description`
    *   `docs(scope): update documentation`
*   **Pull Request Rule:** All Pull Requests require code compilation pass checks and approval from at least one other team member.
