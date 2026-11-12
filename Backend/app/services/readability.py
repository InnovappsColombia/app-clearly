"""
CLEARLY — Fernández-Huerta Readability Auditor Module
Implements Spanish Readability Index (FH >= 80) tailored for Plain Language (Lenguaje Claro)
and geriatric accessibility (WCAG 2.1 AAA).
"""

import re
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.services.spanish_syllabifier import count_syllables_word, count_total_syllables


class ReadabilityAudit(BaseModel):
    score: float = Field(description="Índice Fernández-Huerta (0 a 100+)")
    is_acceptable: bool = Field(description="True si cumple el umbral gerontológico FH >= 80")
    category: str = Field(description="Clasificación cualitativa de comprensión")
    reading_level: str = Field(description="Nivel educativo aproximado requerido")
    num_words: int
    num_sentences: int
    total_syllables: int
    syllables_per_word: float
    words_per_sentence: float
    recommendations: List[str] = Field(default_factory=list)


# Bureaucratic to Plain Language replacement dictionary
COMMON_BUREAUCRATIC_REPLACEMENTS = {
    r"\bde conformidad con\b": "según",
    r"\ba tenor de\b": "según",
    r"\bcon posterioridad a\b": "después de",
    r"\bcon anterioridad a\b": "antes de",
    r"\bfenecido el plazo\b": "vencido el tiempo",
    r"\ba la mayor brevedad posible\b": "cuanto antes",
    r"\ben aras de\b": "para",
    r"\bcon el objeto de\b": "para",
    r"\bcon la finalidad de\b": "para",
    r"\b(?:se\s+)?proceder[aá]\s+al\s+pago\b": "pagar",
    r"\b(?:se\s+)?proceder[aá]\s+a\b": "hará",
    r"\bproceder a la entrega\b": "entregar",
    r"\bproceder al pago\b": "pagar",
    r"\binterponer recurso\b": "apelar",
    r"\bhacer entrega de\b": "entregar",
    r"\bhacer llegar\b": "enviar",
    r"\bponer en conocimiento\b": "informar",
    r"\btener a bien\b": "pedir",
    r"\badicionalmente\b": "además",
    r"\basimismo\b": "también",
    r"\bno obstante\b": "pero",
    r"\bsin embargo\b": "pero",
    r"\bpor consiguiente\b": "por eso",
    r"\ben consecuencia\b": "por eso",
}


def clean_words_list(text: str) -> List[str]:
    """Extract clean words from Spanish text."""
    raw_words = text.split()
    words = []
    for w in raw_words:
        cleaned = re.sub(r"[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ]", "", w)
        if cleaned:
            words.append(cleaned)
    return words


def split_sentences(text: str) -> List[str]:
    """Split text into sentences using standard Spanish punctuation boundaries."""
    raw = [s.strip() for s in re.split(r"[.!?]+|\n+", text) if s.strip()]
    return [s for s in raw if any(c.isalnum() for c in s)]


def calculate_fernandez_huerta(text: str, method: str = "canonical") -> float:
    """
    Calculate the Fernández-Huerta readability score.
    Formula: FH = 206.84 - (0.60 * P) - (1.02 * F)
    
    where:
    - P = syllables per 100 words
    - F:
      - 'canonical': Average Sentence Length (words / sentence)
      - 'spec': sentences per 100 words (as in engineering spec snippet)
    """
    words = clean_words_list(text)
    num_words = len(words)
    if num_words == 0:
        return 0.0

    sentences = split_sentences(text)
    num_sentences = max(1, len(sentences))

    total_syllables = sum(count_syllables_word(w) for w in words)
    p = (total_syllables / num_words) * 100.0

    if method == "spec":
        f = (num_sentences / num_words) * 100.0
    else:
        # Standard canonical Flesch-Huerta: F = words per sentence
        f = num_words / num_sentences

    score = 206.84 - (0.60 * p) - (1.02 * f)
    return round(score, 2)


def classify_readability(score: float) -> tuple[str, str]:
    """Classify FH score into qualitative category and school level."""
    if score >= 90.0:
        return "Muy fácil", "4º de primaria (Lenguaje universal accesible)"
    elif score >= 80.0:
        return "Fácil", "5º de primaria (Recomendado CLEARLY A11y)"
    elif score >= 70.0:
        return "Algo fácil", "6º de primaria"
    elif score >= 60.0:
        return "Normal / Adecuado", "1º - 2º de secundaria"
    elif score >= 50.0:
        return "Algo difícil", "3º de secundaria"
    elif score >= 30.0:
        return "Difícil", "Bachillerato"
    else:
        return "Muy difícil / Burocrático", "Universidad / Especialista legal"


def audit_readability(text: str, min_acceptable_score: float = 80.0) -> ReadabilityAudit:
    """
    Run full readability audit on a text.
    Validates whether the text fulfills the Plain Language requirement (FH >= 80).
    """
    words = clean_words_list(text)
    num_words = len(words)
    sentences = split_sentences(text)
    num_sentences = max(1, len(sentences))

    if num_words == 0:
        return ReadabilityAudit(
            score=0.0,
            is_acceptable=False,
            category="Vacío",
            reading_level="N/A",
            num_words=0,
            num_sentences=0,
            total_syllables=0,
            syllables_per_word=0.0,
            words_per_sentence=0.0,
            recommendations=["El texto está vacío."],
        )

    total_syllables = sum(count_syllables_word(w) for w in words)
    syllables_per_word = round(total_syllables / num_words, 2)
    words_per_sentence = round(num_words / num_sentences, 2)

    score = calculate_fernandez_huerta(text, method="canonical")
    category, level = classify_readability(score)
    is_acceptable = score >= min_acceptable_score

    recommendations = []
    if words_per_sentence > 15:
        recommendations.append(
            f"Las oraciones son muy largas ({words_per_sentence} palabras/frase). Divídelas en frases cortas de menos de 12 palabras."
        )
    if syllables_per_word > 2.2:
        recommendations.append(
            f"Hay muchas palabras complejas o polisílabas ({syllables_per_word} sílabas/palabra). Usa sinónimos más sencillos."
        )
    if score < min_acceptable_score:
        recommendations.append(
            f"El índice Fernández-Huerta ({score}) no alcanza el umbral de accesibilidad gerontológica ({min_acceptable_score}). Reescribe en Lenguaje Claro."
        )

    return ReadabilityAudit(
        score=score,
        is_acceptable=is_acceptable,
        category=category,
        reading_level=level,
        num_words=num_words,
        num_sentences=num_sentences,
        total_syllables=total_syllables,
        syllables_per_word=syllables_per_word,
        words_per_sentence=words_per_sentence,
        recommendations=recommendations,
    )


def simplify_bureaucratic_text(text: str) -> str:
    """Apply deterministic plain-language replacements to simplify bureaucratic text."""
    simplified = text
    for pattern, replacement in COMMON_BUREAUCRATIC_REPLACEMENTS.items():
        simplified = re.sub(pattern, replacement, simplified, flags=re.IGNORECASE)
    return simplified
