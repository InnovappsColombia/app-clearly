"""
Unit Tests for Legal & Ethical Guardrails (IRPA Section 91 & Medical Boundaries)
"""

import unittest
import sys
from pathlib import Path

# Add Backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.legal_guardrail import (
    LegalGuardrailViolation,
    assert_no_unauthorized_advice,
    audit_legal_guardrails,
)


class TestLegalGuardrail(unittest.TestCase):
    def test_prohibited_legal_advice_raises_violation(self):
        forbidden_phrases = [
            "Usted debe demandar al propietario ante el tribunal.",
            "Tiene que apelar esta resolución de inmediato.",
            "Le recomiendo no contestar y acudir a los medios.",
            "Mi consejo legal es no firmar el acuerdo.",
            "No pague la renta de este mes bajo ninguna circunstancia.",
            "Ignore esta carta porque el oficial cometió un error.",
            "Su diagnóstico médico indica que necesita cirugía urgente.",
        ]
        for phrase in forbidden_phrases:
            with self.subTest(phrase=phrase):
                with self.assertRaises(LegalGuardrailViolation):
                    assert_no_unauthorized_advice(phrase)

    def test_clean_plain_language_passes(self):
        clean_phrases = [
            "Esta carta es un aviso de su tribunal de vivienda.",
            "Le informan sobre el alquiler pendiente de su hogar.",
            "Debe enviar los documentos solicitados antes del 15 de diciembre.",
            "Guarde este papel en un lugar seguro con sus identificaciones.",
        ]
        for phrase in clean_phrases:
            with self.subTest(phrase=phrase):
                try:
                    assert_no_unauthorized_advice(phrase)
                except LegalGuardrailViolation:
                    self.fail(f"Clean phrase raised unexpected LegalGuardrailViolation: {phrase}")

    def test_audit_escalates_to_human_expert(self):
        # Removal order / deportation text
        critical_doc = "Se emite una orden de expulsión (removal order) bajo la ley de inmigración."
        audit = audit_legal_guardrails(critical_doc)
        self.assertTrue(audit.requires_human_expert)
        self.assertIn(audit.risk_level, ["medium", "high"])

    def test_audit_flags_violations(self):
        bad_text = "Le recomiendo apelar ante la corte judicial."
        audit = audit_legal_guardrails(bad_text)
        self.assertFalse(audit.is_valid)
        self.assertEqual(audit.risk_level, "high")
        self.assertTrue(audit.requires_human_expert)
        self.assertGreater(len(audit.violations), 0)


if __name__ == "__main__":
    unittest.main()

