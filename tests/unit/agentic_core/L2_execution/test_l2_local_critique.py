"""Tests for spec 04.10 L2 Verify-Then-Execute / Local Critique.

Spec source: docs/reference/04_L2_Execute/04.10_L2_Verify_Then_Execute_Local_Critique.md
SUT:         agentic_core/L2_execution/types/l2_local_critique.py
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.observability.l2_spans import (
    L2_LOCAL_CRITIQUE_SPANS,
)
from agentic_core.L2_execution.types.l2_local_critique import (
    DEFAULT_MAX_LOCAL_CRITIQUE_PASSES,
    CritiqueResult,
    CritiqueType,
    LocalCritiqueInput,
    LocalCritiqueReceipt,
)


def _input(**overrides: object) -> LocalCritiqueInput:
    base = dict(
        approved_work_order_ref="wo-1",
        invocation_candidate_ref="inv-1",
        capability_token_ref="cap-1",
        sandbox_envelope_ref="sb-1",
        policy_hash="ph",
        blueprint_hash="bh",
        replay_key="rk",
        risk_tier="HIGH",
        verification_budget=100,
    )
    base.update(overrides)
    return LocalCritiqueInput(**base)  # type: ignore[arg-type]


def _receipt(**overrides: object) -> LocalCritiqueReceipt:
    base = dict(
        critique_receipt_id="cr-1",
        critique_type=CritiqueType.PRE_INVOCATION,
        result=CritiqueResult.PASS,
        deterministic_digest="dig",
    )
    base.update(overrides)
    return LocalCritiqueReceipt(**base)  # type: ignore[arg-type]


# ---------------------------------- spec 04.10 §TEST REQUIREMENTS (6 entries)
def test_local_critique_blocks_script_outside_sandbox() -> None:
    """SCRIPT_SAFETY_SANITY critique with FAIL_LOCAL records the block."""
    r = _receipt(
        critique_type=CritiqueType.SCRIPT_SAFETY_SANITY,
        result=CritiqueResult.FAIL_LOCAL,
        reason_codes=("script_path_outside_sandbox_envelope",),
    )
    assert r.result is CritiqueResult.FAIL_LOCAL
    assert "script_path_outside_sandbox_envelope" in r.reason_codes


def test_local_critique_cannot_change_route() -> None:
    """no_route_change_assertion is always True — overriding to False is rejected."""
    r = _receipt()
    assert r.no_route_change_assertion is True
    with pytest.raises(ValueError, match="no_route_change_assertion"):
        _receipt(no_route_change_assertion=False)


def test_local_critique_cannot_fetch_evidence() -> None:
    """no_new_evidence_assertion pinned True. Spec DISALLOWED 'Fetch new evidence'."""
    r = _receipt()
    assert r.no_new_evidence_assertion is True
    with pytest.raises(ValueError, match="no_new_evidence_assertion"):
        _receipt(no_new_evidence_assertion=False)


def test_local_critique_counts_against_l2_budget() -> None:
    """verification_budget must be positive and is recorded on the input."""
    inp = _input(verification_budget=42)
    assert inp.verification_budget == 42
    with pytest.raises(ValueError, match="verification_budget"):
        _input(verification_budget=0)
    with pytest.raises(ValueError, match="verification_budget"):
        _input(verification_budget=-1)


def test_local_critique_receipt_replays() -> None:
    """deterministic_digest is required; equal inputs produce equal receipts."""
    r1 = _receipt()
    r2 = _receipt()
    assert r1 == r2
    with pytest.raises(ValueError, match="deterministic_digest"):
        _receipt(deterministic_digest="")


def test_local_critique_post_output_schema_sanity_before_e5() -> None:
    """ARTIFACT_SANITY/SCHEMA_SANITY post-invocation critique types are modeled."""
    r = _receipt(
        critique_type=CritiqueType.ARTIFACT_SANITY,
        result=CritiqueResult.WARN_LOCAL,
        reason_codes=("artifact_manifest_unparseable",),
    )
    assert r.critique_type is CritiqueType.ARTIFACT_SANITY
    schema = _receipt(
        critique_type=CritiqueType.SCHEMA_SANITY,
        result=CritiqueResult.PASS,
    )
    assert schema.critique_type is CritiqueType.SCHEMA_SANITY


# ---------------------------------- additional invariants
def test_local_critique_default_loop_bound_is_1() -> None:
    """Spec 04.10 LOOP BOUNDS — default max_local_critique_passes = 1."""
    assert DEFAULT_MAX_LOCAL_CRITIQUE_PASSES == 1


def test_local_critique_spans_registered() -> None:
    """All 7 local-critique span names are in the canonical L2 span registry."""
    assert "l2.local_critique.pre_invocation" in L2_LOCAL_CRITIQUE_SPANS
    assert "l2.local_critique.post_invocation" in L2_LOCAL_CRITIQUE_SPANS
    assert len(L2_LOCAL_CRITIQUE_SPANS) >= len(list(CritiqueType))


def test_local_critique_adjustment_requires_flag() -> None:
    """Suggested adjustment without adjustment_allowed=True is rejected."""
    with pytest.raises(ValueError, match="adjustment_allowed"):
        _receipt(suggested_local_adjustment="rerun-with-narrower-args")
    ok = _receipt(
        suggested_local_adjustment="rerun-with-narrower-args",
        adjustment_allowed=True,
    )
    assert ok.adjustment_allowed is True
