"""
train.py
HemaGrid AI - Model Training & ONNX Compiler Pipeline

Loads historical CSV datasets, performs pipeline preprocessing, trains a
predictive Random Forest regression model, and exports the final weights to ONNX format.
"""

import os
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ONNX Libraries
try:
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
    HAS_ONNX_CONVERTER = True
except ImportError:
    HAS_ONNX_CONVERTER = False

def train_model():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "..", "datasets", "sample_blood_data.csv")

    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at: {data_path}. Run generate_sample_data.py first.")
        return

    # Load dataset
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} training examples.")

    # Split features and label
    X = df.drop(columns=["units_demanded"])
    y = df["units_demanded"]

    # Define Preprocessing Column Transformer
    categorical_features = ["hospital_type", "blood_type"]
    numerical_features = ["hospital_id", "temperature_c", "dengue_cases_weekly", "day_of_week", "month"]

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
            ('num', 'passthrough', numerical_features)
        ]
    )

    # Construct the full pipeline
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    # Train / Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Model
    print("Training Random Forest Regressor Model...")
    model_pipeline.fit(X_train, y_train)
    print("Training completed.")

    # Evaluate Model
    y_pred = model_pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print("\n--- Model Performance Evaluation ---")
    print(f"    R^2 Score:               {r2:.4f}")
    print(f"    Mean Absolute Error:     {mae:.2f} units")
    print(f"    Root Mean Squared Error: {rmse:.2f} units")
    print("------------------------------------\n")

    # Export Model weights to models directory
    models_dir = os.path.join(current_dir, "..", "models")
    os.makedirs(models_dir, exist_ok=True)

    if HAS_ONNX_CONVERTER:
        print("Converting model to ONNX format...")
        # Define the input type format: Float Tensor of shape [None, 7]
        # (5 numerical features, and two categorical string features)
        # Note: For ONNX conversion, scikit-learn pipeline expects specific inputs.
        # We define input as a dataframe-like structure for skl2onnx conversion.
        # To avoid type mismatch issues in diverse runtimes, we compile input features.
        
        # We convert individual types for the inputs
        initial_types = [
            ('hospital_id', FloatTensorType([None, 1])),
            ('hospital_type', FloatTensorType([None, 1])), # Handled as strings in initial split
            ('blood_type', FloatTensorType([None, 1])),
            ('temperature_c', FloatTensorType([None, 1])),
            ('dengue_cases_weekly', FloatTensorType([None, 1])),
            ('day_of_week', FloatTensorType([None, 1])),
            ('month', FloatTensorType([None, 1]))
        ]

        # For simple ONNX inference, we compile inputs as float representation (e.g. pre-encoded features) 
        # or we export the scikit-learn pipeline directly.
        # We export the pipeline features directly to simplify client usage:
        initial_type = [('float_input', FloatTensorType([None, X.shape[1]]))]
        
        # We train a secondary numerical-only pipeline if conversion of strings is problematic
        # but to keep it simple, we encode the input dataframe to float matrix for robust ONNX execution.
        X_train_encoded = preprocessor.fit_transform(X_train)
        X_test_encoded = preprocessor.transform(X_test)
        
        # Convert X_train_encoded from sparse matrix if needed
        if hasattr(X_train_encoded, "toarray"):
            X_train_encoded = X_train_encoded.toarray()
            X_test_encoded = X_test_encoded.toarray()

        encoded_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
        encoded_regressor.fit(X_train_encoded, y_train)

        # Evaluate parity
        test_pred_encoded = encoded_regressor.predict(X_test_encoded)
        r2_encoded = r2_score(y_test, test_pred_encoded)
        print(f"Parity check - Encoded Model R^2: {r2_encoded:.4f}")

        # Convert to ONNX
        num_features = X_train_encoded.shape[1]
        onnx_input_type = [('input', FloatTensorType([None, num_features]))]
        
        onnx_model = convert_sklearn(
            encoded_regressor, 
            initial_types=onnx_input_type,
            target_opset=12
        )

        onnx_path = os.path.join(models_dir, "demand_predictor.onnx")
        with open(onnx_path, "wb") as f:
            f.write(onnx_model.SerializeToString())
        print(f"Successfully compiled and saved ONNX model to: {onnx_path}")
        
        # Save preprocessor transformer mapping details
        # For simplicity, we also pickle the preprocessor so the inference engine can map categories
        import pickle
        preprocessor_path = os.path.join(models_dir, "preprocessor.pkl")
        with open(preprocessor_path, "wb") as f:
            pickle.dump(preprocessor, f)
        print(f"Saved preprocessor encoder map to: {preprocessor_path}")

    else:
        print("Warning: 'skl2onnx' is not installed. Exporting model as standard Python pickle instead.")
        import pickle
        pickle_path = os.path.join(models_dir, "demand_predictor.pkl")
        with open(pickle_path, "wb") as f:
            pickle.dump(model_pipeline, f)
        print(f"Saved scikit-learn pipeline pickle to: {pickle_path}")

if __name__ == "__main__":
    train_model()
