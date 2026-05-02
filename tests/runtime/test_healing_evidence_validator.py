"""Tests for the healing-side evidence validator and registry stamp.

Per operator directive 2026-05-01 14:45 UTC-04:00. Verifies that:

  - The healing validator accepts well-formed healing records.
  - The healing validator REJECTS judge / panel attestations.
  - Deterministic tier requires healing_model_id=None.
  - Other tiers require healing_model_id non-empty.
  - Each missing / mismatched field surfaces its own reject code.
  - ``build_healing_evidence_stamp`` emits the canonical 6/7-field shape.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.healers.healing_cascade_registry import (
    DETERMINISTIC_MODEL_SENTINEL,
    GEMINI_FLASH_MODEL_ID,
    GEMINI_PRO_MODEL_ID,
    HEALING_CASCADE,
    QWEN_LOCAL_MODEL_ID,
    build_healing_evidence_stamp,
    get_tier_by_model_id,
    resolve_healing_gemini_pro_model_id,
)
from agentic_core.L2_execution.healers.healing_evidence_validator import (
    HealingEvidenceRejectReason,
    validate_healing_evidence,
)


def _mk_healing_record(**overrides):
    base = {
        "control_surface": "healing",
        "purpose": "remediation",
        "healing_tier": "qwen",
        "healing_model_id": QWEN_LOCAL_MODEL_ID,
        "healing_confidence_band": "medium_high",
        "healing_action": "repair",
        "healing_evidence_ref": "artifacts/healing/run-1234/repair.json",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Acceptance — every canonical tier
# ---------------------------------------------------------------------------


class TestAcceptValidHealingRecords:
    def test_qwen_repair_accepted(self):
        v = validate_healing_evidence(_mk_healing_record())
        assert v.accepted is True
        assert v.reason_codes == ()

    def test_gemini_flash_propose_accepted(self):
        v = validate_healing_evidence(_mk_healing_record(
            healing_tier="gemini_flash",
            healing_model_id=GEMINI_FLASH_MODEL_ID,
            healing_confidence_band="medium",
            healing_action="propose",
        ))
        assert v.accepted is True

    def test_gemini_pro_escalate_accepted(self):
        v = validate_healing_evidence(_mk_healing_record(
            healing_tier="gemini_pro",
            healing_model_id=GEMINI_PRO_MODEL_ID,
            healing_confidence_band="low_confidence_escalation",
            healing_action="escalate",
        ))
        assert v.accepted is True

    def test_deterministic_with_null_model_id_accepted(self):
        v = validate_healing_evidence(_mk_healing_record(
            healing_tier="deterministic",
            healing_model_id=None,
            healing_confidence_band="high",
            healing_action="deterministic_fix",
        ))
        assert v.accepted is True

    def test_deterministic_with_absent_model_id_accepted(self):
        rec = _mk_healing_record(
            healing_tier="deterministic",
            healing_confidence_band="high",
            healing_action="deterministic_fix",
        )
        rec.pop("healing_model_id")
        v = validate_healing_evidence(rec)
        assert v.accepted is True

    def test_evidence_ref_optional(self):
        rec = _mk_healing_record()
        rec.pop("healing_evidence_ref")
        v = validate_healing_evidence(rec)
        assert v.accepted is True


# ---------------------------------------------------------------------------
# REJECTION: judge / panel attestations must NOT be accepted
# ---------------------------------------------------------------------------


class TestRejectsJudgeAndPanel:
    def test_judge_panel_rejected_outright(self):
        """Symmetric mirror of the RTC-REQ-056 gate: a panel attestation
        with control_surface='llm_as_judge' MUST be rejected by the
        healing validator."""
        panel = {
            "control_surface": "llm_as_judge",
            "purpose": "certification",
            "certification_scope": "RTC-REQ-056",
            "judge_mode": "consensus_jury",
            "quorum_rule": "all_required_safe",
            "jurors": [],
        }
        v = validate_healing_evidence(panel)
        assert v.accepted is False
        assert (
            HealingEvidenceRejectReason.REJECT_NOT_HEALING_SURFACE
            in v.reason_codes
        )

    def test_missing_control_surface_rejected(self):
        rec = _mk_healing_record()
        rec.pop("control_surface")
        v = validate_healing_evidence(rec)
        assert v.accepted is False
        assert (
            HealingEvidenceRejectReason.REJECT_NOT_HEALING_SURFACE
            in v.reason_codes
        )

    def test_experimental_surface_rejected(self):
        v = validate_healing_evidence(_mk_healing_record(
            control_surface="experimental"
        ))
        assert v.accepted is False
        assert (
            HealingEvidenceRejectReason.REJECT_NOT_HEALING_SURFACE
            in v.reason_codes
        )


# ---------------------------------------------------------------------------
# Per-field rejections
# ---------------------------------------------------------------------------


class TestPerFieldRejections:
    def test_purpose_mismatch_rejected(self):
        v = validate_healing_evidence(_mk_healing_record(purpose="certification"))
        assert v.accepted is False
        assert (
            HealingEvidenceRejectReason.REJECT_PURPOSE_MISMATCH
            in v.reason_codes
        )

    def test_unknown_tier_rejected(self):
        v = validate_healing_evidence(_mk_healing_record(
            healing_tier="quantum_repair",
        ))
        assert v.accepted is False
        assert (
            HealingEvidenceRejectReason.REJECT_UNKNOWN_TIER
            in v.reason_codes
        )

    def test_missing_tier_rejected(self):
        rec = _mk_healing_record()
        rec.pop("healing_tier")
        v = validate_healing_evidence(rec)
        assert v.accepted is False
        assert (
            HealingEvidenceRejectReason.REJECT_TIER_MISSING
            in v.reason_codes
        )

    def test_unknown_action_rejected(self):
        v = validate_healing_evidence(_mk_healing_record(
            healing_action="invent_a_fix"
        ))
        assert v.accepted is False
        assert (
            HealingEvidenceRejectReason.REJECT_UNKNOWN_ACTION
            in v.reason_codes
        )

    def test_missing_action_rejected(self):
        rec = _mk_healing_record()
        rec.pop("healing_action")
        v = validate_healing_evidence(rec)
        assert v.accepted is False
        assert (
            HealingEvidenceRejectReason.REJECT_ACTION_MISSING
            in v.reason_codes
        )

    def test_missing_confidence_band_rejected(self):
        rec = _mk_healing_record()
        rec.pop("healing_confidence_band")
        v = validate_healing_evidence(rec)
        assert v.accepted is False
        assert (
            HealingEvidenceRejectReason.REJECT_CONFIDENCE_BAND_MISSING
            in v.reason_codes
        )

    def test_qwen_with_missing_model_id_rejected(self):
        rec = _mk_healing_record(healing_tier="qwen")
        rec["healing_model_id"] = None
        v = validate_healing_evidence(rec)
        assert v.accepted is False
        assert (
            HealingEvidenceRejectReason.REJECT_MODEL_ID_MISSING
            in v.reason_codes
        )

    def test_deterministic_with_non_null_model_id_rejected(self):
        v = validate_healing_evidence(_mk_healing_record(
            healing_tier="deterministic",
            healing_model_id="some-stray-model",
            healing_action="deterministic_fix",
            healing_confidence_band="high",
        ))
        assert v.accepted is False
        assert (
            HealingEvidenceRejectReason.REJECT_DETERMINISTIC_MUST_HAVE_NULL_MODEL
            in v.reason_codes
        )


class TestPayloadShape:
    @pytest.mark.parametrize("payload", [None, "string", 42, [1, 2, 3]])
    def test_non_dict_payload_rejected(self, payload):
        v = validate_healing_evidence(payload)
        assert v.accepted is False
        assert (
            HealingEvidenceRejectReason.REJECT_PAYLOAD_NOT_DICT
            in v.reason_codes
        )


# ---------------------------------------------------------------------------
# Registry — build_healing_evidence_stamp + helpers
# ---------------------------------------------------------------------------


class TestBuildHealingEvidenceStamp:
    def test_qwen_stamp_shape(self):
        s = build_healing_evidence_stamp(
            healing_tier="qwen",
            healing_action="repair",
        )
        assert s["control_surface"] == "healing"
        assert s["purpose"] == "remediation"
        assert s["healing_tier"] == "qwen"
        assert s["healing_model_id"] == QWEN_LOCAL_MODEL_ID
        assert s["healing_confidence_band"] == "medium_high"
        assert s["healing_action"] == "repair"
        assert "healing_evidence_ref" not in s  # optional, omitted

    def test_with_evidence_ref(self):
        s = build_healing_evidence_stamp(
            healing_tier="deterministic",
            healing_action="deterministic_fix",
            healing_evidence_ref="artifacts/healing/run-1/det.json",
        )
        assert s["healing_evidence_ref"] == "artifacts/healing/run-1/det.json"
        assert s["healing_model_id"] is None
        assert s["healing_confidence_band"] == "high"

    def test_stamp_passes_validator_round_trip(self):
        """Anything build_healing_evidence_stamp produces must pass
        validate_healing_evidence — the helper IS the canonical shape."""
        for tier in HEALING_CASCADE:
            action = (
                "deterministic_fix" if tier.tier == "deterministic" else "repair"
            )
            stamp = build_healing_evidence_stamp(
                healing_tier=tier.tier,
                healing_action=action,
                healing_evidence_ref=f"artifacts/healing/{tier.tier}.json",
            )
            v = validate_healing_evidence(stamp)
            assert v.accepted is True, (
                f"tier={tier.tier} stamp rejected: {v.reason_codes}"
            )

    def test_unknown_tier_raises(self):
        with pytest.raises(ValueError, match="unknown healing_tier"):
            build_healing_evidence_stamp(
                healing_tier="quantum",
                healing_action="repair",
            )

    def test_unknown_action_raises(self):
        with pytest.raises(ValueError, match="unknown healing_action"):
            build_healing_evidence_stamp(
                healing_tier="qwen",
                healing_action="invent_a_fix",
            )

    def test_confidence_band_override(self):
        s = build_healing_evidence_stamp(
            healing_tier="qwen",
            healing_action="repair",
            confidence_band_override="custom_band",
        )
        assert s["healing_confidence_band"] == "custom_band"


class TestGetTierByModelId:
    def test_qwen_lookup(self):
        t = get_tier_by_model_id(QWEN_LOCAL_MODEL_ID)
        assert t is not None
        assert t.tier == "qwen"

    def test_deterministic_sentinel_excluded_from_lookup(self):
        # Deterministic has model_id=None; calling with the sentinel string
        # is NOT how callers should look it up.
        assert get_tier_by_model_id(None) is None
        assert get_tier_by_model_id("") is None

    def test_unknown_model_id(self):
        assert get_tier_by_model_id("definitely-not-a-real-model") is None


class TestResolveHealingGeminiPro:
    def test_default_when_no_override(self, monkeypatch):
        monkeypatch.delenv("HEALING_GEMINI_MODEL", raising=False)
        assert resolve_healing_gemini_pro_model_id() == GEMINI_PRO_MODEL_ID

    def test_override_takes_effect(self, monkeypatch):
        monkeypatch.setenv("HEALING_GEMINI_MODEL", "gemini-experimental-pro")
        assert resolve_healing_gemini_pro_model_id() == "gemini-experimental-pro"

    def test_empty_override_uses_default(self, monkeypatch):
        monkeypatch.setenv("HEALING_GEMINI_MODEL", "   ")
        assert resolve_healing_gemini_pro_model_id() == GEMINI_PRO_MODEL_ID
