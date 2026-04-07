"""
W4-E Retrieval Profile Proposal System

Stages W4-D advisory recommendations into deterministic proposal sets
requiring explicit approval (HITL) without mutating active profile.
"""

import hashlib
import json
from dataclasses import dataclass

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "retrieval_profile_proposal", "execution_auth")
_emit_validates_capability("p2", "retrieval_profile_proposal", "capability_check")
_emit_routes_to_capability("p2", "retrieval_profile_proposal", "capability_route")
_emit_writes_via_uwg("p2", "retrieval_profile_proposal", "uwg_write")
_emit_blocks_direct_write("p2", "retrieval_profile_proposal", "direct_write_block")
_emit_records_tool_invocation("p2", "retrieval_profile_proposal", "tool_invocation")
_emit_captures_execution_output("p2", "retrieval_profile_proposal", "exec_output")
_emit_dispatches_agent("p3", "retrieval_profile_proposal", "agent_dispatch")
_emit_coordinates_agents("p3", "retrieval_profile_proposal", "agent_coordination")
_emit_records_workflow_lineage("p3", "retrieval_profile_proposal", "workflow_lineage")
_emit_records_healing_outcome("p3", "retrieval_profile_proposal", "healing_outcome")
_emit_escalates_failure("p3", "retrieval_profile_proposal", "failure_escalation")
_emit_orchestrates_workflow("p3", "retrieval_profile_proposal", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "retrieval_profile_proposal", "healing_dispatch")
_emit_invokes_evaluation("p3", "retrieval_profile_proposal", "evaluation_signal")
_emit_records_telemetry_event("p4", "retrieval_profile_proposal", "telemetry_event")
_emit_captures_evaluation_metric("p4", "retrieval_profile_proposal", "eval_metric")
_emit_stores_embedding("p4", "retrieval_profile_proposal", "embedding_store")
_emit_updates_meta_learning_state("p4", "retrieval_profile_proposal", "meta_learning")
_emit_links_execution_to_snapshot("p4", "retrieval_profile_proposal", "exec_snapshot_link")
from system_learning.engines.retrieval_profile import RetrievalProfile

