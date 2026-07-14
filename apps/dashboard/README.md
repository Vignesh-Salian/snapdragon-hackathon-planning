# Dashboard — Live Monitoring UI

React + TypeScript + Vite + Recharts dashboard (port **5173**). Real-time cold-box
telemetry, inventory, demand forecasts (with explainable-AI), and donor fraud
alerts — one glass-dark control room.

## Data
- **REST** (`src/services/api.ts`) → the gateway (`:8002`) for inventory, demand
  (via `predict/demand-delegate`), and donor verification.
- **WebSocket** (`src/hooks/useWebSocket.ts`) → `ws://<gateway>/ws/live`; adapts
  the gateway's telemetry frames to the UI. Auto-reconnect + "Connection Lost"
  banner; falls back to a mock stream so the UI always renders.
- Gateway base URL is configurable via `VITE_API_URL`.

## Run / build
```bash
npm install
npm run dev      # http://127.0.0.1:5173
npm run build    # type-checks + production build
```

See [`../../project.md`](../../project.md) for the full architecture.
