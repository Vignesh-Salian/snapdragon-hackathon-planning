# Verification — Donor De-duplication

Donor face verification service (port **8000**). Prevents unsafe over-frequent
donations by flagging a returning donor inside the clinical **56-day lockout**.

## How it works
- Extract a face **embedding**, compare (Euclidean) against donors enrolled in the
  last 56 days; a match below the threshold ⇒ duplicate (**HTTP 409**).
- **Today:** a dependency-light deterministic fallback embedding so the service
  runs and tests pass anywhere.
- **Target (headline NPU workload):** a real **MobileFaceNet** identity model,
  INT8-quantized via Qualcomm AI Hub, running on the **phone's Hexagon NPU**
  (SM8850). Face-mesh landmarks are *not* identity — this fixes that.
  ⚠️ When you swap in MobileFaceNet, **recalibrate `DUPLICATE_THRESHOLD`** — real
  embedding distances are on a different scale than the fallback's.

## Endpoints
```
POST /api/v1/donor/enroll   {name, image_b64}
POST /api/v1/donor/verify   {image_b64}
 → 200 {duplicate_detected:false}  |  409 {duplicate_detected:true, confidence, matched_donor, message}
 → 400 if no face found
```

## Run / test
```bash
pip install -r requirements.txt
python api/main.py     # :8000
pytest                 # enroll / duplicate-409 / verify / no-face-400
```
See [`../../project.md`](../../project.md) §2 & §7 for the NPU strategy.
