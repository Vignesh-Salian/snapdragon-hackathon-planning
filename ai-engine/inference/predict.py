"""
HemaGrid AI - Inference Service
Owner: Tejas

The single entry point the FastAPI backend will call for a prediction. Loads
the trained pipeline ONCE at module import time (not per-request), then
exposes predict() as a pure function: raw feature dict in, JSON-ready dict
out - demand forecast, inventory recommendation, alert level, and a
lightweight rule-based explanation (no SHAP - this needs to stay fast enough
for a live demo and simple enough to reason about on stage).

Clean-architecture separation, matching preprocessing/preprocess.py,
training/train.py, and the onnx/ modules:

  - load_pipeline()                  -> loads pipeline.pkl (called once, at
                                         import time - see _PIPELINE below)
  - validate_input()                 -> checks the raw feature dict is complete
  - build_input_dataframe()          -> raw dict -> single-row pandas DataFrame
  - predict_demand()                 -> runs the pipeline, returns a float
  - compute_recommended_inventory()  -> predicted_demand * 1.3
  - compute_inventory_health_score() -> (current / recommended) * 100, clamped
  - determine_alert_level()          -> SAFE / WARNING / CRITICAL
  - generate_explanations()          -> rule-based "top contributing factors"
  - predict()                        -> orchestrates all of the above; this
                                         is the function FastAPI routes call

Usage (future FastAPI route):
    from inference.predict import predict
    result = predict(raw_features_dict)
"""

import logging
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline

# Make `preprocessing` importable regardless of the caller's cwd.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.preprocess import ALL_FEATURES  # noqa: E402

# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("hemagrid.predict")

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

MODELS_DIR = PROJECT_ROOT / "models"
PIPELINE_PATH = MODELS_DIR / "pipeline.pkl"

# Reserved for inventory logic - required in the input dict, but never fed
# to the model (see preprocessing.preprocess.NON_FEATURE_COLUMNS for why).
CURRENT_INVENTORY_KEY = "current_inventory"
REQUIRED_INPUT_KEYS = ALL_FEATURES + [CURRENT_INVENTORY_KEY]

RECOMMENDED_INVENTORY_MULTIPLIER = 1.3  # recommended = predicted demand * 1.3

MAX_EXPLANATION_FACTORS = 5


# --------------------------------------------------------------------------
# Model loading (once, at import time)
# --------------------------------------------------------------------------

