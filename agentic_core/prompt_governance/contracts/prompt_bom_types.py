"""PromptBOM data contract — L0 → Assembly Stage handoff.

Defines the immutable Bill of Materials for prompt assembly.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

# Self-bootstrap governance wiring
trace_contract._emit_authorize_and_execute("p2", "PromptBOM", "execution_auth")
trace_contract._emit_validates_capability("p2", "PromptBOM", "capability_check")
trace_contract._emit_routes_to_capability("p2", "PromptBOM", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "PromptBOM", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "PromptBOM", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "PromptBOM", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "PromptBOM", "exec_output")
trace_contract._emit_dispatches_agent("p3", "PromptBOM", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "PromptBOM", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "PromptBOM", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "PromptBOM", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "PromptBOM", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "PromptBOM", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "PromptBOM", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "PromptBOM", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "PromptBOM", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "PromptBOM", "eval_metric")
trace_contract._emit_stores_embedding("p4", "PromptBOM", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "PromptBOM", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "PromptBOM", "exec_snapshot_link")
trace_contract._emit_dispatches_healing_run("p1", "PromptBOM", "L0")
trace_contract._emit_routes_through("p1", "PromptBOM", "L0")
trace_contract._emit_checks_agent_registry("p1", "PromptBOM", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "PromptBOM", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "PromptBOM", "exec_plan")
trace_contract._emit_routes_to_agent("p1", "PromptBOM", "target_agent")
trace_contract._emit_verifies_policy("p1", "PromptBOM", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "PromptBOM", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "PromptBOM", "boundary_check")
trace_contract._emit_transcripts_response("p1", "PromptBOM", "transcript")
trace_contract._emit_gated_by_confidence("p1", "PromptBOM", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "PromptBOM", "L0")
trace_contract._emit_reads_policy_state("p1", "PromptBOM", "L0")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "PromptBOM", "p0_governance")
trace_contract._emit_snapshots_state("p0", "PromptBOM", "state_snapshot")


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
    # EQ-3 (ADR-PROMPT-ASSEMBLY-001 Q1): optional M0 and H0 carriers.
    # Both default to absent; legacy callers that construct a 5-slot BOM
    # continue to work unchanged.
    meta_cognitive_mixin_id: str | None = None
    healing_context: str | None = None
    # Y0 synthesis and R0 output format carriers (EQ-18).
    # Both default to absent; legacy callers that construct a BOM
    # without Y0/R0 continue to work unchanged.
    synthesis_required: tuple[str, ...] = ()
    output_format_schema: str | None = None

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
            "meta_cognitive_mixin_id": self.meta_cognitive_mixin_id,
            "healing_context": self.healing_context,
            "synthesis_required": tuple(sorted(self.synthesis_required)),
            "output_format_schema": self.output_format_schema,
        }

    def stable_hash(self) -> str:
        """Compute content-addressed SHA-256 hash."""
        canonical = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["PromptBOM"]
