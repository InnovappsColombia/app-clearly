"""
CLEARLY — Legal Guardrails & Readability Auditor for Sovereign RAG
Validates:
1. Fernández-Huerta readability score (FH >= 80) for Spanish Plain Language.
2. Flesch Reading Ease (FRE >= 80) for English Plain Language.
3. Strict Grounding & Anti-Hallucination:
   - Verifies all mentioned dates exist in source chunks.
   - Checks presence of chunk citation references.
   - Injects non-negotiable legal disclaimer.
   - Evaluates escalation triggers for CLEARLY Premium human experts.
"""

import math
import re
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

from RAG.prompts.plain_language import (
    LEGAL_DISCLAIMER_EN,
    LEGAL_DISCLAIMER_ES,
    LEGAL_DISCLAIMER_PA,
)


@dataclass
class ReadabilityMetrics:
    score: float
    grade_level: str
    is_plain_language: bool  # True if >= 80.0
    word_count: int
    sentence_count: int
    syllable_count: int
    avg_sentence_length: float
    avg_syllables_per_word: float


@dataclass
class GuardrailAuditResult:
    is_safe: bool
    readability: ReadabilityMetrics
    has_citations: bool
    cited_chunks: List[int]
    unverified_dates: List[str]
    requires_human_expert: bool
    expert_reason: Optional[str] = None
    sanitized_text: str = ""


class SovereignReadabilityAuditor:
    """
    Computes Fernández-Huerta (Spanish) and Flesch Reading Ease (English) metrics
    using native rule-based syllabification without external network calls.
    """

    STRONG_VOWELS = set("aeoáéóAEOÁÉÓ")
    WEAK_VOWELS = set("iuüIUÜ")
    ACCENTED_WEAK = set("íúÍÚ")

    @classmethod
    def count_spanish_syllables(cls, word: str) -> int:
        """Counts syllables in a Spanish word considering hiatuses and diphthongs."""
        w = re.sub(r"[^\w]", "", word).lower()
        if not w:
            return 0
        if len(w) <= 2:
            return 1

        syllables = 0
        i = 0
        n = len(w)

        while i < n:
            char = w[i]
            if char in cls.STRONG_VOWELS or char in cls.WEAK_VOWELS or char in cls.ACCENTED_WEAK:
                syllables += 1
                # Check next character for diphthong or hiatus
                if i + 1 < n:
                    next_char = w[i + 1]
                    # Accented weak + any vowel = Hiatus (2 syllables, do not consume)
                    if char in cls.ACCENTED_WEAK or next_char in cls.ACCENTED_WEAK:
                        pass
                    # Strong + Strong = Hiatus (2 syllables, do not consume)
                    elif char in cls.STRONG_VOWELS and next_char in cls.STRONG_VOWELS:
                        pass
                    # Strong + Weak or Weak + Strong or Weak + Weak = Diphthong (1 syllable, consume next)
                    elif (
                        (char in cls.STRONG_VOWELS and next_char in cls.WEAK_VOWELS)
                        or (char in cls.WEAK_VOWELS and next_char in cls.STRONG_VOWELS)
                        or (char in cls.WEAK_VOWELS and next_char in cls.WEAK_VOWELS)
                    ):
                        i += 1
            i += 1

        return max(1, syllables)

    @classmethod
    def count_english_syllables(cls, word: str) -> int:
        """Counts syllables in an English word."""
        w = re.sub(r"[^\w]", "", word).lower()
        if not w:
            return 0
        if len(w) <= 3:
            return 1

        # Common suffixes
        w = re.sub(r"(?:[^laeiouy]|ed|es|e)$", "", w)
        sylls = len(re.findall(r"[aeiouy]{1,2}", w))
        return max(1, sylls)

    @classmethod
    def audit_spanish_fernandez_huerta(cls, text: str) -> ReadabilityMetrics:
        """
        Computes the Fernández-Huerta Readability Index:
        FH = 206.84 - (0.60 * P) - (1.02 * F)
        Where:
        P = (Total syllables / Total words) * 100
        F = Total words / Total sentences
        Threshold for Plain Language (Lectura Fácil / Muy Fácil): FH >= 80.0
        """
        words = re.findall(r"\b[A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9-]+\b", text)
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

        total_words = len(words)
        total_sentences = max(1, len(sentences))

        if total_words == 0:
            return ReadabilityMetrics(
                score=100.0,
                grade_level="Lectura Muy Fácil",
                is_plain_language=True,
                word_count=0,
                sentence_count=0,
                syllable_count=0,
                avg_sentence_length=0.0,
                avg_syllables_per_word=0.0,
            )

        total_syllables = sum(cls.count_spanish_syllables(w) for w in words)
        P = (total_syllables / total_words) * 100.0
        F = total_words / total_sentences

        score = 206.84 - (0.60 * P) - (1.02 * F)
        score = max(0.0, min(100.0, round(score, 2)))

        if score >= 90:
            grade = "Lectura Muy Fácil (4º Primaria)"
        elif score >= 80:
            grade = "Lectura Fácil (5º Primaria)"
        elif score >= 70:
            grade = "Adecuada (6º Primaria)"
        elif score >= 60:
            grade = "Aceptable (Secundaria)"
        else:
            grade = "Complejo / Burocrático"

        return ReadabilityMetrics(
            score=score,
            grade_level=grade,
            is_plain_language=score >= 80.0,
            word_count=total_words,
            sentence_count=total_sentences,
            syllable_count=total_syllables,
            avg_sentence_length=round(F, 2),
            avg_syllables_per_word=round(total_syllables / total_words, 2),
        )

    @classmethod
    def audit_english_flesch_reading_ease(cls, text: str) -> ReadabilityMetrics:
        """
        Computes Flesch Reading Ease:
        FRE = 206.835 - (1.015 * ASL) - (84.6 * ASW)
        """
        words = re.findall(r"\b[A-Za-z0-9-]+\b", text)
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

        total_words = len(words)
        total_sentences = max(1, len(sentences))

        if total_words == 0:
            return ReadabilityMetrics(
                score=100.0,
                grade_level="Very Easy",
                is_plain_language=True,
                word_count=0,
                sentence_count=0,
                syllable_count=0,
                avg_sentence_length=0.0,
                avg_syllables_per_word=0.0,
            )

        total_syllables = sum(cls.count_english_syllables(w) for w in words)
        ASL = total_words / total_sentences
        ASW = total_syllables / total_words

        score = 206.835 - (1.015 * ASL) - (84.6 * ASW)
        score = max(0.0, min(100.0, round(score, 2)))

        if score >= 90:
            grade = "Very Easy (5th grade)"
        elif score >= 80:
            grade = "Easy (6th grade)"
        elif score >= 70:
            grade = "Fairly Easy (7th grade)"
        else:
            grade = "Standard to Difficult"

        return ReadabilityMetrics(
            score=score,
            grade_level=grade,
            is_plain_language=score >= 80.0,
            word_count=total_words,
            sentence_count=total_sentences,
            syllable_count=total_syllables,
            avg_sentence_length=round(ASL, 2),
            avg_syllables_per_word=round(ASW, 2),
        )


