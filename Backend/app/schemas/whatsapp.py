"""
CLEARLY — Pydantic Schemas for WhatsApp Integration via Evolution API v2.
Handles incoming webhook events (text, voice notes, documents) and outgoing notifications.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class EvolutionMessageKey(BaseModel):
    remoteJid: str
    fromMe: bool = False
    id: str


class EvolutionAudioMessage(BaseModel):
    url: Optional[str] = None
    base64: Optional[str] = None
    mimetype: Optional[str] = "audio/ogg; codecs=opus"
    seconds: Optional[int] = 0


class EvolutionImageMessage(BaseModel):
    url: Optional[str] = None
    base64: Optional[str] = None
    caption: Optional[str] = None
    mimetype: Optional[str] = "image/jpeg"


class EvolutionDocumentMessage(BaseModel):
    url: Optional[str] = None
    base64: Optional[str] = None
    title: Optional[str] = None
    fileName: Optional[str] = None
    mimetype: Optional[str] = "application/pdf"


class EvolutionMessageContent(BaseModel):
    conversation: Optional[str] = None
    extendedTextMessage: Optional[Dict[str, Any]] = None
    audioMessage: Optional[EvolutionAudioMessage] = None
    imageMessage: Optional[EvolutionImageMessage] = None
    documentMessage: Optional[EvolutionDocumentMessage] = None


class EvolutionMessageData(BaseModel):
    key: EvolutionMessageKey
    pushName: Optional[str] = "Usuario WhatsApp"
    message: Optional[EvolutionMessageContent] = None
    messageType: Optional[str] = "conversation"
    messageTimestamp: Optional[int] = None


class EvolutionWebhookPayload(BaseModel):
    event: str = "messages.upsert"
    instance: str = "clearly-instance"
    data: Optional[EvolutionMessageData] = None
    sender: Optional[str] = None


class WhatsAppProcessResult(BaseModel):
    status: str = "processed"
    sender_phone: str
    sender_name: str
    detected_intent: str = Field(
        ...,
        description="One of: 'document_analysis', 'events_query', 'general_civic', 'voice_dialogue'",
    )
    incoming_text: str
    text_reply: str
    audio_reply_generated: bool = False
    audio_reply_base64: Optional[str] = None
    audio_latency_ms: Optional[float] = None
    tutor_alert_dispatched: bool = False
    plain_language_score: Optional[float] = None
    document_id: Optional[UUID] = None

