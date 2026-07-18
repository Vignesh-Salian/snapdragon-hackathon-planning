"""
HemaGrid AI - ONNX Conversion

Converts the trained MLPRegressor into an ONNX graph
for Qualcomm QAIRT / Snapdragon NPU deployment.

Preprocessing is handled separately before inference.
The ONNX model receives only numeric FLOAT32 tensors.

Functions:

  - load_model()        -> loads the trained MLP model
  - build_onnx_schema() -> creates numeric input schema
  - convert_model()     -> converts MLPRegressor to ONNX
  - save_onnx_model()   -> writes the ONNX file to disk

Run:
    python onnx/convert_to_onnx.py
"""

import logging
import sys
from pathlib import Path

import joblib
from onnx import ModelProto
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from sklearn.neural_network import MLPRegressor

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

# NPU deployment model (MLP only)
MODEL_PATH = MODELS_DIR / "mlp_model.pkl"

# Output ONNX file
ONNX_MODEL_PATH = MODELS_DIR / "model.onnx"

# Number of features after preprocessing
INPUT_FEATURE_COUNT = 28

# Snapdragon's Hexagon NPU / QAIRT toolchain expects...
TARGET_OPSET = 17


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def load_model(path: Path = MODEL_PATH) -> MLPRegressor:
    """Load the trained MLP model for ONNX/NPU conversion."""

    if not path.exists():
        raise FileNotFoundError(
            f"No trained MLP model found at {path}. Run training/train.py first."
        )

    logger.info("Loading MLP model from %s", path)

    model = joblib.load(path)

    logger.info(
        "MLP model loaded: hidden_layers=%s",
        model.hidden_layer_sizes,
    )

    return model


# --------------------------------------------------------------------------
# Schema construction
# --------------------------------------------------------------------------

def build_onnx_schema():
    """
    Build ONNX input schema for Qualcomm NPU.

    The preprocessing is handled separately.
    ONNX receives only the transformed numeric feature vector.
    """

    logger.info(
        "Building ONNX schema with %d float features",
        INPUT_FEATURE_COUNT,
    )

    schema = [
    (
        "input",
        FloatTensorType([1, INPUT_FEATURE_COUNT])
    )
]

    logger.info("Schema built: input shape [1, %d]", INPUT_FEATURE_COUNT)

    return schema


# --------------------------------------------------------------------------
# Conversion
# --------------------------------------------------------------------------

def convert_model(
    model: MLPRegressor,
    schema,
) -> ModelProto:
    """
    Convert only the trained MLP model into ONNX.

    Preprocessing is intentionally excluded because Qualcomm
    AI Hub / NPU requires numeric tensor inputs only.
    """

    logger.info(
        "Starting ONNX conversion (target_opset=%d)...",
        TARGET_OPSET,
    )

    try:
        onnx_model = convert_sklearn(
            model,
            initial_types=schema,
            target_opset=TARGET_OPSET,
        )

    except Exception as exc:
        raise RuntimeError(
            f"skl2onnx conversion failed: {exc}"
        ) from exc

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
        model = load_model()
        schema = build_onnx_schema()
        onnx_model = convert_model(model, schema)
        save_onnx_model(onnx_model)
    except (FileNotFoundError, RuntimeError, OSError) as exc:
        logger.error("ONNX conversion failed: %s", exc)
        sys.exit(1)

    print("\n" + "=" * 60)
    print("HemaGrid AI - ONNX Conversion Complete")
    print("=" * 60)
    print(f"Source model:    {MODEL_PATH}")
    
    print(f"ONNX model:      {ONNX_MODEL_PATH}")
    print(f"Target opset:    {TARGET_OPSET}")
    print(f"Input features:  {INPUT_FEATURE_COUNT}")
    print("=" * 60)
    print("Next: run onnx/verify_parity.py to confirm sklearn/ONNX prediction parity.")


if __name__ == "__main__":
    main()