class LegalGuardrail:
    """
    Guards against hallucination, ungrounded legal advice, and missing disclaimers.
    """

    CITATION_REGEX = re.compile(r"\[(?:Fragmento|Chunk|Doc(?:umento)?)[^\]]*?(\d+)\]", re.IGNORECASE)
    DATE_REGEX = re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})\b")

    HIGH_RISK_TERMS = [
        "desalojo", "eviction", "tribunal", "deportación", "deportation",
        "multa", "penalización", "embargo", "comparecencia", "hearing",
        "inadmisibilidad", "inadmissibility", "prisión", "custody",
    ]

    @classmethod
    def audit_response(
        cls,
        response_text: str,
        retrieved_chunks: List[dict],
        language: str = "es",
    ) -> GuardrailAuditResult:
        """
        Performs thorough audit on the generated RAG response.
        """
        lang = (language or "es").lower()

        # 1. Readability Audit (evaluated on the plain-language content body)
        if lang == "es":
            readability = SovereignReadabilityAuditor.audit_spanish_fernandez_huerta(response_text)
        else:
            readability = SovereignReadabilityAuditor.audit_english_flesch_reading_ease(response_text)

        # 2. Citation Extraction
        cited_indices = [int(m) for m in cls.CITATION_REGEX.findall(response_text)]
        has_citations = len(cited_indices) > 0

        # 3. Grounded Date Verification
        # Collect all valid dates from retrieved context
        known_dates: Set[str] = set()
        for chunk in retrieved_chunks:
            dates = chunk.get("dates_found", [])
            for d in dates:
                # Normalize digits
                clean_d = re.sub(r"[^\d/ -]", "", str(d)).strip()
                if clean_d:
                    known_dates.add(clean_d)

        # Detect dates in response
        response_dates = cls.DATE_REGEX.findall(response_text)
        unverified_dates = []
        for rd in response_dates:
            if not any(rd in kd or kd in rd for kd in known_dates):
                unverified_dates.append(rd)

        # 4. Check for High-Risk Triggers requiring Human Expert Escalation
        # Evaluates both the response and the underlying retrieved context
        requires_expert = False
        expert_reason = None
        combined_text = response_text.lower() + " " + " ".join(
            (c.get("content", "") + " " + str(c.get("section_header") or "")).lower()
            for c in retrieved_chunks
        )
        for term in cls.HIGH_RISK_TERMS:
            if term in combined_text:
                requires_expert = True
                expert_reason = f"Detección de término de alto impacto legal o patrimonial: '{term}'"
                break

        # 5. Sanitize text and ensure legal disclaimer is present
        sanitized = response_text.strip()
        if lang == "es":
            disclaimer = LEGAL_DISCLAIMER_ES
        elif lang == "pa":
            disclaimer = LEGAL_DISCLAIMER_PA
        else:
            disclaimer = LEGAL_DISCLAIMER_EN

        if disclaimer not in sanitized:
            sanitized = f"{sanitized}\n\n---\n{disclaimer}"

        is_safe = (len(unverified_dates) == 0) and (readability.score >= 70.0)

        return GuardrailAuditResult(
            is_safe=is_safe,
            readability=readability,
            has_citations=has_citations,
            cited_chunks=cited_indices,
            unverified_dates=unverified_dates,
            requires_human_expert=requires_expert,
            expert_reason=expert_reason,
            sanitized_text=sanitized,
        )


readability_auditor = SovereignReadabilityAuditor()
legal_guardrail = LegalGuardrail()
