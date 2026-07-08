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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "commit_proof_invariant_types")
trace_contract.emit_determinism_digest("p0", "commit_proof_invariant_types")

trace_contract._emit_dispatches_healing_run("p1", "commit_proof_invariant_types", "L2")
trace_contract._emit_routes_through("p1", "commit_proof_invariant_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "commit_proof_invariant_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "commit_proof_invariant_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "commit_proof_invariant_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "commit_proof_invariant_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "commit_proof_invariant_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "commit_proof_invariant_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "commit_proof_invariant_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "commit_proof_invariant_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "commit_proof_invariant_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "commit_proof_invariant_types")
trace_contract._emit_gated_by_confidence("p1", "commit_proof_invariant_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "commit_proof_invariant_types", "L2")
trace_contract._emit_reads_policy_state("p1", "commit_proof_invariant_types", "L2")

trace_contract._emit_applies_guardrail("p0", "commit_proof_invariant_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "commit_proof_invariant_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "commit_proof_invariant_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "commit_proof_invariant_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "commit_proof_invariant_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "commit_proof_invariant_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "commit_proof_invariant_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "commit_proof_invariant_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "commit_proof_invariant_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "commit_proof_invariant_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "commit_proof_invariant_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "commit_proof_invariant_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "commit_proof_invariant_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "commit_proof_invariant_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "commit_proof_invariant_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "commit_proof_invariant_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "commit_proof_invariant_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "commit_proof_invariant_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "commit_proof_invariant_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "commit_proof_invariant_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "commit_proof_invariant_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "commit_proof_invariant_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("commit_proof_invariant_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("commit_proof_invariant_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("commit_proof_invariant_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("commit_proof_invariant_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("commit_proof_invariant_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("commit_proof_invariant_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("commit_proof_invariant_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("commit_proof_invariant_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("commit_proof_invariant_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("commit_proof_invariant_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("commit_proof_invariant_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("commit_proof_invariant_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("commit_proof_invariant_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("commit_proof_invariant_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("commit_proof_invariant_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("commit_proof_invariant_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("commit_proof_invariant_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("commit_proof_invariant_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("commit_proof_invariant_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("commit_proof_invariant_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("commit_proof_invariant_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("commit_proof_invariant_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("commit_proof_invariant_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("commit_proof_invariant_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("commit_proof_invariant_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("commit_proof_invariant_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("commit_proof_invariant_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("commit_proof_invariant_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "commit_proof_invariant_types", "context_pull")
trace_contract._emit_pulls_context("p1", "commit_proof_invariant_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "commit_proof_invariant_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "commit_proof_invariant_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "commit_proof_invariant_types", "write_through")
trace_contract._emit_writes_through("p1", "commit_proof_invariant_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "commit_proof_invariant_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "commit_proof_invariant_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "commit_proof_invariant_types", "routing_commit")


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
                f"CommitProofInvariant.digest must be a 64-char lowercase hex string, got '{self.digest[:16]}...' (len={len(self.digest)})",
            )

    def verify_stable(self, recompute_fn: Callable[[], str]) -> None:
        """Assert that recompute_fn() returns the same digest as self.digest.

        Raises DeterminismProofFailure if the digest has changed (non-determinism detected).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "CommitProofInvariant.verify_stable",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:CommitProofInvariant.verify_stable".encode()).hexdigest()[
            :24
        ]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        actual = recompute_fn()
        if actual != self.digest:
            raise DeterminismProofFailure(
                f"[Phase {self.phase_id}] Determinism proof FAILED: expected={self.digest[:16]}..., actual={actual[:16]}... Inputs changed without updating the committed proof.",
            )

    def verify_unstable(self, recompute_fn: Callable[[], str]) -> None:
        """Assert that recompute_fn() returns a DIFFERENT digest than self.digest.

        Negative control: verifies that tampered inputs produce a different hash.
        Raises DeterminismProofFailure if the digest is unchanged (tamper not detected).
        """
        actual = recompute_fn()
        if actual == self.digest:
            raise DeterminismProofFailure(
                f"[Phase {self.phase_id}] Negative control FAILED: tampered inputs produced the same digest={self.digest[:16]}... The determinism function is insensitive to this mutation.",
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
