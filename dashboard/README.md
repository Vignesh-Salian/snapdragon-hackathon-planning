# Module Owner Assignment: Frontend Dashboard

*   **Module Owner:** Shaun
*   **Module Name:** Frontend Dashboard UI

---

## 1. Module Overview

*   **Purpose:** Build a real-time web console displaying blood logistics, active alerts, AI prediction insights, and duplicate donor warnings.
*   **Scope:** React single-page dashboard application, charting components, state management, and WebSocket hooks.
*   **Success Criteria:** Telemetry dashboards update instantly, UI renders cleanly on various devices, and socket connection state handles disconnects gracefully.

---

## 2. Responsibilities

Shaun is responsible for designing, styling, and coding the React application using TypeScript and TailwindCSS. This includes drawing charts, managing local UI states, and listening to Mithun's WebSocket feed.

---

## 3. Repository Ownership

*   **Folder Scope:** `/dashboard`
*   **Components Owned:**
    *   `dashboard/src/components/*`
    *   `dashboard/src/hooks/useWebSocket.ts`
    *   `dashboard/src/pages/Home.tsx`
    *   `dashboard/src/services/api.ts`
    *   `dashboard/src/tests/*`

---

## 4. Functional Requirements

### Feature 1: Blood Inventory Dashboard
*   *Task:* Render grid cards showing blood types and active counts.
*   *Task:* Implement inventory adjustments modal form returning values to backend.

### Feature 2: Cold Box Telemetry Viewer
*   *Task:* Render time-series charts displaying temperature and acceleration logs.
*   *Task:* Trigger amber warning or red breach modals on incoming socket alerts.

### Feature 3: Biometric Lockout Modal
*   *Task:* Expose a critical screen pop-up when duplicate donor alerts are received.
*   *Task:* Display matching name, confidence metrics, and registration time.

---

## 5. Technical Responsibilities

### APIs to Consume
*   `GET http://127.0.0.1:8002/api/v1/inventory/{hospital_id}` -> Fetches blood levels.
*   `POST http://127.0.0.1:8002/api/v1/inventory/update` -> Updates inventory items.
*   `WebSocket ws://127.0.0.1:8002/ws/live` -> Listens for live telemetry and duplicate donor alerts.
*   **Gateway Proxy Calls (routes to internal modules through Hub):**
    *   `POST http://127.0.0.1:8002/api/v1/donor/enroll-delegate` -> Sends JSON payload (`{"name": "...", "image_b64": "..."}`) to enroll donors.
    *   `POST http://127.0.0.1:8002/api/v1/donor/verify-delegate` -> Sends JSON payload (`{"image_b64": "..."}`) to check for duplicate donor profiles.
    *   `POST http://127.0.0.1:8002/api/v1/predict/demand-delegate` -> Sends hospital metrics JSON payload to predict blood demand.

### Stream Payloads Handled
*   `TELEMETRY_UPDATE`: Modifies charts and cold-box card status.
*   `FRAUD_ALERT`: Triggers emergency lockout warning modal.

---

## 6. Non-Functional Requirements

*   **Performance:** UI updates must render within **50ms** of receiving socket messages.
*   **Design Aesthetics:** Premium slate/dark theme with glassmorphism panels. State color tags: Green = Safe, Amber = Warning, Red = Breach.
*   **Responsiveness:** Fluid grid structures scaling to Tablet, Desktop, and Presentation Mode.

---

## 7. Deliverables

*   React web project with TypeScript definitions.
*   Chart integrations displaying active sensor history.
*   WebSocket client connection hooks with auto-reconnection logic.
*   Isolated testing suite checking card rendering states.

---

## 8. Development Milestones

*   **Hours 00–06 (Phase 1: Structure & Charts):** Scaffold React application with TypeScript and Tailwind, and build mock charting panels.
*   **Hours 06–12 (Phase 2: WebSocket Binding):** Implement custom WebSocket client hooks and bind active dashboard updates to incoming packages.
*   **Hours 12–18 (Phase 3: Control & Alert Modals):** Build warning triggers, fraud modals, and inventory form connections.
*   **Hours 18–24 (Phase 4: Design Polish & Presentation):** Polish layout styles for presentation mode on tablets and perform end-to-end client checks.

---

## 9. Dependencies & Module Boundaries

*   **What You Depend On:** Mithun (Core Backend for database logs and WebSocket updates).
*   **Module Boundaries:** Do not modify backend code files under `/backend`, `/ai-engine`, `/face-recognition`, or `/hardware`.

---

## 10. Acceptance Criteria

*   Dashboard displays incoming mock telemetry stream values without lag.
*   Inventory stock cards match the backend database state.
*   Lockout modals trigger immediately on duplicate donor events.

---

## 11. Integration Checklist

- [ ] Confirm frontend boots on port `3000`.
- [ ] Verify local WebSocket connection to backend on port `8002` operates correctly.
- [ ] Confirm alert components render properly when receiving simulated alert JSON packages.
