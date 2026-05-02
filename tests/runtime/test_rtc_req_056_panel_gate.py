"""RTC-REQ-056 consensus-jury panel-gate tests.

Covers the positive + negative matrix required by the operator
directive dated 2026-05-01 13:39 UTC-04:00.

No SDK calls, no network, no API keys. Each test builds an attestation
payload in-memory and runs it through ``validate_panel_attestation``.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest

from tools.certification.safety.rtc_req_056_gate import (
    PanelGateResult,
    validate_panel_attestation,
)
from tools.certification.safety.rtc_req_056_panel import (
    ANTHROPIC_JUROR,
    ATTESTATION_SCHEMA_VERSION,
    CERTIFICATION_SCOPE,
    GEMINI_JUROR,
    JUDGE_MODE,
    OPENAI_JUROR,
    QUORUM_RULE,
    REQUIRED_JUROR_COUNT,
    REQUIRED_JURORS,
    RejectReason,
)


# ---------------------------------------------------------------------------
# Helpers — build a baseline-valid attestation
# ---------------------------------------------------------------------------


def _mk_juror_entry(
    *,
    juror_id: str,
    family: str,
    provider: str,
    model_id: str,
    verdict: str = "SAFE",
    confidence: float = 0.92,
    response_hash: str = "aa" * 32,
    provider_match: str = "PASS",
    model_match: str = "PASS",
    approved: bool = True,
    parse_status: str = "OK",
    timeout_count: int = 0,
    error_count: int = 0,
    unknown_count: int = 0,
    unsafe_count: int = 0,
    parse_fail_count: int = 0,
    mock_safe_used: bool = False,
    deterministic_used: bool = False,
    latency_ms: float = 1200.0,
    control_surface: str = "llm_as_judge",
) -> dict[str, Any]:
    # Target identity always reflects the registry
    target = next(
        (j for j in REQUIRED_JURORS if j.provider_family == family), None
    )
    return {
        "juror_id": juror_id,
        "control_surface": control_surface,
        "provider_family": family,
        "provider": provider,
        "model_id": model_id,
        "target_provider_family": target.provider_family if target else family,
        "target_provider": target.provider if target else provider,
        "target_model_id": target.model_id if target else model_id,
        "provider_match_status": provider_match,
        "model_match_status": model_match,
        "approved_provider": approved,
        "verdict": verdict,
        "confidence": confidence,
        "latency_ms": latency_ms,
        "response_hash_sha256": response_hash,
        "parse_status": parse_status,
        "timeout_count": timeout_count,
        "error_count": error_count,
        "unknown_count": unknown_count,
        "unsafe_count": unsafe_count,
        "parse_fail_count": parse_fail_count,
        "mock_safe_used": mock_safe_used,
        "deterministic_proof_stage_used": deterministic_used,
        "raw_output_retention_mode": "hash_only",
    }


def _mk_gemini_safe(**kwargs) -> dict[str, Any]:
    base = dict(
        juror_id=GEMINI_JUROR.juror_id,
        family=GEMINI_JUROR.provider_family,
        provider=GEMINI_JUROR.provider,
        model_id=GEMINI_JUROR.model_id,
    )
    base.update(kwargs)
    return _mk_juror_entry(**base)


def _mk_anthropic_safe(**kwargs) -> dict[str, Any]:
    base = dict(
        juror_id=ANTHROPIC_JUROR.juror_id,
        family=ANTHROPIC_JUROR.provider_family,
        provider=ANTHROPIC_JUROR.provider,
        model_id=ANTHROPIC_JUROR.model_id,
    )
    base.update(kwargs)
    return _mk_juror_entry(**base)


def _mk_openai_safe(**kwargs) -> dict[str, Any]:
    base = dict(
        juror_id=OPENAI_JUROR.juror_id,
        family=OPENAI_JUROR.provider_family,
        provider=OPENAI_JUROR.provider,
        model_id=OPENAI_JUROR.model_id,
    )
    base.update(kwargs)
    return _mk_juror_entry(**base)


def _mk_valid_attestation(*, jurors: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Build a baseline-valid panel attestation. All 3 jurors SAFE by default."""
    if jurors is None:
        jurors = [_mk_gemini_safe(), _mk_anthropic_safe(), _mk_openai_safe()]
    return {
        "attestation_schema_version": ATTESTATION_SCHEMA_VERSION,
        "attestation_kind": "rtc_req_056_consensus_jury_panel",
        "certification_scope": CERTIFICATION_SCOPE,
        # Schema v3 — control-surface labels required
        "control_surface": "llm_as_judge",
        "purpose": "certification",
        "judge_mode": JUDGE_MODE,
        "quorum_rule": QUORUM_RULE,
        "required_juror_count": REQUIRED_JUROR_COUNT,
        "invoked_juror_count": len(jurors),
        "final_consensus_verdict": "SAFE",
        "final_safe_reuse_allow": True,
        "final_x3_disposition": "X3D",
        "rubric_hash_sha256": "bb" * 32,
        "request_hash_sha256": "cc" * 32,
        "cache_candidate_hash_sha256": "dd" * 32,
        "panel_response_hash_sha256": "ee" * 32,
        "provider_panel_match_status": "PASS",
        "model_panel_match_status": "PASS",
        "mock_safe_used_any": False,
        "deterministic_proof_stage_used_any": False,
        "created_at_utc": "2026-05-01T17:39:00.000000Z",
        "artifact_hash": "ff" * 32,
        "jurors": jurors,
    }


