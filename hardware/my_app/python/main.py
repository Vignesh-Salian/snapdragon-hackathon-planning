"""Smart Cold Box — MPU daemon (Arduino UNO Q, Qualcomm Dragonwing QRB2210).

Kit: Uno Q 4GB + Modulino Thermo (temp/humidity) + Modulino Buzzer + Modulino
Knob, and — if fitted — Modulino Movement (6-axis IMU) for shock/impact
detection. Blood is damaged by mechanical shock as well as heat, so the box
watches BOTH hazards: a temperature breach OR a hard knock trips COMPROMISED and
sounds the buzzer. The Knob adjusts the safe-temperature threshold live.

`shock_g` is OPTIONAL: with no Movement module (or in simulation without a spike)
it degrades gracefully — the box still works on temperature alone.

Runs on the UNO Q via the `modulino` Python library over QWIIC/I2C. On any
machine without that hardware (or with HEMAGRID_SIMULATE=1) it falls back to a
built-in simulator so the sensor→backend→dashboard pipeline is fully demoable.

Run on the box:   python main.py
Run the sim:      HEMAGRID_SIMULATE=1 python main.py
"""
from __future__ import annotations

import json
import math
import os
import random
import time
import urllib.request

# Backend host: the MPU is on WiFi, so this must be the laptop's LAN IP, NOT
# 127.0.0.1. Set BACKEND_URL in the App Lab .env, e.g. http://192.168.1.20:8002
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8002")
DEVICE_ID = os.getenv("DEVICE_ID", "COLDBOX-01")
SAFE_MAX_C = float(os.getenv("SAFE_MAX_C", "6.0"))   # ≤ this = SAFE
WARN_MARGIN_C = float(os.getenv("WARN_MARGIN_C", "2.0"))  # SAFE_MAX..+margin = WARNING
SHOCK_MAX_G = float(os.getenv("SHOCK_MAX_G", "2.0"))  # impact above this = COMPROMISED
POLL_SECONDS = float(os.getenv("POLL_SECONDS", "1.0"))

try:
    from modulino import ModulinoBuzzer, ModulinoKnob, ModulinoThermo  # type: ignore

    HARDWARE = True
except Exception:  # noqa: BLE001 — any import/bus error means no hardware here
    HARDWARE = False

try:
    from modulino import ModulinoMovement  # type: ignore

    HAS_MOVEMENT = True
except Exception:  # noqa: BLE001 — accelerometer is optional
    HAS_MOVEMENT = False

SIMULATE = os.getenv("HEMAGRID_SIMULATE") == "1" or not HARDWARE


def evaluate_status(temperature: float, safe_max: float,
                    shock_g: float | None = None, shock_max: float = SHOCK_MAX_G) -> str:
    """Cold-chain safety state from temperature and (if present) impact.

    A hard knock trips COMPROMISED regardless of temperature — mechanical shock
    damages blood on its own.
    """
    if shock_g is not None and shock_g >= shock_max:
        return "COMPROMISED"
    if temperature <= safe_max:
        return "SAFE"
    if temperature <= safe_max + WARN_MARGIN_C:
        return "WARNING"
    return "COMPROMISED"


def build_payload(device_id: str, uptime_ms: int, temperature: float,
                  humidity: float, shock_g: float | None, status: str) -> dict:
    return {
        "device_id": device_id,
        "uptime_ms": uptime_ms,
        "telemetry": {
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            # None when no Movement module is fitted — schema allows null
            "shock_g": round(shock_g, 2) if shock_g is not None else None,
        },
        "status": status,
    }


def post_telemetry(payload: dict) -> bool:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{BACKEND_URL}/api/v1/telemetry/report", data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception as exc:  # noqa: BLE001 — auto-reconnect: never crash the loop
        print(f"[coldbox] backend unreachable ({exc.__class__.__name__}); will retry")
        return False


def _hardware_reader():
    thermo, buzzer, knob = ModulinoThermo(), ModulinoBuzzer(), ModulinoKnob()
    movement = ModulinoMovement() if HAS_MOVEMENT else None

    def _read_shock():
        if movement is None:
            return None
        try:
            x, y, z = movement.accelerometer  # in g
            # deviation of the acceleration magnitude from 1g gravity ≈ impact
            return abs(math.sqrt(x * x + y * y + z * z) - 1.0)
        except Exception:  # noqa: BLE001 — IMU hiccup shouldn't kill the loop
            return None

    def read():
        # Knob nudges the threshold ±5°C around SAFE_MAX_C for live calibration.
        safe_max = SAFE_MAX_C + (knob.value % 100 - 50) / 10.0
        return float(thermo.temperature), float(thermo.humidity), _read_shock(), safe_max, buzzer

    return read


def _sim_reader():
    state = {"temp": 4.0}

    def read():
        # random walk with an occasional thermal breach...
        state["temp"] += random.uniform(-0.4, 0.5)
        if random.random() < 0.05:
            state["temp"] += random.uniform(2.0, 5.0)  # door-open breach
        state["temp"] = max(1.0, min(14.0, state["temp"]))
        humidity = 40 + random.uniform(-5, 5)
        # ...and an occasional physical knock (simulated accelerometer)
        shock = random.uniform(0.0, 0.3)
        if random.random() < 0.04:
            shock = random.uniform(2.5, 4.0)  # box dropped / mishandled
        return state["temp"], humidity, shock, SAFE_MAX_C, None

    return read


def run() -> None:
    reader = _sim_reader() if SIMULATE else _hardware_reader()
    mode = "SIMULATE" if SIMULATE else f"HARDWARE (Modulino{'+Movement' if HAS_MOVEMENT else ''})"
    print(f"[coldbox] {DEVICE_ID} starting in {mode} → {BACKEND_URL}")
    start = time.monotonic()
    while True:
        temperature, humidity, shock_g, safe_max, buzzer = reader()
        status = evaluate_status(temperature, safe_max, shock_g)
        if buzzer is not None:  # real hardware: sound the alarm on breach
            buzzer.tone(880 if status == "COMPROMISED" else 0)
        uptime_ms = int((time.monotonic() - start) * 1000)
        payload = build_payload(DEVICE_ID, uptime_ms, temperature, humidity, shock_g, status)
        ok = post_telemetry(payload)
        shock_str = f"{shock_g:4.1f}g" if shock_g is not None else "  -  "
        print(f"[coldbox] {status:11s} {temperature:5.1f}°C {shock_str}  sent={ok}")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    run()
