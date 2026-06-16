"""Live GPT X1D preflight for apps_lic W1.

The preflight proves that the independent judge path can call OpenAI GPT
and parse a minimal rubric response. It does not clear a draft by itself; Exit
still requires candidate-specific X1D judge artifacts.
"""

from __future__ import annotations

import importlib.util
import json
import os
from dataclasses import dataclass
from typing import Any, Mapping

from apps_lic.engines.validation_exit import (
    OPENAI_RESPONSES_API,
    DEFAULT_X1D_JUDGE_MODEL,
    DEFAULT_X1D_JUDGE_PROVIDER,
    JUDGE_AVAILABLE,
    JUDGE_UNAVAILABLE,
    LIVE_GPT_API_CALL,
    X1DJudgeProfile,
)
from apps_lic.engines.x1d_gpt_judge_adapter import (
    DEFAULT_GPT_MAX_TOKENS,
    DEFAULT_GPT_TRANSPORT_MODEL_ID,
    OpenAIGPTX1DTransport,
    GPTX1DTransport,
    parse_gpt_x1d_response,
    raw_response_digest,
)


X1D_MODE_FAKE = "fake"
X1D_MODE_LIVE = "live"
X1D_MODE_UNAVAILABLE_EXPECTED = "unavailable-expected"
X1D_MODE_UNAVAILABLE_EXPECTED_ALIAS = "unavailable_expected"

PREFLIGHT_READY = "GPT_X1D_PREFLIGHT_READY"
PREFLIGHT_UNAVAILABLE = "GPT_X1D_PREFLIGHT_UNAVAILABLE"
PREFLIGHT_FAKE_ONLY = "GPT_X1D_PREFLIGHT_FAKE_ONLY"
PREFLIGHT_BLOCKED = "GPT_X1D_PREFLIGHT_BLOCKED"

ISSUE_API_KEY_MISSING = "openai_api_key_missing"
ISSUE_SDK_MISSING = "openai_sdk_missing"
ISSUE_WRONG_MODEL_ID = "wrong_gpt_model_id"
ISSUE_FAKE_MODE = "fake_x1d_mode_cannot_clear_exit"
ISSUE_UNAVAILABLE_EXPECTED_MODE = "unavailable_expected_mode_does_not_clear_exit"
ISSUE_UNAVAILABLE_EXPECTED_WITH_LIVE_READY = "unavailable_expected_mode_with_live_prerequisites"
ISSUE_NON_LIVE_TRANSPORT = "non_live_gpt_transport_rejected"
ISSUE_PARSE_FAILED = "gpt_minimal_rubric_parse_failed"
ISSUE_UNAVAILABLE_RESPONSE = "gpt_minimal_rubric_unavailable"
ISSUE_NON_LIVE_RECEIPT = "gpt_minimal_rubric_non_live_receipt"
ISSUE_RUBRIC_FAILED = "gpt_minimal_rubric_failed"

_PREFLIGHT_JUDGE_ID = "x1d_preflight_minimal_rubric"
_PREFLIGHT_RUBRIC_ID = "apps_lic.x1d.preflight_minimal_rubric.v1"
_PREFLIGHT_THRESHOLD = 0.01


