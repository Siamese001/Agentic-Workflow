"""Unit tests for agentic_core.L2_execution.healers.healing_cascade_registry.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 core module.
``healing_cascade_registry`` is the SSOT for the healing/remediation ladder
(control_surface="healing"). Coverage targets the frozen ``HealingTier`` dataclass,
the ordered ``HEALING_CASCADE`` table, the name/model-id lookup helpers, and the
``build_healing_evidence_stamp`` validator (ValueError on unknown tier/action).
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L2_execution.healers.healing_cascade_registry import (
    CONTROL_SURFACE,
    DETERMINISTIC_TIER,
    GEMINI_FLASH_TIER,
    GEMINI_PRO_TIER,
    HEALING_CASCADE,
    HEALING_EVIDENCE_ROOT,
    HealingTier,
    PURPOSE,
    QWEN_TIER,
    build_healing_evidence_stamp,
    get_healing_tier,
    get_tier_by_model_id,
    is_healing_model_id,
)


class TestSurfaceLabels:
    def test_control_surface_is_healing(self) -> None:
        assert CONTROL_SURFACE == "healing"
        assert PURPOSE == "remediation"

    def test_evidence_root_isolated_from_certification(self) -> None:
        assert HEALING_EVIDENCE_ROOT == "artifacts/healing"
        assert "certification" not in HEALING_EVIDENCE_ROOT


class TestCascadeTable:
    def test_cascade_order_and_names(self) -> None:
        assert tuple(t.tier for t in HEALING_CASCADE) == (
            "deterministic",
            "qwen",
            "gemini_flash",
            "gemini_pro",
        )

    def test_cascade_entries_identity(self) -> None:
        assert HEALING_CASCADE == (DETERMINISTIC_TIER, QWEN_TIER, GEMINI_FLASH_TIER, GEMINI_PRO_TIER)

    def test_deterministic_tier_has_no_model(self) -> None:
        assert DETERMINISTIC_TIER.model_id is None
        assert DETERMINISTIC_TIER.confidence_band == "high"

    def test_tier_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            DETERMINISTIC_TIER.tier = "x"  # type: ignore[misc]

    def test_tier_constructible(self) -> None:
        t = HealingTier(tier="custom", model_id="m", confidence_band="medium")
        assert t.model_id == "m"


class TestGetHealingTier:
    @pytest.mark.parametrize(
        "name", ["deterministic", "qwen", "gemini_flash", "gemini_pro"]
    )
    def test_known_names(self, name: str) -> None:
        tier = get_healing_tier(name)
        assert tier is not None and tier.tier == name

    def test_case_insensitive(self) -> None:
        assert get_healing_tier("  QWEN  ") is QWEN_TIER

    def test_empty_returns_none(self) -> None:
        assert get_healing_tier("") is None

    def test_unknown_returns_none(self) -> None:
        assert get_healing_tier("nonexistent_tier") is None


class TestModelIdHelpers:
    def test_is_healing_model_id_true_for_qwen(self) -> None:
        assert is_healing_model_id(QWEN_TIER.model_id) is True

    def test_is_healing_model_id_false_for_none(self) -> None:
        assert is_healing_model_id(None) is False
        assert is_healing_model_id("") is False

    def test_is_healing_model_id_false_for_unknown(self) -> None:
        assert is_healing_model_id("totally-made-up-model") is False

    def test_get_tier_by_model_id_qwen(self) -> None:
        tier = get_tier_by_model_id(QWEN_TIER.model_id)
        assert tier is QWEN_TIER

    def test_get_tier_by_model_id_none_for_deterministic_sentinel(self) -> None:
        # deterministic tier has model_id=None and is intentionally not matched.
        assert get_tier_by_model_id(None) is None

    def test_get_tier_by_model_id_unknown(self) -> None:
        assert get_tier_by_model_id("unknown") is None


class TestEvidenceStamp:
    def test_stamp_minimal(self) -> None:
        stamp = build_healing_evidence_stamp(healing_tier="qwen", healing_action="repair")
        assert stamp["control_surface"] == "healing"
        assert stamp["purpose"] == "remediation"
        assert stamp["healing_tier"] == "qwen"
        assert stamp["healing_model_id"] == QWEN_TIER.model_id
        assert stamp["healing_confidence_band"] == "medium_high"
        assert stamp["healing_action"] == "repair"
        assert "healing_evidence_ref" not in stamp

    def test_stamp_with_evidence_ref(self) -> None:
        stamp = build_healing_evidence_stamp(
            healing_tier="deterministic",
            healing_action="deterministic_fix",
            healing_evidence_ref="artifacts/healing/x.json",
        )
        assert stamp["healing_evidence_ref"] == "artifacts/healing/x.json"
        assert stamp["healing_model_id"] is None

    def test_confidence_band_override(self) -> None:
        stamp = build_healing_evidence_stamp(
            healing_tier="qwen",
            healing_action="propose",
            confidence_band_override="low",
        )
        assert stamp["healing_confidence_band"] == "low"

    def test_unknown_tier_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown healing_tier"):
            build_healing_evidence_stamp(healing_tier="bogus", healing_action="repair")

    @pytest.mark.parametrize("action", ["propose", "repair", "escalate", "deterministic_fix"])
    def test_valid_actions(self, action: str) -> None:
        stamp = build_healing_evidence_stamp(healing_tier="qwen", healing_action=action)
        assert stamp["healing_action"] == action

    def test_unknown_action_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown healing_action"):
            build_healing_evidence_stamp(healing_tier="qwen", healing_action="delete")
