# Work Assignment: Donor Verification

*   **Module Owner:** Vignesh
*   **Module Name:** Biometric Donor Validation Engine
*   **Objective:** Develop a local computer vision pipeline to extract face landmarks, cache donor profiles, detect duplicate donor registrations, and expose the logic via a REST API.

---

## 1. Why This Module Exists

Safe donations require tracking donor frequencies to protect health and block illegal blood brokers. Processing face checks locally at registration desks prevents double registrations even under unstable internet conditions.

---

## 2. Responsibilities & Folders Owned

*   **Repository Folder:** `/face-recognition`
*   **Primary Tasks:**
    *   Integrate MediaPipe Face Mesh model.
    *   Construct biometric feature extractor.
    *   Build local SQLite profile storage.
    *   Expose FastAPI route for verification.

---

## 3. Features to Implement

1.  **Face Landmark Extractor:** Decodes raw image bytes and processes them using MediaPipe Face Mesh to get 468 landmarks (biometric topological embedding).
2.  **Biometric Database:** Schema to store name, time of enrollment, and landmarks array in a local SQLite file.
3.  **Duplicate Detector:** Vector comparison engine using Euclidean distance to compare input face meshes with recent records.
4.  **REST API:** Route handlers to enroll and check donor duplicate status.

---

## 4. Detailed Task Checklist

- [ ] Create folder structure under `/face-recognition` including `api`, `models`, `database`, `docs`, and `tests`.
- [ ] Initialize MediaPipe Face Mesh module in `models/detector.py`.
- [ ] Implement Euclidean distance comparison method inside `detector.py`.
- [ ] Write SQLite connection wrapper and create `donors` table schemas in `database/db.py`.
- [ ] Write DB helper to retrieve recent donors within the standard 56-day lockout window.
- [ ] Write the FastAPI app `api/main.py` exposing `/enroll` and `/verify` endpoints.
- [ ] Implement error checking (e.g. raise `HTTPException 400` if no face is detected in uploaded photo).
- [ ] Write mock test suite using TestClient to verify duplicate detection without requiring physical cameras.

---

## 5. Interface Specifications

### APIs to Expose
*   `POST /api/v1/donor/enroll` -> Payload: `name` (form field), `image` (file upload).
*   `POST /api/v1/donor/verify` -> Payload: `image` (file upload).
*   **Response (Duplicate Flagged):**
    ```json
    {
      "duplicate_detected": true,
      "confidence": "float",
      "matched_donor": {
        "id": "integer",
        "name": "string",
        "enrolled_at": "string"
      },
      "message": "string"
    }
    ```

---

## 6. Coding & Documentation Standards

*   **Language & Tech:** Python, MediaPipe, OpenCV, SQLite, FastAPI, NumPy.
*   **Coding Conventions:**
    *   Reuse the MediaPipe model instance context across requests; do not instantiate on every call.
    *   Store landmark coordinates as serialized JSON strings in SQLite database.
    *   Format floating-point outputs to 2 decimal places.

---

## 7. Testing Responsibilities

*   Create comprehensive test cases inside `tests/test_api.py`.
*   Mock face model outputs (e.g. static float arrays) to assert endpoint behaviors.
*   Validate that non-face images are rejected with appropriate error messages.

---

## 8. Weekly Milestones

*   **Week 1:** MediaPipe integration verified. Single-image landmark extraction functional.
*   **Week 2:** SQLite database schema and lookup functions validated.
*   **Week 3:** FastAPI endpoints established. Verification logic return schemas verified.
*   **Week 4:** Unit tests completed. Parity check runs without errors.

---

## 9. Dependencies & Constraints

*   **Modules Depending on Your Work:** Mithun (Core Backend proxies validation requests to your API).
*   **Things NOT to Modify:** Do not modify directories outside `/face-recognition`.
*   **Verification Target:** Comparison requests must complete in `<300ms` for a db size of 1,000 donors.
