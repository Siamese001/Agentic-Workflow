"""
Wave 5 Invariant: The LongPathsEnabled advisory in execute_ssot.py must be
suppressed when AGENTIC_BYPASS_LONGPATHS_CHECK is set.
"""

from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import L0_ROUTING_DIR

EXECUTE_SSOT_PATH = Path(__file__).parent.parent.parent / L0_ROUTING_DIR / "scripts" / "execute_ssot.py"


@pytest.mark.unit_min_deps
def test_longpaths_bypass_guard_present():
    """Wave 5: execute_ssot.py must check AGENTIC_BYPASS_LONGPATHS_CHECK before emitting warning."""

    src = EXECUTE_SSOT_PATH.read_text(encoding="utf-8", errors="replace")
    assert "AGENTIC_BYPASS_LONGPATHS_CHECK" in src, (
        "AGENTIC_BYPASS_LONGPATHS_CHECK guard missing from execute_ssot.py — "
        "LongPathsEnabled advisory cannot be suppressed"
    )


@pytest.mark.unit_min_deps
def test_longpaths_guard_wraps_advisory():
    """Wave 5: The bypass guard must appear in proximity to LongPathsEnabled check."""
    src = EXECUTE_SSOT_PATH.read_text(encoding="utf-8", errors="replace")
    lines = src.splitlines()
    bypass_lines = [i for i, l in enumerate(lines) if "AGENTIC_BYPASS_LONGPATHS_CHECK" in l]
    longpath_lines = [i for i, l in enumerate(lines) if "LongPathsEnabled" in l]
    assert bypass_lines, "AGENTIC_BYPASS_LONGPATHS_CHECK not found in execute_ssot.py"
    assert longpath_lines, "LongPathsEnabled not found in execute_ssot.py"
    # At least one bypass guard must be within 20 lines of a LongPathsEnabled reference
    for bp in bypass_lines:
        for lp in longpath_lines:
            if abs(bp - lp) <= 20:
                return
    assert False, (
        "AGENTIC_BYPASS_LONGPATHS_CHECK guard is not adjacent to LongPathsEnabled check — "
        "advisory may not be suppressed correctly"
    )
