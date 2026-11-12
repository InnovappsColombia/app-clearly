"""
Integration & Unit Tests for FastAPI API Endpoints (Sprint 1 Hero Feature)
Directly tests route handlers, response schemas, and error handling.
"""

import unittest
from io import BytesIO
from uuid import UUID, uuid4
import sys
from pathlib import Path
from starlette.datastructures import UploadFile
from fastapi import HTTPException

# Add Backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api.v1.health import get_health
from app.api.v1.documents import (
    process_document,
    get_document_by_id,
    list_user_documents,
    toggle_action,
    audit_text_readability,
    extract_dates_endpoint,
)
from app.db.repository import repository
from app.main import root
from app.schemas.document import ReadabilityAuditRequest, DateExtractionRequest
from tests.async_helper import run_sync


class TestApiDocuments(unittest.TestCase):
    def setUp(self):
        self.senior_id = UUID("11111111-1111-1111-1111-111111111111")
        self.tutor_id = UUID("22222222-2222-2222-2222-222222222222")

    def test_health_check(self):
        res = run_sync(get_health())
        self.assertEqual(res.status, "ok")
        self.assertEqual(res.app_name, "CLEARLY")
        self.assertIn("storage_backend", res.model_dump())

    def test_root_endpoint(self):
        res = run_sync(root())
        self.assertEqual(res["app"], "CLEARLY")
        self.assertIn("tagline", res)

    def test_audit_readability_endpoint(self):
        payload = ReadabilityAuditRequest(
            text="Esta carta es de su ciudad. Debe enviar su foto hoy. Tiene diez días para responder."
        )
        res = run_sync(audit_text_readability(payload))
        self.assertGreaterEqual(res.score, 80.0)
        self.assertTrue(res.is_acceptable)
        self.assertIn(res.category, ["Muy fácil", "Fácil"])

    def test_extract_dates_endpoint(self):
        from datetime import date
        payload = DateExtractionRequest(
            text="Fecha de la carta: 30 de octubre de 2026. Dispone de un plazo de 14 días para responder.",
            reference_date=date(2026, 11, 1),
        )
        res = run_sync(extract_dates_endpoint(payload))
        self.assertEqual(res.deadline_date, date(2026, 11, 13))
        self.assertEqual(res.operator, "+14d")
        self.assertEqual(res.urgency, "high")
        self.assertTrue(res.tutor_alert_required)

    def test_process_document_lifecycle(self):
        file_bytes = (
            "INMIGRACIÓN Y CIUDADANÍA DE CANADÁ (IRCC)\n"
            "Fecha de emisión: 10 de noviembre de 2026.\n"
            "Procedural Fairness Letter sobre solicitud de permiso de trabajo.\n"
            "Por favor envíe sus certificados médicos en un plazo de 30 días posteriores a esta notificación."
        ).encode("utf-8")

        upload_file = UploadFile(
            file=BytesIO(file_bytes),
            filename="carta_ircc.txt",
            headers={"content-type": "text/plain"},
        )

        # 1. Process Document
        doc_res = run_sync(
            process_document(
                file=upload_file,
                user_id=str(self.senior_id),
                target_language="es",
                default_user_id=self.senior_id,
            )
        )
        self.assertIsNotNone(doc_res.id)
        self.assertEqual(doc_res.user_id, self.senior_id)
        self.assertIn("IRCC", doc_res.document_type)
        self.assertGreaterEqual(doc_res.fernandez_huerta_score, 80.0)
        self.assertGreater(len(doc_res.actions_required), 0)

        # 2. Get Document by ID
        detail = run_sync(get_document_by_id(doc_res.id, repo=repository))
        self.assertEqual(detail.id, doc_res.id)
        self.assertIn("INMIGRACIÓN", detail.original_extracted_text)

        # 3. List Documents by User
        user_docs = run_sync(list_user_documents(self.senior_id, repo=repository))
        self.assertGreaterEqual(len(user_docs), 1)

        # 4. Toggle Action item
        action_id = doc_res.actions_required[0].id
        toggled = run_sync(toggle_action(action_id, repo=repository, user_id=self.senior_id))
        self.assertTrue(toggled.is_completed)
        self.assertIsNotNone(toggled.completed_at)

        # 5. Untoggle Action item
        untoggled = run_sync(toggle_action(action_id, repo=repository, user_id=self.senior_id))
        self.assertFalse(untoggled.is_completed)

    def test_empty_file_raises_400(self):
        upload_file = UploadFile(
            file=BytesIO(b""),
            filename="empty.txt",
        )
        with self.assertRaises(HTTPException) as ctx:
            run_sync(
                process_document(
                    file=upload_file,
                    user_id=None,
                    target_language="es",
                    default_user_id=self.senior_id,
                )
            )
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("vacío", ctx.exception.detail)

    def test_document_not_found_raises_404(self):
        with self.assertRaises(HTTPException) as ctx:
            run_sync(get_document_by_id(uuid4(), repo=repository))
        self.assertEqual(ctx.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
