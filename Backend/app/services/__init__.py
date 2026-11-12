"""Services package for CLEARLY Backend."""
from app.services.spanish_syllabifier import count_syllables_word, count_total_syllables
from app.services.readability import (
    calculate_fernandez_huerta,
    audit_readability,
    simplify_bureaucratic_text,
    ReadabilityAudit,
)
from app.services.date_extractor import (
    extract_deterministic_deadline,
    extract_base_date,
    calculate_urgency,
    ExtractedDeadline,
)
from app.services.legal_guardrail import (
    assert_no_unauthorized_advice,
    audit_legal_guardrails,
    LegalGuardrailViolation,
    GuardrailAuditResult,
)
from app.services.storage import storage_service, StorageService
from app.services.ocr_service import ocr_service, OCRService
from app.services.plain_language import analyze_document_plain_language, AnalysisStructure
from app.services.document_pipeline import document_pipeline, DocumentPipeline

__all__ = [
    "count_syllables_word",
    "count_total_syllables",
    "calculate_fernandez_huerta",
    "audit_readability",
    "simplify_bureaucratic_text",
    "ReadabilityAudit",
    "extract_deterministic_deadline",
    "extract_base_date",
    "calculate_urgency",
    "ExtractedDeadline",
    "assert_no_unauthorized_advice",
    "audit_legal_guardrails",
    "LegalGuardrailViolation",
    "GuardrailAuditResult",
    "storage_service",
    "StorageService",
    "ocr_service",
    "OCRService",
    "analyze_document_plain_language",
    "AnalysisStructure",
    "document_pipeline",
    "DocumentPipeline",
]

