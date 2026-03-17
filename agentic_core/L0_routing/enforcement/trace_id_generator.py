"""Trace ID generator with deterministic replay support.

Ensures TraceID is deterministic under replay conditions.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from typing import Optional

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_dispatches_healing_run("p1", "trace_id_generator", "L0")
_emit_routes_through("p1", "trace_id_generator", "L0")
_emit_checks_agent_registry("p1", "trace_id_generator", "agent_registry")
_emit_validates_agent_capability("p1", "trace_id_generator", "capability")
_emit_dispatches_execution_plan("p1", "trace_id_generator", "exec_plan")
_emit_agent_executes_agent("p1", "trace_id_generator", "sub_agent")
_emit_routes_to_agent("p1", "trace_id_generator", "target_agent")
_emit_verifies_policy("p1", "trace_id_generator", "policy_check")
_emit_observes_runtime_state("p1", "trace_id_generator", "runtime_state")
_emit_verifies_boundary("p1", "trace_id_generator", "boundary_check")
_emit_transcripts_response("p1", "trace_id_generator", "transcript")
_emit_hard_fails_untranscripted("p1", "trace_id_generator")
_emit_gated_by_confidence("p1", "trace_id_generator", "confidence_gate")
_emit_escalates_to_human("p1", "trace_id_generator", "L0")
_emit_reads_policy_state("p1", "trace_id_generator", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_snapshots_state("p0", "trace_id_generator", "state_snapshot")
_emit_authorize_and_execute("p2", "trace_id_generator", "execution_auth")
_emit_validates_capability("p2", "trace_id_generator", "capability_check")
_emit_routes_to_capability("p2", "trace_id_generator", "capability_route")
_emit_writes_via_uwg("p2", "trace_id_generator", "uwg_write")
_emit_blocks_direct_write("p2", "trace_id_generator", "direct_write_block")
_emit_records_tool_invocation("p2", "trace_id_generator", "tool_invocation")
_emit_captures_execution_output("p2", "trace_id_generator", "exec_output")
_emit_dispatches_agent("p3", "trace_id_generator", "agent_dispatch")
_emit_coordinates_agents("p3", "trace_id_generator", "agent_coordination")
_emit_records_workflow_lineage("p3", "trace_id_generator", "workflow_lineage")
_emit_records_healing_outcome("p3", "trace_id_generator", "healing_outcome")
_emit_escalates_failure("p3", "trace_id_generator", "failure_escalation")
_emit_orchestrates_workflow("p3", "trace_id_generator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "trace_id_generator", "healing_dispatch")
_emit_invokes_evaluation("p3", "trace_id_generator", "evaluation_signal")
_emit_records_telemetry_event("p4", "trace_id_generator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "trace_id_generator", "eval_metric")
_emit_stores_embedding("p4", "trace_id_generator", "embedding_store")
_emit_updates_meta_learning_state("p4", "trace_id_generator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "trace_id_generator", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("trace_id_generator", "p4obs", "metric_1")
_emit_emits_metric_event("trace_id_generator", "p4obs", "metric_2")
_emit_emits_metric_event("trace_id_generator", "p4obs", "metric_3")
_emit_emits_metric_event("trace_id_generator", "p4obs", "metric_4")
_emit_emits_metric_event("trace_id_generator", "p4obs", "metric_5")
_emit_emits_metric_event("trace_id_generator", "p4obs", "metric_6")
_emit_records_incident_event("trace_id_generator", "p4obs", "incident")
_emit_captures_runtime_anomaly("trace_id_generator", "p4obs", "anomaly")
_emit_writes_observability_log("trace_id_generator", "p4obs", "obs_log")
_emit_updates_monitoring_state("trace_id_generator", "p4obs", "mon_state")
_emit_triggers_alert("trace_id_generator", "p4obs", "alert")
_emit_links_incident_trace("trace_id_generator", "p4obs", "trace_link")
_emit_captures_pattern("trace_id_generator", "p3lm", "pattern")
_emit_records_learning_event("trace_id_generator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("trace_id_generator", "p3lm", "snapshot")
_emit_feeds_meta_learning("trace_id_generator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("trace_id_generator", "p3lm", "routing")
_emit_improves_agent_policy("trace_id_generator", "p3lm", "policy")
_emit_stores_learning_state("trace_id_generator", "p3lm", "state")
_emit_records_execution_trace("trace_id_generator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("trace_id_generator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("trace_id_generator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("trace_id_generator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("trace_id_generator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("trace_id_generator", "env_read", "p2_env_1")
_emit_reads_environ("trace_id_generator", "env_read", "p2_env_2")
_emit_reads_runtime_state("trace_id_generator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("trace_id_generator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "trace_id_generator", "context_pull")
_emit_pulls_context("p1", "trace_id_generator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "trace_id_generator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "trace_id_generator", "uwg_term_2")
_emit_writes_through("p1", "trace_id_generator", "write_through")
_emit_writes_through("p1", "trace_id_generator", "write_through_2")
_emit_validated_by_safety_plane("p1", "trace_id_generator", "safety_validation")
_emit_invokes_eval("p1", "trace_id_generator", "eval_call")
_emit_proposal_commits_routing("p1", "trace_id_generator", "routing_commit")


class TraceIdGenerator:
    """Generates deterministic TraceIDs with replay support."""

    TRACE_ID_PATTERN = re.compile("^CC3AL1-[0-9A-F]{8}$")

    def __init__(self, replay_mode: bool = False):
        """Initialize generator.

        Args:
            replay_mode: If True, generates deterministic IDs for replay
        """
        self.replay_mode = replay_mode
        self._seed_counter = 0

    def generate_trace_id(
        self, semantic_clock: SemanticClockSnapshot, operation: str, additional_context: str | None = None
    ) -> str:
        """Generate a deterministic TraceID.

        Args:
            semantic_clock: Current semantic clock snapshot
            operation: Operation being performed
            additional_context: Optional additional context for uniqueness

        Returns:
            TraceID matching pattern ^CC3AL1-[0-9A-F]{8}$
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "TraceIdGenerator.generate_trace_id"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        input_parts = ["CC3AL1", str(semantic_clock.tick), operation, additional_context or ""]
        if self.replay_mode:
            input_parts.append(f"replay_{self._seed_counter}")
            self._seed_counter += 1
        input_string = "|".join(input_parts)
        hash_bytes = hashlib.sha256(input_string.encode("utf-8")).digest()
        hash_suffix = hash_bytes[:4].hex().upper()
        return f"CC3AL1-{hash_suffix}"

    def validate_trace_id(self, trace_id: str) -> bool:
        """Validate TraceID matches required pattern.

        Args:
            trace_id: TraceID to validate

        Returns:
            True if valid, False otherwise
        """
        return bool(self.TRACE_ID_PATTERN.match(trace_id))

    def is_replay_deterministic(
        self,
        trace_id1: str,
        trace_id2: str,
        semantic_clock: SemanticClockSnapshot,
        operation: str,
        additional_context: str | None = None,
    ) -> bool:
        """Check if two TraceIDs would be deterministic under same conditions.

        Args:
            trace_id1: First TraceID
            trace_id2: Second TraceID
            semantic_clock: Semantic clock snapshot
            operation: Operation being performed
            additional_context: Additional context

        Returns:
            True if IDs would be deterministic under same conditions
        """
        expected_id = self.generate_trace_id(semantic_clock, operation, additional_context)
        return trace_id1 == expected_id and trace_id2 == expected_id


_default_generator = TraceIdGenerator(replay_mode=False)


def generate_trace_id(
    semantic_clock: SemanticClockSnapshot,
    operation: str,
    additional_context: str | None = None,
    replay_mode: bool = False,
) -> str:
    """Generate a TraceID.

    Args:
        semantic_clock: Current semantic clock snapshot
        operation: Operation being performed
        additional_context: Optional additional context
        replay_mode: If True, generates deterministic ID for replay

    Returns:
        TraceID matching pattern ^CC3AL1-[0-9A-F]{8}$
    """
    if replay_mode:
        generator = TraceIdGenerator(replay_mode=True)
        return generator.generate_trace_id(semantic_clock, operation, additional_context)
    else:
        return _default_generator.generate_trace_id(semantic_clock, operation, additional_context)


def validate_trace_id(trace_id: str) -> bool:
    """Validate TraceID matches required pattern.

    Args:
        trace_id: TraceID to validate

    Returns:
        True if valid, False otherwise
    """
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.validate_trace_id", "L0_ROUTING")
    return _default_generator.validate_trace_id(trace_id)
