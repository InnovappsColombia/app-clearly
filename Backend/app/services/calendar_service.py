r"""
CLEARLY — Production RFC 5545 iCalendar (.ICS) Generator & Validator
Follows the official IETF RFC 5545 specification with:
- Strict CRLF line terminations (\r\n)
- 75-octet line folding
- Standard character escaping (\\, \;, \,, \\n)
- Zero external dependencies to prevent supply chain vulnerabilities
"""

from datetime import datetime, timezone
import re
from typing import List, Optional, Tuple


def rfc5545_escape_text(text: str) -> str:
    """
    Escape text according to RFC 5545 Section 3.3.11.
    A backslash, semicolon, comma, or newline must be escaped.
    """
    if not text:
        return ""
    # Backslash first
    res = text.replace("\\", "\\\\")
    res = res.replace(";", "\\;")
    res = res.replace(",", "\\,")
    res = res.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")
    return res


def fold_line(line: str, max_octets: int = 75) -> str:
    """
    Fold long lines according to RFC 5545 Section 3.1.
    Lines of text SHOULD NOT be longer than 75 octets, excluding line break.
    Long lines are folded by inserting CRLF followed by a single space or tab.
    """
    encoded = line.encode("utf-8")
    if len(encoded) <= max_octets:
        return line

    parts = []
    current_line = bytearray()
    
    # We fold cleanly by UTF-8 byte boundary
    i = 0
    first_line = True
    limit = max_octets
    
    while i < len(encoded):
        chunk_limit = limit if first_line else (limit - 1)  # subtract 1 for the leading space
        # Take up to chunk_limit bytes without breaking a multi-byte UTF-8 character
        end = min(i + chunk_limit, len(encoded))
        # Ensure we do not split a multi-byte UTF-8 code point
        while end < len(encoded) and (encoded[end] & 0xC0) == 0x80:
            end -= 1
        
        piece = encoded[i:end]
        if first_line:
            parts.append(piece.decode("utf-8"))
            first_line = False
        else:
            parts.append(" " + piece.decode("utf-8"))
        i = end

    return "\r\n".join(parts)


def format_ics_datetime(dt: datetime) -> str:
    """Format datetime into RFC 5545 timestamp YYYYMMDDTHHMMSSZ."""
    if dt.tzinfo is None:
        # Assume UTC if naive
        dt_utc = dt.replace(tzinfo=timezone.utc)
    else:
        dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.strftime("%Y%m%dT%H%M%SZ")


class RFC5545CalendarGenerator:
    """
    Production-grade iCalendar (.ics) generator.
    """

    @classmethod
    def generate_event_ics(
        cls,
        event_id: str,
        title: str,
        description: str,
        location: str,
        start_datetime: datetime,
        end_datetime: Optional[datetime] = None,
        organizer_name: Optional[str] = None,
        organizer_email: Optional[str] = None,
        url: Optional[str] = None,
    ) -> str:
        """
        Produce a strictly compliant RFC 5545 iCalendar document string.
        """
        now = datetime.now(timezone.utc)
        dtstamp = format_ics_datetime(now)
        dtstart = format_ics_datetime(start_datetime)
        dtend = format_ics_datetime(end_datetime) if end_datetime else format_ics_datetime(start_datetime)
        uid = f"{event_id}-{now.strftime('%Y%m%d%H%M%S')}@clearly.community"

        raw_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//CLEARLY//Civic Inclusion & Accessibility Events//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp}",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}",
            f"SUMMARY:{rfc5545_escape_text(title)}",
            f"LOCATION:{rfc5545_escape_text(location)}",
            f"DESCRIPTION:{rfc5545_escape_text(description)}",
            "STATUS:CONFIRMED",
            "TRANSP:OPAQUE",
        ]

        if url:
            raw_lines.append(f"URL:{url.strip()}")
        if organizer_name and organizer_email:
            raw_lines.append(f"ORGANIZER;CN={rfc5545_escape_text(organizer_name)}:mailto:{organizer_email.strip()}")
        elif organizer_name:
            raw_lines.append(f"ORGANIZER;CN={rfc5545_escape_text(organizer_name)}:mailto:support@clearly.community")

        raw_lines.append("END:VEVENT")
        raw_lines.append("END:VCALENDAR")

        # Fold lines according to RFC 5545
        folded_lines = [fold_line(line) for line in raw_lines]
        # Must terminate with CRLF
        return "\r\n".join(folded_lines) + "\r\n"

    @classmethod
    def validate_syntax(cls, ics_content: str) -> Tuple[bool, List[str]]:
        """
        Validate iCalendar text against core RFC 5545 invariants.
        Returns (is_valid, list_of_errors).
        """
        errors = []
        if not ics_content:
            return False, ["Contenido iCalendar vacío."]

        # Check line endings: must contain CRLF
        if "\r\n" not in ics_content:
            errors.append("Las líneas deben terminar con CRLF (\\r\\n).")

        lines = ics_content.split("\r\n")
        # Remove trailing empty string from split
        if lines and lines[-1] == "":
            lines.pop()

        # Check required tags
        has_vcal_begin = any(l == "BEGIN:VCALENDAR" for l in lines)
        has_vcal_end = any(l == "END:VCALENDAR" for l in lines)
        has_vevent_begin = any(l == "BEGIN:VEVENT" for l in lines)
        has_vevent_end = any(l == "END:VEVENT" for l in lines)
        has_version = any(l == "VERSION:2.0" for l in lines)
        has_prodid = any(l.startswith("PRODID:") for l in lines)
        has_uid = any(l.startswith("UID:") for l in lines)
        has_dtstart = any(l.startswith("DTSTART:") for l in lines)
        has_summary = any(l.startswith("SUMMARY:") for l in lines)

        if not has_vcal_begin:
            errors.append("Falta 'BEGIN:VCALENDAR'.")
        if not has_vcal_end:
            errors.append("Falta 'END:VCALENDAR'.")
        if not has_vevent_begin:
            errors.append("Falta 'BEGIN:VEVENT'.")
        if not has_vevent_end:
            errors.append("Falta 'END:VEVENT'.")
        if not has_version:
            errors.append("Falta 'VERSION:2.0'.")
        if not has_prodid:
            errors.append("Falta 'PRODID'.")
        if not has_uid:
            errors.append("Falta 'UID'.")
        if not has_dtstart:
            errors.append("Falta 'DTSTART'.")
        if not has_summary:
            errors.append("Falta 'SUMMARY'.")

        # Check line length (no line should exceed 75 octets without folding)
        for idx, line in enumerate(lines, 1):
            if len(line.encode("utf-8")) > 75:
                errors.append(f"Línea {idx} excede el límite de 75 octetos sin plegado RFC 5545.")

        return len(errors) == 0, errors
