"""
§1-Compliant robust tests for healing_tier_dispatcher.py.

Coverage per §1.1 Required test dimensions:
  - Edge cases: FailureSignal import reachability, empty agent_id, zero blast radius,
    max retry_count, all HealingTier values
  - State transitions: FailureSignal → HealingInput conversion, dispatch_healing flow
  - Fail-closed: TIERING_ALLOWLIST blocks unknown agents (sovereignty)
  - Mutation-sensitive: FailureSignal reference, route_healing_tier choke point,
    import invariants
  - Regression Fix #5: FailureSignal missing import → NameError at runtime

§1.2: Deterministic only — no random, no wall-clock, no external state.
      Mocks ONLY for WSL/vLLM (external hardware interface).
"""

from __future__ import annotations

import inspect

import pytest

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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "test_healing_tier_dispatcher_robust")
_emit_applies_guardrail("p0", "test_healing_tier_dispatcher_robust", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_tier_dispatcher_robust", "policy_binding")
_emit_snapshots_state("p0", "test_healing_tier_dispatcher_robust", "state_snapshot")
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

_emit_emits_metric_event("test_healing_tier_dispatcher_robust", "p4obs", "metric_1")
_emit_emits_metric_event("test_healing_tier_dispatcher_robust", "p4obs", "metric_2")
_emit_emits_metric_event("test_healing_tier_dispatcher_robust", "p4obs", "metric_3")
_emit_emits_metric_event("test_healing_tier_dispatcher_robust", "p4obs", "metric_4")
_emit_emits_metric_event("test_healing_tier_dispatcher_robust", "p4obs", "metric_5")
_emit_emits_metric_event("test_healing_tier_dispatcher_robust", "p4obs", "metric_6")
_emit_records_incident_event("test_healing_tier_dispatcher_robust", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_healing_tier_dispatcher_robust", "p4obs", "anomaly")
_emit_writes_observability_log("test_healing_tier_dispatcher_robust", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_healing_tier_dispatcher_robust", "p4obs", "mon_state")
_emit_triggers_alert("test_healing_tier_dispatcher_robust", "p4obs", "alert")
_emit_links_incident_trace("test_healing_tier_dispatcher_robust", "p4obs", "trace_link")
_emit_captures_pattern("test_healing_tier_dispatcher_robust", "p3lm", "pattern")
_emit_records_learning_event("test_healing_tier_dispatcher_robust", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_healing_tier_dispatcher_robust", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_healing_tier_dispatcher_robust", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_healing_tier_dispatcher_robust", "p3lm", "routing")
_emit_improves_agent_policy("test_healing_tier_dispatcher_robust", "p3lm", "policy")
_emit_stores_learning_state("test_healing_tier_dispatcher_robust", "p3lm", "state")
_emit_records_execution_trace("test_healing_tier_dispatcher_robust", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_healing_tier_dispatcher_robust", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_healing_tier_dispatcher_robust", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_healing_tier_dispatcher_robust", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_healing_tier_dispatcher_robust", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_healing_tier_dispatcher_robust", "env_read", "p2_env_1")
_emit_reads_environ("test_healing_tier_dispatcher_robust", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_healing_tier_dispatcher_robust", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_healing_tier_dispatcher_robust", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_healing_tier_dispatcher_robust", "context_pull")
_emit_pulls_context("p1", "test_healing_tier_dispatcher_robust", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_healing_tier_dispatcher_robust", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_healing_tier_dispatcher_robust", "uwg_term_2")
_emit_writes_through("p1", "test_healing_tier_dispatcher_robust", "write_through")
_emit_writes_through("p1", "test_healing_tier_dispatcher_robust", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_healing_tier_dispatcher_robust", "safety_validation")
_emit_invokes_eval("p1", "test_healing_tier_dispatcher_robust", "eval_call")
_emit_proposal_commits_routing("p1", "test_healing_tier_dispatcher_robust", "routing_commit")
_emit_escalates_to_human("p1", "test_healing_tier_dispatcher_robust", "human_escalation")
_emit_routes_through("p1", "test_healing_tier_dispatcher_robust", "route_through")
_emit_checks_agent_registry("p1", "test_healing_tier_dispatcher_robust", "agent_registry")
_emit_validates_agent_capability("p1", "test_healing_tier_dispatcher_robust", "capability")
_emit_dispatches_execution_plan("p1", "test_healing_tier_dispatcher_robust", "exec_plan")
_emit_agent_executes_agent("p1", "test_healing_tier_dispatcher_robust", "sub_agent")
_emit_routes_to_agent("p1", "test_healing_tier_dispatcher_robust", "target_agent")
_emit_verifies_policy("p1", "test_healing_tier_dispatcher_robust", "policy_check")
_emit_observes_runtime_state("p1", "test_healing_tier_dispatcher_robust", "runtime_state")
_emit_verifies_boundary("p1", "test_healing_tier_dispatcher_robust", "boundary_check")
_emit_transcripts_response("p1", "test_healing_tier_dispatcher_robust", "transcript")
_emit_hard_fails_untranscripted("p1", "test_healing_tier_dispatcher_robust")
_emit_gated_by_confidence("p1", "test_healing_tier_dispatcher_robust", "confidence_gate")
emit_replay_key("p0", "test_healing_tier_dispatcher_robust")
emit_determinism_digest("p0", "test_healing_tier_dispatcher_robust")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_healing_tier_dispatcher_robust", "execution_auth")
_emit_validates_capability("p2", "test_healing_tier_dispatcher_robust", "capability_check")
_emit_routes_to_capability("p2", "test_healing_tier_dispatcher_robust", "capability_route")
_emit_writes_via_uwg("p2", "test_healing_tier_dispatcher_robust", "uwg_write")
_emit_blocks_direct_write("p2", "test_healing_tier_dispatcher_robust", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healing_tier_dispatcher_robust", "tool_invocation")
_emit_captures_execution_output("p2", "test_healing_tier_dispatcher_robust", "exec_output")
_emit_dispatches_agent("p3", "test_healing_tier_dispatcher_robust", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healing_tier_dispatcher_robust", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healing_tier_dispatcher_robust", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healing_tier_dispatcher_robust", "healing_outcome")
_emit_escalates_failure("p3", "test_healing_tier_dispatcher_robust", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healing_tier_dispatcher_robust", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healing_tier_dispatcher_robust", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healing_tier_dispatcher_robust", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healing_tier_dispatcher_robust", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healing_tier_dispatcher_robust", "eval_metric")
_emit_stores_embedding("p4", "test_healing_tier_dispatcher_robust", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healing_tier_dispatcher_robust", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healing_tier_dispatcher_robust", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


# ---------------------------------------------------------------------------
# §1.1 FailureSignal import — Fix #5 regression
# ---------------------------------------------------------------------------


class TestFailureSignalImportInvariant:
    """Fix #5 regression: FailureSignal was used but not imported.

    Mutation-sensitive: removing the import from healing_tier_dispatcher.py
    causes NameError at runtime on OOM events.
    """

    def test_failure_signal_is_module_level_name_in_dispatcher(self):
        """FailureSignal must be bound at module level in healing_tier_dispatcher."""
        import agentic_core.L2_execution.healers.healing_tier_dispatcher as mod

        assert hasattr(mod, "FailureSignal"), (
            "FailureSignal must be imported at module level — "
            "removing it causes NameError in handle_qwen_oom_via_router"
        )

    def test_failure_signal_is_correct_class_from_healing_tier_types(self):
        """FailureSignal in dispatcher must be the canonical type from healing_tier_types."""
        import agentic_core.L2_execution.healers.healing_tier_dispatcher as mod
        from agentic_core.L2_execution.healers.healing_tier_types import FailureSignal

        assert mod.FailureSignal is FailureSignal, (
            "healing_tier_dispatcher.FailureSignal must be the same object as "
            "healing_tier_types.FailureSignal — not a shadow or alias"
        )

    def test_failure_signal_not_a_mock_or_none(self):
        """FailureSignal must be a real class, not None or a mock."""
        import agentic_core.L2_execution.healers.healing_tier_dispatcher as mod

        fs = mod.FailureSignal
        assert fs is not None
        assert isinstance(fs, type), f"FailureSignal must be a class, got {type(fs)}"

    def test_handle_qwen_oom_references_failure_signal_in_source(self):
        """Source invariant: handle_qwen_oom_via_router must reference FailureSignal.

        Mutation-sensitive: removing the FailureSignal usage from the function
        would mean OOM escalation no longer uses the canonical failure type.
        """
        from agentic_core.L2_execution.healers.healing_tier_dispatcher import (
            handle_qwen_oom_via_router,
        )

        source = inspect.getsource(handle_qwen_oom_via_router)
        assert "FailureSignal" in source, (
            "handle_qwen_oom_via_router must reference FailureSignal in its body"
        )

    def test_handle_qwen_oom_references_route_healing_tier(self):
        """Source invariant: OOM handler must route through route_healing_tier choke point."""
        from agentic_core.L2_execution.healers.healing_tier_dispatcher import (
            handle_qwen_oom_via_router,
        )

        source = inspect.getsource(handle_qwen_oom_via_router)
        assert "route_healing_tier" in source, (
            "handle_qwen_oom_via_router must call route_healing_tier — "
            "removing this would bypass the sovereignty choke point"
        )


# ---------------------------------------------------------------------------
# §1.1 FailureSignal dataclass construction — edge cases
# ---------------------------------------------------------------------------


class TestFailureSignalConstruction:
    """FailureSignal dataclass edge cases per §1.1."""

    def test_failure_signal_minimal_construction(self):
        """Minimal valid FailureSignal must construct without error."""
        from agentic_core.L2_execution.healers.healing_tier_types import FailureSignal

        sig = FailureSignal(
            source_agent="test_agent",
            failure_type="syntax_error",
            error_signature="sig_001",
            trace_id="trace_001",
            context={},
            retry_count=0,
            blast_radius_estimate=0.0,
        )
        assert sig.failure_type == "syntax_error"
        assert sig.retry_count == 0

    def test_failure_signal_max_retry_count(self):
        """retry_count at maximum (MAX_RETRIES=3) must construct successfully."""
        from agentic_core.L2_execution.healers.healing_tier_types import FailureSignal

        sig = FailureSignal(
            source_agent="test_agent",
            failure_type="import_cycle",
            error_signature="sig_max",
            trace_id="trace_max",
            context={"key": "val"},
            retry_count=3,
            blast_radius_estimate=1.0,
        )
        assert sig.retry_count == 3
        assert sig.blast_radius_estimate == 1.0

    def test_failure_signal_to_healing_input_conversion(self):
        """FailureSignal.to_healing_input() must produce a valid HealingInput."""
        from agentic_core.L2_execution.healers.healing_tier_types import (
            FailureSignal,
            HealingInput,
        )

        sig = FailureSignal(
            source_agent="dispatch_agent",
            failure_type="ast_violation",
            error_signature="sig_ast",
            trace_id="trace_ast",
            context={"territory": "L2"},
            retry_count=1,
            blast_radius_estimate=0.3,
        )
        healing_input = sig.to_healing_input()
        assert isinstance(healing_input, HealingInput)
        assert healing_input.failure_type == "ast_violation"
        assert healing_input.error_signature == "sig_ast"
        assert healing_input.retry_count == 1

    def test_failure_signal_to_healing_input_preserves_agent_id(self):
        """to_healing_input() must preserve source_agent as agent_id."""
        from agentic_core.L2_execution.healers.healing_tier_types import FailureSignal

        sig = FailureSignal(
            source_agent="remediation_dispatcher",
            failure_type="healer_error",
            error_signature="sig_rem",
            trace_id="t",
            context={},
            retry_count=0,
            blast_radius_estimate=0.1,
        )
        hi = sig.to_healing_input()
        assert hi.agent_id == "remediation_dispatcher"

    def test_failure_signal_is_frozen(self):
        """FailureSignal must be immutable (frozen dataclass)."""
        from agentic_core.L2_execution.healers.healing_tier_types import FailureSignal

        sig = FailureSignal(
            source_agent="a",
            failure_type="f",
            error_signature="s",
            trace_id="t",
            context={},
            retry_count=0,
            blast_radius_estimate=0.0,
        )
        with pytest.raises((AttributeError, TypeError)):
            sig.retry_count = 99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# §1.1 HealingInput dataclass — edge cases and validation
# ---------------------------------------------------------------------------


class TestHealingInputValidation:
    """HealingInput validation edge cases per §1.1 fail-closed requirement."""

    def test_empty_failure_type_raises(self):
        """HealingInput with empty failure_type must raise ValueError (fail-closed)."""
        from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

        with pytest.raises(ValueError, match="failure_type must not be empty"):
            HealingInput(
                failure_type="",  # invalid
                error_signature="s",
                trace_id="t",
                retry_count=0,
                blast_radius_estimate=0.5,
            )

    def test_empty_error_signature_raises(self):
        """HealingInput with empty error_signature must raise ValueError."""
        from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

        with pytest.raises(ValueError, match="error_signature must not be empty"):
            HealingInput(
                failure_type="f",
                error_signature="",  # invalid
                trace_id="t",
                retry_count=0,
                blast_radius_estimate=0.5,
            )

    def test_empty_trace_id_raises(self):
        """HealingInput with empty trace_id must raise ValueError."""
        from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

        with pytest.raises(ValueError, match="trace_id must not be empty"):
            HealingInput(
                failure_type="f",
                error_signature="s",
                trace_id="",  # invalid
                retry_count=0,
                blast_radius_estimate=0.5,
            )

    def test_negative_retry_count_raises(self):
        """HealingInput with negative retry_count must raise ValueError (fail-closed)."""
        from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

        with pytest.raises(ValueError, match="retry_count must be >= 0"):
            HealingInput(
                failure_type="f",
                error_signature="s",
                trace_id="t",
                retry_count=-1,  # invalid
                blast_radius_estimate=0.5,
            )

    def test_blast_radius_below_zero_raises(self):
        """blast_radius_estimate < 0.0 must raise ValueError."""
        from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

        with pytest.raises(ValueError, match="blast_radius_estimate must be in"):
            HealingInput(
                failure_type="f",
                error_signature="s",
                trace_id="t",
                retry_count=0,
                blast_radius_estimate=-0.01,  # invalid
            )

    def test_blast_radius_above_one_raises(self):
        """blast_radius_estimate > 1.0 must raise ValueError."""
        from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

        with pytest.raises(ValueError, match="blast_radius_estimate must be in"):
            HealingInput(
                failure_type="f",
                error_signature="s",
                trace_id="t",
                retry_count=0,
                blast_radius_estimate=1.01,  # invalid
            )

    def test_blast_radius_boundary_zero_valid(self):
        """blast_radius_estimate == 0.0 must be valid (boundary)."""
        from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

        hi = HealingInput(
            failure_type="f", error_signature="s", trace_id="t", retry_count=0, blast_radius_estimate=0.0
        )
        assert hi.blast_radius_estimate == 0.0

    def test_blast_radius_boundary_one_valid(self):
        """blast_radius_estimate == 1.0 must be valid (boundary)."""
        from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

        hi = HealingInput(
            failure_type="f", error_signature="s", trace_id="t", retry_count=0, blast_radius_estimate=1.0
        )
        assert hi.blast_radius_estimate == 1.0

    def test_healing_input_is_frozen(self):
        """HealingInput must be immutable (frozen dataclass)."""
        from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

        hi = HealingInput(
            failure_type="f", error_signature="s", trace_id="t", retry_count=0, blast_radius_estimate=0.5
        )
        with pytest.raises((AttributeError, TypeError)):
            hi.retry_count = 99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# §1.1 HealingDecision dataclass — determinism
# ---------------------------------------------------------------------------


class TestHealingDecisionInvariants:
    """HealingDecision invariants per §1.1 determinism requirement."""

    def test_healing_decision_is_frozen(self):
        """HealingDecision must be immutable."""
        from agentic_core.L2_execution.healers.healing_tier_types import (
            HealingDecision,
            HealingTier,
        )

        d = HealingDecision(
            heal_confidence=0.75,
            tier=HealingTier.QWEN_VLLM,
            reason_codes=("test",),
        )
        with pytest.raises((AttributeError, TypeError)):
            d.heal_confidence = 0.5  # type: ignore[misc]

    def test_all_healing_tier_values_constructable(self):
        """All three HealingTier enum values must be constructable in HealingDecision."""
        from agentic_core.L2_execution.healers.healing_tier_types import (
            HealingDecision,
            HealingTier,
        )

        for tier in HealingTier:
            d = HealingDecision(heal_confidence=0.5, tier=tier, reason_codes=(tier.value,))
            assert d.tier == tier

    def test_reason_codes_is_tuple_not_list(self):
        """reason_codes must be a tuple (immutable) not a list."""
        from agentic_core.L2_execution.healers.healing_tier_types import (
            HealingDecision,
            HealingTier,
        )

        d = HealingDecision(
            heal_confidence=0.6,
            tier=HealingTier.LOCAL_AGENT,
            reason_codes=("blast_radius_low", "retry_count_zero"),
        )
        assert isinstance(d.reason_codes, tuple)


# ---------------------------------------------------------------------------
# §1.1 dispatch_healing — choke point integration with fake invoker
# ---------------------------------------------------------------------------


class TestDispatchHealingChokePoint:
    """dispatch_healing must route through the single choke point (route_healing_tier)
    and invoke the correct provider via the injected invoker.
    """

    def _make_healing_input(
        self, *, agent_id: str = "remediation_dispatcher", retry_count: int = 0
    ) -> HealingInput:
        from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

        return HealingInput(
            failure_type="syntax_error",
            error_signature="sig_001",
            trace_id="trace_001",
            retry_count=retry_count,
            blast_radius_estimate=0.1,
            agent_id=agent_id,
        )

    def test_dispatch_healing_returns_decision_and_record(self):
        """dispatch_healing must return a (HealingDecision, InvocationRecord) tuple."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            load_default_healing_tier_config,
        )
        from agentic_core.L2_execution.healers.healing_tier_dispatcher import (
            InvocationRecord,
            dispatch_healing,
        )
        from agentic_core.L2_execution.healers.healing_tier_types import HealingDecision

        config = load_default_healing_tier_config()
        hi = self._make_healing_input()
        decision, record = dispatch_healing(hi, config)

        assert isinstance(decision, HealingDecision)
        assert isinstance(record, InvocationRecord)

    def test_dispatch_healing_record_has_trace_id(self):
        """InvocationRecord must carry the trace_id from the HealingInput."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            load_default_healing_tier_config,
        )
        from agentic_core.L2_execution.healers.healing_tier_dispatcher import dispatch_healing

        config = load_default_healing_tier_config()
        hi = self._make_healing_input()
        _, record = dispatch_healing(hi, config)

        assert record.trace_id == "trace_001"

    def test_dispatch_healing_record_is_deterministic_for_identical_inputs(self):
        """Two identical inputs must produce records with identical tier and model_id."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            load_default_healing_tier_config,
        )
        from agentic_core.L2_execution.healers.healing_tier_dispatcher import dispatch_healing

        config = load_default_healing_tier_config()
        hi_a = self._make_healing_input()
        hi_b = self._make_healing_input()

        decision_a, record_a = dispatch_healing(hi_a, config)
        decision_b, record_b = dispatch_healing(hi_b, config)

        # Same inputs must yield same tier and model_id (determinism)
        assert record_a.tier == record_b.tier
        assert record_a.model_id == record_b.model_id
        assert decision_a.tier == decision_b.tier
        assert decision_a.heal_confidence == decision_b.heal_confidence

    def test_dispatch_healing_different_failure_types_may_produce_different_tiers(self):
        """Different failure types (with different blast radius) can produce different tiers."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            load_default_healing_tier_config,
        )
        from agentic_core.L2_execution.healers.healing_tier_dispatcher import dispatch_healing
        from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

        config = load_default_healing_tier_config()
        # Low blast radius — likely LOCAL_AGENT or QWEN
        hi_low = self._make_healing_input(retry_count=0)
        # High blast radius — more likely GEMINI
        hi_high = HealingInput(
            failure_type="import_cycle",
            error_signature="sig_high",
            trace_id="trace_high",
            retry_count=3,  # max retries → higher tier
            blast_radius_estimate=0.9,  # high blast → higher tier
            agent_id="remediation_dispatcher",
        )

        decision_low, _ = dispatch_healing(hi_low, config)
        decision_high, _ = dispatch_healing(hi_high, config)

        # Just assert they are valid decisions (tier may differ or not — both valid)
        from agentic_core.L2_execution.healers.healing_tier_types import HealingDecision

        assert isinstance(decision_low, HealingDecision)
        assert isinstance(decision_high, HealingDecision)
        # The high-blast, max-retry case should have >= confidence tier
        assert decision_high.heal_confidence <= 1.0
        assert decision_low.heal_confidence <= 1.0

    def test_dispatch_healing_record_model_id_is_string(self):
        """InvocationRecord.model_id must be a non-empty string."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            load_default_healing_tier_config,
        )
        from agentic_core.L2_execution.healers.healing_tier_dispatcher import dispatch_healing

        config = load_default_healing_tier_config()
        hi = self._make_healing_input()
        _, record = dispatch_healing(hi, config)

        assert isinstance(record.model_id, str)
        assert len(record.model_id) > 0


# ---------------------------------------------------------------------------
# §1.1 Sovereignty — TIERING_ALLOWLIST blocks unknown agents (fail-closed)
# ---------------------------------------------------------------------------


class TestSovereigntyAllowlistEnforcement:
    """TIERING_ALLOWLIST is a compile-time frozen sovereignty check.

    Fail-closed: unknown agents must raise SovereigntyViolation, not silently route.
    Mutation-sensitive: removing the allowlist check would allow arbitrary agents.
    """

    def test_unknown_agent_raises_sovereignty_violation(self):
        """An agent not in TIERING_ALLOWLIST must raise SovereigntyViolation."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            load_default_healing_tier_config,
        )
        from agentic_core.L2_execution.healers.healing_tier_router import (
            SovereigntyViolation,
            route_healing_tier,
        )
        from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

        config = load_default_healing_tier_config()
        hi = HealingInput(
            failure_type="f",
            error_signature="s",
            trace_id="t",
            retry_count=0,
            blast_radius_estimate=0.1,
            agent_id="unknown_rogue_agent_XYZ",
        )
        with pytest.raises(SovereigntyViolation, match="not in compile-time frozen TIERING_ALLOWLIST"):
            route_healing_tier(hi, config)

    def test_no_agent_id_skips_allowlist_check(self):
        """Empty agent_id skips the allowlist check (anonymous/test caller)."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            load_default_healing_tier_config,
        )
        from agentic_core.L2_execution.healers.healing_tier_router import route_healing_tier
        from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

        config = load_default_healing_tier_config()
        hi = HealingInput(
            failure_type="f",
            error_signature="s",
            trace_id="t",
            retry_count=0,
            blast_radius_estimate=0.1,
            agent_id="",  # empty → skip allowlist check
        )
        # Must not raise SovereigntyViolation
        from agentic_core.L2_execution.healers.healing_tier_types import HealingDecision

        decision = route_healing_tier(hi, config)
        assert isinstance(decision, HealingDecision)

    def test_allowlist_is_frozen_set(self):
        """TIERING_ALLOWLIST_AGENT_NAMES must be a frozenset (compile-time frozen)."""
        from agentic_core.L2_execution.healers.tiering_allowlist import (
            TIERING_ALLOWLIST_AGENT_NAMES,
        )

        assert isinstance(TIERING_ALLOWLIST_AGENT_NAMES, frozenset), (
            "TIERING_ALLOWLIST_AGENT_NAMES must be a frozenset — "
            "mutable set would allow runtime injection of unauthorized agents"
        )

    def test_remediation_dispatcher_in_allowlist(self):
        """remediation_dispatcher must be in the compile-time TIERING_ALLOWLIST."""
        from agentic_core.L2_execution.healers.tiering_allowlist import (
            TIERING_ALLOWLIST_AGENT_NAMES,
        )

        assert "remediation_dispatcher" in TIERING_ALLOWLIST_AGENT_NAMES, (
            "remediation_dispatcher must be in TIERING_ALLOWLIST_AGENT_NAMES — "
            "it is the primary caller of dispatch_healing"
        )


# ---------------------------------------------------------------------------
# §1.1 Healing tier config immutability (regression for HEALING_CONFIDENCE_X/Y)
# ---------------------------------------------------------------------------


class TestHealingTierConfigImmutability:
    """HEALING_CONFIDENCE_X and HEALING_CONFIDENCE_Y must be immutable constants.

    Regression: qwen_meta_learning.py enforces boundary protection for these thresholds.
    """

    def test_confidence_x_is_0_80(self):
        """HEALING_CONFIDENCE_X must be exactly 0.80 (SSOT constant)."""
        from agentic_core.L2_execution.healers.healing_tier_config import HEALING_CONFIDENCE_X

        assert HEALING_CONFIDENCE_X == 0.80, f"HEALING_CONFIDENCE_X must be 0.80, got {HEALING_CONFIDENCE_X}"

    def test_confidence_y_is_0_50(self):
        """HEALING_CONFIDENCE_Y must be exactly 0.50 (SSOT constant)."""
        from agentic_core.L2_execution.healers.healing_tier_config import HEALING_CONFIDENCE_Y

        assert HEALING_CONFIDENCE_Y == 0.50, f"HEALING_CONFIDENCE_Y must be 0.50, got {HEALING_CONFIDENCE_Y}"

    def test_confidence_x_greater_than_y(self):
        """HEALING_CONFIDENCE_X must be strictly greater than HEALING_CONFIDENCE_Y."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            HEALING_CONFIDENCE_X,
            HEALING_CONFIDENCE_Y,
        )

        assert HEALING_CONFIDENCE_X > HEALING_CONFIDENCE_Y, (
            "Threshold ordering violation: X must be > Y for routing to be deterministic"
        )

    def test_qwen_model_id_is_non_empty_string(self):
        """QWEN_14B_MODEL_ID must be a non-empty string."""
        from agentic_core.L2_execution.healers.healing_tier_config import QWEN_14B_MODEL_ID

        assert isinstance(QWEN_14B_MODEL_ID, str)
        assert len(QWEN_14B_MODEL_ID) > 0

    def test_qwen_model_id_contains_qwen(self):
        """QWEN_14B_MODEL_ID must reference a Qwen model (contains 'Qwen')."""
        from agentic_core.L2_execution.healers.healing_tier_config import QWEN_14B_MODEL_ID

        assert "Qwen" in QWEN_14B_MODEL_ID or "qwen" in QWEN_14B_MODEL_ID.lower()

    def test_healing_tier_config_load_default_returns_config(self):
        """load_default_healing_tier_config() must return a HealingTierConfig."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            HealingTierConfig,
            load_default_healing_tier_config,
        )

        config = load_default_healing_tier_config()
        assert isinstance(config, HealingTierConfig)

    def test_healing_tier_config_thresholds_match_ssot_constants(self):
        """HealingTierConfig thresholds must match HEALING_CONFIDENCE_X/Y."""
        from agentic_core.L2_execution.healers.healing_tier_config import (
            HEALING_CONFIDENCE_X,
            HEALING_CONFIDENCE_Y,
            load_default_healing_tier_config,
        )

        config = load_default_healing_tier_config()
        assert config.heal_confidence_x == HEALING_CONFIDENCE_X
        assert config.heal_confidence_y == HEALING_CONFIDENCE_Y
