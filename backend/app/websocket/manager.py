from typing import List, Dict, Any
from fastapi import WebSocket
from app.core.logging import logger
import json


class ConnectionManager:
    """Manages active WebSocket connections for streaming real-time simulation telemetry."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcasts a JSON-serializable message to all connected clients."""
        payload = {
            **message,
            "is_simulated": True,
        }
        text_data = json.dumps(payload)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(text_data)
            except Exception as e:
                logger.warning(f"Error broadcasting to client, removing: {e}")
                self.disconnect(connection)


ws_manager = ConnectionManager()
