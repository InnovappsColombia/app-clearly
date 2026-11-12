"""
CLEARLY — Test Suite for Real-Time WebSocket Tutor Hub
Validates connection management, action toggling broadcasts, and proactive critical alerts.
Runs with deterministic synchronous async execution (safe across all sandboxes).
"""

import unittest
import sys
from pathlib import Path
from uuid import UUID

# Add Backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.connection_manager import ws_manager
from tests.async_helper import run_sync

ELENA_ID = "11111111-1111-1111-1111-111111111111"
CARLOS_ID = "22222222-2222-2222-2222-222222222222"
SEED_ACTION_ID = "99999999-9999-9999-9999-999999999991"


class MockWebSocket:
    def __init__(self):
        self.accepted = False
        self.sent_messages = []

    async def accept(self):
        self.accepted = True

    async def send_json(self, data):
        self.sent_messages.append(data)


class TestWebSocketHub(unittest.TestCase):
    def test_websocket_connection_and_broadcast(self):
        """Tests connecting to the senior's WebSocket room and broadcasting an action update."""
        mock_ws = MockWebSocket()

        # Connect client to Elena's room
        run_sync(ws_manager.connect(mock_ws, ELENA_ID))
        self.assertTrue(mock_ws.accepted)
        self.assertIn(ELENA_ID, ws_manager.active_rooms)
        self.assertIn(mock_ws, ws_manager.active_rooms[ELENA_ID])

        # Broadcast action toggle
        action_payload = {
            "action_id": SEED_ACTION_ID,
            "task_description": "Reunir sellos del pasaporte",
            "is_completed": True,
            "completed_by_name": "Carlos Pabla",
        }
        run_sync(ws_manager.broadcast_action_toggle(ELENA_ID, action_payload))

        self.assertEqual(len(mock_ws.sent_messages), 1)
        msg = mock_ws.sent_messages[0]
        self.assertEqual(msg["type"], "ACTION_UPDATED")
        self.assertEqual(msg["data"]["action_id"], SEED_ACTION_ID)
        self.assertEqual(msg["data"]["completed_by_name"], "Carlos Pabla")

        # Broadcast critical alert (< 15 days)
        alert_payload = {
            "document_id": "doc-uuid-123",
            "issuing_entity": "LTB Ontario",
            "deadline": "2026-11-25",
            "days_remaining": 13,
            "plain_summary": "Aviso N4 con 13 días de plazo.",
        }
        run_sync(ws_manager.broadcast_critical_alert(ELENA_ID, alert_payload))

        self.assertEqual(len(mock_ws.sent_messages), 2)
        alert_msg = mock_ws.sent_messages[1]
        self.assertEqual(alert_msg["type"], "CRITICAL_ALERT")
        self.assertEqual(alert_msg["data"]["days_remaining"], 13)

        # Disconnect client
        ws_manager.disconnect(mock_ws, ELENA_ID)
        self.assertNotIn(ELENA_ID, ws_manager.active_rooms)


if __name__ == "__main__":
    unittest.main()
