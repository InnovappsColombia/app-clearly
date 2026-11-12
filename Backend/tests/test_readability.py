"""
Unit Tests for Fernández-Huerta Readability Auditor (FH >= 80)
"""

import unittest
import sys
from pathlib import Path

# Add Backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.readability import (
    audit_readability,
    calculate_fernandez_huerta,
    classify_readability,
    simplify_bureaucratic_text,
)


class TestReadabilityAuditor(unittest.TestCase):
    def test_plain_language_meets_threshold(self):
        """Plain language designed for seniors should achieve FH >= 80."""
        text = (
            "Esta carta es de su ciudad. "
            "Debe enviar su foto hoy. "
            "Tiene diez días para responder. "
            "Guarde este papel en su casa."
        )
        score = calculate_fernandez_huerta(text)
        self.assertGreaterEqual(score, 80.0, f"Expected FH >= 80, got {score}")
        audit = audit_readability(text)
        self.assertTrue(audit.is_acceptable)
        self.assertIn(audit.category, ["Muy fácil", "Fácil"])

    def test_bureaucratic_text_fails_threshold(self):
        """Complex legal/administrative text should fail FH >= 80."""
        text = (
            "De conformidad con lo dispuesto en el artículo octavo del reglamento administrativo "
            "correspondiente a los procedimientos de desahucio y rescisión contractual, se le "
            "notifica que fenecido el plazo improrrogable sin subsanar la controversia, se "
            "procederá conforme a derecho mediante las acciones judiciales pertinentes."
        )
        score = calculate_fernandez_huerta(text)
        self.assertLess(score, 60.0, f"Expected complex text FH < 60, got {score}")
        audit = audit_readability(text)
        self.assertFalse(audit.is_acceptable)
        self.assertGreater(len(audit.recommendations), 0)

    def test_classification_scale(self):
        cat, level = classify_readability(95.0)
        self.assertEqual(cat, "Muy fácil")

        cat, level = classify_readability(82.0)
        self.assertEqual(cat, "Fácil")

        cat, level = classify_readability(45.0)
        self.assertEqual(cat, "Difícil")

    def test_bureaucratic_simplification(self):
        text = "De conformidad con la ley, fenecido el plazo se procederá al pago."
        simplified = simplify_bureaucratic_text(text)
        self.assertIn("según", simplified)
        self.assertIn("vencido el tiempo", simplified)
        self.assertIn("pagar", simplified)


if __name__ == "__main__":
    unittest.main()

