"""
CLEARLY — Pydantic Schemas for Tutor Hub, Handshake, and Real-Time Synchronization.
WCAG 2.1 AAA and FMEA FM-04 / PASETO compliant schemas.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.document import ActionItemResponse


class PairingCodeRequest(BaseModel):
    senior_id: Optional[UUID] = None


class PairingCodeResponse(BaseModel):
    pairing_code: str = Field(..., description="6-digit ephemeral pairing code")
    senior_id: UUID
    senior_name: str
    expires_at: datetime
    expires_in_seconds: int = 900
    qr_payload: str = Field(..., description="Curve25519 ephemeral handshake URI")


class PairTutorRequest(BaseModel):
    pairing_code: str = Field(..., min_length=6, max_length=6, description="6-digit code")
    tutor_id: Optional[UUID] = None


class PairTutorResponse(BaseModel):
    status: str = "paired"
    relationship_id: UUID
    senior_profile: Dict[str, Any]
    granted_permissions: Dict[str, bool]
    capability_token: str = Field(..., description="Attenuated PASETO v4 / Macaroon token")


class TutorSeniorSummaryResponse(BaseModel):
    senior_id: UUID
    full_name: str
    relationship_id: UUID
    is_active: bool
    active_deadlines_count: int
    pending_tasks_count: int
    critical_alert_active: bool


class CollaborativeTaskItem(BaseModel):
    id: UUID
    document_id: UUID
    document_title: str
    task_description: str
    required_document: Optional[str] = None
    deadline: Optional[date] = None
    days_remaining: Optional[int] = None
    is_critical: bool = False
    is_completed: bool = False
    completed_by_user_id: Optional[UUID] = None
    completed_by_name: Optional[str] = None
    completed_at: Optional[datetime] = None


class TutorDashboardResponse(BaseModel):
    senior: Dict[str, Any]
    relationship: Dict[str, Any]
    critical_deadlines: List[Dict[str, Any]]
    recent_documents: List[Dict[str, Any]]
    collaborative_checklist: List[CollaborativeTaskItem]
    notifications: List[Dict[str, Any]]
    is_quarantine_mode: bool = False


class ChecklistToggleRequest(BaseModel):
    completed_by_user_id: Optional[UUID] = None


class ChecklistToggleResponse(BaseModel):
    action_id: UUID
    document_id: UUID
    task_description: str
    is_completed: bool
    completed_by_user_id: Optional[UUID] = None
    completed_by_name: Optional[str] = None
    completed_at: Optional[datetime] = None


class DuressTriggerRequest(BaseModel):
    senior_id: UUID
    entered_pin: str


class DuressTriggerResponse(BaseModel):
    status: str = "success"
    # Identical innocent message to avoid revealing duress mode to a coercing party
    message: str = "Preferencias de privacidad y acompañamiento actualizadas correctamente."
    quarantine_mode: bool = True

