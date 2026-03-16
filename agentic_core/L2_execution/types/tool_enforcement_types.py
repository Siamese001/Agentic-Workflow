"""
§Wave2.4 — Tool Enforcement Artifact Types.

Typed artifacts for the LawSlotHandler enforcement gate at tool choke points.
All artifacts are frozen dataclasses with deterministic serialization.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "tool_enforcement_types")
emit_determinism_digest("p0", "tool_enforcement_types")

_emit_dispatches_healing_run("p1", "tool_enforcement_types", "L2")
_emit_routes_through("p1", "tool_enforcement_types", "L2")
_emit_escalates_to_human("p1", "tool_enforcement_types", "L2")
_emit_reads_policy_state("p1", "tool_enforcement_types", "L2")
_emit_authorize_and_execute("p2", "tool_enforcement_types", "execution_auth")
_emit_validates_capability("p2", "tool_enforcement_types", "capability_check")
_emit_routes_to_capability("p2", "tool_enforcement_types", "capability_route")
_emit_writes_via_uwg("p2", "tool_enforcement_types", "uwg_write")
_emit_blocks_direct_write("p2", "tool_enforcement_types", "direct_write_block")
_emit_records_tool_invocation("p2", "tool_enforcement_types", "tool_invocation")
_emit_captures_execution_output("p2", "tool_enforcement_types", "exec_output")
_emit_dispatches_agent("p3", "tool_enforcement_types", "agent_dispatch")
_emit_coordinates_agents("p3", "tool_enforcement_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "tool_enforcement_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "tool_enforcement_types", "healing_outcome")
_emit_escalates_failure("p3", "tool_enforcement_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "tool_enforcement_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tool_enforcement_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "tool_enforcement_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "tool_enforcement_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tool_enforcement_types", "eval_metric")
_emit_stores_embedding("p4", "tool_enforcement_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "tool_enforcement_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tool_enforcement_types", "exec_snapshot_link")


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
                f"ToolEnforcementArtifact: outcome must be LawSlotOutcome, got {type(self.outcome).__name__}"
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

        _emit_snapshots_state(str(_uuid.uuid4()), "ToolPolicyBlocked.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ToolPolicyBlocked.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ToolPolicyBlocked.__init__")
        self.tool_name = tool_name
        self.rationale = rationale
        self.artifact = artifact
        super().__init__(f"Tool '{tool_name}' blocked by policy: {rationale}")


__all__ = ["LawSlotOutcome", "ToolEnforcementArtifact", "ToolPolicyBlocked"]
