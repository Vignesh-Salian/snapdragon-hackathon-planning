"""Prediction routes for the AI engine (POST /api/v1/predict/demand)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from inference.predict import get_predictor

router = APIRouter(prefix="/api/v1", tags=["predict"])


class DemandRequest(BaseModel):
    hospital_id: int
    hospital_type: str
    city_region: str
    blood_type: str
    season: str  # Summer | Monsoon | Winter — required categorical model feature
    temperature_c: float
    rainfall_mm: float
    dengue_cases_weekly: float
    road_accidents: float
    emergency_cases: float
    scheduled_surgeries: float
    holiday: int
    blood_donation_camp: int
    current_inventory: float
    day_of_week: int
    month: int


@router.post("/predict/demand")
def predict_demand(req: DemandRequest):
    try:
        prediction = get_predictor().predict(req.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"status": "success", "prediction": prediction}
