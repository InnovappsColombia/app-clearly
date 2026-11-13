"""
CLEARLY — Prompt Management & Templates for Sovereign Local RAG
Provides structured prompts and formatting utilities for:
- Plain Language Transformation (FH >= 80 Spanish, FRE >= 80 English, Punjabi Gurmukhi).
- 6 Canonical Questions Framework for Civic Activities.
- Grounded QA with mandatory chunk citation and legal guardrails.
"""

from pathlib import Path
from typing import Dict, List, Optional


# Canonical Legal Disclaimers
LEGAL_DISCLAIMER_ES = (
    "Aviso Importante: CLEARLY simplifica textos para su fácil lectura pero no sustituye "
    "el asesoramiento legal ni representa a ninguna entidad oficial. Si tiene dudas críticas, "
    "consulte con un familiar o contacte a un profesional verificado en CLEARLY Premium."
)

LEGAL_DISCLAIMER_EN = (
    "Important Notice: CLEARLY simplifies documents for ease of reading but does not provide "
    "legal advice or represent any government agency. If in doubt, please consult a family tutor "
    "or connect with a verified professional on CLEARLY Premium."
)

LEGAL_DISCLAIMER_PA = (
    "ਮਹੱਤਵਪੂਰਨ ਸੂਚਨਾ: CLEARLY ਜਾਣਕਾਰੀ ਨੂੰ ਆਸਾਨ ਬਣਾਉਣ ਵਿੱਚ ਮਦਦ ਕਰਦਾ ਹੈ ਪਰ ਕਾਨੂੰਨੀ ਸਲਾਹ ਨਹੀਂ ਦਿੰਦਾ। "
    "ਲੋੜ ਪੈਣ 'ਤੇ ਪਰਿਵਾਰਕ ਮੈਂਬਰ ਜਾਂ ਮਾਹਰ ਨਾਲ ਸੰਪਰਕ ਕਰੋ।"
)


class PromptManager:
    TEMPLATES_DIR: Path = Path(__file__).resolve().parent / "templates"

    @classmethod
    def get_template(cls, template_name: str) -> str:
        """Reads markdown template from disk."""
        path = cls.TEMPLATES_DIR / template_name
        if path.is_file():
            return path.read_text(encoding="utf-8")
        raise FileNotFoundError(f"Template '{template_name}' not found at {path}")

    @classmethod
    def format_grounded_qa_prompt(
        cls,
        user_query: str,
        context_chunks: List[Dict[str, str]],
        language: str = "es",
    ) -> str:
        """
        Builds grounded QA prompt with numbered chunk contexts.
        """
        formatted_context_list = []
        for c in context_chunks:
            idx = c.get("chunk_index", 0)
            sec = c.get("section_header") or "Sección General"
            text = c.get("content", "").strip()
            formatted_context_list.append(f"--- [Fragmento {idx}: {sec}] ---\n{text}")

        context_str = "\n\n".join(formatted_context_list)
        template = cls.get_template("rag_grounded_qa.md")
        return template.replace("{context_chunks}", context_str).replace("{user_query}", user_query)

    @classmethod
    def get_disclaimer(cls, language: str = "es") -> str:
        """Returns language-appropriate legal disclaimer."""
        lang = (language or "es").lower()
        if lang == "es":
            return LEGAL_DISCLAIMER_ES
        elif lang == "pa":
            return LEGAL_DISCLAIMER_PA
        return LEGAL_DISCLAIMER_EN


prompt_manager = PromptManager()

