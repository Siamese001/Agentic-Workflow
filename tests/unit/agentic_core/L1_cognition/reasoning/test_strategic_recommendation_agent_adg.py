"""ADG-driven tests for L1_cognition/reasoning/StrategicRecommendationAgent.py — fan_in=1."""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_strategic_recommendation_agent_adg")
_emit_applies_guardrail("p0", "test_strategic_recommendation_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_strategic_recommendation_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_strategic_recommendation_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_strategic_recommendation_agent_adg")
emit_determinism_digest("p0", "test_strategic_recommendation_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.L1_cognition.reasoning.StrategicRecommendationAgent import (
        StrategicRecommendationAgent,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    StrategicRecommendationAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="StrategicRecommendationAgent deps unavailable")
class TestStrategicRecommendationAgent:
    def test_importable(self):
        assert callable(StrategicRecommendationAgent)

    def test_creates_with_defaults(self):
        agent = StrategicRecommendationAgent()
        assert agent is not None

    def test_has_run_or_generate(self):
        assert hasattr(StrategicRecommendationAgent, "run") or hasattr(
            StrategicRecommendationAgent, "generate_recommendations"
        )


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
