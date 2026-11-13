"""
Unit Tests for Sovereign Readability Auditor
Validates Fernández-Huerta (Spanish) and Flesch Reading Ease (English) algorithms.
"""

import unittest
from RAG.pipeline.guardrails import SovereignReadabilityAuditor, readability_auditor


class TestReadabilityAuditor(unittest.TestCase):
    def setUp(self):
        self.auditor = readability_auditor

    def test_spanish_syllables_hiatus_and_diphthongs(self):
        """Validates accurate Spanish syllable segmentation for hiatuses and diphthongs."""
        # Diphthongs (1 syllable)
        self.assertEqual(self.auditor.count_spanish_syllables("aire"), 2)   # ai-re
        self.assertEqual(self.auditor.count_spanish_syllables("bueno"), 2)  # bue-no
        self.assertEqual(self.auditor.count_spanish_syllables("ciudad"), 2) # ciu-dad

        # Hiatus with accented weak vowel (2 syllables)
        self.assertEqual(self.auditor.count_spanish_syllables("día"), 2)    # dí-a
        self.assertEqual(self.auditor.count_spanish_syllables("país"), 2)   # pa-ís
        self.assertEqual(self.auditor.count_spanish_syllables("caída"), 3)  # ca-í-da

        # Hiatus strong + strong
        self.assertEqual(self.auditor.count_spanish_syllables("teatro"), 3) # te-a-tro
        self.assertEqual(self.auditor.count_spanish_syllables("poema"), 3)  # po-e-ma

    def test_fernandez_huerta_plain_language_threshold(self):
        """
        Validates that senior-adapted plain language achieves FH >= 80.0
        and bureaucratic text scores < 60.0.
        """
        # Senior Plain Language sample (Short words, short sentences)
        senior_text = (
            "Este es un aviso de su casa. Debe pagar el alquiler antes del viernes. "
            "El pago es de mil dólares. Si tiene dudas, llame a su hijo o tutor. "
            "Estamos para ayudarle con calma."
        )
        metrics_plain = self.auditor.audit_spanish_fernandez_huerta(senior_text)
        self.assertGreaterEqual(
            metrics_plain.score,
            80.0,
            f"Plain language text should achieve FH >= 80.0, got {metrics_plain.score}",
        )
        self.assertTrue(metrics_plain.is_plain_language)

        # Bureaucratic text sample (High syllables, long subordinate clauses)
        bureaucratic_text = (
            "Habiéndose constatado fehacientemente la incomparecencia de la parte arrendataria, "
            "se procede conminatoriamente a la sustanciación del requerimiento judicial correspondiente, "
            "con apercibimiento de lanzamiento forzoso de conformidad con los preceptos normativos aplicables."
        )
        metrics_complex = self.auditor.audit_spanish_fernandez_huerta(bureaucratic_text)
        self.assertLess(
            metrics_complex.score,
            60.0,
            f"Bureaucratic text should score below 60.0, got {metrics_complex.score}",
        )
        self.assertFalse(metrics_complex.is_plain_language)

    def test_flesch_reading_ease_english_threshold(self):
        """Validates that plain English text achieves FRE >= 80.0."""
        senior_english = (
            "This is a notice about your home. You need to pay your rent by Friday. "
            "The total cost is ten dollars. Please call your son or helper if you have questions. "
            "We are here to help you."
        )
        metrics_en = self.auditor.audit_english_flesch_reading_ease(senior_english)
        self.assertGreaterEqual(
            metrics_en.score,
            80.0,
            f"Plain English should achieve FRE >= 80.0, got {metrics_en.score}",
        )
        self.assertTrue(metrics_en.is_plain_language)

    def test_empty_string_metrics(self):
        """Verifies empty string produces safe neutral metrics."""
        m_es = self.auditor.audit_spanish_fernandez_huerta("")
        self.assertEqual(m_es.score, 100.0)
        self.assertEqual(m_es.word_count, 0)


if __name__ == "__main__":
    unittest.main()

