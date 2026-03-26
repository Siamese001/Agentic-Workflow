"""ADG importability contract for agentic_core/L5_safety/reasoning/guardian_decision.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.guardian_decision  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.reasoning.guardian_decision  # noqa: F401
    """Module guardian_decision must be importable."""
    assert agentic_core.L5_safety.reasoning.guardian_decision is not None
