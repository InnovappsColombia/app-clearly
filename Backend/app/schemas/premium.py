"""
CLEARLY — Pydantic Schemas for CLEARLY Premium, Matching & Escrow Bookings.
Implements Stripe Connect escrow hold and LiveKit WebRTC room payload models.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ExpertProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    specialty: str
    license_number: str
    id_verification_status: str
    hourly_rate_cents: int
    hourly_rate_formatted: str
    bio_plain_text: str
    languages_spoken: List[str]
    service_modalities: List[str]
    average_rating: float
    total_reviews: int
    is_available: bool


class ExpertMatchRequest(BaseModel):
    document_id: Optional[UUID] = None
    query_text: Optional[str] = None
    senior_id: Optional[UUID] = None


class ExpertMatchResponse(BaseModel):
    matched_expert: ExpertProfileResponse
    detected_specialty: str
    match_score: float
    plain_language_reasoning: str
    alternative_experts: List[ExpertProfileResponse] = Field(default_factory=list)


class CreateBookingRequest(BaseModel):
    expert_id: UUID
    client_senior_id: UUID
    requested_by_user_id: Optional[UUID] = None  # Tutor or Senior themselves
    document_id: Optional[UUID] = None
    modality: str = "virtual"
    scheduled_start: datetime
    scheduled_end: Optional[datetime] = None
    payment_method_id: Optional[str] = "pm_card_visa_test"


class BookingResponse(BaseModel):
    id: UUID
    client_senior_id: UUID
    client_name: str
    requested_by_name: str
    expert_id: UUID
    expert_name: str
    specialty: str
    license_number: str
    modality: str
    scheduled_start: datetime
    scheduled_end: datetime
    status: str
    stripe_payment_intent_id: str
    amount_cents: int
    amount_formatted: str
    livekit_room_name: str
    livekit_token: Optional[str] = None
    escrow_held: bool = True
    created_at: datetime


class ReleaseEscrowRequest(BaseModel):
    rating: int = Field(ge=1, le=5, description="Calificación de 1 a 5 estrellas")
    review_text: Optional[str] = None


class ReleaseEscrowResponse(BaseModel):
    booking_id: UUID
    status: str = "completed"
    escrow_released_at: datetime
    expert_payout_cents: int
    expert_payout_formatted: str
    client_review_rating: int
    message: str


class LiveKitRoomDetails(BaseModel):
    room_name: str
    participant_identity: str
    participant_name: str
    token: str
    livekit_url: str
    enable_realtime_transcription: bool = True
    caption_font_scale: float = 1.5
