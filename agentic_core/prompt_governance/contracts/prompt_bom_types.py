"""PromptBOM data contract — L0 → Assembly Stage handoff.

Defines the immutable Bill of Materials for prompt assembly.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
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
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
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
)

# Self-bootstrap governance wiring
_emit_authorize_and_execute("p2", "PromptBOM", "execution_auth")
_emit_validates_capability("p2", "PromptBOM", "capability_check")
_emit_routes_to_capability("p2", "PromptBOM", "capability_route")
_emit_writes_via_uwg("p2", "PromptBOM", "uwg_write")
_emit_blocks_direct_write("p2", "PromptBOM", "direct_write_block")
_emit_records_tool_invocation("p2", "PromptBOM", "tool_invocation")
_emit_captures_execution_output("p2", "PromptBOM", "exec_output")
_emit_dispatches_agent("p3", "PromptBOM", "agent_dispatch")
_emit_coordinates_agents("p3", "PromptBOM", "agent_coordination")
_emit_records_workflow_lineage("p3", "PromptBOM", "workflow_lineage")
_emit_records_healing_outcome("p3", "PromptBOM", "healing_outcome")
_emit_escalates_failure("p3", "PromptBOM", "failure_escalation")
_emit_orchestrates_workflow("p3", "PromptBOM", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "PromptBOM", "healing_dispatch")
_emit_invokes_evaluation("p3", "PromptBOM", "evaluation_signal")
_emit_records_telemetry_event("p4", "PromptBOM", "telemetry_event")
_emit_captures_evaluation_metric("p4", "PromptBOM", "eval_metric")
_emit_stores_embedding("p4", "PromptBOM", "embedding_store")
_emit_updates_meta_learning_state("p4", "PromptBOM", "meta_learning")
_emit_links_execution_to_snapshot("p4", "PromptBOM", "exec_snapshot_link")
_emit_dispatches_healing_run("p1", "PromptBOM", "L0")
_emit_routes_through("p1", "PromptBOM", "L0")
_emit_checks_agent_registry("p1", "PromptBOM", "agent_registry")
_emit_validates_agent_capability("p1", "PromptBOM", "capability")
_emit_dispatches_execution_plan("p1", "PromptBOM", "exec_plan")
_emit_routes_to_agent("p1", "PromptBOM", "target_agent")
_emit_verifies_policy("p1", "PromptBOM", "policy_check")
_emit_observes_runtime_state("p1", "PromptBOM", "runtime_state")
_emit_verifies_boundary("p1", "PromptBOM", "boundary_check")
_emit_transcripts_response("p1", "PromptBOM", "transcript")
_emit_gated_by_confidence("p1", "PromptBOM", "confidence_gate")
_emit_escalates_to_human("p1", "PromptBOM", "L0")
_emit_reads_policy_state("p1", "PromptBOM", "L0")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "PromptBOM", "p0_governance")
_emit_snapshots_state("p0", "PromptBOM", "state_snapshot")


@dataclass(frozen=True)
class PromptBOM:
    """Bill of Materials for prompt assembly.

    Immutable contract between L0 Router and Assembly Stage.
    Contains pointers only — no inline prompt strings.

    Attributes
    ----------
    trace_id : str
        Execution trace identifier.
    system_version_hash : str
        SHA-256 hash of S0 system prompt version.
    mixins_required : tuple[str, ...]
        Sorted tuple of I0 mixin IDs required.
    exemplars_required : tuple[str, ...]
        Sorted tuple of E0 exemplar IDs required (Golden Context, few-shot).
    raw_u0 : str
        Raw user input (U0 slot content).
    raw_c0 : dict[str, Any]
        Context pointers for C0 slot (not content).
    template_args : dict[str, Any]
        Template variable bindings.
    path : Literal["A", "B", "C", "D"]
        Routing path selected by PathRouter.
    """

    trace_id: str
    system_version_hash: str
    mixins_required: tuple[str, ...]
    raw_u0: str
    raw_c0: dict[str, Any]
    template_args: dict[str, Any]
    path: Literal["A", "B", "C", "D"]
    exemplars_required: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if not self.system_version_hash:
            raise ValueError("system_version_hash must not be empty")
        if self.path not in ("A", "B", "C", "D"):
            raise ValueError(f"path must be A/B/C/D, got {self.path!r}")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "system_version_hash": self.system_version_hash,
            "mixins_required": tuple(sorted(self.mixins_required)),
            "exemplars_required": tuple(sorted(self.exemplars_required)),
            "raw_u0": self.raw_u0,
            "raw_c0": dict(self.raw_c0),
            "template_args": dict(self.template_args),
            "path": self.path,
        }

    def stable_hash(self) -> str:
        """Compute content-addressed SHA-256 hash."""
        canonical = str(self.to_dict())
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["PromptBOM"]
