"""Unit tests for PA invariants checker."""

from __future__ import annotations

from agentic_core.prompt_governance.prompt_assembly.invariants import check_invariants


def _ok_ctx(**overrides):
    base = dict(
        s0_present=True,
        s0_user_supplied=False,
        d0_present=True,
        c0_present=False,
        d0_includes_rc_controls=True,
        u0_origin_trust="user_turn",
        u0_overrides_s0=False,
        c0_overrides_s0=False,
        h0_overrides_d0=False,
        contradictions_present=False,
        contradictions_preserved=True,
        grounding_required=False,
        evidence_present=True,
        evidence_status="PASS",
        support_score=0.9,
        support_threshold=0.6,
        r0_parseable=True,
        r0_can_abstain=True,
        r0_can_cite=True,
        citation_required=False,
        tools_present=False,
        tools_in_registry=True,
        tools_allowed_by_token=True,
        capability_token_present=True,
        policy_hashes=("ph", "ph"),
        blueprint_hashes=("bp",),
        replay_key_present=True,
        manifest_hash_present=True,
        signature_present=True,
        budget_overflow=False,
        token_budget_respected=True,
        dispatch_allowed=True,
        events_emitted=("PromptAssemblyStarted", "PromptAssemblyDispatched"),
        spans_emitted=("prompt_assembly.boundary_check",),
        executable_requested=False,
        hitl_required=False,
        provider_lane="anthropic",
        provider_lanes_supported=("anthropic", "openai_chat"),
    )
    base.update(overrides)
    return base


def test_invariants_all_held_in_ok_ctx():
    rep = check_invariants(_ok_ctx())
    assert rep.all_held is True
    assert len(rep.results) == 30


def test_inv_02_s0_user_supplied_violation():
    rep = check_invariants(_ok_ctx(s0_user_supplied=True))
    ids = {r.invariant_id for r in rep.violations}
    assert "INV-02" in ids


def test_inv_05_c0_overrides_s0_violation():
    rep = check_invariants(_ok_ctx(c0_overrides_s0=True))
    assert "INV-05" in {r.invariant_id for r in rep.violations}


def test_inv_09_grounding_no_evidence_violation():
    rep = check_invariants(_ok_ctx(grounding_required=True, evidence_present=False))
    assert "INV-09" in {r.invariant_id for r in rep.violations}


def test_inv_10_grounding_blocked_evidence_violation():
    rep = check_invariants(_ok_ctx(grounding_required=True, evidence_status="BLOCKED"))
    assert "INV-10" in {r.invariant_id for r in rep.violations}


def test_inv_19_policy_hash_consistency_violation():
    rep = check_invariants(_ok_ctx(policy_hashes=("ph-a", "ph-b")))
    assert "INV-19" in {r.invariant_id for r in rep.violations}


def test_inv_24_budget_overflow_dispatched_violation():
    rep = check_invariants(_ok_ctx(budget_overflow=True, dispatch_allowed=True))
    assert "INV-24" in {r.invariant_id for r in rep.violations}


def test_inv_26_first_event_violation():
    rep = check_invariants(_ok_ctx(events_emitted=("PromptBOMResolved", "PromptAssemblyDispatched")))
    assert "INV-26" in {r.invariant_id for r in rep.violations}


def test_inv_29_hitl_with_executable_violation():
    rep = check_invariants(_ok_ctx(hitl_required=True, executable_requested=True))
    assert "INV-29" in {r.invariant_id for r in rep.violations}


def test_inv_30_unknown_provider_lane_violation():
    rep = check_invariants(_ok_ctx(provider_lane="rogue", provider_lanes_supported=("anthropic",)))
    assert "INV-30" in {r.invariant_id for r in rep.violations}
