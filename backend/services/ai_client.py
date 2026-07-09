"""
ai_client.py
HemaGrid AI - AI Engine Service Client

Sends feature vectors to the AI Engine module to fetch demand predictions.
"""

import httpx

AI_ENGINE_URL = "http://127.0.0.1:8001/api/v1/predict/demand"

async def fetch_demand_prediction(
    hospital_id: int,
    hospital_type: str,
    blood_type: str,
    temperature_c: float,
    dengue_cases_weekly: int,
    day_of_week: int,
    month: int
) -> dict:
    """
    Submits structured parameters to the AI Engine forecasting service.
    """
    payload = {
        "hospital_id": hospital_id,
        "hospital_type": hospital_type,
        "blood_type": blood_type,
        "temperature_c": temperature_c,
        "dengue_cases_weekly": dengue_cases_weekly,
        "day_of_week": day_of_week,
        "month": month
    }
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.post(AI_ENGINE_URL, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": f"AI Engine returned status code: {response.status_code}"}
        except httpx.RequestError as e:
            return {"status": "error", "message": f"Connection to AI Engine failed: {str(e)}"}
