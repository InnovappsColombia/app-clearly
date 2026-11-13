"""
CLEARLY — Semantic Document Chunker
Tailored for Canadian administrative, legal, and community documents
(IRCC, Ontario LTB, CRA, Service Canada, Municipal Civic Bulletins).

Key Features:
- Section-aware hierarchical splitting (Headers -> Paragraphs -> Sentences).
- Boundary overlap preservation for context continuity.
- Automatic metadata extraction per chunk (section header, dates, amounts, token count).
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


@dataclass
class ChunkData:
    chunk_index: int
    content: str
    token_count: int
    char_count: int
    section_header: Optional[str] = None
    dates_found: List[str] = field(default_factory=list)
    amounts_found: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunk_id: str = field(default_factory=lambda: str(uuid4()))


class SemanticChunker:
    """
    Splits text documents into semantically coherent chunks with overlap,
    preserving structural headers, deadlines, and financial amounts.
    """

    # Section header patterns (Markdown headers, ALL CAPS lines, numbered sections)
    HEADER_REGEX = re.compile(
        r"^(?:#{1,6}\s+|[0-9]+\.\s+|[A-ZÁÉÍÓÚÑ\s]{4,}:|[A-Z][a-zA-Z\s]{3,}:)(.+)$",
        re.MULTILINE,
    )

    # Date detection regex (ISO, English, Spanish formats)
    DATE_REGEX = re.compile(
        r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|"
        r"(?:January|February|March|April|May|June|July|August|September|October|November|December|"
        r"Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre)"
        r"\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}|"
        r"\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+\d{4})\b",
        re.IGNORECASE,
    )

    # Currency amount detection
    CURRENCY_REGEX = re.compile(r"\$\s?[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?(?:\s?(?:CAD|USD))?")

    def __init__(
        self,
        max_chunk_chars: int = 1200,
        chunk_overlap_chars: int = 200,
        approx_chars_per_token: float = 3.8,
    ):
        self.max_chunk_chars = max_chunk_chars
        self.chunk_overlap_chars = chunk_overlap_chars
        self.chars_per_token = approx_chars_per_token

    def chunk_document(
        self,
        text: str,
        document_id: Optional[str] = None,
        base_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[ChunkData]:
        """
        Processes full document text into an ordered list of structured chunks.
        """
        clean_text = (text or "").strip()
        if not clean_text:
            return []

        base_meta = base_metadata or {}
        sections = self._split_into_sections(clean_text)
        chunks: List[ChunkData] = []
        chunk_idx = 0

        for sec_header, sec_text in sections:
            # If section fits within max chunk size, keep intact
            if len(sec_text) <= self.max_chunk_chars:
                chunk = self._build_chunk(
                    chunk_index=chunk_idx,
                    content=sec_text,
                    section_header=sec_header,
                    document_id=document_id,
                    extra_meta=base_meta,
                )
                chunks.append(chunk)
                chunk_idx += 1
            else:
                # Subdivide large section into overlapping chunks
                sub_chunks = self._subdivide_section(
                    text=sec_text,
                    section_header=sec_header,
                    start_index=chunk_idx,
                    document_id=document_id,
                    extra_meta=base_meta,
                )
                chunks.extend(sub_chunks)
                chunk_idx += len(sub_chunks)

        return chunks

    def _split_into_sections(self, text: str) -> List[Tuple[Optional[str], str]]:
        """
        Splits document by recognized structural headers.
        Returns list of (header_name, section_body) tuples.
        """
        lines = text.splitlines()
        sections: List[Tuple[Optional[str], str]] = []
        current_header: Optional[str] = None
        current_buffer: List[str] = []

        for line in lines:
            line_str = line.strip()
            # Check if this line looks like a header
            is_header = False
            header_name = None

            if line_str.startswith("#"):
                is_header = True
                header_name = line_str.lstrip("#").strip()
            elif len(line_str) > 4 and line_str.isupper() and len(line_str) < 80:
                is_header = True
                header_name = line_str
            elif ":" in line_str and len(line_str.split(":")[0]) < 40 and not line_str.startswith("http"):
                # E.g. "Motivo del Aviso:", "Important Notice:"
                prefix = line_str.split(":")[0].strip()
                if any(w in prefix.lower() for w in ["aviso", "notice", "fecha", "date", "asunto", "re:", "sección", "section", "instrucción"]):
                    is_header = True
                    header_name = line_str

            if is_header:
                if current_buffer:
                    body = "\n".join(current_buffer).strip()
                    if body:
                        sections.append((current_header, body))
                    current_buffer = []
                current_header = header_name or line_str
            else:
                current_buffer.append(line)

        # Flush remaining
        if current_buffer:
            body = "\n".join(current_buffer).strip()
            if body:
                sections.append((current_header, body))

        if not sections:
            sections = [(None, text)]

        return sections

    def _subdivide_section(
        self,
        text: str,
        section_header: Optional[str],
        start_index: int,
        document_id: Optional[str],
        extra_meta: Dict[str, Any],
    ) -> List[ChunkData]:
        """
        Recursively splits a large section into overlapping sentence-aware chunks.
        """
        # Split by paragraphs first
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: List[ChunkData] = []
        current_text = ""
        idx = start_index

        for para in paragraphs:
            if len(current_text) + len(para) + 2 <= self.max_chunk_chars:
                current_text = f"{current_text}\n\n{para}".strip()
            else:
                if current_text:
                    chunks.append(
                        self._build_chunk(
                            chunk_index=idx,
                            content=current_text,
                            section_header=section_header,
                            document_id=document_id,
                            extra_meta=extra_meta,
                        )
                    )
                    idx += 1
                    # Retain overlap from end of current text
                    overlap = self._extract_overlap(current_text)
                    current_text = f"{overlap}\n\n{para}".strip()
                else:
                    # Single paragraph exceeds max_chunk_chars -> split by sentences
                    sentences = self._split_sentences(para)
                    for sentence in sentences:
                        if len(current_text) + len(sentence) + 1 <= self.max_chunk_chars:
                            current_text = f"{current_text} {sentence}".strip()
                        else:
                            if current_text:
                                chunks.append(
                                    self._build_chunk(
                                        chunk_index=idx,
                                        content=current_text,
                                        section_header=section_header,
                                        document_id=document_id,
                                        extra_meta=extra_meta,
                                    )
                                )
                                idx += 1
                                overlap = self._extract_overlap(current_text)
                                current_text = f"{overlap} {sentence}".strip()
                            else:
                                # Giant sentence: hard slice
                                chunks.append(
                                    self._build_chunk(
                                        chunk_index=idx,
                                        content=sentence[: self.max_chunk_chars],
                                        section_header=section_header,
                                        document_id=document_id,
                                        extra_meta=extra_meta,
                                    )
                                )
                                idx += 1
                                current_text = sentence[self.max_chunk_chars - self.chunk_overlap_chars :].strip()

        if current_text:
            chunks.append(
                self._build_chunk(
                    chunk_index=idx,
                    content=current_text,
                    section_header=section_header,
                    document_id=document_id,
                    extra_meta=extra_meta,
                )
            )

        return chunks

    def _extract_overlap(self, text: str) -> str:
        """Takes roughly chunk_overlap_chars from the end, starting at sentence or space."""
        if len(text) <= self.chunk_overlap_chars:
            return text
        slice_point = len(text) - self.chunk_overlap_chars
        # Look for period or space near slice_point
        space_idx = text.find(" ", slice_point)
        if space_idx != -1 and space_idx < len(text) - 20:
            return text[space_idx:].strip()
        return text[slice_point:].strip()

    def _split_sentences(self, text: str) -> List[str]:
        """Splits paragraph into sentences respecting abbreviations."""
        raw = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in raw if s.strip()]

    def _build_chunk(
        self,
        chunk_index: int,
        content: str,
        section_header: Optional[str],
        document_id: Optional[str],
        extra_meta: Dict[str, Any],
    ) -> ChunkData:
        """Constructs ChunkData with extracted metadata."""
        char_count = len(content)
        token_count = max(1, int(char_count / self.chars_per_token))
        scan_text = f"{section_header or ''}\n{content}"
        dates = list(set(self.DATE_REGEX.findall(scan_text)))
        amounts = list(set(self.CURRENCY_REGEX.findall(scan_text)))

        meta = dict(extra_meta)
        if document_id:
            meta["document_id"] = document_id

        return ChunkData(
            chunk_index=chunk_index,
            content=content,
            token_count=token_count,
            char_count=char_count,
            section_header=section_header,
            dates_found=dates,
            amounts_found=amounts,
            metadata=meta,
        )


semantic_chunker = SemanticChunker()
