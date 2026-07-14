# HemaGrid AI — Hackathon Master Plan

> **Team:** Mithun (Backend) · Shaun (Dashboard) · Tejas (AI Engine) · Vignesh (Face) · Hardware Team (Cold Box)
> **Event:** Qualcomm Snapdragon Multiverse Hackathon (24h on-site)
> **Strategy:** build the software **now**, so on-site is assembly + NPU + demo, not coding.

---

## 1. Is this project good? — Yes, with one caution

| Criteria | Rating | Notes |
|---|---|---|
| Problem relevance | ⭐⭐⭐⭐⭐ | Blood supply chain — real, high-impact, healthcare + social good |
| Multi-device fit | ⭐⭐⭐⭐⭐ | AI PC + phone + Arduino UNO Q = literally "multiverse". Uses **3** devices (needed ≥2) |
| Technical ambition | ⭐⭐⭐⭐⭐ | On-device NPU (QNN), ONNX/LiteRT, real sensors — hits every scoring box |
| Architecture | ⭐⭐⭐⭐ | Clean gateway + microservices, strict API contracts, parallel-buildable |
| Feasibility | ⭐⭐⭐⭐ | Software is now **built & tested**; on-site risk is NPU compile + hardware only |

**The one honest caution — over-scoped for the "stability" score (20%).** Five
interdependent live systems across three devices means five things that can crash
in front of a judge, who sees the crash, not the ambition. **Mitigation:** we
defined a *minimum bulletproof demo path* (§6) that works with zero external
services, and made everything else gracefully optional. That discipline is
already coded — delegates return 503 (never crash), the dashboard falls back to
mock, and a software cold-box simulator replaces the hardware if it misbehaves.

---

## 2. Team status — what's built (all verified on Linux)

Everything below is **written, runnable, and test-passing today** — this is the
whole point: on-site we copy-paste and integrate, we don't write from scratch.

| Module | Owner | Status | Evidence |
|---|---|---|---|
| **Backend hub** (:8002) | Mithun | ✅ Built | 7/7 tests: inventory (no negative stock), telemetry→WS broadcast, graceful 503 |
| **AI engine** (:8001) | Tejas | ✅ Built | MLP trained (MAE 2.1), ONNX exported, live `/predict` returns demand + XAI |
| **Face verification** (:8000) | Vignesh | ✅ Built | 5/5 tests: enroll, duplicate→409, verify, no-face→400 |
| **Dashboard** (:5173) | Shaun | ✅ Wired | `api.ts` + WS adapter to backend; `npm run build` clean |
| **Smart Cold Box** | Hardware | ✅ Built | MPU daemon + simulator; sim→backend integration verified (6 frames, SAFE→COMPROMISED) |

**Fixes applied vs. the original spec:**
- **RandomForest → MLPRegressor** — trees can't run on the Hexagon NPU (QNN has no `TreeEnsembleRegressor`); MLP does. Numerics now scaled for the MLP.
- **`season` was missing** from the documented request but is a required model feature — added to the API + clients.
- **Hardware re-scoped to the provided kit** — see §5.
- **Eligibility gaps closed** — added `LICENSE` (MIT) + team names/emails in the README (both are hard prize requirements that were missing).

---

## 3. Rules that actually gate us (from the official guide)

