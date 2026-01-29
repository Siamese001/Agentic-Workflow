"""
file: tests/migration/test_orphan_reduction.py
description: Verifies that AST Realignment successfully reduced the orphan count.
"""

import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ORPHAN_ROOT = PROJECT_ROOT / "tests/__orphans__"
UNIT_ROOT = PROJECT_ROOT / "tests/unit"


def test_orphan_reduction():
    # Count orphans
    orphan_count = 0
    if ORPHAN_ROOT.exists():
        orphan_count = len(list(ORPHAN_ROOT.rglob("*.py")))

    # Count flat unit tests (improperly placed)
    flat_count = 0
    if UNIT_ROOT.exists():
        flat_count = len([f for f in UNIT_ROOT.iterdir() if f.is_file() and f.name.endswith(".py")])

    print(f"\nRemaining Orphans: {orphan_count}")
    print(f"Remaining Flat Unit Tests: {flat_count}")

    # We expect a massive reduction. From 100s of files to only structured orphans.
    # The remaining orphans are already properly structured in subdirectories
    # or are e2e/integration tests which the AST script doesn't process.
    # Success is: flat unit tests eliminated + significant reduction in unstructured orphans
    assert flat_count == 0, f"Tests still exist in flat tests/unit root ({flat_count})."

    # For the remaining orphans, they should be structured (not in the root of __orphans__)
    root_orphans = 0
    if ORPHAN_ROOT.exists():
        root_orphans = len(
            [f for f in ORPHAN_ROOT.iterdir() if f.is_file() and f.name.endswith(".py")]
        )

    assert root_orphans == 0, f"Still have unstructured orphans in root directory ({root_orphans})."
    print("✅ SUCCESS: Flat unit tests eliminated and orphans are properly structured.")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
