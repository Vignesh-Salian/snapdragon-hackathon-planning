# HemaGrid AI - Core Backend Service

The Core Backend acts as the central orchestrator and integration hub for the HemaGrid AI multiverse ecosystem. It manages hospital blood inventory records, coordinates REST API requests between the Donor Verification and AI Intelligence modules, and provides real-time telemetry streaming via WebSockets.

---

## 📂 Folder Structure

```text
backend/
├── README.md                 # System overview and deployment guidelines
├── docs/
│   ├── contracts.md           # Structural payload contracts between subsystems
│   └── openapi.json           # OpenAPI (Swagger) specifications
├── api/
│   └── main.py                # FastAPI central application configuration
├── database/
│   └── models.py              # SQLite schemas and database operations
├── services/
│   ├── ai_client.py           # HTTP client interface to the AI Engine
│   └── face_client.py         # HTTP client interface to Face Verification
├── websocket_hub/
│   └── manager.py             # WebSocket broker for live dashboard updates
└── tests/
    └── test_backend.py        # Core integration test suite
```

---

## 🏗 System Architecture & Integration Points

The core backend acts as the single point of coordination:

```text
                               +----------------------------+
                               |     React Dashboard        |
                               +--------------▲-------------+
                                              │ WebSocket: Live streams
                                              v
+------------------------+     +----------------------------+     +------------------------+
|   Smart Cold Box (MCU) |---->|     Core Backend Host      |<--->|   AI Engine Module     |
|   (Serial-to-WS bridge)|     |     - FastAPI Server       |     |   - Demand Predictions |
+------------------------+     |     - SQLite Database      |     +------------------------+
                               +--------------▲-------------+
                                              │ HTTP JSON Client
                                              v
                               +----------------------------+
                               |  Face Verification Engine  |
                               +----------------------------+
```

---

## 🔌 Interface Contracts

To prevent merge conflicts during development, all modules adhere to the schemas defined in [docs/contracts.md](file:///C:/Users/Vignesh/snapdragon-hackathon-planning/backend/docs/contracts.md). 

### Summary of Contracts:
*   **Hardware to Backend:** Standard JSON telemetry payloads containing temperature, shock, and system flags.
*   **Backend to Face Verification:** Multi-part images uploaded for duplicate checks; returns binary match decision and confidence score.
*   **Backend to AI Engine:** JSON vector inputs containing environmental, temporal, and outbreak metrics; returns expected daily demand.
*   **Backend to Dashboard:** Structured state broadcasts containing current inventory levels, telemetry logs, and active alert notifications.

---

## 🗄 Database Design

The database stores metadata for hospitals, live blood inventories, and cold box shipping logs.

### `hospitals` Table
| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **id** | INTEGER | PRIMARY KEY | Unique hospital identifier |
| **name** | VARCHAR(255) | NOT NULL | Registered clinic name |
| **hospital_type**| VARCHAR(50) | NOT NULL | Type profile: General, Trauma, Clinic |

### `inventory` Table
| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **hospital_id** | INTEGER | FOREIGN KEY | References `hospitals.id` |
| **blood_type** | VARCHAR(10) | NOT NULL | Blood type classification |
| **units_available**| INTEGER | DEFAULT 0 | Count of ready units in stock |

### `shipment_logs` Table
| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| **id** | INTEGER | PRIMARY KEY | Unique log identifier |
| **device_id** | VARCHAR(50) | NOT NULL | Cold Box hardware ID |
| **temperature** | FLOAT | NOT NULL | Recorded internal temp |
| **max_impact** | FLOAT | NOT NULL | Maximum G-force shock |
| **state** | VARCHAR(20) | NOT NULL | SAFE, WARNING, COMPROMISED |

---

## 📡 Core API Specification

### Blood Inventory Management
*   **GET `/api/v1/inventory/{hospital_id}`:** Retrieves current inventory levels by blood type.
*   **POST `/api/v1/inventory/update`:** Updates stock levels (used when blood is donated or consumed).

### Telemetry Intake
*   **POST `/api/v1/telemetry/report`:** Ingests cold box metrics, stores shipment logs, and triggers WebSocket broadcasts.

### WebSockets Stream
*   **WebSocket `/ws/live`:** Real-time channel for dashboard clients to receive active telemetry frames.

---

## 🛠 Installation & Setup

### Install Dependencies
```bash
pip install fastapi uvicorn sqlalchemy httpx pydantic
```

### Run Server Local Dev
```bash
uvicorn api.main:app --host 127.0.0.1 --port 8002 --reload
```

---

## 🧪 Testing Strategy

Tests validate routes, local database updates, and mock responses for the AI/Face engines:
```bash
python -m unittest tests/test_backend.py
```
