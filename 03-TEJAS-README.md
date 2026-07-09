# Work Assignment: AI Intelligence

*   **Module Owner:** Tejas
*   **Module Name:** Predictive Demand Forecasting Engine
*   **Objective:** Develop a machine learning model to forecast local hospital blood demand, compile it to ONNX format, and wrap it in a lightweight inference API.

---

## 1. Why This Module Exists

Predicting demand allows blood banks to move reserves toward hospitals before shortages occur. Running this model locally on Snapdragon hardware ensures fast, private predictions at the hospital hub.

---

## 2. Responsibilities & Folders Owned

*   **Repository Folder:** `/ai-engine`
*   **Primary Tasks:**
    *   Design synthetic datasets to simulate blood demand patterns.
    *   Build scikit-learn models (regression trees) to forecast expected units.
    *   Compile the model weights to ONNX format.
    *   Expose a FastAPI inference endpoint.

---

## 3. Features to Implement

1.  **Dataset Generator:** Create synthetic data mapping hospital types, blood types, weekly outbreak case counts, and seasonal weather logs.
2.  **Training Pipeline:** Train a regression model (e.g. Random Forest) and validate metrics.
3.  **ONNX Compiler:** Convert the trained model to `.onnx` and preprocessor parameters to `.pkl` formats.
4.  **Inference Endpoint:** Load the compiled ONNX model and return predicted values along with recommended inventory stock levels.

---

## 4. Detailed Task Checklist

- [ ] Create folder structure under `/ai-engine` including `datasets`, `training`, `inference`, `evaluation`, and `tests`.
- [ ] Write `generate_sample_data.py` to create a 1,000-row historical training dataset.
- [ ] Write `train.py` to preprocess features, train a Random Forest regressor, and validate performance.
- [ ] Implement ONNX export step inside `train.py` using `skl2onnx`. Save `demand_predictor.onnx` and `preprocessor.pkl`.
- [ ] Write the FastAPI app `inference/predict.py` to run predictions using `onnxruntime`.
- [ ] Build fallback logic inside `predict.py` to load standard scikit-learn pickles if ONNX Runtime is unavailable.
- [ ] Write `evaluation/evaluate.py` to check prediction parity between ONNX and scikit-learn outputs.

---

## 5. Interface Specifications

### APIs to Expose
*   `POST /api/v1/predict/demand`
*   **Request Schema:**
    ```json
    {
      "hospital_id": "integer",
      "hospital_type": "General | Trauma | Clinic",
      "blood_type": "string (A_POS, O_NEG, etc.)",
      "temperature_c": "float",
      "dengue_cases_weekly": "integer",
      "day_of_week": "integer (1-7)",
      "month": "integer (1-12)"
    }
    ```
*   **Response Schema:**
    ```json
    {
      "status": "success",
      "predictions": {
        "expected_demand_units": "float",
        "recommended_min_inventory": "integer",
        "alert_level": "SAFE | WARNING | CRITICAL"
      }
    }
    ```

---

## 6. Coding & Documentation Standards

*   **Language & Tech:** Python, Scikit-Learn, ONNX Runtime, FastAPI, Pandas, NumPy.
*   **Coding Conventions:**
    *   Do not include string category mapping directly inside model features; use the preprocessor pipeline to one-hot encode inputs.
    *   Do not hardcode threshold rules; load boundaries from standard configuration blocks.
*   **Qualcomm Optimization Roadmap:** Prepare variables for compilation via the Qualcomm AI Engine Direct SDK (QAIRT) to target Snapdragon Hexagon NPUs.

---

## 7. Testing Responsibilities

*   Write model integration tests inside `/ai-engine/tests/test_model.py`.
*   Validate that data schemas match expected types.
*   Verify that model predictions are bounded within reasonable limits (e.g. demand is never negative).

---

## 8. Weekly Milestones

*   **Week 1:** Data generation script completed. CSV dataset stored in `/datasets/`.
*   **Week 2:** Model training script completed. Scikit-learn baseline evaluations ($R^2 > 0.70$) validated.
*   **Week 3:** ONNX conversion validated. Preprocessor serialization operational.
*   **Week 4:** FastAPI prediction server and parity checking scripts validated.

---

## 9. Dependencies & Constraints

*   **Modules Depending on Your Work:** Mithun (Core Backend forwards proxy requests to your API).
*   **Things NOT to Modify:** Do not modify directories outside `/ai-engine`.
*   **Inference Latency Target:** Single predictions must process in `<50ms`.
