"""
CLEARLY — Data Models and Domain Entities
Supports both relational DB schemas and in-memory persistence.
"""

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    phone_number: str
    email: Optional[str] = None
    full_name: str
    role: str = "senior"  # senior, tutor, expert, admin
    preferred_language: str = "es"
    accessibility_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "font_scale": 1.25,
            "high_contrast": False,
            "audio_speed": 1.0,
            "auto_read_aloud": True,
        }
    )
    is_active: bool = True
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)


class TutorRelationshipEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    senior_id: UUID
    tutor_id: UUID
    pairing_code_hash: Optional[str] = None
    duress_pin_hash: Optional[str] = None
    is_active: bool = True
    is_duress_active: bool = False
    duress_activated_at: Optional[datetime] = None
    permissions: Dict[str, bool] = Field(
        default_factory=lambda: {
            "can_view_critical_alerts": True,
            "can_view_documents": True,
            "can_view_events": True,
            "can_hire_experts": True,
        }
    )
    created_at: datetime = Field(default_factory=get_utc_now)
    revoked_at: Optional[datetime] = None


class TutorPairingCodeEntity(BaseModel):
    code: str
    senior_id: UUID
    created_at: datetime = Field(default_factory=get_utc_now)
    expires_at: datetime
    is_redeemed: bool = False


class DuressAlertEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    senior_id: UUID
    triggered_at: datetime = Field(default_factory=get_utc_now)
    quarantine_token: str
    social_worker_alert_sent: bool = True
    status: str = "active"


class CommunityEventEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    external_id: Optional[str] = None
    source: str = "civic_library"
    raw_title: str
    made_clear_what: str
    made_clear_when_where: str
    made_clear_cost: str
    made_clear_how_to_register: str
    event_url: Optional[str] = None
    audio_summary_path: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_wheelchair_accessible: bool = True
    is_senior_friendly: bool = True
    is_free: bool = True
    supported_languages: List[str] = Field(default_factory=lambda: ["es", "en"])
    created_at: datetime = Field(default_factory=get_utc_now)


class DocumentActionEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    task_description: str
    required_document: Optional[str] = None
    deadline: Optional[date] = None
    is_completed: bool = False
    completed_by_user_id: Optional[UUID] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=get_utc_now)


class DocumentEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    storage_path: str
    file_sha256: str
    original_extracted_text: Optional[str] = None
    plain_summary: str
    issuing_entity: Optional[str] = None
    urgency: str = "medium"  # low, medium, high, critical
    critical_deadline: Optional[date] = None
    fernandez_huerta_score: Optional[float] = None
    ambiguities: List[str] = Field(default_factory=list)
    recommended_questions: List[str] = Field(default_factory=list)
    requires_human_expert: bool = False
    embedding: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)


class NotificationEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    title: str
    message: str
    channel: str = "in_app"  # in_app, whatsapp, push, sms
    is_urgent: bool = False
    is_read: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=get_utc_now)


class ExpertProfileEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    specialty: str
    license_number: str
    id_verification_status: str = "verified"
    hourly_rate_cents: int = 4500  # $45.00 CAD
    bio_plain_text: str
    languages_spoken: List[str] = Field(default_factory=lambda: ["es", "en"])
    service_modalities: List[str] = Field(default_factory=lambda: ["virtual", "in_person"])
    average_rating: float = 5.0
    total_reviews: int = 0
    is_available: bool = True
    created_at: datetime = Field(default_factory=get_utc_now)


class PremiumBookingEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    client_senior_id: UUID
    requested_by_user_id: UUID
    expert_id: UUID
    document_id: Optional[UUID] = None
    modality: str = "virtual"
    scheduled_start: datetime
    scheduled_end: datetime
    livekit_room_name: str
    livekit_token: Optional[str] = None
    status: str = "escrow_held"  # pending, escrow_held, in_progress, completed, cancelled, disputed
    stripe_payment_intent_id: str
    amount_cents: int = 4500
    expert_payout_cents: int = 3825
    platform_fee_cents: int = 675
    client_review_rating: Optional[int] = None
    client_review_text: Optional[str] = None
    escrow_released_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)
