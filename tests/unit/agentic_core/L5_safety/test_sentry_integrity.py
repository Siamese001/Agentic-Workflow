"""
file: tests/governance/test_sentry_integrity.py
description: Verifies that no test files exist outside of the mirrored hierarchy.
"""

from pathlib import Path

import pytest

PROJECT_ROOT = Path("C:/Git/Agentic-Workflow").resolve()


def test_no_misplaced_tests():
    # Scan everything EXCEPT the allowed 'tests/' directory
    misplaced = []
    for root in ["agentic_core", "apps_rg", "apps_lic"]:
        path = PROJECT_ROOT / root
        if path.exists():
            misplaced.extend(list(path.rglob("test_*.py")))

    assert not misplaced, (
        f"Structural drift detected! Tests found in core folders: {[f.name for f in misplaced]}"
    )


def test_l6_visibility():
    # Ensure L6 Observability is properly mirrored
    l6_test_dir = PROJECT_ROOT / "tests/unit/agentic_core/L6_observability"
    if (PROJECT_ROOT / "agentic_core/L6_observability").exists():
        assert l6_test_dir.exists(), "L6_observability mirror is missing in tests/unit/"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
