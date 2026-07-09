# Module Owner Assignment: AI Intelligence

*   **Module Owner:** Tejas
*   **Module Name:** Predictive Demand Forecasting Engine

---

## 1. Module Overview

*   **Purpose:** Develop a forecasting model to predict regional blood demand, compile it to ONNX, and expose it via a REST API to support inventory optimization.
*   **Scope:** Synthetic dataset generator, regression model training, ONNX conversion, and inference endpoints.
*   **Success Criteria:** Model achieving $R^2 > 0.70$ on validation sets, inference response latency $<50\text{ms}$, and clean ONNX compilation output.

---

## 2. Responsibilities

Tejas is responsible for writing the dataset generation scripts, training the regression model (e.g. Random Forest), converting the weights to ONNX, and wrapping the output inside a FastAPI inference service.

---

## 3. Repository Ownership

*   **Folder Scope:** `/ai-engine`
*   **Files Owned:**
    *   `ai-engine/datasets/generate_sample_data.py`
    *   `ai-engine/training/train.py`
    *   `ai-engine/inference/predict.py`
    *   `ai-engine/evaluation/evaluate.py`
    *   `ai-engine/tests/test_model.py`

---

## 4. Functional Requirements

### Feature 1: Historical Data Generator
*   *Task:* Generate a CSV dataset representing 1,000 days of mock hospital transactions (dengue cases, seasonal weather, baseline demand).

### Feature 2: Model Training & Conversion
*   *Task:* Train a scikit-learn regressor to predict expected daily units demanded.
*   *Task:* Convert the trained pipeline to ONNX format using `skl2onnx`.

### Feature 3: Prediction API
*   *Task:* Expose a `/predict/demand` route.
*   *Task:* Run model predictions using `onnxruntime` and return expected units and inventory levels.

---

## 5. Technical Responsibilities

### APIs to Expose
*   `POST /api/v1/predict/demand`
*   **Request Format:**
    ```json
    {
      "hospital_id": "integer",
      "hospital_type": "General | Trauma | Clinic",
      "blood_type": "string",
      "temperature_c": "float",
      "dengue_cases_weekly": "integer",
      "day_of_week": "integer",
      "month": "integer"
    }
    ```
*   **Response Format:**
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

## 6. Non-Functional Requirements

*   **Performance:** Model inference must execute in `<50ms`.
*   **ONNX Parity:** Prediction output variance between scikit-learn and ONNX Runtime must be $<0.01$.
*   **Qualcomm Compilation Ready:** Avoid custom python layers to ensure seamless translation to Snapdragon Hexagon NPU libraries.

---

## 7. Deliverables

*   Synthetic dataset generator.
*   Scikit-learn training code.
*   Compiled ONNX model file.
*   FastAPI inference endpoint.
*   Unit tests checking input shape limits.

---

## 8. Development Milestones

*   **Week 1:** Data generation script completed; CSV training data generated.
*   **Week 2:** Model training script completed; scikit-learn baseline evaluations validated.
*   **Week 3:** ONNX conversion completed; preprocessor parameters serialized.
*   **Week 4:** FastAPI prediction server and parity checking validated.

---

## 9. Dependencies & Module Boundaries

*   **What Depends On You:** Mithun (Core Backend forwards proxy requests to your API).
*   **Module Boundaries:** Do not modify code files inside `/backend`, `/dashboard`, `/face-recognition`, or `/hardware`.

---

## 10. Acceptance Criteria

*   ONNX prediction outputs are verified as functionally correct and match scikit-learn training predictions.
*   Unit tests execute with 100% pass rates.
*   Model latency remains below target.

---

## 11. Integration Checklist

- [ ] Confirm local FastAPI runs on port `8001`.
- [ ] Verify ONNX runtime outputs compile on host architectures.
- [ ] Confirm prediction results format matches Backend specs.
