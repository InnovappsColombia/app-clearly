"""
CLEARLY — WebSocket Connection Manager
Provides real-time room-based synchronization for Senior Titulars and Family Tutors.
Supports collaborative checklists, instant deadline alerts, and duress decoupling.
"""

from typing import Any, Dict, List
from uuid import UUID
from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    def __init__(self):
        # Maps senior_id (UUID or str) -> List[WebSocket]
        self.active_rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, senior_id: str):
        await websocket.accept()
        if senior_id not in self.active_rooms:
            self.active_rooms[senior_id] = []
        self.active_rooms[senior_id].append(websocket)
        logger.info(
            f"WebSocket client connected to Senior room '{senior_id}'. Total clients: {len(self.active_rooms[senior_id])}"
        )

    def disconnect(self, websocket: WebSocket, senior_id: str):
        if senior_id in self.active_rooms:
            if websocket in self.active_rooms[senior_id]:
                self.active_rooms[senior_id].remove(websocket)
            if not self.active_rooms[senior_id]:
                del self.active_rooms[senior_id]
        logger.info(f"WebSocket client disconnected from Senior room '{senior_id}'")

    async def broadcast_to_room(self, senior_id: str, message: Dict[str, Any]):
        """Broadcasts a JSON message to all clients connected to senior_id room."""
        clients = self.active_rooms.get(senior_id, [])
        if not clients:
            logger.debug(f"No active WebSocket clients for room '{senior_id}' to broadcast: {message.get('type')}")
            return

        dead_connections = []
        for connection in clients:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error broadcasting to client in room '{senior_id}': {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead, senior_id)

    async def broadcast_action_toggle(self, senior_id: str, action_data: Dict[str, Any]):
        """Broadcasts when a checklist action is checked or unchecked."""
        await self.broadcast_to_room(
            senior_id,
            {
                "type": "ACTION_UPDATED",
                "data": action_data,
            },
        )

    async def broadcast_critical_alert(self, senior_id: str, alert_data: Dict[str, Any]):
        """Broadcasts proactive critical deadline alerts to Tutor and Senior."""
        await self.broadcast_to_room(
            senior_id,
            {
                "type": "CRITICAL_ALERT",
                "data": alert_data,
            },
        )

    async def broadcast_new_document(self, senior_id: str, document_data: Dict[str, Any]):
        """Broadcasts when a new document has been processed."""
        await self.broadcast_to_room(
            senior_id,
            {
                "type": "NEW_DOCUMENT",
                "data": document_data,
            },
        )


ws_manager = ConnectionManager()

