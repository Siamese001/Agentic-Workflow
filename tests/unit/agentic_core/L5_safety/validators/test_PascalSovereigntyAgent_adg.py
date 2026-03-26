"""ADG importability contract for agentic_core/L5_safety/validators/PascalSovereigntyAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.validators.PascalSovereigntyAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.validators.PascalSovereigntyAgent  # noqa: F401
    """Module PascalSovereigntyAgent must be importable."""
    assert agentic_core.L5_safety.validators.PascalSovereigntyAgent is not None