@dataclass(frozen=True)
class GPTX1DPreflightReceipt:
    schema_version: str = "apps_lic.GPT_X1D_preflight.v1"
    mode: str = X1D_MODE_LIVE
    preflight_status: str = PREFLIGHT_UNAVAILABLE
    availability_status: str = JUDGE_UNAVAILABLE
    provider: str = DEFAULT_X1D_JUDGE_PROVIDER
    model: str = DEFAULT_X1D_JUDGE_MODEL
    transport_model_id: str = DEFAULT_GPT_TRANSPORT_MODEL_ID
    score: float = 0.0
    threshold: float = _PREFLIGHT_THRESHOLD
    api_key_present: bool = False
    openai_sdk_available: bool = False
    model_id_configured: bool = True
    minimal_rubric_call_attempted: bool = False
    minimal_rubric_json_parse_valid: bool = False
    clearance_allowed: bool = False
    expected_unavailable: bool = False
    independence_status: str = "independent_judge"
    transport_provenance: str = ""
    transport_provider: str = ""
    transport_call_id: str = ""
    raw_response_digest: str = ""
    issues: tuple[str, ...] = ()

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "mode": self.mode,
            "preflight_status": self.preflight_status,
            "availability_status": self.availability_status,
            "provider": self.provider,
            "model": self.model,
            "transport_model_id": self.transport_model_id,
            "score": self.score,
            "threshold": self.threshold,
            "api_key_present": self.api_key_present,
            "openai_sdk_available": self.openai_sdk_available,
            "model_id_configured": self.model_id_configured,
            "minimal_rubric_call_attempted": self.minimal_rubric_call_attempted,
            "minimal_rubric_json_parse_valid": self.minimal_rubric_json_parse_valid,
            "clearance_allowed": self.clearance_allowed,
            "expected_unavailable": self.expected_unavailable,
            "independence_status": self.independence_status,
            "transport_provenance": self.transport_provenance,
            "transport_provider": self.transport_provider,
            "transport_call_id": self.transport_call_id,
            "raw_response_digest": self.raw_response_digest,
            "issues": list(self.issues),
            "clearance": "pass" if self.clearance_allowed else "fail",
        }


def normalize_x1d_mode(mode: str) -> str:
    cleaned = str(mode or "").strip().lower().replace("_", "-")
    if cleaned in {X1D_MODE_FAKE, X1D_MODE_LIVE, X1D_MODE_UNAVAILABLE_EXPECTED}:
        return cleaned
    return ""


def openai_sdk_available() -> bool:
    try:
        return importlib.util.find_spec("openai") is not None
    except (ImportError, ValueError):
        return False


def _preflight_profile() -> X1DJudgeProfile:
    return X1DJudgeProfile(
        judge_id=_PREFLIGHT_JUDGE_ID,
        rubric_id=_PREFLIGHT_RUBRIC_ID,
        model=DEFAULT_X1D_JUDGE_MODEL,
        provider=DEFAULT_X1D_JUDGE_PROVIDER,
        threshold=_PREFLIGHT_THRESHOLD,
        role="Minimal live GPT JSON rubric parse validation.",
        required_for_depth="preflight",
    )


def build_gpt_x1d_preflight_payload(
    *,
    transport_model_id: str = DEFAULT_GPT_TRANSPORT_MODEL_ID,
) -> dict[str, Any]:
    return {
        "provider": DEFAULT_X1D_JUDGE_PROVIDER,
        "model": DEFAULT_X1D_JUDGE_MODEL,
        "transport_model_id": transport_model_id,
        "temperature": 0.0,
        "max_tokens": min(128, DEFAULT_GPT_MAX_TOKENS),
        "judge_id": _PREFLIGHT_JUDGE_ID,
        "rubric_id": _PREFLIGHT_RUBRIC_ID,
        "threshold": _PREFLIGHT_THRESHOLD,
        "system_prompt": "Return only valid JSON for this minimal judge preflight.",
        "user_prompt": json.dumps(
            {
                "task": "Return a passing minimal JSON judge receipt.",
                "required_json": {
                    "score": 1.0,
                    "passed": True,
                    "issues": [],
                    "required_repairs": [],
                },
            },
            sort_keys=True,
        ),
        "response_schema": {
            "score": "float 0.0-1.0",
            "passed": "boolean",
            "issues": "list[str]",
            "required_repairs": "list[str]",
        },
    }


def _base_receipt(
    *,
    mode: str,
    preflight_status: str,
    availability_status: str,
    api_key_present: bool,
    openai_sdk_is_available: bool,
    model_id_configured: bool,
    transport_model_id: str,
    issues: tuple[str, ...],
    expected_unavailable: bool = False,
) -> GPTX1DPreflightReceipt:
    return GPTX1DPreflightReceipt(
        mode=mode,
        preflight_status=preflight_status,
        availability_status=availability_status,
        api_key_present=api_key_present,
        openai_sdk_available=openai_sdk_is_available,
        model_id_configured=model_id_configured,
        transport_model_id=transport_model_id,
        expected_unavailable=expected_unavailable,
        issues=issues,
    )


