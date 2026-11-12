"""
CLEARLY — Deterministic Date Extraction & Temporal Arithmetic Engine
FMEA FM-02 Mitigation: Prevents LLM date arithmetic hallucination by extracting
base dates and operators, then executing 100% deterministic calendar calculations.
"""

import re
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

# Month mapping for Spanish and English
MONTH_NAMES = {
    # Spanish
    "enero": 1, "ene": 1,
    "febrero": 2, "feb": 2,
    "marzo": 3, "mar": 3,
    "abril": 4, "abr": 4,
    "mayo": 5, "may": 5,
    "junio": 6, "jun": 6,
    "julio": 7, "jul": 7,
    "agosto": 8, "ago": 8,
    "septiembre": 9, "setiembre": 9, "sep": 9, "sept": 9,
    "octubre": 10, "oct": 10,
    "noviembre": 11, "nov": 11,
    "diciembre": 12, "dic": 12,
    # English
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12, "dec": 12,
}


class ExtractedDeadline(BaseModel):
    deadline_date: Optional[date] = None
    base_date: Optional[date] = None
    offset_days: Optional[int] = None
    is_business_days: bool = False
    operator: str = "none"
    urgency: str = "low"  # low, medium, high, critical
    days_remaining: Optional[int] = None
    tutor_alert_required: bool = False
    raw_snippet: Optional[str] = None
    confidence: float = 1.0


def add_business_days(start_date: date, num_days: int) -> date:
    """Deterministically add business days (excluding Saturdays and Sundays)."""
    current = start_date
    added = 0
    while added < num_days:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Monday to Friday
            added += 1
    return current


def parse_spanish_text_date(day_str: str, month_str: str, year_str: Optional[str] = None) -> Optional[date]:
    """Parse textual dates like '15 de octubre de 2026'."""
    try:
        day = int(day_str)
        month_clean = month_str.lower().strip("., ")
        month = MONTH_NAMES.get(month_clean)
        if not month:
            return None
        year = int(year_str) if year_str else date.today().year
        return date(year, month, day)
    except (ValueError, TypeError):
        return None


def parse_iso_or_numeric_date(date_str: str) -> Optional[date]:
    """Parse ISO (YYYY-MM-DD) or DD/MM/YYYY formats."""
    # YYYY-MM-DD
    iso_match = re.search(r"\b(20\d{2})[-/.](0[1-9]|1[0-2])[-/.](0[1-9]|[12]\d|3[01])\b", date_str)
    if iso_match:
        try:
            return date(int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3)))
        except ValueError:
            pass

    # DD/MM/YYYY or DD-MM-YYYY
    dmy_match = re.search(r"\b(0?[1-9]|[12]\d|3[01])[-/.](0?[1-9]|1[0-2])[-/.](20\d{2})\b", date_str)
    if dmy_match:
        try:
            return date(int(dmy_match.group(3)), int(dmy_match.group(2)), int(dmy_match.group(1)))
        except ValueError:
            pass

    return None