# ---------------------------------------------------------------------------
# POSITIVE TESTS (5)
# ---------------------------------------------------------------------------


class TestPositiveAllThreeSafe:
    def test_all_three_safe_accepts(self):
        result = validate_panel_attestation(_mk_valid_attestation())
        assert result.accepted is True, result.reason_codes
        assert result.reason_codes == ()
        assert result.row_status == "ACCEPTED"

    def test_panel_attestation_has_all_required_top_level_fields(self):
        att = _mk_valid_attestation()
        required = {
            "attestation_schema_version", "certification_scope",
            "judge_mode", "quorum_rule", "required_juror_count",
            "invoked_juror_count", "final_consensus_verdict",
            "final_safe_reuse_allow", "final_x3_disposition",
            "rubric_hash_sha256", "request_hash_sha256",
            "cache_candidate_hash_sha256", "panel_response_hash_sha256",
            "provider_panel_match_status", "model_panel_match_status",
            "mock_safe_used_any", "deterministic_proof_stage_used_any",
            "created_at_utc", "artifact_hash", "jurors",
        }
        assert required.issubset(set(att.keys()))

    def test_per_juror_attestation_has_all_required_fields(self):
        att = _mk_valid_attestation()
        required = {
            "juror_id", "provider_family", "provider", "model_id",
            "target_provider_family", "target_provider", "target_model_id",
            "provider_match_status", "model_match_status",
            "approved_provider", "verdict", "confidence", "latency_ms",
            "response_hash_sha256", "parse_status", "timeout_count",
            "error_count", "unknown_count", "unsafe_count",
            "parse_fail_count", "mock_safe_used",
            "deterministic_proof_stage_used", "raw_output_retention_mode",
        }
        for j in att["jurors"]:
            assert required.issubset(set(j.keys())), (
                f"juror missing fields: {required - set(j.keys())}"
            )

    def test_accepted_row_status_is_accepted(self):
        result = validate_panel_attestation(_mk_valid_attestation())
        assert result.row_status == "ACCEPTED"

    def test_composer_would_allow_rtc_req_056(self):
        # This simulates what the composer does — load + validate + use
        # row_status to decide R1B_INTEGRATED_RUNTIME_PROOF verdict.
        result = validate_panel_attestation(_mk_valid_attestation())
        assert result.accepted and result.row_status == "ACCEPTED"
        # In composer: if result.accepted -> R1B_INTEGRATED_RUNTIME_PROOF = PASS


# ---------------------------------------------------------------------------
# NEGATIVE — verdict mix
# ---------------------------------------------------------------------------


