# Work Assignment: Smart Cold Box (Hardware Team)

*   **Module Owner:** Hardware Team
*   **Module Name:** Smart Cold Box IoT Node
*   **Objective:** Develop Arduino UNO Q firmware to monitor shipment temperature and shock/vibration levels, evaluate safety states, and stream structured telemetry over serial interfaces.

---

## 1. Why This Module Exists

Blood units are vulnerable to temperature excursions and mechanical shocks during transport. Monitoring these variables locally on low-power microcontrollers ensures immediate warnings can be triggered before damage is done.

---

## 2. Responsibilities & Folders Owned

*   **Repository Folder:** `/hardware`
*   **Primary Tasks:**
    *   Assemble sensors and write Arduino C++ firmware.
    *   Implement threshold rules and local state evaluation.
    *   Serialize sensor metrics as JSON strings over UART.
    *   Document hardware connections.

---

## 3. Features to Implement

1.  **Sensor Polling Loop:** Query DHT22 and ADXL345 sensors at a non-blocking 1 Hz frequency.
2.  **State Logic Engine:** Evaluate safety parameters locally (SAFE, WARNING, COMPROMISED) based on physical thresholds.
3.  **Active Alert Indicators:** Drive status LEDs and piezo alarms to represent calculated state locally.
4.  **Serial Payload Generator:** Print structured JSON payloads to the serial UART port at 115200 baud.

---

## 4. Detailed Task Checklist

- [ ] Create folder structure under `/hardware` with `firmware`, `schematics`, `docs`, and `tests`.
- [ ] Connect DHT22 and ADXL345 to Arduino UNO R4/Minima breadboard.
- [ ] Wire status indicator LEDs (Green, Yellow, Red) and active buzzer using correct resistors.
- [ ] Write non-blocking timer logic using `millis()` to poll sensors every 1 second.
- [ ] Write local threshold comparison rules for temperature and shock magnitude.
- [ ] Construct JSON serialization printer using the standard Arduino string buffers.
- [ ] Write `schematics/connections.md` detailing all wiring diagrams.
- [ ] Build a python serial listener script inside `tests/` to parse and validate JSON payloads.

---

## 5. Interface Specifications

### Telemetry Packet Output (Serial USB)
*   **Baud Rate:** `115200`
*   **Format:**
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

## 6. Coding & Documentation Standards

*   **Language & Tech:** Arduino C++, DHT22 Temperature, ADXL345 I2C Accelerometer.
*   **Coding Conventions:**
    *   Do not use `delay()` in the loop. Use `millis()` tasks.
    *   Avoid using the dynamic `String` library to prevent memory leaks on microcontrollers. Use static char arrays.
    *   Protect print strings in Flash memory using the `F()` macro helper.
*   **Documentation:** Maintain absolute pin maps and wiring diagrams within the schematics markdown file.

---

## 7. Testing Responsibilities

*   Implement test verification scripts (e.g. `mock_serial_reader.py`) to test serial outputs on local computers.
*   Conduct thermal validation (warm/cool sensors) and shock triggers (tap accelerometer) to verify state updates.

---

## 8. Weekly Milestones

*   **Week 1:** Sensors wired and reading values successfully.
*   **Week 2:** State logic and LED indicators validated.
*   **Week 3:** JSON serialization verified over serial monitor.
*   **Week 4:** Physical enclosure assembled, and telemetry validated using mock listener scripts.

---

## 9. Dependencies & Constraints

*   **Modules Depending on Your Work:** Mithun (Core Backend USB daemon reads your serial stream).
*   **Things NOT to Modify:** Do not alter directories outside `/hardware`.
*   **Baud Limit:** Ensure UART transmissions remain locked at `115200` to prevent buffer frame corruption.
