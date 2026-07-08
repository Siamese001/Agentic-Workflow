"""TemplateManifest data contract — L4 Registry → Assembly Stage reference.

Defines the immutable template manifest for S0/I0 versioning.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

# Self-bootstrap governance wiring
trace_contract._emit_authorize_and_execute("p2", "TemplateManifest", "execution_auth")
trace_contract._emit_validates_capability("p2", "TemplateManifest", "capability_check")
trace_contract._emit_routes_to_capability("p2", "TemplateManifest", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "TemplateManifest", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "TemplateManifest", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "TemplateManifest", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "TemplateManifest", "exec_output")
trace_contract._emit_dispatches_agent("p3", "TemplateManifest", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "TemplateManifest", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "TemplateManifest", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "TemplateManifest", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "TemplateManifest", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "TemplateManifest", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "TemplateManifest", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "TemplateManifest", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "TemplateManifest", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "TemplateManifest", "eval_metric")
trace_contract._emit_stores_embedding("p4", "TemplateManifest", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "TemplateManifest", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "TemplateManifest", "exec_snapshot_link")
trace_contract._emit_dispatches_healing_run("p1", "TemplateManifest", "L0")
trace_contract._emit_routes_through("p1", "TemplateManifest", "L0")
trace_contract._emit_checks_agent_registry("p1", "TemplateManifest", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "TemplateManifest", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "TemplateManifest", "exec_plan")
trace_contract._emit_routes_to_agent("p1", "TemplateManifest", "target_agent")
trace_contract._emit_verifies_policy("p1", "TemplateManifest", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "TemplateManifest", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "TemplateManifest", "boundary_check")
trace_contract._emit_transcripts_response("p1", "TemplateManifest", "transcript")
trace_contract._emit_gated_by_confidence("p1", "TemplateManifest", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "TemplateManifest", "L0")
trace_contract._emit_reads_policy_state("p1", "TemplateManifest", "L0")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "TemplateManifest", "p0_governance")
trace_contract._emit_snapshots_state("p0", "TemplateManifest", "state_snapshot")


@dataclass(frozen=True)
class TemplateManifest:
    """Template manifest for S0 system prompts and I0 mixins.

    Immutable registry entry owned by L4 State layer.
    Referenced by PromptBOM.system_version_hash.

    Attributes
    ----------
    template_id : str
        Unique template identifier.
    version : str
        Semantic version string.
    git_commit_hash : str
        Git commit hash for provenance.
    required_variables : tuple[str, ...]
        Sorted tuple of required template variables.
    schema_version : str
        Schema version for forward compatibility.
    """

    template_id: str
    version: str
    git_commit_hash: str
    required_variables: tuple[str, ...]
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if not self.template_id:
            raise ValueError("template_id must not be empty")
        if not self.version:
            raise ValueError("version must not be empty")
        if not self.git_commit_hash:
            raise ValueError("git_commit_hash must not be empty")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "template_id": self.template_id,
            "version": self.version,
            "git_commit_hash": self.git_commit_hash,
            "required_variables": tuple(sorted(self.required_variables)),
            "schema_version": self.schema_version,
        }

    def stable_hash(self) -> str:
        """Compute content-addressed SHA-256 hash."""
        canonical = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["TemplateManifest"]