class TestNegativeVerdictMix:
    def test_gemini_safe_claude_safe_gpt_unknown_blocks(self):
        att = _mk_valid_attestation(jurors=[
            _mk_gemini_safe(),
            _mk_anthropic_safe(),
            _mk_openai_safe(verdict="UNCERTAIN", unknown_count=1,
                            parse_status="UNKNOWN"),
        ])
        # Panel final_consensus must be overridden by test to match
        att["final_consensus_verdict"] = "NOT_SAFE"
        att["final_safe_reuse_allow"] = False
        att["final_x3_disposition"] = "X3_DENIED_FAIL_CLOSED"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_JUROR_UNKNOWN in result.reason_codes

    def test_gemini_safe_claude_unsafe_gpt_safe_blocks(self):
        att = _mk_valid_attestation(jurors=[
            _mk_gemini_safe(),
            _mk_anthropic_safe(verdict="UNSAFE_DIFFERENT_INTENT",
                               unsafe_count=1),
            _mk_openai_safe(),
        ])
        att["final_consensus_verdict"] = "NOT_SAFE"
        att["final_safe_reuse_allow"] = False
        att["final_x3_disposition"] = "X3_DENIED_FAIL_CLOSED"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_JUROR_UNSAFE in result.reason_codes

    def test_one_juror_timeout_blocks(self):
        att = _mk_valid_attestation(jurors=[
            _mk_gemini_safe(),
            _mk_anthropic_safe(verdict="ERROR", parse_status="TIMEOUT",
                               timeout_count=1, error_count=0),
            _mk_openai_safe(),
        ])
        att["final_consensus_verdict"] = "NOT_SAFE"
        att["final_safe_reuse_allow"] = False
        att["final_x3_disposition"] = "X3_DENIED_FAIL_CLOSED"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_JUROR_TIMEOUT in result.reason_codes

    def test_one_juror_parse_failure_blocks(self):
        att = _mk_valid_attestation(jurors=[
            _mk_gemini_safe(),
            _mk_anthropic_safe(),
            _mk_openai_safe(verdict="ERROR", parse_status="PARSE_FAIL",
                            parse_fail_count=1),
        ])
        att["final_consensus_verdict"] = "NOT_SAFE"
        att["final_safe_reuse_allow"] = False
        att["final_x3_disposition"] = "X3_DENIED_FAIL_CLOSED"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_JUROR_PARSE_FAIL in result.reason_codes

    def test_one_juror_provider_error_blocks(self):
        att = _mk_valid_attestation(jurors=[
            _mk_gemini_safe(),
            _mk_anthropic_safe(verdict="ERROR", parse_status="ERROR",
                               error_count=1),
            _mk_openai_safe(),
        ])
        att["final_consensus_verdict"] = "NOT_SAFE"
        att["final_safe_reuse_allow"] = False
        att["final_x3_disposition"] = "X3_DENIED_FAIL_CLOSED"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_JUROR_ERROR in result.reason_codes


# ---------------------------------------------------------------------------
# NEGATIVE — wrong model IDs
# ---------------------------------------------------------------------------


class TestNegativeWrongModelIds:
    def test_wrong_gemini_model_rejects(self):
        att = _mk_valid_attestation(jurors=[
            _mk_gemini_safe(model_id="gemini-2.5-pro",
                            model_match="FAIL", approved=False),
            _mk_anthropic_safe(),
            _mk_openai_safe(),
        ])
        att["model_panel_match_status"] = "FAIL"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_UNREGISTERED_MODEL in result.reason_codes

    def test_wrong_claude_model_rejects(self):
        att = _mk_valid_attestation(jurors=[
            _mk_gemini_safe(),
            _mk_anthropic_safe(model_id="claude-3-opus-20240229",
                               model_match="FAIL", approved=False),
            _mk_openai_safe(),
        ])
        att["model_panel_match_status"] = "FAIL"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_UNREGISTERED_MODEL in result.reason_codes

    def test_wrong_gpt_model_rejects(self):
        att = _mk_valid_attestation(jurors=[
            _mk_gemini_safe(),
            _mk_anthropic_safe(),
            _mk_openai_safe(model_id="gpt-4o",
                            model_match="FAIL", approved=False),
        ])
        att["model_panel_match_status"] = "FAIL"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_UNREGISTERED_MODEL in result.reason_codes


# ---------------------------------------------------------------------------
# NEGATIVE — rejected providers
# ---------------------------------------------------------------------------


