"""ADG importability contract for agentic_core/L5_safety/enforcement/priority_violation_guard.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.enforcement.priority_violation_guard  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.enforcement.priority_violation_guard  # noqa: F401
    """Module priority_violation_guard must be importable."""
    assert agentic_core.L5_safety.enforcement.priority_violation_guard is not None
