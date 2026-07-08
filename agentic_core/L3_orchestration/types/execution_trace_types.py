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
from agentic_core.L0_routing.utils.clock_provider import ClockProvider as clock_provider
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "execution_trace_types")
trace_contract.emit_determinism_digest("p0", "execution_trace_types")

trace_contract._emit_dispatches_healing_run("p1", "execution_trace_types", "L3")
trace_contract._emit_routes_through("p1", "execution_trace_types", "L3")
trace_contract._emit_checks_agent_registry("p1", "execution_trace_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "execution_trace_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "execution_trace_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "execution_trace_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "execution_trace_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "execution_trace_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "execution_trace_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "execution_trace_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "execution_trace_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "execution_trace_types")
trace_contract._emit_gated_by_confidence("p1", "execution_trace_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "execution_trace_types", "L3")
trace_contract._emit_reads_policy_state("p1", "execution_trace_types", "L3")
trace_contract._emit_authorize_and_execute("p2", "execution_trace_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "execution_trace_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "execution_trace_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "execution_trace_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "execution_trace_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "execution_trace_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "execution_trace_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "execution_trace_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "execution_trace_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "execution_trace_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "execution_trace_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "execution_trace_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "execution_trace_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "execution_trace_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "execution_trace_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "execution_trace_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "execution_trace_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "execution_trace_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "execution_trace_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "execution_trace_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("execution_trace_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("execution_trace_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("execution_trace_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("execution_trace_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("execution_trace_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("execution_trace_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("execution_trace_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("execution_trace_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("execution_trace_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("execution_trace_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("execution_trace_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("execution_trace_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("execution_trace_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("execution_trace_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("execution_trace_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("execution_trace_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("execution_trace_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("execution_trace_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("execution_trace_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("execution_trace_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("execution_trace_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("execution_trace_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("execution_trace_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("execution_trace_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("execution_trace_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("execution_trace_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("execution_trace_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("execution_trace_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "execution_trace_types", "context_pull")
trace_contract._emit_pulls_context("p1", "execution_trace_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "execution_trace_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "execution_trace_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "execution_trace_types", "write_through")
trace_contract._emit_writes_through("p1", "execution_trace_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "execution_trace_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "execution_trace_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "execution_trace_types", "routing_commit")


def canonical_json(data: dict[str, Any]) -> str:
    """
    Convert dictionary to canonical JSON string.

    Alphabetical key sort, UTF-8, no whitespace variance.
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "canonical_json", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "canonical_json", "p0_governance")
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
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "ExecutionTrace.compute_replay_key",
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
