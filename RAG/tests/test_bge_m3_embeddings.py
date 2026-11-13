"""
Unit Tests for Sovereign BGE-M3 1024-Dimension Embedding Engine
"""

import math
import unittest
from RAG.embeddings.bge_m3_engine import BGEM3EmbeddingEngine, bge_m3_engine


class TestBGEM3EmbeddingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = bge_m3_engine

    def test_dimensions_and_normalization(self):
        """Verifies 1024 dimensions and unit length ||v|| = 1.0."""
        text = "Aviso oficial de la Junta de Propietarios e Inquilinos de Ontario (LTB)."
        vec = self.engine.embed_text(text)

        self.assertEqual(len(vec), 1024, "Vector must have exactly 1024 dimensions")
        norm = math.sqrt(sum(x * x for x in vec))
        self.assertAlmostEqual(norm, 1.0, places=5, msg="Vector must have unit L2 norm")

    def test_deterministic_embedding_invariant(self):
        """Verifies identical text yields exactly identical vector."""
        text = "Immigration, Refugees and Citizenship Canada biometrics instruction letter."
        v1 = self.engine.embed_text(text)
        v2 = self.engine.embed_text(text)
        self.assertEqual(v1, v2, "Deterministic encoder must produce identical floats for identical text")

    def test_binary_packing_round_trip(self):
        """Verifies struct binary packing and unpacking for sqlite-vec."""
        text = "Formulario de solicitud del suplemento de pensión OAS / GIS."
        vec = self.engine.embed_text(text)
        blob = self.engine.vector_to_bytes(vec)

        # 1024 floats * 4 bytes = 4096 bytes
        self.assertEqual(len(blob), 1024 * 4)

        unpacked = self.engine.bytes_to_vector(blob)
        self.assertEqual(len(unpacked), 1024)
        for original, restored in zip(vec, unpacked):
            self.assertAlmostEqual(original, restored, places=6)

    def test_semantic_similarity_proximities(self):
        """Verifies semantic documents exhibit higher cosine similarity than unrelated documents."""
        doc_tenant_1 = self.engine.embed_text("Tribunal de inquilinos orden de desalojo y reclamo de renta mensual atrasada")
        doc_tenant_2 = self.engine.embed_text("Juicio de inquilinos por orden de desalojo y reclamo de renta")
        doc_cooking = self.engine.embed_text("Receta de cocina para preparar pastel de chocolate con crema")

        sim_related = self.engine.cosine_similarity(doc_tenant_1, doc_tenant_2)
        sim_unrelated = self.engine.cosine_similarity(doc_tenant_1, doc_cooking)

        self.assertGreater(
            sim_related,
            sim_unrelated,
            f"Related legal texts ({sim_related:.3f}) should have higher similarity than cooking text ({sim_unrelated:.3f})",
        )
        self.assertGreater(sim_related, 0.60)
        self.assertLess(sim_unrelated, 0.40)

    def test_empty_string_handling(self):
        """Verifies empty or whitespace text generates a normalized neutral vector without error."""
        v_empty = self.engine.embed_text("")
        self.assertEqual(len(v_empty), 1024)
        norm = math.sqrt(sum(x * x for x in v_empty))
        self.assertAlmostEqual(norm, 1.0, places=5)


if __name__ == "__main__":
    unittest.main()
