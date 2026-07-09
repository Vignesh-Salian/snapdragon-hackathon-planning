"""
evaluate.py
HemaGrid AI - Model Parity & Metric Evaluation

Compares scikit-learn and compiled ONNX model outputs over validation datasets,
verifying calculations, measuring error, and confirming parity.
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    import onnxruntime as ort
    HAS_ONNX_RUNTIME = True
except ImportError:
    HAS_ONNX_RUNTIME = False

def run_evaluation():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(current_dir, "..", "models")
    data_path = os.path.join(current_dir, "..", "datasets", "sample_blood_data.csv")
    
    preprocessor_path = os.path.join(models_dir, "preprocessor.pkl")
    onnx_path = os.path.join(models_dir, "demand_predictor.onnx")
    pickle_path = os.path.join(models_dir, "demand_predictor.pkl")

    if not os.path.exists(data_path):
        print("Error: Training data CSV not found. Run generate_sample_data.py first.")
        return

    # Load dataset
    df = pd.read_csv(data_path)
    X = df.drop(columns=["units_demanded"])
    y = df["units_demanded"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 1. Evaluate Pipeline Model
    if os.path.exists(pickle_path):
        with open(pickle_path, "rb") as f:
            pipeline_model = pickle.load(f)
        
        preds_pk = pipeline_model.predict(X_test)
        mae_pk = mean_absolute_error(y_test, preds_pk)
        r2_pk = r2_score(y_test, preds_pk)
        
        print("\n=== Pipeline Pickle Model Performance ===")
        print(f"    R2 Score: {r2_pk:.4f}")
        print(f"    MAE:      {mae_pk:.2f} units")
    else:
        print("Note: Pickle pipeline model not found.")

    # 2. Evaluate ONNX Parity
    if HAS_ONNX_RUNTIME and os.path.exists(onnx_path) and os.path.exists(preprocessor_path):
        with open(preprocessor_path, "rb") as f:
            preprocessor = pickle.load(f)
            
        session = ort.InferenceSession(onnx_path)
        
        # Transform categories to numerical float indices
        X_test_encoded = preprocessor.transform(X_test)
        if hasattr(X_test_encoded, "toarray"):
            X_test_encoded = X_test_encoded.toarray()
            
        input_name = session.get_inputs()[0].name
        input_data = X_test_encoded.astype(np.float32)
        
        preds_onnx = session.run(None, {input_name: input_data})[0].flatten()
        
        mae_onnx = mean_absolute_error(y_test, preds_onnx)
        r2_onnx = r2_score(y_test, preds_onnx)
        
        print("\n=== Compiled ONNX Model Performance ===")
        print(f"    R2 Score: {r2_onnx:.4f}")
        print(f"    MAE:      {mae_onnx:.2f} units")
        
        # Parity calculation
        if os.path.exists(pickle_path):
            # For checking parity, we match encoded model predictions
            # Load encoded scikit-learn model to compare directly
            # Here we just compare predictions directly to check variance
            diff = np.abs(preds_pk - preds_onnx)
            max_diff = np.max(diff)
            mean_diff = np.mean(diff)
            
            print("\n=== Model Parity Metrics ===")
            print(f"    Mean Prediction Variance: {mean_diff:.5f}")
            print(f"    Max Prediction Variance:  {max_diff:.5f}")
            if mean_diff < 0.1:
                print("    Parity Status: PASS")
            else:
                print("    Parity Status: WARNING (Encoder difference or different estimator weights)")
    else:
        print("\nONNX Runtime or model files not available. Skipping parity checks.")

if __name__ == "__main__":
    run_evaluation()
