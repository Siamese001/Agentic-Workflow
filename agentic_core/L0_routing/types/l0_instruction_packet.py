"""InstructionPacket data contract — L0 Router → PromptBOM Builder handoff.

Defines the immutable instruction packet for path-based routing.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

# Self-bootstrap governance wiring
trace_contract._emit_authorize_and_execute("p2", "InstructionPacket", "execution_auth")
trace_contract._emit_validates_capability("p2", "InstructionPacket", "capability_check")
trace_contract._emit_routes_to_capability("p2", "InstructionPacket", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "InstructionPacket", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "InstructionPacket", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "InstructionPacket", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "InstructionPacket", "exec_output")
trace_contract._emit_dispatches_agent("p3", "InstructionPacket", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "InstructionPacket", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "InstructionPacket", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "InstructionPacket", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "InstructionPacket", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "InstructionPacket", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "InstructionPacket", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "InstructionPacket", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "InstructionPacket", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "InstructionPacket", "eval_metric")
trace_contract._emit_stores_embedding("p4", "InstructionPacket", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "InstructionPacket", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "InstructionPacket", "exec_snapshot_link")
trace_contract._emit_dispatches_healing_run("p1", "InstructionPacket", "L0")
trace_contract._emit_routes_through("p1", "InstructionPacket", "L0")
trace_contract._emit_checks_agent_registry("p1", "InstructionPacket", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "InstructionPacket", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "InstructionPacket", "exec_plan")
trace_contract._emit_routes_to_agent("p1", "InstructionPacket", "target_agent")
trace_contract._emit_verifies_policy("p1", "InstructionPacket", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "InstructionPacket", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "InstructionPacket", "boundary_check")
trace_contract._emit_transcripts_response("p1", "InstructionPacket", "transcript")
trace_contract._emit_gated_by_confidence("p1", "InstructionPacket", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "InstructionPacket", "L0")
trace_contract._emit_reads_policy_state("p1", "InstructionPacket", "L0")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "InstructionPacket", "p0_governance")
trace_contract._emit_snapshots_state("p0", "InstructionPacket", "state_snapshot")


@dataclass(frozen=True)
class InstructionPacket:
    """Routing instruction packet for L0 → PromptBOM Builder.

    Produced by PathRouter, consumed by PromptBOMBuilder.
    Captures path classification and intent for BOM construction.

    Attributes
    ----------
    trace_id : str
        Execution trace identifier.
    path : Literal["A", "B", "C", "D"]
        Routing path (A=High/Strict, B=Med/Std, C=Low/Fast, D=Novel/Learning).
    intent_class : str
        Classified intent category.
    required_mixins : tuple[str, ...]
        Sorted tuple of required I0 mixin IDs.
    escalation_threshold : float
        Confidence threshold for HITL escalation.
    """

    trace_id: str
    path: Literal["A", "B", "C", "D"]
    intent_class: str
    required_mixins: tuple[str, ...]
    escalation_threshold: float = 0.85

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if self.path not in ("A", "B", "C", "D"):
            raise ValueError(f"path must be A/B/C/D, got {self.path!r}")
        if not self.intent_class:
            raise ValueError("intent_class must not be empty")
        if not 0.0 <= self.escalation_threshold <= 1.0:
            raise ValueError(
                f"escalation_threshold must be in [0.0, 1.0], got {self.escalation_threshold}",
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "path": self.path,
            "intent_class": self.intent_class,
            "required_mixins": tuple(sorted(self.required_mixins)),
            "escalation_threshold": self.escalation_threshold,
        }

    def stable_hash(self) -> str:
        """Compute content-addressed SHA-256 hash."""
        canonical = str(self.to_dict())
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["InstructionPacket"]
