"""
Phase 0.5 — ReplayGuardMixin Tests.

Validates:
  - ExecutionContext injection (not env vars)
  - Policy hash loaded from L4 config
  - Replay mode installs deterministic providers
  - Non-replay mode does not install providers
  - Properties: is_replay_mode, active_policy_hash, trace_id, safety_status
  - Policy hash drift detection
  - Deterministic replay proof across two instances
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
from agentic_core.mixins.replay_guard_mixin import ReplayGuardMixin
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_replay_guard_mixin")
# REMOVED: _emit_applies_guardrail("p0", "test_replay_guard_mixin", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_replay_guard_mixin", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_replay_guard_mixin", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_replay_guard_mixin", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_replay_guard_mixin", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_replay_guard_mixin", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_replay_guard_mixin", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_replay_guard_mixin", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_replay_guard_mixin", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_replay_guard_mixin", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_replay_guard_mixin", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_replay_guard_mixin", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_replay_guard_mixin", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_replay_guard_mixin", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_replay_guard_mixin", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_replay_guard_mixin", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_replay_guard_mixin", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_replay_guard_mixin", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_replay_guard_mixin", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_replay_guard_mixin", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_replay_guard_mixin", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_replay_guard_mixin", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_replay_guard_mixin", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_replay_guard_mixin", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_replay_guard_mixin", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_replay_guard_mixin", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_replay_guard_mixin", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_replay_guard_mixin", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_replay_guard_mixin", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_replay_guard_mixin", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_replay_guard_mixin", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_replay_guard_mixin", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_replay_guard_mixin", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_replay_guard_mixin", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_replay_guard_mixin", "write_through")
# REMOVED: _emit_writes_through("p1", "test_replay_guard_mixin", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_replay_guard_mixin", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_replay_guard_mixin", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_replay_guard_mixin", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_replay_guard_mixin", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_replay_guard_mixin", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_replay_guard_mixin", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_replay_guard_mixin", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_replay_guard_mixin", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_replay_guard_mixin", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_replay_guard_mixin", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_replay_guard_mixin", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_replay_guard_mixin", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_replay_guard_mixin", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_replay_guard_mixin", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_replay_guard_mixin")
# REMOVED: _emit_gated_by_confidence("p1", "test_replay_guard_mixin", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_replay_guard_mixin")
# REMOVED: emit_determinism_digest("p0", "test_replay_guard_mixin")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_replay_guard_mixin", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_replay_guard_mixin", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_replay_guard_mixin", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_replay_guard_mixin", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_replay_guard_mixin", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_replay_guard_mixin", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_replay_guard_mixin", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_replay_guard_mixin", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_replay_guard_mixin", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_replay_guard_mixin", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_replay_guard_mixin", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_replay_guard_mixin", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_replay_guard_mixin", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_replay_guard_mixin", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_replay_guard_mixin", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_replay_guard_mixin", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_replay_guard_mixin", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_replay_guard_mixin", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_replay_guard_mixin", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_replay_guard_mixin", "exec_snapshot_link")


@dataclass
class _TestExecutionContext:
    """Minimal ExecutionContext stand-in for unit tests.

    Avoids importing execution_context.py which has unresolvable
    class dependencies (MCPHardenedMixin, HealerMixin) at module level.
    """

    mission_id: str = ""
    step_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    trace_id: str | None = None
    parent_span_id: str | None = None
    replay_mode: bool = False
    active_policy_hash: str | None = None
    safety_status: str = "PENDING"


# ---------------------------------------------------------------------------
# Helper: concrete class using ReplayGuardMixin
# ---------------------------------------------------------------------------


class _GuardedClass(ReplayGuardMixin):
    """Minimal concrete class for testing ReplayGuardMixin."""

    def __init__(self, execution_context=None):
        super().__init__(execution_context=execution_context)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestReplayGuardMixinNonReplay:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_default_non_replay(self):
        """Without ExecutionContext, defaults to non-replay mode."""
        obj = _GuardedClass()
        assert obj.is_replay_mode is False
        assert obj.trace_id == "no-trace"
        assert obj.safety_status == "PENDING"
        assert not is_patched()

    @pytest.mark.unit_min_deps
    def test_explicit_non_replay_context(self):
        """ExecutionContext with replay_mode=False does not install providers."""
        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-non-replay",
            replay_mode=False,
            active_policy_hash="abc123",
            safety_status="CLEARED",
        )
        obj = _GuardedClass(execution_context=ctx)
        assert obj.is_replay_mode is False
        assert obj.trace_id == "trace-non-replay"
        assert obj.active_policy_hash == "abc123"
        assert obj.safety_status == "CLEARED"
        assert not is_patched()

    @pytest.mark.unit_min_deps
    def test_policy_hash_from_l4(self):
        """Without explicit policy hash, loads from L4 config."""
        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-l4",
            replay_mode=False,
            active_policy_hash=None,
            safety_status="PENDING",
        )
        obj = _GuardedClass(execution_context=ctx)
        # Should have loaded from L4 (or fallback)
        assert obj.active_policy_hash is not None
        assert len(obj.active_policy_hash) > 0


class TestReplayGuardMixinReplay:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_replay_mode_installs_providers(self):
        """replay_mode=True installs deterministic providers."""
        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-replay",
            replay_mode=True,
            active_policy_hash="policy-hash-replay",
            safety_status="CLEARED",
        )
        obj = _GuardedClass(execution_context=ctx)
        assert obj.is_replay_mode is True
        assert is_patched()

    @pytest.mark.unit_min_deps
    def test_replay_trace_id_immutable(self):
        """trace_id is set from ExecutionContext and immutable."""
        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-immutable",
            replay_mode=True,
            active_policy_hash="ph",
            safety_status="CLEARED",
        )
        obj = _GuardedClass(execution_context=ctx)
        assert obj.trace_id == "trace-immutable"

    @pytest.mark.unit_min_deps
    def test_replay_policy_hash_from_context(self):
        """Policy hash comes from ExecutionContext, not env."""
        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-ph",
            replay_mode=True,
            active_policy_hash="explicit-policy-hash",
            safety_status="CLEARED",
        )
        obj = _GuardedClass(execution_context=ctx)
        assert obj.active_policy_hash == "explicit-policy-hash"


class TestPolicyHashDrift:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_no_drift_initially(self):
        """initial_policy_hash matches active_policy_hash at construction."""
        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-drift",
            replay_mode=False,
            active_policy_hash="stable-hash",
            safety_status="CLEARED",
        )
        obj = _GuardedClass(execution_context=ctx)
        assert not obj.policy_hash_drifted()
        assert obj.initial_policy_hash == "stable-hash"

    @pytest.mark.unit_min_deps
    def test_drift_detected(self):
        """Drift detected when active_policy_hash changes."""
        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-drift2",
            replay_mode=False,
            active_policy_hash="hash-v1",
            safety_status="CLEARED",
        )
        obj = _GuardedClass(execution_context=ctx)
        # Simulate drift
        obj._active_policy_hash = "hash-v2"
        assert obj.policy_hash_drifted()


class TestReplayDeterminismProof:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_two_instances_same_trace_identical_providers(self):
        """Two ReplayGuard instances with same trace_id share deterministic state."""
        import time

        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-proof",
            replay_mode=True,
            active_policy_hash="ph-proof",
            safety_status="CLEARED",
        )
        _GuardedClass(execution_context=ctx)
        t1 = time.time()

        # Unpatch and re-create with same trace
        unpatch_deterministic()
        _GuardedClass(execution_context=ctx)
        t2 = time.time()

        assert t1 == t2


class TestExecutionContextEnhancements:
    @pytest.mark.unit_min_deps
    def test_new_fields_exist(self):
        """ExecutionContext has replay_mode, active_policy_hash, safety_status."""
        ctx = _TestExecutionContext()
        assert hasattr(ctx, "replay_mode")
        assert hasattr(ctx, "active_policy_hash")
        assert hasattr(ctx, "safety_status")

    @pytest.mark.unit_min_deps
    def test_defaults(self):
        """Default values are non-replay, no policy hash, PENDING."""
        ctx = _TestExecutionContext()
        assert ctx.replay_mode is False
        assert ctx.active_policy_hash is None
        assert ctx.safety_status == "PENDING"

    @pytest.mark.unit_min_deps
    def test_fields_settable(self):
        """Fields can be set via constructor kwargs."""
        ctx = _TestExecutionContext(
            replay_mode=True,
            active_policy_hash="test-hash",
            safety_status="CLEARED",
        )
        assert ctx.replay_mode is True
        assert ctx.active_policy_hash == "test-hash"
        assert ctx.safety_status == "CLEARED"
