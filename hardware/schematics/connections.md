# Smart Cold Box — Connections

## Provided kit (use ONLY these)
- **Arduino UNO Q (4GB)** — Dragonwing QRB2210 MPU (Debian) + STM32U585 MCU
- **Modulino Thermo** — temperature + humidity (I²C)
- **Modulino Buzzer** — piezo alarm (I²C)
- **Modulino Knob** — rotary encoder + button (I²C), sets the safe-temp threshold

> No accelerometer is in this kit → `shock_g` is reported as `null`. Safety
> state is driven by **temperature** (the real cold-chain metric).

## Wiring — QWIIC daisy chain (no breadboard, no soldering)
All three Modulinos are I²C. Chain them with QWIIC cables; order doesn't matter:

```
UNO Q  QWIIC ── Modulino Thermo ── Modulino Knob ── Modulino Buzzer
        (SDA/SCL/3V3/GND carried through every QWIIC connector)
```

Each Modulino has a fixed I²C address, so the daisy chain needs no config.

## Power
- **USB-C Power Delivery required** — the UNO Q will not boot without a PD source.

## Thresholds (tunable)
| State | Condition | Indication |
|---|---|---|
| SAFE | temp ≤ `SAFE_MAX_C` (default 6 °C) | buzzer silent |
| WARNING | `SAFE_MAX_C` < temp ≤ +2 °C | buzzer silent |
| COMPROMISED | temp > `SAFE_MAX_C` + 2 °C | **buzzer sounds** |

The **Knob** shifts `SAFE_MAX_C` by ±5 °C live for calibration.

## Network
The MPU is on WiFi — set the backend to the laptop's **LAN IP** (not 127.0.0.1)
in App Lab's `.env`:  `BACKEND_URL=http://192.168.x.x:8002`