class TestNegativeRejectedProviders:
    def test_local_qwen_cannot_certify(self):
        att = _mk_valid_attestation(jurors=[
            _mk_juror_entry(
                juror_id="local_qwen_32b",
                family="local_qwen",
                provider="local_qwen",
                model_id="Qwen/Qwen2.5-32B-Instruct-AWQ",
                provider_match="FAIL",
                model_match="FAIL",
                approved=False,
            ),
            _mk_anthropic_safe(),
            _mk_openai_safe(),
        ])
        att["provider_panel_match_status"] = "FAIL"
        att["model_panel_match_status"] = "FAIL"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        # Either the provider OR model rejection code should fire
        assert (
            RejectReason.REJECT_LOCAL_QWEN_FOR_RTC_REQ_056 in result.reason_codes
            or RejectReason.REJECT_QWEN_FOR_RTC_REQ_056 in result.reason_codes
        )

    def test_anthropic_haiku_cannot_certify(self):
        att = _mk_valid_attestation(jurors=[
            _mk_gemini_safe(),
            _mk_juror_entry(
                juror_id="anthropic_haiku",
                family="anthropic_haiku",
                provider="claude",
                model_id="claude-3-haiku-20240307",
                provider_match="FAIL",
                model_match="FAIL",
                approved=False,
            ),
            _mk_openai_safe(),
        ])
        att["provider_panel_match_status"] = "FAIL"
        att["model_panel_match_status"] = "FAIL"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_ANTHROPIC_HAIKU_FOR_RTC_REQ_056
            in result.reason_codes
        )

    def test_mock_safe_any_rejects(self):
        att = _mk_valid_attestation()
        att["mock_safe_used_any"] = True
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_MOCK_SAFE_IN_CERTIFICATION in result.reason_codes

    def test_deterministic_stage_rejects(self):
        att = _mk_valid_attestation()
        att["deterministic_proof_stage_used_any"] = True
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_DETERMINISTIC_STAGE_IN_CERTIFICATION
            in result.reason_codes
        )


# ---------------------------------------------------------------------------
# NEGATIVE — panel shape / quorum / missing fields
# ---------------------------------------------------------------------------


class TestNegativePanelShape:
    def test_single_model_attestation_rejects(self):
        # Only one juror present
        att = _mk_valid_attestation(jurors=[_mk_gemini_safe()])
        att["invoked_juror_count"] = 1
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_MISSING_JUROR in result.reason_codes

    def test_missing_quorum_rule_rejects(self):
        att = _mk_valid_attestation()
        att["quorum_rule"] = "majority_vote"  # wrong value
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_MISSING_QUORUM_RULE in result.reason_codes

    def test_missing_one_juror_in_attestation_rejects(self):
        # Two jurors — Gemini and OpenAI, but no Anthropic
        att = _mk_valid_attestation(jurors=[
            _mk_gemini_safe(), _mk_openai_safe()
        ])
        att["invoked_juror_count"] = 2
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_MISSING_JUROR in result.reason_codes

    def test_missing_rubric_hash_rejects(self):
        att = _mk_valid_attestation()
        att["rubric_hash_sha256"] = ""
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_MALFORMED_JUROR_OUTPUT in result.reason_codes
        )

    def test_missing_response_hash_rejects(self):
        att = _mk_valid_attestation(jurors=[
            _mk_gemini_safe(response_hash=""),
            _mk_anthropic_safe(),
            _mk_openai_safe(),
        ])
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_MALFORMED_JUROR_OUTPUT in result.reason_codes
        )

    def test_missing_panel_attestation_rejects(self):
        result = validate_panel_attestation(None)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_MISSING_PANEL_ATTESTATION in result.reason_codes
        )
        assert result.row_status == "BLOCKED"

    def test_final_verdict_not_safe_rejects(self):
        att = _mk_valid_attestation()
        att["final_consensus_verdict"] = "NOT_SAFE"
        att["final_safe_reuse_allow"] = False
        att["final_x3_disposition"] = "X3_DENIED_FAIL_CLOSED"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_PANEL_NOT_FULLY_SAFE in result.reason_codes

    def test_wrong_judge_mode_rejects(self):
        att = _mk_valid_attestation()
        att["judge_mode"] = "single_judge"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert (
            RejectReason.REJECT_SINGLE_MODEL_JUDGE_FOR_RTC_REQ_056
            in result.reason_codes
        )


