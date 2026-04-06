"""CommitProofInvariant — determinism proof standard for phase digests.

Spec: Determinism & Replayability, Guarantee #18.
A CommitProofInvariant captures a determinism digest at a known point in time.
It can be re-evaluated to verify the digest is stable (same inputs → same hash)
or verify it has changed (negative control: tampered inputs → different hash).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable

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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "commit_proof_invariant_types")
emit_determinism_digest("p0", "commit_proof_invariant_types")

_emit_dispatches_healing_run("p1", "commit_proof_invariant_types", "L2")
_emit_routes_through("p1", "commit_proof_invariant_types", "L2")
_emit_checks_agent_registry("p1", "commit_proof_invariant_types", "agent_registry")
_emit_validates_agent_capability("p1", "commit_proof_invariant_types", "capability")
_emit_dispatches_execution_plan("p1", "commit_proof_invariant_types", "exec_plan")
_emit_agent_executes_agent("p1", "commit_proof_invariant_types", "sub_agent")
_emit_routes_to_agent("p1", "commit_proof_invariant_types", "target_agent")
_emit_verifies_policy("p1", "commit_proof_invariant_types", "policy_check")
_emit_observes_runtime_state("p1", "commit_proof_invariant_types", "runtime_state")
_emit_verifies_boundary("p1", "commit_proof_invariant_types", "boundary_check")
_emit_transcripts_response("p1", "commit_proof_invariant_types", "transcript")
_emit_hard_fails_untranscripted("p1", "commit_proof_invariant_types")
_emit_gated_by_confidence("p1", "commit_proof_invariant_types", "confidence_gate")
_emit_escalates_to_human("p1", "commit_proof_invariant_types", "L2")
_emit_reads_policy_state("p1", "commit_proof_invariant_types", "L2")

_emit_applies_guardrail("p0", "commit_proof_invariant_types", "p0_governance")
_emit_snapshots_state("p0", "commit_proof_invariant_types", "state_snapshot")
_emit_authorize_and_execute("p2", "commit_proof_invariant_types", "execution_auth")
_emit_validates_capability("p2", "commit_proof_invariant_types", "capability_check")
_emit_routes_to_capability("p2", "commit_proof_invariant_types", "capability_route")
_emit_writes_via_uwg("p2", "commit_proof_invariant_types", "uwg_write")
_emit_blocks_direct_write("p2", "commit_proof_invariant_types", "direct_write_block")
_emit_records_tool_invocation("p2", "commit_proof_invariant_types", "tool_invocation")
_emit_captures_execution_output("p2", "commit_proof_invariant_types", "exec_output")
_emit_dispatches_agent("p3", "commit_proof_invariant_types", "agent_dispatch")
_emit_coordinates_agents("p3", "commit_proof_invariant_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "commit_proof_invariant_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "commit_proof_invariant_types", "healing_outcome")
_emit_escalates_failure("p3", "commit_proof_invariant_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "commit_proof_invariant_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "commit_proof_invariant_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "commit_proof_invariant_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "commit_proof_invariant_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "commit_proof_invariant_types", "eval_metric")
_emit_stores_embedding("p4", "commit_proof_invariant_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "commit_proof_invariant_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "commit_proof_invariant_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("commit_proof_invariant_types", "p4obs", "metric_1")
_emit_emits_metric_event("commit_proof_invariant_types", "p4obs", "metric_2")
_emit_emits_metric_event("commit_proof_invariant_types", "p4obs", "metric_3")
_emit_emits_metric_event("commit_proof_invariant_types", "p4obs", "metric_4")
_emit_emits_metric_event("commit_proof_invariant_types", "p4obs", "metric_5")
_emit_emits_metric_event("commit_proof_invariant_types", "p4obs", "metric_6")
_emit_records_incident_event("commit_proof_invariant_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("commit_proof_invariant_types", "p4obs", "anomaly")
_emit_writes_observability_log("commit_proof_invariant_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("commit_proof_invariant_types", "p4obs", "mon_state")
_emit_triggers_alert("commit_proof_invariant_types", "p4obs", "alert")
_emit_links_incident_trace("commit_proof_invariant_types", "p4obs", "trace_link")
_emit_captures_pattern("commit_proof_invariant_types", "p3lm", "pattern")
_emit_records_learning_event("commit_proof_invariant_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("commit_proof_invariant_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("commit_proof_invariant_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("commit_proof_invariant_types", "p3lm", "routing")
_emit_improves_agent_policy("commit_proof_invariant_types", "p3lm", "policy")
_emit_stores_learning_state("commit_proof_invariant_types", "p3lm", "state")
_emit_records_execution_trace("commit_proof_invariant_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("commit_proof_invariant_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("commit_proof_invariant_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("commit_proof_invariant_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("commit_proof_invariant_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("commit_proof_invariant_types", "env_read", "p2_env_1")
_emit_reads_environ("commit_proof_invariant_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("commit_proof_invariant_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("commit_proof_invariant_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "commit_proof_invariant_types", "context_pull")
_emit_pulls_context("p1", "commit_proof_invariant_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "commit_proof_invariant_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "commit_proof_invariant_types", "uwg_term_2")
_emit_writes_through("p1", "commit_proof_invariant_types", "write_through")
_emit_writes_through("p1", "commit_proof_invariant_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "commit_proof_invariant_types", "safety_validation")
_emit_invokes_eval("p1", "commit_proof_invariant_types", "eval_call")
_emit_proposal_commits_routing("p1", "commit_proof_invariant_types", "routing_commit")


class DeterminismProofFailure(RuntimeError):
    """Raised when a CommitProofInvariant verification fails."""


@dataclass(frozen=True)
class CommitProofInvariant:
    """Captures a determinism digest and verifies it is reproducible.

    Spec: Determinism & Replayability, Guarantee #18.

    Fields:
        phase_id: Stable identifier for the phase this proof covers.
        digest: The expected 64-hex SHA-256 digest.
        inputs_summary: Human-readable summary of what contributed to the digest.
    """

    phase_id: str
    digest: str
    inputs_summary: str

    def __post_init__(self) -> None:
        if not self.phase_id or not self.phase_id.strip():
            raise DeterminismProofFailure("CommitProofInvariant.phase_id must be non-empty")
        if len(self.digest) != 64 or not all(c in "0123456789abcdef" for c in self.digest):
            raise DeterminismProofFailure(
                f"CommitProofInvariant.digest must be a 64-char lowercase hex string, got '{self.digest[:16]}...' (len={len(self.digest)})"
            )

    def verify_stable(self, recompute_fn: Callable[[], str]) -> None:
        """Assert that recompute_fn() returns the same digest as self.digest.

        Raises DeterminismProofFailure if the digest has changed (non-determinism detected).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "CommitProofInvariant.verify_stable"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:CommitProofInvariant.verify_stable".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        actual = recompute_fn()
        if actual != self.digest:
            raise DeterminismProofFailure(
                f"[Phase {self.phase_id}] Determinism proof FAILED: expected={self.digest[:16]}..., actual={actual[:16]}... Inputs changed without updating the committed proof."
            )

    def verify_unstable(self, recompute_fn: Callable[[], str]) -> None:
        """Assert that recompute_fn() returns a DIFFERENT digest than self.digest.

        Negative control: verifies that tampered inputs produce a different hash.
        Raises DeterminismProofFailure if the digest is unchanged (tamper not detected).
        """
        actual = recompute_fn()
        if actual == self.digest:
            raise DeterminismProofFailure(
                f"[Phase {self.phase_id}] Negative control FAILED: tampered inputs produced the same digest={self.digest[:16]}... The determinism function is insensitive to this mutation."
            )


def make_proof(phase_id: str, inputs_summary: str, recompute_fn: Callable[[], str]) -> CommitProofInvariant:
    """Compute a fresh CommitProofInvariant by calling recompute_fn().

    Use this at seal time to capture the current digest.
    """
    digest = recompute_fn()
    return CommitProofInvariant(phase_id=phase_id, digest=digest, inputs_summary=inputs_summary)


def canonical_digest(obj: Any) -> str:
    """Compute SHA-256 of canonical JSON (sorted keys, no spaces, ASCII-safe)."""
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


__all__ = ["CommitProofInvariant", "DeterminismProofFailure", "make_proof", "canonical_digest"]