def _prerequisite_issues(
    *,
    api_key_present: bool,
    openai_sdk_is_available: bool,
    model_id_configured: bool,
) -> tuple[str, ...]:
    issues: list[str] = []
    if not api_key_present:
        issues.append(ISSUE_API_KEY_MISSING)
    if not openai_sdk_is_available:
        issues.append(ISSUE_SDK_MISSING)
    if not model_id_configured:
        issues.append(ISSUE_WRONG_MODEL_ID)
    return tuple(issues)


def _is_live_receipt(result) -> bool:
    return (
        result.provider == DEFAULT_X1D_JUDGE_PROVIDER
        and result.model == DEFAULT_X1D_JUDGE_MODEL
        and result.transport_provenance == LIVE_GPT_API_CALL
        and result.transport_provider == OPENAI_RESPONSES_API
        and bool(result.transport_call_id)
        and result.raw_response_digest.startswith("sha256:")
    )


def run_gpt_x1d_preflight(
    *,
    mode: str = X1D_MODE_LIVE,
    api_key: str = "",
    env: Mapping[str, str] | None = None,
    transport_model_id: str = DEFAULT_GPT_TRANSPORT_MODEL_ID,
    transport: GPTX1DTransport | None = None,
    openai_sdk_available_override: bool | None = None,
) -> GPTX1DPreflightReceipt:
    """Run the W1 GPT X1D preflight or emit a fail-closed receipt."""
    normalized_mode = normalize_x1d_mode(mode)
    env_map = os.environ if env is None else env
    key = (api_key or env_map.get("OPENAI_API_KEY", "")).strip()
    key_present = bool(key)
    sdk_available = (
        openai_sdk_available()
        if openai_sdk_available_override is None
        else bool(openai_sdk_available_override)
    )
    model_id_configured = transport_model_id == DEFAULT_GPT_TRANSPORT_MODEL_ID
    prereq_issues = _prerequisite_issues(
        api_key_present=key_present,
        openai_sdk_is_available=sdk_available,
        model_id_configured=model_id_configured,
    )

    if not normalized_mode:
        return _base_receipt(
            mode=str(mode or ""),
            preflight_status=PREFLIGHT_BLOCKED,
            availability_status=JUDGE_UNAVAILABLE,
            api_key_present=key_present,
            openai_sdk_is_available=sdk_available,
            model_id_configured=model_id_configured,
            transport_model_id=transport_model_id,
            issues=("invalid_x1d_mode",),
        )

    if normalized_mode == X1D_MODE_FAKE:
        return _base_receipt(
            mode=normalized_mode,
            preflight_status=PREFLIGHT_FAKE_ONLY,
            availability_status=JUDGE_UNAVAILABLE,
            api_key_present=key_present,
            openai_sdk_is_available=sdk_available,
            model_id_configured=model_id_configured,
            transport_model_id=transport_model_id,
            issues=(ISSUE_FAKE_MODE,),
        )

    if normalized_mode == X1D_MODE_UNAVAILABLE_EXPECTED:
        issues = prereq_issues or (ISSUE_UNAVAILABLE_EXPECTED_WITH_LIVE_READY,)
        return _base_receipt(
            mode=normalized_mode,
            preflight_status=PREFLIGHT_UNAVAILABLE,
            availability_status=JUDGE_UNAVAILABLE,
            api_key_present=key_present,
            openai_sdk_is_available=sdk_available,
            model_id_configured=model_id_configured,
            transport_model_id=transport_model_id,
            expected_unavailable=True,
            issues=tuple(dict.fromkeys((*issues, ISSUE_UNAVAILABLE_EXPECTED_MODE))),
        )

    if prereq_issues:
        status = PREFLIGHT_BLOCKED if ISSUE_WRONG_MODEL_ID in prereq_issues else PREFLIGHT_UNAVAILABLE
        return _base_receipt(
            mode=normalized_mode,
            preflight_status=status,
            availability_status=JUDGE_UNAVAILABLE,
            api_key_present=key_present,
            openai_sdk_is_available=sdk_available,
            model_id_configured=model_id_configured,
            transport_model_id=transport_model_id,
            issues=prereq_issues,
        )

    live_transport = transport or OpenAIGPTX1DTransport(
        api_key=key,
        model_id=transport_model_id,
    )
    if not isinstance(live_transport, OpenAIGPTX1DTransport) or not getattr(live_transport, "live_gpt_transport", False):
        return _base_receipt(
            mode=normalized_mode,
            preflight_status=PREFLIGHT_BLOCKED,
            availability_status=JUDGE_UNAVAILABLE,
            api_key_present=key_present,
            openai_sdk_is_available=sdk_available,
            model_id_configured=model_id_configured,
            transport_model_id=transport_model_id,
            issues=(ISSUE_NON_LIVE_TRANSPORT,),
        )

    payload = build_gpt_x1d_preflight_payload(transport_model_id=transport_model_id)
    try:
        raw = live_transport(payload)
    except Exception as exc:  # guardian: allow-broad-exception -- live provider transports raise heterogeneous SDK/network errors; preflight records an unavailable receipt
        return _base_receipt(
            mode=normalized_mode,
            preflight_status=PREFLIGHT_UNAVAILABLE,
            availability_status=JUDGE_UNAVAILABLE,
            api_key_present=key_present,
            openai_sdk_is_available=sdk_available,
            model_id_configured=model_id_configured,
            transport_model_id=transport_model_id,
            issues=(f"gpt_preflight_transport_error:{type(exc).__name__}",),
        )

    result = parse_gpt_x1d_response(
        raw,
        profile=_preflight_profile(),
        trust_transport_proof=True,
    )
    issues: list[str] = []
    if not result.raw_response_digest.startswith("sha256:"):
        result_digest = raw_response_digest(raw)
    else:
        result_digest = result.raw_response_digest
    if result.availability_status != JUDGE_AVAILABLE:
        issues.append(ISSUE_UNAVAILABLE_RESPONSE)
    if "judge_response_not_parseable" in result.issues:
        issues.append(ISSUE_PARSE_FAILED)
    if not _is_live_receipt(result):
        issues.append(ISSUE_NON_LIVE_RECEIPT)
    if not result.passed or result.score < result.threshold:
        issues.append(ISSUE_RUBRIC_FAILED)

    parse_valid = not any(issue in issues for issue in (ISSUE_PARSE_FAILED, ISSUE_UNAVAILABLE_RESPONSE))
    ready = not issues
    return GPTX1DPreflightReceipt(
        mode=normalized_mode,
        preflight_status=PREFLIGHT_READY if ready else PREFLIGHT_BLOCKED,
        availability_status=JUDGE_AVAILABLE if ready else JUDGE_UNAVAILABLE,
        provider=result.provider,
        model=result.model,
        transport_model_id=transport_model_id,
        score=result.score,
        threshold=result.threshold,
        api_key_present=key_present,
        openai_sdk_available=sdk_available,
        model_id_configured=model_id_configured,
        minimal_rubric_call_attempted=True,
        minimal_rubric_json_parse_valid=parse_valid,
        clearance_allowed=ready,
        transport_provenance=result.transport_provenance,
        transport_provider=result.transport_provider,
        transport_call_id=result.transport_call_id,
        raw_response_digest=result_digest,
        issues=tuple(dict.fromkeys(issues)),
    )


__all__ = [
    "GPTX1DPreflightReceipt",
    "ISSUE_API_KEY_MISSING",
    "ISSUE_FAKE_MODE",
    "ISSUE_NON_LIVE_TRANSPORT",
    "ISSUE_PARSE_FAILED",
    "ISSUE_SDK_MISSING",
    "ISSUE_UNAVAILABLE_EXPECTED_MODE",
    "ISSUE_WRONG_MODEL_ID",
    "PREFLIGHT_BLOCKED",
    "PREFLIGHT_FAKE_ONLY",
    "PREFLIGHT_READY",
    "PREFLIGHT_UNAVAILABLE",
    "X1D_MODE_FAKE",
    "X1D_MODE_LIVE",
    "X1D_MODE_UNAVAILABLE_EXPECTED",
    "openai_sdk_available",
    "build_gpt_x1d_preflight_payload",
    "normalize_x1d_mode",
    "run_gpt_x1d_preflight",
]
