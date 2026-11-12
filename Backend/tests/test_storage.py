"""
Unit Tests for Storage Service (Sovereign Storage & SHA-256 Verification)
"""

import unittest
import sys
from pathlib import Path

# Add Backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.storage import storage_service
from tests.async_helper import run_sync


class TestStorageService(unittest.TestCase):
    def test_sha256_calculation(self):
        data = b"CLEARLY Sovereign Document 2026"
        computed = storage_service.calculate_sha256(data)
        self.assertEqual(len(computed), 64)

    def test_save_and_retrieve_document(self):
        test_content = b"Contenido de prueba de carta LTB Brampton 2026."
        filename = "carta_prueba.txt"

        async def run_test():
            path, sha = await storage_service.save_document(test_content, filename, "text/plain")
            self.assertTrue(path.startswith("local://") or path.startswith("minio://"))
            self.assertEqual(len(sha), 64)

            retrieved = await storage_service.get_document(path)
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved, test_content)

        run_sync(run_test())


if __name__ == "__main__":
    unittest.main()
