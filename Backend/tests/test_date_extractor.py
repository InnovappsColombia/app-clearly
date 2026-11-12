"""
Unit Tests for Deterministic Date Extraction Engine (FMEA FM-02 Mitigation)
"""

import unittest
from datetime import date, timedelta
import sys
from pathlib import Path

# Add Backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.date_extractor import (
    add_business_days,
    calculate_urgency,
    extract_base_date,
    extract_deterministic_deadline,
)


class TestDateExtractor(unittest.TestCase):
    def test_fm02_fmea_benchmark_case(self):
        """
        FMEA FM-02 Ground Truth Test:
        Document states: 'plazo de 14 días a partir de la fecha del matasellos (30 de octubre de 2026)'
        Deterministic target: Exactly November 13, 2026 (0% error tolerance).
        """
        text = (
            "Notificación Oficial LTB Formulario N4.\n"
            "Fecha de la carta: 30 de octubre de 2026.\n"
            "Usted dispone de un plazo de 14 días a partir de la fecha de esta notificación para pagar el saldo."
        )
        res = extract_deterministic_deadline(text, reference_date=date(2026, 11, 1))

        self.assertEqual(res.base_date, date(2026, 10, 30))
        self.assertEqual(res.offset_days, 14)
        self.assertEqual(res.deadline_date, date(2026, 11, 13))
        self.assertEqual(res.operator, "+14d")
        # Remaining from Nov 1 to Nov 13 = 12 days -> high urgency -> triggers tutor alert!
        self.assertEqual(res.urgency, "high")
        self.assertTrue(res.tutor_alert_required)

    def test_explicit_textual_deadline(self):
        text = "Por favor remita su pasaporte. Fecha límite: 15 de diciembre de 2026."
        res = extract_deterministic_deadline(text, reference_date=date(2026, 11, 1))

        self.assertEqual(res.deadline_date, date(2026, 12, 15))
        self.assertEqual(res.operator, "absolute")
        # 44 days remaining -> low urgency
        self.assertEqual(res.urgency, "low")
        self.assertFalse(res.tutor_alert_required)

    def test_business_days_arithmetic(self):
        # Friday Oct 30, 2026 + 3 business days -> Mon Nov 2 (1), Tue Nov 3 (2), Wed Nov 4 (3)
        start = date(2026, 10, 30)
        end = add_business_days(start, 3)
        self.assertEqual(end, date(2026, 11, 4))

        text = (
            "Fecha de emisión: 30 de octubre de 2026.\n"
            "Dispone de 5 días hábiles para responder a esta solicitud."
        )
        res = extract_deterministic_deadline(text, reference_date=date(2026, 10, 30))
        self.assertTrue(res.is_business_days)
        # 5 business days from Friday Oct 30: Mon 2, Tue 3, Wed 4, Thu 5, Fri 6 -> Nov 6
        self.assertEqual(res.deadline_date, date(2026, 11, 6))

    def test_critical_hours_urgency(self):
        text = "Debe presentarse a la audiencia dentro de 48 horas."
        ref = date(2026, 11, 10)
        res = extract_deterministic_deadline(text, reference_date=ref)
        self.assertEqual(res.urgency, "critical")
        self.assertTrue(res.tutor_alert_required)
        self.assertEqual(res.deadline_date, date(2026, 11, 12))

    def test_urgency_tiers(self):
        today = date(2026, 11, 10)

        # Critical: <= 3 days
        urg, rem, alert = calculate_urgency(date(2026, 11, 12), today)
        self.assertEqual(urg, "critical")
        self.assertTrue(alert)

        # High: <= 14 days
        urg, rem, alert = calculate_urgency(date(2026, 11, 20), today)
        self.assertEqual(urg, "high")
        self.assertTrue(alert)

        # Medium: <= 30 days
        urg, rem, alert = calculate_urgency(date(2026, 12, 5), today)
        self.assertEqual(urg, "medium")
        self.assertFalse(alert)

        # Low: > 30 days
        urg, rem, alert = calculate_urgency(date(2026, 12, 25), today)
        self.assertEqual(urg, "low")
        self.assertFalse(alert)


if __name__ == "__main__":
    unittest.main()

