# HemaGrid AI - Donor Verification (Face Recognition Module)

This module handles secure donor enrollment and fraud prevention for HemaGrid AI. It uses local computer vision pipelines to extract face landmarks, cache donor profiles, and detect over-frequent donations (double-donating within a short time frame) via a REST API.

---

## 📂 Folder Structure

```text
face-recognition/
├── README.md                 # Module documentation and API specifications
├── docs/
│   └── standards_and_roadmap.md # Task list, coding guidelines, and future Qualcomm NPU path
├── api/
│   └── main.py                # FastAPI application endpoints
├── database/
│   └── db.py                  # Local SQLite storage wrapper for donor embeddings
├── models/
│   └── detector.py            # MediaPipe face landmark extraction logic
└── tests/
    └── test_api.py            # API endpoint integration test suite
```

---

## 🏗 System Architecture

```text
[ Donor Registration App ]
          │
          │ POST /enroll (Image, Name)
          v
+─────────────────────────────────────────+
|         FastAPI REST Endpoint           |
+────────────────────┬────────────────────+
                     │
                     v
+─────────────────────────────────────────+
|     MediaPipe Landmark Extractor        |
+────────────────────┬────────────────────+
                     │
                     v
+─────────────────────────────────────────+
|  Local SQLite DB (Vector Landmark Sync) |
+─────────────────────────────────────────+
```

1. **Image Ingestion:** The client registration app uploads a raw image byte stream.
2. **Face Landmarks & Extraction:** MediaPipe Face Mesh processes the image, detects the face, and isolates 468 landmark coordinates (acting as a unique biometric topology/embedding).
3. **Similarity Querying:** The API queries recent donor records from the local SQLite database. Landmarks are compared using normalized Euclidean distance.
4. **Fraud Detection Decision:** If a match is found under the threshold (0.15 normalized distance) within the lockout window (e.g., 56 days), the transaction is flagged as a duplicate.

---

## 🗄 Database Schema

The system uses SQLite to store metadata and vector topology local array caches.

### `donors` Table
| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **id** | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique enrollment key |
| **name** | VARCHAR(255) | NOT NULL | Registered name of the donor |
| **enrolled_at**| TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date and time of the registration |
| **landmarks** | TEXT | NOT NULL | JSON string representation of the 468 coordinates |

---

## 📡 API Documentation

FastAPI exposes swagger docs at `/docs`. Below are the core API specifications.

### 1. Enroll Donor
Enrolls a new donor and saves their face signature.

* **URL:** `/api/v1/donor/enroll`
* **Method:** `POST`
* **Content-Type:** `multipart/form-data`
* **Payload:**
  * `name` (string): Donor's full name
  * `image` (binary): Raw PNG/JPG face image
* **Response (Success - 200 OK):**
  ```json
  {
    "status": "success",
    "donor_id": 12,
    "message": "Donor successfully enrolled"
  }
  ```

### 2. Verify / Check Duplicate
Checks whether a donor has registered previously within the database.

* **URL:** `/api/v1/donor/verify`
* **Method:** `POST`
* **Content-Type:** `multipart/form-data`
* **Payload:**
  * `image` (binary): Raw PNG/JPG face image
* **Response (No Duplicate Found - 200 OK):**
  ```json
  {
    "duplicate_detected": false,
    "confidence": 0.0,
    "message": "No matching donor record found. Safe to proceed."
  }
  ```
* **Response (Duplicate Flagged - 409 Conflict):**
  ```json
  {
    "duplicate_detected": true,
    "confidence": 0.94,
    "matched_donor": {
      "id": 8,
      "name": "Jane Doe",
      "enrolled_at": "2026-07-09T14:12:00Z"
    },
    "message": "Fraud Alert: Donor registered recently."
  }
  ```

---

## 🛠 Installation & Setup

### Prerequisites
* Python 3.8 to 3.11
* OpenCV native build dependencies

### Install Dependencies
```bash
pip install fastapi uvicorn mediapipe opencv-python numpy python-multipart
```

### Run Server Local Dev
```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🧪 Testing Guide

To run local integration checks on endpoints:
```bash
python -m unittest tests/test_api.py
```

---

## 📋 Milestones & Acceptance Criteria

### Milestones
1. **Milestone 1 (Detection Pipeline):** Establish working MediaPipe Face Mesh model loading.
2. **Milestone 2 (Database CRUD):** Complete SQLite schemas and serialization for coordinate matrices.
3. **Milestone 3 (API Interface):** Build FastAPI routing.
4. **Milestone 4 (Integration):** Verify that mock face images are correctly evaluated and duplicated donor scenarios are blocked.

### Acceptance Criteria
* Face detection must fail gracefully with `400 Bad Request` if no face is detected in the uploaded image.
* Comparison latency must remain below **300ms** for a database size of 1,000 donors.
* False acceptance rate (duplicate flagged for different people) must remain below 1.5% under normalized parameters.
