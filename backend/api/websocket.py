"""
WebSocket endpoint for real-time deepfake detection alerts.

Manages WebSocket connections and broadcasts alert messages
when new detections are made or network activity is flagged.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """Manages active WebSocket connections for real-time alerts."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send a message to a specific client."""
        await websocket.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for real-time alerts.

    Clients connect here to receive live notifications when:
    - A new deepfake is detected
    - Coordinated network activity is flagged
    - A claim is verified as false
    """
    await manager.connect(websocket)
    try:
        # Send welcome message
        await manager.send_personal(websocket, {
            "type": "connection",
            "message": "Connected to Deepfake Detection alert stream",
        })

        # Keep connection alive and listen for client messages
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Echo acknowledgment
                await manager.send_personal(websocket, {
                    "type": "ack",
                    "message": f"Received: {data}",
                })
            except asyncio.TimeoutError:
                # Send heartbeat
                await manager.send_personal(websocket, {"type": "heartbeat"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
