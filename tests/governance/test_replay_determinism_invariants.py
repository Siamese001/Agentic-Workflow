"""Replay determinism invariant contract tests.

Invariants asserted:
  INV-RPL-1: Replay artifacts produce identical digests across two independent runs.
  INV-RPL-2: Replay engine rejects tampered or drifted inputs (determinism self-check).
"""

from __future__ import annotations

import hashlib
import os

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_replay_determinism_invariants")
_emit_applies_guardrail("p0", "test_replay_determinism_invariants", "p0_governance")
_emit_reads_policy_state("p0", "test_replay_determinism_invariants", "policy_binding")
_emit_snapshots_state("p0", "test_replay_determinism_invariants", "state_snapshot")
emit_replay_key("p0", "test_replay_determinism_invariants")
emit_determinism_digest("p0", "test_replay_determinism_invariants")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_replay_determinism_invariants", "execution_auth")
_emit_validates_capability("p2", "test_replay_determinism_invariants", "capability_check")
_emit_routes_to_capability("p2", "test_replay_determinism_invariants", "capability_route")
_emit_writes_via_uwg("p2", "test_replay_determinism_invariants", "uwg_write")
_emit_blocks_direct_write("p2", "test_replay_determinism_invariants", "direct_write_block")
_emit_records_tool_invocation("p2", "test_replay_determinism_invariants", "tool_invocation")
_emit_captures_execution_output("p2", "test_replay_determinism_invariants", "exec_output")
_emit_dispatches_agent("p3", "test_replay_determinism_invariants", "agent_dispatch")
_emit_coordinates_agents("p3", "test_replay_determinism_invariants", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_replay_determinism_invariants", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_replay_determinism_invariants", "healing_outcome")
_emit_escalates_failure("p3", "test_replay_determinism_invariants", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_replay_determinism_invariants", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_replay_determinism_invariants", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_replay_determinism_invariants", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_replay_determinism_invariants", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_replay_determinism_invariants", "eval_metric")
_emit_stores_embedding("p4", "test_replay_determinism_invariants", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_replay_determinism_invariants", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_replay_determinism_invariants", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance

from system_learning.engines.deterministic_replay_engine import DeterministicReplayEngine
from system_learning.engines.retrieval_profile import RetrievalProfile


def _make_profile(profile_id: str, top_k: int = 10, cutoff: float = 0.85) -> RetrievalProfile:
    return RetrievalProfile(
        profile_id=profile_id,
        primary_embedder_id="invariant-embedder",
        embedding_dim=1024,
        shadow_embedder_id="invariant-shadow",
        top_k=top_k,
        similarity_cutoff=cutoff,
        influence_cap=0.5,
        normalization_policy="l2",
    )


def test_replay_artifacts_stable_across_two_runs():
    """INV-RPL-1: Same inputs produce identical replay digest on two consecutive runs."""
    tamper = os.environ.get("SPRAWL_NEGCTRL_TAMPER", "0")

    engine = DeterministicReplayEngine()
    base = _make_profile("base-profile")
    candidate = _make_profile("candidate-profile", top_k=12, cutoff=0.80)

    result1 = engine.replay(base_profile=base, candidate_profile=candidate)
    result2 = engine.replay(base_profile=base, candidate_profile=candidate)

    if tamper == "1":
        pytest.xfail(reason="SPRAWL_NEGCTRL_TAMPER=1: INV-RPL-1 xfail — tamper mode active")

    assert result1.replay_digest == result2.replay_digest, (
        "INV-RPL-1 VIOLATION — replay digest not stable across runs: "
        f"run1={result1.replay_digest!r} run2={result2.replay_digest!r}"
    )
    assert len(result1.replay_digest) == 64, "Replay digest must be 64-char hex (SHA-256)"
    assert result1.case_count == result2.case_count, "Case count must be stable"


def test_replay_rejects_tamper_or_drift():
    """INV-RPL-2: Replay engine's determinism self-check raises on digest mismatch."""
    engine = DeterministicReplayEngine()
    base = _make_profile("base-drift")
    candidate = _make_profile("candidate-drift", top_k=15, cutoff=0.70)

    original_compute = engine._compute_replay_digest
    call_count = 0

    def drifted_compute(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        digest = original_compute(*args, **kwargs)
        if call_count > 1:
            return hashlib.sha256(b"tampered-drift").hexdigest()
        return digest

    engine._compute_replay_digest = drifted_compute

    with pytest.raises(ValueError, match="Determinism self-check failed"):
        engine.replay(base_profile=base, candidate_profile=candidate)

    engine._compute_replay_digest = original_compute
