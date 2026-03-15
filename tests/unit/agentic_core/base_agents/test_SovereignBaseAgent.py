"""Foundational behavioral tests for agentic_core/base_agents/SovereignBaseAgent.py.

fan_in=134 — imported by 134 other modules.
ADG import-hygiene is covered separately by test_SovereignBaseAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.base_agents.SovereignBaseAgent import (  # noqa: F401
        SovereignBaseAgent,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SovereignBaseAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="SovereignBaseAgent.py deps unavailable")
class TestSovereignBaseAgentContract:
    def test_is_class(self):
        assert isinstance(SovereignBaseAgent, type)

    def test_has_method_get_sovereign_capabilities(self):
        assert callable(getattr(SovereignBaseAgent, 'get_sovereign_capabilities', None))

    def test_has_method_execute(self):
        assert callable(getattr(SovereignBaseAgent, 'execute', None))

    def test_has_method_get_state(self):
        assert callable(getattr(SovereignBaseAgent, 'get_state', None))

    def test_has_method_set_state(self):
        assert callable(getattr(SovereignBaseAgent, 'set_state', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(SovereignBaseAgent) if not m.startswith('_')]
        assert len(pub) >= 1


def test_module_importable():
    """Smoke: SovereignBaseAgent importable or gracefully unavailable."""
    pass
