"""
Unit & Integration Tests for Sovereign SQLite Vector Store with sqlite-vec & FTS5
"""

import unittest
from uuid import uuid4

from RAG.embeddings.bge_m3_engine import bge_m3_engine
from RAG.storage.sqlite_vector_store import (
    ChunkRecord,
    DocumentRecord,
    EventRecord,
    SQLiteVectorStore,
)


class TestSQLiteVectorStore(unittest.TestCase):
    def setUp(self):
        # Use isolated in-memory store for fast, deterministic unit testing
        self.store = SQLiteVectorStore(":memory:")

    def test_sqlite_vec_extension_loaded(self):
        """Verifies sqlite-vec extension is successfully loaded and vec0 tables exist."""
        self.assertTrue(self.store.has_sqlite_vec, "sqlite-vec extension should be active")
        with self.store.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('vec_chunks', 'vec_events')")
            tables = [r[0] for r in cur.fetchall()]
            self.assertIn("vec_chunks", tables)
            self.assertIn("vec_events", tables)

    def test_document_lifecycle_crud(self):
        """Tests inserting, fetching, updating, and deleting documents."""
        doc_id = str(uuid4())
        doc = DocumentRecord(
            id=doc_id,
            filename="carta_ircc_2026.txt",
            file_sha256="abc123sha256hash",
            content="Instrucciones para la toma de datos biométricos en Mississauga.",
            user_id="user-elena-123",
            issuing_entity="Immigration Refugees and Citizenship Canada",
            urgency="HIGH",
            critical_deadline="2026-12-01",
            fernandez_huerta_score=85.5,
        )

        inserted_id = self.store.insert_document(doc)
        self.assertEqual(inserted_id, doc_id)

        # Retrieve
        fetched = self.store.get_document(doc_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.filename, "carta_ircc_2026.txt")
        self.assertEqual(fetched.issuing_entity, "Immigration Refugees and Citizenship Canada")
        self.assertEqual(fetched.urgency, "HIGH")
        self.assertEqual(fetched.critical_deadline, "2026-12-01")

        # Delete
        deleted = self.store.delete_document(doc_id)
        self.assertTrue(deleted)
        self.assertIsNone(self.store.get_document(doc_id))

    def test_chunk_insertion_and_vector_search(self):
        """Tests inserting chunks with embeddings and querying via sqlite-vec cosine distance."""
        doc_id = str(uuid4())
        self.store.insert_document(
            DocumentRecord(id=doc_id, filename="doc.txt", file_sha256="hash", content="Contenido completo")
        )

        c1 = ChunkRecord(
            id=str(uuid4()),
            document_id=doc_id,
            chunk_index=0,
            content="Aviso de desalojo inmediato LTB por falta de pago de renta.",
            token_count=14,
            section_header="Aviso LTB",
            dates_found=["2026-11-20"],
            amounts_found=["$1,850.00 CAD"],
        )
        c2 = ChunkRecord(
            id=str(uuid4()),
            document_id=doc_id,
            chunk_index=1,
            content="Taller de pintura y acuarela en la biblioteca pública de Brampton.",
            token_count=13,
            section_header="Cultura",
        )

        inserted = self.store.insert_chunks([c1, c2])
        self.assertEqual(inserted, 2)

        # Vector search for legal eviction
        query_vec = bge_m3_engine.embed_text("orden de desalojo del tribunal")
        results = self.store.search_vector(query_vec, top_k=2)

        self.assertEqual(len(results), 2)
        # Top result should be chunk c1 (eviction)
        self.assertEqual(results[0].chunk_id, c1.id)
        self.assertIn("desalojo", results[0].content)
        self.assertGreater(results[0].score, results[1].score)

    def test_fts5_lexical_search(self):
        """Tests SQLite FTS5 BM25 search across document chunks."""
        doc_id = str(uuid4())
        self.store.insert_document(
            DocumentRecord(id=doc_id, filename="tax.txt", file_sha256="taxhash", content="CRA Tax notice")
        )

        c1 = ChunkRecord(
            id=str(uuid4()),
            document_id=doc_id,
            chunk_index=0,
            content="Declaración de impuestos CRA y solicitud del suplemento de ingreso garantizado GIS.",
            token_count=15,
        )
        c2 = ChunkRecord(
            id=str(uuid4()),
            document_id=doc_id,
            chunk_index=1,
            content="Paseos comunitarios por el parque Chinguacousy los martes por la mañana.",
            token_count=12,
        )
        self.store.insert_chunks([c1, c2])

        # FTS5 search
        fts_res = self.store.search_fts("impuestos suplemento GIS", top_k=2)
        self.assertGreaterEqual(len(fts_res), 1)
        self.assertEqual(fts_res[0].chunk_id, c1.id)

    def test_hybrid_search_rrf_fusion(self):
        """Tests Reciprocal Rank Fusion blending dense vector and sparse lexical rankings."""
        doc_id = str(uuid4())
        self.store.insert_document(
            DocumentRecord(id=doc_id, filename="mixed.txt", file_sha256="hash", content="Mixed notices")
        )

        c1 = ChunkRecord(
            id=str(uuid4()),
            document_id=doc_id,
            chunk_index=0,
            content="Audiencia ante la Junta de Propietarios e Inquilinos Landlord Tenant Board expediente N4-8891.",
            token_count=16,
            amounts_found=["$1,200 CAD"],
        )
        c2 = ChunkRecord(
            id=str(uuid4()),
            document_id=doc_id,
            chunk_index=1,
            content="Requisitos de renovación de tarjeta de salud de Ontario OHIP en ServiceOntario.",
            token_count=14,
        )
        self.store.insert_chunks([c1, c2])

        # Hybrid search with exact keyword + semantic concept
        hybrid_res = self.store.search_hybrid("expediente N4 audiencia inquilinos", top_k=2)
        self.assertGreaterEqual(len(hybrid_res), 1)
        self.assertEqual(hybrid_res[0].chunk_id, c1.id)
        self.assertIsNotNone(hybrid_res[0].dense_rank)
        self.assertIsNotNone(hybrid_res[0].sparse_rank)

    def test_civic_event_indexing_and_search(self):
        """Tests civic event storage and hybrid search."""
        ev1 = EventRecord(
            id="ev-brampton-1",
            title="Café Tecnológico y Lectura Clara para Mayores",
            description="Aprende a usar tu teléfono móvil y la app CLEARLY en la Biblioteca de Brampton.",
            city="Brampton",
            start_time="2026-11-20T10:00:00",
            is_free=True,
            postal_code="L6V 1A1",
            category="Tecnología y Educación",
        )
        ev2 = EventRecord(
            id="ev-toronto-2",
            title="Concierto Clásico en Nathan Phillips Square",
            description="Música sinfónica al aire libre en Downtown Toronto para toda la familia.",
            city="Toronto",
            start_time="2026-11-22T18:00:00",
            is_free=True,
            postal_code="M5H 2N2",
            category="Música y Artes",
        )

        self.store.insert_event(ev1)
        self.store.insert_event(ev2)

        # Search specifically in Brampton
        search_res = self.store.search_events_hybrid("biblioteca tecnología para mayores", city="Brampton")
        self.assertEqual(len(search_res), 1)
        self.assertEqual(search_res[0].event.id, "ev-brampton-1")
        self.assertEqual(search_res[0].event.city, "Brampton")


if __name__ == "__main__":
    unittest.main()

