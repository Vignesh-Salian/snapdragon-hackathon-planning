"""Self-checks for the AI engine.

The prediction test is skipped until the ONNX model is built (train + convert),
so the suite is green on a fresh checkout and meaningful once the model exists.

Run:  cd ai-engine && pytest
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.preprocess import ALL_FEATURES  # noqa: E402

DEMO = {
    "hospital_id": 1, "hospital_type": "Trauma", "city_region": "Urban",
    "blood_type": "O+", "season": "Monsoon", "temperature_c": 31.4, "rainfall_mm": 112,
    "dengue_cases_weekly": 52, "road_accidents": 21, "emergency_cases": 13,
    "scheduled_surgeries": 9, "holiday": 0, "blood_donation_camp": 1,
    "current_inventory": 80, "day_of_week": 2, "month": 7,
}

MODEL_EXISTS = (PROJECT_ROOT / "models" / "model.onnx").exists()


def test_request_covers_all_15_features():
    # The API request must carry exactly the 15 model features (+ current_inventory).
    assert set(ALL_FEATURES).issubset(DEMO.keys())
    assert len(ALL_FEATURES) == 15


@pytest.mark.skipif(not MODEL_EXISTS, reason="model.onnx not built yet")
def test_prediction_shape_and_alert():
    from inference.predict import get_predictor

    out = get_predictor().predict(DEMO)
    assert out["expected_demand_units"] >= 0
    assert out["alert_level"] in ("SAFE", "WARNING", "CRITICAL")
    assert out["recommended_inventory"] >= out["expected_demand_units"]
