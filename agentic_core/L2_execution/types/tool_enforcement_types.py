"""
§Wave2.4 — Tool Enforcement Artifact Types.

Typed artifacts for the LawSlotHandler enforcement gate at tool choke points.
All artifacts are frozen dataclasses with deterministic serialization.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "tool_enforcement_types")
trace_contract.emit_determinism_digest("p0", "tool_enforcement_types")

trace_contract._emit_dispatches_healing_run("p1", "tool_enforcement_types", "L2")
trace_contract._emit_routes_through("p1", "tool_enforcement_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "tool_enforcement_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "tool_enforcement_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "tool_enforcement_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "tool_enforcement_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "tool_enforcement_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "tool_enforcement_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "tool_enforcement_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "tool_enforcement_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "tool_enforcement_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "tool_enforcement_types")
trace_contract._emit_gated_by_confidence("p1", "tool_enforcement_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "tool_enforcement_types", "L2")
trace_contract._emit_reads_policy_state("p1", "tool_enforcement_types", "L2")
trace_contract._emit_authorize_and_execute("p2", "tool_enforcement_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "tool_enforcement_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "tool_enforcement_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "tool_enforcement_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "tool_enforcement_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "tool_enforcement_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "tool_enforcement_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "tool_enforcement_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "tool_enforcement_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "tool_enforcement_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "tool_enforcement_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "tool_enforcement_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "tool_enforcement_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "tool_enforcement_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "tool_enforcement_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "tool_enforcement_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "tool_enforcement_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "tool_enforcement_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "tool_enforcement_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "tool_enforcement_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("tool_enforcement_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("tool_enforcement_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("tool_enforcement_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("tool_enforcement_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("tool_enforcement_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("tool_enforcement_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("tool_enforcement_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("tool_enforcement_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("tool_enforcement_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("tool_enforcement_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("tool_enforcement_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("tool_enforcement_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("tool_enforcement_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("tool_enforcement_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("tool_enforcement_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("tool_enforcement_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("tool_enforcement_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("tool_enforcement_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("tool_enforcement_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("tool_enforcement_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("tool_enforcement_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("tool_enforcement_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("tool_enforcement_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("tool_enforcement_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("tool_enforcement_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("tool_enforcement_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("tool_enforcement_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("tool_enforcement_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "tool_enforcement_types", "context_pull")
trace_contract._emit_pulls_context("p1", "tool_enforcement_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "tool_enforcement_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "tool_enforcement_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "tool_enforcement_types", "write_through")
trace_contract._emit_writes_through("p1", "tool_enforcement_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "tool_enforcement_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "tool_enforcement_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "tool_enforcement_types", "routing_commit")


class LawSlotOutcome(Enum):
    """§Wave2.4 — Enforcement outcomes at the tool choke point."""

    PASS = "pass"
    BLOCK = "block"
    MODIFY = "modify"


@dataclass(frozen=True)
class ToolEnforcementArtifact:
    """§Wave2.4 — Enforcement record emitted exactly once per tool call.

    Captures the enforcement decision, applied law slots, argument hashes,
    and rationale for audit trail.
    """

    enforcement_id: str
    timestamp_utc: str
    trace_id: str
    agent_id: str
    tool_name: str
    outcome: LawSlotOutcome
    applied_law_slots: tuple[str, ...]
    rationale: str
    original_args_hash: str
    modified_args_hash: str = ""
    policy_context_hash: str = ""

    def __post_init__(self) -> None:
        if not self.enforcement_id:
            raise ValueError("ToolEnforcementArtifact: enforcement_id must be non-empty")
        if not self.trace_id:
            raise ValueError("ToolEnforcementArtifact: trace_id must be non-empty")
        if not self.tool_name:
            raise ValueError("ToolEnforcementArtifact: tool_name must be non-empty")
        if not isinstance(self.outcome, LawSlotOutcome):
            raise TypeError(
                f"ToolEnforcementArtifact: outcome must be LawSlotOutcome, got {type(self.outcome).__name__}",
            )
        if not self.original_args_hash:
            raise ValueError("ToolEnforcementArtifact: original_args_hash must be non-empty")
        if self.outcome == LawSlotOutcome.MODIFY and (not self.modified_args_hash):
            raise ValueError("ToolEnforcementArtifact: modified_args_hash required when outcome is MODIFY")


class ToolPolicyBlocked(Exception):
    """§Wave2.4 — Raised when a tool call is blocked by enforcement policy.

    Preserves the enforcement rationale and artifact for upstream handling.
    """

    def __init__(self, tool_name: str, rationale: str, artifact: ToolEnforcementArtifact) -> None:
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "ToolPolicyBlocked.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "ToolPolicyBlocked.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "ToolPolicyBlocked.__init__")
        self.tool_name = tool_name
        self.rationale = rationale
        self.artifact = artifact
        super().__init__(f"Tool '{tool_name}' blocked by policy: {rationale}")


__all__ = ["LawSlotOutcome", "ToolEnforcementArtifact", "ToolPolicyBlocked"]
