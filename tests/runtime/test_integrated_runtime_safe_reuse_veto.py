"""W2 — Veto must be invoked on every D2 hit; fail-closed buckets never allow.

Drives the production entry point with deterministic veto verdicts:
SAFE / UNSAFE / UNKNOWN / ERROR / TIMEOUT / PARSE_FAIL. Asserts that
SafeReuseDecision invariants hold for every bucket.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.entrypoints.integrated_safe_reuse_run import run_integrated_safe_reuse
from agentic_core.runtime.contracts.safe_reuse_decision import SafeReuseDecision
from agentic_core.runtime.contracts.runtime_gate_verdict_bundle import VetoOutcome
from tools.certification.safety.deterministic_proof_stage import DeterministicProofStage
from tools.certification.safety.veto_orchestrator import VetoOrchestrator


def _seed_and_run(tmp: Path, *, verdict: str, query: str = "Q?", cached: str = "Q'?"):
    """Seed cache + run entry point with a deterministic verdict."""
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
        SemanticCacheManager,
    )
    cache = SemanticCacheManager.get_instance()
    namespace = f"test_w2_veto_{verdict.lower()}"
    ctx = json.dumps(
        {"body_text": query, "namespace": namespace, "tenant_id": "", "policy_hash": "no-policy"},
        sort_keys=True, separators=(",", ":"),
    )
    cache.learn(ctx, namespace, {"text": "answer", "answer": "answer",
                                  "cached_query_text": cached})
    os.environ.setdefault("SEMANTIC_CACHE_D2_ENABLED", "1")
    orch = VetoOrchestrator(stages=[
        DeterministicProofStage(verdicts={(query, cached): verdict})
    ])
    return run_integrated_safe_reuse(
        {"body_text": query, "transport": "api"},
        namespace=namespace, tenant_id="",
        artifact_dir=tmp,
        veto_orchestrator=orch,
    )


class TestVetoOutcomes:
    def test_safe_verdict_allows(self, tmp_path):
        r = _seed_and_run(tmp_path, verdict="SAFE")
        assert r.cache_hit is True
        assert r.safe_reuse_decision.allow is True
        assert r.safe_reuse_decision.veto_outcome is VetoOutcome.ALLOWED
        assert r.safe_reuse_decision.unsafe_reuse_allowed_count == 0
        assert r.x3_disposition == "X3D"

    @pytest.mark.parametrize("verdict,expected_outcome", [
        ("UNSAFE_DIFFERENT_INTENT", VetoOutcome.BLOCKED),
        ("UNSAFE_POLICY_DRIFT",     VetoOutcome.BLOCKED),
        ("VETO",                    VetoOutcome.BLOCKED),
    ])
    def test_blocking_verdicts_block_reuse(self, tmp_path, verdict, expected_outcome):
        r = _seed_and_run(tmp_path, verdict=verdict)
        assert r.safe_reuse_decision.allow is False
        assert r.safe_reuse_decision.veto_outcome is expected_outcome
        assert r.safe_reuse_decision.safe_reuse_blocked_count == 1
        # No fail-closed counter for legitimate BLOCK.
        assert r.safe_reuse_decision.unknown_error_timeout_parse_fail_block_count == 0

    @pytest.mark.parametrize("verdict,expected_outcome", [
        ("UNCERTAIN",  VetoOutcome.UNKNOWN),
        ("UNKNOWN",    VetoOutcome.UNKNOWN),
        ("TIMEOUT",    VetoOutcome.TIMEOUT),
        ("PARSE_FAIL", VetoOutcome.PARSE_FAIL),
        ("ERROR",      VetoOutcome.ERROR),
    ])
    def test_fail_closed_buckets_never_allow(self, tmp_path, verdict, expected_outcome):
        r = _seed_and_run(tmp_path, verdict=verdict)
        assert r.safe_reuse_decision.allow is False
        assert r.safe_reuse_decision.veto_outcome is expected_outcome
        # Fail-closed counter increments.
        assert r.safe_reuse_decision.unknown_error_timeout_parse_fail_block_count == 1
        assert r.safe_reuse_decision.unsafe_reuse_allowed_count == 0


class TestSafeReuseDecisionInvariants:
    """The SafeReuseDecision contract refuses unsafe states at construction."""

    def test_allow_without_dense_candidate_raises(self):
        with pytest.raises(ValueError, match="dense_candidate_produced"):
            SafeReuseDecision(
                allow=True, reason_code="SAFE_REUSE",
                dense_candidate_produced=False, veto_invoked=True,
                veto_outcome=VetoOutcome.ALLOWED, d2_similarity=0.95,
            )

    def test_allow_without_veto_invoked_raises(self):
        with pytest.raises(ValueError, match="veto_invoked"):
            SafeReuseDecision(
                allow=True, reason_code="SAFE_REUSE",
                dense_candidate_produced=True, veto_invoked=False,
                veto_outcome=VetoOutcome.ALLOWED, d2_similarity=0.95,
            )

    @pytest.mark.parametrize("outcome", [
        VetoOutcome.UNKNOWN, VetoOutcome.ERROR,
        VetoOutcome.TIMEOUT, VetoOutcome.PARSE_FAIL,
        VetoOutcome.BLOCKED, VetoOutcome.NOT_INVOKED,
    ])
    def test_non_allowed_outcome_with_allow_raises(self, outcome):
        # ANY non-ALLOWED outcome with allow=True is rejected. The
        # message matches "veto_outcome=ALLOWED" because that invariant
        # fires first in __post_init__; the fail-closed check is the
        # second-line defense and is independently exercised through
        # the full integration runs above.
        with pytest.raises(ValueError, match="ALLOWED"):
            SafeReuseDecision(
                allow=True, reason_code="SAFE_REUSE",
                dense_candidate_produced=True, veto_invoked=True,
                veto_outcome=outcome, d2_similarity=0.95,
            )

    def test_unsafe_reuse_allowed_with_block_raises(self):
        with pytest.raises(ValueError, match="unsafe_reuse_allowed_count"):
            SafeReuseDecision(
                allow=False, reason_code="VETOED",
                dense_candidate_produced=True, veto_invoked=True,
                veto_outcome=VetoOutcome.BLOCKED, d2_similarity=0.95,
                unsafe_reuse_allowed_count=1,
            )
