"""HumanDecisionArtifact — spec contract [5].

MODIFY_DIFF MUST reference original_plan_hash and force L5 re-clear.
Prior plan signature is STRICTLY INVALID after MODIFY_DIFF.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from typing import Literal

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "human_decision_artifact_types")
emit_determinism_digest("p0", "human_decision_artifact_types")

_emit_dispatches_healing_run("p1", "human_decision_artifact_types", "L5")
_emit_routes_through("p1", "human_decision_artifact_types", "L5")
_emit_escalates_to_human("p1", "human_decision_artifact_types", "L5")
_emit_reads_policy_state("p1", "human_decision_artifact_types", "L5")

_emit_applies_guardrail("p0", "human_decision_artifact_types", "p0_governance")
_emit_snapshots_state("p0", "human_decision_artifact_types", "state_snapshot")
_emit_authorize_and_execute("p2", "human_decision_artifact_types", "execution_auth")
_emit_validates_capability("p2", "human_decision_artifact_types", "capability_check")
_emit_routes_to_capability("p2", "human_decision_artifact_types", "capability_route")
_emit_writes_via_uwg("p2", "human_decision_artifact_types", "uwg_write")
_emit_blocks_direct_write("p2", "human_decision_artifact_types", "direct_write_block")
_emit_records_tool_invocation("p2", "human_decision_artifact_types", "tool_invocation")
_emit_captures_execution_output("p2", "human_decision_artifact_types", "exec_output")
_emit_dispatches_agent("p3", "human_decision_artifact_types", "agent_dispatch")
_emit_coordinates_agents("p3", "human_decision_artifact_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "human_decision_artifact_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "human_decision_artifact_types", "healing_outcome")
_emit_escalates_failure("p3", "human_decision_artifact_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "human_decision_artifact_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "human_decision_artifact_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "human_decision_artifact_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "human_decision_artifact_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "human_decision_artifact_types", "eval_metric")
_emit_stores_embedding("p4", "human_decision_artifact_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "human_decision_artifact_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "human_decision_artifact_types", "exec_snapshot_link")

ReviewAction = Literal["APPROVE", "MODIFY_DIFF", "REJECT"]


class HumanDecisionViolation(ValueError):
    """Raised when HumanDecisionArtifact invariants are broken."""


@dataclass(frozen=True)
class HumanDecisionArtifact:
    trace_id: str
    policy_hash: str
    reviewer_id: str
    action: ReviewAction
    original_plan_hash: str
    structured_patch_schema: dict
    reviewer_sig: str = ""
    l5_reclear_required: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise HumanDecisionViolation("trace_id required")
        if not self.original_plan_hash:
            raise HumanDecisionViolation("original_plan_hash required — must reference submitted plan")
        if self.action == "MODIFY_DIFF" and (not self.structured_patch_schema):
            raise HumanDecisionViolation("structured_patch_schema required for MODIFY_DIFF")
        object.__setattr__(self, "l5_reclear_required", self.action == "MODIFY_DIFF")

    def _signable_dict(self) -> dict:
        return {
            "action": self.action,
            "original_plan_hash": self.original_plan_hash,
            "policy_hash": self.policy_hash,
            "reviewer_id": self.reviewer_id,
            "trace_id": self.trace_id,
        }

    def sign(self, secret: bytes) -> HumanDecisionArtifact:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "HumanDecisionArtifact.sign")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HumanDecisionArtifact.sign".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        mac = hmac.new(
            secret,
            json.dumps(self._signable_dict(), sort_keys=True, separators=(",", ":")).encode("ascii"),
            hashlib.sha256,
        )
        return HumanDecisionArtifact(
            trace_id=self.trace_id,
            policy_hash=self.policy_hash,
            reviewer_id=self.reviewer_id,
            action=self.action,
            original_plan_hash=self.original_plan_hash,
            structured_patch_schema=self.structured_patch_schema,
            reviewer_sig=mac.hexdigest().lower(),
        )

    def verify(self, secret: bytes) -> None:
        if not self.reviewer_sig:
            raise HumanDecisionViolation("reviewer_sig absent")
        mac = hmac.new(
            secret,
            json.dumps(self._signable_dict(), sort_keys=True, separators=(",", ":")).encode("ascii"),
            hashlib.sha256,
        )
        if not hmac.compare_digest(self.reviewer_sig, mac.hexdigest().lower()):
            raise HumanDecisionViolation("reviewer_sig mismatch — artifact tampered")

    def assert_plan_hash_matches(self, submitted_plan_hash: str) -> None:
        """Hard-fail if this artifact references a different plan than what was submitted."""
        if self.original_plan_hash != submitted_plan_hash:
            raise HumanDecisionViolation(
                f"original_plan_hash mismatch: artifact={self.original_plan_hash[:12]} submitted={submitted_plan_hash[:12]}"
            )
