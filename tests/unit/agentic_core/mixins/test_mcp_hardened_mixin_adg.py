"""ADG importability contract for agentic_core/mixins/mcp_hardened_mixin.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.mixins.mcp_hardened_mixin  # noqa: F401


def test_module_importable():
        import agentic_core.mixins.mcp_hardened_mixin  # noqa: F401
        """Module mcp_hardened_mixin must be importable."""
        assert agentic_core.mixins.mcp_hardened_mixin is not None

    assert agentic_core.mixins.mcp_hardened_mixin is not None
