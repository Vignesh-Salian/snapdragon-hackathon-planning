# Module Owner Assignment: Smart Cold Box (Hardware Team)

*   **Module Owner:** Hardware Team
*   **Module Name:** Smart Cold Box IoT Node

---

## 1. Module Overview

*   **Purpose:** Develop Arduino UNO Q firmware to monitor shipment temperature and shock/vibration levels, evaluate safety states, and stream structured telemetry over serial interfaces.
*   **Scope:** Arduino C++ firmware, DHT22 sensor integration, ADXL345 accelerometer integration, status indicators (LEDs/buzzer), and serial serialization.
*   **Success Criteria:** Non-blocking 1 Hz sensor polling loops, state updates matching thresholds, and stable JSON frames outputted at 115200 baud.

---

## 2. Responsibilities

The Hardware Team is responsible for wiring the sensors and indicators, writing non-blocking polling loops, implementing threshold rules, generating structured JSON payloads, and documenting circuit connections.

---

## 3. Repository Ownership

*   **Folder Scope:** `/hardware`
*   **Files Owned:**
    *   `hardware/firmware/smart_cold_box/smart_cold_box.ino`
    *   `hardware/schematics/connections.md`
    *   `hardware/tests/mock_serial_reader.py`
    *   `hardware/docs/standards_and_milestones.md`

---

## 4. Functional Requirements

### Feature 1: Sensor Polling Loop
*   *Task:* Query DHT22 and ADXL345 sensors at a non-blocking 1 Hz frequency using `millis()`.

### Feature 2: Threshold Engine
*   *Task:* Compare metrics locally to classify state (SAFE, WARNING, COMPROMISED).
*   *Task:* Drive status LEDs and piezo alarms to represent state changes.

### Feature 3: Serial Payload Generator
*   *Task:* Format and stream telemetry data as structured JSON strings over serial UART.

---

## 5. Technical Responsibilities

### Telemetry Packet Output (Serial USB)
*   **Baud Rate:** `115200`
*   **Payload Format:**
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

## 6. Non-Functional Requirements

*   **Performance:** Telemetry data must be evaluated and outputted within **100ms** of a threshold violation.
*   **Reliability:** Strict non-blocking architecture; zero dynamic memory allocations (`malloc` or `String` library).
*   **Safety:** Flash string optimization using the `F()` macro to keep dynamic RAM utilization low.

---

## 7. Deliverables

*   Arduino C++ firmware source file.
*   Physical circuit schematics document.
*   Python serial validation utility.
*   Standards and guidelines document.

---

## 8. Development Milestones

*   **Week 1:** Sensors wired and value reading validated.
*   **Week 2:** State logic and indicator LEDs validated.
*   **Week 3:** JSON serialization verified over serial interfaces.
*   **Week 4:** Physical enclosure built; serial telemetry validation complete.

---

## 9. Dependencies & Module Boundaries

*   **What Depends On You:** Mithun (Core Backend USB daemon reads your serial stream).
*   **Module Boundaries:** Do not modify code files inside `/backend`, `/dashboard`, `/ai-engine`, or `/face-recognition`.

---

## 10. Acceptance Criteria

*   Buzzer pulses and red LED illuminates during COMPROMISED state.
*   JSON outputs match the validation schema.
*   Firmware memory footprint is $<60\%$ dynamic RAM.

---

## 11. Integration Checklist

- [ ] Confirm UART baud rate is locked at `115200`.
- [ ] Verify sensors read correct temperature values in test compartments.
- [ ] Confirm python serial test script validates payloads without JSON syntax errors.
