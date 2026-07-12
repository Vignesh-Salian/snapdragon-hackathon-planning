# Module Owner Assignment: Smart Cold Box (Hardware Team)

*   **Module Owner:** Hardware Team
*   **Module Name:** Smart Cold Box IoT Node

---

## 1. Module Overview

*   **Purpose:** Develop a dual-brain edge application on the Arduino UNO Q to monitor blood shipment temperature and shock levels, evaluate safety states, and stream telemetry.
*   **Scope:** Zephyr-based STM32U585 MCU C++ sketch (sensing and control), Qualcomm Dragonwing QRB2210 MPU Python daemon (logging, analytics, networking), and Bridge RPC libraries.
*   **Success Criteria:** Non-blocking 1 Hz sensor polling on MCU, real-time Bridge RPC RPC functions exposed to Linux, stable direct-to-backend WebSockets via MPU WiFi, and zero serial lockups.

---

## 2. Responsibilities

The Hardware Team is responsible for wiring the DHT22 and ADXL345 to the Arduino UNO Q headers, writing the MCU Zephyr sketch, establishing the MPU Python environment inside Arduino App Lab, registering Bridge RPC functions, and configuring MPU-controlled status LEDs.

---

## 3. Repository Ownership

*   **Folder Scope:** `/hardware`
*   **Files Owned:**
    *   `hardware/my_app/app.yaml` (App Lab layout config)
    *   `hardware/my_app/sketch/sketch.ino` (MCU Zephyr sketch code)
    *   `hardware/my_app/sketch/sketch.yaml` (MCU compile configuration)
    *   `hardware/my_app/python/main.py` (MPU Python execution daemon)
    *   `hardware/my_app/python/requirements.txt` (MPU package dependencies)
    *   `hardware/schematics/connections.md` (Pins mapping and schematics)
    *   `hardware/tests/mock_serial_reader.py` (Local COM testing helper)

---

## 4. Functional Requirements

### Feature 1 — MCU Telemetry Acquisition
*   *Task:* Program the STM32U585 MCU to poll DHT22 (temperature/humidity) and ADXL345 (I2C accelerometer) at 1 Hz using Zephyr non-blocking timers.
*   *Task:* Expose readings as service functions using the Arduino Bridge RPC library (`Bridge.begin()`, `Bridge.provide()`).

### Feature 2 — MPU State Evaluation & Networking
*   *Task:* Write a Python daemon (`main.py`) running on the QRB2210 MPU that queries the MCU via the Bridge RPC client.
*   *Task:* Implement safety threshold rules in Python. Trigger local status updates.
*   *Task:* Establish direct WiFi connection to the backend and stream telemetry frames using standard WebSockets.

### Feature 3 — Dual-Processor Indicators
*   *Task:* Program the MCU to drive status LEDs #3 & #4 and the buzzer based on calculated state.
*   *Task:* Program the MPU to drive user LEDs #1 & #2 on the Linux filesystem (`/sys/class/leds/`) to display warning indicators.

---

## 5. Technical Responsibilities

### Bridge RPC API Exposed (MCU to MPU)
*   `float get_temp()` -> Returns DHT22 temperature.
*   `float get_shock()` -> Returns ADXL345 max shock.
*   `void trigger_buzzer(bool active)` -> Enables/disables the active buzzer on D11.

### Telemetry Packet Format (MPU to Backend)
*   **Protocol:** WebSocket or HTTP JSON payload via WiFi.
*   **Schema:** Matches the master `IMPLEMENTATION_PLAN.md` specification.

### Hardware Details
*   **Compute Block:** MPU (Cortex-A53 @ 2.0 GHz) + MCU (Cortex-M33 @ 160 MHz).
*   **Power:** USB-C Power Delivery dongle is required; the board will not boot without PD support.
*   **Bridge Lockout:** Do not access `Serial1` on the MCU directly as it is reserved for the `arduino-router` RPC link.

---

## 6. Non-Functional Requirements

*   **Performance:** Telemetry data must be fetched and pushed to the backend within **150ms** of acquisition.
*   **Memory Constraints:** The MCU firmware must stay under `786 kB SRAM` limit.
*   **Reliability:** MPU daemon must implement auto-reconnect loops for both the Bridge RPC client and WiFi host links.

---

## 7. Deliverables

*   Arduino C++ sketch and App Lab configurations.
*   Python MPU background script.
*   Physical pinout schematics.
*   Mock testing utilities.

---

## 8. Development Milestones

*   **Hours 00–06 (Phase 1: Wiring & Inputs):** Connect sensors to UNO Q headers; verify basic reading via MCU serial console.
*   **Hours 06–12 (Phase 2: Bridge RPC Setup):** Register sensor get functions on the MCU and verify MPU-to-MCU Bridge calls.
*   **Hours 12–18 (Phase 3: MPU Logic & WiFi):** Build the threshold evaluation loop and establish WebSocket communication on MPU.
*   **Hours 18–24 (Phase 4: Calibration & Box Assembly):** Assemble the physical box compartment, verify MPU/MCU LED controls, and calibrate shock thresholds.

---

## 9. Dependencies & Module Boundaries

*   **What Depends On You:** Mithun (Core Backend consumes your telemetry JSON frames).
*   **Module Boundaries:** Do not modify code files inside `/backend`, `/dashboard`, `/ai-engine`, or `/face-recognition`.

---

## 10. Acceptance Criteria

*   Buzzer sounds and Red LED illuminates during COMPROMISED state.
*   MPU successfully connects to the backend and pushes JSON frames.
*   RPC calls operate without latency blocks or connection timeouts.

---

## 11. Integration Checklist

- [ ] Confirm USB-C Power Delivery is active.
- [ ] Verify local MPU connection to the backend WebSocket broker.
- [ ] Confirm Bridge client executes RPC functions without error logs.
