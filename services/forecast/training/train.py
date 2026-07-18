"""
HemaGrid AI - Model Training
Owner: Tejas

Clean-architecture training script: data loading, search construction,
fitting, evaluation, and artifact persistence are kept as separate,
independently testable functions rather than one monolithic main().

  - load_training_data()     -> wraps preprocessing.load_and_preprocess_data()
  - build_search()            -> constructs the RandomizedSearchCV object
  - train_model()              -> fits the search, returns the best pipeline
  - evaluate_model()           -> R^2 / MAE / RMSE on the held-out test set
  - save_pipeline()            -> persists the fitted pipeline with joblib
  - save_feature_importance()  -> persists encoded feature importances

The saved pipeline (models/pipeline.pkl) must stay a single sklearn
Pipeline object (no custom wrappers) so a later skl2onnx conversion step
can convert preprocessing + model as one ONNX graph.

Run:
    python training/train.py
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import RandomizedSearchCV
from sklearn.pipeline import Pipeline

# Make `preprocessing` importable regardless of the caller's cwd.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.preprocess import load_and_preprocess_data  # noqa: E402

# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("hemagrid.train")

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

MODELS_DIR = PROJECT_ROOT / "models"

# Full pipeline used by FastAPI inference
PIPELINE_PATH = MODELS_DIR / "pipeline.pkl"

# Separate artifacts for Qualcomm NPU deployment
PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.pkl"
MODEL_PATH = MODELS_DIR / "mlp_model.pkl"

FEATURE_IMPORTANCE_PATH = MODELS_DIR / "feature_importance.csv"

# Prefixed "model__" per sklearn Pipeline convention, since the estimator
# lives at pipeline.named_steps["model"] (an MLPRegressor — see preprocess.py).
PARAM_DISTRIBUTIONS = {
    "model__hidden_layer_sizes": [
        (128, 64), 
        (128, 64, 32), 
        (256, 128, 64),
        (256, 128, 64, 32)
    ],
    "model__alpha": [1e-3, 5e-3, 1e-2, 5e-2, 1e-1], # Added higher alpha regularization to prevent overfitting
    "model__learning_rate_init": [1e-3, 3e-3, 5e-3],
}

SEARCH_CONFIG = dict(
    cv=5,            # Increased cross-validation folds from 3 to 5 for better generalization
    n_iter=15,       # Increased search iterations from 6 to 15 to find a better configuration
    random_state=42,
    n_jobs=-1,
    scoring="r2",
)

R2_TARGET = 0.75
TOP_N_FEATURES = 10


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------

def load_training_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, Pipeline]:
    """Load, validate, and split the dataset via the preprocessing module.

    Thin wrapper kept as its own function so training's data-loading step
    is independently callable/mockable in tests, separate from the search
    and fitting logic.

    Returns:
        X_train, X_test, y_train, y_test, pipeline (unfitted).

    Raises:
        FileNotFoundError: If the dataset CSV is missing.
        ValueError: If the dataset fails validation.
    """
    logger.info("Loading and preprocessing training data...")
    X_train, X_test, y_train, y_test, pipeline = load_and_preprocess_data()
    logger.info("Data ready. X_train=%s X_test=%s", X_train.shape, X_test.shape)
    return X_train, X_test, y_train, y_test, pipeline


# --------------------------------------------------------------------------
# Search construction
# --------------------------------------------------------------------------

def build_search(pipeline: Pipeline) -> RandomizedSearchCV:
    """Construct the RandomizedSearchCV object over the pipeline.

    Args:
        pipeline: Unfitted Pipeline (preprocessing + placeholder model)
            from load_training_data().

    Returns:
        An unfitted RandomizedSearchCV wrapping the pipeline.
    """
    logger.info(
        "Building RandomizedSearchCV: n_iter=%d, cv=%d, scoring=%s",
        SEARCH_CONFIG["n_iter"], SEARCH_CONFIG["cv"], SEARCH_CONFIG["scoring"],
    )
    return RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=PARAM_DISTRIBUTIONS,
        **SEARCH_CONFIG,
    )


# --------------------------------------------------------------------------
# Training
# --------------------------------------------------------------------------

def train_model(
    search: RandomizedSearchCV, X_train: pd.DataFrame, y_train: pd.Series
) -> Tuple[Pipeline, Dict]:
    """Fit the search over the training data.

    Args:
        search: Unfitted RandomizedSearchCV from build_search().
        X_train: Raw (unencoded) training features.
        y_train: Training targets.

    Returns:
        best_pipeline: The fitted Pipeline with the best-found hyperparameters.
        search_summary: Dict with best_params and cv_score.

    Raises:
        RuntimeError: If fitting fails for any reason (wrapped with context).
    """
    logger.info("Starting hyperparameter search fit...")
    try:
        search.fit(X_train, y_train)
    except Exception as exc:
        raise RuntimeError(f"RandomizedSearchCV fitting failed: {exc}") from exc

    logger.info("Search complete. Best CV R^2: %.4f", search.best_score_)
    search_summary = {
        "best_params": search.best_params_,
        "cv_score": search.best_score_,
    }
    return search.best_estimator_, search_summary


# --------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------

def evaluate_model(
    fitted_pipeline: Pipeline, X_test: pd.DataFrame, y_test: pd.Series
) -> Dict[str, float]:
    """Evaluate the fitted pipeline on the held-out test set.

    Args:
        fitted_pipeline: A fitted sklearn Pipeline.
        X_test: Raw (unencoded) test features.
        y_test: Test targets.

    Returns:
        Dict with keys: r2, mae, rmse.
    """
    y_pred = fitted_pipeline.predict(X_test)
    metrics = {
        "r2": r2_score(y_test, y_pred),
        "mae": mean_absolute_error(y_test, y_pred),
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
    }
    logger.info(
        "Evaluation: R^2=%.4f MAE=%.4f RMSE=%.4f",
        metrics["r2"], metrics["mae"], metrics["rmse"],
    )
    return metrics


# --------------------------------------------------------------------------
# Persistence
# --------------------------------------------------------------------------

def save_pipeline(fitted_pipeline: Pipeline, path: Path = PIPELINE_PATH) -> None:
    """Persist the fitted Pipeline (preprocessing + model) with joblib.

    Args:
        fitted_pipeline: A fitted sklearn Pipeline.
        path: Destination path for the .pkl file.

    Raises:
        OSError: If the file cannot be written.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(fitted_pipeline, path)
    except OSError as exc:
        raise OSError(f"Failed to save pipeline to {path}: {exc}") from exc
    logger.info("Saved fitted pipeline -> %s", path)

