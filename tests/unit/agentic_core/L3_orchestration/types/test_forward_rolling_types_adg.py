"""ADG importability contract for agentic_core/L3_orchestration/types/forward_rolling_types.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L3_orchestration.types.forward_rolling_types  # noqa: F401


def test_module_importable():
    import agentic_core.L3_orchestration.types.forward_rolling_types  # noqa: F401
    """Module forward_rolling_types must be importable."""
    assert agentic_core.L3_orchestration.types.forward_rolling_types is not None
