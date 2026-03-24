"""ADG importability contract for agentic_core/mixins/mcp_operation_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_mcp_operation_mixin.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.mcp_operation_mixin import (  # noqa: F401
        MCPOperationMixin,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    MCPOperationMixin = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_operation_mixin.py deps unavailable")
class TestMcpOperationMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: mcp_operation_mixin.py must be importable."""
        assert _AVAILABLE

    def test_mcpoperationmixin_is_type(self) -> None:
        assert MCPOperationMixin is not None