def load_pipeline(path: Path = PIPELINE_PATH) -> Pipeline:
    """Load the fitted pipeline saved by training/train.py.

    Args:
        path: Path to the pipeline.pkl file.

    Returns:
        The fitted sklearn Pipeline (preprocessing + model).

    Raises:
        FileNotFoundError: If no pipeline has been trained/saved yet.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"No trained pipeline found at {path}. Run training/train.py first."
        )
    logger.info("Loading pipeline from %s", path)
    pipeline = joblib.load(path)
    logger.info("Pipeline loaded: steps=%s", [name for name, _ in pipeline.steps])
    return pipeline


# Loaded exactly once when this module is first imported - Python's own
# module cache guarantees re-imports elsewhere in the process reuse this
# same object rather than reloading from disk. FastAPI routes should
# `from inference.predict import predict` rather than re-instantiating
# anything here.
_PIPELINE: Pipeline = load_pipeline()


# --------------------------------------------------------------------------
# Input validation & construction
# --------------------------------------------------------------------------

def validate_input(raw_features: Dict[str, Any]) -> None:
    """Verify the raw feature dict has every key the pipeline and inventory
    logic need before doing any work.

    Args:
        raw_features: Raw hospital feature values, keyed by column name
            (must include every column in ALL_FEATURES plus
            "current_inventory").

    Raises:
        ValueError: If any required key is missing.
    """
    missing_keys = [key for key in REQUIRED_INPUT_KEYS if key not in raw_features]
    if missing_keys:
        raise ValueError(f"Missing required input fields: {missing_keys}")


def build_input_dataframe(raw_features: Dict[str, Any]) -> pd.DataFrame:
    """Convert a raw feature dict into the single-row DataFrame the pipeline
    expects, in the exact column order the ColumnTransformer was fit with.

    Args:
        raw_features: Validated raw hospital feature values. May contain
            extra keys (e.g. "current_inventory") - only ALL_FEATURES
            columns are extracted here.

    Returns:
        A one-row pandas DataFrame with columns == ALL_FEATURES.
    """
    row = {col: raw_features[col] for col in ALL_FEATURES}
    return pd.DataFrame([row], columns=ALL_FEATURES)


# --------------------------------------------------------------------------
# Prediction
# --------------------------------------------------------------------------

def predict_demand(input_df: pd.DataFrame) -> float:
    """Run the loaded pipeline on a single-row input DataFrame.

    Args:
        input_df: Output of build_input_dataframe().

    Returns:
        The predicted expected_demand_units as a float.

    Raises:
        RuntimeError: If the pipeline fails to produce a prediction.
    """
    try:
        prediction = _PIPELINE.predict(input_df)
    except Exception as exc:
        raise RuntimeError(f"Pipeline prediction failed: {exc}") from exc
    return float(prediction[0])


# --------------------------------------------------------------------------
# Inventory logic
# --------------------------------------------------------------------------

def compute_recommended_inventory(predicted_demand: float) -> float:
    """Recommended Inventory = Predicted Demand * 1.3 (a 30% safety buffer
    over expected same-day demand).

    Args:
        predicted_demand: Output of predict_demand().

    Returns:
        The recommended inventory level.
    """
    return predicted_demand * RECOMMENDED_INVENTORY_MULTIPLIER


def compute_inventory_health_score(
    current_inventory: float, recommended_inventory: float
) -> float:
    """Inventory Health Score = (current_inventory / recommended_inventory) * 100,
    clamped to [0, 100].

    Args:
        current_inventory: The hospital's current on-hand stock.
        recommended_inventory: Output of compute_recommended_inventory().

    Returns:
        A score in [0, 100]. If recommended_inventory is 0 (i.e. predicted
        demand is 0), any non-negative stock is treated as a full 100 -
        there is nothing to be short of.
    """
    if recommended_inventory <= 0:
        return 100.0 if current_inventory >= 0 else 0.0

    score = (current_inventory / recommended_inventory) * 100
    return max(0.0, min(100.0, score))


def determine_alert_level(current_inventory: float, predicted_demand: float) -> str:
    """Classify inventory status against predicted demand.

    - SAFE:     current_inventory >= 130% of predicted_demand
    - WARNING:  current_inventory is between 100% and 130% of predicted_demand
    - CRITICAL: current_inventory is below predicted_demand

    Args:
        current_inventory: The hospital's current on-hand stock.
        predicted_demand: Output of predict_demand().

    Returns:
        One of "SAFE", "WARNING", "CRITICAL".
    """
    if predicted_demand <= 0:
        # No meaningful demand predicted - nothing to be short of.
        return "SAFE"

    safe_threshold = predicted_demand * RECOMMENDED_INVENTORY_MULTIPLIER

    if current_inventory >= safe_threshold:
        return "SAFE"
    if current_inventory >= predicted_demand:
        return "WARNING"
    return "CRITICAL"


# --------------------------------------------------------------------------
# Explainability (rule-based, no SHAP)
# --------------------------------------------------------------------------

# Each rule: (condition over the raw feature dict, human-readable explanation).
# Deliberately simple threshold checks rather than SHAP - this needs to run
# in microseconds on a live demo and be easy for a judge to verify by eye
# against the input values, not a black-box attribution.
EXPLANATION_RULES: List[Tuple[Callable[[Dict[str, Any]], bool], str]] = [
    (lambda f: f.get("emergency_cases", 0) > 20, "High emergency admissions"),
    (lambda f: f.get("rainfall_mm", 0) > 100, "Heavy rainfall"),
    (lambda f: f.get("hospital_type") == "Trauma", "Trauma hospital baseline demand"),
    (lambda f: f.get("season") == "Monsoon", "Seasonal disease trend"),
    (lambda f: f.get("road_accidents", 0) > 15, "High road accident frequency"),
    (lambda f: f.get("dengue_cases_weekly", 0) > 15, "Elevated dengue case load"),
    (lambda f: f.get("scheduled_surgeries", 0) > 6, "High scheduled surgery volume"),
    (lambda f: f.get("holiday") == 1, "Holiday - reduced elective activity"),
]


def generate_explanations(raw_features: Dict[str, Any]) -> List[str]:
    """Evaluate EXPLANATION_RULES against the raw feature dict and return
    the human-readable messages for every rule that fired, in rule-priority
    order, capped at MAX_EXPLANATION_FACTORS.

    Args:
        raw_features: Raw hospital feature values (same dict passed to predict()).

    Returns:
        A list of explanation strings. If no rule fires, returns a single
        generic message rather than an empty list.
    """
    matched = [message for condition, message in EXPLANATION_RULES if condition(raw_features)]

    if not matched:
        return ["No significant risk factors detected"]

    return matched[:MAX_EXPLANATION_FACTORS]


# --------------------------------------------------------------------------
# Orchestration - the function FastAPI routes will call
# --------------------------------------------------------------------------

def predict(raw_features: Dict[str, Any]) -> Dict[str, Any]:
    """Run the full inference pipeline: validate input, predict demand,
    compute inventory recommendation/health/alert level, and generate a
    rule-based explanation.

    Args:
        raw_features: Raw hospital feature values, keyed by column name.
            Must include every column in preprocessing.preprocess.ALL_FEATURES
            plus "current_inventory".

    Returns:
        A JSON-serializable dict:
            {
                "expected_demand_units": int,
                "recommended_inventory": int,
                "inventory_health_score": int,
                "alert_level": str,
                "top_prediction_factors": List[str],
            }

    Raises:
        ValueError: If raw_features is missing required keys.
        RuntimeError: If the underlying pipeline prediction fails.
    """
    validate_input(raw_features)

    input_df = build_input_dataframe(raw_features)
    predicted_demand = predict_demand(input_df)

    recommended_inventory = compute_recommended_inventory(predicted_demand)
    current_inventory = float(raw_features[CURRENT_INVENTORY_KEY])
    health_score = compute_inventory_health_score(current_inventory, recommended_inventory)
    alert_level = determine_alert_level(current_inventory, predicted_demand)
    top_prediction_factors = generate_explanations(raw_features)

    logger.info(
        "Prediction: demand=%.2f recommended_inventory=%.2f health_score=%.1f alert=%s",
        predicted_demand, recommended_inventory, health_score, alert_level,
    )

    return {
        "expected_demand_units": round(predicted_demand),
        "recommended_inventory": round(recommended_inventory),
        "inventory_health_score": round(health_score),
        "alert_level": alert_level,
        "top_prediction_factors": top_prediction_factors,
    }


# --------------------------------------------------------------------------
# Standalone smoke test
# --------------------------------------------------------------------------

if __name__ == "__main__":
    sample_input = {
        "hospital_id": 3,
        "hospital_type": "Trauma",
        "city_region": "Urban",
        "blood_type": "O+",
        "day_of_week": 5,
        "month": 7,
        "season": "Monsoon",
        "temperature_c": 28.5,
        "rainfall_mm": 145.0,
        "dengue_cases_weekly": 18,
        "road_accidents": 17,
        "emergency_cases": 25,
        "scheduled_surgeries": 4,
        "holiday": 0,
        "blood_donation_camp": 1,
        "current_inventory": 60,
    }

    result = predict(sample_input)
    print("\nSample prediction:")
    for key, value in result.items():
        print(f"  {key}: {value}")