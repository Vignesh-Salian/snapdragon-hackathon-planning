# Smart Cold Box Standards & Tasks Document

This document outlines the coding standards, documentation guidelines, roadmap milestones, and active developer tasks for the Smart Cold Box module.

---

## 💻 Coding Standards

### C++ / Arduino Code Guidelines
1.  **Non-Blocking Loops:** Never use `delay()`. Use `millis()` based scheduling for all polling, buzzer, and LED logic. This guarantees responsive UART communication.
2.  **Memory Management:** Avoid dynamic memory allocations (`new`, `malloc`, `realloc`). Do not use the Arduino `String` class as it fragment memory on small MCUs. Use standard C-style strings (`char[]`) and integer/float states.
3.  **Global Constants:** Define configuration variables (`PIN_` defines, thresholds) using `#define` or `const` keywords. Keep constants in uppercase.
4.  **Static Data Types:** Structs must be used to group related state properties (e.g. telemetry metrics, status flags).
5.  **Serial Print Optimizations:** Use the `F()` macro (e.g. `Serial.print(F("string"))`) for all static print expressions to keep string literals in Flash memory rather than dynamic RAM.
6.  **I2C Communications:** Always check the return code of I2C transactions. If `accel.begin()` fails, lock execution and pulse the visual alarm.

### Code Style Example
```cpp
// Correct: Use F() macro and non-blocking timers
if (currentTime - lastPollTime >= POLLING_INTERVAL) {
    lastPollTime = currentTime;
    pollSensors();
}
```

---

## 📝 Documentation Standards

1.  **Function Documentation:** Every function must have a header comment describing its parameters, return values, and behavior.
2.  **Pin Mapping Updates:** Any changes to pins must be documented in both the main `README.md` and `schematics/connections.md`.
3.  **JSON Payload Changes:** Any modification to the JSON string keys or structure must be reflected in the schema file and the mock test suite.

---

## 📋 Developer TODO List & Issue Tracker

### Issue 1: High-Frequency Vibration False Alarm Filtering
*   **Problem:** Sudden bumps in transport trigger transient warnings that immediately register as a breach.
*   **Resolution:** Implement a moving-average filter or a debounce buffer for accelerometer magnitude spikes. A shock event must exceed the warning limit for at least 3 consecutive poll cycles to trigger a `WARNING` state.

### Issue 2: Manual Hardware Reset Button
*   **Problem:** The `COMPROMISED` state is sticky and can only be cleared by rebooting the MCU.
*   **Resolution:** Add a physical tactile push button on Pin 3 (using internal pullup) to clear sticky alarms and reset `max_impact_g` back to `0.0`.

### Issue 3: Sensor Failure Safe-State Trigger
*   **Problem:** If the temperature sensor fails or is unplugged during shipping, it continues reading `0.0` or outputs `NaN` values, which might register as SAFE.
*   **Resolution:** If `dht.readTemperature()` returns `NaN` or fails for 5 seconds, automatically default the system state to `COMPROMISED` and turn on the buzzer.

---

## 🚀 Future Improvements & Qualcomm Integrations

1.  **WebSocket / Cellular Transport Layer:** Integrate a WiFi shield (e.g. ESP8266 or Arduino UNO R4 WiFi) or cellular shield (SIM800L) to establish directly bound WebSockets without host-PC assistance.
2.  **Secure Telemetry Signing:** Add cryptographic message verification (HMAC-SHA256) using a shared secret between the Arduino and the Snapdragon PC to prevent malicious telemetry tampering in transit.
3.  **Deep Sleep Optimization:** Implement low-power watchdog timers to put the ATmega/ARM MCU into deep sleep during shipment intervals, waking up every 5 seconds to check sensors and saving up to 90% battery life.
4.  **Local Threshold Calibration:** Develop serial console command handlers so that managers can update temperature limits dynamically without re-uploading firmware.