# ---------------------------------------------------------------------------
# NEGATIVE — single-provider-only attestation cannot certify
# ---------------------------------------------------------------------------


class TestNegativeSingleProviderCannotCertify:
    def test_qwen_only_attestation_rejected(self):
        att = _mk_valid_attestation(jurors=[
            _mk_juror_entry(
                juror_id="local_qwen_32b",
                family="local_qwen",
                provider="local_qwen",
                model_id="Qwen/Qwen2.5-32B-Instruct-AWQ",
                provider_match="FAIL",
                model_match="FAIL",
                approved=False,
            ),
        ])
        att["invoked_juror_count"] = 1
        att["provider_panel_match_status"] = "FAIL"
        att["model_panel_match_status"] = "FAIL"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        # Multiple reasons: missing juror + rejected provider + rejected model
        assert RejectReason.REJECT_MISSING_JUROR in result.reason_codes

    def test_anthropic_only_attestation_rejected(self):
        att = _mk_valid_attestation(jurors=[_mk_anthropic_safe()])
        att["invoked_juror_count"] = 1
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_MISSING_JUROR in result.reason_codes

    def test_gemini_only_attestation_rejected(self):
        att = _mk_valid_attestation(jurors=[_mk_gemini_safe()])
        att["invoked_juror_count"] = 1
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_MISSING_JUROR in result.reason_codes

    def test_non_panel_model_cannot_certify(self):
        # Three jurors but one using unregistered family
        att = _mk_valid_attestation(jurors=[
            _mk_gemini_safe(),
            _mk_anthropic_safe(),
            _mk_juror_entry(
                juror_id="cohere_command_r",
                family="cohere",
                provider="cohere",
                model_id="command-r-plus",
                provider_match="FAIL",
                model_match="FAIL",
                approved=False,
            ),
        ])
        att["provider_panel_match_status"] = "FAIL"
        att["model_panel_match_status"] = "FAIL"
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_UNREGISTERED_PROVIDER in result.reason_codes


# ---------------------------------------------------------------------------
# ROW STATUS mapping checks
# ---------------------------------------------------------------------------


class TestRowStatus:
    def test_accepted_when_clean(self):
        assert validate_panel_attestation(_mk_valid_attestation()).row_status == "ACCEPTED"

    def test_pending_when_attestation_missing(self):
        assert validate_panel_attestation(None).row_status in ("PENDING", "BLOCKED")

    def test_blocked_when_reject_codes_fire(self):
        att = _mk_valid_attestation()
        att["mock_safe_used_any"] = True
        result = validate_panel_attestation(att)
        assert result.row_status == "BLOCKED"


# ---------------------------------------------------------------------------
# Schema v3 regression — top-level control_surface is now REQUIRED
# ---------------------------------------------------------------------------


class TestSchemaV3TopLevelControlSurfaceRequired:
    def test_attestation_without_top_level_control_surface_is_rejected(self):
        """Regression: an attestation that would have been valid under v2 — i.e.
        panel shape correct, jurors SAFE, but missing top-level
        ``control_surface`` — must now be rejected with
        ``REJECT_CONTROL_SURFACE_MISSING``."""
        from tools.certification.safety.rtc_req_056_panel import RejectReason

        att = _mk_valid_attestation()
        att.pop("control_surface", None)  # drop top-level surface
        result = validate_panel_attestation(att)
        assert result.accepted is False
        assert RejectReason.REJECT_CONTROL_SURFACE_MISSING in result.reason_codes

    def test_attestation_without_top_level_purpose_is_rejected(self):
        from tools.certification.safety.rtc_req_056_panel import RejectReason

        att = _mk_valid_attestation()
        att.pop("purpose", None)
        result = validate_panel_attestation(att)
        assert result.accepted is False
        # purpose-missing fires REJECT_CONTROL_SURFACE_MISMATCH per gate logic
        assert (
            RejectReason.REJECT_CONTROL_SURFACE_MISMATCH in result.reason_codes
            or RejectReason.REJECT_MALFORMED_JUROR_OUTPUT in result.reason_codes
        )
