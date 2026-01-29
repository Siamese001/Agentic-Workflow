"""
file: tests/migration/test_final_audit.py
description: Final audit of the file counts to ensure no data loss during Phase 7/8.
"""

import pytest
from pathlib import Path

PROJECT_ROOT = Path("C:/Git/Agentic-Workflow").resolve()


def test_final_file_counts():
    """
    Verify that the total number of tests in the new structure
    matches the expected rescued count.
    """
    # Sum up all .py files in the valid test directories
    unit_tests = list((PROJECT_ROOT / "tests/unit").rglob("test_*.py"))
    int_tests = list((PROJECT_ROOT / "tests/integration").rglob("test_*.py"))
    e2e_tests = list((PROJECT_ROOT / "tests/e2e").rglob("test_*.py"))

    total_found = len(unit_tests) + len(int_tests) + len(e2e_tests)

    print("\nAudit Results:")
    print(f"  Unit: {len(unit_tests)}")
    print(f"  Integration: {len(int_tests)}")
    print(f"  E2E: {len(e2e_tests)}")
    print(f"  Total: {total_found}")

    # Based on Phase 7 (239) + Phase 8 (54) = 293 rescued files
    assert total_found >= 293, f"Audit failed! Only found {total_found} tests."


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
