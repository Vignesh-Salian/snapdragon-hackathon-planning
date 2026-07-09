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
9. [Cost Comparison](#cost-comparison)
10. [Hardware Availability Analysis](#hardware-availability-analysis)
11. [Engineering Cost](#engineering-cost)
12. [Time Cost](#time-cost)
13. [Resource Dependency Analysis](#resource-dependency-analysis)
14. [Cost-to-Impact Analysis](#cost-to-impact-analysis)
15. [Demo Comparison](#demo-comparison)
16. [24-Hour Execution Analysis](#24-hour-execution-analysis)
17. [Risk Matrix](#risk-matrix)
18. [Scoring Table](#scoring-table)
19. [Final Decision](#final-decision)
20. [Why We Selected This Project](#why-we-selected-this-project)
21. [Action Items](#action-items)
22. [Conclusion](#conclusion)

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

## Cost Comparison

Prototyping cost estimates directly impact development readiness and scalability.

| Cost Category | Idea 1: HemaGrid AI | Idea 2: SynapseX | Analysis & Rationale |
| :--- | :--- | :--- | :--- |
| **Hardware Cost** | Low (~$50) | Moderate (~$150) | HemaGrid uses standard components; SynapseX requires higher-end controllers. |
| **Sensor Cost** | Low (~$15) | Moderate (~$60) | High-G accelerometers and AC current transformers are expensive. |
| **Arduino Components** | Arduino Uno or Clone ($15) | Arduino Uno Q ($35+) | Idea 2 requires a higher-spec MCU for TinyML execution. |
| **Additional Electronics**| Enclosure cooler box, wiring ($20) | Mounting structures, industrial wiring ($40) | HemaGrid relies on simple consumer-grade containers. |
| **Networking** | Standard WiFi hotspot ($0) | Custom multi-device router network ($20)| SynapseX requires stable multi-agent data backbones. |
| **Cloud Cost** | Firebase Free Tier ($0) | Cloud AI 100 testing/emulation ($0-$50)| SynapseX cloud signature search carries setup/API costs. |
| **Software Cost** | Open-source libraries ($0) | Open-source libraries ($0) | Both utilize open-source frameworks. |
| **Development Tooling** | Standard IDEs (Free) | Edge Impulse & QAIRT SDK (Free) | No direct tool licensing costs are required for either. |
| **Hidden Engineering Cost**| Low (Standard debugging, simple APIs) | **Extreme** (NPU compilation, layer errors) | Lost developer hours resolving compiler bugs on SynapseX. |
| **Debugging Cost** | Low (WebSocket console logs) | High (Multi-agent tracing & logging) | Resolving distributed state synchronization is difficult. |
| **Maintenance Cost** | Low (Stateless operations) | High (Continuous drift calibration) | SynapseX models require frequent tuning and retraining. |
| **Total Estimated Cost** | **~$85** | **~$300 - $350** | **HemaGrid AI is a highly cost-efficient prototype.** |

---

## Hardware Availability Analysis

Prototyping speed in a 24-hour hackathon is bound by hardware logistics.

*   **Availability of Required Sensors:** The DHT22 (temperature) and ADXL345 (accelerometer) used in HemaGrid AI are standard items in basic sensor kits. SynapseX requires industrial-grade vibration (piezoelectric/high-G accelerometer) and AC current transformers, which are rarely available in general hackathon hardware pools.
*   **Availability of Arduino Components:** HemaGrid runs on any basic Arduino Uno or compatible board. SynapseX requires the newer Arduino Uno Q (or equivalent ARM Cortex-M4/M85 MCU) to support Edge Impulse/TinyML runtimes, which are harder to acquire on short notice.
*   **Dependency on Snapdragon Devices:** HemaGrid has a low dependency profile. Its face verification app runs on any Android or iOS device, and the demand forecasting model can execute on standard CPU runtimes if necessary. SynapseX is deeply dependent on specific Snapdragon mobile references and Snapdragon X Elite NPUs to run its on-device YOLOv8 and local SLM at acceptable latencies.
*   **Availability of Backup Hardware:** Since HemaGrid's components are highly generic, they can be replaced immediately from peer kits or local hardware stores if damaged. If SynapseX's specific MCU or industrial sensor fails, finding a replacement during the 24-hour event is highly improbable.
*   **Ease of Replacing Failed Hardware:** Replacing standard temperature sensors takes seconds. Calibrating and mapping new current or high-G vibration sensors takes hours, which is unacceptable during a live sprint.
*   **Setup Complexity:** HemaGrid requires simple breadboard wiring and standard library imports. SynapseX requires building TinyML training rigs to capture vibration/current data, creating massive setup friction.

> [!NOTE]
> **Hackathon Assembly Advantage:** HemaGrid AI is significantly easier to physically assemble and program under tight deadlines. The hardware setup can be completed in under 3 hours, leaving the team with ample time to focus on software integration and user interface.

---

## Engineering Cost

Engineering time is the most constrained resource in a 24-hour hackathon. The table below compares the estimated engineering resource allocation.

| Dimension | Idea 1: HemaGrid AI | Idea 2: SynapseX | Analysis & Comparison |
| :--- | :--- | :--- | :--- |
| **Person-Hours Required** | ~36 Person-Hours | ~75 Person-Hours | SynapseX requires more than double the engineering capacity, exceeding a 3-person team limit. |
| **Team Workload** | Balanced (Clean modular split) | Overloaded (Heavy focus on compilation & NPU binding) | HemaGrid allows parallelized frontend, backend, and hardware paths. |
| **Parallel Development**| High (Modular boundaries) | Low-Medium (Sequential dependencies on model outputs) | SynapseX developers will block each other waiting for model integrations. |
| **Integration Effort** | Low (Standard JSON schemas) | High (Multi-agent payload orchestration, text-to-SLM prompts)| Structuring and testing multi-agent telemetry is highly error-prone. |
| **Testing Effort** | Low (Sensor data simulation scripts) | High (Physical engine testing, voice command scenarios) | Testing a physical engine anomaly requires simulating physical defects. |
| **Debugging Effort** | Low (Local consoles, standard logs) | Extreme (Chained NPU runtimes, memory leaks, latency checks) | Tracking issues across MCU, Mobile, AI PC, and Cloud is extremely difficult. |
| **Opportunity Cost** | Low (Quick wins allow focus on UI/demo) | High (All time spent debugging compilers, neglecting demo polish)| SynapseX leaves no time for branding, pitching, or UX. |

---

## Time Cost

Time breakdown estimates for a 4-person team (Totaling 96 active hours of engineering capacity):

```text
HemaGrid AI:
[||||||||] Hardware Setup (8 hrs)
[||||||||||||||||] AI & Logic Models (16 hrs)
[||||||||||||] Integration (12 hrs)
[||||||] Debugging (6 hrs)
[||||||||||] Demo Preparation & UI Polish (10 hrs)
Buffer: 44 hrs (Shared across tasks / Sleep / Presentation rehearsal)

SynapseX:
[||||||||||||||||] Hardware Setup & Calibration (16 hrs)
[||||||||||||||||||||||||||||||||] AI & Model Compilation (32 hrs)
[||||||||||||||||||||] Integration & Prompting (20 hrs)
[||||||||||||||||] Debugging & Quantization (16 hrs)
[||||||||] Demo Prep & UI (8 hrs)
Buffer: 4 hrs (Critically narrow window, zero room for error)
```

*   **Buffer Analysis:** HemaGrid AI leaves a substantial time buffer, allowing the team to refine the dashboard's design, practice the pitch, and build solid fallback mocks. SynapseX consumes almost all engineering bandwidth, leaving the team with zero buffer if any of the hardware or compiler integrations stall.

---

## Resource Dependency Analysis

Analyzing dependencies highlights potential external blockers that can stall development.

| Dependency Type | HemaGrid AI Rating | SynapseX Rating | Key Differences |
| :--- | :---: | :---: | :--- |
| **Hardware Dependency** | Low | **High** | SynapseX depends on specific MCUs, sensors, and Snapdragon platforms. |
| **Software Dependency** | Low | **High** | SynapseX requires Edge Impulse SDK, Whisper, and YOLO. |
| **SDK Dependency** | Low | **High** | SynapseX depends on QAIRT SDK and ONNX Runtime QNN Execution Provider. |
| **Qualcomm Tooling** | Medium | **High** | HemaGrid can run on CPU if needed; SynapseX depends on Hexagon NPUs. |
| **Internet Dependency** | Medium | Low | HemaGrid uses cloud syncing; SynapseX relies mostly on edge computing. |
| **Cloud Dependency** | Medium | Medium | HemaGrid syncs regional data; SynapseX queries historical signature DBs. |
| **External API Dependency**| Low | Low | Both keep processing local to the system nodes where possible. |

---

## Cost-to-Impact Analysis

Maximizing return on engineering effort (ROEE) is critical for winning a hackathon.

*   **Total Estimated Prototype Cost:** HemaGrid AI (~$85) vs. SynapseX (~$300-$350).
*   **Engineering Effort:** HemaGrid AI (~36 person-hours) vs. SynapseX (~75 person-hours).
*   **Expected Demo Quality:** HemaGrid AI will showcase a high-fidelity, polished, responsive frontend with a physical interactive trigger. SynapseX will likely result in a console-based terminal interface with high execution latency.
*   **Expected Judge Impact:** HemaGrid AI scores high on immediate comprehensibility and social utility. SynapseX scores high on systems engineering depth, but only if the entire chain works flawlessly—a gamble that rarely pays off in a 24-hour sprint.
*   **Return on Engineering Effort (ROEE):**
    *   *HemaGrid AI:* High ROEE. With low hardware cost and moderate engineering effort, the team delivers a highly visual, emotionally resonant, working medical supply prototype.
    *   *SynapseX:* Low-Medium ROEE. Despite high hardware cost and extreme engineering effort, the resulting demo is highly abstract and carries a 60% chance of failing completely during presentation.

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

Our decision is guided by strict engineering pragmatism and a multi-dimensional analysis:

1.  **Technical Feasibility & Execution Probability:** HemaGrid AI features a modular, parallelizable architecture. By avoiding complex multi-agent synchronization and deep dependencies on experimental NPU compilers, we achieve a **90%+ chance of completing a fully functional prototype** in 24 hours.
2.  **Innovation & Snapdragon Ecosystem Alignment:** While SynapseX has higher conceptual novelty, HemaGrid AI provides a robust, end-to-end demonstration of Snapdragon technology. It integrates a Snapdragon AI PC as an on-site intelligence hub running local demand forecasting models, proving the value of edge-based hospital coordination.
3.  **Demo Quality & Interactive Value:** Live demos are won by tangible, physical proof of concept. Shaking a physical cooler box to trigger real-time sensor alerts on a beautiful dashboard is a reliable, high-impact demonstration. SynapseX is highly abstract and vulnerable to high inference latency or complete system freezing.
4.  **Cost Efficiency & Hardware Availability:** HemaGrid's sensor stack (DHT22, ADXL345) and standard microcontrollers cost ~$85 and are highly available with abundant backup units. SynapseX requires expensive, specialized hardware (~$300+) that is difficult to replace or recalibrate quickly.
5.  **Engineering & Time Cost:** HemaGrid AI requires ~36 person-hours to build, leaving a comfortable time buffer for team coordination and presentation preparation. SynapseX requires ~75 person-hours, consuming all buffer and leaving zero margin for integration issues.
6.  **Risk vs. Reward:** SynapseX carries a high risk of NPU driver mismatches and compiler errors (85% probability) which can render the core demo non-functional. HemaGrid AI mitigates this risk through a graceful CPU/ONNX fallback, ensuring we deliver a polished, stable, and winning demo.

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
