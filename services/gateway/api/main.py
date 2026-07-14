"""HemaGrid Core Backend Hub (FastAPI).

Central orchestrator: owns inventory + telemetry + the /ws/live stream, and
proxies donor/prediction calls to the isolated microservices. Runs fully
standalone — every owned route works with zero external services up; only the
`*-delegate` proxies need Vignesh's (:8000) / Tejas's (:8001) modules, and they
degrade to 503 when those are down.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Body, Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.models import BloodInventory, SessionLocal, TelemetryLog, init_db
from services.proxy import forward
from websocket_hub.manager import manager


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()  # create tables + seed demo inventory (idempotent)
    yield


app = FastAPI(title="HemaGrid Core Backend Hub", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- schemas ----------
class InventoryUpdate(BaseModel):
    hospital_id: str
    blood_type: str
    units_added_removed: int = Field(..., description="signed delta; result may not go below 0")


class Telemetry(BaseModel):
    temperature: float | None = None
    humidity: float | None = None
    shock_g: float | None = None


class TelemetryReport(BaseModel):
    device_id: str
    uptime_ms: int | None = None
    telemetry: Telemetry = Telemetry()
    status: str = "SAFE"


# ---------- health ----------
@app.get("/health")
def health():
    return {"status": "ok", "service": "hemagrid-backend", "ws_clients": manager.count}


# ---------- inventory ----------
@app.get("/api/v1/inventory/{hospital_id}")
def get_inventory(hospital_id: str, db: Session = Depends(get_db)):
    rows = db.query(BloodInventory).filter_by(hospital_id=hospital_id).all()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No inventory for hospital '{hospital_id}'")
    return {"hospital_id": hospital_id, "inventory": [r.as_dict() for r in rows]}


@app.post("/api/v1/inventory/update")
async def update_inventory(body: InventoryUpdate):
    with SessionLocal() as db:
        row = (
            db.query(BloodInventory)
            .filter_by(hospital_id=body.hospital_id, blood_type=body.blood_type)
            .one_or_none()
        )
        current = row.units if row else 0
        new_units = current + body.units_added_removed
        if new_units < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Stock cannot go negative ({current} + {body.units_added_removed})",
            )
        if row is None:
            row = BloodInventory(
                hospital_id=body.hospital_id, blood_type=body.blood_type, units=new_units
            )
            db.add(row)
        else:
            row.units = new_units
        db.commit()
        payload = row.as_dict()
    await manager.broadcast({"type": "inventory", **payload})
    return payload


# ---------- telemetry ----------
@app.post("/api/v1/telemetry/report")
async def report_telemetry(report: TelemetryReport):
    if report.status not in ("SAFE", "WARNING", "COMPROMISED"):
        raise HTTPException(status_code=422, detail="status must be SAFE|WARNING|COMPROMISED")
    with SessionLocal() as db:
        log = TelemetryLog(
            device_id=report.device_id,
            uptime_ms=report.uptime_ms,
            temperature=report.telemetry.temperature,
            humidity=report.telemetry.humidity,
            shock_g=report.telemetry.shock_g,
            status=report.status,
        )
        db.add(log)
        db.commit()
    await manager.broadcast(
        {
            "type": "telemetry",
            "device_id": report.device_id,
            "uptime_ms": report.uptime_ms,
            "telemetry": report.telemetry.model_dump(),
            "status": report.status,
        }
    )
    return {"ok": True, "broadcast_to": manager.count}


# ---------- live stream ----------
@app.websocket("/ws/live")
async def ws_live(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # keepalive; dashboard is read-mostly
    except WebSocketDisconnect:
        manager.disconnect(ws)


# ---------- delegate proxies (graceful 503 if upstream down) ----------
@app.post("/api/v1/donor/enroll-delegate")
async def enroll_delegate(payload: dict = Body(...)):
    return await forward("donor/enroll", payload)


@app.post("/api/v1/donor/verify-delegate")
async def verify_delegate(payload: dict = Body(...)):
    return await forward("donor/verify", payload)


@app.post("/api/v1/predict/demand-delegate")
async def demand_delegate(payload: dict = Body(...)):
    return await forward("predict/demand", payload)
