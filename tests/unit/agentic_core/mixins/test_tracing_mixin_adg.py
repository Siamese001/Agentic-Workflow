"""ADG importability contract for agentic_core/mixins/tracing_mixin.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.mixins.tracing_mixin  # noqa: F401


def test_module_importable():
    import agentic_core.mixins.tracing_mixin  # noqa: F401
    """Module tracing_mixin must be importable."""
    assert agentic_core.mixins.tracing_mixin is not None
