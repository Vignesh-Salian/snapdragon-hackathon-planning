"""
HemaGrid AI - ONNX Conversion
Owner: Tejas

Converts the trained sklearn Pipeline (ColumnTransformer + OneHotEncoder +
RandomForestRegressor) into a single ONNX graph, so the exact same
preprocessing + inference logic can run on ONNX Runtime - and ultimately
on Qualcomm QAIRT / the Snapdragon Hexagon NPU - without reimplementing
the encoding step separately at inference time.

Clean-architecture separation, matching preprocessing/preprocess.py and
training/train.py:

  - load_pipeline()      -> loads the fitted pipeline from disk
  - build_onnx_schema()  -> derives the ONNX input schema from
                             preprocessing.preprocess's own feature lists
                             (never hardcoded - adding/removing a feature
                             in preprocess.py automatically flows through)
  - convert_pipeline()   -> runs the skl2onnx conversion
  - save_onnx_model()    -> writes the .onnx file to disk

Run:
    python onnx/convert_to_onnx.py
"""

import logging
import sys
from pathlib import Path
from typing import List, Tuple

import joblib
from onnx import ModelProto
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType, StringTensorType
from sklearn.pipeline import Pipeline

# Make `preprocessing` importable regardless of the caller's cwd.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.preprocess import (  # noqa: E402
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
)

# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("hemagrid.convert_to_onnx")

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

MODELS_DIR = PROJECT_ROOT / "models"
PIPELINE_PATH = MODELS_DIR / "pipeline.pkl"
ONNX_MODEL_PATH = MODELS_DIR / "model.onnx"

# Snapdragon's Hexagon NPU / QAIRT toolchain expects a reasonably mainstream
# opset - 17 is well within ONNX Runtime's and QAIRT's supported range and
# avoids pulling in operators only recent opsets define.
TARGET_OPSET = 17


# --------------------------------------------------------------------------
# Loading
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


# --------------------------------------------------------------------------
# Schema construction
# --------------------------------------------------------------------------

def build_onnx_schema() -> List[Tuple[str, object]]:
    """Derive the ONNX input schema directly from preprocessing.preprocess's
    NUMERICAL_FEATURES / CATEGORICAL_FEATURES lists.

    Deliberately NOT hardcoded: if a feature is added to or removed from
    preprocessing.preprocess, this schema picks it up automatically on the
    next conversion run, with no changes needed here.

    Each column becomes its own named ONNX input of shape [None, 1]
    (skl2onnx's standard convention for a ColumnTransformer operating on a
    pandas DataFrame with heterogeneous dtypes per column):
      - Numerical columns -> FloatTensorType (RandomForestRegressor and the
        "passthrough" transformer both operate on float32 internally).
      - Categorical columns -> StringTensorType (consumed by the
        OneHotEncoder step inside the pipeline).

    Returns:
        A list of (column_name, onnx_type) tuples suitable for
        skl2onnx.convert_sklearn's `initial_types` argument.
    """
    logger.info(
        "Building ONNX input schema: %d numerical + %d categorical features",
        len(NUMERICAL_FEATURES), len(CATEGORICAL_FEATURES),
    )

    schema: List[Tuple[str, object]] = [
        (col, FloatTensorType([None, 1])) for col in NUMERICAL_FEATURES
    ]
    schema += [
        (col, StringTensorType([None, 1])) for col in CATEGORICAL_FEATURES
    ]

    logger.info("Schema built with %d total input columns.", len(schema))
    return schema


# --------------------------------------------------------------------------
# Conversion
# --------------------------------------------------------------------------

def convert_pipeline(
    pipeline: Pipeline, schema: List[Tuple[str, object]]
) -> ModelProto:
    """Convert the fitted sklearn Pipeline into an ONNX ModelProto.

    Args:
        pipeline: A fitted sklearn Pipeline (preprocessing + model).
        schema: The ONNX input schema from build_onnx_schema().

    Returns:
        The converted ONNX ModelProto.

    Raises:
        RuntimeError: If skl2onnx conversion fails for any reason (wrapped
            with context - the raw skl2onnx traceback is often unhelpful on
            its own).
    """
    logger.info("Starting ONNX conversion (target_opset=%d)...", TARGET_OPSET)
    try:
        onnx_model = convert_sklearn(
            pipeline, initial_types=schema, target_opset=TARGET_OPSET
        )
    except Exception as exc:
        raise RuntimeError(f"skl2onnx conversion failed: {exc}") from exc

    logger.info("Conversion successful.")
    return onnx_model


# --------------------------------------------------------------------------
# Persistence
# --------------------------------------------------------------------------

def save_onnx_model(onnx_model: ModelProto, path: Path = ONNX_MODEL_PATH) -> None:
    """Serialize and write the ONNX model to disk.

    Args:
        onnx_model: The converted ONNX ModelProto.
        path: Destination path for the .onnx file.

    Raises:
        OSError: If the file cannot be written.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(onnx_model.SerializeToString())
    except OSError as exc:
        raise OSError(f"Failed to save ONNX model to {path}: {exc}") from exc
    logger.info("Model saved -> %s", path)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> None:
    try:
        pipeline = load_pipeline()
        schema = build_onnx_schema()
        onnx_model = convert_pipeline(pipeline, schema)
        save_onnx_model(onnx_model)
    except (FileNotFoundError, RuntimeError, OSError) as exc:
        logger.error("ONNX conversion failed: %s", exc)
        sys.exit(1)

    print("\n" + "=" * 60)
    print("HemaGrid AI - ONNX Conversion Complete")
    print("=" * 60)
    print(f"Source pipeline: {PIPELINE_PATH}")
    print(f"ONNX model:      {ONNX_MODEL_PATH}")
    print(f"Target opset:    {TARGET_OPSET}")
    print(f"Input columns:   {len(NUMERICAL_FEATURES) + len(CATEGORICAL_FEATURES)}")
    print("=" * 60)
    print("Next: run onnx/verify_parity.py to confirm sklearn/ONNX prediction parity.")


if __name__ == "__main__":
    main()