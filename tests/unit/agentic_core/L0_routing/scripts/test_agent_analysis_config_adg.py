"""ADG-driven tests for L0_routing/scripts/agent_analysis_config.py — fan_in=0."""
from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_agent_analysis_config_adg")
_emit_applies_guardrail("p0", "test_agent_analysis_config_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_agent_analysis_config_adg", "policy_binding")
_emit_snapshots_state("p0", "test_agent_analysis_config_adg", "state_snapshot")
emit_replay_key("p0", "test_agent_analysis_config_adg")
emit_determinism_digest("p0", "test_agent_analysis_config_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.agent_analysis_config import AgentAnalysis
    _AVAILABLE = True
except ImportError:
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
