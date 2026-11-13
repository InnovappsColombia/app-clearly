"""
CLEARLY — LiveKit WebRTC Service
Generates secure ephemeral JWT room tokens with geriatric accessibility metadata
(real-time subtitles, high contrast, enlarged video feed).
"""

import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional
from uuid import UUID
from loguru import logger

from app.core.config import settings
from app.schemas.premium import LiveKitRoomDetails


class LiveKitService:
    def __init__(self):
        self.api_key = settings.LIVEKIT_API_KEY
        self.api_secret = settings.LIVEKIT_API_SECRET
        self.livekit_url = settings.LIVEKIT_URL

    def create_room_token(
        self,
        booking_id: UUID,
        participant_identity: str,
        participant_name: str,
        is_senior: bool = True,
    ) -> LiveKitRoomDetails:
        """
        Creates signed LiveKit access token with video grants and geriatric accessibility metadata.
        """
        room_name = f"clearly-consultation-{str(booking_id)[:8]}"
        now = int(time.time())
        exp = now + 7200  # 2 hours validity

        # Gerontological accessibility settings injected into participant metadata
        a11y_metadata = {
            "enable_realtime_transcription": True,
            "caption_language": "es",
            "caption_font_scale": 1.5 if is_senior else 1.0,
            "high_contrast": True if is_senior else False,
            "audio_enhancement_geriatric": True,
        }

        # LiveKit Claims standard structure
        claims = {
            "iss": self.api_key,
            "sub": participant_identity,
            "name": participant_name,
            "nbf": now - 5,
            "exp": exp,
            "video": {
                "room": room_name,
                "roomJoin": True,
                "canPublish": True,
                "canSubscribe": True,
                "canPublishData": True,
            },
            "metadata": json.dumps(a11y_metadata),
        }

        # Build HS256 JWT
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
        signing_input = f"{header_b64}.{payload_b64}".encode()

        signature = hmac.new(self.api_secret.encode(), signing_input, hashlib.sha256).digest()
        sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

        token = f"{header_b64}.{payload_b64}.{sig_b64}"
        logger.info(f"Generated LiveKit token for '{participant_name}' in room '{room_name}'")

        return LiveKitRoomDetails(
            room_name=room_name,
            participant_identity=participant_identity,
            participant_name=participant_name,
            token=token,
            livekit_url=self.livekit_url,
            enable_realtime_transcription=True,
            caption_font_scale=1.5 if is_senior else 1.0,
        )


livekit_service = LiveKitService()
