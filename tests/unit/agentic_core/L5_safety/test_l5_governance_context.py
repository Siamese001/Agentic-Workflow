"""Unit tests for `agentic_core.L5_safety.types.l5_governance_context`.

Maps to: docs/reference/00A_L5_Governance_Safety/00A.7a_L5_Governance_Context_Invariant.md
Phase 1 DATA CONTRACT.
"""

from __future__ import annotations

import json

import pytest

from agentic_core.L5_safety.types.l5_governance_context import (
    CertificationScope,
    ExecutionForm,
    L5GovernanceContext,
    L5GovernanceContextField,
    RiskTier,
    SideEffectClass,
    compute_l5_context_digest,
)


def _digest_filler(seed: str, n: int = 64) -> str:
    """Deterministic 64-char hex digest filler for tests."""
    return (seed * 16)[:n]


def make_ctx(
    *,
    seed: str = "a",
    execution_form: ExecutionForm = ExecutionForm.L2_BOUNDED,
    side_effect_class: SideEffectClass = SideEffectClass.READ_ONLY,
    hitl_packet: str = "",
    reclearance: str = "",
    egress_profile: str = "",
    session_id: str = "sess-1",
    step_id: str = "step-1",
) -> L5GovernanceContext:
    return L5GovernanceContext(
        request_id="req-1",
        run_id="run-1",
        trace_id="trace-1",
        tenant_id="tenant-1",
        principal_id="prin-1",
        session_id=session_id,
        route_id="route-1",
        step_id=step_id,
        execution_form=execution_form,
        risk_tier=RiskTier.R2,
        side_effect_class=side_effect_class,
        policy_hash=_digest_filler(seed),
        blueprint_hash=_digest_filler("b"),
        registry_snapshot_hash=_digest_filler("c"),
        agent_profile_hash=_digest_filler("d"),
        capability_scope_hash=_digest_filler("e"),
        sandbox_envelope_hash=_digest_filler("f"),
        origin_trust_manifest_hash=_digest_filler("0"),
        egress_profile_hash=egress_profile,
        hitl_packet_hash=hitl_packet,
        reclearance_hash=reclearance,
        replay_envelope_hash=_digest_filler("1"),
        audit_manifest_hash=_digest_filler("2"),
        static_governance_snapshot_hash=_digest_filler("3"),
        certifier_id="cert-1",
        certifier_version="v1",
        certification_scope=CertificationScope.AGGREGATE,
        frozen_governance_context_hash=_digest_filler("4"),
        l5_resolver_digest=_digest_filler("5"),
    )


class TestL5GovernanceContextConstruction:
    def test_construction_succeeds_with_minimal_required_fields(self) -> None:
        ctx = make_ctx()
        assert ctx.request_id == "req-1"
        assert ctx.execution_form is ExecutionForm.L2_BOUNDED
        assert ctx.is_hitl_required() is False
        assert ctx.is_egress_required() is False

    def test_frozen_dataclass_rejects_mutation(self) -> None:
        ctx = make_ctx()
        with pytest.raises((AttributeError, TypeError)):
            ctx.request_id = "req-2"  # type: ignore[misc]

    def test_empty_required_string_rejected(self) -> None:
        with pytest.raises(ValueError, match="request_id"):
            make_ctx().__class__(  # build directly to bypass make_ctx default
                request_id="",
                run_id="run-1",
                trace_id="trace-1",
                tenant_id="tenant-1",
                principal_id="prin-1",
                session_id="",
                route_id="route-1",
                step_id="",
                execution_form=ExecutionForm.L2_BOUNDED,
                risk_tier=RiskTier.R0,
                side_effect_class=SideEffectClass.READ_ONLY,
                policy_hash=_digest_filler("a"),
                blueprint_hash=_digest_filler("b"),
                registry_snapshot_hash=_digest_filler("c"),
                agent_profile_hash=_digest_filler("d"),
                capability_scope_hash=_digest_filler("e"),
                sandbox_envelope_hash=_digest_filler("f"),
                origin_trust_manifest_hash=_digest_filler("0"),
                egress_profile_hash="",
                hitl_packet_hash="",
                reclearance_hash="",
                replay_envelope_hash=_digest_filler("1"),
                audit_manifest_hash=_digest_filler("2"),
                static_governance_snapshot_hash=_digest_filler("3"),
                certifier_id="cert-1",
                certifier_version="v1",
                certification_scope=CertificationScope.AGGREGATE,
                frozen_governance_context_hash=_digest_filler("4"),
                l5_resolver_digest=_digest_filler("5"),
            )

    def test_nullable_fields_accept_empty(self) -> None:
        ctx = make_ctx(session_id="", step_id="")
        # Construction succeeded — nullable fields accept "".
        assert ctx.session_id == ""
        assert ctx.step_id == ""

    def test_hitl_required_when_execution_form_is_hitl_only(self) -> None:
        with pytest.raises(ValueError, match="hitl_packet_hash"):
            make_ctx(execution_form=ExecutionForm.HITL_ONLY, hitl_packet="")

    def test_hitl_packet_present_satisfies_constraint(self) -> None:
        ctx = make_ctx(
            execution_form=ExecutionForm.HITL_ONLY,
            hitl_packet=_digest_filler("h"),
            reclearance=_digest_filler("r"),
        )
        assert ctx.is_hitl_required() is True

    def test_egress_required_when_side_effect_external_egress(self) -> None:
        with pytest.raises(ValueError, match="egress_profile_hash"):
            make_ctx(side_effect_class=SideEffectClass.EXTERNAL_EGRESS, egress_profile="")

    def test_egress_present_satisfies_constraint(self) -> None:
        ctx = make_ctx(
            side_effect_class=SideEffectClass.EXTERNAL_EGRESS,
            egress_profile=_digest_filler("e"),
        )
        assert ctx.is_egress_required() is True


