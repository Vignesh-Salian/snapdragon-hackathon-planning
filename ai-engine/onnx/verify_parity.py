"""
HemaGrid AI - ONNX Parity Verification
Owner: Tejas

Confirms that ONNX Runtime produces (near-)identical predictions to the
original sklearn Pipeline, and measures ONNX inference latency - the two
acceptance criteria that actually matter before this model is trusted to
run on the Snapdragon Hexagon NPU: correctness (max diff < 0.01) and speed.

Clean-architecture separation, matching preprocessing/preprocess.py and
training/train.py:

  - load_artifacts()        -> loads pipeline.pkl + model.onnx + test data
  - build_onnx_inputs()     -> converts a pandas sample into the named,
                                per-column tensors ONNX Runtime expects
  - run_predictions()        -> runs both sklearn and ONNX Runtime inference
  - compute_parity_metrics() -> max/mean absolute difference + latency
  - print_report()           -> the human-readable verification report

Run:
    python onnx/verify_parity.py
"""

import logging
import sys
import time
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import onnxruntime as ort
import pandas as pd
from sklearn.pipeline import Pipeline

# Make `preprocessing` importable regardless of the caller's cwd.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.preprocess import (  # noqa: E402
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    load_and_preprocess_data,
)

# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("hemagrid.verify_parity")

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

MODELS_DIR = PROJECT_ROOT / "models"
PIPELINE_PATH = MODELS_DIR / "pipeline.pkl"
ONNX_MODEL_PATH = MODELS_DIR / "model.onnx"

N_SAMPLES = 100
N_DISPLAY_SAMPLES = 10
MAX_DIFF_THRESHOLD = 0.01
RANDOM_STATE = 42


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def load_artifacts() -> Tuple[Pipeline, ort.InferenceSession, pd.DataFrame, pd.Series]:
    """Load the sklearn pipeline, the ONNX Runtime session, and the test split.

    Returns:
        pipeline: The fitted sklearn Pipeline.
        session: An ONNX Runtime InferenceSession over model.onnx.
        X_test: Raw (unencoded) test features from load_and_preprocess_data().
        y_test: Test targets.

    Raises:
        FileNotFoundError: If pipeline.pkl or model.onnx is missing.
    """
    if not PIPELINE_PATH.exists():
        raise FileNotFoundError(
            f"No trained pipeline found at {PIPELINE_PATH}. Run training/train.py first."
        )
    if not ONNX_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No ONNX model found at {ONNX_MODEL_PATH}. Run onnx/convert_to_onnx.py first."
        )

    logger.info("Loading sklearn pipeline from %s", PIPELINE_PATH)
    pipeline = joblib.load(PIPELINE_PATH)

    logger.info("Loading ONNX Runtime session from %s", ONNX_MODEL_PATH)
    session = ort.InferenceSession(str(ONNX_MODEL_PATH))

    logger.info("Loading test split via preprocessing.preprocess...")
    _, X_test, _, y_test, _ = load_and_preprocess_data()

    return pipeline, session, X_test, y_test


# --------------------------------------------------------------------------
# Input construction
# --------------------------------------------------------------------------

def build_onnx_inputs(sample: pd.DataFrame) -> Dict[str, np.ndarray]:
    """Convert a pandas sample into the named, per-column tensors that the
    ONNX graph expects (mirrors the schema built in convert_to_onnx.py's
    build_onnx_schema(): one input per column, numeric as float32,
    categorical as string objects).

    Args:
        sample: A slice of X_test with the raw (unencoded) feature columns.

    Returns:
        Dict mapping ONNX input name -> numpy array of shape (n, 1).
    """
    inputs: Dict[str, np.ndarray] = {}
    for col in NUMERICAL_FEATURES:
        inputs[col] = sample[col].to_numpy().reshape(-1, 1).astype(np.float32)
    for col in CATEGORICAL_FEATURES:
        inputs[col] = sample[col].to_numpy().reshape(-1, 1).astype(str).astype(object)
    return inputs


# --------------------------------------------------------------------------
# Prediction
# --------------------------------------------------------------------------

