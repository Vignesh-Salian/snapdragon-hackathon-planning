"""
predict.py
HemaGrid AI - Demand Forecasting Inference API

Loads the compiled ONNX model (or scikit-learn pickle fallback),
runs real-time prediction queries, and calculates corresponding risk flags
and inventory targets.
"""

import os
import pickle
import numpy as np
import pandas as pd
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, status

# ONNX Runtime
try:
    import onnxruntime as ort
    HAS_ONNX_RUNTIME = True
except ImportError:
    HAS_ONNX_RUNTIME = False

app = FastAPI(
    title="HemaGrid AI - Demand Forecasting Service",
    version="1.0.0",
    description="Predictive analytics and inventory alert engine."
)

# Global variables to store model session and encoders
session = None
preprocessor = None
pickle_model = None

# Model paths
current_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(current_dir, "..", "models")
onnx_path = os.path.join(models_dir, "demand_predictor.onnx")
preprocessor_path = os.path.join(models_dir, "preprocessor.pkl")
pickle_path = os.path.join(models_dir, "demand_predictor.pkl")

# Pydantic schema for inputs
class PredictionRequest(BaseModel):
    hospital_id: int
    hospital_type: str        # "General", "Trauma", "Clinic"
    blood_type: str           # "A_POS", "A_NEG", "B_POS", "B_NEG", "AB_POS", "AB_NEG", "O_POS", "O_NEG"
    temperature_c: float
    dengue_cases_weekly: int
    day_of_week: int          # 1 to 7
    month: int                # 1 to 12

@app.on_event("startup")
def load_models():
    global session, preprocessor, pickle_model
    
    # 1. Load Preprocessor mapping details
    if os.path.exists(preprocessor_path):
        with open(preprocessor_path, "rb") as f:
            preprocessor = pickle.load(f)
            
    # 2. Load Model weights
    if HAS_ONNX_RUNTIME and os.path.exists(onnx_path):
        print(f"Loading ONNX Model from: {onnx_path}")
        session = ort.InferenceSession(onnx_path)
    elif os.path.exists(pickle_path):
        print(f"Loading scikit-learn Pickle Model from: {pickle_path}")
        with open(pickle_path, "rb") as f:
            pickle_model = pickle.load(f)
    else:
        print("Warning: No model files found. Run train.py first to compile models.")

@app.get("/health")
def health_check():
    has_onnx = "ONNX" if session else ("Pickle" if pickle_model else "None")
    return {
        "status": "healthy",
        "loaded_model": has_onnx,
        "engine": "ONNXRuntime" if session else "scikit-learn"
    }

@app.post("/api/v1/predict/demand")
def predict_demand(request: PredictionRequest):
    global session, preprocessor, pickle_model

    # Ensure models are loaded
    if not session and not pickle_model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Predictive models are not loaded. Train the models first."
        )

    # 1. Pipeline execution using standard scikit-learn Pickle Model
    if pickle_model:
        input_df = pd.DataFrame([request.dict()])
        try:
            prediction = pickle_model.predict(input_df)[0]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Inference error: {str(e)}"
            )
            
    # 2. Pipeline execution using NPU-friendly ONNX model
    else:
        if not preprocessor:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Mapping encoder (preprocessor.pkl) is missing. Cannot encode inputs for ONNX."
            )
            
        # Transform input record to dataframe
        input_df = pd.DataFrame([request.dict()])
        
        try:
            # Transform categorical features to one-hot floats
            encoded_input = preprocessor.transform(input_df)
            if hasattr(encoded_input, "toarray"):
                encoded_input = encoded_input.toarray()
            
            # Format inputs for ONNX session
            input_name = session.get_inputs()[0].name
            # input shape must match: [1, num_features]
            input_data = encoded_input.astype(np.float32)
            
            # Run inference
            raw_pred = session.run(None, {input_name: input_data})
            prediction = float(raw_pred[0][0])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ONNX Inference Failure: {str(e)}"
            )

    # Post-process outputs
    predicted_units = max(1.0, round(prediction, 1))
    
    # Calculate inventory recommendation (baseline safety buffer = predicted + 30%)
    recommended_inventory = int(np.ceil(predicted_units * 1.3))

    # Determine alert level
    # If expected demand is extremely high relative to normal (e.g., > 20 units)
    alert_level = "SAFE"
    if predicted_units >= 25.0:
        alert_level = "CRITICAL"
    elif predicted_units >= 15.0:
        alert_level = "WARNING"

    return {
        "status": "success",
        "predictions": {
            "expected_demand_units": predicted_units,
            "recommended_min_inventory": recommended_inventory,
            "alert_level": alert_level
        }
    }
