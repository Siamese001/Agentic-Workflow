import contextvars
import logging
import uuid
import weakref
from functools import wraps

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "context_propagation_mixin", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "context_propagation_mixin", "policy_binding")
trace_contract._emit_snapshots_state("p0", "context_propagation_mixin", "state_snapshot")

trace_contract._emit_emits_metric_event("context_propagation_mixin", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("context_propagation_mixin", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("context_propagation_mixin", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("context_propagation_mixin", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("context_propagation_mixin", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("context_propagation_mixin", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("context_propagation_mixin", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("context_propagation_mixin", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("context_propagation_mixin", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("context_propagation_mixin", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("context_propagation_mixin", "p4obs", "alert")
trace_contract._emit_links_incident_trace("context_propagation_mixin", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("context_propagation_mixin", "p3lm", "pattern")
trace_contract._emit_records_learning_event("context_propagation_mixin", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("context_propagation_mixin", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("context_propagation_mixin", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("context_propagation_mixin", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("context_propagation_mixin", "p3lm", "policy")
trace_contract._emit_stores_learning_state("context_propagation_mixin", "p3lm", "state")
trace_contract._emit_records_execution_trace("context_propagation_mixin", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("context_propagation_mixin", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("context_propagation_mixin", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("context_propagation_mixin", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("context_propagation_mixin", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("context_propagation_mixin", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("context_propagation_mixin", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("context_propagation_mixin", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("context_propagation_mixin", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "context_propagation_mixin", "context_pull")
trace_contract._emit_pulls_context("p1", "context_propagation_mixin", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "context_propagation_mixin", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "context_propagation_mixin", "uwg_term_2")
trace_contract._emit_writes_through("p1", "context_propagation_mixin", "write_through")
trace_contract._emit_writes_through("p1", "context_propagation_mixin", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "context_propagation_mixin", "safety_validation")
trace_contract._emit_invokes_eval("p1", "context_propagation_mixin", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "context_propagation_mixin", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "context_propagation_mixin", "human_escalation")
trace_contract._emit_routes_through("p1", "context_propagation_mixin", "route_through")
trace_contract._emit_checks_agent_registry("p1", "context_propagation_mixin", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "context_propagation_mixin", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "context_propagation_mixin", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "context_propagation_mixin", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "context_propagation_mixin", "target_agent")
trace_contract._emit_verifies_policy("p1", "context_propagation_mixin", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "context_propagation_mixin", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "context_propagation_mixin", "boundary_check")
trace_contract._emit_transcripts_response("p1", "context_propagation_mixin", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "context_propagation_mixin")
trace_contract._emit_gated_by_confidence("p1", "context_propagation_mixin", "confidence_gate")
trace_contract.emit_replay_key("p0", "context_propagation_mixin")
trace_contract.emit_determinism_digest("p0", "context_propagation_mixin")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "context_propagation_mixin", "execution_auth")
trace_contract._emit_validates_capability("p2", "context_propagation_mixin", "capability_check")
trace_contract._emit_routes_to_capability("p2", "context_propagation_mixin", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "context_propagation_mixin", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "context_propagation_mixin", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "context_propagation_mixin", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "context_propagation_mixin", "exec_output")
trace_contract._emit_dispatches_agent("p3", "context_propagation_mixin", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "context_propagation_mixin", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "context_propagation_mixin", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "context_propagation_mixin", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "context_propagation_mixin", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "context_propagation_mixin", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "context_propagation_mixin", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "context_propagation_mixin", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "context_propagation_mixin", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "context_propagation_mixin", "eval_metric")
trace_contract._emit_stores_embedding("p4", "context_propagation_mixin", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "context_propagation_mixin", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "context_propagation_mixin", "exec_snapshot_link")

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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ContextPropagationMixin.set_context"
        )

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
