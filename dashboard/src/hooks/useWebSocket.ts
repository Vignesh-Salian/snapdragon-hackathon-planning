import { useState, useEffect, useRef } from "react";
import type { WSMessage, WSTelemetryPayload, DonorVerifyResponse } from "../types";

export interface UseWebSocketOptions {
  url?: string;
  useMock?: boolean;
}

/**
 * Custom React hook to manage WebSocket connection to HemaGrid telemetry live feed.
 * Supports auto-reconnection and a swappable mock simulation mode for local development.
 */
export function useWebSocket({
  url = "ws://127.0.0.1:8002/ws/live",
  useMock = false,
}: UseWebSocketOptions = {}) {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (useMock) {
      // Mock Simulator Mode
      setConnected(true);
      setLastMessage(null);

      // Emulate telemetry streams every 3s
      const telemetryInterval = setInterval(() => {
        const coldBoxIds = ["CB-014", "CB-021", "CB-009", "CB-033"];
        const randomId = coldBoxIds[Math.floor(Math.random() * coldBoxIds.length)];
        const telemetryPayload: WSTelemetryPayload = {
          device_id: randomId,
          temp: parseFloat((3.5 + Math.random() * 5).toFixed(1)),
          batt: Math.floor(Math.random() * 40) + 60,
          accel: parseFloat((Math.random() * 0.4).toFixed(2)),
        };
        setLastMessage({
          type: "TELEMETRY_UPDATE",
          payload: telemetryPayload,
        });
      }, 3000);

      // Emulate face-recognition duplicate donor lockout trigger occasionally
      const fraudInterval = setInterval(() => {
        const matchCase: DonorVerifyResponse = {
          duplicate_detected: true,
          confidence: parseFloat((90 + Math.random() * 9).toFixed(1)),
          matched_donor: {
            id: 201 + Math.floor(Math.random() * 100),
            name: ["Sarah Connor", "John Doe", "Jane Smith", "Anita R."][Math.floor(Math.random() * 4)],
            enrolled_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString(),
          },
          message: "Potential duplicate donor detected on verification proxy.",
        };
        setLastMessage({
          type: "FRAUD_ALERT",
          payload: matchCase,
        });
      }, 25000);

      return () => {
        clearInterval(telemetryInterval);
        clearInterval(fraudInterval);
        setConnected(false);
      };
    }

    // Real Connection Mode
    function connect() {
      if (wsRef.current) return;

      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          if (parsed && (parsed.type === "TELEMETRY_UPDATE" || parsed.type === "FRAUD_ALERT")) {
            setLastMessage(parsed as WSMessage);
          }
        } catch (err) {
          console.error("Error parsing WebSocket message data:", err);
        }
      };

      ws.onclose = () => {
        setConnected(false);
        wsRef.current = null;
        // Schedule auto-reconnection
        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, 5000);
      };

      ws.onerror = () => {
        ws.close();
      };
    }

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close();
        wsRef.current = null;
      }
      setConnected(false);
    };
  }, [url, useMock]);

  return { connected, lastMessage };
}
export default useWebSocket;
