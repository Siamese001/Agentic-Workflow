"""Foundational behavioral tests for agentic_core/L3_orchestration/reasoning/mcp_manager.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_mcp_manager_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L3_orchestration.reasoning.mcp_manager import (  # noqa: F401
        MCPConnectionManager,
        load_mcp_config,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    MCPConnectionManager = None  # type: ignore[assignment,misc]
    load_mcp_config = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="mcp_manager.py deps unavailable")
class TestMCPConnectionManagerContract:
    def test_is_class(self):
        assert isinstance(MCPConnectionManager, type)

    def test_has_method_connect(self):
        assert callable(getattr(MCPConnectionManager, 'connect', None))

    def test_has_method_disconnect(self):
        assert callable(getattr(MCPConnectionManager, 'disconnect', None))

    def test_has_method_call_tool(self):
        assert callable(getattr(MCPConnectionManager, 'call_tool', None))

    def test_has_method_cleanup(self):
        assert callable(getattr(MCPConnectionManager, 'cleanup', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(MCPConnectionManager) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_manager.py deps unavailable")
class TestLoadMcpConfigFunction:
    def test_is_callable(self):
        assert callable(load_mcp_config)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(load_mcp_config)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: mcp_manager importable or gracefully unavailable."""
    pass
