# Module Owner Assignment: Donor Verification

*   **Module Owner:** Vignesh
*   **Module Name:** Biometric Donor Validation Engine

---

## 1. Module Overview

*   **Purpose:** Develop a local computer vision pipeline to extract face landmarks, cache donor profiles, detect duplicate donor registrations, and expose the logic via a REST API to prevent donor fraud.
*   **Scope:** MediaPipe Face Mesh integration, local SQLite profile storage, duplicate check logic, and API endpoints.
*   **Success Criteria:** Zero false negatives on identical faces, comparison request latency under 300ms, and clean error handling for non-face images.

---

## 2. Responsibilities

Vignesh is responsible for integrating MediaPipe Face Mesh, building the Euclidean distance comparison algorithm, setting up the local SQLite donor profile database, and writing the FastAPI service endpoint wrapper.

---

## 3. Repository Ownership

*   **Folder Scope:** `/face-recognition`
*   **Files Owned:**
    *   `face-recognition/api/main.py`
    *   `face-recognition/database/db.py`
    *   `face-recognition/models/detector.py`
    *   `face-recognition/tests/test_api.py`
    *   `face-recognition/docs/standards_and_roadmap.md`

---

## 4. Functional Requirements

### Feature 1: Face Landmark Extractor
*   *Task:* Decode input image bytes and process them using MediaPipe Face Mesh.
*   *Task:* Extract standard 468 landmark coordinates (flat array of 1404 floats).

### Feature 2: Local SQLite profile storage
*   *Task:* Define DB schemas to store names, enrollment times, and landmarks.
*   *Task:* Retrieve recent enrollments within the clinical 56-day lockout window.

### Feature 3: Similarity Matching
*   *Task:* Implement Euclidean distance calculations to compare input face meshes.
*   *Task:* Flag duplicate donor matches if the distance drops below the 0.15 threshold.

---

## 5. Technical Responsibilities

### APIs to Expose
*   `POST /api/v1/donor/enroll` -> Payload: `name` (form field), `image` (file upload).
*   `POST /api/v1/donor/verify` -> Payload: `image` (file upload).
*   **Response Format (409 Conflict - Duplicate Flagged):**
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

## 6. Non-Functional Requirements

*   **Performance:** Verification requests must complete in `<300ms` for 1,000 donor records.
*   **Reliability:** Return `400 Bad Request` if no face is found in the photo.
*   **Scalability:** SQLite indexing on `enrolled_at` column to speed up lookup requests.

---

## 7. Deliverables

*   FastAPI application.
*   MediaPipe Face Mesh extractor.
*   Local database schemas.
*   Unit tests mocking face mesh arrays.

---

## 8. Development Milestones

*   **Week 1:** MediaPipe integration verified; single-image landmark extraction functional.
*   **Week 2:** SQLite database schemas and query lookups validated.
*   **Week 3:** FastAPI endpoints established; duplicate verification response format validated.
*   **Week 4:** Unit tests completed.

---

## 9. Dependencies & Module Boundaries

*   **What Depends On You:** Mithun (Core Backend proxies validation requests to your API).
*   **Module Boundaries:** Do not modify code files inside `/backend`, `/dashboard`, `/ai-engine`, or `/hardware`.

---

## 10. Acceptance Criteria

*   Image uploads without faces are rejected with HTTP 400.
*   Identical faces trigger duplicate donor matches (HTTP 409).
*   Tests pass with 100% success rate.

---

## 11. Integration Checklist

- [ ] Confirm local FastAPI runs on port `8000`.
- [ ] Confirm database creates `donors.db` file correctly.
- [ ] Verify image post-request payload formats match backend specifications.
