# HemaGrid AI - AI Intelligence Module

This module handles predictive demand forecasting, shortage analysis, and inventory optimization alert generation. It uses a machine learning model trained on historical regional data (epidemiological cycles, weather, hospital profiles) and exports standard ONNX models optimized for Qualcomm Snapdragon NPU runtimes.

---

## 📂 Folder Structure

```text
ai-engine/
├── README.md                 # System architecture and model pipelines
├── datasets/
│   ├── generate_sample_data.py # Synthetic data generation script
│   └── sample_blood_data.csv # Generated training dataset
├── training/
│   └── train.py               # Model training and ONNX export pipeline
├── inference/
│   └── predict.py             # Inference API wrapper (FastAPI)
├── evaluation/
│   └── evaluate.py            # Model performance evaluation suite
├── tests/
│   └── test_model.py          # Integration validation checks
└── models/
    └── demand_predictor.onnx  # Compiled ONNX model weights
```

---

## 🧠 Model Architecture & Feature Engineering

The forecasting system uses a Multi-variable Regression Tree model (e.g., Random Forest or Gradient Boosting) to predict daily blood unit demand per hospital.

```text
Inputs:
  [ Hospital ID ] --------+
  [ Blood Type ] ---------+---> [ Feature Vector ] ---> [ Random Forest ] ---> Expected Demand (Units)
  [ Temperature ] --------+
  [ Dengue Outbreak Flag ]+
```

### Feature engineering details:
*   **Target Label:** `units_demanded` (Integer - number of blood units requested on a given day).
*   **Numerical Features:** `mean_temperature_c`, `humidity_pct`, `dengue_cases_weekly`.
*   **Categorical Features (One-Hot Encoded):** `hospital_type` (General, Emergency Trauma, Clinic), `blood_type` (A+, O-, etc.).
*   **Temporal Features:** `day_of_week`, `month`.

---

## 📡 Inference API Documentation

FastAPI runs the inference host. Below are the endpoint details:

### 1. Predict Daily Demand
Predicts the expected blood demand for a specific location.

* **URL:** `/api/v1/predict/demand`
* **Method:** `POST`
* **Content-Type:** `application/json`
* **Request Payload:**
  ```json
  {
    "hospital_id": 4,
    "hospital_type": "Trauma",
    "blood_type": "O_NEG",
    "temperature_c": 31.5,
    "dengue_cases_weekly": 145,
    "day_of_week": 5,
    "month": 7
  }
  ```
* **Response (Success - 200 OK):**
  ```json
  {
    "status": "success",
    "predictions": {
      "expected_demand_units": 18.4,
      "recommended_min_inventory": 25,
      "alert_level": "WARNING"
    }
  }
  ```

---

## 🛠 Setup & Development Flow

### Install Dependencies
```bash
pip install numpy pandas scikit-learn onnx onnxruntime fastapi uvicorn pydantic
```

### 1. Generate Synthetic Dataset
Before training, generate 1,000 historical record samples:
```bash
python datasets/generate_sample_data.py
```

### 2. Train and Export Model to ONNX
Run the training script to evaluate the Random Forest model and write the `.onnx` output:
```bash
python training/train.py
```

### 3. Run Inference API
```bash
uvicorn inference.predict:app --host 127.0.0.1 --port 8001 --reload
```

---

## 🧪 Testing Guide

Verify model shape parsing, inference outputs, and API routes:
```bash
python -m unittest tests/test_model.py
```

---

## 📋 Milestones & Acceptance Criteria

### Milestones
1.  **Milestone 1 (Dataset Setup):** Generate synthetic datasets matching target hospital distributions.
2.  **Milestone 2 (Training Core):** Establish training pipelines and measure baseline performance.
3.  **Milestone 3 (ONNX Export):** Export weights to ONNX format and verify parity between scikit-learn and ONNX runtime outputs.
4.  **Milestone 4 (Inference API):** Launch API and connect alert thresholds.

### Acceptance Criteria
*   The model must achieve an $R^2$ score of `> 0.70` on the validation dataset.
*   Inference response times using the ONNX model must remain below **50ms**.
*   The alert generator must raise `CRITICAL` warnings if predicted demand exceeds inventory by 25%+.
