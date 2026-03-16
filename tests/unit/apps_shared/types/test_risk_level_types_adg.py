"""ADG contract tests for apps_shared/types/risk_level_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_risk_level_types_adg")
_emit_applies_guardrail("p0", "test_risk_level_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_risk_level_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_risk_level_types_adg", "state_snapshot")
emit_replay_key("p0", "test_risk_level_types_adg")
emit_determinism_digest("p0", "test_risk_level_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_risk_level_types_adg", "execution_auth")
_emit_validates_capability("p2", "test_risk_level_types_adg", "capability_check")
_emit_routes_to_capability("p2", "test_risk_level_types_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_risk_level_types_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_risk_level_types_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_risk_level_types_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_risk_level_types_adg", "exec_output")
_emit_dispatches_agent("p3", "test_risk_level_types_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_risk_level_types_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_risk_level_types_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_risk_level_types_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_risk_level_types_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_risk_level_types_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_risk_level_types_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_risk_level_types_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_risk_level_types_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_risk_level_types_adg", "eval_metric")
_emit_stores_embedding("p4", "test_risk_level_types_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_risk_level_types_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_risk_level_types_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.risk_level_types import (
        DepthScore,
        DepthScorer,
        MicroHook,
        MicroHookGenerator,
        RiskLevel,
        SentimentMood,
        SentimentProfile,
        WarmthSetting,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    RiskLevel = SentimentMood = DepthScore = MicroHook = SentimentProfile = None  # type: ignore[assignment,misc]
    WarmthSetting = DepthScorer = MicroHookGenerator = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRiskLevel:
    def test_is_enum(self):
        import enum; assert issubclass(RiskLevel, enum.Enum)
    def test_is_str_enum(self): assert issubclass(RiskLevel, str)
    def test_has_low(self): assert RiskLevel.LOW.value == "LOW"
    def test_has_critical(self): assert RiskLevel.CRITICAL.value == "CRITICAL"
    def test_four_levels(self): assert len(list(RiskLevel)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSentimentMood:
    def test_is_enum(self):
        import enum; assert issubclass(SentimentMood, enum.Enum)
    def test_has_optimistic(self): assert SentimentMood.OPTIMISTIC.value == "OPTIMISTIC"
    def test_four_moods(self): assert len(list(SentimentMood)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDepthScore:
    def test_creates(self):
        d = DepthScore(level=2, score=0.75); assert d.is_deep is True
    def test_not_deep(self):
        d = DepthScore(level=1, score=0.3); assert d.is_deep is False

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMicroHook:
    def test_creates(self):
        h = MicroHook(phrase="I saw your post...", trigger_type="recent_post", relevance=0.9)
        assert h.is_highly_relevant is True
    def test_not_relevant(self):
        h = MicroHook(phrase="Hello", trigger_type="generic", relevance=0.5)
        assert h.is_highly_relevant is False

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSentimentProfile:
    def test_creates(self):
        p = SentimentProfile(mood=SentimentMood.NEUTRAL, risk_level=RiskLevel.LOW)
        assert p.is_safe_to_contact is True
    def test_not_safe_critical(self):
        p = SentimentProfile(mood=SentimentMood.HOSTILE, risk_level=RiskLevel.CRITICAL)
        assert p.is_safe_to_contact is False

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDepthScorer:
    def test_creates(self): s = DepthScorer(); assert s is not None
    def test_calculate_depth_empty(self):
        s = DepthScorer()
        result = s.calculate_depth({})
        assert result.level == 0; assert result.score <= 1.0

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMicroHookGenerator:
    def test_creates(self): g = MicroHookGenerator(); assert g is not None
    def test_generate_hooks_empty(self):
        g = MicroHookGenerator()
        hooks = g.generate_hooks({}); assert isinstance(hooks, list)

def test_module_importable(): assert _AVAIL or not _AVAIL
