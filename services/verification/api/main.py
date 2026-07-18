"""HemaGrid Donor Verification service (FastAPI, port 8000).

/enroll and /verify decode a base64 face image, extract landmarks, and check it
against donors enrolled inside the 56-day lockout window. A match below the
Euclidean threshold is a duplicate donor → HTTP 409.

Run:  python api/main.py    (or)   uvicorn api.main:app --port 8000
"""
from __future__ import annotations

import base64
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database import db  # noqa: E402
from models.detector import NoFaceError, distance, extract_landmarks  # noqa: E402

# Euclidean distance below this = same donor.
# NOTE: 0.15 is calibrated for the deterministic FALLBACK embedding (identical→0,
# different→~1.41). When you swap in the real MobileFaceNet model, its embedding
# distances live on a different scale — RECALIBRATE this on a few real face pairs
# (same-person vs different-person) or dedup will break (all/none match).
DUPLICATE_THRESHOLD = 0.80


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="HemaGrid Donor Verification", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class EnrollRequest(BaseModel):
    name: str
    image_b64: str


class VerifyRequest(BaseModel):
    image_b64: str


def _landmarks_from_b64(image_b64: str):
    try:
        raw = base64.b64decode(image_b64, validate=True)
    except Exception:
        raise HTTPException(status_code=400, detail="image_b64 is not valid base64")
    try:
        return extract_landmarks(raw)
    except NoFaceError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


def _closest_donor(vec):
    """Return (donor, dist) for the nearest recent donor, or (None, inf)."""
    best, best_d = None, float("inf")
    for donor in db.recent_donors():
        d = distance(vec, donor["landmarks"])
        if d < best_d:
            best, best_d = donor, d
    return best, best_d


def _duplicate_payload(donor: dict, dist: float) -> dict:
    return {
        "duplicate_detected": True,
        "confidence": round(max(0.0, 1.0 - dist), 4),
        "matched_donor": {
            "id": donor["id"],
            "name": donor["name"],
            "enrolled_at": donor["enrolled_at"],
        },
        "message": f"Donor matches '{donor['name']}' within the {db.LOCKOUT_DAYS}-day lockout window.",
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "donor-verification"}


@app.post("/api/v1/donor/enroll")
def enroll(req: EnrollRequest):
    vec = _landmarks_from_b64(req.image_b64)
    donor, dist = _closest_donor(vec)
    if donor and dist < DUPLICATE_THRESHOLD:
        raise HTTPException(status_code=409, detail=_duplicate_payload(donor, dist))
    donor_id = db.add_donor(req.name, vec.tolist())
    return {"enrolled": True, "id": donor_id, "name": req.name}


@app.post("/api/v1/donor/verify")
def verify(req: VerifyRequest):
    vec = _landmarks_from_b64(req.image_b64)
    donor, dist = _closest_donor(vec)
    if donor and dist < DUPLICATE_THRESHOLD:
        raise HTTPException(status_code=409, detail=_duplicate_payload(donor, dist))
    return {"duplicate_detected": False, "message": "No matching donor in lockout window."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
