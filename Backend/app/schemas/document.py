"""
CLEARLY — Pydantic Schemas for Document Processing & Analysis
Strictly typed for Pydantic v2.
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ActionItemBase(BaseModel):
    task: str = Field(description="Acción concreta y sencilla que el usuario debe realizar")
    required_document: Optional[str] = Field(None, description="Documento específico necesario para la acción")
    deadline: Optional[date] = Field(None, description="Fecha límite calculada determinísticamente")
    is_mandatory: bool = Field(True, description="Si es un requisito obligatorio o sugerido")


class ActionItemResponse(BaseModel):
    id: UUID
    document_id: UUID
    task_description: str
    required_document: Optional[str] = None
    deadline: Optional[date] = None
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    created_at: datetime


class DocumentProcessResponse(BaseModel):
    id: UUID
    user_id: UUID
    document_type: str = Field(description="Tipo de documento clasificado (ej. Notificación LTB, IRCC, Salud)")
    issuing_entity: str = Field(description="Entidad emisora de la carta")
    plain_summary: str = Field(description="Explicación en Lenguaje Claro accesible de 2-3 frases (FH >= 80)")
    detected_language: str = Field(default="es")
    fernandez_huerta_score: float = Field(description="Puntuación de legibilidad Fernández-Huerta")
    readability_category: str = Field(description="Categoría cualitativa (Muy fácil / Fácil)")
    urgency: str = Field(description="Nivel de urgencia: low, medium, high, critical")
    critical_deadline: Optional[date] = Field(None, description="Fecha límite más urgente detectada")
    days_remaining: Optional[int] = Field(None, description="Días restantes hasta la fecha límite")
    tutor_alert_triggered: bool = Field(False, description="True si se despachó alerta preventiva al Tutor")
    requires_human_expert: bool = Field(False, description="True si excede el alcance ético de la IA")
    actions_required: List[ActionItemResponse] = Field(default_factory=list)
    ambiguities_flagged: List[str] = Field(default_factory=list)
    recommended_questions: List[str] = Field(default_factory=list)
    storage_path: str
    file_sha256: str
    created_at: datetime


class DocumentDetailResponse(DocumentProcessResponse):
    original_extracted_text: Optional[str] = None


class ReadabilityAuditRequest(BaseModel):
    text: str = Field(..., description="Texto en español para auditar legibilidad")


class ReadabilityAuditResponse(BaseModel):
    score: float
    is_acceptable: bool
    category: str
    reading_level: str
    num_words: int
    num_sentences: int
    total_syllables: int
    syllables_per_word: float
    words_per_sentence: float
    recommendations: List[str]


class DateExtractionRequest(BaseModel):
    text: str = Field(..., description="Texto de la carta para extraer fechas")
    reference_date: Optional[date] = Field(None, description="Fecha de referencia para cálculo (default: hoy)")


class DateExtractionResponse(BaseModel):
    deadline_date: Optional[date]
    base_date: Optional[date]
    offset_days: Optional[int]
    is_business_days: bool
    operator: str
    urgency: str
    days_remaining: Optional[int]
    tutor_alert_required: bool
    raw_snippet: Optional[str]
    confidence: float

