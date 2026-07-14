"""Generic async proxy to the isolated microservices (face :8000, AI :8001).

One forwarder covers all three delegate routes — the only difference between
them is the target URL, so there is no reason for separate client classes.
Upstream being down returns a clean 503, never a 500 crash, so the hub stays
demoable while Vignesh's / Tejas's services aren't running yet.
"""
from __future__ import annotations

import os

import httpx
from fastapi import HTTPException

FACE_BASE = os.getenv("FACE_URL", "http://127.0.0.1:8000")
AI_BASE = os.getenv("AI_URL", "http://127.0.0.1:8001")

# delegate route -> (base url, upstream path)
ROUTES = {
    "donor/enroll": (FACE_BASE, "/api/v1/donor/enroll"),
    "donor/verify": (FACE_BASE, "/api/v1/donor/verify"),
    "predict/demand": (AI_BASE, "/api/v1/predict/demand"),
}


async def forward(route: str, payload: dict, timeout: float = 5.0) -> dict:
    base, path = ROUTES[route]
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(base + path, json=payload)
    except httpx.RequestError as exc:
        # service not up / unreachable — degrade gracefully
        raise HTTPException(
            status_code=503,
            detail=f"Upstream '{route}' unavailable at {base}: {exc.__class__.__name__}",
        )
    if resp.status_code >= 400:
        # Pass the upstream's STRUCTURED error through (e.g. the face service's
        # duplicate-donor 409 body {duplicate_detected, matched_donor, ...}).
        # Stringifying it here would double-encode + truncate it and break the
        # dashboard's fraud modal.
        try:
            body = resp.json()
            detail = body.get("detail", body) if isinstance(body, dict) else body
        except ValueError:
            detail = resp.text[:500]
        raise HTTPException(status_code=resp.status_code, detail=detail)
    return resp.json()
