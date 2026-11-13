"""
Unit Tests for Sovereign Legal Guardrails
Validates anti-hallucination, mandatory citation extraction, and expert escalation triggers.
"""

import unittest
from RAG.pipeline.guardrails import legal_guardrail
from RAG.prompts.plain_language import LEGAL_DISCLAIMER_ES


class TestLegalGuardrails(unittest.TestCase):
    def setUp(self):
        self.guardrail = legal_guardrail

    def test_citation_extraction(self):
        """Verifies chunk citation references are accurately extracted."""
        response = (
            "El tribunal fijó la fecha de audiencia [Fragmento: 2]. "
            "El importe adeudado es de mil dólares [Fragmento: 0]."
        )
        audit = self.guardrail.audit_response(response, [], language="es")
        self.assertTrue(audit.has_citations)
        self.assertEqual(audit.cited_chunks, [2, 0])

    def test_anti_hallucination_unverified_dates(self):
        """Flags dates mentioned in response that do not exist in source chunks."""
        retrieved_chunks = [
            {"chunk_index": 0, "content": "Aviso emitido", "dates_found": ["2026-11-20"]}
        ]

        # Case 1: Grounded date
        grounded_resp = "Debe comparecer el 2026-11-20 [Fragmento: 0]."
        audit_grounded = self.guardrail.audit_response(grounded_resp, retrieved_chunks, language="es")
        self.assertEqual(len(audit_grounded.unverified_dates), 0)

        # Case 2: Hallucinated date
        hallucinated_resp = "Tiene plazo hasta el 2026-12-31 [Fragmento: 0]."
        audit_hallucinated = self.guardrail.audit_response(hallucinated_resp, retrieved_chunks, language="es")
        self.assertIn("2026-12-31", audit_hallucinated.unverified_dates)
        self.assertFalse(audit_hallucinated.is_safe)

    def test_legal_disclaimer_attachment(self):
        """Verifies canonical legal disclaimer is appended if missing."""
        raw_text = "Esta es una explicación sencilla de su trámite [Fragmento: 1]."
        audit = self.guardrail.audit_response(raw_text, [], language="es")
        self.assertIn(LEGAL_DISCLAIMER_ES, audit.sanitized_text)

    def test_human_expert_escalation_triggers(self):
        """Triggers requires_human_expert=True on high-risk legal/eviction terms."""
        eviction_resp = "Ha recibido una orden de desalojo del tribunal [Fragmento: 1]."
        audit = self.guardrail.audit_response(eviction_resp, [], language="es")
        self.assertTrue(audit.requires_human_expert)
        self.assertIsNotNone(audit.expert_reason)
        self.assertIn("desalojo", audit.expert_reason.lower())


if __name__ == "__main__":
    unittest.main()

