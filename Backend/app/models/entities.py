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
