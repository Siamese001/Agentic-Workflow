"""ADG importability contract for agentic_core/mixins/metrics_mixin.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.mixins.metrics_mixin  # noqa: F401


def test_module_importable():
        import agentic_core.mixins.metrics_mixin  # noqa: F401
        """Module metrics_mixin must be importable."""
        assert agentic_core.mixins.metrics_mixin is not None

    assert agentic_core.mixins.metrics_mixin is not None
