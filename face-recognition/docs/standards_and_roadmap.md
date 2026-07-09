# Donor Verification Standards, Roadmap & Task List

This document lists developer tasks, coding guidelines, milestones, and future Qualcomm Snapdragon NPU optimizations for the HemaGrid AI Donor Verification module.

---

## 💻 Coding Guidelines

### FastAPI & API Code Rules
1.  **Request Parsing:** Use FastAPI's `UploadFile` and `Form` inputs for file multi-part uploads rather than raw JSON strings for images.
2.  **Explicit Exception Handling:** Throw HTTP exceptions using `HTTPException` with precise status codes:
    *   `400 Bad Request` for invalid media or missing faces.
    *   `409 Conflict` for duplicate donor registrations.
    *   `500 Internal Server Error` for storage crashes.
3.  **Concurrency Safety:** Keep SQLite transactions short and simple to prevent lock contention under concurrent uploads.

### Computer Vision (MediaPipe) Rules
1.  **Static Mode:** Run MediaPipe Face Mesh with `static_image_mode=True` for single-image uploads to prevent overhead tracking.
2.  **Resource Lifecycle:** Reuse the `FaceMesh` class instance rather than recreating it on every request.
3.  **No Image Cache Leakage:** Ensure decoded image buffers are garbage collected after landmark extraction.

---

## 📋 Developer Tasks

### API Submodule
*   [ ] Configure logging middleware to record API transaction latency.
*   [ ] Implement rate limiting on `/verify` to prevent brute-force landmark checking attacks.
*   [ ] Expose custom error payloads during network timeout conditions.

### Biometric Model Submodule
*   [ ] Add image pre-processing steps (contrast enhancement via CLAHE) to handle low-light registration desks.
*   [ ] Implement a 3D alignment step using facial landmarks before distance calculations.
*   [ ] Research and integrate cosine similarity as an alternative distance metric.

### Database Submodule
*   [ ] Add database migration tooling (Alembic) to handle future changes to donor metadata columns.
*   [ ] Build automated weekly backup routines to dump the `donors.db` SQLite file.
*   [ ] Add indexing to the `enrolled_at` column to optimize lockout window queries.

---

## 🚀 Qualcomm AI Snapdragon Optimization Roadmap

The current version runs MediaPipe Face Mesh on standard CPU runtimes. To optimize this module for Snapdragon-powered hardware (Mobile and AI PC):

```text
+-----------------------------------------------------------+
|               Qualcomm AI Stack Pipeline                  |
+-----------------------------┬-----------------------------+
                              │
  1. Export Model             v
  [ FaceMesh / FaceNet ] ---> ONNX Representation
                              │
  2. Qualcomm AI Hub          v
  [ Model Quantization ] ---> Quantized INT8 Model
                              │
  3. QAIRT SDK                v
  [ Compile to Hexagon ] ---> .elf / .so Library
                              │
  4. Local Edge Execution     v
  [ NPU Deployment ] --------> Direct Hardware Execution
+-----------------------------------------------------------+
```

1.  **Model Migration:** Move from MediaPipe Face Mesh to a dedicated Face Verification model like **FaceNet** or **MobileFaceNet** exported as an ONNX model.
2.  **Quantization via Qualcomm AI Hub:** Quantize the model (FP32 to INT8) using the Qualcomm AI Hub compiler to target Snapdragon Hexagon NPUs.
3.  **QAIRT SDK Compilation:** Compile the model using the **Qualcomm AI Engine Direct SDK (QAIRT)** to generate optimized binaries (`.elf` or `.so` libraries).
4.  **Local Execution Bridge:** Modify `models/detector.py` to run the compiled model via ONNX Runtime using the **QNN Execution Provider** (for Windows on Snapdragon) or SNPE (Snapdragon Neural Processing Engine) for Android devices, bypassing CPU and execution latency.
