"""ADG importability contract for agentic_core/L6_observability/types/vigilance_event_types.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L6_observability.types.vigilance_event_types  # noqa: F401


def test_module_importable():
    import agentic_core.L6_observability.types.vigilance_event_types  # noqa: F401
    """Module vigilance_event_types must be importable."""
    assert agentic_core.L6_observability.types.vigilance_event_types is not None
