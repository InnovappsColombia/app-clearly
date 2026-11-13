"""
CLEARLY — Sovereign RAG & SQLite/sqlite-vec Test Runner
Executes all unit, integration, and guardrail test suites for Sprint 6.
"""

import sys
import unittest
from pathlib import Path

# Set working directory to project root
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))


def run_all_rag_tests():
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(Path(__file__).resolve().parent),
        pattern="test_*.py",
    )

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print(f"CLEARLY Sovereign RAG Suite Results: Ran {result.testsRun} tests.")
    if result.wasSuccessful():
        print(f"✅ ALL {result.testsRun} RAG & SQLITE-VEC TESTS PASSED SUCCESSFULLY!")
        return 0
    else:
        print(f"❌ FAILURES: {len(result.failures)}, ERRORS: {len(result.errors)}")
        return 1


if __name__ == "__main__":
    exit_code = run_all_rag_tests()
    sys.exit(exit_code)