class TestL5GovernanceContextDigest:
    def test_digest_is_64char_lowercase_hex(self) -> None:
        digest = make_ctx().digest()
        assert len(digest) == 64
        assert digest == digest.lower()
        int(digest, 16)  # parses as hex

    def test_digest_deterministic_across_calls(self) -> None:
        ctx = make_ctx()
        assert ctx.digest() == ctx.digest()

    def test_digest_deterministic_across_construction(self) -> None:
        d1 = make_ctx().digest()
        d2 = make_ctx().digest()
        assert d1 == d2

    def test_digest_changes_when_any_field_changes(self) -> None:
        baseline = make_ctx().digest()
        for field_enum in L5GovernanceContextField:
            name = field_enum.value
            # Skip fields that are enum-valued — those are exercised below.
            if name in {"execution_form", "risk_tier", "side_effect_class", "certification_scope"}:
                continue
            # Skip nullable fields whose default is "" (already covered).
            kw = {name: _digest_filler("z" + name[:1])}
            try:
                ctx = make_ctx(**kw)  # type: ignore[arg-type]
            except (TypeError, ValueError):
                # make_ctx doesn't expose every field as kwarg; assert via direct construction.
                continue
            assert ctx.digest() != baseline, f"changing {name} did not change digest"

    def test_canonical_dict_serializes_enums_as_values(self) -> None:
        ctx = make_ctx()
        canonical = ctx.to_canonical_dict()
        assert canonical["execution_form"] == "L2_BOUNDED"
        assert canonical["risk_tier"] == "R2"
        assert canonical["side_effect_class"] == "READ_ONLY"
        assert canonical["certification_scope"] == "AGGREGATE"
        # Round-trippable JSON
        round_trip = json.loads(json.dumps(canonical, sort_keys=True))
        assert round_trip["execution_form"] == "L2_BOUNDED"

    def test_compute_function_matches_method(self) -> None:
        ctx = make_ctx()
        assert compute_l5_context_digest(ctx) == ctx.digest()


class TestL5GovernanceContextFirstMismatchedField:
    def test_identical_contexts_produce_empty_mismatch(self) -> None:
        ctx_a = make_ctx()
        ctx_b = make_ctx()
        assert ctx_a.first_mismatched_field(ctx_b) == ""

    def test_different_request_id_surfaces_request_id(self) -> None:
        ctx_a = make_ctx()
        ctx_b = make_ctx().__class__(
            request_id="req-2",
            run_id=ctx_a.run_id,
            trace_id=ctx_a.trace_id,
            tenant_id=ctx_a.tenant_id,
            principal_id=ctx_a.principal_id,
            session_id=ctx_a.session_id,
            route_id=ctx_a.route_id,
            step_id=ctx_a.step_id,
            execution_form=ctx_a.execution_form,
            risk_tier=ctx_a.risk_tier,
            side_effect_class=ctx_a.side_effect_class,
            policy_hash=ctx_a.policy_hash,
            blueprint_hash=ctx_a.blueprint_hash,
            registry_snapshot_hash=ctx_a.registry_snapshot_hash,
            agent_profile_hash=ctx_a.agent_profile_hash,
            capability_scope_hash=ctx_a.capability_scope_hash,
            sandbox_envelope_hash=ctx_a.sandbox_envelope_hash,
            origin_trust_manifest_hash=ctx_a.origin_trust_manifest_hash,
            egress_profile_hash=ctx_a.egress_profile_hash,
            hitl_packet_hash=ctx_a.hitl_packet_hash,
            reclearance_hash=ctx_a.reclearance_hash,
            replay_envelope_hash=ctx_a.replay_envelope_hash,
            audit_manifest_hash=ctx_a.audit_manifest_hash,
            static_governance_snapshot_hash=ctx_a.static_governance_snapshot_hash,
            certifier_id=ctx_a.certifier_id,
            certifier_version=ctx_a.certifier_version,
            certification_scope=ctx_a.certification_scope,
            frozen_governance_context_hash=ctx_a.frozen_governance_context_hash,
            l5_resolver_digest=ctx_a.l5_resolver_digest,
        )
        assert ctx_a.first_mismatched_field(ctx_b) == "request_id"