def extract_base_date(text: str) -> Optional[date]:
    """
    Extract the issuing or notice base date from a document.
    Matches anchors like 'fecha de emisión', 'date of notice', 'matasellos', etc.
    """
    # 1. Textual Spanish notice dates: e.g. "Fecha de emisión: 30 de octubre de 2026"
    base_anchor_patterns = [
        r"(?:fecha\s+de\s+(?:emisi[oó]n|notificaci[oó]n|la\s+carta)|matasellos|postmarked|issued\s+on|date\s+of\s+notice)[\s:]*([0-9]{1,2})\s+de\s+([a-zA-ZáéíóúÁÉÍÓÚ]+)(?:\s+de|\s+del)?\s+([0-9]{4})?",
        r"(?:fecha\s+de\s+(?:emisi[oó]n|notificaci[oó]n|la\s+carta)|matasellos|issued\s+on)[\s:]*([0-9]{4}[-/.][0-9]{2}[-/.][0-9]{2})",
        r"(?:fecha\s+de\s+(?:emisi[oó]n|notificaci[oó]n|la\s+carta)|matasellos|issued\s+on)[\s:]*([0-9]{1,2}[-/.][0-9]{1,2}[-/.][0-9]{4})",
    ]

    for pat in base_anchor_patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 3 and groups[1]:
                parsed = parse_spanish_text_date(groups[0], groups[1], groups[2])
                if parsed:
                    return parsed
            elif len(groups) >= 1 and groups[0]:
                parsed = parse_iso_or_numeric_date(groups[0])
                if parsed:
                    return parsed

    # General date search if anchor not found
    textual_date = re.search(r"\b([0-9]{1,2})\s+de\s+([a-zA-ZáéíóúÁÉÍÓÚ]+)(?:\s+de|\s+del)?\s+(20\d{2})\b", text, re.IGNORECASE)
    if textual_date:
        parsed = parse_spanish_text_date(textual_date.group(1), textual_date.group(2), textual_date.group(3))
        if parsed:
            return parsed

    return None


def calculate_urgency(deadline: date, reference_date: Optional[date] = None) -> Tuple[str, int, bool]:
    """
    Calculate urgency category, days remaining, and whether tutor alert is required.
    
    Urgency scale:
    - critical: <= 3 days (< 72 hours)
    - high: <= 14 days (< 15 days) -> triggers tutor alert
    - medium: <= 30 days
    - low: > 30 days
    """
    ref = reference_date or date.today()
    delta = (deadline - ref).days
    days_remaining = max(0, delta)

    if delta <= 3:
        urgency = "critical"
        tutor_alert = True
    elif delta <= 14:
        urgency = "high"
        tutor_alert = True
    elif delta <= 30:
        urgency = "medium"
        tutor_alert = False
    else:
        urgency = "low"
        tutor_alert = False

    return urgency, days_remaining, tutor_alert


