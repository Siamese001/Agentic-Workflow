"""V15 P9.3 — Daemon Soak Stability Guards.

Deterministic (no timing thresholds). Proves over many cycles:
1) No accumulation in per-call lists
2) _seen_signals growth caps at K for K unique cycling manifests
3) Clock monotonic across all cycles
4) Mode behavior stable after many prior cycles (no drift)
"""

from __future__ import annotations

import hashlib
import os
from unittest.mock import patch

import pytest

from agentic_core.L0_maintenance.enforcement.v15_execution_gateway import (
    V15ExecutionGateway,
)
from agentic_core.L0_maintenance.types.guardian_contract import (
    V15HardFailAbort,
)

# ===========================================================================
# Helpers
# ===========================================================================

K_UNIQUE = 10
N_CYCLES = 2000


def _make_manifest(seed: str):
    """Create a distinct valid SurgicalManifest from a seed."""
    from agentic_core.L0_maintenance.enforcement.v15_p4_contracts import generate_trace_id
    from agentic_core.L0_maintenance.types.v15_p2_types import FixConstraint, SurgicalManifest

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


# Pre-build K unique manifests for cycling
CYCLING_MANIFESTS = [_make_manifest(f"daemon_{i}") for i in range(K_UNIQUE)]


# ===========================================================================
# A) Daemon Cycle Soak (LOG_ONLY)
# ===========================================================================


class TestDaemonSoakLogOnly:
    """N=2000 sequential cycles on one gateway, K=10 cycling manifests."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_violation_lists_empty_every_cycle(self):
        """Per-call violation lists must be empty after every cycle."""
        gw = V15ExecutionGateway()
        for i in range(N_CYCLES):
            m = CYCLING_MANIFESTS[i % K_UNIQUE]
            gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)
            assert len(gw._pipe_violations) == 0, f"Pipe violations at cycle {i}"
            assert len(gw._policy_violations) == 0, f"Policy violations at cycle {i}"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_seen_signals_caps_at_k(self):
        """_seen_signals must cap at K unique entries, not grow to N."""
        gw = V15ExecutionGateway()
        for i in range(N_CYCLES):
            m = CYCLING_MANIFESTS[i % K_UNIQUE]
            gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)
        assert len(gw._seen_signals) == K_UNIQUE, f"Expected {K_UNIQUE}, got {len(gw._seen_signals)}"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_seen_signals_stable_after_first_k(self):
        """After the first K calls, _seen_signals size must not change."""
        gw = V15ExecutionGateway()
        # Warm up: first K calls
        for i in range(K_UNIQUE):
            m = CYCLING_MANIFESTS[i]
            gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)
        size_after_warmup = len(gw._seen_signals)
        assert size_after_warmup == K_UNIQUE

        # Soak: remaining N-K calls
        for i in range(K_UNIQUE, N_CYCLES):
            m = CYCLING_MANIFESTS[i % K_UNIQUE]
            gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)
            assert len(gw._seen_signals) == size_after_warmup, (
                f"_seen_signals grew at cycle {i}: {len(gw._seen_signals)}"
            )

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_clock_monotonic_across_all_cycles(self):
        """Semantic clock must be strictly monotonic across all N cycles."""
        gw = V15ExecutionGateway()
        prev_tick = -1
        for i in range(N_CYCLES):
            m = CYCLING_MANIFESTS[i % K_UNIQUE]
            r = gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)
            assert r.semantic_clock_tick > prev_tick, (
                f"Clock not monotonic at cycle {i}: {prev_tick} -> {r.semantic_clock_tick}"
            )
            prev_tick = r.semantic_clock_tick

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_all_cycles_succeed(self):
        """All N cycles must succeed (no silent failure drift)."""
        gw = V15ExecutionGateway()
        for i in range(N_CYCLES):
            m = CYCLING_MANIFESTS[i % K_UNIQUE]
            r = gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)
            assert r.success is True, f"Cycle {i} failed unexpectedly: {r.error}"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_dedupe_hit_after_warmup(self):
        """After first K unique calls, all subsequent calls should be dedupe hits."""
        gw = V15ExecutionGateway()
        for i in range(K_UNIQUE):
            m = CYCLING_MANIFESTS[i]
            r = gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)
            assert r.dedupe_hit is False, f"Unexpected dedupe hit at warmup {i}"

        for i in range(K_UNIQUE, K_UNIQUE + 100):
            m = CYCLING_MANIFESTS[i % K_UNIQUE]
            r = gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)
            assert r.dedupe_hit is True, f"Expected dedupe hit at cycle {i}"


# ===========================================================================
# B) Mode Smoke After Soak
# ===========================================================================


class TestModeSmokeAfterSoak:
    """Prove mode behavior is stable after many prior cycles."""

    def _soak_gateway(self, gw, n=500):
        """Run n clean LOG_ONLY cycles to age the gateway."""
        with patch.dict(os.environ, {"V15_ENFORCEMENT": "log"}):
            for i in range(n):
                m = CYCLING_MANIFESTS[i % K_UNIQUE]
                gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)

    def test_soft_fail_stable_after_soak(self):
        """SOFT_FAIL returns structured failure after many prior cycles."""
        from agentic_core.L0_maintenance.types.v15_contracts import PipeOrderEnforcer

        gw = V15ExecutionGateway()
        self._soak_gateway(gw)

        with patch.dict(os.environ, {"V15_ENFORCEMENT": "soft"}):
            m = _make_manifest("post_soak_soft")
            _orig_inner = gw._execute_inner

            def _force_violation(*args, **kwargs):
                pipe = PipeOrderEnforcer()
                gw._pipe_advance(pipe, "hash_verification", "soak-soft")
                return _orig_inner(*args, **kwargs)

            with patch.object(gw, "_execute_inner", _force_violation):
                r = gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)

            assert r.success is False
            assert "SOFT_FAIL" in r.error

    def test_hard_fail_stable_after_soak(self):
        """HARD_FAIL raises V15HardFailAbort after many prior cycles."""
        from agentic_core.L0_maintenance.types.v15_contracts import PipeOrderEnforcer

        gw = V15ExecutionGateway()
        self._soak_gateway(gw)

        with patch.dict(os.environ, {"V15_ENFORCEMENT": "1"}):
            pipe = PipeOrderEnforcer()
            with pytest.raises(V15HardFailAbort):
                gw._pipe_advance(pipe, "hash_verification", "soak-hard")

    def test_log_only_stable_after_soak(self):
        """LOG_ONLY still succeeds cleanly after many prior cycles."""
        gw = V15ExecutionGateway()
        self._soak_gateway(gw)

        with patch.dict(os.environ, {"V15_ENFORCEMENT": "log"}):
            m = _make_manifest("post_soak_log")
            r = gw.execute(m, _ok_heal, _stub_hashes, trace_id=m.correlation_id)
            assert r.success is True
            assert r.error is None
