"""Control-surface separation tests — healing vs llm_as_judge.

Per operator directive 2026-05-01 14:15 UTC-04:00. Verifies that:
  - Healing outputs (any tier) CANNOT satisfy RTC-REQ-056.
  - Missing control_surface is rejected.
  - Mismatched control_surface is rejected.
  - Valid three-juror panel is accepted.
  - Rejected providers stay rejected (regression).
  - Spoofed healing Gemini Pro artifact cannot leak through even if it
    falsely stamps ``control_surface = "llm_as_judge"``.

Reuses the fixtures from test_rtc_req_056_panel_gate.py via direct
import to avoid duplicating large attestation bodies.
"""

from __future__ import annotations

from typing import Any

import pytest

# Reuse the baseline attestation fixture from the existing panel-gate suite
from tests.runtime.test_rtc_req_056_panel_gate import (
    _mk_anthropic_safe,
    _mk_gemini_safe,
    _mk_juror_entry,
    _mk_openai_safe,
    _mk_valid_attestation,
)
from tools.certification.safety.rtc_req_056_gate import (
    validate_panel_attestation,
)
from tools.certification.safety.rtc_req_056_panel import (
    ANTHROPIC_JUROR,
    GEMINI_JUROR,
    OPENAI_JUROR,
    RejectReason,
    classify_healing_tier_for_reject,
)


# ---------------------------------------------------------------------------
# Helpers — build healing-origin attestations to assert rejection
# ---------------------------------------------------------------------------


def _mk_healing_doc(
    *,
    healing_tier: str,
    model_id: str | None,
    spoof_surface: str | None = None,
) -> dict[str, Any]:
    """Build a healing-origin document shaped vaguely like an
    attestation (SAFE-like outputs) that tries to certify RTC-REQ-056.

    If ``spoof_surface`` is provided it is stamped at top-level instead
    of the honest ``"healing"`` — used by the spoofing test.
    """
    surface = spoof_surface if spoof_surface is not None else "healing"
    doc: dict[str, Any] = {
        "attestation_schema_version": 3,
        "certification_scope": "RTC-REQ-056",
        "control_surface": surface,
        "purpose": "remediation",
        "healing_tier": healing_tier,
        "healing_model_id": model_id,
        "healing_confidence_band": "high",
        "healing_action": "propose",
        "healing_evidence_ref": "artifacts/healing/fake/run.json",
        "judge_mode": "consensus_jury",
        "quorum_rule": "all_required_safe",
        "required_juror_count": 3,
        "invoked_juror_count": 1,
        "final_consensus_verdict": "SAFE",
        "final_safe_reuse_allow": True,
        "final_x3_disposition": "X3D",
        "rubric_hash_sha256": "aa" * 32,
        "request_hash_sha256": "bb" * 32,
        "cache_candidate_hash_sha256": "cc" * 32,
        "panel_response_hash_sha256": "dd" * 32,
        "provider_panel_match_status": "PASS",
        "model_panel_match_status": "PASS",
        "mock_safe_used_any": False,
        "deterministic_proof_stage_used_any": False,
        "created_at_utc": "2026-05-01T18:15:00.000000Z",
        "artifact_hash": "ee" * 32,
        "jurors": [],
    }
    return doc


# ---------------------------------------------------------------------------
# 1–4. Healing tier rejection (deterministic / qwen / gemini_flash / gemini_pro)
# ---------------------------------------------------------------------------


