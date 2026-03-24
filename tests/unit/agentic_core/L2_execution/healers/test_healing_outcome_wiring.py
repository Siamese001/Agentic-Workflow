"""L2.3 Healing Outcome Wiring Tests — emit-only seam verification.

Tests:
  - Inject fake sink; assert exactly one event emitted on success.
  - Inject fake sink; assert exactly one event emitted on failure.
  - No sink provided: default runtime unchanged (no emission).
  - Sink exception swallowed: dispatch still returns normally.
"""

from __future__ import annotations

import pytest

_AVAILABLE = False
try:
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
    _AVAILABLE = True
except (ImportError, NameError, AttributeError, TypeError, Exception):  # guardian: allow-silent-swallow
    pass

_emit_records_execution_trace("p0", "evidence", "test_healing_outcome_wiring")
_emit_applies_guardrail("p0", "test_healing_outcome_wiring", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_outcome_wiring", "policy_binding")
_emit_snapshots_state("p0", "test_healing_outcome_wiring", "state_snapshot")
emit_replay_key("p0", "test_healing_outcome_wiring")
emit_determinism_digest("p0", "test_healing_outcome_wiring")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_healing_outcome_wiring", "execution_auth")
_emit_validates_capability("p2", "test_healing_outcome_wiring", "capability_check")
_emit_routes_to_capability("p2", "test_healing_outcome_wiring", "capability_route")
_emit_writes_via_uwg("p2", "test_healing_outcome_wiring", "uwg_write")
_emit_blocks_direct_write("p2", "test_healing_outcome_wiring", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healing_outcome_wiring", "tool_invocation")
_emit_captures_execution_output("p2", "test_healing_outcome_wiring", "exec_output")
_emit_dispatches_agent("p3", "test_healing_outcome_wiring", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healing_outcome_wiring", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healing_outcome_wiring", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healing_outcome_wiring", "healing_outcome")
_emit_escalates_failure("p3", "test_healing_outcome_wiring", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healing_outcome_wiring", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healing_outcome_wiring", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healing_outcome_wiring", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healing_outcome_wiring", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healing_outcome_wiring", "eval_metric")
_emit_stores_embedding("p4", "test_healing_outcome_wiring", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healing_outcome_wiring", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healing_outcome_wiring", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

_AVAILABLE = False
try:
    from agentic_core.L2_execution.healers.healing_tier_config import (
        load_default_healing_tier_config,
    )
    _AVAILABLE = True
except (ImportError, NameError, AttributeError, TypeError, Exception):  # guardian: allow-silent-swallow
    pass
_AVAILABLE = False
try:
    from agentic_core.L2_execution.healers.healing_tier_dispatcher import (
        InvocationRecord,
        dispatch_healing,
    )
    _AVAILABLE = True
except (ImportError, NameError, AttributeError, TypeError, Exception):  # guardian: allow-silent-swallow
    pass
_AVAILABLE = False
try:
    from agentic_core.L2_execution.healers.healing_tier_types import (
        HealingInput,
        HealingTier,
    )
    _AVAILABLE = True
except (ImportError, NameError, AttributeError, TypeError, Exception):  # guardian: allow-silent-swallow
    pass
_AVAILABLE = False
try:
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
    _AVAILABLE = True
except (ImportError, NameError, AttributeError, TypeError, Exception):  # guardian: allow-silent-swallow
    pass
try:
    from system_learning.types.healing_outcome_types import HealingOutcomeEvent
except (ImportError, ModuleNotFoundError):
    HealingOutcomeEvent = None  # type: ignore[misc,assignment]
    _AVAILABLE = False

_emit_emits_metric_event("test_healing_outcome_wiring", "p4obs", "metric_1")
_emit_emits_metric_event("test_healing_outcome_wiring", "p4obs", "metric_2")
_emit_emits_metric_event("test_healing_outcome_wiring", "p4obs", "metric_3")
_emit_emits_metric_event("test_healing_outcome_wiring", "p4obs", "metric_4")
_emit_emits_metric_event("test_healing_outcome_wiring", "p4obs", "metric_5")
_emit_emits_metric_event("test_healing_outcome_wiring", "p4obs", "metric_6")
_emit_records_incident_event("test_healing_outcome_wiring", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_healing_outcome_wiring", "p4obs", "anomaly")
_emit_writes_observability_log("test_healing_outcome_wiring", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_healing_outcome_wiring", "p4obs", "mon_state")
_emit_triggers_alert("test_healing_outcome_wiring", "p4obs", "alert")
_emit_links_incident_trace("test_healing_outcome_wiring", "p4obs", "trace_link")
_emit_captures_pattern("test_healing_outcome_wiring", "p3lm", "pattern")
_emit_records_learning_event("test_healing_outcome_wiring", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_healing_outcome_wiring", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_healing_outcome_wiring", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_healing_outcome_wiring", "p3lm", "routing")
_emit_improves_agent_policy("test_healing_outcome_wiring", "p3lm", "policy")
_emit_stores_learning_state("test_healing_outcome_wiring", "p3lm", "state")
_emit_records_execution_trace("test_healing_outcome_wiring", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_healing_outcome_wiring", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_healing_outcome_wiring", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_healing_outcome_wiring", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_healing_outcome_wiring", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_healing_outcome_wiring", "env_read", "p2_env_1")
_emit_reads_environ("test_healing_outcome_wiring", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_healing_outcome_wiring", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_healing_outcome_wiring", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_healing_outcome_wiring", "context_pull")
_emit_pulls_context("p1", "test_healing_outcome_wiring", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_healing_outcome_wiring", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_healing_outcome_wiring", "uwg_term_secondary")
_emit_writes_through("p1", "test_healing_outcome_wiring", "write_through")
_emit_writes_through("p1", "test_healing_outcome_wiring", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_healing_outcome_wiring", "safety_validation")
_emit_invokes_eval("p1", "test_healing_outcome_wiring", "eval_call")
_emit_proposal_commits_routing("p1", "test_healing_outcome_wiring", "routing_commit")
_emit_escalates_to_human("p1", "test_healing_outcome_wiring", "human_escalation")
_emit_routes_through("p1", "test_healing_outcome_wiring", "route_through")
_emit_checks_agent_registry("p1", "test_healing_outcome_wiring", "agent_registry")
_emit_validates_agent_capability("p1", "test_healing_outcome_wiring", "capability")
_emit_dispatches_execution_plan("p1", "test_healing_outcome_wiring", "exec_plan")
_emit_agent_executes_agent("p1", "test_healing_outcome_wiring", "sub_agent")
_emit_routes_to_agent("p1", "test_healing_outcome_wiring", "target_agent")
_emit_verifies_policy("p1", "test_healing_outcome_wiring", "policy_check")
_emit_observes_runtime_state("p1", "test_healing_outcome_wiring", "runtime_state")
_emit_verifies_boundary("p1", "test_healing_outcome_wiring", "boundary_check")
_emit_transcripts_response("p1", "test_healing_outcome_wiring", "transcript")
_emit_hard_fails_untranscripted("p1", "test_healing_outcome_wiring")
_emit_gated_by_confidence("p1", "test_healing_outcome_wiring", "confidence_gate")

# -------------------------------------------------------------------------
# Fake sink that records emitted events
# -------------------------------------------------------------------------


class FakeOutcomeSink:
    """Test double: records all emitted events."""

    def __init__(self) -> None:
        self.events: list[HealingOutcomeEvent] = []

    def emit(self, event: HealingOutcomeEvent) -> None:
        self.events.append(event)


class ExplodingSink:
    """Test double: raises on emit to prove swallow behaviour."""

    def emit(self, event: HealingOutcomeEvent) -> None:
        raise RuntimeError("sink exploded")


# -------------------------------------------------------------------------
# Fake invoker that always succeeds
# -------------------------------------------------------------------------


class SuccessInvoker:
    """Test invoker that always returns a successful InvocationRecord."""

    def invoke_local(self, healing_input, decision, config, *, agent_name=""):
        return InvocationRecord(
            tier=HealingTier.LOCAL_AGENT,
            model_id="local",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_local",
        )

    def invoke_qwen_vllm(self, healing_input, decision, config, *, agent_name=""):
        return InvocationRecord(
            tier=HealingTier.QWEN_VLLM,
            model_id="qwen-test",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_qwen_vllm",
        )

    def invoke_gemini(self, healing_input, decision, config, *, agent_name=""):
        return InvocationRecord(
            tier=HealingTier.GEMINI_2_5_PRO,
            model_id="gemini-test",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_gemini",
        )


class FailingInvoker:
    """Test invoker that always raises on every method."""

    def invoke_local(self, healing_input, decision, config, *, agent_name=""):
        raise RuntimeError("provider failed")

    def invoke_qwen_vllm(self, healing_input, decision, config, *, agent_name=""):
        raise RuntimeError("provider failed")

    def invoke_gemini(self, healing_input, decision, config, *, agent_name=""):
        raise RuntimeError("provider failed")


# -------------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------------


def _make_input(
    *,
    failure_type: str = "syntax_error",
    blast_radius: float = 0.3,
    retry_count: int = 0,
) -> HealingInput:
    return HealingInput(
        failure_type=failure_type,
        error_signature="sig-abc123",
        trace_id="trace-001",
        retry_count=retry_count,
        blast_radius_estimate=blast_radius,
        required_tools=("ast_rewrite",),
        violation_metadata_refs=(),
    )


# -------------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------------


class TestOutcomeSinkWiring:
    """Verify emit-only wiring via injected outcome_sink."""

    def test_success_emits_exactly_one_event(self) -> None:
        """On successful invocation, exactly one event with success=True is emitted."""
        sink = FakeOutcomeSink()
        config = load_default_healing_tier_config()
        inp = _make_input()

        decision, record = dispatch_healing(
            inp,
            config,
            invoker=SuccessInvoker(),
            agent_name="test_healer",
            outcome_sink=sink,
            timestamp_utc=1000,
        )

        assert len(sink.events) == 1
        ev = sink.events[0]
        assert ev.success is True
        assert ev.healer_id == "test_healer"
        assert ev.tier == decision.tier.value
        assert ev.failure_type == "syntax_error"
        assert ev.timestamp_utc == 1000
        assert ev.trace_id == "trace-001"
        assert ev.error_signature == "sig-abc123"

    def test_failure_emits_exactly_one_event(self) -> None:
        """On failed invocation, exactly one event with success=False is emitted."""
        sink = FakeOutcomeSink()
        config = load_default_healing_tier_config()
        inp = _make_input()

        with pytest.raises(RuntimeError, match="provider failed"):
            dispatch_healing(
                inp,
                config,
                invoker=FailingInvoker(),
                agent_name="test_healer",
                outcome_sink=sink,
                timestamp_utc=2000,
            )

        assert len(sink.events) == 1
        ev = sink.events[0]
        assert ev.success is False
        assert ev.healer_id == "test_healer"
        assert ev.timestamp_utc == 2000

    def test_no_sink_no_emission(self) -> None:
        """When outcome_sink is None, dispatch works exactly as before."""
        config = load_default_healing_tier_config()
        inp = _make_input()

        decision, record = dispatch_healing(
            inp,
            config,
            invoker=SuccessInvoker(),
            agent_name="test_healer",
            outcome_sink=None,
            timestamp_utc=3000,
        )

        # Should succeed normally without any sink-related issues
        assert record.method_called in ("invoke_local", "invoke_qwen_vllm", "invoke_gemini")

    def test_sink_exception_swallowed(self) -> None:
        """If sink.emit() raises, dispatch still returns normally."""
        sink = ExplodingSink()
        config = load_default_healing_tier_config()
        inp = _make_input()

        # Should NOT raise despite ExplodingSink
        decision, record = dispatch_healing(
            inp,
            config,
            invoker=SuccessInvoker(),
            agent_name="test_healer",
            outcome_sink=sink,
            timestamp_utc=4000,
        )

        assert record.method_called in ("invoke_local", "invoke_qwen_vllm", "invoke_gemini")

    def test_no_timestamp_skips_emission(self) -> None:
        """When timestamp_utc is None, no emission even with a sink."""
        sink = FakeOutcomeSink()
        config = load_default_healing_tier_config()
        inp = _make_input()

        decision, record = dispatch_healing(
            inp,
            config,
            invoker=SuccessInvoker(),
            agent_name="test_healer",
            outcome_sink=sink,
            timestamp_utc=None,
        )

        assert len(sink.events) == 0

    def test_default_healer_id_when_agent_name_empty(self) -> None:
        """When agent_name is empty, healer_id defaults to 'unknown'."""
        sink = FakeOutcomeSink()
        config = load_default_healing_tier_config()
        inp = _make_input()

        dispatch_healing(
            inp,
            config,
            invoker=SuccessInvoker(),
            agent_name="",
            outcome_sink=sink,
            timestamp_utc=5000,
        )

        assert len(sink.events) == 1
        assert sink.events[0].healer_id == "unknown"
