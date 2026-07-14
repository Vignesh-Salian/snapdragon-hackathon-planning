# Gateway — Orchestrator Hub

Central FastAPI service (port **8002**). The one "brain" every device talks to:
it ingests cold-box telemetry, brokers donor verification and demand forecasts,
and streams everything to the dashboard. Nothing talks device-to-device.

## Responsibilities
- **Inventory** — blood levels per hospital (never drops below zero).
- **Telemetry** — ingest cold-box frames → persist (SQLite, WAL) → broadcast.
- **Live stream** — `WebSocket /ws/live` fan-out to dashboards.
- **Delegate proxies** — CORS gateway to the forecast (:8001) and verification
  (:8000) services; degrade to **503** (never crash) when they're down.

## Endpoints
```
GET  /api/v1/inventory/{hospital_id}
POST /api/v1/inventory/update            {hospital_id, blood_type, units_added_removed}
POST /api/v1/telemetry/report            {device_id, uptime_ms, telemetry{...}, status}
WS   /ws/live
POST /api/v1/donor/enroll-delegate       → verification :8000
POST /api/v1/donor/verify-delegate       → verification :8000
POST /api/v1/predict/demand-delegate     → forecast :8001
```

## Run / test
```bash
pip install -r requirements.txt
python run.py          # http://127.0.0.1:8002  (Swagger at /docs)
pytest                 # 8 passed
```

See [`../../project.md`](../../project.md) for the full architecture and contracts.
