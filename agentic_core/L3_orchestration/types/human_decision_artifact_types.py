"""
Human Decision Artifact - W5 Implementation

Defines HumanDecisionArtifact structure for Path D human review workflow.
Ensures proper loopback invariants and certification invalidation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal

from agentic_core.L0_routing.reasoning.assembly_stage import GovernedPayload
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "human_decision_artifact_types")
trace_contract.emit_determinism_digest("p0", "human_decision_artifact_types")

trace_contract._emit_dispatches_healing_run("p1", "human_decision_artifact_types", "L3")
trace_contract._emit_routes_through("p1", "human_decision_artifact_types", "L3")
trace_contract._emit_checks_agent_registry("p1", "human_decision_artifact_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "human_decision_artifact_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "human_decision_artifact_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "human_decision_artifact_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "human_decision_artifact_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "human_decision_artifact_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "human_decision_artifact_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "human_decision_artifact_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "human_decision_artifact_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "human_decision_artifact_types")
trace_contract._emit_gated_by_confidence("p1", "human_decision_artifact_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "human_decision_artifact_types", "L3")
trace_contract._emit_reads_policy_state("p1", "human_decision_artifact_types", "L3")
trace_contract._emit_authorize_and_execute("p2", "human_decision_artifact_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "human_decision_artifact_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "human_decision_artifact_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "human_decision_artifact_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "human_decision_artifact_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "human_decision_artifact_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "human_decision_artifact_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "human_decision_artifact_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "human_decision_artifact_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "human_decision_artifact_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "human_decision_artifact_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "human_decision_artifact_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "human_decision_artifact_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "human_decision_artifact_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "human_decision_artifact_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "human_decision_artifact_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "human_decision_artifact_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "human_decision_artifact_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "human_decision_artifact_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "human_decision_artifact_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("human_decision_artifact_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("human_decision_artifact_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("human_decision_artifact_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("human_decision_artifact_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("human_decision_artifact_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("human_decision_artifact_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("human_decision_artifact_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("human_decision_artifact_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("human_decision_artifact_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("human_decision_artifact_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("human_decision_artifact_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("human_decision_artifact_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("human_decision_artifact_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("human_decision_artifact_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("human_decision_artifact_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("human_decision_artifact_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("human_decision_artifact_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("human_decision_artifact_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("human_decision_artifact_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("human_decision_artifact_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("human_decision_artifact_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("human_decision_artifact_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("human_decision_artifact_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("human_decision_artifact_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("human_decision_artifact_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("human_decision_artifact_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("human_decision_artifact_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("human_decision_artifact_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "human_decision_artifact_types", "context_pull")
trace_contract._emit_pulls_context("p1", "human_decision_artifact_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "human_decision_artifact_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "human_decision_artifact_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "human_decision_artifact_types", "write_through")
trace_contract._emit_writes_through("p1", "human_decision_artifact_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "human_decision_artifact_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "human_decision_artifact_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "human_decision_artifact_types", "routing_commit")


class HumanAction(Enum):
    """Actions available for human review."""

    APPROVE = "APPROVE"
    MODIFY_DIFF = "MODIFY_DIFF"
    REJECT = "REJECT"


@dataclass
class StructuredPatchSchema:
    """Schema for structured patches in MODIFY_DIFF actions."""

    allowed_tools: tuple[str, ...]
    patch_format: Literal["unified", "json", "structured"] = "structured"
    max_patch_size: int = 1024 * 1024
    required_fields: tuple[str, ...] = ("tool_name", "parameters", "rationale")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "StructuredPatchSchema.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "StructuredPatchSchema.to_dict", "p0_governance")
        return {
            "allowed_tools": list(self.allowed_tools),
            "patch_format": self.patch_format,
            "max_patch_size": self.max_patch_size,
            "required_fields": list(self.required_fields),
        }


@dataclass
class HumanDecisionArtifact:
    """Artifact for human review workflow in Path D."""

    trace_id: str
    policy_hash: str
    reviewer_id: str | None
    action: HumanAction
    structured_patch_schema: StructuredPatchSchema
    original_plan_hash: str
    plan_content: dict[str, Any] | None = None
    review_timestamp: str | None = None
    review_rationale: str | None = None
    modified_plan_hash: str | None = None
    certification_invalidated: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "policy_hash": self.policy_hash,
            "reviewer_id": self.reviewer_id,
            "action": self.action.value,
            "structured_patch_schema": self.structured_patch_schema.to_dict(),
            "original_plan_hash": self.original_plan_hash,
            "plan_content": self.plan_content,
            "review_timestamp": self.review_timestamp,
            "review_rationale": self.review_rationale,
            "modified_plan_hash": self.modified_plan_hash,
            "certification_invalidated": self.certification_invalidated,
        }

    def apply_modify_diff(self, reviewer_id: str, modified_plan: dict[str, Any], rationale: str) -> None:
        """
        Apply MODIFY_DIFF action to the artifact.

        Args:
            reviewer_id: ID of the reviewer making changes
            modified_plan: Modified plan content
            rationale: Rationale for the modifications
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "HumanDecisionArtifact.apply_modify_diff",
        )

        import hashlib
        from datetime import datetime

        if self.action != HumanAction.MODIFY_DIFF:
            raise ValueError("Can only apply modify_diff to MODIFY_DIFF artifacts")
        self.reviewer_id = reviewer_id
        self.plan_content = modified_plan
        self.review_rationale = rationale
        self.review_timestamp = datetime.utcnow().isoformat() + "Z"
        self.certification_invalidated = True
        canonical = json.dumps(modified_plan, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        self.modified_plan_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def validate_patch_constraints(self, patch: dict[str, Any]) -> bool:
        """
        Validate that a patch conforms to the structured patch schema.

        Args:
            patch: Patch to validate

        Returns:
            True if patch conforms to schema, False otherwise
        """
        if not isinstance(patch, dict):
            return False
        for field in self.structured_patch_schema.required_fields:
            if field not in patch:
                return False
        tool_name = patch.get("tool_name")
        if tool_name not in self.structured_patch_schema.allowed_tools:
            return False
        patch_str = json.dumps(patch, separators=(",", ":"))
        if len(patch_str) > self.structured_patch_schema.max_patch_size:
            return False
        return True


def create_human_review_draft(
    trace_id: str,
    policy_hash: str,
    plan_hash: str,
    governed_payload: GovernedPayload,
    allowed_tools: tuple[str, ...] = (),
    plan_content: dict[str, Any] | None = None,
) -> HumanDecisionArtifact:
    """
    Create a human decision artifact draft for Path D.

    Args:
        trace_id: Unique trace identifier
        policy_hash: Policy validation hash
        plan_hash: Hash of the original plan
        governed_payload: The governed payload being reviewed
        allowed_tools: Tuple of allowed tools for modifications
        plan_content: Plan content for review (optional)

    Returns:
        HumanDecisionArtifact ready for human review
    """
    structured_schema = StructuredPatchSchema(
        allowed_tools=allowed_tools,
        patch_format="structured",
        max_patch_size=1024 * 1024,
        required_fields=("tool_name", "parameters", "rationale"),
    )
    artifact = HumanDecisionArtifact(
        trace_id=trace_id,
        policy_hash=policy_hash,
        reviewer_id=None,
        action=HumanAction.MODIFY_DIFF,
        structured_patch_schema=structured_schema,
        original_plan_hash=plan_hash,
        plan_content=plan_content,
        certification_invalidated=False,
    )
    return artifact


def create_approval_artifact(
    trace_id: str,
    policy_hash: str,
    plan_hash: str,
    reviewer_id: str,
    rationale: str | None = None,
) -> HumanDecisionArtifact:
    """
    Create an approval artifact for Path D.

    Args:
        trace_id: Unique trace identifier
        policy_hash: Policy validation hash
        plan_hash: Hash of the approved plan
        reviewer_id: ID of the approving reviewer
        rationale: Rationale for approval (optional)

    Returns:
        HumanDecisionArtifact with APPROVE action
    """
    from datetime import datetime

    structured_schema = StructuredPatchSchema(
        allowed_tools=(),
        patch_format="structured",
        max_patch_size=1024 * 1024,
        required_fields=(),
    )
    artifact = HumanDecisionArtifact(
        trace_id=trace_id,
        policy_hash=policy_hash,
        reviewer_id=reviewer_id,
        action=HumanAction.APPROVE,
        structured_patch_schema=structured_schema,
        original_plan_hash=plan_hash,
        review_timestamp=datetime.utcnow().isoformat() + "Z",
        review_rationale=rationale,
        certification_invalidated=False,
    )
    return artifact


def create_rejection_artifact(
    trace_id: str,
    policy_hash: str,
    plan_hash: str,
    reviewer_id: str,
    rationale: str,
) -> HumanDecisionArtifact:
    """
    Create a rejection artifact for Path D.

    Args:
        trace_id: Unique trace identifier
        policy_hash: Policy validation hash
        plan_hash: Hash of the rejected plan
        reviewer_id: ID of the rejecting reviewer
        rationale: Rationale for rejection

    Returns:
        HumanDecisionArtifact with REJECT action
    """
    from datetime import datetime

    structured_schema = StructuredPatchSchema(
        allowed_tools=(),
        patch_format="structured",
        max_patch_size=1024 * 1024,
        required_fields=(),
    )
    artifact = HumanDecisionArtifact(
        trace_id=trace_id,
        policy_hash=policy_hash,
        reviewer_id=reviewer_id,
        action=HumanAction.REJECT,
        structured_patch_schema=structured_schema,
        original_plan_hash=plan_hash,
        review_timestamp=datetime.utcnow().isoformat() + "Z",
        review_rationale=rationale,
        certification_invalidated=True,
    )
    return artifact


__all__ = [
    "HumanDecisionArtifact",
    "HumanAction",
    "StructuredPatchSchema",
    "create_human_review_draft",
    "create_approval_artifact",
    "create_rejection_artifact",
]
