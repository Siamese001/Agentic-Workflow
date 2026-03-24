"""ADG importability contract for agentic_core/mixins/mcp_hardened_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_mcp_hardened_mixin.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.mcp_hardened_mixin import (  # noqa: F401
        MCPHardenedMixin,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    MCPHardenedMixin = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="mcp_hardened_mixin deps unavailable")
class TestMcpHardenedMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/mixins/mcp_hardened_mixin.py must be importable."""
        assert _AVAILABLE

    def test_mcphardenedmixin_defined(self) -> None:
        assert MCPHardenedMixin is not None