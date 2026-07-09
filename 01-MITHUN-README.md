# Module Owner Assignment: Backend Platform

*   **Module Owner:** Mithun
*   **Module Name:** Backend Platform Hub

---

## 1. Module Overview

*   **Purpose:** Build the central orchestration hub for HemaGrid AI to manage data tables, ingest hardware telemetry, broker WebSocket streams, and route request/response sequences between subsystems.
*   **Scope:** Backend application routing, database models, WebSocket brokers, and HTTP proxy clients.
*   **Success Criteria:** Zero data corruption on write sequences, WebSocket broadcasts completing under 100ms, and complete coverage of API interface contracts.

---

## 2. Responsibilities

Mithun is responsible for designing, developing, and deploying the centralized FastAPI application. This includes SQLite database management, WebSocket streaming, and client wrappers to communicate with Vignesh's and Tejas's services.

---

## 3. Repository Ownership

*   **Folder Scope:** `/backend`
*   **Files Owned:**
    *   `backend/api/main.py`
    *   `backend/database/models.py`
    *   `backend/services/ai_client.py`
    *   `backend/services/face_client.py`
    *   `backend/websocket_hub/manager.py`
    *   `backend/tests/test_backend.py`

---

## 4. Functional Requirements

### Feature 1: Inventory REST API
*   *Task:* Implement endpoints to fetch stock levels and add/remove blood units per hospital.
*   *Task:* Validate inventory increments to ensure stock never drops below zero.

### Feature 2: Telemetry Logger & Adaptor
*   *Task:* Build route to ingest telemetry from the Smart Cold Box.
*   *Task:* Log sensor readings (temperature, impact G-force) into SQLite.
*   *Task:* Trigger WebSocket broadcast payload immediately upon packet arrival.

### Feature 3: Biometric & AI Delegate Proxies
*   *Task:* Implement async HTTP clients to request donor duplicate checks from Vignesh's service.
*   *Task:* Implement async HTTP clients to request demand predictions from Tejas's service.

---

## 5. Technical Responsibilities

### APIs to Expose
*   `GET /api/v1/inventory/{hospital_id}` -> Fetches blood levels.
*   `POST /api/v1/inventory/update` -> Body: `{hospital_id, blood_type, units_added_removed}`.
*   `POST /api/v1/telemetry/report` -> Body: `{device_id, uptime_ms, telemetry, status}`.
*   `WebSocket /ws/live` -> Stream dashboard updates.

### APIs to Consume
*   `POST http://127.0.0.1:8000/api/v1/donor/verify` (Vignesh's module)
*   `POST http://127.0.0.1:8001/api/v1/predict/demand` (Tejas's module)

---

## 6. Non-Functional Requirements

*   **Performance:** Telemetry database write sequence must take `<30ms`.
*   **Reliability:** Auto-reconnect handlers for database pools; graceful API error mappings.
*   **Documentation:** Expose OpenAPI Swagger schema documentation on startup.

---

## 7. Deliverables

*   FastAPI application configured with CORS.
*   SQLAlchemy models generating SQLite tables.
*   WebSocket manager broadcasting data packets.
*   Async integration tests showing complete mocks of external microservices.

---

## 8. Development Milestones

*   **Week 1:** Initialize folder, configure SQLAlchemy, and pop data templates.
*   **Week 2:** Complete WebSocket Connection Manager.
*   **Week 3:** Connect async proxies to Vignesh's and Tejas's local services.
*   **Week 4:** Verify multi-device broadcasts and prepare mock tests.

---

## 9. Dependencies & Module Boundaries

*   **What You Depend On:** Vignesh (Face Verification API) and Tejas (AI Engine API).
*   **What Depends On You:** Shaun (Dashboard UI fetches data and listens to your WebSockets).
*   **Module Boundaries:** Do not modify code files inside `/dashboard`, `/ai-engine`, `/face-recognition`, or `/hardware`.

---

## 10. Acceptance Criteria

*   SQLite database tables are successfully generated on startup.
*   Test suites execute with 100% pass rates.
*   WebSocket broadcasts successfully distribute JSON payloads to all connected clients.

---

## 11. Integration Checklist

- [ ] Confirm local FastAPI runs on port `8002`.
- [ ] Verify database schema tables exist inside `hemagrid.db`.
- [ ] Verify proxy endpoints route queries correctly under mock API environments.