def save_npu_artifacts(
    fitted_pipeline: Pipeline,
    preprocessor_path: Path = PREPROCESSOR_PATH,
    model_path: Path = MODEL_PATH,
) -> None:
    """
    Save preprocessing and model separately for Qualcomm NPU deployment.

    The complete sklearn pipeline is kept for backend inference,
    while the MLP model alone is exported to ONNX for NPU execution.
    """

    try:
        preprocessor = fitted_pipeline.named_steps["preprocessor"]
        model = fitted_pipeline.named_steps["model"]

        joblib.dump(
            preprocessor,
            preprocessor_path,
        )

        joblib.dump(
            model,
            model_path,
        )

    except OSError as exc:
        raise OSError(
            f"Failed saving NPU artifacts: {exc}"
        ) from exc

    logger.info(
        "Saved NPU preprocessor -> %s",
        preprocessor_path,
    )

    logger.info(
        "Saved NPU model -> %s",
        model_path,
    )

def save_feature_importance(
    fitted_pipeline: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    path: Path = FEATURE_IMPORTANCE_PATH,
) -> pd.DataFrame:
    """Compute and save permutation feature importances over the raw input
    columns. MLPRegressor has no `feature_importances_`, and raw-column names
    (e.g. "dengue_cases_weekly") are what the Explainable-AI panel wants to
    show — so permutation importance on the whole pipeline is the right tool.

    Args:
        fitted_pipeline: A fitted sklearn Pipeline (preprocessing + MLP).
        X_test: Raw (unencoded) test features — the 15 model inputs.
        y_test: Test targets.
        path: Destination CSV path.

    Returns:
        DataFrame with columns [feature_name, importance], sorted descending.

    Raises:
        OSError: If the file cannot be written.
    """
    result = permutation_importance(
        fitted_pipeline, X_test, y_test, n_repeats=5, random_state=42, n_jobs=-1
    )
    importance_df = (
        pd.DataFrame(
            {"feature_name": list(X_test.columns), "importance": result.importances_mean}
        )
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        importance_df.to_csv(path, index=False)
    except OSError as exc:
        raise OSError(f"Failed to save feature importance to {path}: {exc}") from exc
    logger.info("Saved feature importances -> %s", path)

    return importance_df


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> None:
    try:
        X_train, X_test, y_train, y_test, pipeline = load_training_data()
        search = build_search(pipeline)
        best_pipeline, search_summary = train_model(search, X_train, y_train)
        metrics = evaluate_model(best_pipeline, X_test, y_test)

    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        logger.error("Training failed: %s", exc)
        sys.exit(1)

    print("\n" + "=" * 60)
    print("HemaGrid AI - Training Results")
    print("=" * 60)
    print(f"Best Parameters:        {search_summary['best_params']}")
    print(f"Cross Validation Score: {search_summary['cv_score']:.4f} (R^2, mean over cv=5)")
    print(f"Test R^2:               {metrics['r2']:.4f}")
    print(f"Test MAE:               {metrics['mae']:.4f}")
    print(f"Test RMSE:              {metrics['rmse']:.4f}")
    print("=" * 60)

    if metrics["r2"] < R2_TARGET:
        logger.warning(
            "Test R^2 (%.4f) is below the spec target of %.2f.",
            metrics["r2"],
            R2_TARGET,
        )
    else:
        logger.info(
            "Test R^2 (%.4f) meets the spec target of %.2f.",
            metrics["r2"],
            R2_TARGET,
        )

    try:
        # Save complete pipeline for FastAPI/backend inference
        save_pipeline(best_pipeline)

        # Save separate artifacts for Qualcomm NPU deployment
        save_npu_artifacts(best_pipeline)

        # Save feature importance for explainability
        importance_df = save_feature_importance(
            best_pipeline,
            X_test,
            y_test,
        )

    except (OSError, ValueError) as exc:
        logger.error("Failed to save artifacts: %s", exc)
        sys.exit(1)

    print(f"\nTop {TOP_N_FEATURES} Most Important Features:")
    print(importance_df.head(TOP_N_FEATURES).to_string(index=False))


if __name__ == "__main__":
    main()