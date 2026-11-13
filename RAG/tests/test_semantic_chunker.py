"""
Unit Tests for Sovereign Semantic Chunker
Validates section boundary preservation, contextual overlap, and metadata extraction.
"""

import unittest
from RAG.chunker.semantic_chunker import SemanticChunker, semantic_chunker


class TestSemanticChunker(unittest.TestCase):
    def setUp(self):
        self.chunker = SemanticChunker(max_chunk_chars=500, chunk_overlap_chars=100)

    def test_empty_or_whitespace_document(self):
        """Verifies empty or whitespace text returns an empty list without error."""
        self.assertEqual(self.chunker.chunk_document(""), [])
        self.assertEqual(self.chunker.chunk_document("   \n\t  "), [])

    def test_section_header_recognition(self):
        """Tests hierarchical recognition of Markdown headers and uppercase titles."""
        sample_doc = (
            "# LANDLORD AND TENANT BOARD\n\n"
            "This is official notice regarding tenancy agreement at 45 Main Street, Brampton.\n\n"
            "REASON FOR NOTICE:\n"
            "The tenant has not paid the full rent owing for November 2026.\n\n"
            "## WHAT YOU MUST DO\n"
            "Pay the total amount owing of $1,850.00 CAD on or before November 20, 2026."
        )

        chunks = self.chunker.chunk_document(sample_doc, document_id="doc-ltb-test")
        self.assertGreaterEqual(len(chunks), 2)

        # First chunk should identify the header
        headers = [c.section_header for c in chunks if c.section_header]
        self.assertTrue(any("LANDLORD" in h for h in headers))
        self.assertTrue(any("WHAT YOU MUST DO" in h or "REASON FOR NOTICE" in h for h in headers))

    def test_metadata_extraction_dates_and_currency(self):
        """Tests regex extraction of Canadian currency and dates within each chunk."""
        sample_notice = (
            "NOTICE OF ASSESSMENT - CANADA REVENUE AGENCY\n\n"
            "Date of notice: 2026-11-15.\n"
            "We have assessed your 2025 tax return. You have a balance due of $432.50 CAD.\n"
            "Please pay this amount by December 10, 2026 to avoid interest charges."
        )

        chunks = self.chunker.chunk_document(sample_notice)
        self.assertGreaterEqual(len(chunks), 1)

        # Aggregate dates and amounts found across chunks
        all_dates = [d for c in chunks for d in c.dates_found]
        all_amounts = [a for c in chunks for a in c.amounts_found]

        # Dates found
        self.assertTrue(any("2026-11-15" in d for d in all_dates))
        self.assertTrue(any("December 10, 2026" in d or "10" in d for d in all_dates))

        # Currency found
        self.assertTrue(any("$432.50" in a for a in all_amounts))
        for c in chunks:
            self.assertGreater(c.token_count, 0)
            self.assertGreater(c.char_count, 0)

    def test_large_section_subdivision_and_overlap(self):
        """Tests that long paragraphs are split into multiple chunks with overlap continuity."""
        long_paragraph = (
            "This is sentence one detailing the immigrant support program. "
            "This is sentence two explaining the eligibility criteria for Ontario seniors. "
            "This is sentence three indicating that language classes are available on weekdays. "
            "This is sentence four explaining how volunteer drivers assist seniors. "
            "This is sentence five listing the contact telephone number for inquiries. "
            "This is sentence six providing the address at Brampton City Centre. "
            "This is sentence seven concluding the civic overview for newcomers."
        ) * 4  # Repeat to exceed 500 chars

        chunks = self.chunker.chunk_document(long_paragraph)
        self.assertGreater(len(chunks), 1)

        # Check chunk indices are continuous
        indices = [c.chunk_index for c in chunks]
        self.assertEqual(indices, list(range(len(chunks))))

        # Check all chunks stay within maximum char boundary
        for c in chunks:
            self.assertLessEqual(c.char_count, 650)  # max + buffer for sentence boundaries


if __name__ == "__main__":
    unittest.main()
