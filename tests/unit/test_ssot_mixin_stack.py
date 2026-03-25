"""
SSOT Mixin Stack Integration Tests.

Validates:
  - Full MRO resolution without conflicts
  - All mixin properties accessible from composite class
  - ExecutionContext threading through full stack
  - Replay mode propagation through all mixins
  - Policy hash scoping across all mixins
  - No MRO duplicate mixins
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pytest

from agentic_core.L2_execution.deterministic_providers import (
    is_patched,
    unpatch_deterministic,
)
from agentic_core.mixins.ssot_mixin_stack import SSOTMixinStack
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_ssot_mixin_stack")
# REMOVED: _emit_applies_guardrail("p0", "test_ssot_mixin_stack", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_ssot_mixin_stack", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_ssot_mixin_stack", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_ssot_mixin_stack", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_ssot_mixin_stack", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_ssot_mixin_stack", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_ssot_mixin_stack", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_ssot_mixin_stack", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_ssot_mixin_stack", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_ssot_mixin_stack", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_ssot_mixin_stack", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_ssot_mixin_stack", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_ssot_mixin_stack", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_ssot_mixin_stack", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_ssot_mixin_stack", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_ssot_mixin_stack", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_ssot_mixin_stack", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_ssot_mixin_stack", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_ssot_mixin_stack", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_ssot_mixin_stack", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_ssot_mixin_stack", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_ssot_mixin_stack", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_ssot_mixin_stack", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_ssot_mixin_stack", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_ssot_mixin_stack", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_ssot_mixin_stack", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_ssot_mixin_stack", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_ssot_mixin_stack", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_ssot_mixin_stack", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_ssot_mixin_stack", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_ssot_mixin_stack", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_ssot_mixin_stack", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ssot_mixin_stack", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ssot_mixin_stack", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_ssot_mixin_stack", "write_through")
# REMOVED: _emit_writes_through("p1", "test_ssot_mixin_stack", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_ssot_mixin_stack", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_ssot_mixin_stack", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_ssot_mixin_stack", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_ssot_mixin_stack", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_ssot_mixin_stack", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_ssot_mixin_stack", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_ssot_mixin_stack", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_ssot_mixin_stack", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_ssot_mixin_stack", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_ssot_mixin_stack", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_ssot_mixin_stack", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_ssot_mixin_stack", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_ssot_mixin_stack", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_ssot_mixin_stack", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_ssot_mixin_stack")
# REMOVED: _emit_gated_by_confidence("p1", "test_ssot_mixin_stack", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_ssot_mixin_stack")
# REMOVED: emit_determinism_digest("p0", "test_ssot_mixin_stack")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_ssot_mixin_stack", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_ssot_mixin_stack", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_ssot_mixin_stack", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_ssot_mixin_stack", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_ssot_mixin_stack", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_ssot_mixin_stack", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_ssot_mixin_stack", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_ssot_mixin_stack", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_ssot_mixin_stack", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_ssot_mixin_stack", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_ssot_mixin_stack", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_ssot_mixin_stack", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_ssot_mixin_stack", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_ssot_mixin_stack", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_ssot_mixin_stack", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_ssot_mixin_stack", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_ssot_mixin_stack", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_ssot_mixin_stack", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_ssot_mixin_stack", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_ssot_mixin_stack", "exec_snapshot_link")


@dataclass
class _Ctx:
    """Minimal ExecutionContext stand-in."""

    mission_id: str = ""
    step_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    trace_id: str | None = None
    parent_span_id: str | None = None
    replay_mode: bool = False
    active_policy_hash: str | None = None
    safety_status: str = "PENDING"


class _FullStackEngine(SSOTMixinStack):
    """Simulates a decision engine with full SSOT mixin stack."""

    def __init__(self, execution_context=None):
        self.state = {"audit_chain": []}
        super().__init__(execution_context=execution_context)


@pytest.fixture(autouse=True)
def _cleanup():
    unpatch_deterministic()
    yield
    unpatch_deterministic()


class TestMROResolution:
    @pytest.mark.unit_min_deps
    def test_mro_resolves_without_error(self):
        """Full mixin stack MRO resolves cleanly."""
        mro = _FullStackEngine.__mro__
        assert len(mro) > 15  # All mixins + object

    @pytest.mark.unit_min_deps
    def test_no_duplicate_mixins_in_mro(self):
        """No mixin appears twice in MRO."""
        mro = _FullStackEngine.__mro__
        mro_names = [cls.__name__ for cls in mro]
        assert len(mro_names) == len(set(mro_names))

    @pytest.mark.unit_min_deps
    def test_replay_guard_is_last_ssot_mixin(self):
        """ReplayGuardMixin is the last SSOT mixin before object."""
        mro = _FullStackEngine.__mro__
        mro_names = [cls.__name__ for cls in mro]
        rg_idx = mro_names.index("ReplayGuardMixin")
        # Only 'object' should follow ReplayGuardMixin
        assert mro_names[rg_idx + 1] == "object"


class TestFullStackConstruction:
    @pytest.mark.unit_min_deps
    def test_non_replay_construction(self):
        """Full stack constructs in non-replay mode."""
        ctx = _Ctx(
            trace_id="t-full",
            active_policy_hash="ph-full",
            safety_status="CLEARED",
        )
        obj = _FullStackEngine(execution_context=ctx)
        assert obj.is_replay_mode is False
        assert obj.trace_id == "t-full"
        assert obj.active_policy_hash == "ph-full"
        assert not is_patched()

    @pytest.mark.unit_min_deps
    def test_replay_construction(self):
        """Full stack constructs in replay mode with deterministic providers."""
        ctx = _Ctx(
            trace_id="t-replay",
            active_policy_hash="ph-replay",
            replay_mode=True,
            safety_status="CLEARED",
        )
        obj = _FullStackEngine(execution_context=ctx)
        assert obj.is_replay_mode is True
        assert is_patched()

    @pytest.mark.unit_min_deps
    def test_default_construction(self):
        """Full stack constructs with no context (all defaults)."""
        obj = _FullStackEngine()
        assert obj.is_replay_mode is False
        assert obj.trace_id == "no-trace"


class TestCrossMixinIntegration:
    @pytest.mark.unit_min_deps
    def test_audit_trail_accessible(self):
        """SSOTAuditTrailMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        entry = obj.emit_ssot_audit_entry("TEST", "target.py")
        assert entry["trace_id"] == "t"
        assert entry["policy_hash"] == "ph"

    @pytest.mark.unit_min_deps
    def test_metrics_accessible(self):
        """SSOTMetricsMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        m = obj.record_metric("test_metric", 42.0)
        assert m["scoped_key"] == "ph:test_metric"

    @pytest.mark.unit_min_deps
    def test_cache_accessible(self):
        """SSOTCachingMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        obj.cache_set("k", "v")
        assert obj.cache_get("k") == "v"

    @pytest.mark.unit_min_deps
    def test_circuit_breaker_accessible(self):
        """SSOTCircuitBreakerMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        result = obj.breaker_call("b", lambda: 99)
        assert result == 99

    @pytest.mark.unit_min_deps
    def test_rate_limit_accessible(self):
        """SSOTRateLimitMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        assert obj.rate_check("b", limit=LIMIT) is True

    @pytest.mark.unit_min_deps
    def test_state_validation_accessible(self):
        """SSOTStateValidationMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph", safety_status="CLEARED")
        obj = _FullStackEngine(execution_context=ctx)
        obj.validate_safety_cleared()  # Should not raise

    @pytest.mark.unit_min_deps
    def test_tracing_accessible(self):
        """SSOTTracingMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        with obj.trace_span("test_op") as span:
            pass
        assert span["trace_id"] == "t"

    @pytest.mark.unit_min_deps
    def test_self_diagnosis_accessible(self):
        """SSOTSelfDiagnosisMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        obj.run_health_check("check1", True)
        assert obj.health_status == "HEALTHY"

    @pytest.mark.unit_min_deps
    def test_adaptive_execution_accessible(self):
        """SSOTAdaptiveExecutionMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        assert obj.execution_mode == "standard"

    @pytest.mark.unit_min_deps
    def test_hallucination_detection_accessible(self):
        """SSOTHallucinationDetectionMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        result = obj.detect_hallucination("def foo(): pass")
        assert "confidence" in result

    @pytest.mark.unit_min_deps
    def test_cognitive_recovery_accessible(self):
        """SSOTCognitiveRecoveryMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        sug = obj.suggest_recovery("import_error")
        assert sug["strategy"] == "fix_imports"

    @pytest.mark.unit_min_deps
    def test_meta_learning_accessible(self):
        """SSOTMetaLearningMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph", safety_status="CLEARED")
        obj = _FullStackEngine(execution_context=ctx)
        obj.ml_store_pattern("domain", {"type": "test"})
        assert obj.ml_pattern_count("domain") == 1

    @pytest.mark.unit_min_deps
    def test_feature_flags_accessible(self):
        """SSOTFeatureFlagMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        assert isinstance(obj.all_flags, dict)

    @pytest.mark.unit_min_deps
    def test_audit_chain_integrity_across_operations(self):
        """Audit chain remains valid after multiple cross-mixin operations."""
        ctx = _Ctx(trace_id="t-chain", active_policy_hash="ph-chain", safety_status="CLEARED")
        obj = _FullStackEngine(execution_context=ctx)

        obj.emit_ssot_audit_entry("BOOT", "system")
        obj.record_metric("boot_time", 0.5)
        obj.emit_ssot_audit_entry("HEAL", "file.py", diff={"line": 10})
        obj.cache_set("result", "ok")
        obj.emit_ssot_audit_entry("VALIDATE", "file.py")

        valid, broken = obj.verify_ssot_audit_chain()
        assert valid is True
        assert broken is None
        assert len(obj.state["audit_chain"]) == 3