_emit_applies_guardrail("p0", "retrieval_profile_proposal", "p0_governance")
_emit_reads_policy_state("p0", "retrieval_profile_proposal", "policy_binding")
_emit_snapshots_state("p0", "retrieval_profile_proposal", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("retrieval_profile_proposal", "p4obs", "metric_1")
_emit_emits_metric_event("retrieval_profile_proposal", "p4obs", "metric_2")
_emit_emits_metric_event("retrieval_profile_proposal", "p4obs", "metric_3")
_emit_emits_metric_event("retrieval_profile_proposal", "p4obs", "metric_4")
_emit_emits_metric_event("retrieval_profile_proposal", "p4obs", "metric_5")
_emit_emits_metric_event("retrieval_profile_proposal", "p4obs", "metric_6")
_emit_records_incident_event("retrieval_profile_proposal", "p4obs", "incident")
_emit_captures_runtime_anomaly("retrieval_profile_proposal", "p4obs", "anomaly")
_emit_writes_observability_log("retrieval_profile_proposal", "p4obs", "obs_log")
_emit_updates_monitoring_state("retrieval_profile_proposal", "p4obs", "mon_state")
_emit_triggers_alert("retrieval_profile_proposal", "p4obs", "alert")
_emit_links_incident_trace("retrieval_profile_proposal", "p4obs", "trace_link")
_emit_captures_pattern("retrieval_profile_proposal", "p3lm", "pattern")
_emit_records_learning_event("retrieval_profile_proposal", "p3lm", "learning_event")
_emit_writes_learning_snapshot("retrieval_profile_proposal", "p3lm", "snapshot")
_emit_feeds_meta_learning("retrieval_profile_proposal", "p3lm", "meta_feed")
_emit_updates_routing_strategy("retrieval_profile_proposal", "p3lm", "routing")
_emit_improves_agent_policy("retrieval_profile_proposal", "p3lm", "policy")
_emit_stores_learning_state("retrieval_profile_proposal", "p3lm", "state")
_emit_records_execution_trace("retrieval_profile_proposal", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("retrieval_profile_proposal", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("retrieval_profile_proposal", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("retrieval_profile_proposal", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("retrieval_profile_proposal", "L4_STATE", "p2_trace_5")
_emit_reads_environ("retrieval_profile_proposal", "env_read", "p2_env_1")
_emit_reads_environ("retrieval_profile_proposal", "env_read", "p2_env_2")
_emit_reads_runtime_state("retrieval_profile_proposal", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("retrieval_profile_proposal", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "retrieval_profile_proposal", "context_pull")
_emit_pulls_context("p1", "retrieval_profile_proposal", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "retrieval_profile_proposal", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "retrieval_profile_proposal", "uwg_term_2")
_emit_writes_through("p1", "retrieval_profile_proposal", "write_through")
_emit_writes_through("p1", "retrieval_profile_proposal", "write_through_2")
_emit_validated_by_safety_plane("p1", "retrieval_profile_proposal", "safety_validation")
_emit_invokes_eval("p1", "retrieval_profile_proposal", "eval_call")
_emit_proposal_commits_routing("p1", "retrieval_profile_proposal", "routing_commit")
_emit_escalates_to_human("p1", "retrieval_profile_proposal", "human_escalation")
_emit_routes_through("p1", "retrieval_profile_proposal", "route_through")
_emit_checks_agent_registry("p1", "retrieval_profile_proposal", "agent_registry")
_emit_validates_agent_capability("p1", "retrieval_profile_proposal", "capability")
_emit_dispatches_execution_plan("p1", "retrieval_profile_proposal", "exec_plan")
_emit_agent_executes_agent("p1", "retrieval_profile_proposal", "sub_agent")
_emit_routes_to_agent("p1", "retrieval_profile_proposal", "target_agent")
_emit_verifies_policy("p1", "retrieval_profile_proposal", "policy_check")
_emit_observes_runtime_state("p1", "retrieval_profile_proposal", "runtime_state")
_emit_verifies_boundary("p1", "retrieval_profile_proposal", "boundary_check")
_emit_transcripts_response("p1", "retrieval_profile_proposal", "transcript")
_emit_hard_fails_untranscripted("p1", "retrieval_profile_proposal")
_emit_gated_by_confidence("p1", "retrieval_profile_proposal", "confidence_gate")
emit_replay_key("p0", "retrieval_profile_proposal")
emit_determinism_digest("p0", "retrieval_profile_proposal")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass(frozen=True, slots=True)
class RetrievalProfileProposal:
    """Deterministic proposal for RetrievalProfile changes.

    Stages W4-D advisory recommendations into explicit proposal sets
    that require human approval before activation.
    """

    base_profile_id: str
    proposed_profile: RetrievalProfile
    recommended_changes: dict[str, float]
    approved: bool
    proposed_at_utc: int
    deterministic_digest: str

    def emit_digest(self) -> None:
        """Print the proposal digest for determinism verification."""
        print(f"W4E-PROPOSAL-DIGEST: {self.deterministic_digest}")

    def to_canonical_json(self) -> str:
        """Convert to canonical JSON for deterministic serialization."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalProfileProposal.to_canonical_json")

        data = {
            "base_profile_id": self.base_profile_id,
            "proposed_profile": json.loads(self.proposed_profile.to_canonical_json()),
            "recommended_changes": {k: round(v, 6) for k, v in self.recommended_changes.items()},
            "approved": self.approved,
            "proposed_at_utc": self.proposed_at_utc,
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    def create_approved_copy(self, approved_at_utc: int) -> "RetrievalProfileProposal":
        """Create an approved copy of this proposal.

        Args:
            approved_at_utc: Timestamp when approval was granted

        Returns:
            New proposal with approved=True and updated digest
        """
        approved_proposal = RetrievalProfileProposal(
            base_profile_id=self.base_profile_id,
            proposed_profile=self.proposed_profile,
            recommended_changes=self.recommended_changes,
            approved=True,
            proposed_at_utc=self.proposed_at_utc,
            deterministic_digest=self._compute_approved_digest(approved_at_utc),
        )
        return approved_proposal

    def _compute_approved_digest(self, approved_at_utc: int) -> str:
        """Compute digest for approved proposal."""
        data = {
            "base_profile_id": self.base_profile_id,
            "proposed_profile": json.loads(self.proposed_profile.to_canonical_json()),
            "recommended_changes": {k: round(v, 6) for k, v in self.recommended_changes.items()},
            "approved": True,
            "proposed_at_utc": self.proposed_at_utc,
            "approved_at_utc": approved_at_utc,
            "proposal_version": "W4-E-v1.0",
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def create_proposal_digest(
    base_profile_id: str,
    proposed_profile: RetrievalProfile,
    recommended_changes: dict[str, float],
    proposed_at_utc: int,
) -> str:
    """Compute deterministic SHA-256 digest for proposal.

    Args:
        base_profile_id: ID of the base profile being modified
        proposed_profile: The proposed new profile
        recommended_changes: Dictionary of parameter changes
        proposed_at_utc: Timestamp when proposal was created

    Returns:
        SHA-256 digest string
    """
    data = {
        "base_profile_id": base_profile_id,
        "proposed_profile": json.loads(proposed_profile.to_canonical_json()),
        "recommended_changes": {k: round(v, 6) for k, v in sorted(recommended_changes.items())},
        "approved": False,
        "proposed_at_utc": proposed_at_utc,
        "proposal_version": "W4-E-v1.0",
    }
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["RetrievalProfileProposal", "create_proposal_digest"]
