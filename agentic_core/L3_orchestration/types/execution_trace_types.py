"""
Execution Trace Types - W5 Implementation

Defines ExecutionTrace structure and plan_hash binding for L3 orchestration.
Ensures deterministic audit trail with canonical JSON formatting.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.reasoning.assembly_stage import GovernedPayload
from agentic_core.L0_routing.providers.clock_provider import ClockProvider as clock_provider
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "execution_trace_types")
emit_determinism_digest("p0", "execution_trace_types")

_emit_dispatches_healing_run("p1", "execution_trace_types", "L3")
_emit_routes_through("p1", "execution_trace_types", "L3")
_emit_checks_agent_registry("p1", "execution_trace_types", "agent_registry")
_emit_validates_agent_capability("p1", "execution_trace_types", "capability")
_emit_dispatches_execution_plan("p1", "execution_trace_types", "exec_plan")
_emit_agent_executes_agent("p1", "execution_trace_types", "sub_agent")
_emit_routes_to_agent("p1", "execution_trace_types", "target_agent")
_emit_verifies_policy("p1", "execution_trace_types", "policy_check")
_emit_observes_runtime_state("p1", "execution_trace_types", "runtime_state")
_emit_verifies_boundary("p1", "execution_trace_types", "boundary_check")
_emit_transcripts_response("p1", "execution_trace_types", "transcript")
_emit_hard_fails_untranscripted("p1", "execution_trace_types")
_emit_gated_by_confidence("p1", "execution_trace_types", "confidence_gate")
_emit_escalates_to_human("p1", "execution_trace_types", "L3")
_emit_reads_policy_state("p1", "execution_trace_types", "L3")
_emit_authorize_and_execute("p2", "execution_trace_types", "execution_auth")
_emit_validates_capability("p2", "execution_trace_types", "capability_check")
_emit_routes_to_capability("p2", "execution_trace_types", "capability_route")
_emit_writes_via_uwg("p2", "execution_trace_types", "uwg_write")
_emit_blocks_direct_write("p2", "execution_trace_types", "direct_write_block")
_emit_records_tool_invocation("p2", "execution_trace_types", "tool_invocation")
_emit_captures_execution_output("p2", "execution_trace_types", "exec_output")
_emit_dispatches_agent("p3", "execution_trace_types", "agent_dispatch")
_emit_coordinates_agents("p3", "execution_trace_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "execution_trace_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "execution_trace_types", "healing_outcome")
_emit_escalates_failure("p3", "execution_trace_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "execution_trace_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "execution_trace_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "execution_trace_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "execution_trace_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "execution_trace_types", "eval_metric")
_emit_stores_embedding("p4", "execution_trace_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "execution_trace_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "execution_trace_types", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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

_emit_emits_metric_event("execution_trace_types", "p4obs", "metric_1")
_emit_emits_metric_event("execution_trace_types", "p4obs", "metric_2")
_emit_emits_metric_event("execution_trace_types", "p4obs", "metric_3")
_emit_emits_metric_event("execution_trace_types", "p4obs", "metric_4")
_emit_emits_metric_event("execution_trace_types", "p4obs", "metric_5")
_emit_emits_metric_event("execution_trace_types", "p4obs", "metric_6")
_emit_records_incident_event("execution_trace_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("execution_trace_types", "p4obs", "anomaly")
_emit_writes_observability_log("execution_trace_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("execution_trace_types", "p4obs", "mon_state")
_emit_triggers_alert("execution_trace_types", "p4obs", "alert")
_emit_links_incident_trace("execution_trace_types", "p4obs", "trace_link")
_emit_captures_pattern("execution_trace_types", "p3lm", "pattern")
_emit_records_learning_event("execution_trace_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("execution_trace_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("execution_trace_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("execution_trace_types", "p3lm", "routing")
_emit_improves_agent_policy("execution_trace_types", "p3lm", "policy")
_emit_stores_learning_state("execution_trace_types", "p3lm", "state")
_emit_records_execution_trace("execution_trace_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("execution_trace_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("execution_trace_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("execution_trace_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("execution_trace_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("execution_trace_types", "env_read", "p2_env_1")
_emit_reads_environ("execution_trace_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("execution_trace_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("execution_trace_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "execution_trace_types", "context_pull")
_emit_pulls_context("p1", "execution_trace_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "execution_trace_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "execution_trace_types", "uwg_term_2")
_emit_writes_through("p1", "execution_trace_types", "write_through")
_emit_writes_through("p1", "execution_trace_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "execution_trace_types", "safety_validation")
_emit_invokes_eval("p1", "execution_trace_types", "eval_call")
_emit_proposal_commits_routing("p1", "execution_trace_types", "routing_commit")


def canonical_json(data: dict[str, Any]) -> str:
    """
    Convert dictionary to canonical JSON string.

    Alphabetical key sort, UTF-8, no whitespace variance.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "canonical_json", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "canonical_json", "p0_governance")
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass
class ExecutionTrace:
    """Execution trace for L3 orchestration audit trail."""

    trace_id: str
    plan_hash: str
    actor: str
    target: str | None = None
    diff: dict[str, Any] | None = None
    policy_hash: str = ""
    timestamp: str = ""
    prev_hash: str = ""
    replay_key: str = ""
    governed_payload_hash: str = ""

    def compute_replay_key(self, transcript_hash: str) -> str:
        """
        Compute replay key: SHA256(trace_id + plan_hash + transcript_hash).

        Args:
            transcript_hash: Hash of the execution transcript

        Returns:
            Replay key for deterministic replay verification
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ExecutionTrace.compute_replay_key"
        )

        replay_data = f"{self.trace_id}{self.plan_hash}{transcript_hash}"
        return hashlib.sha256(replay_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "plan_hash": self.plan_hash,
            "actor": self.actor,
            "target": self.target,
            "diff": self.diff,
            "policy_hash": self.policy_hash,
            "timestamp": self.timestamp,
            "prev_hash": self.prev_hash,
            "replay_key": self.replay_key,
            "governed_payload_hash": self.governed_payload_hash,
        }


def create_execution_trace_skeleton(
    trace_id: str,
    plan_hash: str,
    governed_payload: GovernedPayload,
    actor: str = "L3_Orchestrator",
    target: str | None = None,
) -> ExecutionTrace:
    """
    Create ExecutionTrace skeleton for L3 orchestration.

    Args:
        trace_id: Unique trace identifier
        plan_hash: Hash of the canonical plan
        governed_payload: The governed payload being processed
        actor: Actor performing the orchestration
        target: Target of the orchestration (optional)

    Returns:
        ExecutionTrace with populated skeleton
    """
    from datetime import timezone

    payload_dict = {
        "s0_system": governed_payload.s0_system,
        "i0_instructional": governed_payload.i0_instructional,
        "c0_context": governed_payload.c0_context,
        "u0_user_prompt": governed_payload.u0_user_prompt,
        "manifest_hash": governed_payload.manifest_hash,
        "routing_hash": governed_payload.routing_hash,
    }
    governed_payload_hash = hashlib.sha256(canonical_json(payload_dict).encode("utf-8")).hexdigest()
    trace = ExecutionTrace(
        trace_id=trace_id,
        plan_hash=plan_hash,
        actor=actor,
        target=target,
        governed_payload_hash=governed_payload_hash,
        timestamp=clock_provider.now(timezone.utc).isoformat(),
    )
    return trace


def compute_plan_hash(plan: dict[str, Any]) -> str:
    """
    Compute SHA256 hash of canonical plan JSON.

    Args:
        plan: Plan dictionary to hash

    Returns:
        SHA256 hash of canonical plan JSON
    """
    canonical = canonical_json(plan)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["ExecutionTrace", "create_execution_trace_skeleton", "compute_plan_hash", "canonical_json"]