class TestReplayModeAcrossStack:
    @pytest.mark.unit_min_deps
    def test_replay_disables_rate_limit(self):
        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True)
        obj = _FullStackEngine(execution_context=ctx)
        for _ in range(100):
            assert obj.rate_check("b", limit=LIMIT) is True

    @pytest.mark.unit_min_deps
    def test_replay_freezes_flags(self):
        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True)
        obj = _FullStackEngine(execution_context=ctx)
        assert obj.flags_frozen is True

    @pytest.mark.unit_min_deps
    def test_replay_locks_adaptive_mode(self):
        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True)
        obj = _FullStackEngine(execution_context=ctx)
        assert obj.execution_mode == "standard"
        assert obj.set_execution_mode("aggressive") is False

    @pytest.mark.unit_min_deps
    def test_replay_blocks_ml_writes(self):
        from agentic_core.mixins.ssot_meta_learning_mixin import MetaLearningWriteRejected

        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True, safety_status="CLEARED")
        obj = _FullStackEngine(execution_context=ctx)
        with pytest.raises(MetaLearningWriteRejected):
            obj.ml_store_pattern("d", {"x": 1})

    @pytest.mark.unit_min_deps
    def test_replay_cognitive_recovery_returns_none(self):
        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True)
        obj = _FullStackEngine(execution_context=ctx)
        assert obj.suggest_recovery("import_error") is None