class TestHealingTierRejections:
    def test_healing_deterministic_safelike_output_rejected(self):
        doc = _mk_healing_doc(healing_tier="deterministic", model_id=None)
        result = validate_panel_attestation(doc)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_DETERMINISTIC_HEALING_FOR_RTC_REQ_056
            in result.reason_codes
        )

    def test_healing_qwen_safelike_output_rejected(self):
        doc = _mk_healing_doc(
            healing_tier="qwen",
            model_id="Qwen/Qwen2.5-32B-Instruct-AWQ",
        )
        result = validate_panel_attestation(doc)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_QWEN_HEALING_FOR_RTC_REQ_056
            in result.reason_codes
        )

    def test_healing_gemini_flash_safelike_output_rejected(self):
        doc = _mk_healing_doc(
            healing_tier="gemini_flash",
            model_id="gemini-3-flash-preview",
        )
        result = validate_panel_attestation(doc)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_GEMINI_FLASH_HEALING_FOR_RTC_REQ_056
            in result.reason_codes
        )

    def test_healing_gemini_pro_output_rejected_unless_panel_juror(self):
        # Healing gemini_pro doc — same model string as panel juror, but
        # control_surface=healing must still be rejected.
        doc = _mk_healing_doc(
            healing_tier="gemini_pro",
            model_id=GEMINI_JUROR.model_id,
        )
        result = validate_panel_attestation(doc)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_HEALING_GEMINI_PRO_NOT_PANEL_JUROR
            in result.reason_codes
        )

        # Contrast: Gemini Pro appearing as the registered juror inside
        # a valid panel attestation is accepted.
        panel = _mk_valid_attestation()
        panel_result = validate_panel_attestation(panel)
        assert panel_result.accepted is True


# ---------------------------------------------------------------------------
# 5–7. Control-surface field presence / mismatch
# ---------------------------------------------------------------------------


class TestControlSurfaceFieldRules:
    def test_control_surface_healing_rejected(self):
        # Generic healing doc without a recognized healing_tier — still
        # rejected by the generic healing bucket.
        doc = _mk_healing_doc(
            healing_tier="custom_future_tier",
            model_id="some-model",
        )
        result = validate_panel_attestation(doc)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_HEALING_OUTPUT_FOR_JUDGE_CERTIFICATION
            in result.reason_codes
        )

    def test_control_surface_missing_rejected(self):
        att = _mk_valid_attestation()
        att.pop("control_surface", None)
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_CONTROL_SURFACE_MISSING in result.reason_codes
        )

    def test_control_surface_mismatch_rejected(self):
        att = _mk_valid_attestation()
        att["control_surface"] = "experimental"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_CONTROL_SURFACE_MISMATCH in result.reason_codes
        )


# ---------------------------------------------------------------------------
# 8. Judge panel missing juror — rejected
# ---------------------------------------------------------------------------


class TestJudgePanelMissingJuror:
    def test_control_surface_llm_as_judge_but_missing_one_juror_rejected(self):
        # Only 2 of the 3 required jurors present, correct surface
        att = _mk_valid_attestation(
            jurors=[_mk_gemini_safe(), _mk_openai_safe()]
        )
        att["invoked_juror_count"] = 2
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_MISSING_JUROR in result.reason_codes


# ---------------------------------------------------------------------------
# 9. Valid three-juror panel is accepted (regression sentinel)
# ---------------------------------------------------------------------------


class TestValidPanelAccepted:
    def test_valid_three_juror_panel_accepted(self):
        result = validate_panel_attestation(_mk_valid_attestation())
        assert result.accepted is True
        assert result.reason_codes == ()
        assert result.row_status == "ACCEPTED"


# ---------------------------------------------------------------------------
# 10–12. Regression — provider/stage rejections still fire
# ---------------------------------------------------------------------------


class TestProviderAndStageRejections:
    def test_local_qwen_diagnostic_rejected(self):
        att = _mk_valid_attestation(jurors=[
            _mk_juror_entry(
                juror_id="local_qwen_32b",
                family="local_qwen",
                provider="local_qwen",
                model_id="Qwen/Qwen2.5-32B-Instruct-AWQ",
                provider_match="FAIL",
                model_match="FAIL",
                approved=False,
                # Juror surface stays llm_as_judge so the per-juror
                # surface gate passes and the provider classifier fires.
                control_surface="llm_as_judge",
            ),
            _mk_anthropic_safe(),
            _mk_openai_safe(),
        ])
        att["provider_panel_match_status"] = "FAIL"
        att["model_panel_match_status"] = "FAIL"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_LOCAL_QWEN_FOR_RTC_REQ_056
            in result.reason_codes
            or RejectReason.REJECT_QWEN_FOR_RTC_REQ_056
            in result.reason_codes
        )

    def test_mock_safe_rejected(self):
        att = _mk_valid_attestation()
        att["mock_safe_used_any"] = True
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_MOCK_SAFE_IN_CERTIFICATION
            in result.reason_codes
        )

    def test_deterministic_stage_rejected(self):
        att = _mk_valid_attestation()
        att["deterministic_proof_stage_used_any"] = True
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_DETERMINISTIC_STAGE_IN_CERTIFICATION
            in result.reason_codes
        )


