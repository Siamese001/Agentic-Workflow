"""
baggage_propagator.py - Context Propagator Module

Domain: tracing
Generated: 2025-12-07T12:07:59.853999
"""

import logging

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "baggage_propagator_util", "p0_governance")
_emit_reads_policy_state("p0", "baggage_propagator_util", "policy_binding")
_emit_snapshots_state("p0", "baggage_propagator_util", "state_snapshot")
emit_replay_key("p0", "baggage_propagator_util")
emit_determinism_digest("p0", "baggage_propagator_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "baggage_propagator_util", "execution_auth")
_emit_validates_capability("p2", "baggage_propagator_util", "capability_check")
_emit_routes_to_capability("p2", "baggage_propagator_util", "capability_route")
_emit_writes_via_uwg("p2", "baggage_propagator_util", "uwg_write")
_emit_blocks_direct_write("p2", "baggage_propagator_util", "direct_write_block")
_emit_records_tool_invocation("p2", "baggage_propagator_util", "tool_invocation")
_emit_captures_execution_output("p2", "baggage_propagator_util", "exec_output")
_emit_dispatches_agent("p3", "baggage_propagator_util", "agent_dispatch")
_emit_coordinates_agents("p3", "baggage_propagator_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "baggage_propagator_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "baggage_propagator_util", "healing_outcome")
_emit_escalates_failure("p3", "baggage_propagator_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "baggage_propagator_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "baggage_propagator_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "baggage_propagator_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "baggage_propagator_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "baggage_propagator_util", "eval_metric")
_emit_stores_embedding("p4", "baggage_propagator_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "baggage_propagator_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "baggage_propagator_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class BaggagePropagator:
    """Context propagator for tracing domain."""

    HEADER_TRACE_ID = "X-Trace-ID"
    HEADER_SPAN_ID = "X-Span-ID"
    HEADER_SAMPLED = "X-Sampled"

    def __init__(self, config: dict[str, object] | None = None):
        self.config = config or {}
        logger.info(f"Initialized {self.__class__.__name__}")

    def inject(self, context: dict[str, object], carrier: dict[str, str]) -> None:
        """Inject context into carrier."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BaggagePropagator.inject")

        if "trace_id" in context:
            carrier[self.HEADER_TRACE_ID] = context["trace_id"]
        if "span_id" in context:
            carrier[self.HEADER_SPAN_ID] = context["span_id"]
        if "sampled" in context:
            carrier[self.HEADER_SAMPLED] = "1" if context["sampled"] else "0"

    def extract(self, carrier: dict[str, str]) -> dict[str, object]:
        """Extract context from carrier."""
        context = {}
        if self.HEADER_TRACE_ID in carrier:
            context["trace_id"] = carrier[self.HEADER_TRACE_ID]
        if self.HEADER_SPAN_ID in carrier:
            context["span_id"] = carrier[self.HEADER_SPAN_ID]
        if self.HEADER_SAMPLED in carrier:
            context["sampled"] = carrier[self.HEADER_SAMPLED] == "1"
        return context


def inject_context(context: dict[str, object], carrier: dict[str, str], config: dict | None = None) -> None:
    """Inject context into carrier."""
    BaggagePropagator(config).inject(context, carrier)


def extract_context(carrier: dict[str, str], config: dict | None = None) -> dict[str, object]:
    """Extract context from carrier."""
    return BaggagePropagator(config).extract(carrier)
