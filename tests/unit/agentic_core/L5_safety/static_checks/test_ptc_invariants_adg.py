"""ADG importability contract for agentic_core/L5_safety/static_checks/ptc_invariants.py."""
from __future__ import annotations

import agentic_core.L5_safety.static_checks.ptc_invariants  # noqa: F401


def test_module_importable():
    """Module ptc_invariants must be importable."""
    assert agentic_core.L5_safety.static_checks.ptc_invariants is not None
