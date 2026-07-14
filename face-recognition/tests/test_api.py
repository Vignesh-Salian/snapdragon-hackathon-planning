"""Self-checks for donor verification (runs with the fallback embedding).

Run:  cd face-recognition && pytest
"""
import base64
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["DONORS_DB"] = os.path.join(tempfile.mkdtemp(), "donors.db")

from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402
from database import db  # noqa: E402

db.init_db()
client = TestClient(app)

FACE_A = base64.b64encode(b"person-A-face-image-bytes" * 8).decode()
FACE_B = base64.b64encode(b"person-B-different-face!!" * 8).decode()


def test_enroll_new_donor():
    r = client.post("/api/v1/donor/enroll", json={"name": "Asha", "image_b64": FACE_A})
    assert r.status_code == 200
    assert r.json()["enrolled"] is True


def test_duplicate_enroll_is_409():
    client.post("/api/v1/donor/enroll", json={"name": "Ravi", "image_b64": FACE_B})
    # same face again → duplicate donor
    r = client.post("/api/v1/donor/enroll", json={"name": "Ravi again", "image_b64": FACE_B})
    assert r.status_code == 409
    assert r.json()["detail"]["duplicate_detected"] is True


def test_verify_known_face_is_409():
    r = client.post("/api/v1/donor/verify", json={"image_b64": FACE_A})
    assert r.status_code == 409


def test_verify_unknown_face_ok():
    novel = base64.b64encode(b"totally-unseen-face-xyz!!" * 8).decode()
    r = client.post("/api/v1/donor/verify", json={"image_b64": novel})
    assert r.status_code == 200
    assert r.json()["duplicate_detected"] is False


def test_no_face_is_400():
    r = client.post("/api/v1/donor/verify", json={"image_b64": base64.b64encode(b"x").decode()})
    assert r.status_code == 400
