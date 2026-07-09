"""
manager.py
HemaGrid AI - WebSocket Connection Broker

Tracks active WebSocket client connections and manages real-time telemetry
broadcasts to coordination dashboards.
"""

from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # List of active WebSocket client connections (dashboards/alerts consoles)
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"WebSocket client disconnected. Remaining connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        """
        Transmits JSON payload to all active listeners. Removes inactive sockets.
        """
        disconnected_sockets = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Connection might have dropped without calling disconnect()
                disconnected_sockets.append(connection)

        # Cleanup dead sockets
        for socket in disconnected_sockets:
            self.disconnect(socket)
