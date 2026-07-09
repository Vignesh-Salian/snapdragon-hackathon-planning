# HemaGrid AI

> **Smart, Connected Blood Logistics & Verification**  
> *A collaborative edge AI intelligence network designed for the Qualcomm Snapdragon Multiverse Hackathon.*

---

## 📋 Overview

HemaGrid AI is a distributed, connected cold chain monitoring and donor verification system designed to optimize the blood donation and supply pipeline. By linking low-power edge microcontrollers, on-device mobile face recognition, and Snapdragon-powered AI PCs, HemaGrid AI ensures that blood reserves are monitored, secured, and distributed efficiently.

---

## 🏗 System Architecture

```text
                  +--------------------------+
                  |  Smart Cold Box (Arduino)|
                  +------------┬-------------+
                               │ Serial JSON (USB)
                               v
                  +--------------------------+
                  |    Core Backend (FastAPI)|
                  +----┬────────────────┬----+
                       │                │
             HTTP POST │                │ HTTP POST
                       v                v
          +-----------------+      +-----------------+
          |Donor Verification|      | AI Intelligence |
          | - MediaPipe     |      | - ONNX Predictor|
          +-----------------+      +-----------------+
                               │
                               │ WebSocket
                               v
                  +--------------------------+
                  |  Dashboard App (React)   |
                  +--------------------------+
```

---

## 📂 Repository Structure & Assignments

This repository contains the system specification and individual developer README files. Each contributor owns a specific, isolated module to enable parallel development.

*   **[`IMPLEMENTATION_PLAN.md`](file:///C:/Users/Vignesh/snapdragon-hackathon-planning/IMPLEMENTATION_PLAN.md)** - Master engineering architecture and integration specs.
*   **[`backend/README.md`](file:///C:/Users/Vignesh/snapdragon-hackathon-planning/backend/README.md) (Mithun)** - **Backend Platform:** FastAPI backend, SQLite database schemas, REST APIs, WebSockets, and integration interfaces.
*   **[`dashboard/README.md`](file:///C:/Users/Vignesh/snapdragon-hackathon-planning/dashboard/README.md) (Shaun)** - **Frontend Dashboard:** React dashboard, live monitoring alerts, inventory visualizations, and demo control UI.
*   **[`ai-engine/README.md`](file:///C:/Users/Vignesh/snapdragon-hackathon-planning/ai-engine/README.md) (Tejas)** - **AI Intelligence:** Demand predictions, inventory forecasting models, training scripts, and ONNX compiler pipelines.
*   **[`face-recognition/README.md`](file:///C:/Users/Vignesh/snapdragon-hackathon-planning/face-recognition/README.md) (Vignesh)** - **Donor Verification:** Face recognition, MediaPipe landmarks, duplicate checks, and validation REST APIs.
*   **[`hardware/README.md`](file:///C:/Users/Vignesh/snapdragon-hackathon-planning/hardware/README.md) (Hardware Team)** - **Smart Cold Box:** Arduino UNO Q firmware, temperature/shock sensors, calibration, and USB serial output.

---

## 🛠 Tech Stack

| Module | Technologies | Target Environment |
| :--- | :--- | :--- |
| **Core Backend** | Python, FastAPI, SQLite, WebSockets | Snapdragon X Elite PC |
| **Frontend** | React, TypeScript, TailwindCSS, Chart.js | Web Browser |
| **AI Engine** | Python, Scikit-Learn, ONNX Runtime | Hexagon NPU (via QNN EP) |
| **Face Recognition** | Python, OpenCV, MediaPipe | CPU / GPU / Mobile NPU |
| **IoT Node** | Arduino C++, Temp Sensor, Accelerometer | Arduino UNO R4 WiFi / Minima |

---

## 🚀 Development Workflow

To ensure integration proceeds smoothly during the hackathon:

1.  **Branching Rule:** Always branch from `main` to a feature branch (e.g. `feature/backend-inventory`).
2.  **Pull Requests:** Submit PRs back to `main` with detailed descriptions. Code must pass local test sweeps.
3.  **Namespace Isolation:** Ensure all code and build dependencies are kept within your designated workspace folder. Do not modify files in other folders.

---

## 📅 Timeline & Execution

*   **Pre-Event Development:** All contributors work independently in their respective folders, matching the JSON schema contracts specified in the README assignments.
*   **Hackathon Assembly:** The team will converge to flash the microcontrollers, compile target ONNX models to NPU binaries using the QAIRT SDK, and execute end-to-end integration testing on Snapdragon hardware.
