"""
CLEARLY — Multilingual Readability Auditor Module
Implements:
- Spanish: Fernández-Huerta Readability Index (FH >= 80) tailored for Plain Language & geriatric A11y.
- English: Flesch Reading Ease (FRE >= 80) and Flesch-Kincaid Grade Level (FKGL <= 5.0).
- Punjabi (Gurmukhi): Word count per sentence (ASL <= 15) and token brevity metrics.
"""

import re
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.services.spanish_syllabifier import count_syllables_word, count_total_syllables


class ReadabilityAudit(BaseModel):
    score: float = Field(description="Índice de legibilidad (FH para español, FRE para inglés)")
    is_acceptable: bool = Field(description="True si cumple el umbral gerontológico (FH >= 80 o FRE >= 80)")
    category: str = Field(description="Clasificación cualitativa de comprensión")
    reading_level: str = Field(description="Nivel educativo aproximado requerido")
    language: str = Field(default="es")
    num_words: int
    num_sentences: int
    total_syllables: int
    syllables_per_word: float
    words_per_sentence: float
    recommendations: List[str] = Field(default_factory=list)


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


def clean_words_list(text: str, language: str = "es") -> List[str]:
    """Extract clean words from text in Spanish, English, or Punjabi."""
    raw_words = text.split()
    words = []
    for w in raw_words:
        if language == "pa":
            # Gurmukhi Unicode block: U+0A00 to U+0A7F
            cleaned = re.sub(r"[^\u0A00-\u0A7F0-9a-zA-Z]", "", w)
        else:
            cleaned = re.sub(r"[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ]", "", w)
        if cleaned:
            words.append(cleaned)
    return words


def split_sentences(text: str) -> List[str]:
    """Split text into sentences using punctuation boundaries (. ! ? or newline or danda ।)."""
    raw = [s.strip() for s in re.split(r"[.!?।]+|\n+", text) if s.strip()]
    return [s for s in raw if any(c.isalnum() or '\u0A00' <= c <= '\u0A7F' for c in s)]


def count_syllables_english(word: str) -> int:
    """Accurate English syllable heuristic based on vowel sequences and silent-e."""
    w = word.lower().strip()
    if not w:
        return 0
    if len(w) <= 3:
        return 1

    # Remove non-alpha
    w = re.sub(r"[^a-z]", "", w)
    if not w:
        return 1

    # Handle common prefixes / suffixes
    if w.endswith("es") and not w.endswith("ses") and not w.endswith("zes") and not w.endswith("ches") and not w.endswith("shes"):
        w = w[:-2]
    elif w.endswith("e") and not w.endswith("le") and not w.endswith("ee"):
        w = w[:-1]

    # Count vowel groups
    vowels = "aeiouy"
    count = 0
    in_vowel = False
    for char in w:
        if char in vowels:
            if not in_vowel:
                count += 1
                in_vowel = True
        else:
            in_vowel = False

    return max(1, count)


def calculate_fernandez_huerta(text: str, method: str = "canonical") -> float:
    """
    Calculate the Fernández-Huerta readability score for Spanish.
    Formula: FH = 206.84 - (0.60 * P) - (1.02 * F)
    """
    words = clean_words_list(text, language="es")
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
        f = num_words / num_sentences

    score = 206.84 - (0.60 * p) - (1.02 * f)
    return round(score, 2)


def calculate_flesch_reading_ease(text: str) -> float:
    """
    Calculate Flesch Reading Ease for English.
    Formula: FRE = 206.835 - (1.015 * ASL) - (84.6 * ASW)
    where ASL = Average Sentence Length, ASW = Average Syllables per Word.
    """
    words = clean_words_list(text, language="en")
    num_words = len(words)
    if num_words == 0:
        return 0.0

    sentences = split_sentences(text)
    num_sentences = max(1, len(sentences))

    asl = num_words / num_sentences
    total_syllables = sum(count_syllables_english(w) for w in words)
    asw = total_syllables / num_words

    fre = 206.835 - (1.015 * asl) - (84.6 * asw)
    return round(fre, 2)


