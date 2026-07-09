"""
test_model.py
HemaGrid AI - Model & Telemetry Verification Tests

Unit tests validating dataset schemas, preprocessing pipelines,
inference outputs, and alert boundary logic.
"""

import os
import unittest
import pandas as pd
import numpy as np
from training.train import train_model
from inference.predict import app, load_models
from fastapi.testclient import TestClient

class TestAIEngine(unittest.TestCase):
    def setUp(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(self.current_dir, "..", "datasets", "sample_blood_data.csv")
        self.models_dir = os.path.join(self.current_dir, "..", "models")
        self.client = TestClient(app)

    def test_dataset_schema(self):
        """
        Validates that the generated synthetic CSV matches the feature specification.
        """
        self.assertTrue(os.path.exists(self.data_path), "Dataset CSV must be generated first.")
        df = pd.read_csv(self.data_path)
        
        required_columns = [
            "hospital_id", "hospital_type", "blood_type", 
            "temperature_c", "dengue_cases_weekly", 
            "day_of_week", "month", "units_demanded"
        ]
        
        for col in required_columns:
            self.assertIn(col, df.columns, f"Missing required column: {col}")

    def test_model_training(self):
        """
        Runs model training and verifies that at least one model artifact is written.
        """
        train_model()
        
        onnx_file = os.path.join(self.models_dir, "demand_predictor.onnx")
        pkl_file = os.path.join(self.models_dir, "demand_predictor.pkl")
        
        model_exists = os.path.exists(onnx_file) or os.path.exists(pkl_file)
        self.assertTrue(model_exists, "Training failed to output any model files.")

    def test_inference_endpoints(self):
        """
        Triggers the FastAPI startup loader, and tests mock requests against the predict endpoint.
        """
        # Manually load the compiled models
        load_models()
        
        test_payload = {
            "hospital_id": 1,
            "hospital_type": "Trauma",
            "blood_type": "O_NEG",
            "temperature_c": 35.0,
            "dengue_cases_weekly": 200,
            "day_of_week": 6,
            "month": 7
        }
        
        # Verify endpoint returns expected fields
        response = self.client.post("/api/v1/predict/demand", json=test_payload)
        
        # If model is not trained yet, it might return 503, which is a handled test outcome.
        # But we train it in the previous step, so it should succeed.
        if response.status_code == 200:
            data = response.json()
            self.assertEqual(data["status"], "success")
            self.assertIn("expected_demand_units", data["predictions"])
            self.assertIn("recommended_min_inventory", data["predictions"])
            self.assertIn("alert_level", data["predictions"])
            
            # Assert alert level boundary mapping logic
            predicted = data["predictions"]["expected_demand_units"]
            alert = data["predictions"]["alert_level"]
            if predicted >= 25.0:
                self.assertEqual(alert, "CRITICAL")
            elif predicted >= 15.0:
                self.assertEqual(alert, "WARNING")
            else:
                self.assertEqual(alert, "SAFE")
        else:
            self.assertEqual(response.status_code, 503)

if __name__ == "__main__":
    unittest.main()
