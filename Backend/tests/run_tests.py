"""
CLEARLY Backend — Comprehensive Test Runner
Executes all unit, integration, and API tests for Sprint 1.
"""

import unittest
import sys
from pathlib import Path

# Set working directory to Backend
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))


def run_all_tests():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(backend_dir / "tests"), pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print(f"CLEARLY Sprint 1 Test Results: Ran {result.testsRun} tests.")
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        return 0
    else:
        print(f"❌ FAILURES: {len(result.failures)}, ERRORS: {len(result.errors)}")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

