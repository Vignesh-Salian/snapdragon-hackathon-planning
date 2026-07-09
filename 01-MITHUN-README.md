# Work Assignment: Core Backend

*   **Module Owner:** Mithun
*   **Module Name:** Core Backend Hub
*   **Objective:** Build a central orchestrator that manages hospital inventories, logs telemetry, exposes REST/WebSocket connections, and acts as the integration gateway.

---

## 1. Why This Module Exists

No edge device acts alone in the HemaGrid AI system. The Core Backend acts as the single source of truth and communication broker, aggregating sensor telemetry from the cold boxes and proxying requests to the AI demand predictor and face verification services.

---

## 2. Responsibilities & Folders Owned

*   **Repository Folder:** `/backend`
*   **Primary Tasks:**
    *   Expose blood inventory database CRUD routes.
    *   Ingest serial telemetry and log sensor records.
    *   Implement WebSocket broadcast channel.
    *   Proxy queries to the AI and Face modules.

---

## 3. Features to Implement

1.  **Inventory REST APIs:** Set, fetch, and update blood unit quantities per hospital and blood type.
2.  **WebSocket Stream (`/ws/live`):** Establish connection endpoints, track dashboard listeners, and push real-time telemetry updates.
3.  **Telemetry Logger:** Ingest cold box payloads, persist logs to SQLite, and forward broadcasts.
4.  **Microservice Proxies:** Communicate with `/face-recognition` and `/ai-engine` API hosts using async clients.

---

## 4. Detailed Task Checklist

- [ ] Create folder structure under `/backend` with standard FastAPI layouts.
- [ ] Initialize SQLAlchemy engine and declare schema tables (`hospitals`, `inventory`, `shipment_logs`).
- [ ] Write DB population script for sample hospital profiles.
- [ ] Build WebSocket Connection Manager to handle active client sockets.
- [ ] Write inventory update endpoints `/api/v1/inventory/update`.
- [ ] Write telemetry intake endpoint `/api/v1/telemetry/report`.
- [ ] Implement proxy service `face_client.py` for multipart photo verification queries.
- [ ] Implement proxy service `ai_client.py` for predictive demand requests.
- [ ] Expose FastAPI OpenAPI Swagger documentation.

---

## 5. Interface Specifications

### APIs to Expose
*   `GET /api/v1/inventory/{hospital_id}` -> Fetches blood levels.
*   `POST /api/v1/inventory/update` -> Body: `{hospital_id, blood_type, units_added_removed}`.
*   `POST /api/v1/telemetry/report` -> Body: `{device_id, uptime_ms, telemetry, status}`.
*   `WebSocket /ws/live` -> Pushes real-time dashboard updates.

### APIs to Consume
*   `POST http://127.0.0.1:8000/api/v1/donor/verify` (Vignesh's module)
*   `POST http://127.0.0.1:8001/api/v1/predict/demand` (Tejas's module)

---

## 6. Coding & Documentation Standards

*   **Language & Tech:** Python, FastAPI, SQLAlchemy, SQLite, Uvicorn.
*   **Coding Conventions:**
    *   Keep database session lifecycle within endpoints using dependencies (`get_db`).
    *   Use relative imports within `/backend/api/`.
    *   Keep routes clean; delegate database queries to `/backend/database/` operations.
*   **Documentation:** Expose complete docstrings for every routing handler and connection manager helper.

---

## 7. Testing Responsibilities

*   Write comprehensive test suites inside `/backend/tests/test_backend.py`.
*   Mock outgoing HTTP requests to Vignesh's and Tejas's services using unit test libraries (e.g. `unittest.mock.patch`).
*   Validate inventory updates do not drop below zero.

---

## 8. Weekly Milestones

*   **Week 1:** SQLite database tables declared, and mock inventory update routes functional.
*   **Week 2:** WebSocket connection manager implemented. Broadcast loops tested via mock clients.
*   **Week 3:** Outgoing HTTP clients integrated with local mock APIs of Vignesh and Tejas.
*   **Week 4:** Integration testing, error-handling validation, and API parity checks completed.

---

## 9. Dependencies & Constraints

*   **Modules Depending on Your Work:** Shaun (Dashboard relies on your REST inventory APIs and WebSockets).
*   **Modules You Depend On:** Vignesh (Face Verification API) and Tejas (AI Engine API).
*   **Things NOT to Modify:** Do not change folders outside `/backend` without PR approvals.

---

## 10. Acceptance Criteria

*   Inventory queries return in `<50ms` on SQLite.
*   Telemetry broadcasts route to all active WebSocket listeners within `100ms` of packet ingestion.
*   The database correctly persists telemetry logs and updates inventories without race conditions.
