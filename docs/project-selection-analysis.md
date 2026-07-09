# Project Selection Analysis

This document serves as the formal Architecture Decision Record (ADR) and project selection analysis for our submission to the Qualcomm Snapdragon Multiverse Hackathon.

## Table of Contents
1. [Overview](#overview)
2. [Objective](#objective)
3. [Evaluation Criteria](#evaluation-criteria)
4. [Idea 1 – HemaGrid AI](#idea-1--hemagrid-ai)
   * [Workflow](#workflow)
   * [Strengths](#strengths)
   * [Weaknesses](#weaknesses)
   * [Technical Analysis](#technical-analysis)
   * [Feasibility](#feasibility)
   * [Risks](#risks)
5. [Idea 2 – SynapseX](#idea-2--synapsex)
   * [Workflow](#workflow)
   * [Strengths](#strengths)
   * [Weaknesses](#weaknesses)
   * [Technical Analysis](#technical-analysis)
   * [Feasibility](#feasibility)
   * [Risks](#risks)
6. [Side-by-Side Comparison](#side-by-side-comparison)
7. [Hardware Comparison](#hardware-comparison)
8. [Software Comparison](#software-comparison)
9. [Demo Comparison](#demo-comparison)
10. [24-Hour Execution Analysis](#24-hour-execution-analysis)
11. [Risk Matrix](#risk-matrix)
12. [Scoring Table](#scoring-table)
13. [Final Decision](#final-decision)
14. [Why We Selected This Project](#why-we-selected-this-project)
15. [Action Items](#action-items)
16. [Conclusion](#conclusion)

---

## Overview

A successful hackathon project requires a delicate balance of architectural innovation, execution feasibility, hardware availability, and a stable, high-impact demonstration. This analysis provides an engineering evaluation of two proposed concepts, HemaGrid AI and SynapseX, determining their viability within a restricted 24-hour development cycle using Qualcomm Snapdragon hardware.

---

## Objective

To select and commit to a single project that maximizes the probability of winning the Qualcomm Snapdragon Multiverse Hackathon. The evaluation is prioritized around execution reliability, integration complexity, and demo stability under rapid prototyping constraints.

---

## Evaluation Criteria

Projects are evaluated based on the following engineering dimensions:
*   **Feasibility (24-Hour Window):** Likelihood of completing a fully integrated, end-to-end prototype within the time limit.
*   **Hardware Accessibility:** Risk profile of setting up and operating required Qualcomm and third-party hardware on-site.
*   **Software and Compiler Stability:** Complexity of model compilation using the Qualcomm AI Engine Direct SDK (QAIRT) and Qualcomm AI Hub.
*   **Demo Reliability:** The presence of physical fail-safes and fallback mechanisms during live presentation.
*   **Qualcomm Alignment:** Level of integration with the Snapdragon heterogeneous computing ecosystem (CPU, GPU, NPU).
*   **Societal/Business Impact:** Clearness of the value proposition and real-world utility to judges.

---

## Idea 1 – HemaGrid AI

HemaGrid AI is a distributed, connected cold chain monitoring and donor validation system designed to secure and optimize the blood donation pipeline in India.

### Workflow

```text
+-----------------------+      +---------------------------+
|  Registration Desk   |      |  Cold Box Transport Unit  |
|  - Android Mobile     |      |  - Arduino UNO            |
|  - MediaPipe Vision   |      |  - Temp & Accel Sensors   |
+-----------+-----------+      +-------------+-------------+
            |                                |
            | WebSockets                     | WebSockets
            +----------------+---------------+
                             |
                             v
               +---------------------------+
               |  Hospital AI PC (Hub)     |
               |  - Snapdragon X Elite     |
               |  - Demand Predictor (ONNX)|
               +-------------+-------------+
                             |
                             v
               +---------------------------+
               |    Regional Cloud Sync    |
               |  - Firebase/AWS Backend   |
               +---------------------------+
```

1.  **Registration Validation:** An Android application captures donor facial landmarks using MediaPipe, matching against local vector caches to prevent fraud or over-frequent donations.
2.  **Cold Chain Monitoring:** Temperature and shock sensors on an Arduino unit continuously monitor the integrity of blood storage containers in transit.
3.  **Local Hub Aggregation:** Telemetry and donor events are streamed in real time via WebSockets to a local Snapdragon X Elite AI PC.
4.  **Demand Forecasting:** The AI PC runs a regression model to predict localized blood demand spikes.
5.  **Cloud Sync:** Anonymized logs and regional forecasts are synced to a cloud backend.

### Strengths
*   **High Parallelization:** Development modules (Android app, Arduino sensor integration, PC orchestration hub) have clean separation boundaries.
*   **Graceful Degradation:** The AI PC dashboard and analytics can fall back to standard CPU execution in minutes if the Qualcomm NPU compilation encounters runtime errors.
*   **Tangible Live Demo:** A physical cooler box can be physically shaken or heated to trigger instantaneous, visual alerts on the dashboard.

### Weaknesses
*   **Ecosystem Depth:** The local demand model is tabular, which does not showcase complex NPU-heavy generative workloads compared to a Large Language Model.

### Technical Analysis
*   **Model Complexity:** Low to Moderate. MediaPipe runs locally on mobile; the demand forecasting model uses lightweight tabular inference.
*   **Networking:** Simple real-time state synchronization using standard WebSocket JSON payloads.

### Feasibility
*   **High (85% Completion Probability):** Standard sensor logic, mature APIs, and straightforward UI layouts minimize development friction.

### Risks
*   **Telemetry Drops:** Wireless network drops in the demo room could break real-time sensor streams.
*   **Sensor Calibration:** Accelerometer thresholds must be finely tuned to avoid false alarms during transport.

---

## Idea 2 – SynapseX

SynapseX is a decentralized collaborative edge intelligence network where independent Snapdragon devices run local AI agents and coordinate reasoning to perform industrial predictive maintenance.

### Workflow

```text
+-----------------------+      +---------------------------+      +---------------------------+
|  IoT Edge Agent       |      |  Mobile CV Agent          |      |  Cloud AI 100             |
|  - Arduino TinyML     |      |  - Snapdragon Mobile      |      |  - Signature DB           |
|  - Vibration/Temp     |      |  - Defect YOLO & ASR      |      |  - Historical Patterns    |
+-----------+-----------+      +-------------+-------------+      +-------------+-------------+
            |                                |                                  |
            | WebSockets                     | WebSockets                       | WebSockets
            +----------------+---------------+----------------------------------+
                             |
                             v
               +---------------------------+
               |  Orchestrator Hub (PC)    |
               |  - Snapdragon X Elite     |
               |  - ONNX local SLM         |
               +---------------------------+
```

1.  **TinyML Anomaly Detection:** An Arduino processing vibration, temperature, and current outputs local classification states.
2.  **Mobile Inspection:** A Snapdragon mobile device runs local object detection (YOLOv8) to classify physical damage and Automatic Speech Recognition (ASR) to capture vocal operator inputs.
3.  **Agent Orchestration:** All edge agents stream structured textual conclusions to the Snapdragon AI PC.
4.  **Multi-Agent Reasoning:** A local Small Language Model (SLM) running on the Snapdragon X Elite NPU aggregates the inputs and generates failure analyses and corrective recommendations.
5.  **Cloud Matching:** Historical industrial failure signatures are queried from a remote Qualcomm Cloud AI 100 backend.

### Strengths
*   **Maximum Qualcomm Ecosystem Alignment:** Integrates mobile NPUs, PC NPUs, and cloud AI accelerators.
*   **High Innovation Score:** Showcases collaborative edge AI reasoning and multi-modal sensory aggregation on Qualcomm hardware.

### Weaknesses
*   **Fragile Critical Path:** The local SLM is the central point of failure. If the NPU compiler blocks model execution, CPU fallbacks will be too slow for an interactive demo.
*   **High Software Friction:** Requires simultaneous setup of three distinct model compilers and runtimes (TinyML on MCU, YOLO/ASR on Mobile NPU, and SLM on PC NPU).

### Technical Analysis
*   **Model Complexity:** High. Quantized SLM inference, Mobile YOLOv8, Whisper ASR, and Edge Impulse TinyML classifiers running concurrently.
*   **Tooling Dependencies:** High reliance on specific SDK versions of QAIRT, ONNX Runtime QNN Execution Provider, and mobile NPU runtimes.

### Feasibility
*   **Low (45% Completion Probability):** The integration overhead of multiple hardware compilers and heterogeneous models exceeds standard 24-hour limits.

### Risks
*   **Compiler Obstacles:** Model quantization and conversion steps often fail due to unsupported layers, requiring extensive manual restructuring.
*   **NPU Resource Exhaustion:** Running local LLMs and concurrent video streams on mobile/PC hardware may hit thermal throttling or memory limitations.

---

## Side-by-Side Comparison

| Feature | Idea 1: HemaGrid AI | Idea 2: SynapseX |
| :--- | :--- | :--- |
| **Primary Domain** | Connected Healthcare Logistics | Industrial IoT & Collaborative Edge AI |
| **System Architecture** | Client-Server / Hub-and-Spoke | Multi-Agent Collaborative Network |
| **Primary AI Tasks** | Face landmarks, Tabular demand forecast | TinyML classification, Object detection, ASR, SLM |
| **Complexity Level** | Moderate | High / Extreme |
| **Development Path** | Highly parallelizable | Highly sequential and interdependent |
| **Visual Element** | Physical box manipulation, Donor scanner | Dashboard telemetry graphs, Text output console |
| **Fail-Safe Robustness**| High (Software mocks take 5 minutes) | Low (SLM failure freezes entire workflow) |

---

## Hardware Comparison

| Hardware Component | Idea 1: HemaGrid AI | Idea 2: SynapseX | Availability / Setup Difficulty |
| :--- | :--- | :--- | :--- |
| **MCU Board** | Arduino UNO (Standard) | Arduino UNO Q | Standard boards are plug-and-play. TinyML boards require compilation tools. |
| **Sensors** | DHT22 (Temp), ADXL345 (Accel) | Accelerometer, Temp, Current sensor | Standard sensors are cheap and easy to calibrate. |
| **Mobile Hardware** | Any iOS / Android Device | Snapdragon Mobile Reference / NPU Phone | HemaGrid can run on any phone. SynapseX depends on specific mobile NPU driver access. |
| **Host PC** | Snapdragon X Elite Laptop | Snapdragon X Elite Laptop | Both use the same PC. HemaGrid code runs on standard runtimes; SynapseX requires exact QNN SDKs. |
| **Cloud/Accelerator**| Serverless DB (Firebase/AWS) | Qualcomm Cloud AI 100 | Firebase is instant. Cloud AI 100 is highly restricted and difficult to configure in 24 hours. |

---

## Software Comparison

| Software Stack | Idea 1: HemaGrid AI | Idea 2: SynapseX | Integration Risk |
| :--- | :--- | :--- | :--- |
| **Edge Vision SDK** | MediaPipe (Local) | YOLOv8 (On-Device Mobile) | YOLOv8 on mobile NPU requires complex compilation; MediaPipe is pre-packaged. |
| **Audio/Voice Processing**| None | Whisper / Local ASR | Audio processing adds threading and latency bottlenecks. |
| **Orchestrator Runtime**| Node.js / Python Hub | Local SLM (ONNX Runtime / QNN) | SLM integration with QNN Execution Provider is highly sensitive to version changes. |
| **Edge ML Library** | Simple ML (ONNX Runtime CPU/NPU) | TinyML (Edge Impulse / TF Lite Micro) | TinyML requires physical dataset recording and model training. |
| **Protocol Layer** | WebSockets (Standard JSON) | WebSockets (Custom state-sharing) | Standard schemas are highly resilient. |

---

## Demo Comparison

*   **HemaGrid AI Demo Strength:** Highly interactive, tangible, and easy for non-technical judges to understand within 3 minutes.
*   **SynapseX Demo Strength:** Highly technical and showcases impressive systems engineering, but is abstract and fragile under live networking conditions.

---

## 24-Hour Execution Analysis

*   **HemaGrid AI Parallelization:** Extreme parallel potential. The MCU developer, Android developer, and Node.js/Dashboard developer can develop entirely in isolation against a shared WebSocket contract.
*   **SynapseX Parallelization:** Low. The system is highly sequential. Dashboard logic relies on the output of the local SLM, which depends on the inputs of the mobile YOLO and MCU TinyML classification streams.

---

## Risk Matrix

| Risk Event | Probability (HemaGrid) | Probability (SynapseX) | Severity | Impact on Demo |
| :--- | :---: | :---: | :--- | :--- |
| **NPU Driver / Toolchain Mismatch** | Low (15%) | **High (85%)** | Critical | Prevents model compilation; fallbacks cause lag. |
| **Hardware Component Failure** | Low (20%) | Moderate (50%) | High | Renders specific agent data inputs blank. |
| **Network Interruption** | Moderate (25%) | Moderate (40%) | Moderate | Blocks multi-device synchronization. |
| **Model Inaccuracy / Output Drift** | Low (10%) | High (50%) | High | Causes the SLM to output hallucinations or wrong classifications. |
| **Time-to-Integration Exhaustion** | Low (15%) | **High (70%)** | Critical | Prevents running a complete end-to-end demo. |

---

## Scoring Table

Scores are out of 10, indicating potential performance under strict 24-hour constraints.

| Metric | Idea 1: HemaGrid AI | Idea 2: SynapseX | Scoring Rationale |
| :--- | :---: | :---: | :--- |
| **Innovation** | 7.5 | **9.5** | SynapseX is an advanced architecture concept. |
| **Execution Feasibility** | **9.5** | 4.0 | HemaGrid uses standard APIs and clear separation. |
| **Technical Depth** | 7.0 | **9.0** | SynapseX utilizes multi-device heterogeneous runtimes. |
| **Snapdragon Ecosystem** | 7.5 | **9.5** | SynapseX integrates mobile, PC, and cloud NPU layers. |
| **AI System Polish** | **8.5** | 5.0 | HemaGrid models are lightweight and compile reliably. |
| **Demo Interaction Quality** | **9.0** | 6.0 | Physical sensory manipulation is highly engaging. |
| **Real-World Impact** | **9.5** | 7.5 | Medical cold chains have clear, direct human impact. |
| **Implementation Simplicity** | **8.5** | 3.0 | High score denotes lower development friction. |
| **Scalability & Maintenance** | **8.0** | 6.0 | Clean client-server models are easier to scale. |
| **Overall Hackathon Readiness**| **9.5** | 4.5 | HemaGrid is highly optimized for 24-hour delivery. |
| **TOTAL SCORE** | **84.5** | **64.0** | **HemaGrid AI presents a stronger execution path.** |

---

## Final Decision

### Selected Project: **HemaGrid AI: Smarter, Safer Blood Supply for India**

---

## Why We Selected This Project

Our decision is guided by strict engineering pragmatism:

1.  **Compilation Safety:** Compiling an SLM and a mobile computer vision pipeline on Snapdragon hardware via the QAIRT SDK in 24 hours introduces high compiler toolchain risk. HemaGrid AI uses lightweight models with CPU fallbacks, insulating the team from NPU compilation blockers.
2.  **High Interactive Value:** Live software demos are highly effective when they include physical components. HemaGrid's sensor-based cold-box setup allows immediate, tactile interactions that demonstrate system value in seconds.
3.  **Low Integration Overhead:** HemaGrid separates tasks cleanly. Development tasks can run in parallel without blocking, whereas SynapseX requires a fully integrated chain of edge classifications to evaluate the central SLM.
4.  **Societal Impact:** Medical cold chain security and fraud prevention are highly relatable, compelling stories that appeal to both technical and business judges.

---

## Action Items

```text
snapdragon-hackathon-planning/
├── docs/
│   └── project-selection-analysis.md (This Document)
├── src/
│   ├── hardware/
│   │   └── arduino_sensor_node/      [Arduino Temp & Shock Telemetry]
│   ├── mobile/
│   │   └── donor_face_verify/        [Android MediaPipe Face Mesh]
│   ├── backend/
│   │   └── hospital_hub_server/      [WebSocket Hub & Demand Prediction]
│   └── frontend/
│       └── coordination_dashboard/   [Real-time Dashboard & Alerts]
```

1.  **Interface Definition (Hours 0–2):** Define JSON payload schemas for WebSocket telemetry and registration events.
2.  **Parallel Scaffolding (Hours 2–8):**
    *   Setup the WebSocket Server and standard SQLite schemas.
    *   Construct the MediaPipe Face Mesh module on Android.
    *   Write the basic sensor polling loop on the Arduino.
3.  **Model Quantization & Verification (Hours 8–12):** Convert the tabular demand forecasting model to ONNX. Verify inference on the target Snapdragon platform.
4.  **Hardware Mocking & Integration (Hours 12–16):** Assemble the physical box and verify sensor threshold alerts.
5.  **Dashboard Integration & UI Polish (Hours 16–20):** Style the central dashboard with premium HSL-tailored charts, alert animations, and glassmorphism styling.
6.  **Dry Runs & Fallback Validation (Hours 20–24):** Run end-to-end scenario validations. Confirm manual overrides and simulation fallbacks work correctly.

---

## Conclusion

HemaGrid AI provides a robust balance of Qualcomm ecosystem integration, clear societal impact, and low execution risk. By selecting HemaGrid AI, the team avoids dangerous compiler paths and toolchain dependencies, focusing energy on building a polished, interactive product that runs reliably on target hardware.
