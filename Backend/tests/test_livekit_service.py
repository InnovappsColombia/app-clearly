"""
CLEARLY — Test Suite for LiveKit WebRTC Service (Sprint 4)
Validates room token generation, HS256 JWT signatures, and gerontological caption metadata.
"""

import base64
import json
import unittest
import sys
from pathlib import Path
from uuid import uuid4

# Add Backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.livekit_service import livekit_service


class TestLiveKitService(unittest.TestCase):
    def test_senior_room_token_generation_with_a11y(self):
        """Validates that senior tokens include enlarged subtitle metadata (scale 1.5)."""
        booking_id = uuid4()
        details = livekit_service.create_room_token(
            booking_id=booking_id,
            participant_identity="senior_123",
            participant_name="Elena Pabla",
            is_senior=True,
        )

        self.assertIn("clearly-consultation-", details.room_name)
        self.assertEqual(details.caption_font_scale, 1.5)
        self.assertTrue(details.enable_realtime_transcription)

        # Parse JWT payload to verify claims
        token_parts = details.token.split(".")
        self.assertEqual(len(token_parts), 3)

        payload_bytes = base64.urlsafe_b64decode(token_parts[1] + "==")
        claims = json.loads(payload_bytes.decode())

        self.assertEqual(claims["sub"], "senior_123")
        self.assertEqual(claims["name"], "Elena Pabla")
        self.assertTrue(claims["video"]["roomJoin"])

        metadata = json.loads(claims["metadata"])
        self.assertTrue(metadata["enable_realtime_transcription"])
        self.assertEqual(metadata["caption_font_scale"], 1.5)
        self.assertTrue(metadata["high_contrast"])

    def test_expert_room_token_generation(self):
        """Validates that expert tokens have standard subtitle scale (1.0)."""
        booking_id = uuid4()
        details = livekit_service.create_room_token(
            booking_id=booking_id,
            participant_identity="expert_999",
            participant_name="David Mendoza, RCIC",
            is_senior=False,
        )

        self.assertEqual(details.caption_font_scale, 1.0)
        self.assertIn("clearly-consultation-", details.room_name)


if __name__ == "__main__":
    unittest.main()
