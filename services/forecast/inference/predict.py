"""ONNX inference for blood-demand forecasting.

Loads models/model.onnx and runs it through ONNX Runtime. On Snapdragon it
targets the Hexagon NPU via the QNN Execution Provider; everywhere else it
falls back to CPU. Because skl2onnx exported the ColumnTransformer as one graph
with a named input per column, we feed one tensor per feature (float32 for
numerics, string for categoricals).

Run:  python inference/predict.py    # runs a demo prediction
"""
from __future__ import annotations

import csv
import logging
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import onnxruntime as ort
import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.preprocess import ALL_FEATURES, CATEGORICAL_FEATURES, NUMERICAL_FEATURES  # noqa: E402

logger = logging.getLogger("hemagrid.predict")

PREPROCESSOR_PATH = PROJECT_ROOT / "models" / "preprocessor.pkl"
ONNX_MODEL_PATH = PROJECT_ROOT / "models" / "model.onnx"
FEATURE_IMPORTANCE_PATH = PROJECT_ROOT / "models" / "feature_importance.csv"
SAFETY_FACTOR = 1.5  # recommended inventory = demand * safety factor


class DemandPredictor:
    """Wraps an ONNX Runtime session; picks NPU when available, CPU otherwise."""

    def __init__(self, model_path: Path = ONNX_MODEL_PATH, preprocessor_path: Path = PREPROCESSOR_PATH):
        if not model_path.exists():
            raise FileNotFoundError(
                f"No ONNX model at {model_path}. Run training/train.py then "
                f"onnx/convert_to_onnx.py first."
            )
        if not preprocessor_path.exists():
            raise FileNotFoundError(
                f"No preprocessor found at {preprocessor_path}. Run training/train.py first."
            )
        self.session, self.provider = self._make_session(model_path)
        logger.info("ONNX session ready on provider: %s", self.provider)
        logger.info("Loading preprocessor from %s", preprocessor_path)
        self.preprocessor = joblib.load(preprocessor_path)
        self._top_features = self._load_top_features()

    @staticmethod
    def _make_session(model_path: Path):
        # Prefer QNN (Hexagon NPU) with balanced power; fall back to CPU.
        available = ort.get_available_providers()
        if "QNNExecutionProvider" in available:
            try:
                sess = ort.InferenceSession(
                    str(model_path),
                    providers=["QNNExecutionProvider", "CPUExecutionProvider"],
                    provider_options=[
                        {"backend_path": "QnnHtp.dll", "htp_performance_mode": "balanced"},
                        {},
                    ],
                )
                return sess, sess.get_providers()[0]
            except Exception as exc:  # noqa: BLE001
                logger.warning("QNN EP init failed (%s); using CPU.", exc)
        sess = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
        return sess, sess.get_providers()[0]

    def npu_active(self) -> bool:
        """True only if the Hexagon NPU is really in the provider chain.

        Uses get_ep_devices() when present — get_available_providers() does NOT
        reliably list QNN on ORT 2.x, so it must not be trusted here.
        """
        if "QNN" not in self.provider:
            return False
        get_devices = getattr(ort, "get_ep_devices", None)
        if get_devices is None:
            return True  # provider is QNN and we can't introspect further
        return any("QNN" in str(getattr(d, "ep_name", d)) for d in get_devices())

    def predict_units(self, features: dict) -> float:
        # Convert dictionary to DataFrame and filter/order features properly
        df = pd.DataFrame([features])
        df = df[ALL_FEATURES]
        
        # Transform categorical and numerical features
        processed = self.preprocessor.transform(df).astype(np.float32)
        
        # Run ONNX session with the float32 feature tensor
        outputs = self.session.run(None, {"input": processed})
        return max(0.0, float(np.ravel(outputs[0])[0]))

    def _load_top_features(self, n: int = 3) -> list[str]:
        if not FEATURE_IMPORTANCE_PATH.exists():
            return []
        with open(FEATURE_IMPORTANCE_PATH) as f:
            rows = list(csv.DictReader(f))
        return [r["feature_name"] for r in rows[:n]]

    def predict(self, features: dict) -> dict:
        """Full forecast: demand + inventory intelligence + XAI contributors."""
        demand = round(self.predict_units(features))
        recommended = round(demand * SAFETY_FACTOR)
        current = float(features.get("current_inventory", 0))
        ratio = (current / demand) if demand > 0 else float("inf")

        if ratio >= 1.3:
            alert = "SAFE"
        elif ratio >= 1.0:
            alert = "WARNING"
        else:
            alert = "CRITICAL"
        health = int(max(0, min(100, round(ratio * 65))))  # ratio 1.3 ≈ ~85

        return {
            "expected_demand_units": demand,
            "recommended_inventory": recommended,
            "inventory_health_score": health,
            "alert_level": alert,
            "top_contributors": self._top_features,
        }


_PREDICTOR: Optional[DemandPredictor] = None


def get_predictor() -> DemandPredictor:
    """Lazy singleton so the model loads once per process."""
    global _PREDICTOR
    if _PREDICTOR is None:
        _PREDICTOR = DemandPredictor()
    return _PREDICTOR


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    demo = {
        "hospital_id": 1, "hospital_type": "Trauma", "city_region": "Urban",
        "blood_type": "O+", "season": "Monsoon", "temperature_c": 31.4, "rainfall_mm": 112,
        "dengue_cases_weekly": 52, "road_accidents": 21, "emergency_cases": 13,
        "scheduled_surgeries": 9, "holiday": 0, "blood_donation_camp": 1,
        "current_inventory": 80, "day_of_week": 2, "month": 7,
    }
    p = get_predictor()
    print("NPU active:", p.npu_active(), "| provider:", p.provider)
    print(p.predict(demo))
