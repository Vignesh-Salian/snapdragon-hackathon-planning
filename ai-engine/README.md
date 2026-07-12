# Module Owner Assignment: AI Intelligence

**Module Owner:** Tejas Nayak  
**Module Name:** Predictive Blood Demand Forecasting & Inventory Intelligence Engine

---

# 1. Module Overview

## Purpose

Develop an AI-powered blood demand forecasting engine capable of predicting future blood requirements for hospitals using historical demand trends, environmental conditions, hospital characteristics, and emergency indicators.

The trained model will be exported to ONNX format for deployment on Qualcomm Snapdragon platforms using ONNX Runtime and QNN Execution Provider.

The module will also generate inventory recommendations and risk alerts to help blood banks maintain safe blood reserves.

---

# 2. Objectives

The AI Engine should:

- Predict daily blood demand
- Recommend minimum inventory levels
- Generate inventory risk alerts
- Run inference using ONNX Runtime
- Support Snapdragon Hexagon NPU deployment
- Expose prediction APIs for backend integration

---

# 3. Responsibilities

Tejas is responsible for:

- Designing and generating synthetic datasets
- Building data preprocessing pipelines
- Training regression models
- Model evaluation
- ONNX model conversion
- FastAPI inference APIs
- Prediction validation
- Unit testing

---

# 4. Repository Ownership

```
ai-engine/
├── datasets/
│      generate_sample_data.py
│      blood_demand.csv
├── preprocessing/
│      preprocess.py
├── training/
│      train.py
├── evaluation/
│      evaluate.py
├── inference/
│      predict.py
├── models/
│      model.pkl
│      model.onnx
├── api/
│      routes.py
└── tests/
       test_model.py
```

---

# 5. Functional Requirements

## Feature 1 — Synthetic Dataset Generator

Generate 5,000–10,000 realistic hospital transaction records.

Each record represents one hospital's blood demand for one day.

### Dataset Features

| Feature | Description |
|----------|-------------|
| hospital_id | Hospital identifier |
| hospital_type | General / Trauma / Clinic |
| city_region | Urban / Semi-Urban / Rural |
| blood_type | O+, A+, B+, AB+, O-, etc. |
| day_of_week | 1–7 |
| month | 1–12 |
| season | Summer / Monsoon / Winter |
| temperature_c | Daily temperature |
| rainfall_mm | Rainfall |
| dengue_cases_weekly | Weekly dengue count |
| road_accidents | Accident cases |
| emergency_cases | Daily emergencies |
| scheduled_surgeries | Planned surgeries |
| holiday | Yes/No |
| blood_donation_camp | Yes/No |
| current_inventory | Current stock |
| expected_demand_units | Target variable |

Dataset relationships should simulate realistic healthcare scenarios rather than random values.

Examples:

- Higher dengue → Higher platelet demand
- More road accidents → Higher trauma blood demand
- Festivals → Reduced donation camps
- Trauma hospitals → Higher emergency demand

---

## Feature 2 — Data Preprocessing

Implement preprocessing pipeline for

- Missing values
- Label Encoding
- One-Hot Encoding
- Feature Scaling (where required)

Pipeline must be reusable during inference.

---

## Feature 3 — Model Training

Train a regression model compatible with Hexagon NPU acceleration (avoiding tree ensembles like Random Forest or XGBoost which are unsupported by the QNN Execution Provider and will fall back to CPU).

Recommended baseline:

- Scikit-Learn MLPRegressor (Multi-Layer Perceptron) or a PyTorch Neural Network

Optional comparison:

- Simple Feed-Forward Neural Network (using PyTorch or Keras)
- Ridge/Linear Regression (for low latency)

Target

```
expected_demand_units
```

Evaluation Metrics

- R² Score
- MAE
- RMSE

Target Accuracy

```
R² > 0.75
```

---

## Feature 4 — Model Export & Compiling

Convert the trained scikit-learn pipeline to ONNX format using `skl2onnx` (or to LiteRT `.tflite` format).

Requirements:
- **NPU Compatibility:** No custom operators. Ensure all layers are compatible with the Hexagon NPU. Note: Tree-based ensemble operators (e.g. `TreeEnsembleRegressor` from Random Forest or XGBoost) are unsupported by the QNN execution provider and will fall back to CPU. Use neural network models (like Multi-Layer Perceptron).
- **Quantization:** Quantize the model to **INT8** using Qualcomm AI Hub or `onnxruntime.quantization.quantize_static`. Quantizing to INT8 is mandatory to run on Snapdragon NPUs; FP32 models will silently fall back to CPU.
- **Calibration Data:** Use 10-100 real validation data samples during the quantization calibration pass. Do not use random noise.
- **Inference Runtime:** Execute predictions using `onnxruntime` with the **QNN Execution Provider** (`QNNExecutionProvider` referencing the `QnnHtp.dll` / `libQnnHtp.so` backend library).
- **Power Configuration:** Configure the session to use the `balanced` power profile for single interactive inference requests.

