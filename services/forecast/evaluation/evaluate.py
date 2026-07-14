"""Standalone evaluation of the saved pipeline on a held-out split.

Run:  python evaluation/evaluate.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import joblib

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.preprocess import load_and_preprocess_data  # noqa: E402
from training.train import evaluate_model  # noqa: E402

PIPELINE_PATH = PROJECT_ROOT / "models" / "pipeline.pkl"


def main() -> None:
    if not PIPELINE_PATH.exists():
        raise SystemExit(f"No pipeline at {PIPELINE_PATH}. Run training/train.py first.")
    pipeline = joblib.load(PIPELINE_PATH)
    _, X_test, _, y_test, _ = load_and_preprocess_data()
    metrics = evaluate_model(pipeline, X_test, y_test)
    print("Evaluation:", {k: round(v, 4) for k, v in metrics.items()})


if __name__ == "__main__":
    main()