# ---------------------------------------------------------------------------
# 13. Healing artifacts remain valid for remediation workflows
# ---------------------------------------------------------------------------


class TestHealingArtifactsValidForRemediation:
    def test_healing_artifact_has_valid_healing_shape_but_fails_judge_gate(self):
        """A healing artifact is structurally valid for its own workflow
        (has healing_tier + healing_action + healing_evidence_ref), but
        MUST NEVER satisfy RTC-REQ-056 — even when SAFE-shaped."""
        healing = _mk_healing_doc(
            healing_tier="deterministic",
            model_id=None,
        )
        # Its healing-shape fields are intact
        assert healing["control_surface"] == "healing"
        assert healing["purpose"] == "remediation"
        assert healing["healing_tier"] == "deterministic"
        assert healing["healing_action"] == "propose"
        # But the RTC-REQ-056 gate rejects it
        result = validate_panel_attestation(healing)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_DETERMINISTIC_HEALING_FOR_RTC_REQ_056
            in result.reason_codes
        )


# ---------------------------------------------------------------------------
# 14. SPOOFING — a healing Gemini Pro artifact that falsely stamps
#     control_surface="llm_as_judge" must still fail
# ---------------------------------------------------------------------------


class TestSpoofingHealingAsJudge:
    def test_healing_gemini_pro_with_faked_judge_surface_still_rejected(self):
        """Adversarial case: a healing-origin document stamps
        ``control_surface = "llm_as_judge"`` on itself in an attempt to
        pass the top-level surface gate. The document has only ONE
        juror-shaped entry (healing gemini_pro), no panel quorum, no
        matching identities, and the rest of the gate must catch it:

          - REJECT_MISSING_JUROR (only 1 of 3 required)
          - REJECT_SINGLE_MODEL_JUDGE_FOR_RTC_REQ_056 implicitly via
            missing jurors + mode checks
          - per-juror provider/model match failures

        The test asserts that the document is REJECTED and that the
        failure does NOT permit ACCEPTED regardless of the faked surface
        label.
        """
        # Build a spoofed doc: stamp judge surface at top BUT with only
        # one juror entry and a healing_tier field still present.
        spoofed = _mk_healing_doc(
            healing_tier="gemini_pro",
            model_id=GEMINI_JUROR.model_id,
            spoof_surface="llm_as_judge",
        )
        # Add ONE juror record shaped like a judge juror so the doc
        # looks more convincing. Single-juror panel = quorum fail.
        spoofed["jurors"] = [
            _mk_juror_entry(
                juror_id=GEMINI_JUROR.juror_id,
                family=GEMINI_JUROR.provider_family,
                provider=GEMINI_JUROR.provider,
                model_id=GEMINI_JUROR.model_id,
                control_surface="llm_as_judge",
            )
        ]
        spoofed["invoked_juror_count"] = 1

        result = validate_panel_attestation(spoofed)

        # Must NOT be accepted
        assert result.accepted is False

        # The top-level surface gate passes (spoofed), BUT:
        #  - the healing_tier field at top level is now classifying as
        #    a healing document through the SAME classifier (because the
        #    gate now also inspects healing_tier even under spoofed
        #    surface — defensive). However, classify_healing_tier_for_reject
        #    only fires on surface=="healing"; a spoofed surface of
        #    "llm_as_judge" bypasses the healing bucket. The test
        #    therefore must catch the doc via structural / quorum gates:
        assert RejectReason.REJECT_MISSING_JUROR in result.reason_codes
        # And the panel must not be fully SAFE since quorum isn't met
        assert (
            RejectReason.REJECT_MISSING_JUROR in result.reason_codes
            or RejectReason.REJECT_SINGLE_MODEL_JUDGE_FOR_RTC_REQ_056
            in result.reason_codes
        )

    def test_spoofed_single_juror_still_fails_even_if_identity_perfect(self):
        """Even if the single juror matches the registered Gemini juror
        perfectly, one juror is not a quorum. The ``all_required_safe``
        rule requires all three."""
        spoofed = {
            "attestation_schema_version": 3,
            "attestation_kind": "rtc_req_056_consensus_jury_panel",
            "certification_scope": "RTC-REQ-056",
            "control_surface": "llm_as_judge",
            "purpose": "certification",
            "judge_mode": "consensus_jury",
            "quorum_rule": "all_required_safe",
            "required_juror_count": 3,
            "invoked_juror_count": 1,
            "final_consensus_verdict": "SAFE",
            "final_safe_reuse_allow": True,
            "final_x3_disposition": "X3D",
            "rubric_hash_sha256": "aa" * 32,
            "request_hash_sha256": "bb" * 32,
            "cache_candidate_hash_sha256": "cc" * 32,
            "panel_response_hash_sha256": "dd" * 32,
            "provider_panel_match_status": "PASS",
            "model_panel_match_status": "PASS",
            "mock_safe_used_any": False,
            "deterministic_proof_stage_used_any": False,
            "created_at_utc": "2026-05-01T18:15:00.000000Z",
            "artifact_hash": "ff" * 32,
            "jurors": [
                _mk_juror_entry(
                    juror_id=GEMINI_JUROR.juror_id,
                    family=GEMINI_JUROR.provider_family,
                    provider=GEMINI_JUROR.provider,
                    model_id=GEMINI_JUROR.model_id,
                    control_surface="llm_as_judge",
                )
            ],
        }
        result = validate_panel_attestation(spoofed)
        assert result.accepted is False
        assert RejectReason.REJECT_MISSING_JUROR in result.reason_codes


