"""ADG importability contract for agentic_core/config/core/reflection_config.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.config.core.reflection_config  # noqa: F401


def test_module_importable():
        import agentic_core.config.core.reflection_config  # noqa: F401
        """Module reflection_config must be importable."""
        assert agentic_core.config.core.reflection_config is not None

    assert agentic_core.config.core.reflection_config is not None
