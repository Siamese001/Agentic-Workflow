"""Tests for guardrail registry (G9), risk-tier control matrix (G10), promotion receipt (G11)."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.v5 import (
    PromotionReceipt,
    all_families,
    apply_band_controls,
    assert_band_monotonicity,
    get_family,
    hard_constraint_family_ids,
)
from agentic_core.L5_safety.v5.types import (
    GuardrailFamilyId,
    PromotionPlane,
    RiskTierBandV5,
)


# G9 — Guardrail family registry ---------------------------------------------
def test_guardrail_registry_has_all_18_families() -> None:
    assert len(all_families()) == 18
    ids = {f.id for f in all_families()}
    assert ids == set(GuardrailFamilyId)


def test_hard_constraint_families_are_six() -> None:
    """`guardrail_families.md` §5 — F-01, F-02, F-04, F-05, F-17, F-18."""
    hard = set(hard_constraint_family_ids())
    expected = {
        GuardrailFamilyId.F01_MODERATION,
        GuardrailFamilyId.F02_SECRET_KEYS,
        GuardrailFamilyId.F04_JAILBREAK,
        GuardrailFamilyId.F05_PROMPT_INJECTION,
        GuardrailFamilyId.F17_SUPPLY_CHAIN_DIGEST,
        GuardrailFamilyId.F18_THREAT_INTEL_SIGNATURE,
    }
    assert hard == expected


def test_get_family_unknown_id_raises() -> None:
    # Build a fake enum-shaped object with a value not in registry → ValueError
    with pytest.raises((ValueError, KeyError)):
        get_family(None)  # type: ignore[arg-type]


def test_family_serializes_with_required_keys() -> None:
    rec = get_family(GuardrailFamilyId.F01_MODERATION)
    d = rec.to_dict()
    for k in (
        "id",
        "name",
        "stage",
        "bank",
        "evaluator_kind",
        "risk_tier_activation",
        "hard_constraint",
        "remediable_when_false",
    ):
        assert k in d
    assert d["id"] == "F-01"
    assert d["hard_constraint"] is True


# G10 — Risk-tier control matrix ---------------------------------------------
def test_band_controls_low_moderate_high_present() -> None:
    low = apply_band_controls(RiskTierBandV5.LOW)
    mod = apply_band_controls(RiskTierBandV5.MODERATE)
    high = apply_band_controls(RiskTierBandV5.HIGH)
    assert low.band == RiskTierBandV5.LOW
    assert mod.band == RiskTierBandV5.MODERATE
    assert high.band == RiskTierBandV5.HIGH


def test_band_monotonicity_holds() -> None:
    """Restrictiveness must increase LOW → MODERATE → HIGH."""
    assert_band_monotonicity()


def test_high_band_requires_hitl_and_guard_model() -> None:
    high = apply_band_controls(RiskTierBandV5.HIGH)
    assert high.hitl_required is True
    assert high.guard_model_review_required is True
    assert high.capability_token_single_use_default is True


def test_low_band_does_not_require_hitl() -> None:
    low = apply_band_controls(RiskTierBandV5.LOW)
    assert low.hitl_required is False


def test_critical_band_collapses_to_high_strictness() -> None:
    crit = apply_band_controls(RiskTierBandV5.CRITICAL)
    high = apply_band_controls(RiskTierBandV5.HIGH)
    # CRITICAL is at least as strict as HIGH
    assert crit.delegation_depth_max <= high.delegation_depth_max
    assert crit.capability_token_ttl_max_seconds <= high.capability_token_ttl_max_seconds


# G11 — Promotion receipt -----------------------------------------------------
def test_promotion_receipt_rejects_same_version() -> None:
    with pytest.raises(ValueError, match="must differ"):
        PromotionReceipt(
            receipt_id="r",
            plane=PromotionPlane.CALIBRATION,
            candidate_policy_version="v1",
            current_policy_version="v1",
            regression_pack_ref="rp",
            rollback_plan_ref="rb",
            owner_approval_ref="ow",
            uwg_admission_ref="",
        )


def test_promotion_receipt_requires_regression_pack_unless_veto() -> None:
    # Non-veto without regression pack → ValueError
    with pytest.raises(ValueError, match="regression_pack_ref"):
        PromotionReceipt(
            receipt_id="r",
            plane=PromotionPlane.CALIBRATION,
            candidate_policy_version="v2",
            current_policy_version="v1",
            regression_pack_ref="",  # missing
            rollback_plan_ref="rb",
            owner_approval_ref="ow",
            uwg_admission_ref="",
        )


def test_promotion_receipt_veto_requires_reason() -> None:
    with pytest.raises(ValueError, match="veto_reason"):
        PromotionReceipt(
            receipt_id="r",
            plane=PromotionPlane.ASSURANCE,
            candidate_policy_version="v2",
            current_policy_version="v1",
            regression_pack_ref="",
            rollback_plan_ref="",
            owner_approval_ref="",
            uwg_admission_ref="",
            veto=True,
            veto_reason="",  # missing
        )


def test_promotion_receipt_admitted_only_when_uwg_committed_and_no_veto() -> None:
    pending = PromotionReceipt(
        receipt_id="r",
        plane=PromotionPlane.CALIBRATION,
        candidate_policy_version="v2",
        current_policy_version="v1",
        regression_pack_ref="rp",
        rollback_plan_ref="rb",
        owner_approval_ref="ow",
        uwg_admission_ref="",  # pending UWG
    )
    assert pending.admitted is False

    admitted = PromotionReceipt(
        receipt_id="r",
        plane=PromotionPlane.CALIBRATION,
        candidate_policy_version="v2",
        current_policy_version="v1",
        regression_pack_ref="rp",
        rollback_plan_ref="rb",
        owner_approval_ref="ow",
        uwg_admission_ref="uwg-1",
    )
    assert admitted.admitted is True