# ---------------------------------------------------------------------------
# classify_healing_tier_for_reject — direct unit tests
# ---------------------------------------------------------------------------


class TestClassifyHealingTierForReject:
    def test_missing_surface_returns_control_surface_missing(self):
        assert classify_healing_tier_for_reject(None, None, None) == (
            RejectReason.REJECT_CONTROL_SURFACE_MISSING
        )

    def test_empty_string_surface_returns_control_surface_missing(self):
        assert classify_healing_tier_for_reject("", None, None) == (
            RejectReason.REJECT_CONTROL_SURFACE_MISSING
        )

    @pytest.mark.parametrize("tier,expected", [
        ("deterministic", RejectReason.REJECT_DETERMINISTIC_HEALING_FOR_RTC_REQ_056),
        ("qwen", RejectReason.REJECT_QWEN_HEALING_FOR_RTC_REQ_056),
        ("gemini_flash", RejectReason.REJECT_GEMINI_FLASH_HEALING_FOR_RTC_REQ_056),
        ("gemini_pro", RejectReason.REJECT_HEALING_GEMINI_PRO_NOT_PANEL_JUROR),
        ("unknown_future_tier",
         RejectReason.REJECT_HEALING_OUTPUT_FOR_JUDGE_CERTIFICATION),
        (None, RejectReason.REJECT_HEALING_OUTPUT_FOR_JUDGE_CERTIFICATION),
    ])
    def test_healing_surface_dispatches_by_tier(self, tier, expected):
        assert classify_healing_tier_for_reject("healing", tier, None) == expected

    def test_mismatched_surface_returns_mismatch(self):
        assert classify_healing_tier_for_reject(
            "experimental", None, None
        ) == RejectReason.REJECT_CONTROL_SURFACE_MISMATCH

    def test_llm_as_judge_surface_returns_none(self):
        assert classify_healing_tier_for_reject(
            "llm_as_judge", None, None
        ) is None

    def test_llm_as_judge_is_case_insensitive(self):
        assert classify_healing_tier_for_reject(
            "LLM_As_Judge", None, None
        ) is None
