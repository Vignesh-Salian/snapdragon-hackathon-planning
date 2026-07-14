"""Self-checks for the standalone paths (no external services required).

Run:  cd backend && pytest        (or)   python tests/test_backend.py
"""
import os
import pathlib
import sys
import tempfile

# isolated temp DB + import path — must be set before importing the app
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
os.environ["HEMAGRID_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")

from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402
from database.models import init_db  # noqa: E402

init_db()  # TestClient() without a `with` block skips lifespan, so seed explicitly
client = TestClient(app)


def test_health_ok():
    assert client.get("/health").json()["status"] == "ok"


def test_seeded_inventory_has_eight_types():
    r = client.get("/api/v1/inventory/KMC-MANIPAL")
    assert r.status_code == 200
    assert len(r.json()["inventory"]) == 8


def test_unknown_hospital_404():
    assert client.get("/api/v1/inventory/NOPE").status_code == 404


def test_inventory_update_applies_delta():
    before = _units("KMC-MANIPAL", "O+")
    r = client.post(
        "/api/v1/inventory/update",
        json={"hospital_id": "KMC-MANIPAL", "blood_type": "O+", "units_added_removed": 5},
    )
    assert r.status_code == 200
    assert r.json()["units"] == before + 5


def test_inventory_never_goes_negative():
    r = client.post(
        "/api/v1/inventory/update",
        json={"hospital_id": "APOLLO-BLR", "blood_type": "AB-", "units_added_removed": -9999},
    )
    assert r.status_code == 400  # AB- seeded at 3, can't withdraw 9999


def test_telemetry_ingest_broadcasts_to_ws():
    with client.websocket_connect("/ws/live") as ws:
        r = client.post(
            "/api/v1/telemetry/report",
            json={
                "device_id": "COLDBOX-01",
                "uptime_ms": 1000,
                "telemetry": {"temperature": 9.9, "humidity": 40.0},
                "status": "WARNING",
            },
        )
        assert r.json()["ok"] is True
        msg = ws.receive_json()
        assert msg["type"] == "telemetry"
        assert msg["status"] == "WARNING"
        assert msg["telemetry"]["temperature"] == 9.9


def test_delegate_degrades_to_503_when_upstream_down():
    # nothing is running on :8001, so this must be a clean 503, not a 500 crash
    r = client.post("/api/v1/predict/demand-delegate", json={"any": "payload"})
    assert r.status_code == 503


def test_delegate_passes_structured_409_through(monkeypatch):
    """An upstream duplicate-donor 409 must reach the caller as a structured
    dict (not a stringified/truncated blob), or the dashboard fraud modal breaks.
    """
    import asyncio

    import httpx
    from fastapi import HTTPException

    import services.proxy as proxy

    dup = {"duplicate_detected": True, "confidence": 0.95,
           "matched_donor": {"id": 7, "name": "Asha", "enrolled_at": "t"},
           "message": "dup"}

    class _Resp:
        status_code = 409
        text = '{"detail": ...}'

        def json(self):
            return {"detail": dup}

    class _Client:
        def __init__(self, *a, **k): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False
        async def post(self, *a, **k): return _Resp()

    monkeypatch.setattr(httpx, "AsyncClient", _Client)
    try:
        asyncio.run(proxy.forward("donor/verify", {"image_b64": "x"}))
        assert False, "should have raised 409"
    except HTTPException as exc:
        assert exc.status_code == 409
        assert exc.detail["duplicate_detected"] is True  # dict, not a string


def _units(hospital, btype):
    inv = client.get(f"/api/v1/inventory/{hospital}").json()["inventory"]
    return next(x["units"] for x in inv if x["blood_type"] == btype)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("all self-checks passed")
