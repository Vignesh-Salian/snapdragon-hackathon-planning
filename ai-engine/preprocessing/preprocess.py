import logging
from pathlib import Path
from typing import List, Tuple

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("hemagrid.preprocess")

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

# Resolved relative to this file so the module works regardless of the
# caller's current working directory (e.g. train.py importing from /training).
DEFAULT_CSV_PATH = Path(__file__).resolve().parent.parent / "datasets" / "blood_demand.csv"

TARGET_COLUMN = "expected_demand_units"

# Reserved for post-prediction inventory logic, not a model input.
NON_FEATURE_COLUMNS = ["current_inventory"]

NUMERICAL_FEATURES: List[str] = [
    "hospital_id",
    "temperature_c",
    "rainfall_mm",
    "dengue_cases_weekly",
    "road_accidents",
    "emergency_cases",
    "scheduled_surgeries",
    "holiday",
    "blood_donation_camp",
    "day_of_week",
    "month",
]

CATEGORICAL_FEATURES: List[str] = [
    "hospital_type",
    "city_region",
    "blood_type",
    "season",
]

ALL_FEATURES: List[str] = NUMERICAL_FEATURES + CATEGORICAL_FEATURES


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def load_dataset(csv_path: Path = DEFAULT_CSV_PATH) -> pd.DataFrame:
    """Load the raw blood demand dataset from disk.

    Args:
        csv_path: Path to blood_demand.csv.

    Returns:
        The raw, unvalidated DataFrame.

    Raises:
        FileNotFoundError: If csv_path does not exist.
    """
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    logger.info("Loading dataset from %s", csv_path)
    df = pd.read_csv(csv_path)
    logger.info("Loaded dataset with shape %s", df.shape)
    return df


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def validate_dataset(df: pd.DataFrame) -> None:
    """Fail fast on data quality issues before any splitting/fitting.

    Checks:
        - No missing values anywhere in the dataset.
        - All expected feature + target columns are present.
        - The feature count (excluding target and NON_FEATURE_COLUMNS)
          matches the expected ALL_FEATURES count.

    Args:
        df: Raw dataset as loaded by load_dataset().

    Raises:
        ValueError: If any validation check fails.
    """
    missing_values = df.isnull().sum()
    total_missing = missing_values.sum()
    if total_missing > 0:
        logger.error("Dataset contains missing values:\n%s", missing_values[missing_values > 0])
        raise ValueError(f"Dataset contains {total_missing} missing values, aborting.")
    logger.info("No missing values found.")

    required_columns = ALL_FEATURES + [TARGET_COLUMN]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Dataset is missing expected columns: {missing_columns}")
    logger.info("All required columns present.")

    expected_feature_count = len(ALL_FEATURES)
    available_feature_count = len(
        [c for c in df.columns if c not in NON_FEATURE_COLUMNS + [TARGET_COLUMN]]
    )
    if expected_feature_count != available_feature_count:
        raise ValueError(
            f"Feature count mismatch: expected {expected_feature_count} features "
            f"({ALL_FEATURES}), but dataset (minus target/excluded columns) has "
            f"{available_feature_count}."
        )
    logger.info("Feature count matches expected (%d features).", expected_feature_count)


# --------------------------------------------------------------------------
# Pipeline construction
# --------------------------------------------------------------------------

def build_preprocessor() -> ColumnTransformer:
    """Build the ColumnTransformer that encodes categoricals and passes
    numeric features through untouched.

    Returns:
        An unfitted ColumnTransformer.
    """
    # Numerics are scaled (not passed through) because the MLP is sensitive to
    # input magnitude; StandardScaler converts cleanly to ONNX.
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERICAL_FEATURES),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ],
        remainder="drop",
    )


def _build_pipeline() -> Pipeline:
    """Build the full reusable pipeline: preprocessing -> MLP estimator.

    Internal helper used by load_and_preprocess_data(). An MLPRegressor (not a
    tree ensemble) is used so the exported ONNX graph runs on the Hexagon NPU
    via the QNN Execution Provider — TreeEnsembleRegressor falls back to CPU.
    Training/tuning lives in training/train.py.

    Returns:
        An unfitted sklearn Pipeline.
    """
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            (
                "model",
                MLPRegressor(
                    hidden_layer_sizes=(64, 32),
                    activation="relu",
                    max_iter=500,
                    early_stopping=True,
                    random_state=42,
                ),
            ),
        ]
    )


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def load_and_preprocess_data(
    csv_path: Path = DEFAULT_CSV_PATH,
    test_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, Pipeline]:
    """Load, validate, split the dataset, and build the reusable pipeline.

    Args:
        csv_path: Path to the blood_demand.csv dataset.
        test_size: Fraction of rows held out for the test split.
        random_state: Seed for a reproducible split.

    Returns:
        X_train: Training features (raw, unencoded - the pipeline encodes them).
        X_test: Test features (raw, unencoded).
        y_train: Training targets.
        y_test: Test targets.
        pipeline: Unfitted sklearn Pipeline (preprocessing + placeholder model).
            Call pipeline.fit(X_train, y_train) in training/train.py.
    """
    df = load_dataset(csv_path)
    validate_dataset(df)

    X = df[ALL_FEATURES]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    logger.info("Split dataset: X_train=%s X_test=%s", X_train.shape, X_test.shape)

    pipeline = _build_pipeline()
    logger.info("Built unfitted pipeline (preprocessing + MLPRegressor).")

    return X_train, X_test, y_train, y_test, pipeline


# --------------------------------------------------------------------------
# Standalone validation run
# --------------------------------------------------------------------------

if __name__ == "__main__":
    raw_df = load_dataset()
    print(f"\nDataset shape: {raw_df.shape}")

    missing_summary = raw_df.isnull().sum()
    print("\nMissing value summary:")
    print(missing_summary.to_string())
    print(f"Total missing values: {missing_summary.sum()}")

    X_train, X_test, y_train, y_test, pipeline = load_and_preprocess_data()

    print(f"\nX_train shape: {X_train.shape}")
    print(f"X_test shape:  {X_test.shape}")
    print(f"y_train shape: {y_train.shape}")
    print(f"y_test shape:  {y_test.shape}")

    # Fit just the preprocessing step to report the encoded feature space.
    preprocessor = pipeline.named_steps["preprocessor"]
    preprocessor.fit(X_train)
    feature_names = preprocessor.get_feature_names_out()

    print(f"\nEncoded feature count: {len(feature_names)}")
    print(f"Encoded feature names:\n{list(feature_names)}")

