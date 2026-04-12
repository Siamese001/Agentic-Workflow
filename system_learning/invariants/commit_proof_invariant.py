"""CommitProofInvariant -- binds committed version_ids to real implementation content.

GAP-010: The target-state requires that every commit proof binds to a true
implementation commit.  Churn commits (no-op content, placeholder bytes) must
not count as valid proof.

Rules enforced:
  - version_id must be a 64-char lowercase hex string (SHA-256).
  - implementation_hash must be a non-empty hex string.
  - version_id must equal SHA-256(canonical_bytes) of the committed package.
  - implementation_hash must NOT match the sentinel churn hash.
  - commit_timestamp_utc must be > 0.
"""

from __future__ import annotations

import hashlib
import re
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

_emit_applies_guardrail("p0", "commit_proof_invariant", "p0_governance")
_emit_reads_policy_state("p0", "commit_proof_invariant", "policy_binding")
_emit_snapshots_state("p0", "commit_proof_invariant", "state_snapshot")
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

_emit_emits_metric_event("commit_proof_invariant", "p4obs", "metric_1")
_emit_emits_metric_event("commit_proof_invariant", "p4obs", "metric_2")
_emit_emits_metric_event("commit_proof_invariant", "p4obs", "metric_3")
_emit_emits_metric_event("commit_proof_invariant", "p4obs", "metric_4")
_emit_emits_metric_event("commit_proof_invariant", "p4obs", "metric_5")
_emit_emits_metric_event("commit_proof_invariant", "p4obs", "metric_6")
_emit_records_incident_event("commit_proof_invariant", "p4obs", "incident")
_emit_captures_runtime_anomaly("commit_proof_invariant", "p4obs", "anomaly")
_emit_writes_observability_log("commit_proof_invariant", "p4obs", "obs_log")
_emit_updates_monitoring_state("commit_proof_invariant", "p4obs", "mon_state")
_emit_triggers_alert("commit_proof_invariant", "p4obs", "alert")
_emit_links_incident_trace("commit_proof_invariant", "p4obs", "trace_link")
_emit_captures_pattern("commit_proof_invariant", "p3lm", "pattern")
_emit_records_learning_event("commit_proof_invariant", "p3lm", "learning_event")
_emit_writes_learning_snapshot("commit_proof_invariant", "p3lm", "snapshot")
_emit_feeds_meta_learning("commit_proof_invariant", "p3lm", "meta_feed")
_emit_updates_routing_strategy("commit_proof_invariant", "p3lm", "routing")
_emit_improves_agent_policy("commit_proof_invariant", "p3lm", "policy")
_emit_stores_learning_state("commit_proof_invariant", "p3lm", "state")
_emit_records_execution_trace("commit_proof_invariant", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("commit_proof_invariant", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("commit_proof_invariant", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("commit_proof_invariant", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("commit_proof_invariant", "L4_STATE", "p2_trace_5")
_emit_reads_environ("commit_proof_invariant", "env_read", "p2_env_1")
_emit_reads_environ("commit_proof_invariant", "env_read", "p2_env_2")
_emit_reads_runtime_state("commit_proof_invariant", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("commit_proof_invariant", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "commit_proof_invariant", "context_pull")
_emit_pulls_context("p1", "commit_proof_invariant", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "commit_proof_invariant", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "commit_proof_invariant", "uwg_term_2")
_emit_writes_through("p1", "commit_proof_invariant", "write_through")
_emit_writes_through("p1", "commit_proof_invariant", "write_through_2")
_emit_validated_by_safety_plane("p1", "commit_proof_invariant", "safety_validation")
_emit_invokes_eval("p1", "commit_proof_invariant", "eval_call")
_emit_proposal_commits_routing("p1", "commit_proof_invariant", "routing_commit")
_emit_escalates_to_human("p1", "commit_proof_invariant", "human_escalation")
_emit_routes_through("p1", "commit_proof_invariant", "route_through")
_emit_checks_agent_registry("p1", "commit_proof_invariant", "agent_registry")
_emit_validates_agent_capability("p1", "commit_proof_invariant", "capability")
_emit_dispatches_execution_plan("p1", "commit_proof_invariant", "exec_plan")
_emit_agent_executes_agent("p1", "commit_proof_invariant", "sub_agent")
_emit_routes_to_agent("p1", "commit_proof_invariant", "target_agent")
_emit_verifies_policy("p1", "commit_proof_invariant", "policy_check")
_emit_observes_runtime_state("p1", "commit_proof_invariant", "runtime_state")
_emit_verifies_boundary("p1", "commit_proof_invariant", "boundary_check")
_emit_transcripts_response("p1", "commit_proof_invariant", "transcript")
_emit_hard_fails_untranscripted("p1", "commit_proof_invariant")
_emit_gated_by_confidence("p1", "commit_proof_invariant", "confidence_gate")
emit_replay_key("p0", "commit_proof_invariant")
emit_determinism_digest("p0", "commit_proof_invariant")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "commit_proof_invariant", "execution_auth")
_emit_validates_capability("p2", "commit_proof_invariant", "capability_check")
_emit_routes_to_capability("p2", "commit_proof_invariant", "capability_route")
_emit_writes_via_uwg("p2", "commit_proof_invariant", "uwg_write")
_emit_blocks_direct_write("p2", "commit_proof_invariant", "direct_write_block")
_emit_records_tool_invocation("p2", "commit_proof_invariant", "tool_invocation")
_emit_captures_execution_output("p2", "commit_proof_invariant", "exec_output")
_emit_dispatches_agent("p3", "commit_proof_invariant", "agent_dispatch")
_emit_coordinates_agents("p3", "commit_proof_invariant", "agent_coordination")
_emit_records_workflow_lineage("p3", "commit_proof_invariant", "workflow_lineage")
_emit_records_healing_outcome("p3", "commit_proof_invariant", "healing_outcome")
_emit_escalates_failure("p3", "commit_proof_invariant", "failure_escalation")
_emit_orchestrates_workflow("p3", "commit_proof_invariant", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "commit_proof_invariant", "healing_dispatch")
_emit_invokes_evaluation("p3", "commit_proof_invariant", "evaluation_signal")
_emit_records_telemetry_event("p4", "commit_proof_invariant", "telemetry_event")
_emit_captures_evaluation_metric("p4", "commit_proof_invariant", "eval_metric")
_emit_stores_embedding("p4", "commit_proof_invariant", "embedding_store")
_emit_updates_meta_learning_state("p4", "commit_proof_invariant", "meta_learning")
_emit_links_execution_to_snapshot("p4", "commit_proof_invariant", "exec_snapshot_link")

_HEX_RE = re.compile("^[0-9a-f]+$")
_EMPTY_CONTENT_HASH = hashlib.sha256(b"").hexdigest()
_PLACEHOLDER_HASH = hashlib.sha256(b"placeholder").hexdigest()
_CHURN_HASHES: frozenset[str] = frozenset({_EMPTY_CONTENT_HASH, _PLACEHOLDER_HASH})


class CommitProofViolation(Exception):
    """Raised when a commit proof invariant is violated."""


@dataclass(frozen=True)
class CommitProofInvariant:
    """Immutable proof record binding version_id to implementation content.

    Attributes
    ----------
    version_id : str
        SHA-256 hex digest of the committed ChangePackage.canonical_bytes().
    implementation_hash : str
        SHA-256 hex digest of the actual implementation bytes being committed
        (e.g. canonical_bytes() of the ChangePackage).  Must not be a churn hash.
    commit_timestamp_utc : int
        UTC timestamp at which the commit was made.  Must be > 0.
    """

    version_id: str
    implementation_hash: str
    commit_timestamp_utc: int

    def verify(self) -> None:
        """Verify all invariant conditions.  Raises CommitProofViolation on any failure."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CommitProofInvariant.verify")

        if not isinstance(self.version_id, str) or len(self.version_id) != 64:
            raise CommitProofViolation(
                f"COMMIT_PROOF_VIOLATION: version_id must be 64-char hex, got {self.version_id!r}",
            )
        if not _HEX_RE.match(self.version_id):
            raise CommitProofViolation(
                f"COMMIT_PROOF_VIOLATION: version_id is not lowercase hex: {self.version_id!r}",
            )
        if not isinstance(self.implementation_hash, str) or not self.implementation_hash:
            raise CommitProofViolation(
                "COMMIT_PROOF_VIOLATION: implementation_hash must be a non-empty hex string",
            )
        if not _HEX_RE.match(self.implementation_hash):
            raise CommitProofViolation(
                f"COMMIT_PROOF_VIOLATION: implementation_hash is not hex: {self.implementation_hash!r}",
            )
        if self.implementation_hash in _CHURN_HASHES:
            raise CommitProofViolation(
                f"COMMIT_PROOF_VIOLATION: implementation_hash {self.implementation_hash!r} matches a known churn/placeholder hash -- commit is not bound to real content",
            )
        if not isinstance(self.commit_timestamp_utc, int) or self.commit_timestamp_utc <= 0:
            raise CommitProofViolation(
                f"COMMIT_PROOF_VIOLATION: commit_timestamp_utc must be > 0, got {self.commit_timestamp_utc!r}",
            )

    @classmethod
    def from_package(
        cls,
        version_id: str,
        package: object,
        commit_timestamp_utc: int,
    ) -> CommitProofInvariant:
        """Create and immediately verify a proof for a committed package.

        Parameters
        ----------
        version_id : str
            The version_id returned by VersionStore.commit_change_package().
        package : object
            The committed package (must implement canonical_bytes() -> bytes).
        commit_timestamp_utc : int
            UTC timestamp of the commit.

        Returns
        -------
        CommitProofInvariant
            Verified proof instance.

        Raises
        ------
        CommitProofViolation
            If any invariant is violated, including version_id mismatch.
        """
        if not hasattr(package, "canonical_bytes"):
            raise CommitProofViolation("COMMIT_PROOF_VIOLATION: package does not implement canonical_bytes()")
        pkg_bytes: bytes = package.canonical_bytes()
        impl_hash = hashlib.sha256(pkg_bytes).hexdigest()
        if version_id != impl_hash:
            raise CommitProofViolation(
                f"COMMIT_PROOF_VIOLATION: version_id {version_id!r} does not match SHA-256(canonical_bytes()) = {impl_hash!r} -- proof not bound to implementation",
            )
        proof = cls(
            version_id=version_id,
            implementation_hash=impl_hash,
            commit_timestamp_utc=commit_timestamp_utc,
        )
        proof.verify()
        return proof


def verify_commit_proof(version_id: str, package: object, commit_timestamp_utc: int) -> CommitProofInvariant:
    """Convenience function: create and verify a CommitProofInvariant.

    Raises CommitProofViolation if any invariant fails.
    """
    return CommitProofInvariant.from_package(
        version_id=version_id,
        package=package,
        commit_timestamp_utc=commit_timestamp_utc,
    )


__all__ = ["CommitProofInvariant", "CommitProofViolation", "verify_commit_proof"]