Prediction parity:
```
Difference < 0.01
```
between scikit-learn and NPU/ONNX runtime.

---

## Feature 5 — Prediction API

### Endpoint

```
POST /api/v1/predict/demand
```

### Request

```json
{
  "hospital_id": 1,
  "hospital_type": "Trauma",
  "city_region": "Urban",
  "blood_type": "O+",
  "temperature_c": 31.4,
  "rainfall_mm": 112,
  "dengue_cases_weekly": 52,
  "road_accidents": 21,
  "emergency_cases": 13,
  "scheduled_surgeries": 9,
  "holiday": 0,
  "blood_donation_camp": 1,
  "current_inventory": 80,
  "day_of_week": 2,
  "month": 7
}
```

### Response

```json
{
  "status": "success",
  "prediction": {
    "expected_demand_units": 43,
    "recommended_inventory": 60,
    "inventory_health_score": 84,
    "alert_level": "SAFE"
  }
}
```

---

# 6. Inventory Intelligence

Using predicted demand and current inventory, generate

### Inventory Recommendation

```
Recommended Inventory =
Predicted Demand × Safety Factor
```

### Alert Levels

SAFE

Inventory > 130% demand

WARNING

Inventory between 100–130%

CRITICAL

Inventory below predicted demand

---

# 7. Explainable AI

The prediction service should expose the most influential features contributing to the prediction.

Example

```
Prediction: 43 Units
Top Contributors:
• High dengue cases
• Trauma hospital
• Increased emergency admissions
```

This improves transparency during hackathon demonstrations.

---

# 8. Non-Functional Requirements

*   **Inference Latency:** `< 50 ms` under local CPU/NPU execution.
*   **ONNX/LiteRT Parity:** Output difference between scikit-learn and NPU runtime must be `< 0.01`.
*   **NPU Execution Verification:** Program verification checks in python using `get_ep_devices()` to verify the execution provider is active. Do not trust `onnxruntime.get_available_providers()` as it does not list QNN EP in version 2.x.
*   **Target Platform:** Snapdragon X Elite (Hexagon v73 NPU, 45 TOPS).
*   **Quantization Mode:** Mandatory static INT8 quantization mapping. FP32 models will silently fall back to CPU execution.
*   **Memory Efficiency:** Quantized ONNX weights under 5MB footprint.

---

# 9. Deliverables

- Synthetic dataset generator
- Training pipeline
- Preprocessing pipeline
- Model evaluation
- ONNX model
- FastAPI prediction server
- Unit tests
- Documentation

---

# 10. Development Milestones

### Hours 00–06 (Phase 1: Data & Training)
- Dataset generation and validation.
- Pipeline pre-processing and training MLP Neural Network baseline model.

### Hours 06–12 (Phase 2: ONNX Compilation)
- ONNX model conversion and validation.
- Parity checking between scikit-learn and ONNX.

### Hours 12–18 (Phase 3: Prediction API)
- FastAPI prediction server implementation.
- Explainable AI (top feature contributors) integration.

### Hours 18–24 (Phase 4: Integration & QA)
- Backend integration verification.
- Target latency (<50ms) validation and unit testing.

---

# 11. Dependencies

Backend depends on this module.

Output API must strictly follow agreed JSON schema.

Do not modify

- backend/
- dashboard/
- hardware/
- face-recognition/

---

# 12. Acceptance Criteria

✓ Dataset generated successfully

✓ Model R² > 0.75

✓ ONNX conversion successful

✓ ONNX parity verified

✓ Inference latency <50ms

✓ API passes unit tests

✓ Backend integration successful

✓ Snapdragon deployment ready

---

# 13. Integration Checklist

- [ ] FastAPI running on port 8001
- [ ] ONNX Runtime QNN Execution Provider verified via `get_ep_devices()` (prints `True`)
- [ ] Prediction endpoint working with 15-field request payload
- [ ] Backend integration complete (routes proxy demand-delegate queries)
- [ ] Dashboard receives predictions and renders Explainable AI (XAI) contributors
- [ ] QAIRT/AI Hub compilation tested and outputting INT8 quantized models using real calibration data