def run_predictions(
    pipeline: Pipeline, session: ort.InferenceSession, sample: pd.DataFrame
) -> Tuple[np.ndarray, np.ndarray, float]:
    """Run predictions through both sklearn and ONNX Runtime on the same sample.

    Args:
        pipeline: The fitted sklearn Pipeline.
        session: The ONNX Runtime InferenceSession.
        sample: A slice of X_test (raw, unencoded features).

    Returns:
        sklearn_preds: 1D array of sklearn predictions.
        onnx_preds: 1D array of ONNX Runtime predictions.
        avg_latency_ms: Average per-call ONNX Runtime inference latency, in
            milliseconds, measured one row at a time (matches the real
            single-request inference pattern the FastAPI endpoint will use).

    Raises:
        RuntimeError: If either inference path fails.
    """
    try:
        sklearn_preds = pipeline.predict(sample).astype(np.float64)
    except Exception as exc:
        raise RuntimeError(f"sklearn Pipeline prediction failed: {exc}") from exc

    onnx_preds = np.zeros(len(sample), dtype=np.float64)
    latencies_ms = []
    output_name = session.get_outputs()[0].name

    try:
        for i in range(len(sample)):
            row = sample.iloc[[i]]
            onnx_inputs = build_onnx_inputs(row)

            start = time.perf_counter()
            result = session.run([output_name], onnx_inputs)
            latencies_ms.append((time.perf_counter() - start) * 1000)

            onnx_preds[i] = float(np.asarray(result[0]).reshape(-1)[0])
    except Exception as exc:
        raise RuntimeError(f"ONNX Runtime prediction failed: {exc}") from exc

    avg_latency_ms = float(np.mean(latencies_ms))
    return sklearn_preds, onnx_preds, avg_latency_ms


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------

def compute_parity_metrics(
    sklearn_preds: np.ndarray, onnx_preds: np.ndarray, avg_latency_ms: float
) -> Dict[str, float]:
    """Compute max/mean absolute difference between the two prediction sets.

    Args:
        sklearn_preds: sklearn Pipeline predictions.
        onnx_preds: ONNX Runtime predictions.
        avg_latency_ms: Average ONNX Runtime inference latency in ms.

    Returns:
        Dict with keys: max_diff, mean_diff, avg_latency_ms, passed.
    """
    abs_diff = np.abs(sklearn_preds - onnx_preds)
    max_diff = float(np.max(abs_diff))
    mean_diff = float(np.mean(abs_diff))
    passed = max_diff < MAX_DIFF_THRESHOLD

    return {
        "max_diff": max_diff,
        "mean_diff": mean_diff,
        "avg_latency_ms": avg_latency_ms,
        "passed": passed,
    }


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

def print_report(
    metrics: Dict[str, float],
    sklearn_preds: np.ndarray,
    onnx_preds: np.ndarray,
) -> None:
    """Print the verification report and a per-sample comparison table.

    Args:
        metrics: Output of compute_parity_metrics().
        sklearn_preds: sklearn Pipeline predictions (same order as onnx_preds).
        onnx_preds: ONNX Runtime predictions.
    """
    print("\n" + "=" * 40)
    print("ONNX Verification Report")
    print("=" * 40)
    print(f"Maximum Difference: {metrics['max_diff']:.6f}")
    print(f"Mean Difference:    {metrics['mean_diff']:.6f}")
    print(f"Average Latency:    {metrics['avg_latency_ms']:.4f} ms")
    print(f"Result:             {'PASS' if metrics['passed'] else 'FAIL'} "
          f"(threshold: max diff < {MAX_DIFF_THRESHOLD})")
    print("=" * 40)

    rng = np.random.default_rng(RANDOM_STATE)
    display_indices = rng.choice(len(sklearn_preds), size=min(N_DISPLAY_SAMPLES, len(sklearn_preds)), replace=False)
    display_indices.sort()

    comparison_df = pd.DataFrame(
        {
            "Sample Number": display_indices,
            "Scikit-Learn Prediction": sklearn_preds[display_indices].round(4),
            "ONNX Prediction": onnx_preds[display_indices].round(4),
            "Difference": np.abs(
                sklearn_preds[display_indices] - onnx_preds[display_indices]
            ).round(6),
        }
    )
    print(f"\nComparison Table ({N_DISPLAY_SAMPLES} random samples):")
    print(comparison_df.to_string(index=False))


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> None:
    try:
        pipeline, session, X_test, y_test = load_artifacts()
    except FileNotFoundError as exc:
        logger.error("Verification failed: %s", exc)
        sys.exit(1)

    n_samples = min(N_SAMPLES, len(X_test))
    logger.info("Randomly selecting %d samples from X_test (size=%d)...", n_samples, len(X_test))
    rng = np.random.default_rng(RANDOM_STATE)
    sample_indices = rng.choice(len(X_test), size=n_samples, replace=False)
    sample = X_test.iloc[sample_indices].reset_index(drop=True)

    try:
        sklearn_preds, onnx_preds, avg_latency_ms = run_predictions(pipeline, session, sample)
    except RuntimeError as exc:
        logger.error("Verification failed: %s", exc)
        sys.exit(1)

    metrics = compute_parity_metrics(sklearn_preds, onnx_preds, avg_latency_ms)
    logger.info(
        "Parity check: max_diff=%.6f mean_diff=%.6f avg_latency=%.4fms result=%s",
        metrics["max_diff"], metrics["mean_diff"], metrics["avg_latency_ms"],
        "PASS" if metrics["passed"] else "FAIL",
    )

    print_report(metrics, sklearn_preds, onnx_preds)

    if not metrics["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()