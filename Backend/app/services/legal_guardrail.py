"""
CLEARLY — Legal & Ethical Guardrail Engine
Enforces Canadian IRPA Section 91 and Law Society / Medical ethics boundaries.
Strictly prohibits unauthorized prescriptive legal advice, medical diagnosis, or strategic counseling.
Escalates high-complexity cases to CLEARLY Premium verified human experts.
"""

import re
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field


class LegalGuardrailViolation(ValueError):
    """Raised when LLM output violates legal advice boundaries."""
    def __init__(self, message: str, pattern: str, matched_text: str):
        super().__init__(message)
        self.pattern = pattern
        self.matched_text = matched_text


class GuardrailAuditResult(BaseModel):
    is_valid: bool = Field(description="True si el texto cumple los guardrails legales y éticos")
    violations: List[str] = Field(default_factory=list, description="Lista de frases prohibidas detectadas")
    requires_human_expert: bool = Field(
        default=False, description="True si requiere escalamiento a CLEARLY Premium"
    )
    risk_level: str = "none"  # none, low, medium, high
    disclaimer: str = Field(
        default=(
            "CLEARLY ofrece simplificación lingüística y de accesibilidad. "
            "No constituye asesoramiento legal ni médico. Para asesoría formal, "
            "consulte a un profesional verificado en CLEARLY Premium."
        )
    )


# Critical prohibited prescriptive patterns
PROHIBITED_LEGAL_ADVICE_PATTERNS = [
    # Demanda / Apelación no autorizada
    r"\b(debe(?:s)?|tiene(?:s)? que)\s+(demandar|apelar|denunciar|declarar)\b",
    # Consejo directo no autorizado
    r"\b(le conviene|le recomiendo|mi consejo legal es|te sugiero apelar|mi opini[oó]n profesional es)\b",
    # Promesas de resultado judicial o migratorio
    r"\b(este documento significa que ganar[aá]|perder[aá] su caso|seguro le aprueban|no se preocupe no lo expulsar[aá]n)\b",
    # Instrucciones de desacato o evasión
    r"\b(no pague|ignore esta carta|haga caso omiso|no se presente a la cita)\b",
    # Diagnóstico médico o prescripción farmacéutica
    r"\b(su diagn[oó]stico m[eé]dico indica|usted padece de|debe tomar el medicamento|suspenda su tratamiento)\b",
    # Evasión fiscal o patrimonial
    r"\b(no declare este ingreso|oculte sus bienes|transfiera su dinero para evitar)\b",
]

# Patterns indicating that the case is complex and should be escalated to CLEARLY Premium
HUMAN_ESCALATION_TRIGGERS = [
    r"\b(orden de expulsi[oó]n|deportaci[oó]n|removal order|procedural fairness letter|denegaci[oó]n de refugio)\b",
    r"\b(desalojo inmediato|lanzamiento judicial|tribunal de alquileres|n4|n12)\b",
    r"\b(suspensi[oó]n de pensi[oó]n|fraude fiscal|auditor[ií]a cra)\b",
    r"\b(procedimiento quir[uú]rgico mayor|consentimiento informado cr[ií]tico)\b",
]


def assert_no_unauthorized_advice(llm_output_text: str) -> None:
    """
    Validates that the output contains NO unauthorized prescriptive legal or medical advice.
    Raises LegalGuardrailViolation if a forbidden pattern is detected.
    """
    for pattern in PROHIBITED_LEGAL_ADVICE_PATTERNS:
        match = re.search(pattern, llm_output_text, re.IGNORECASE)
        if match:
            matched_phrase = match.group(0)
            raise LegalGuardrailViolation(
                message=(
                    f"Violación de Guardrail Legal: Detección de consejo prescriptivo no autorizado ('{matched_phrase}'). "
                    f"El motor CLEARLY debe limitarse a la simplificación lingüística objetiva."
                ),
                pattern=pattern,
                matched_text=matched_phrase,
            )


def audit_legal_guardrails(text: str) -> GuardrailAuditResult:
    """
    Comprehensive audit of text against legal boundaries and escalation triggers.
    Returns structured audit result without raising exceptions.
    """
    violations = []
    for pattern in PROHIBITED_LEGAL_ADVICE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            violations.append(match.group(0))

    # Check if case complexity warrants escalation to CLEARLY Premium
    requires_expert = False
    for pat in HUMAN_ESCALATION_TRIGGERS:
        if re.search(pat, text, re.IGNORECASE):
            requires_expert = True
            break

    is_valid = len(violations) == 0
    risk = "none"
    if not is_valid:
        risk = "high"
        requires_expert = True
    elif requires_expert:
        risk = "medium"

    return GuardrailAuditResult(
        is_valid=is_valid,
        violations=violations,
        requires_human_expert=requires_expert,
        risk_level=risk,
    )

