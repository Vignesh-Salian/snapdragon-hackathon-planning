# HemaGrid AI

> **Smart, Connected Blood Logistics & Verification** — an edge-AI network for the
> Qualcomm Snapdragon Multiverse Hackathon.

HemaGrid AI monitors the blood cold chain, forecasts hospital demand, and blocks
duplicate donors — running **on-device across three Snapdragon form factors**
(AI PC + phone + Arduino UNO Q), with no cloud dependency.

---

## 👥 Team

> ⚠️ Teammates: replace the placeholder emails with your real ones — the
> hackathon requires **names + emails** in the README for prize eligibility.

| Member | Module | Email |
|---|---|---|
| **Mithun** | Backend Platform Hub | mithunmallya97@gmail.com |
| **Shaun** | Frontend Dashboard | `<add-email>` |
| **Tejas Nayak** | AI Intelligence (demand forecasting) | `<add-email>` |
| **Vignesh** | Donor Verification (face) | `<add-email>` |
| Hardware Team | Smart Cold Box (Arduino UNO Q) | `<add-email>` |

**License:** [MIT](./LICENSE) · **Edge execution:** every component runs locally
on-device; the only network traffic is LAN between the box, the laptop, and the
dashboard.

---

## 🏗 Architecture (multi-device = "multiverse")

```text
  Arduino UNO Q (Modulino)          Snapdragon 8 Elite phone
  Thermo · Buzzer · Knob            MediaPipe/LiteRT face mesh (NPU)
        │ HTTP telemetry                     │ HTTP (via gateway)
        ▼                                     ▼
  ┌─────────────────────────  Core Backend Hub (FastAPI, :8002)  ─────────────────────────┐
  │   inventory · telemetry · WebSocket /ws/live · delegate proxies (CORS gateway)          │
  └───────────────┬───────────────────────────────────────────────┬────────────────────────┘
        WebSocket │                                                 │ HTTP delegate
                  ▼                                                 ▼
        Dashboard (React, browser)                        AI Engine (ONNX/QNN NPU, :8001)
                                                          demand forecast + XAI
```

| Device | Runs | Snapdragon target |
|---|---|---|
| **AI PC** | Backend hub + AI demand engine (ONNX Runtime + QNN EP) | Snapdragon X Elite (Hexagon, 45 TOPS) |
| **Phone** | Donor face verification (MediaPipe → LiteRT INT8) | OnePlus 15 · Snapdragon 8 Elite Gen 5 (SM8850) |
| **IoT** | Smart Cold Box telemetry | Arduino UNO Q · Dragonwing QRB2210 + STM32U585 |

---

## 🚀 Quick start

Each module runs independently. **You do not need the hardware** — a built-in
cold-box simulator drives the full pipeline.

```bash
# 1) Gateway hub (:8002)
cd services/gateway && pip install -r requirements.txt && python run.py

# 2) Forecast engine (:8001) — first build the model, then serve
cd services/forecast && pip install -r requirements.txt
python training/train.py && python onnx/convert_to_onnx.py
python main.py

# 3) Donor verification (:8000)
cd services/verification && pip install -r requirements.txt && python api/main.py

# 4) Dashboard (:5173)
cd apps/dashboard && npm install && npm run dev

# 5) Cold box — real hardware:   cd edge/cold-box/my_app/python && python main.py
#    ...or no hardware (demo):    HEMAGRID_SIMULATE=1 BACKEND_URL=http://127.0.0.1:8002 \
#                                 python edge/cold-box/my_app/python/main.py
```

Then open the dashboard → watch live telemetry, forecasts, and fraud alerts.

### Tests
```bash
cd services/gateway && pytest       # 8 passed
cd services/forecast && pytest      # model + prediction
cd services/verification && pytest  # enroll / verify / duplicate / no-face
cd edge/cold-box && pytest          # cold-box state logic
```

---

## 📂 Structure

```text
services/   backend microservices
  gateway/        FastAPI hub (:8002) — inventory, telemetry, /ws/live, delegate proxies
  forecast/       demand forecaster → ONNX → Hexagon NPU (QNN EP) + explainable-AI (:8001)
  verification/   donor face verification, SQLite donor store, 56-day lockout (:8000)
apps/
  dashboard/      React + Recharts live monitoring UI (:5173)
edge/
  cold-box/       Arduino UNO Q + Modulino Thermo/Buzzer/Knob (+ optional Movement IMU) + simulator
```

See **[`project.md`](project.md)** for the full architecture, system design, tech stack,
datasets, model-training/conversion, social impact, and winning strategy — and
**[`plan.md`](plan.md)** for the hour-by-hour hackathon execution roadmap + demo script.
