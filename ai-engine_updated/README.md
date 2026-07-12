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

│

├── datasets/
│      generate_sample_data.py
│      blood_demand.csv
│
├── preprocessing/
│      preprocess.py
│
├── training/
│      train.py
│
├── evaluation/
│      evaluate.py
│
├── inference/
│      predict.py
│
├── models/
│      model.pkl
│      model.onnx
│
├── api/
│      routes.py
│
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

Train a Scikit-Learn regression model.

Recommended baseline:

- Random Forest Regressor

Optional comparison:

- XGBoost
- Gradient Boosting
- Extra Trees

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

## Feature 4 — ONNX Conversion

Convert trained pipeline using

```
skl2onnx
```

Requirements

- No custom operators
- Snapdragon compatible
- ONNX Runtime compatible

Prediction parity

```
Difference < 0.01
```

between

- Scikit-Learn
- ONNX Runtime

---

## Feature 5 — Prediction API

### Endpoint

```
POST /api/v1/predict/demand
```

### Request

```json
{
  "hospital_id":1,
  "hospital_type":"Trauma",
  "city_region":"Urban",
  "blood_type":"O+",
  "temperature_c":31.4,
  "rainfall_mm":112,
  "dengue_cases_weekly":52,
  "road_accidents":21,
  "emergency_cases":13,
  "scheduled_surgeries":9,
  "holiday":0,
  "blood_donation_camp":1,
  "current_inventory":80,
  "day_of_week":2,
  "month":7
}
```

### Response

```json
{
  "status":"success",
  "prediction":{
      "expected_demand_units":43,
      "recommended_inventory":60,
      "inventory_health_score":84,
      "alert_level":"SAFE"
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
Prediction

43 Units

Top Contributors

• High dengue cases
• Trauma hospital
• Increased emergency admissions
```

This improves transparency during hackathon demonstrations.

---

# 8. Non-Functional Requirements

Inference latency

```
< 50 ms
```

ONNX parity

```
< 0.01
```

Memory efficient

Compatible with Snapdragon X Elite

Ready for Qualcomm QAIRT compilation

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

### Week 1

- Dataset generation
- Data validation

### Week 2

- Training
- Hyperparameter tuning
- Evaluation

### Week 3

- ONNX conversion
- ONNX validation

### Week 4

- FastAPI APIs
- Backend integration
- Testing

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
- [ ] ONNX Runtime verified
- [ ] Prediction endpoint working
- [ ] Backend integration complete
- [ ] Dashboard receives predictions
- [ ] QAIRT compilation tested