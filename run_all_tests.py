"""
CLEARLY — Master Test Runner
Executes:
1. Backend Unit & Integration Tests (62 tests)
2. Sovereign Local RAG & sqlite-vec Tests (27 tests)
Total: 89 Python Tests (Plus 23 Frontend Node Tests = 112 Total)
"""

import sys
import unittest
from pathlib import Path

root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "Backend"))


def run_all_system_tests():
    loader = unittest.TestLoader()

    # Discover Backend tests
    backend_suite = loader.discover(
        start_dir=str(root_dir / "Backend" / "tests"),
        pattern="test_*.py",
    )

    # Discover RAG tests
    rag_suite = loader.discover(
        start_dir=str(root_dir / "RAG" / "tests"),
        pattern="test_*.py",
    )

    master_suite = unittest.TestSuite([backend_suite, rag_suite])

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(master_suite)

    print("\n" + "=" * 70)
    print(f"CLEARLY MASTER TEST RUNNER: Ran {result.testsRun} tests across Backend & RAG.")
    if result.wasSuccessful():
        print(f"✅ ALL {result.testsRun} TESTS PASSED WITH 0 FAILURES AND 0 ERRORS!")
        return 0
    else:
        print(f"❌ FAILURES: {len(result.failures)}, ERRORS: {len(result.errors)}")
        return 1


if __name__ == "__main__":
    code = run_all_system_tests()
    sys.exit(code)

