"""Smart Cold Box — MPU daemon (Arduino UNO Q, Qualcomm Dragonwing QRB2210).

Provided kit only: Uno Q 4GB + Modulino Thermo (temp/humidity) + Modulino Buzzer
+ Modulino Knob. There is NO accelerometer in this kit, so `shock_g` is left
null — the safety state is driven by temperature (the real cold-chain metric).
The Knob adjusts the safe-temperature threshold live; the Buzzer sounds on a
COMPROMISED reading.

Runs on the UNO Q using the `modulino` Python library over QWIIC/I2C. On any
machine without that hardware (or with HEMAGRID_SIMULATE=1) it falls back to a
built-in simulator so the sensor→backend→dashboard pipeline is fully demoable.

Run on the box:   python main.py
Run the sim:      HEMAGRID_SIMULATE=1 python main.py
"""
from __future__ import annotations

import json
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
POLL_SECONDS = float(os.getenv("POLL_SECONDS", "1.0"))

try:
    from modulino import ModulinoBuzzer, ModulinoKnob, ModulinoThermo  # type: ignore

    HARDWARE = True
except Exception:  # noqa: BLE001 — any import/bus error means no hardware here
    HARDWARE = False

SIMULATE = os.getenv("HEMAGRID_SIMULATE") == "1" or not HARDWARE


def evaluate_status(temperature: float, safe_max: float) -> str:
    """Cold-chain safety state from temperature and the (knob-set) threshold."""
    if temperature <= safe_max:
        return "SAFE"
    if temperature <= safe_max + WARN_MARGIN_C:
        return "WARNING"
    return "COMPROMISED"


def build_payload(device_id: str, uptime_ms: int, temperature: float,
                  humidity: float, status: str) -> dict:
    return {
        "device_id": device_id,
        "uptime_ms": uptime_ms,
        "telemetry": {
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "shock_g": None,  # no accelerometer in the provided Modulino kit
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

    def read():
        # Knob nudges the threshold ±5°C around SAFE_MAX_C for live calibration.
        safe_max = SAFE_MAX_C + (knob.value % 100 - 50) / 10.0
        return float(thermo.temperature), float(thermo.humidity), safe_max, buzzer

    return read


def _sim_reader():
    state = {"temp": 4.0}

    def read():
        # random walk with an occasional breach so the demo shows all states
        state["temp"] += random.uniform(-0.4, 0.5)
        if random.random() < 0.05:
            state["temp"] += random.uniform(2.0, 5.0)  # door-open breach
        state["temp"] = max(1.0, min(14.0, state["temp"]))
        humidity = 40 + random.uniform(-5, 5)
        return state["temp"], humidity, SAFE_MAX_C, None

    return read


def run() -> None:
    reader = _sim_reader() if SIMULATE else _hardware_reader()
    mode = "SIMULATE" if SIMULATE else "HARDWARE (Modulino)"
    print(f"[coldbox] {DEVICE_ID} starting in {mode} → {BACKEND_URL}")
    start = time.monotonic()
    while True:
        temperature, humidity, safe_max, buzzer = reader()
        status = evaluate_status(temperature, safe_max)
        if buzzer is not None:  # real hardware: sound the alarm on breach
            buzzer.tone(880 if status == "COMPROMISED" else 0)
        uptime_ms = int((time.monotonic() - start) * 1000)
        payload = build_payload(DEVICE_ID, uptime_ms, temperature, humidity, status)
        ok = post_telemetry(payload)
        print(f"[coldbox] {status:11s} {temperature:5.1f}°C  sent={ok}")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    run()
