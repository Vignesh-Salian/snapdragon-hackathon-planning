# HemaGrid AI — Project Reference

> The single source of truth for **what** we're building, **how** it fits together,
> **why** it wins, and **how fast** we can finish. For the hour-by-hour build/demo
> schedule see [`plan.md`](plan.md).

**One-line pitch:** *An edge-AI network that keeps donated blood safe and moving —
it watches every cold box for heat and shock, verifies donors on-device to stop
unsafe repeat donations, and forecasts hospital demand before shortages happen —
orchestrated live across an AI PC, a phone, and an Arduino, with zero cloud.*

---

## Table of contents
1. [Brutal review — read this first](#1-brutal-review)
2. [Winning strategy (mapped to judging)](#2-winning-strategy)
3. [Architecture](#3-architecture)
4. [System design & data flows](#4-system-design)
5. [Tech stack & software](#5-tech-stack--software)
6. [Hardware (bill of materials)](#6-hardware-bom)
7. [The AI models — datasets, train vs. convert, time](#7-ai-models)
8. [Repository structure](#8-repository-structure)
9. [Developer workflow](#9-developer-workflow)
10. [Finish-ASAP plan (ranked by ROI)](#10-finish-asap)
11. [Social impact](#11-social-impact)

---

<a name="1-brutal-review"></a>
## 1. Brutal review — read this first

We can change anything, so here is the unflinching version.

**What's genuinely strong (keep it):**
- **A real, emotional problem** with a physical, visible demo. Most teams will ship a phone-only LLM chat app. A multi-device system with a live cold box, a buzzer, and a dashboard turning red is *memorable* — that's Innovation (25%) and Presentation (15%).
- **True multi-device orchestration** — AI PC + phone + UNO Q behaving as one system. There is a **dedicated Multi-Device Orchestration prize**; almost nothing else in this project is as on-target for it.

**What will get us marked down — fix these:**
1. **The headline AI was a toy for an NPU hackathon.** The demand model is a tiny tabular MLP (15 numbers → 1 number): kilobytes of weights, microseconds on CPU. The Hexagon NPU adds *nothing* meaningful to it. Technical Implementation is **40%** and is explicitly about *NPU* performance/latency/resource use. Bringing only an MLP to an NPU contest is bringing a calculator to a GPU fight. **We need at least one substantial, verifiably-on-NPU model that is central to the story.**
2. **"Face recognition" via MediaPipe Face Mesh is scientifically wrong for identity.** Mesh landmarks encode *pose and geometry*, not *identity*. The same person at two angles can be farther apart than two different people at the same angle. A technical judge breaks the duplicate-donor claim in one question. **We need a real face-embedding model (identity vectors), not landmarks.**
3. **Five live services × three devices = high variance on the 20% "Deployment & stability" score.** A judge sees the crash, not the ambition. We must have a *bulletproof* minimum path and make everything else gracefully optional.

**The discipline that ties it together:** *one* impressive NPU model done well beats three mediocre ones. We do **not** bolt on every shiny model — we pick the single change with the highest combined ROI and make the rest graceful.

---

<a name="2-winning-strategy"></a>
## 2. Winning strategy (mapped to judging)

**Judging (confirmed):**

| Criterion | Weight | What it rewards |
|---|---|---|
| Technical Implementation | **40%** | NPU performance, latency, resource utilization, real on-device AI |
| Application Use-Case & Innovation | **25%** | Real problem, uniqueness, usefulness |
| Deployment & Accessibility | **20%** | Easy install, **stability during the demo**, edge-only |
| Presentation & Documentation | **15%** | Clear story, clean code + docs |
| **Multi-Device Orchestration** | **separate prize** | Multiple devices working as one coordinated system |

**The plan, in priority order:**

1. **Make face verification the headline NPU workload.** Replace Face Mesh landmarks with a real **face-embedding model (MobileFaceNet, ~3.9 MB, 128-dim identity vectors)**, INT8-quantized via Qualcomm AI Hub. This single change: (a) fixes the correctness bug, (b) creates a genuine vision NPU load for the 40%, and (c) is *central* to the story. **Highest-ROI move in the project.**

   ⚠️ **Decision you must make now (biggest scope fork in the plan) — WHERE does the model run?** Our `verification` service is Python/FastAPI and runs on the *PC*; "on the phone NPU" is a different, bigger piece of work:
   | Option | Effort | Orchestration prize | NPU for 40% |
   |---|---|---|---|
   | **A. PC hosts it** — MobileFaceNet ONNX on the X Elite Hexagon (QNN), keep the FastAPI service | **Low** (~2–4 h convert + wire) | ❌ phone drops out of the "multiverse" | ✅ still a real vision NPU load |
   | **B. Phone hosts it** — a **Kotlin/Android app** (ORT-Android / LiteRT) that runs the INT8 model and calls the gateway | **High** (a real app to build) | ✅ earns the phone in the orchestration story | ✅ true phone NPU |
   You **cannot** get "easy" *and* "phone in the demo." Pick before the event: if the orchestration prize is the goal, budget for **B**; if time is tight, ship **A** and still get the 40% credit. Also note: swapping in the real model means **recalibrating the duplicate-distance threshold** on a few real face pairs — the current `0.15` is tuned to the placeholder embedding only.
2. **Lean hard into orchestration.** The gateway on the AI PC is the conductor: it ingests the UNO Q's telemetry, brokers the phone's verification, serves the forecast, and streams everything to the dashboard live. Frame the demo as *one nervous system across three devices* — that's the separate orchestration prize and reinforces the 40%.
3. **Keep the demand MLP as a supporting analytic, not the NPU headline.** It's done, it's useful, it shows explainable-AI — but we stop pretending it's the NPU showcase. (We can still run it through QNN to say "even our tabular model is on-device.")
4. **Bulletproof the core path** for the 20%: `cold box (or simulator) → gateway → dashboard live`. Zero external services. Everything else degrades cleanly (delegates return 503, dashboard falls back to mock, simulator replaces hardware).
5. **Gemma LLM "Blood-Bank Copilot" = ONE clearly-labeled STRETCH, not core.** Honest truth: "an LLM that summarizes a dashboard" is the most bolted-on pattern at these events, it's a heavy *second* NPU load, and it's tangential to cold-chain. It earns a place **only** if the core is already bulletproof *and* we make it genuinely useful — natural-language **triage**: "given current inventory + forecast + a compromised box, what should the blood bank do right now?" running on LiteRT-LM on the NPU. If time is tight, cut it without regret.

> **Track note:** primary submission track is most likely **UNO Q → Real-Time Hardware & Sensing** (our strongest live story) or **Mobile → LiteRT Classical (Vision)** (the face-embedding NPU model). Confirm with the team.

---

<a name="3-architecture"></a>
## 3. Architecture

```text
        ┌──────────────────────────┐        ┌──────────────────────────────┐
        │   Arduino UNO Q (edge)   │        │   Snapdragon phone (edge)    │
        │  Modulino Thermo/Buzzer/ │        │  Face-embedding model        │
        │  Knob (+ Movement IMU)   │        │  (MobileFaceNet, INT8, NPU)  │
        └────────────┬─────────────┘        └───────────────┬──────────────┘
                     │ HTTP telemetry (LAN)                  │ HTTP verify (via gateway)
                     ▼                                       ▼
   ┌───────────────────────────  GATEWAY  (AI PC · FastAPI :8002)  ───────────────────────────┐
   │  inventory · telemetry ingest · WebSocket /ws/live · delegate proxies (CORS + routing)     │
   │  — the ORCHESTRATOR: every device talks only to the gateway, never to each other —         │
   └───────────────┬───────────────────────────────────────────────────┬───────────────────────┘
      WebSocket    │                                                     │ HTTP delegate
                   ▼                                                     ▼
       Dashboard (React, browser)                        Forecast engine (AI PC · :8001)
       live telemetry · alerts · XAI                     demand MLP → ONNX → Hexagon NPU (QNN)
                                                          [stretch] Gemma copilot (LiteRT-LM, NPU)
```

**Why this shape:** a single gateway means (1) the dashboard needs one URL, (2) no CORS mess, (3) each edge device is independent and replaceable, and (4) there is one clear "brain" to point at when explaining orchestration.

---

<a name="4-system-design"></a>
## 4. System design & data flows

**Services and ports**

| Service | Port | Owns | Runs on |
|---|---|---|---|
| **gateway** | 8002 | inventory, telemetry, `/ws/live`, delegate proxies, SQLite (WAL) | AI PC |
| **forecast** | 8001 | `/api/v1/predict/demand` (ONNX/QNN) + explainable-AI | AI PC |
| **verification** | 8000 | `/api/v1/donor/enroll` + `/verify` (face embedding) | phone (or AI PC fallback) |
| **dashboard** | 5173 | live UI | any browser on the LAN |
| **cold-box** | — | posts telemetry to gateway | UNO Q (or simulator anywhere) |

**Three core flows**

```text
1. Cold-chain:   UNO Q ──(HTTP telemetry)──► gateway ──(WebSocket)──► dashboard
2. Donor check:  dashboard ──► gateway /donor/verify-delegate ──► phone verification ──► 409 if duplicate
3. Forecast:     dashboard ──► gateway /predict/demand-delegate ──► forecast (NPU) ──► units + XAI
```

**Key contracts**
- **Telemetry** `POST /api/v1/telemetry/report`: `{device_id, uptime_ms, telemetry:{temperature, humidity, shock_g?}, status}` where status ∈ `SAFE|WARNING|COMPROMISED`. `shock_g` is nullable (present only with the Movement IMU).
- **Forecast** `POST /api/v1/predict/demand`: 15 model features (11 numeric + 4 categorical incl. `season`) + `current_inventory` → `{status, prediction:{expected_demand_units, recommended_inventory, inventory_health_score, alert_level}, top_contributors[]}`.
- **Verify** `POST /api/v1/donor/verify`: `{image_b64}` → `200 {duplicate_detected:false}` or **`409 {duplicate_detected:true, confidence, matched_donor, message}`**.

**Resilience (this is the 20%)**
- Delegates degrade to **503**, never a 500 crash, when the phone/forecast service is down.
- Dashboard has a **mock fallback** and an auto-reconnecting WebSocket with a "Connection Lost" banner.
- The cold box has a **software simulator** (`HEMAGRID_SIMULATE=1`) so the whole pipeline demos without any hardware.
- SQLite runs in **WAL** mode so telemetry writes and dashboard reads never lock each other.

---

<a name="5-tech-stack--software"></a>
## 5. Tech stack & software

| Layer | Choice | Notes |
|---|---|---|
| Gateway / services | **Python + FastAPI + Uvicorn** | Use **x64 Python** on the AI PC for QNN access |
| DB | **SQLite (WAL)** via SQLAlchemy (gateway), stdlib sqlite3 (verification) | edge-local, no server |
| On-device inference | **ONNX Runtime + QNN Execution Provider** (`onnxruntime-qnn`) | Hexagon NPU on the X Elite |
| Model conversion | **Qualcomm AI Hub** + **QAIRT** (ONNX → INT8 → QNN → context binary) | the real "NPU" work |
| Phone AI | **LiteRT / ONNX Runtime-Android**, model compiled INT8 via AI Hub for **SM8850** | face embedding (+ optional Gemma via LiteRT-LM) |
| Dashboard | **React + TypeScript + Vite + Recharts** | static build, runs in any browser |
| IoT | **Arduino App Lab** (Python on the QRB2210 MPU) + **Modulino** library over QWIIC/I²C | EdgeImpulse optional |
| LLM (stretch) | **Gemma-3 1B**, `.litertlm`, LiteRT-LM on the NPU | natural-language triage only |

**Software/tools to install on the AI PC:** Python 3.x (x64), `onnxruntime-qnn`, the AI Hub CLI/account, Node.js (dashboard), Arduino App Lab (for flashing the UNO Q), and the QAIRT SDK. **Verify the NPU is actually used** with `onnxruntime.get_ep_devices()` — do *not* trust `get_available_providers()` (it doesn't list QNN on ORT 2.x).

---

<a name="6-hardware-bom"></a>
## 6. Hardware (bill of materials)

**Provided by the organizers (only what we requested):**
- **AI PC** — *Surface Laptop 7, Snapdragon X Elite, 32 GB RAM, 512 GB SSD* (Hexagon NPU ~45 TOPS). Runs gateway + forecast (+ optional Gemma).
- **Phone** — *OnePlus 15, Snapdragon 8 Elite Gen 5 (SM8850, Hexagon v81)*. Runs face embedding on the NPU.
- **Arduino UNO Q (4 GB)** — Dragonwing **QRB2210** MPU (Debian) + **STM32U585** MCU.

> Organizer rule: teams receive **only the devices requested** and must **bring any other peripherals** themselves. Participants may also use their **own laptops** for development and use the Snapdragon devices for testing/demos.

**Modulino sensor kit (QWIIC/I²C daisy chain — no breadboard, no soldering):**
- **Modulino Thermo** — temperature + humidity (the core cold-chain metric)
- **Modulino Buzzer** — audible breach alarm
- **Modulino Knob** — sets the safe-temperature threshold live
- **Modulino Movement** *(buy/bring, ~$15)* — 6-axis IMU (LSM6DSOX) for **shock/impact**. Blood is damaged by mechanical shock as well as heat; this adds a second, independent hazard and a second demo beat. **Optional in software** — absent → `shock_g` is null and safety runs on temperature alone.

**Also bring:** a **USB-C Power Delivery** source (the UNO Q won't boot without it), QWIIC cables, and a small box/cooler prop for the physical demo. *(Optional stretch: a camera "Brick" on the UNO Q for a vision model — only if the core is bulletproof.)*

---

<a name="7-ai-models"></a>
## 7. The AI models — datasets, train vs. convert, time

**Critical distinction (this is also our finish-ASAP lever):** the impressive NPU models are **pretrained** — we do **not** train them. We download proven weights and **convert + INT8-quantize** them via AI Hub. The only thing we *train* is the tiny MLP (minutes). So we are **not blocked on training** — we're blocked on **conversion + integration**, which is compile/fiddle time.

| Model | Role | Data needed | Train or convert? | Time |
|---|---|---|---|---|
| **Demand MLP** | forecast (support) | **synthetic** `blood_demand.csv` (8k rows), schema-correct; *calibrate* distributions to real public data (see below) | **Train** (sklearn MLPRegressor) → skl2onnx → QNN INT8 | Train ~**minutes** (done, R²≈0.94). QNN quantize ~**1–2 h** |
| **Face embedding** | headline NPU | **none to train** — pretrained **MobileFaceNet** weights; plus ~a dozen **sample faces** (e.g. an LFW subset) *for the demo enrollment only* | **Convert** pretrained ONNX → AI Hub INT8 | **A (PC host):** ~2–4 h convert+wire · **B (phone Android app):** +a real app. *No training either way.* See the §2 fork. |
| **Gemma copilot** *(stretch)* | NL triage | none — pretrained `gemma-3-1b` `.litertlm` (Hugging Face LiteRT community) | **Download** prequantized → run on LiteRT-LM | ~**2–3 h** integration. *No training.* |

**Datasets — what we actually need:**
- **Demand (MLP):** no public dataset matches our 15-feature hospital-demand schema (the public "blood" datasets are *donor-retention*, a different task). So we keep the **schema-correct synthetic generator** but **calibrate its distributions to real public data** so it's defensible: Indian weather (IMD / Kaggle climate), dengue seasonality (NVBDCP/WHO), road-accident rates (MoRTH), and real ABO/Rh blood-group frequencies. Details + links: [`services/forecast/datasets/REAL_DATA_SOURCES.md`](services/forecast/datasets/REAL_DATA_SOURCES.md).
- **Face (embedding):** **not a training set** — MobileFaceNet is pretrained. We only need a **handful of real faces to enroll for the demo** (an LFW subset or the team's own faces). Verification then compares live embeddings against those.
- **Gemma:** none — pretrained weights.

**How to train the one model we train (MLP):**
```bash
cd services/forecast && pip install -r requirements.txt
python training/train.py            # ~minutes → models/pipeline.pkl (R² ≈ 0.94)
python onnx/convert_to_onnx.py      # → models/model.onnx
python onnx/verify_parity.py        # sklearn vs ONNX parity < 0.01
```

**How to take a pretrained model to the NPU (AI Hub / QAIRT):**
`pretrained ONNX/PyTorch → AI Hub compile (target SM8850 / X Elite) → INT8 static quantization with real calibration samples → QNN context binary → run via onnxruntime-qnn / LiteRT`. Budget hours, not days, and **verify the NPU** with `get_ep_devices()`.

---

<a name="8-repository-structure"></a>
## 8. Repository structure

Reorganized from the initial *per-person* folders into an **architecture-first** monorepo (ownership is people's business, not the directory tree's):

```text
hemagrid/
├── project.md          ← this file
├── plan.md             ← hour-by-hour hackathon roadmap + demo script
├── README.md · LICENSE (MIT)
├── services/           backend microservices (Python/FastAPI)
│   ├── gateway/            orchestrator hub — inventory, telemetry, /ws/live, proxies (:8002)
│   ├── forecast/           demand model + ONNX/QNN inference + XAI (:8001)
│   │   ├── datasets/ preprocessing/ training/ onnx/ inference/ evaluation/ models/ api/
│   └── verification/       donor face enroll/verify + SQLite store (:8000)
├── apps/
│   └── dashboard/          React + Recharts live UI (:5173)
└── edge/
    └── cold-box/           UNO Q App Lab: MPU Python daemon + simulator + schematics
```

Each module is self-contained (own `requirements.txt`/`package.json`, own tests) and talks to the others **only over HTTP/WS**, so any one can be developed, tested, or swapped independently.

---

<a name="9-developer-workflow"></a>
## 9. Developer workflow

**Local dev (no hardware, everything on one laptop):**
1. Start `gateway` (:8002), `forecast` (:8001), `verification` (:8000).
2. `npm run dev` the dashboard (:5173).
3. Run the cold-box **simulator**: `HEMAGRID_SIMULATE=1 BACKEND_URL=http://127.0.0.1:8002 python edge/cold-box/my_app/python/main.py`.
4. Watch the dashboard go live. Run tests per module with `pytest` / `npm run build`.

**On-device deploy (at the event):**
1. Gateway + forecast on the **X Elite**; convert the forecast (and face) models to **INT8/QNN** via AI Hub; verify NPU with `get_ep_devices()`.
2. Face verification on the **phone** (LiteRT/ORT-Android, INT8 MobileFaceNet); point it at the gateway delegate.
3. Flash the **UNO Q** in App Lab; QWIIC-chain the Modulinos; set `BACKEND_URL` to the laptop's **LAN IP** (never 127.0.0.1); stream real telemetry.
4. Put every device on the **same Wi-Fi**; end-to-end test all three flows.

**Git:** feature branches → PR → `main`. Keep the mono-repo edge-only and reproducible.

---

<a name="10-finish-asap"></a>
## 10. Finish-ASAP plan (ranked by ROI)

Do them **in this order** and stop wherever time runs out — each step is independently demoable.

| # | Task | Why (judging) | Status |
|---|---|---|---|
| 1 | **Bulletproof core**: sim/box → gateway → dashboard live | Deployment 20% + orchestration | ✅ built & verified |
| 2 | **Face embedding on NPU** (MobileFaceNet INT8, phone) | **Technical 40%** headline + fixes correctness | ⏳ convert (hrs) |
| 3 | **All-three-devices orchestration** live via gateway | **Orchestration prize** + Technical | ⏳ integrate on-site |
| 4 | **Forecast on NPU** (MLP → QNN INT8) + XAI in UI | Technical (smaller model) | ✅ model done, ⏳ QNN |
| 5 | **Physical box + Movement IMU** (thermal + shock beats) | Innovation 25% + demo wow | ✅ software ready, ⏳ hardware |
| 6 | **Docs + demo script + 3× dry-runs** | Presentation 15% | ⏳ continuous |
| 7 | **Gemma NL-triage copilot** | Innovation flair | 🔶 stretch only |

**What to focus on, by weight:**
- **40% Technical** → *one* real NPU model (face embedding), proven on-NPU via `get_ep_devices()`, low latency, INT8. This is where the marks are.
- **25% Innovation** → the dual-hazard (heat + shock) cold chain + biometric donor protection + predictive demand, tied to a real problem.
- **20% Deployment** → single-command services, edge-only, graceful degradation, simulator. Rehearse the *stable* path.
- **15% Presentation** → the live physical demo + polished dashboard + this doc + a crisp architecture diagram.
- **Orchestration prize** → tell the story as *one system across three devices*, conducted by the gateway.

---

<a name="11-social-impact"></a>
## 11. Social impact

Blood is one of the few things in medicine that cannot be manufactured — it can only be given, and it does not last. When it runs short, people die waiting: mothers in postpartum haemorrhage, trauma patients after a crash, children with severe anaemia. In much of India and the wider Global South, blood banks lurch between shortage and waste, because the system that connects donor, cold box, and hospital is still run on paper and guesswork.

HemaGrid attacks the three quiet failures in that chain.

**Blood that is silently spoiled.** A unit of blood that spends too long above ~6 °C, or is jolted hard in transit, can be destroyed while still looking perfectly fine in the bag. Today that damage is often invisible until it reaches a patient. Our cold box watches **temperature and shock continuously** and raises the alarm the moment a unit is compromised — so a bad unit is caught, not transfused, and a good unit is never thrown away "just in case."

**Donors quietly harmed.** Donating too often causes iron-deficiency anaemia; the safe interval exists for a reason. Paper registers make it trivial for someone to donate again too soon — sometimes out of desperation for the small incentives some centres offer. On-device face verification enforces the **56-day lockout without storing photos in the cloud**, protecting the donor's health *and* their privacy.

**Shortages that could have been seen coming.** Demand spikes are not random — dengue season fills wards with platelet needs, festival weekends empty donation camps, highways produce trauma cases. By **forecasting demand before it lands**, blood banks can move stock and call donors *ahead* of the shortage instead of scrambling during it.

Every part of this runs **on the edge, on-device** — which is not just a hackathon rule but the right design: rural blood banks and ambulances cannot depend on a reliable cloud connection, and health data this sensitive should not have to leave the building to be useful. The goal is simple and human: **fewer units wasted, fewer donors harmed, fewer patients waiting for blood that never comes.**