- **Eligibility:** GitHub repo + detailed README + **team names & emails** + **open-source license** + **most components run on-device.** ✅ all satisfied now.
- **Judging:** Technical Implementation 40% (*performance/latency/**NPU** resource use*) · Innovation 25% · Deployment 20% (*ease of install + **stability during demos***) · Presentation 15%.
- **NPU is explicitly scored** → INT8 quantization is mandatory; FP32 silently falls back to CPU. Verify with `get_ep_devices()`, not `get_available_providers()`.

**Track choice (team must confirm):** HemaGrid spans platforms, so pick the primary
submission track — most likely **Arduino UNO Q → "Real-Time Hardware & Sensing"**
(our strongest live story) or **AI PC → "Classical Models via AI Hub"** (the demand
NPU model). One line to decide; doesn't block anything.

---

## 4. THE ROADMAP — pre-build now, 12h on-site, then present

### Phase A — Pre-hackathon (NOW) — ✅ DONE
All five modules coded, integrated on `localhost`, and tested. Demo runs today
with the simulator. Nothing here should need writing on-site.

### Phase B — On-site build (target ≤ 12h of the 24) — the irreducible work
This is the part that **cannot** be pre-built because it needs the real Snapdragon
hardware, the phone, and the physical box.

| Hour | Task | Fallback if it slips |
|---|---|---|
| **H0–H1** | Pull repo on the X Elite laptop; `pip`/`npm install` all modules; boot backend + AI + face + dashboard; confirm **sim → backend → dashboard** live | Already works today — should be quick |
| **H1–H3** | **NPU compile on X Elite:** `onnxruntime-qnn`; QAIRT **INT8** quantize `model.onnx` with real calibration rows → QNN convert → Context BIN; wire QNN EP; verify `get_ep_devices()` = NPU | CPU ONNX (already working) — still a valid, fast demo |
| **H3–H5** | **Phone:** compile face mesh to LiteRT INT8 (AI Hub, SM8850); run donor verify on-device, point it at the backend delegate | Run face service on the laptop CPU (already working) |
| **H5–H7** | **Arduino:** flash UNO Q via App Lab; QWIIC-chain Modulino Thermo/Buzzer/Knob; run MPU `main.py` posting **real** telemetry over LAN; buzzer on breach | Software simulator (already working) |
| **H7–H9** | **LAN integration:** set `BACKEND_URL` to laptop IP on every device; full round-trips — box→backend→dashboard, dashboard→predict(NPU), dashboard→verify(phone) | Degrade any leg to its fallback; pipeline still shows |
| **H9–H11** | Harden + calibrate thresholds; reconnect testing; **assemble the physical cold box** | — |
| **H11–H12** | Freeze code; final backup/commit | — |

### Phase C — Presentation prep (the remaining ~12h) — the reason we pre-built
Slides + architecture diagram · demo script (§6) · **3× full dry-runs** · README
screenshots · rest before judging. *This buffer only exists because Phase A is
done — that's the whole strategy.*

---

## 5. Hardware — provided kit ONLY

**Base kit:** Arduino **UNO Q (4GB)** · **Modulino Thermo** (temp/humidity) ·
**Modulino Buzzer** (alarm) · **Modulino Knob** (threshold). All QWIIC/I²C —
daisy-chained, no breadboard, no soldering. (DHT22 + ADXL345 plan dropped.)

**Recommended add-on — Modulino Movement (6-axis IMU, ~$15):** blood is damaged
by mechanical **shock** as well as heat, so the box should watch both hazards.
It's QWIIC → clips into the same chain, no rewiring. `shock_g` is **optional** in
code: fitted → a hard knock trips COMPROMISED and the buzzer sounds; not fitted →
`shock_g` is `null` and safety runs on temperature alone (graceful).

- Thermal states: SAFE ≤ 6 °C · WARNING ≤ 8 °C · COMPROMISED > 8 °C. Impact:
  COMPROMISED when shock ≥ 2 g. The **Knob** shifts the temp threshold live.
- USB-C **Power Delivery required** or the board won't boot.

---

## 6. Minimum bulletproof demo path + script

**Bulletproof core (must never fail):** `cold box (or simulator) → backend → dashboard live update`.
Zero external services needed. Everything else layers on top and degrades cleanly.

**Demo script:**
1. Dashboard shows **"Connection Lost"** (stale banner already built).
2. Power on the cold box → audience watches it go **LIVE** in real time. *(power move)*
3. Open the box / warm the Thermo → temp climbs → **WARNING → COMPROMISED**, **buzzer sounds**, dashboard turns red.
4. **Knock the box** (Modulino Movement) → shock spike → COMPROMISED again — a *second, independent* hazard (mechanical, not thermal). Shows the box protects blood on two axes.
5. Run a **demand forecast** → dashboard shows predicted units + **explainable-AI** top contributors (running on the **NPU**).
6. Scan the same donor twice → **duplicate donor 409** → fraud modal.
7. Close with `get_ep_devices()` on screen proving inference ran on the **Hexagon NPU**, not CPU.

---

## 7. Risk register

| Risk | Sev | Mitigation → Fallback |
|---|---|---|
| NPU compile mismatch on-site | 🔴 | Test QAIRT early (H1) → CPU ONNX already works |
| Arduino/Modulino issues | 🟡 | Pre-test wiring → software simulator (built, verified) |
| Cross-machine LAN/CORS | 🟡 | Single backend gateway (built) → localhost demo |
| Face latency / mediapipe on phone | 🟡 | LiteRT INT8 → laptop CPU face service (built) |
| A live service crashes mid-demo | 🟡 | Delegates 503 + dashboard mock fallback (built) → stick to §6 core |
| Model accuracy weak | 🟢 | MLP MAE ~2 units; calibrate synthetic data to real distributions (`ai-engine/datasets/REAL_DATA_SOURCES.md`) |

---

## 8. Immediate next actions

1. **Teammates:** add your real emails to the README (eligibility).
2. **Team:** confirm the submission **track** (§3).
3. **Push** `main` to origin (merges + built modules) — *ask Mithun first.*
4. On-site: follow §4 Phase B.
