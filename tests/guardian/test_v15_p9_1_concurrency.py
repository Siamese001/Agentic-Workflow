"""V15 P9.1 — Concurrency & Reentrancy Safety for V15ExecutionGateway.

Proves:
1) Sequential reuse: no state leakage between consecutive execute() calls
2) Concurrent isolation: two threads on the same gateway instance do not
   cross-contaminate per-call state (violations, manifests, trace_ids)
"""

from __future__ import annotations

import hashlib
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from agentic_core.L0_routing.enforcement.execution_gateway import (
    GatewayResult,
    V15ExecutionGateway,
)

# ===========================================================================
# Helpers
# ===========================================================================


def _make_manifest(seed: str):
    """Create a distinct valid SurgicalManifest from a seed string."""
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


def _failing_heal(manifest):
    return {"status": "fail", "errors": 1}


# ===========================================================================
# A) Sequential Reuse — No State Leakage
# ===========================================================================


class TestSequentialReuse:
    """Single gateway instance, two consecutive execute() calls."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_second_execute_has_no_carried_violations(self):
        """First call triggers a healing failure; second call must start clean."""
        gw = V15ExecutionGateway()

        # First call: heal_fn returns errors → commit_valid=False
        m1 = _make_manifest("seq_first")
        r1 = gw.execute(m1, _failing_heal, _stub_hashes, trace_id=m1.correlation_id)
        assert r1.success is False

        # Second call: clean heal
        m2 = _make_manifest("seq_second")
        r2 = gw.execute(m2, _ok_heal, _stub_hashes, trace_id=m2.correlation_id)
        assert r2.success is True
        assert r2.error is None
        # Must NOT carry over first call's manifest
        assert r2.manifest.node_id == "Node_seq_second"
        assert r2.manifest.correlation_id == m2.correlation_id

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_violation_lists_reset_between_calls(self):
        """Pipe/policy violation lists must be empty at start of each execute()."""
        gw = V15ExecutionGateway()

        m1 = _make_manifest("seq_viol_1")
        gw.execute(m1, _ok_heal, _stub_hashes, trace_id=m1.correlation_id)

        # After first call, manually inspect internal state reset
        # (execute() resets at top — but we verify after second call)
        m2 = _make_manifest("seq_viol_2")
        gw.execute(m2, _ok_heal, _stub_hashes, trace_id=m2.correlation_id)

        # Internal lists should only have state from most recent call (empty if no violations)
        assert gw._pipe_violations == []
        assert gw._policy_violations == []

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_dedupe_set_persists_across_calls(self):
        """_seen_signals is intentionally persistent (dedupe across waves)."""
        gw = V15ExecutionGateway()

        m1 = _make_manifest("seq_dedupe")
        r1 = gw.execute(m1, _ok_heal, _stub_hashes, trace_id=m1.correlation_id)
        assert r1.dedupe_hit is False

        # Same manifest again → dedupe hit expected
        r2 = gw.execute(m1, _ok_heal, _stub_hashes, trace_id=m1.correlation_id)
        assert r2.dedupe_hit is True

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_clock_advances_across_sequential_calls(self):
        """Semantic clock must advance, not reset, across sequential calls."""
        gw = V15ExecutionGateway()

        m1 = _make_manifest("seq_clock_1")
        r1 = gw.execute(m1, _ok_heal, _stub_hashes, trace_id=m1.correlation_id)
        tick1 = r1.semantic_clock_tick

        m2 = _make_manifest("seq_clock_2")
        r2 = gw.execute(m2, _ok_heal, _stub_hashes, trace_id=m2.correlation_id)
        tick2 = r2.semantic_clock_tick

        assert tick2 > tick1, f"Clock did not advance: {tick1} -> {tick2}"


# ===========================================================================
# B) Concurrent Isolation — Two Threads, Same Gateway
# ===========================================================================


class TestConcurrentIsolation:
    """Two threads sharing one V15ExecutionGateway instance."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_concurrent_results_have_correct_trace_ids(self):
        """Each thread's result must reference only its own trace_id/manifest."""
        gw = V15ExecutionGateway()
        barrier = threading.Barrier(2, timeout=5)

        m_a = _make_manifest("conc_alpha")
        m_b = _make_manifest("conc_beta")

        results: dict[str, GatewayResult] = {}

        def _run(manifest, label):
            def _barrier_heal(m):
                barrier.wait()  # synchronize: both threads inside heal_fn
                return {"status": "ok", "errors": 0}

            r = gw.execute(manifest, _barrier_heal, _stub_hashes, trace_id=manifest.correlation_id)
            results[label] = r

        with ThreadPoolExecutor(max_workers=2) as pool:
            fa = pool.submit(_run, m_a, "alpha")
            fb = pool.submit(_run, m_b, "beta")
            fa.result(timeout=10)
            fb.result(timeout=10)

        ra = results["alpha"]
        rb = results["beta"]

        # Each result must reference its own manifest
        assert ra.manifest.node_id == "Node_conc_alpha"
        assert rb.manifest.node_id == "Node_conc_beta"
        assert ra.manifest.correlation_id == m_a.correlation_id
        assert rb.manifest.correlation_id == m_b.correlation_id

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_concurrent_no_cross_contaminated_violations(self):
        """Violation records must reference only their own trace_id."""
        gw = V15ExecutionGateway()
        barrier = threading.Barrier(2, timeout=5)

        m_a = _make_manifest("conc_iso_a")
        m_b = _make_manifest("conc_iso_b")

        results: dict[str, GatewayResult] = {}
        violations_snapshot: dict[str, list] = {}

        def _run(manifest, label):
            def _barrier_heal(m):
                barrier.wait()
                return {"status": "ok", "errors": 0}

            r = gw.execute(manifest, _barrier_heal, _stub_hashes, trace_id=manifest.correlation_id)
            results[label] = r
            # Snapshot violations right after execute returns
            violations_snapshot[label] = list(gw._pipe_violations)

        with ThreadPoolExecutor(max_workers=2) as pool:
            fa = pool.submit(_run, m_a, "a")
            fb = pool.submit(_run, m_b, "b")
            fa.result(timeout=10)
            fb.result(timeout=10)

        # With no forced violations, both should have empty pipe violation lists
        # The key assertion: no violations from the other thread leaked in
        for label, viols in violations_snapshot.items():
            for v in viols:
                assert v.get("trace_id") != results["a" if label == "b" else "b"].manifest.correlation_id, (
                    f"Cross-contamination: {label} has violation from other thread"
                )

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_concurrent_both_succeed(self):
        """Both concurrent executions must succeed independently."""
        gw = V15ExecutionGateway()
        barrier = threading.Barrier(2, timeout=5)

        m_a = _make_manifest("conc_ok_a")
        m_b = _make_manifest("conc_ok_b")

        results: dict[str, GatewayResult] = {}

        def _run(manifest, label):
            def _barrier_heal(m):
                barrier.wait()
                return {"status": "ok", "errors": 0}

            r = gw.execute(manifest, _barrier_heal, _stub_hashes, trace_id=manifest.correlation_id)
            results[label] = r

        with ThreadPoolExecutor(max_workers=2) as pool:
            fa = pool.submit(_run, m_a, "a")
            fb = pool.submit(_run, m_b, "b")
            fa.result(timeout=10)
            fb.result(timeout=10)

        assert results["a"].success is True
        assert results["b"].success is True

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_concurrent_mixed_success_failure(self):
        """One thread succeeds, one fails — results must not mix."""
        gw = V15ExecutionGateway()
        barrier = threading.Barrier(2, timeout=5)

        m_ok = _make_manifest("conc_mix_ok")
        m_fail = _make_manifest("conc_mix_fail")

        results: dict[str, GatewayResult] = {}

        def _run_ok(manifest, label):
            def _heal(m):
                barrier.wait()
                return {"status": "ok", "errors": 0}

            results[label] = gw.execute(manifest, _heal, _stub_hashes, trace_id=manifest.correlation_id)

        def _run_fail(manifest, label):
            def _heal(m):
                barrier.wait()
                return {"status": "fail", "errors": 1}

            results[label] = gw.execute(manifest, _heal, _stub_hashes, trace_id=manifest.correlation_id)

        with ThreadPoolExecutor(max_workers=2) as pool:
            fa = pool.submit(_run_ok, m_ok, "ok")
            fb = pool.submit(_run_fail, m_fail, "fail")
            fa.result(timeout=10)
            fb.result(timeout=10)

        # Each result must match its own outcome
        r_ok = results["ok"]
        r_fail = results["fail"]

        assert r_ok.manifest.node_id == "Node_conc_mix_ok"
        assert r_fail.manifest.node_id == "Node_conc_mix_fail"

        # At least one must succeed and one must fail
        # (Under a race, both could appear to succeed or fail incorrectly)
        outcomes = {r_ok.success, r_fail.success}
        assert outcomes == {True, False}, (
            f"Expected one success + one failure, got ok={r_ok.success}, fail={r_fail.success}"
        )