def calculate_flesch_kincaid_grade(text: str) -> float:
    """
    Calculate Flesch-Kincaid Grade Level for English.
    Formula: FKGL = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
    """
    words = clean_words_list(text, language="en")
    num_words = len(words)
    if num_words == 0:
        return 0.0

    sentences = split_sentences(text)
    num_sentences = max(1, len(sentences))

    asl = num_words / num_sentences
    total_syllables = sum(count_syllables_english(w) for w in words)
    asw = total_syllables / num_words

    fkgl = (0.39 * asl) + (11.8 * asw) - 15.59
    return round(max(0.0, fkgl), 2)


def classify_readability(score: float, language: str = "es") -> Tuple[str, str]:
    """Classify FH or FRE score into qualitative accessibility categories."""
    if score >= 90.0:
        return "Muy fácil", "4º de primaria (Máxima accesibilidad cívica)"
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
        return "Muy difícil / Complejo", "Nivel universitario"


def audit_readability(
    text: str,
    min_acceptable_score: float = 80.0,
    language: str = "es",
) -> ReadabilityAudit:
    """
    Run full multilingual readability audit.
    Enforces Plain Language requirement:
    - Spanish: FH >= 80.0
    - English: FRE >= 80.0
    - Punjabi: Sentence length <= 15 words
    """
    words = clean_words_list(text, language=language)
    num_words = len(words)
    sentences = split_sentences(text)
    num_sentences = max(1, len(sentences))

    if num_words == 0:
        return ReadabilityAudit(
            score=0.0,
            is_acceptable=False,
            category="Vacío",
            reading_level="N/A",
            language=language,
            num_words=0,
            num_sentences=0,
            total_syllables=0,
            syllables_per_word=0.0,
            words_per_sentence=0.0,
            recommendations=["El texto está vacío."],
        )

    if language == "en":
        total_syllables = sum(count_syllables_english(w) for w in words)
        score = calculate_flesch_reading_ease(text)
        fkgl = calculate_flesch_kincaid_grade(text)
        category, level = classify_readability(score, language="en")
        level = f"{level} (Grade {fkgl})"
    elif language == "pa":
        # In Gurmukhi, each vowel carrier/matra roughly corresponds to a syllable
        total_syllables = sum(max(1, len(w) // 2) for w in words)
        words_per_sentence = round(num_words / num_sentences, 2)
        score = max(0.0, min(100.0, 100.0 - (words_per_sentence * 2.5)))
        category = "ਸਰਲ (ਸੌਖੀ ਬੋਲੀ)" if score >= 80 else "ਮੱਧਮ"
        level = "ਪ੍ਰਾਇਮਰੀ ਪੱਧਰ"
    else:
        total_syllables = sum(count_syllables_word(w) for w in words)
        score = calculate_fernandez_huerta(text, method="canonical")
        category, level = classify_readability(score, language="es")

    syllables_per_word = round(total_syllables / num_words, 2)
    words_per_sentence = round(num_words / num_sentences, 2)
    is_acceptable = score >= min_acceptable_score

    recommendations = []
    if words_per_sentence > 15:
        recommendations.append(
            f"Las oraciones son muy largas ({words_per_sentence} palabras/frase). Divídelas en oraciones de menos de 12 palabras."
        )
    if syllables_per_word > 2.2:
        recommendations.append(
            f"Hay muchas palabras complejas ({syllables_per_word} sílabas/palabra). Usa vocabulario cotidiano."
        )
    if score < min_acceptable_score:
        recommendations.append(
            f"El índice de legibilidad ({score}) no alcanza el umbral de accesibilidad gerontológica ({min_acceptable_score})."
        )

    return ReadabilityAudit(
        score=score,
        is_acceptable=is_acceptable,
        category=category,
        reading_level=level,
        language=language,
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
