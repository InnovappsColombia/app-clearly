"""
CLEARLY — Test Suite for Automatic Expert Matching Engine (Sprint 4)
Validates classification of IRCC, LTB, and CRA cases to certified professionals.
"""

import unittest
import sys
from pathlib import Path
from uuid import UUID

# Add Backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api.v1.premium import match_expert
from app.db.repository import repository
from app.schemas.premium import ExpertMatchRequest
from tests.async_helper import run_sync

ELENA_ID = UUID("11111111-1111-1111-1111-111111111111")


class TestPremiumMatching(unittest.TestCase):
    def setUp(self):
        repository._load_seed_data()

    def test_automatic_match_ircc_immigration(self):
        """Validates matching IRCC permanent resident notice to David Mendoza, RCIC."""
        req = ExpertMatchRequest(
            query_text="Immigration Canada IRCC Procedural Fairness Letter regarding permanent resident renewal.",
            senior_id=ELENA_ID,
        )
        res = run_sync(match_expert(req))

        self.assertIn("Inmigración", res.detected_specialty)
        self.assertEqual(res.matched_expert.full_name, "David Mendoza, RCIC")
        self.assertEqual(res.matched_expert.license_number, "R708912-CICC")
        self.assertEqual(res.matched_expert.hourly_rate_cents, 4500)
        self.assertGreaterEqual(res.match_score, 80.0)
        self.assertIn("Inmigración", res.plain_language_reasoning)

    def test_automatic_match_ltb_eviction(self):
        """Validates matching LTB N4 eviction notice to Sarah Jenkins, MSW."""
        req = ExpertMatchRequest(
            query_text="Tribunal de Arrendamiento LTB Ontario. Formulario N4 aviso de desalojo por falta de pago.",
            senior_id=ELENA_ID,
        )
        res = run_sync(match_expert(req))

        self.assertIn("Vivienda", res.detected_specialty)
        self.assertEqual(res.matched_expert.full_name, "Sarah Jenkins, MSW")
        self.assertEqual(res.matched_expert.license_number, "OCSWSSW-839120")
        self.assertEqual(res.matched_expert.hourly_rate_cents, 4000)
        self.assertIn("alquileres", res.plain_language_reasoning)

    def test_automatic_match_cra_pension(self):
        """Validates matching CRA pension inquiry to María Santos."""
        req = ExpertMatchRequest(
            query_text="Carta de Service Canada sobre la pensión de vejez OAS y el suplemento de ingreso garantizado GIS.",
            senior_id=ELENA_ID,
        )
        res = run_sync(match_expert(req))

        self.assertIn("Pensiones", res.detected_specialty)
        self.assertEqual(res.matched_expert.full_name, "María Santos")
        self.assertEqual(res.matched_expert.hourly_rate_cents, 3500)


if __name__ == "__main__":
    unittest.main()
