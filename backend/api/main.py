"""
main.py
HemaGrid AI - Core Backend Server

Central routing coordinator for inventory management, telemetry intake,
biometric checks, and WebSocket broadcasts.
"""

from datetime import datetime
from fastapi import FastAPI, Depends, UploadFile, File, Form, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.models import init_db, SessionLocal, Hospital, Inventory, ShipmentLog
from websocket_hub.manager import ConnectionManager
from services.ai_client import fetch_demand_prediction
from services.face_client import check_donor_duplicate

app = FastAPI(
    title="HemaGrid AI - Core Backend Service",
    version="1.0.0",
    description="Central coordination API hub."
)

# Enable CORS for web dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global WebSocket manager
manager = ConnectionManager()

# --- Database Session Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Startup Initializer
@app.on_event("startup")
def startup_event():
    init_db()

# --- Pydantic Schemas ---
class InventoryUpdateRequest(BaseModel):
    hospital_id: int
    blood_type: str
    units_added_removed: int

class TelemetryReport(BaseModel):
    device_id: str
    uptime_ms: int
    telemetry: dict
    status: dict

class PredictionDelegateRequest(BaseModel):
    hospital_id: int
    blood_type: str
    temperature_c: float
    dengue_cases_weekly: int
    day_of_week: int
    month: int

# --- API Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "core-backend"}

@app.get("/api/v1/inventory/{hospital_id}")
def get_hospital_inventory(hospital_id: int, db: Session = Depends(get_db)):
    """
    Retrieves stock levels for all blood types inside a specific hospital.
    """
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found."
        )
        
    stocks = db.query(Inventory).filter(Inventory.hospital_id == hospital_id).all()
    inventory_dict = {s.blood_type: s.units_available for s in stocks}
    
    return {
        "hospital_name": hospital.name,
        "hospital_type": hospital.hospital_type,
        "inventory": inventory_dict
    }

@app.post("/api/v1/inventory/update")
def update_inventory(req: InventoryUpdateRequest, db: Session = Depends(get_db)):
    """
    Updates available stock levels for a specific blood type (adds/removes units).
    """
    stock = db.query(Inventory).filter(
        Inventory.hospital_id == req.hospital_id,
        Inventory.blood_type == req.blood_type
    ).first()
    
    if not stock:
        # Create record if not exists
        stock = Inventory(
            hospital_id=req.hospital_id,
            blood_type=req.blood_type,
            units_available=0
        )
        db.add(stock)

    new_total = stock.units_available + req.units_added_removed
    if new_total < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stock Update: Available inventory cannot drop below zero."
        )

    stock.units_available = new_total
    db.commit()
    
    return {
        "status": "success",
        "hospital_id": req.hospital_id,
        "blood_type": req.blood_type,
        "updated_total": stock.units_available
    }

@app.post("/api/v1/telemetry/report")
async def report_telemetry(payload: TelemetryReport, db: Session = Depends(get_db)):
    """
    Ingests cold box telemetry streams, registers logs, and broadcasts updates via WS.
    """
    try:
        temp = float(payload.telemetry.get("temperature_c", 0.0))
        impact = float(payload.telemetry.get("max_impact_g", 0.0))
        state = payload.status.get("state", "SAFE")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed telemetry values."
        )

    # Save log to database
    log = ShipmentLog(
        device_id=payload.device_id,
        temperature=temp,
        max_impact=impact,
        state=state
    )
    db.add(log)
    db.commit()

    # Broadcast state update to active dashboards
    broadcast_payload = {
        "event_type": "TELEMETRY_UPDATE",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": {
            "device_id": payload.device_id,
            "state": state,
            "temperature_c": temp,
            "max_impact_g": impact,
            "alert_flags": payload.status.get("flags", {})
        }
    }
    await manager.broadcast(broadcast_payload)
    
    return {"status": "received", "logged_id": log.id}

@app.post("/api/v1/donor/verify-delegate")
async def verify_donor_delegate(
    image: UploadFile = File(...)
):
    """
    Acts as proxy wrapper. Uploads donor face photo to the Face Verification service,
    and broadcasts alert payloads if fraud matches are detected.
    """
    image_bytes = await image.read()
    
    # Query microservice
    result = await check_donor_duplicate(image_bytes)
    
    # Broadcast alert to dashboards if duplication detected
    if result.get("duplicate_detected") is True:
        matched_donor = result.get("matched_donor", {})
        alert_payload = {
            "event_type": "FRAUD_ALERT",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": {
                "matched_donor_name": matched_donor.get("name", "Unknown"),
                "match_confidence": result.get("confidence", 0.0),
                "location": "Donor Registration Desk"
            }
        }
        await manager.broadcast(alert_payload)

    return result

@app.post("/api/v1/predict/demand-delegate")
async def predict_demand_delegate(
    req: PredictionDelegateRequest,
    db: Session = Depends(get_db)
):
    """
    Queries hospital metadata profile locally, then forwards parameters to the
    AI Engine forecasting endpoint.
    """
    hospital = db.query(Hospital).filter(Hospital.id == req.hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found."
        )

    # Fetch prediction
    result = await fetch_demand_prediction(
        hospital_id=req.hospital_id,
        hospital_type=hospital.hospital_type,
        blood_type=req.blood_type,
        temperature_c=req.temperature_c,
        dengue_cases_weekly=req.dengue_cases_weekly,
        day_of_week=req.day_of_week,
        month=req.month
    )
    
    return result

# --- WebSockets Routing ---

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Sockets stay open. Active frames are pushed outwards.
            # We discard inputs from dashboard clients.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
