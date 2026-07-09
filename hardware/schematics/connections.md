# Smart Cold Box Circuit Connections

This document details the physical pin connections and wiring schematics for the HemaGrid AI Smart Cold Box telemetry unit.

---

## 📍 Pin Connection Summary

| Device Pin | Arduino UNO Pin | Description | Required Pull-up / Resistor |
| :--- | :--- | :--- | :--- |
| **DHT22 Pin 1 (VDD)** | 5V | Power Supply (3.3V - 5V) | None |
| **DHT22 Pin 2 (DATA)**| Pin 2 | Bidirectional 1-wire | 10kΩ pull-up resistor to 5V |
| **DHT22 Pin 4 (GND)** | GND | Ground | None |
| **ADXL345 Pin 1 (VCC)**| 3.3V / 5V | Power Supply (I2C Module VCC) | None |
| **ADXL345 Pin 2 (GND)**| GND | Ground | None |
| **ADXL345 Pin 3 (SCL)**| Pin A5 / SCL | I2C Clock (Serial Clock) | None (Module contains internal pull-ups) |
| **ADXL345 Pin 4 (SDA)**| Pin A4 / SDA | I2C Data (Serial Data) | None (Module contains internal pull-ups) |
| **LED Green (Anode)** | Pin 8 | SAFE indicator | 220Ω resistor in series to ground |
| **LED Yellow (Anode)**| Pin 9 | WARNING indicator | 220Ω resistor in series to ground |
| **LED Red (Anode)**   | Pin 10 | COMPROMISED indicator | 220Ω resistor in series to ground |
| **Active Buzzer (+)** | Pin 11 | Audible breach alert | None (directly driven 5V piezo) |

*Note: DHT22 Pin 3 is unused/No Connection (NC).*

---

## 📐 Detailed Wiring Schematic

```text
                  +-----------------------------------+
                  |           ARDUINO UNO             |
                  |                                   |
                  |     5V  GND  A5   A4   D11 D10 D9  D8  D2
                  +------+---+----+----+---+---+---+---+---+
                         |   |    |    |   |   |   |   |   |
     +---------+         |   |    |    |   |   |   |   |   |
     |  DHT22  |         |   |    |    |   |   |   |   |   |
     |         |         |   |    |    |   |   |   |   |   |
     | 1. VDD  <---------+   |    |    |   |   |   |   |   |
     | 2. DATA <=============|====|====|===|===|===|===|===+
     | 3. NC   |             |    |    |   |   |   |   |
     | 4. GND  <-------------+    |    |   |   |   |   |
     +---------+ (Pull-up R) |    |    |   |   |   |   |
        [10k Ohm Resistor]   |    |    |   |   |   |   |
          DATA to VDD        |    |    |   |   |   |   |
                             |    |    |   |   |   |   |
     +---------+             |    |    |   |   |   |   |
     | ADXL345 |             |    |    |   |   |   |   |
     |         |             |    |    |   |   |   |   |
     | 1. VCC  <-------------+    |    |   |   |   |   |
     | 2. GND  <-------------+    |    |   |   |   |   |
     | 3. SCL  <------------------+    |   |   |   |   |
     | 4. SDA  <-----------------------+   |   |   |   |
     +---------+                           |   |   |   |
                                           |   |   |   |
     +---------+                           |   |   |   |
     | BUZZER  |                           |   |   |   |
     |  (+)    <---------------------------+   |   |   |
     |  (-)    <-------------+                 |   |   |
     +---------+             |                 |   |   |
                             |                 |   |   |
     +---------+             |                 |   |   |
     | LED RED |             |                 |   |   |
     | (Anode) <=============|=================+   |   |
     | (Cathode)<--[220 Ohm]-+                     |   |
     +---------+                                   |   |
                                                   |   |
     +---------+                                   |   |
     | LED YEL |                                   |   |
     | (Anode) <===================================+   |
     | (Cathode)<--[220 Ohm]-+                         |
     +---------+             |                         |
                             |                         |
     +---------+             |                         |
     | LED GRN |             |                         |
     | (Anode) <=============|=========================+
     | (Cathode)<--[220 Ohm]-+
     +---------+
```

---

## ⚠️ Assembly & Wiring Rules

1.  **Resistors:** Always place resistors in series with LEDs (220Ω is ideal to limit current draw to ~15mA per pin). Running LEDs directly from GPIO pins will damage the Arduino microcontroller.
2.  **I2C Pullups:** The ADXL345 breakout boards generally contain onboard 4.7kΩ pull-up resistors on SDA and SCL lines. If you are using raw sensors, you must add external 4.7kΩ pull-up resistors to the 3.3V rail.
3.  **Sensor Enclosure Isolation:** The DHT22 and ADXL345 sensors should be physically isolated inside the cooler compartment while the Arduino MCU is placed in a separate, sealed external housing to protect the electronics from humidity and condensation.
