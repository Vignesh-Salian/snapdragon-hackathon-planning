# Cold Box — IoT Edge Node (Arduino UNO Q)

A smart blood cold box that watches **two hazards** — heat and mechanical shock —
and streams telemetry to the gateway. Buzzer sounds on breach; knob sets the safe
threshold live.

## Kit (QWIIC/I²C daisy chain — no breadboard, no soldering)
- **UNO Q (4GB)** — Dragonwing QRB2210 MPU (Debian) + STM32U585 MCU
- **Modulino Thermo** (temp/humidity), **Buzzer** (alarm), **Knob** (threshold)
- **Modulino Movement** *(optional, ~$15)* — 6-axis IMU for shock/impact
- USB-C **Power Delivery** required to boot. Wiring: [`schematics/connections.md`](schematics/connections.md).

## Behavior
- SAFE ≤ 6 °C · WARNING ≤ 8 °C · COMPROMISED > 8 °C **or** shock ≥ 2 g (buzzer).
- `shock_g` is **optional** — no Movement module ⇒ null, safety on temperature alone.
- Posts `POST /api/v1/telemetry/report` to the gateway over Wi-Fi.

## Run
```bash
# on the UNO Q (Arduino App Lab, Python on the MPU):
python my_app/python/main.py

# no hardware — simulator drives the whole pipeline:
HEMAGRID_SIMULATE=1 BACKEND_URL=http://<gateway-lan-ip>:8002 \
  python my_app/python/main.py

pytest   # cold-box state logic (thermal + shock)
```
> On real hardware set `BACKEND_URL` to the laptop's **LAN IP**, never 127.0.0.1.

See [`../../project.md`](../../project.md) for the full architecture.
