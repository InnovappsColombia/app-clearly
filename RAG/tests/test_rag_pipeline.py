"""
Integration Tests for Sovereign Local RAG Pipeline and Backend Adapter
"""

import unittest
from uuid import uuid4

from RAG.adapter.backend_adapter import backend_rag_adapter
from RAG.pipeline.rag_service import SovereignRAGService
from RAG.storage.sqlite_vector_store import SQLiteVectorStore


class TestRAGPipeline(unittest.TestCase):
    def setUp(self):
        # Isolated in-memory store for RAG service
        self.store = SQLiteVectorStore(":memory:")
        self.service = SovereignRAGService(store=self.store)

    def test_end_to_end_document_indexing_and_grounded_query(self):
        """
        Tests indexing an Ontario LTB notice, querying in Spanish,
        and verifying citations, readability >= 80, and actions.
        """
        ltb_notice = (
            "# LANDLORD AND TENANT BOARD - NOTICE TO END TENANCY (FORM N4)\n\n"
            "File Number: LTB-2026-9921.\n"
            "Date of Notice: 2026-11-14.\n\n"
            "REASON FOR NOTICE:\n"
            "The tenant has not paid the full monthly rent owing.\n"
            "Total rent arrears: $1,850.00 CAD.\n\n"
            "## WHAT YOU MUST DO\n"
            "You must pay the full amount of $1,850.00 CAD or move out of the rental unit "
            "on or before December 05, 2026.\n\n"
            "## HOW TO DISPUTE\n"
            "If you do not agree with this notice, you do not have to move out. "
            "The landlord must apply to the Landlord and Tenant Board for a hearing."
        )

        # 1. Index document
        index_res = self.service.index_document(
            content=ltb_notice,
            filename="Form_N4_LTB.txt",
            issuing_entity="Landlord and Tenant Board",
            critical_deadline="2026-12-05",
            urgency="CRITICAL",
        )
        self.assertTrue(index_res.success)
        self.assertGreaterEqual(index_res.chunks_created, 2)

        # 2. Query in Spanish
        query_res = self.service.query(
            user_query="¿Cuánto dinero debo pagar y cuál es la fecha límite?",
            document_id=index_res.document_id,
            language="es",
        )

        self.assertIn("1,850.00", query_res.answer)
        self.assertGreaterEqual(len(query_res.citations), 1)
        self.assertGreaterEqual(
            query_res.readability.score,
            80.0,
            f"Expected FH >= 80, got {query_res.readability.score}",
        )
        self.assertTrue(query_res.requires_human_expert)  # Triggers eviction/LTB expert
        self.assertGreaterEqual(len(query_res.suggested_actions), 1)

    def test_query_in_english(self):
        """Tests querying in English and verifying Flesch Reading Ease score."""
        ircc_letter = (
            "# IMMIGRATION REFUGEES AND CITIZENSHIP CANADA\n\n"
            "Biometrics Instruction Letter.\n"
            "Application: W30491823.\n\n"
            "DETAILS:\n"
            "You must visit an official Service Canada collection centre to give your biometrics. "
            "The scheduled date is December 10, 2026.\n"
            "Fee paid: $85.00 CAD."
        )

        idx_res = self.service.index_document(
            content=ircc_letter,
            filename="ircc_bio.txt",
            issuing_entity="IRCC",
            critical_deadline="2026-12-10",
        )

        resp_en = self.service.query(
            user_query="Where and when should I give my biometrics?",
            document_id=idx_res.document_id,
            language="en",
        )

        self.assertIn("Chunk:", resp_en.answer)
        self.assertGreaterEqual(resp_en.readability.score, 70.0)

    def test_no_matching_documents_fallback(self):
        """Tests that queries on empty knowledge base return non-hallucinating message."""
        res = self.service.query("¿Cuándo es mi cita médica?", language="es")
        self.assertIn("No encontré información", res.answer)
        self.assertEqual(len(res.citations), 0)
        self.assertEqual(len(res.retrieved_chunks), 0)

    def test_backend_rag_adapter_integration(self):
        """Verifies BackendRAGAdapter synchronizes documents and events."""
        adapter = backend_rag_adapter
        doc_id = str(uuid4())
        synced_id = adapter.sync_document(
            document_id=doc_id,
            filename="convenio_alquiler.txt",
            content="Contrato de arrendamiento residencial en Brampton Ontario.",
            issuing_entity="Ontario Standard Lease",
        )
        self.assertEqual(synced_id, doc_id)

        # Query via adapter
        query_res = adapter.query_senior_documents(
            user_query="arrendamiento residencial",
            document_id=doc_id,
        )
        self.assertIsNotNone(query_res)
        self.assertGreaterEqual(len(query_res.retrieved_chunks), 1)


if __name__ == "__main__":
    unittest.main()

