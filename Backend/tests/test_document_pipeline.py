"""
Unit & Integration Tests for Document Processing Pipeline
"""

import unittest
from datetime import date
from uuid import UUID
import sys
from pathlib import Path

# Add Backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.repository import repository
from app.services.document_pipeline import document_pipeline
from tests.async_helper import run_sync


class TestDocumentPipeline(unittest.TestCase):
    def setUp(self):
        self.senior_id = UUID("11111111-1111-1111-1111-111111111111")  # Elena Pabla
        self.tutor_id = UUID("22222222-2222-2222-2222-222222222222")   # Carlos Pabla

    def test_pipeline_ltb_eviction_notice_with_tutor_alert(self):
        """
        Processes an LTB N4 eviction notice.
        Validates:
        1. Plain summary generated with FH >= 80.
        2. Deterministic deadline computed (+14 days from Oct 30 = Nov 13).
        3. Document Actions checklist populated.
        4. Proactive Tutor alert created for Carlos Pabla (< 15 days).
        """
        sample_doc = (
            "TRIBUNAL DE ARRENDAMIENTO DE ONTARIO (LANDLORD AND TENANT BOARD)\n"
            "FORMULARIO N4: AVISO PARA TERMINAR EL ARRENDAMIENTO POR FALTA DE PAGO.\n"
            "Fecha de la carta: 30 de octubre de 2026.\n"
            "Dirección del inmueble: 140 Main St, Brampton, ON.\n"
            "Monto adeudado: $1,450.00 CAD.\n"
            "Usted tiene un plazo de 14 días a partir de la fecha de esta notificación "
            "para pagar el saldo o llegar a un acuerdo con el propietario."
        ).encode("utf-8")

        ref_date = date(2026, 11, 1)

        async def run_pipeline():
            response = await document_pipeline.process_document(
                file_bytes=sample_doc,
                filename="aviso_n4_desalojo.txt",
                user_id=self.senior_id,
                content_type="text/plain",
                target_language="es",
                reference_date=ref_date,
            )

            # 1. Assert Basic Response
            self.assertIsNotNone(response.id)
            self.assertEqual(response.user_id, self.senior_id)
            self.assertIn("LTB", response.document_type)

            # 2. Assert Readability
            self.assertGreaterEqual(response.fernandez_huerta_score, 80.0)
            self.assertIn(response.readability_category, ["Muy fácil", "Fácil"])

            # 3. Assert Deterministic Deadline
            self.assertEqual(response.critical_deadline, date(2026, 11, 13))
            self.assertEqual(response.days_remaining, 12)
            self.assertEqual(response.urgency, "high")
            self.assertTrue(response.tutor_alert_triggered)

            # 4. Assert 3-Layer Structure
            self.assertGreater(len(response.actions_required), 0)
            self.assertGreater(len(response.ambiguities_flagged), 0)
            self.assertGreater(len(response.recommended_questions), 0)

            # 5. Assert Notification Dispatched to Tutor (Carlos Pabla)
            tutor_notifs = await repository.list_notifications_by_user(self.tutor_id)
            self.assertGreater(len(tutor_notifs), 0)
            latest = tutor_notifs[0]
            self.assertTrue(latest.is_urgent)
            self.assertIn("Alerta Preventiva", latest.title)
            self.assertIn(str(response.id), latest.metadata.get("document_id", ""))

        run_sync(run_pipeline())


if __name__ == "__main__":
    unittest.main()
