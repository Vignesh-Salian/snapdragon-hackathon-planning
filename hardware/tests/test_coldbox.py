"""Self-check for the cold-box state logic (no hardware, no network).

Run:  cd hardware && pytest    (or)   python tests/test_coldbox.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "my_app" / "python"))

from main import build_payload, evaluate_status  # noqa: E402


def test_status_thresholds():
    assert evaluate_status(4.0, safe_max=6.0) == "SAFE"
    assert evaluate_status(6.0, safe_max=6.0) == "SAFE"
    assert evaluate_status(7.5, safe_max=6.0) == "WARNING"   # within +2°C margin
    assert evaluate_status(9.0, safe_max=6.0) == "COMPROMISED"


def test_payload_shape_matches_backend_schema():
    p = build_payload("COLDBOX-01", 1234, 4.5, 45.0, "SAFE")
    assert set(p) == {"device_id", "uptime_ms", "telemetry", "status"}
    assert set(p["telemetry"]) == {"temperature", "humidity", "shock_g"}
    assert p["telemetry"]["shock_g"] is None  # no accelerometer in the kit


if __name__ == "__main__":
    test_status_thresholds()
    test_payload_shape_matches_backend_schema()
    print("cold-box self-checks passed")
