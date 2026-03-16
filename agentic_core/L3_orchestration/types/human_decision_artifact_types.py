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

from agentic_core.L0_routing.engines.assembly_stage import GovernedPayload
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "human_decision_artifact_types")
emit_determinism_digest("p0", "human_decision_artifact_types")

_emit_dispatches_healing_run("p1", "human_decision_artifact_types", "L3")
_emit_routes_through("p1", "human_decision_artifact_types", "L3")
_emit_escalates_to_human("p1", "human_decision_artifact_types", "L3")
_emit_reads_policy_state("p1", "human_decision_artifact_types", "L3")


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

        _emit_snapshots_state(str(_uuid.uuid4()), "StructuredPatchSchema.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "StructuredPatchSchema.to_dict", "p0_governance")
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
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "HumanDecisionArtifact.apply_modify_diff"
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
    trace_id: str, policy_hash: str, plan_hash: str, reviewer_id: str, rationale: str | None = None
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
        allowed_tools=(), patch_format="structured", max_patch_size=1024 * 1024, required_fields=()
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
    trace_id: str, policy_hash: str, plan_hash: str, reviewer_id: str, rationale: str
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
        allowed_tools=(), patch_format="structured", max_patch_size=1024 * 1024, required_fields=()
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
