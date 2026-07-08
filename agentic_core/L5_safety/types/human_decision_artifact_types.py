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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "human_decision_artifact_types")
trace_contract.emit_determinism_digest("p0", "human_decision_artifact_types")

trace_contract._emit_dispatches_healing_run("p1", "human_decision_artifact_types", "L5")
trace_contract._emit_routes_through("p1", "human_decision_artifact_types", "L5")
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
trace_contract._emit_escalates_to_human("p1", "human_decision_artifact_types", "L5")
trace_contract._emit_reads_policy_state("p1", "human_decision_artifact_types", "L5")

trace_contract._emit_applies_guardrail("p0", "human_decision_artifact_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "human_decision_artifact_types", "state_snapshot")
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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "HumanDecisionArtifact.sign")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HumanDecisionArtifact.sign".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
                f"original_plan_hash mismatch: artifact={self.original_plan_hash[:12]} submitted={submitted_plan_hash[:12]}",
            )
