# Forecast — Demand Intelligence

Blood-demand forecasting service (port **8001**). Predicts expected units for a
hospital/day from 15 features (weather, dengue, accidents, emergencies, blood
type, season…), plus inventory recommendations and explainable-AI contributors.

## Model
- **MLPRegressor** (not a tree ensemble — trees can't run on the Hexagon NPU),
  numerics scaled, exported to **ONNX**, run via **ONNX Runtime + QNN EP**
  (Hexagon NPU) with CPU fallback. NPU verified with `get_ep_devices()`.
- Test R² ≈ 0.94. This is a *supporting* analytic — see `project.md` for why the
  headline NPU workload is the face-embedding model, not this.

## Endpoint
```
POST /api/v1/predict/demand
 → {status, prediction:{expected_demand_units, recommended_inventory,
                        inventory_health_score, alert_level}, top_contributors[]}
```

## Build / run / test
```bash
pip install -r requirements.txt
python training/train.py            # ~minutes → models/pipeline.pkl
python onnx/convert_to_onnx.py      # → models/model.onnx
python onnx/verify_parity.py        # sklearn vs ONNX parity < 0.01
python main.py                      # serve on :8001
pytest
```
Datasets & real-data calibration: [`datasets/REAL_DATA_SOURCES.md`](datasets/REAL_DATA_SOURCES.md).
See [`../../project.md`](../../project.md) §7 for train-vs-convert details.
