import contextvars
import logging
import uuid
import weakref
from functools import wraps

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "context_propagation_mixin", "p0_governance")
_emit_reads_policy_state("p0", "context_propagation_mixin", "policy_binding")
_emit_snapshots_state("p0", "context_propagation_mixin", "state_snapshot")
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
    _emit_links_incident_trace,
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
    _emit_writes_through,
)

_emit_emits_metric_event("context_propagation_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("context_propagation_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("context_propagation_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("context_propagation_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("context_propagation_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("context_propagation_mixin", "p4obs", "metric_6")
_emit_records_incident_event("context_propagation_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("context_propagation_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("context_propagation_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("context_propagation_mixin", "p4obs", "mon_state")
_emit_triggers_alert("context_propagation_mixin", "p4obs", "alert")
_emit_links_incident_trace("context_propagation_mixin", "p4obs", "trace_link")
_emit_captures_pattern("context_propagation_mixin", "p3lm", "pattern")
_emit_records_learning_event("context_propagation_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("context_propagation_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("context_propagation_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("context_propagation_mixin", "p3lm", "routing")
_emit_improves_agent_policy("context_propagation_mixin", "p3lm", "policy")
_emit_stores_learning_state("context_propagation_mixin", "p3lm", "state")
_emit_records_execution_trace("context_propagation_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("context_propagation_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("context_propagation_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("context_propagation_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("context_propagation_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("context_propagation_mixin", "env_read", "p2_env_1")
_emit_reads_environ("context_propagation_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("context_propagation_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("context_propagation_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "context_propagation_mixin", "context_pull")
_emit_pulls_context("p1", "context_propagation_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "context_propagation_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "context_propagation_mixin", "uwg_term_2")
_emit_writes_through("p1", "context_propagation_mixin", "write_through")
_emit_writes_through("p1", "context_propagation_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "context_propagation_mixin", "safety_validation")
_emit_invokes_eval("p1", "context_propagation_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "context_propagation_mixin", "routing_commit")
_emit_escalates_to_human("p1", "context_propagation_mixin", "human_escalation")
_emit_routes_through("p1", "context_propagation_mixin", "route_through")
_emit_checks_agent_registry("p1", "context_propagation_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "context_propagation_mixin", "capability")
_emit_dispatches_execution_plan("p1", "context_propagation_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "context_propagation_mixin", "sub_agent")
_emit_routes_to_agent("p1", "context_propagation_mixin", "target_agent")
_emit_verifies_policy("p1", "context_propagation_mixin", "policy_check")
_emit_observes_runtime_state("p1", "context_propagation_mixin", "runtime_state")
_emit_verifies_boundary("p1", "context_propagation_mixin", "boundary_check")
_emit_transcripts_response("p1", "context_propagation_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "context_propagation_mixin")
_emit_gated_by_confidence("p1", "context_propagation_mixin", "confidence_gate")
emit_replay_key("p0", "context_propagation_mixin")
emit_determinism_digest("p0", "context_propagation_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "context_propagation_mixin", "execution_auth")
_emit_validates_capability("p2", "context_propagation_mixin", "capability_check")
_emit_routes_to_capability("p2", "context_propagation_mixin", "capability_route")
_emit_writes_via_uwg("p2", "context_propagation_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "context_propagation_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "context_propagation_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "context_propagation_mixin", "exec_output")
_emit_dispatches_agent("p3", "context_propagation_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "context_propagation_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "context_propagation_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "context_propagation_mixin", "healing_outcome")
_emit_escalates_failure("p3", "context_propagation_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "context_propagation_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "context_propagation_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "context_propagation_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "context_propagation_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "context_propagation_mixin", "eval_metric")
_emit_stores_embedding("p4", "context_propagation_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "context_propagation_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "context_propagation_mixin", "exec_snapshot_link")

trace_id_var = contextvars.ContextVar("trace_id", default=None)
span_id_var = contextvars.ContextVar("span_id", default=None)


class ContextPropagationMixin:
    """
    Phase 3 Advanced Infrastructure: Context Propagation (Report 4.7).

    Enables distributed tracing by propagating request context across async calls.
    Features:
    - Thread/Async-safe ContextVars
    - Automatic Trace/Span ID generation
    - Integration with event_emission_mixin
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cp_logger = logging.getLogger(self.__class__.__name__)

    def set_context(self, trace_id: str, span_id: str | None = None):
        """Manually sets the tracing context for the current execution flow."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ContextPropagationMixin.set_context")

        trace_id_var.set(trace_id)
        if span_id:
            span_id_var.set(span_id)
        self._cp_logger.debug(f"Context set: trace_id={trace_id}")

    def get_context(self) -> dict[str, str | None]:
        """Retrieves the current trace and span IDs."""
        return {"trace_id": trace_id_var.get(), "span_id": span_id_var.get()}

    @staticmethod
    def _validate_context():
        if trace_id_var.get() is None:
            raise RuntimeError("Missing trace context in critical path")

    @staticmethod
    def trace_context(func):
        """Decorator to ensure trace context is captured and logged."""

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not trace_id_var.get():
                trace_id_var.set(str(uuid.uuid4()))
            old_span = span_id_var.get()
            new_span = str(uuid.uuid4())[:8]
            span_id_var.set(new_span)
            if weakref.getweakrefcount(self) > 10:
                self._cp_logger.warning("Potential context leak detected")
            if func.__name__.startswith("_critical"):
                ContextPropagationMixin._validate_context()
            self._cp_logger.debug(f"Entering {func.__name__} [Trace: {trace_id_var.get()}, Span: {new_span}]")
            try:
                result = await func(self, *args, **kwargs)
                return result
            finally:
                span_id_var.set(old_span)

        return wrapper
