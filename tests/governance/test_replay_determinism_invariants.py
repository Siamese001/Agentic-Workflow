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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
