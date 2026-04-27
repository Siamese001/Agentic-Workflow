"""Unit tests for L5 cross-child governance consistency gate.

Maps to: docs/reference/00A_L5_Governance_Safety/00A.7a_L5_Governance_Context_Invariant.md
Phase 4 INVARIANTS, Phase 7 TEST CONTRACT.
And: docs/reference/00A_L5_Governance_Safety/00A.8a_L5_Cross_Child_Certification_Consistency_Tests.md
Phases 2-5 (positive, negative, applicability, anti-bypass).
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.enforcement.governance_consistency_gate import (
    L5_GOVERNANCE_CONTEXT_MISMATCH_RULE_ID,
    L5GovernanceContextMismatchError,
    assert_l5_cross_child_match,
)
from agentic_core.L5_safety.types.l5_governance_context import (
    CertificationScope,
    ExecutionForm,
    L5GovernanceContext,
    RiskTier,
    SideEffectClass,
)


def _filler(seed: str) -> str:
    return (seed * 16)[:64]


def _ctx(
    *,
    execution_form: ExecutionForm = ExecutionForm.L2_BOUNDED,
    side_effect_class: SideEffectClass = SideEffectClass.READ_ONLY,
    hitl: str = "",
    reclear: str = "",
    egress: str = "",
) -> L5GovernanceContext:
    return L5GovernanceContext(
        request_id="req-1",
        run_id="run-1",
        trace_id="trace-1",
        tenant_id="tenant-1",
        principal_id="prin-1",
        session_id="sess-1",
        route_id="route-1",
        step_id="step-1",
        execution_form=execution_form,
        risk_tier=RiskTier.R2,
        side_effect_class=side_effect_class,
        policy_hash=_filler("a"),
        blueprint_hash=_filler("b"),
        registry_snapshot_hash=_filler("c"),
        agent_profile_hash=_filler("d"),
        capability_scope_hash=_filler("e"),
        sandbox_envelope_hash=_filler("f"),
        origin_trust_manifest_hash=_filler("0"),
        egress_profile_hash=egress,
        hitl_packet_hash=hitl,
        reclearance_hash=reclear,
        replay_envelope_hash=_filler("1"),
        audit_manifest_hash=_filler("2"),
        static_governance_snapshot_hash=_filler("3"),
        certifier_id="cert-1",
        certifier_version="v1",
        certification_scope=CertificationScope.AGGREGATE,
        frozen_governance_context_hash=_filler("4"),
        l5_resolver_digest=_filler("5"),
    )


# --------------------------------------------------------------------- #
# Phase 2 — Positive coverage
# --------------------------------------------------------------------- #

class TestPositive:
    def test_p1_all_required_match_returns_aggregate(self) -> None:
        ctx = _ctx()
        canonical = ctx.digest()
        result = assert_l5_cross_child_match(
            canonical_context=ctx,
            safety_enforcement_digest=canonical,
            authority_binding_digest=canonical,
            origin_trust_digest=canonical,
            replay_audit_digest=canonical,
            static_governance_digest=canonical,
        )
        assert result == canonical

    def test_p2_with_hitl_required_and_present(self) -> None:
        ctx = _ctx(
            execution_form=ExecutionForm.HITL_ONLY,
            hitl=_filler("h"),
            reclear=_filler("r"),
        )
        canonical = ctx.digest()
        result = assert_l5_cross_child_match(
            canonical_context=ctx,
            safety_enforcement_digest=canonical,
            authority_binding_digest=canonical,
            origin_trust_digest=canonical,
            replay_audit_digest=canonical,
            static_governance_digest=canonical,
            hitl_reclearance_digest=canonical,
        )
        assert result == canonical

    def test_p3_with_egress_required_and_present(self) -> None:
        ctx = _ctx(
            side_effect_class=SideEffectClass.EXTERNAL_EGRESS,
            egress=_filler("g"),
        )
        canonical = ctx.digest()
        result = assert_l5_cross_child_match(
            canonical_context=ctx,
            safety_enforcement_digest=canonical,
            authority_binding_digest=canonical,
            origin_trust_digest=canonical,
            replay_audit_digest=canonical,
            static_governance_digest=canonical,
            egress_certification_digest=canonical,
        )
        assert result == canonical

    def test_p4_both_conditional_present(self) -> None:
        ctx = _ctx(
            execution_form=ExecutionForm.HITL_ONLY,
            side_effect_class=SideEffectClass.EXTERNAL_EGRESS,
            hitl=_filler("h"),
            reclear=_filler("r"),
            egress=_filler("g"),
        )
        canonical = ctx.digest()
        result = assert_l5_cross_child_match(
            canonical_context=ctx,
            safety_enforcement_digest=canonical,
            authority_binding_digest=canonical,
            origin_trust_digest=canonical,
            replay_audit_digest=canonical,
            static_governance_digest=canonical,
            hitl_reclearance_digest=canonical,
            egress_certification_digest=canonical,
        )
        assert result == canonical


# --------------------------------------------------------------------- #
# Phase 3 — Negative / anti-cheat (one mismatch per row)
# --------------------------------------------------------------------- #

class TestNegativeOneFieldAtATime:
    @pytest.mark.parametrize(
        "mismatched_field,kwargs_factory",
        [
            (
                "safety_enforcement_digest",
                lambda canonical: dict(
                    safety_enforcement_digest=_filler("X"),
                    authority_binding_digest=canonical,
                    origin_trust_digest=canonical,
                    replay_audit_digest=canonical,
                    static_governance_digest=canonical,
                ),
            ),
            (
                "authority_binding_digest",
                lambda canonical: dict(
                    safety_enforcement_digest=canonical,
                    authority_binding_digest=_filler("X"),
                    origin_trust_digest=canonical,
                    replay_audit_digest=canonical,
                    static_governance_digest=canonical,
                ),
            ),
            (
                "origin_trust_digest",
                lambda canonical: dict(
                    safety_enforcement_digest=canonical,
                    authority_binding_digest=canonical,
                    origin_trust_digest=_filler("X"),
                    replay_audit_digest=canonical,
                    static_governance_digest=canonical,
                ),
            ),
            (
                "replay_audit_digest",
                lambda canonical: dict(
                    safety_enforcement_digest=canonical,
                    authority_binding_digest=canonical,
                    origin_trust_digest=canonical,
                    replay_audit_digest=_filler("X"),
                    static_governance_digest=canonical,
                ),
            ),
            (
                "static_governance_digest",
                lambda canonical: dict(
                    safety_enforcement_digest=canonical,
                    authority_binding_digest=canonical,
                    origin_trust_digest=canonical,
                    replay_audit_digest=canonical,
                    static_governance_digest=_filler("X"),
                ),
            ),
        ],
    )
    def test_one_required_child_mismatch(
        self, mismatched_field: str, kwargs_factory: object
    ) -> None:
        ctx = _ctx()
        canonical = ctx.digest()
        kwargs = kwargs_factory(canonical)  # type: ignore[operator]
        with pytest.raises(L5GovernanceContextMismatchError) as exc_info:
            assert_l5_cross_child_match(canonical_context=ctx, **kwargs)
        ev = exc_info.value.evidence
        assert ev.first_mismatched_field == mismatched_field
        assert ev.certified is False
        assert ev.decisive_rule_id == L5_GOVERNANCE_CONTEXT_MISMATCH_RULE_ID
        assert ev.dispatch_target == "EXIT_CONTROL"
        assert ev.downstream_recommendation == "deny"
        assert ev.sealed_evidence_id.startswith("l5-evid-")


class TestApplicability:
    def test_a1_hitl_skipped_when_required(self) -> None:
        ctx = _ctx(
            execution_form=ExecutionForm.HITL_ONLY,
            hitl=_filler("h"),
            reclear=_filler("r"),
        )
        canonical = ctx.digest()
        with pytest.raises(L5GovernanceContextMismatchError) as exc_info:
            assert_l5_cross_child_match(
                canonical_context=ctx,
                safety_enforcement_digest=canonical,
                authority_binding_digest=canonical,
                origin_trust_digest=canonical,
                replay_audit_digest=canonical,
                static_governance_digest=canonical,
                # hitl_reclearance_digest deliberately omitted
            )
        assert exc_info.value.evidence.first_mismatched_field == "hitl_reclearance_digest"

    def test_a2_egress_skipped_when_required(self) -> None:
        ctx = _ctx(
            side_effect_class=SideEffectClass.EXTERNAL_EGRESS,
            egress=_filler("g"),
        )
        canonical = ctx.digest()
        with pytest.raises(L5GovernanceContextMismatchError) as exc_info:
            assert_l5_cross_child_match(
                canonical_context=ctx,
                safety_enforcement_digest=canonical,
                authority_binding_digest=canonical,
                origin_trust_digest=canonical,
                replay_audit_digest=canonical,
                static_governance_digest=canonical,
                # egress_certification_digest deliberately omitted
            )
        assert exc_info.value.evidence.first_mismatched_field == "egress_certification_digest"

    def test_a3_hitl_emitted_when_not_required(self) -> None:
        ctx = _ctx()  # L2_BOUNDED — HITL not required
        canonical = ctx.digest()
        with pytest.raises(L5GovernanceContextMismatchError) as exc_info:
            assert_l5_cross_child_match(
                canonical_context=ctx,
                safety_enforcement_digest=canonical,
                authority_binding_digest=canonical,
                origin_trust_digest=canonical,
                replay_audit_digest=canonical,
                static_governance_digest=canonical,
                hitl_reclearance_digest=canonical,  # unexpected
            )
        assert exc_info.value.evidence.first_mismatched_field == "hitl_reclearance_digest"
        assert "conditional_digest_unexpected" in exc_info.value.evidence.reason

    def test_a4_egress_emitted_when_not_required(self) -> None:
        ctx = _ctx()  # READ_ONLY — egress not required
        canonical = ctx.digest()
        with pytest.raises(L5GovernanceContextMismatchError) as exc_info:
            assert_l5_cross_child_match(
                canonical_context=ctx,
                safety_enforcement_digest=canonical,
                authority_binding_digest=canonical,
                origin_trust_digest=canonical,
                replay_audit_digest=canonical,
                static_governance_digest=canonical,
                egress_certification_digest=canonical,  # unexpected
            )
        assert exc_info.value.evidence.first_mismatched_field == "egress_certification_digest"
        assert "conditional_digest_unexpected" in exc_info.value.evidence.reason


class TestAntiBypass:
    def test_b1_substring_compare_refused(self) -> None:
        """Gate uses bit-for-bit compare; truncated digest must fail."""
        ctx = _ctx()
        canonical = ctx.digest()
        truncated = canonical[:60] + "abcd"  # changes last 4 hex chars
        with pytest.raises(L5GovernanceContextMismatchError):
            assert_l5_cross_child_match(
                canonical_context=ctx,
                safety_enforcement_digest=canonical,
                authority_binding_digest=truncated,
                origin_trust_digest=canonical,
                replay_audit_digest=canonical,
                static_governance_digest=canonical,
            )

    def test_b3_malformed_digest_refused(self) -> None:
        ctx = _ctx()
        canonical = ctx.digest()
        with pytest.raises(L5GovernanceContextMismatchError) as exc_info:
            assert_l5_cross_child_match(
                canonical_context=ctx,
                safety_enforcement_digest="not-a-digest",
                authority_binding_digest=canonical,
                origin_trust_digest=canonical,
                replay_audit_digest=canonical,
                static_governance_digest=canonical,
            )
        assert exc_info.value.evidence.first_mismatched_field == "safety_enforcement_digest"
        assert "64-char hex" in exc_info.value.evidence.reason