def extract_deterministic_deadline(text: str, reference_date: Optional[date] = None) -> ExtractedDeadline:
    """
    Main deterministic temporal extraction engine.
    1. Looks for relative offset patterns ('dentro de 14 días a partir de...', 'plazo de 30 días').
    2. Identifies base date (or defaults to reference_date).
    3. Uses deterministic calendar / business days calculation to compute exact deadline date.
    4. If no relative offset is found, searches for explicit deadline dates.
    5. Calculates remaining days and urgency.
    """
    ref = reference_date or date.today()
    base_date = extract_base_date(text) or ref

    # --- Pattern 1: Relative offset (e.g., '14 días a partir de...', 'plazo de 30 días') ---
    # Matches: "14 días", "30 días hábiles", "15 días naturales", "48 horas", "72 horas"
    relative_patterns = [
        # e.g.: "plazo de 14 días a partir de la fecha de esta notificación (30 de octubre de 2026)"
        r"(?:plazo\s+de|dentro\s+de(?:l)?(?:\s+plazo\s+de)?|a\s+m[aá]s\s+tardar\s+en)\s+([0-9]{1,3})\s+d[ií]as(?:\s+(h[aá]biles|laborables|naturales|corridos))?(?:\s+(?:a\s+partir\s+de|posteriores\s+a|tras)\s+([^\n.]+))?",
        r"([0-9]{1,3})\s+d[ií]as(?:\s+(h[aá]biles|laborables|naturales|corridos))?\s+para\s+(?:responder|apelar|subsanar|pagar|presentar|cumplir)",
        r"(?:en|dentro\s+de)\s+([0-9]{1,2})\s+horas",
    ]

    for pat in relative_patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            raw_snippet = match.group(0)
            groups = match.groups()

            # Check if hours
            if "hora" in raw_snippet.lower():
                hours = int(groups[0])
                days_offset = max(1, hours // 24)
                deadline_date = base_date + timedelta(days=days_offset)
                urgency, remaining, alert = calculate_urgency(deadline_date, ref)
                return ExtractedDeadline(
                    deadline_date=deadline_date,
                    base_date=base_date,
                    offset_days=days_offset,
                    is_business_days=False,
                    operator=f"+{hours}h",
                    urgency="critical",
                    days_remaining=remaining,
                    tutor_alert_required=True,
                    raw_snippet=raw_snippet,
                    confidence=0.98,
                )

            # Days extraction
            days_count = int(groups[0])
            day_type = (groups[1] or "").lower() if len(groups) > 1 else ""
            is_business = bool(re.search(r"h[aá]bil|laborable", day_type, re.IGNORECASE))

            # If anchor text has an explicit base date mentioned inside it, use it
            if len(groups) > 2 and groups[2]:
                local_base = extract_base_date(groups[2])
                if local_base:
                    base_date = local_base

            if is_business:
                deadline_date = add_business_days(base_date, days_count)
                operator_str = f"+{days_count} business_days"
            else:
                deadline_date = base_date + timedelta(days=days_count)
                operator_str = f"+{days_count}d"

            urgency, remaining, alert = calculate_urgency(deadline_date, ref)
            return ExtractedDeadline(
                deadline_date=deadline_date,
                base_date=base_date,
                offset_days=days_count,
                is_business_days=is_business,
                operator=operator_str,
                urgency=urgency,
                days_remaining=remaining,
                tutor_alert_required=alert,
                raw_snippet=raw_snippet,
                confidence=0.99,
            )

    # --- Pattern 2: Explicit deadline anchors ---
    # e.g.: "Fecha límite: 15 de diciembre de 2026", "a más tardar el 2026-12-15"
    deadline_anchor_patterns = [
        r"(?:fecha\s+l[ií]mite|vence\s+el|a\s+m[aá]s\s+tardar\s+el|antes\s+del|plazo\s+m[aá]ximo|fecha\s+de\s+audiencia|due\s+date|hearing\s+date)[\s:]*([0-9]{1,2})\s+de\s+([a-zA-ZáéíóúÁÉÍÓÚ]+)(?:\s+de|\s+del)?\s+([0-9]{4})?",
        r"(?:fecha\s+l[ií]mite|vence\s+el|a\s+m[aá]s\s+tardar\s+el|antes\s+del|plazo\s+m[aá]ximo|due\s+date)[\s:]*([0-9]{4}[-/.][0-9]{2}[-/.][0-9]{2})",
        r"(?:fecha\s+l[ií]mite|vence\s+el|a\s+m[aá]s\s+tardar\s+el|antes\s+del|plazo\s+m[aá]ximo|due\s+date)[\s:]*([0-9]{1,2}[-/.][0-9]{1,2}[-/.][0-9]{4})",
    ]

    for pat in deadline_anchor_patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            raw_snippet = match.group(0)
            groups = match.groups()
            deadline_date = None
            if len(groups) == 3 and groups[1]:
                deadline_date = parse_spanish_text_date(groups[0], groups[1], groups[2])
            elif len(groups) >= 1 and groups[0]:
                deadline_date = parse_iso_or_numeric_date(groups[0])

            if deadline_date:
                urgency, remaining, alert = calculate_urgency(deadline_date, ref)
                return ExtractedDeadline(
                    deadline_date=deadline_date,
                    base_date=base_date,
                    offset_days=(deadline_date - base_date).days,
                    is_business_days=False,
                    operator="absolute",
                    urgency=urgency,
                    days_remaining=remaining,
                    tutor_alert_required=alert,
                    raw_snippet=raw_snippet,
                    confidence=0.99,
                )

    # No deadline found
    return ExtractedDeadline(
        deadline_date=None,
        base_date=base_date,
        urgency="low",
        days_remaining=None,
        tutor_alert_required=False,
        operator="none",
        confidence=0.0,
    )
