"""
CLEARLY — Real-Time WebSocket Hub Endpoint
Provides bidirectional real-time synchronization for Senior and Tutor collaborative sessions.
"""

from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from app.services.connection_manager import ws_manager
from app.services.tutor_engine import tutor_engine

router = APIRouter()


@router.websocket("/ws/tutors/{senior_id}")
async def tutor_hub_websocket_endpoint(websocket: WebSocket, senior_id: str):
    """
    WebSocket channel for real-time Tutor Hub synchronization.
    Clients receive instant broadcasts when:
      - A checklist task is marked/unmarked (ACTION_UPDATED)
      - A new document is scanned (NEW_DOCUMENT)
      - An urgent deadline is detected < 15 days (CRITICAL_ALERT)
      - A tutor pairs with the senior (TUTOR_PAIRED)
    """
    await ws_manager.connect(websocket, senior_id)
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "CONNECTED",
            "senior_id": senior_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Conectado al canal en tiempo real de CLEARLY Tutor Hub.",
        })

        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "UNKNOWN")

            if msg_type == "PING":
                await websocket.send_json({
                    "type": "PONG",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

            elif msg_type == "TOGGLE_ACTION":
                action_id_str = data.get("action_id")
                completed_by_str = data.get("completed_by_user_id")

                if action_id_str:
                    try:
                        action_uuid = UUID(action_id_str)
                        completed_by_uuid = UUID(completed_by_str) if completed_by_str else None
                        await tutor_engine.toggle_checklist_item(
                            action_id=action_uuid,
                            completed_by_user_id=completed_by_uuid,
                        )
                    except Exception as e:
                        logger.error(f"Error handling WebSocket TOGGLE_ACTION: {e}")
                        await websocket.send_json({"type": "ERROR", "detail": str(e)})

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, senior_id)
    except Exception as e:
        logger.warning(f"WebSocket error in room '{senior_id}': {e}")
        ws_manager.disconnect(websocket, senior_id)

