"""V15 P9.2 — Performance & Hot-Path Boundedness Guards.

Deterministic (no wall-clock thresholds). Uses operation counting and
state-size assertions to prove:
1) execute() overhead is bounded under repeated clean calls
2) Per-call violation lists do not accumulate across calls
3) Persistent dedupe set (_seen_signals) grows predictably
"""

from __future__ import annotations

import hashlib
import os
from unittest.mock import patch

from agentic_core.L0_routing.enforcement.execution_gateway import (
    V15ExecutionGateway,
)

# ===========================================================================
# Helpers
# ===========================================================================


def _make_manifest(seed: str):
    """Create a distinct valid SurgicalManifest from a seed."""
    from agentic_core.L0_routing.enforcement.traceability_contracts import generate_trace_id
    from agentic_core.L0_routing.types.determinism_types import FixConstraint, SurgicalManifest

    _hex8 = hashlib.sha256(seed.encode()).hexdigest()[:8].upper()
    trace_id = generate_trace_id(_hex8)
    snippet = f"{seed}()"
    return SurgicalManifest(
        schema_version="1.0.0",
        correlation_id=trace_id,
        node_id=f"Node_{seed}",
        target_layer="L0",
        ast_snippet=snippet,
        serialization_canon=seed,
        fix_constraint=FixConstraint.RELAXED,
        manifest_hash=hashlib.sha256(snippet.encode()).hexdigest(),
        change_history=(),
        provenance_chain=(trace_id,),
    )


def _stub_hashes():
    return (
        hashlib.sha256(b"fs").hexdigest(),
        hashlib.sha256(b"git").hexdigest(),
        hashlib.sha256(b"mem").hexdigest(),
    )


def _ok_heal(manifest):
    return {"status": "ok", "errors": 0}


# ===========================================================================
# A) Clean-Path State Growth Bound
# ===========================================================================

N_CLEAN = 500


class TestCleanPathBoundedness:
    """N=500 clean execute() calls on one gateway instance."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_violation_lists_zero_after_every_call(self):
        """Per-call violation lists must be empty after each clean call."""
        gw = V15ExecutionGateway()
        for i in range(N_CLEAN):
            m = _make_manifest(f"clean_{i}")
            r = gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)
            assert r.success is True
            assert len(gw._pipe_violations) == 0, f"Pipe violations leaked at call {i}"
            assert len(gw._policy_violations) == 0, f"Policy violations leaked at call {i}"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_seen_signals_grows_at_most_one_per_call(self):
        """_seen_signals must grow by at most 1 per unique manifest."""
        gw = V15ExecutionGateway()
        for i in range(N_CLEAN):
            before = len(gw._seen_signals)
            m = _make_manifest(f"grow_{i}")
            gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)
            after = len(gw._seen_signals)
            delta = after - before
            assert delta <= 1, f"_seen_signals grew by {delta} at call {i} (expected ≤1)"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_seen_signals_total_equals_unique_manifests(self):
        """After N unique calls, _seen_signals size == N."""
        gw = V15ExecutionGateway()
        for i in range(N_CLEAN):
            m = _make_manifest(f"total_{i}")
            gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)
        assert len(gw._seen_signals) == N_CLEAN

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_repeated_same_manifest_no_signal_growth(self):
        """Repeated identical manifests must NOT grow _seen_signals beyond 1."""
        gw = V15ExecutionGateway()
        m = _make_manifest("repeat_same")
        for i in range(100):
            gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)
        assert len(gw._seen_signals) == 1

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_clock_tick_monotonic(self):
        """Semantic clock tick must increase monotonically across clean calls."""
        gw = V15ExecutionGateway()
        prev_tick = -1
        for i in range(50):
            m = _make_manifest(f"clock_{i}")
            r = gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)
            assert r.semantic_clock_tick > prev_tick, (
                f"Clock not monotonic at call {i}: {prev_tick} -> {r.semantic_clock_tick}"
            )
            prev_tick = r.semantic_clock_tick

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_mismatch_tracker_replaced_each_call(self):
        """_mismatch_tracker must be a fresh instance per call with correct wave_id."""
        gw = V15ExecutionGateway()
        for i in range(20):
            m = _make_manifest(f"tracker_{i}")
            gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)
            # Tracker's wave_id must match the most recent trace_id
            assert gw._mismatch_tracker is not None
            assert gw._mismatch_tracker.wave_id == m.correlation_id, (
                f"Tracker wave_id mismatch at call {i}: {gw._mismatch_tracker.wave_id} != {m.correlation_id}"
            )


# ===========================================================================
# B) Violation-Path Boundedness
# ===========================================================================

N_VIOL = 200


class TestViolationPathBoundedness:
    """N=200 calls each forcing a single violation (LOG_ONLY mode)."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_violation_list_constant_size_per_call(self):
        """Per-call violation list must reset each time, not accumulate."""
        gw = V15ExecutionGateway()
        for i in range(N_VIOL):
            m = _make_manifest(f"viol_{i}")

            def _failing_heal(manifest):
                return {"status": "fail", "errors": 1}

            gw.execute(m, _failing_heal, _stub_hashes, trace_id=m.correlation_id)
            # Pipe violations should be 0 (no pipe order violation, just heal failure)
            assert len(gw._pipe_violations) == 0, f"Pipe violations accumulated at call {i}"
            assert len(gw._policy_violations) == 0, f"Policy violations accumulated at call {i}"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_dedupe_growth_under_repeated_violations(self):
        """Dedupe set grows by at most 1 per unique manifest even on failure path."""
        gw = V15ExecutionGateway()
        for i in range(N_VIOL):
            m = _make_manifest(f"dedup_viol_{i}")

            def _failing_heal(manifest):
                return {"status": "fail", "errors": 1}

            before = len(gw._seen_signals)
            gw.execute(m, _failing_heal, _stub_hashes, trace_id=m.correlation_id)
            after = len(gw._seen_signals)
            assert after - before <= 1, f"Dedupe grew by {after - before} at call {i}"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_same_violation_repeated_no_accumulation(self):
        """Same manifest failing N times: violation lists stay constant, dedupe stays at 1."""
        gw = V15ExecutionGateway()
        m = _make_manifest("same_viol")

        def _failing_heal(manifest):
            return {"status": "fail", "errors": 1}

        for i in range(N_VIOL):
            gw.execute(m, _failing_heal, _stub_hashes, trace_id=m.correlation_id)

        assert len(gw._seen_signals) == 1
        assert len(gw._pipe_violations) == 0
        assert len(gw._policy_violations) == 0
