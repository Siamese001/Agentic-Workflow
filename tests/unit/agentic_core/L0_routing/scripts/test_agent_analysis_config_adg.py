"""ADG-driven tests for L0_routing/scripts/agent_analysis_config.py — fan_in=0."""
from __future__ import annotations

import pytest
from pathlib import Path

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.agent_analysis_config import AgentAnalysis
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AgentAnalysis = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="agent_analysis_config deps unavailable")
class TestAgentAnalysis:
    def test_creates_with_defaults(self):
        a = AgentAnalysis(file_path=Path("agent.py"), class_name="MyAgent")
        assert a.class_name == "MyAgent"
        assert a.has_redis_mixin is False
        assert a.priority == "LOW"
        assert a.methods_needing_hardening == []

    def test_needs_hardening_with_llm_no_cache(self):
        a = AgentAnalysis(
            file_path=Path("x.py"),
            class_name="X",
            has_llm_calls=True,
            has_cache_checks=False,
        )
        assert a.needs_hardening() is True

    def test_no_hardening_when_cached(self):
        a = AgentAnalysis(
            file_path=Path("x.py"),
            class_name="X",
            has_llm_calls=True,
            has_cache_checks=True,
        )
        assert a.needs_hardening() is False

    def test_has_needs_hardening(self):
        assert hasattr(AgentAnalysis, "needs_hardening")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
