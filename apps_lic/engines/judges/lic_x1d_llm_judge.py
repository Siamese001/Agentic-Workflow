"""LIC-specific X1D LLM-as-judge for LinkedIn outreach quality.

The judge follows the apps_rg X1D design shape:

- compact packet only
- GRADE_ONLY, never repair
- low-temperature JSON response
- deterministic X2 gates stay authoritative
- missing/weak C0 evidence cannot be overridden by the judge
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping
from urllib import error as urllib_error
from urllib import request as urllib_request

from apps_lic.policy.reasoning_intensity import (
    JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
)

_LOGGER = logging.getLogger(__name__)

JUDGE_RUBRIC_VERSION = "lic_message_x1d_v1"
DEFAULT_THRESHOLD = 4.0
DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_OUTPUT_TOKENS = 700
DEFAULT_BASE_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_PROVIDER_PROFILE = "anthropic_claude_sonnet_4_6_x1d"
DEFAULT_ANTHROPIC_VERSION = "2023-06-01"

_TRUTHY = frozenset({"1", "true", "yes", "on"})


@dataclass(frozen=True)
class LicX1DJudgeOutput:
    """Normalized LIC X1D judge outcome."""

    judge_id: str
    evaluator_mode: str
    provider_status: str
    provider_profile: str
    model_name: str
    provider_available: bool
    provider_blocked: bool
    score: float | None
    score_scale: str | None
    normalized_score: float | None
    threshold: float
    normalized_threshold: float | None
    pass_: bool
    decisive_failure: bool
    findings: list[str] = field(default_factory=list)
    quality_flags: list[str] = field(default_factory=list)
    cited_message_spans: list[str] = field(default_factory=list)
    remediation_suggestions: list[str] = field(default_factory=list)
    exact_provider_error: str | None = None
    packet_hash: str = ""
    output_hash: str = ""
    rubric_version: str = JUDGE_RUBRIC_VERSION
    attempts: int = 1
    latency_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["pass"] = data.pop("pass_")
        return data


def run_lic_x1d_llm_judge(
    *,
    draft: Mapping[str, Any],
    report: Mapping[str, Any],
    evidence: Mapping[str, Any],
    policy: Mapping[str, Any],
    x2_gate_summary: Mapping[str, Any],
    x2_gates_passed: bool,
) -> LicX1DJudgeOutput:
    """Run the LIC X1D quality judge or return a normalized blocked outcome."""
    packet = build_lic_x1d_judge_packet(
        draft=draft,
        report=report,
        evidence=evidence,
        policy=policy,
        x2_gate_summary=x2_gate_summary,
        x2_gates_passed=x2_gates_passed,
    )
    packet_hash = _stable_hash(packet)
    settings = _resolve_settings(policy)

    if not x2_gates_passed:
        return _blocked_output(
            "SKIPPED_X2_FAILED",
            "SKIPPED_X2_FAILED",
            "X1D quality judge skipped because deterministic X2 gates did not pass.",
            packet_hash=packet_hash,
            settings=settings,
            provider_blocked=False,
        )

    support_status = str(evidence.get("support_status", "") or "").upper()
    if support_status in {"WEAK", "EMPTY"}:
        return _blocked_output(
            "SKIPPED_C0_EVIDENCE_WEAK",
            "SKIPPED_C0_EVIDENCE_WEAK",
            "X1D cannot compensate for weak or empty C0 evidence.",
            packet_hash=packet_hash,
            settings=settings,
            provider_blocked=False,
        )

    if _truthy_env("APPS_LIC_TEST_X1D_JUDGE_STUB"):
        return _test_stub_output(packet, packet_hash=packet_hash, settings=settings)

    if os.environ.get("PYTEST_CURRENT_TEST") and not _truthy_env("APPS_LIC_ENABLE_NETWORK_TESTS"):
        return _blocked_output(
            "BLOCKED_PROVIDER_UNAVAILABLE",
            "NETWORK_TESTS_NOT_ENABLED",
            "LIC X1D judge network calls are disabled under pytest.",
            packet_hash=packet_hash,
            settings=settings,
        )

    if not settings["api_key"]:
        return _blocked_output(
            "BLOCKED_PROVIDER_UNAVAILABLE",
            "ANTHROPIC_API_KEY_UNAVAILABLE",
            f"No Anthropic API key found in {settings['api_key_env_candidates']!r}.",
            packet_hash=packet_hash,
            settings=settings,
        )

    prompt = render_lic_x1d_judge_prompt(packet)
    started = time.time()
    try:
        text = _call_anthropic_messages(
            prompt=prompt,
            settings=settings,
        )
    except (
        OSError,
        TimeoutError,
        TypeError,
        ValueError,
        urllib_error.URLError,
        urllib_error.HTTPError,
    ) as exc:
        _LOGGER.info("[apps_lic.x1d_judge] provider call failed: %s", exc)
        return _blocked_output(
            "BLOCKED_PROVIDER_UNAVAILABLE",
            "GATEWAY_EXCEPTION",
            str(exc),
            packet_hash=packet_hash,
            settings=settings,
            latency_ms=(time.time() - started) * 1000.0,
        )

    parsed = _extract_json(text)
    if not parsed:
        return _blocked_output(
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "Could not parse LIC X1D judge JSON.",
            packet_hash=packet_hash,
            settings=settings,
            latency_ms=(time.time() - started) * 1000.0,
        )
    return _model_backed_output(
        parsed,
        packet_hash=packet_hash,
        settings=settings,
        latency_ms=(time.time() - started) * 1000.0,
    )


def build_lic_x1d_judge_packet(
    *,
    draft: Mapping[str, Any],
    report: Mapping[str, Any],
    evidence: Mapping[str, Any],
    policy: Mapping[str, Any],
    x2_gate_summary: Mapping[str, Any],
    x2_gates_passed: bool,
) -> dict[str, Any]:
    """Build the compact LIC X1D packet."""
    text = _message_text(draft)
    target = {
        "name": str(draft.get("target_contact_name") or ""),
        "title": str(draft.get("target_contact_title") or ""),
        "company": str(draft.get("target_contact_company") or ""),
        "recipient_class": str(
            draft.get("recipient_category") or draft.get("recipient_class") or ""
        ),
    }
    return {
        "judge_packet_version": "lic_x1d_message_quality_packet_v1",
        "judge_task": "GRADE_ONLY",
        "channel": "linkedin",
        "candidate_output": {
            "message_text": text,
            "character_count": len(text),
            "sentence_count": _sentence_count(text),
        },
        "target_contact": target,
        "reasoning_policy": {
            "sc_level": str(policy.get("sc_level") or ""),
            "reasoning_intensity": str(policy.get("reasoning_intensity") or ""),
            "judge_profile": str(policy.get("judge_profile") or ""),
            "max_candidates": int(policy.get("max_candidates") or 1),
        },
        "evidence_summary": {
            "support_status": str(evidence.get("support_status", "") or ""),
            "evidence_count": int(evidence.get("count", 0) or 0),
            "unsupported_claims": list(draft.get("unsupported_claims") or []),
        },
        "deterministic_gate_summary": dict(x2_gate_summary),
        "x2_gates_passed": bool(x2_gates_passed),
        "validation_issues": list(report.get("issues") or []),
        "rubric_ref": "apps_lic.engines.judges.lic_x1d_llm_judge#LIC_X1D_RUBRIC",
        "rubric_compact": [
            "specific_to_contact_company_or_role",
            "original_non_generic_opening",
            "thoughtful_asymmetric_or_operating_insight",
            "linkedin_native_low_friction_tone",
            "clear_single_ask",
            "evidence_discipline_no_new_claims",
        ],
    }


def render_lic_x1d_judge_prompt(packet: Mapping[str, Any]) -> str:
    """Render the compact JSON-only prompt for Claude Sonnet 4.6."""
    return (
        f"{_rubric()}\n\n"
        "Return ONLY one compact JSON object with this shape:\n"
        '{"score_scale":"0_to_5","score":0.0,"threshold":4.0,'
        '"pass":true,"decisive_failure":false,"findings":["short strings"],'
        '"quality_flags":["short strings"],"cited_message_spans":["short snippets"],'
        '"remediation_suggestions":["short strings"]}\n\n'
        f"JUDGE_PACKET:\n{json.dumps(packet, sort_keys=True, separators=(',', ':'))}"
    )


def _system_prompt() -> str:
    return (
        "You are a strict GRADE_ONLY judge for concise LinkedIn outreach. "
        "Return JSON only. Do not rewrite the message. Do not add facts, claims, "
        "metrics, or relationship context. Deterministic X2 gates and C0 evidence "
        "are authoritative. Evaluate subjective message quality only."
    )


def _rubric() -> str:
    return (
        "LIC_X1D_RUBRIC v1, score 0_to_5 threshold 4.0. Reward messages that are "
        "specific to the target, original, thoughtful, LinkedIn-native, low-friction, "
        "and grounded in provided evidence. Penalize generic recruiting filler, "
        "try-hard cleverness, broad claims, unsupported personalization, multi-ask "
        "friction, or anything that would not plausibly earn attention from the "
        "named recipient. If deterministic_gate_summary shows failed gates, do not "
        "claim the message passes those axes. If evidence_summary is weak/empty or "
        "unsupported_claims is non-empty, do not pass on evidence discipline."
    )


def _resolve_settings(policy: Mapping[str, Any]) -> dict[str, Any]:
    base_url = (
        os.environ.get("APPS_LIC_X1D_JUDGE_BASE_URL")
        or DEFAULT_BASE_URL
    )
    model = (
        os.environ.get("APPS_LIC_X1D_JUDGE_MODEL")
        or os.environ.get("APPS_LIC_ANTHROPIC_JUDGE_MODEL")
        or os.environ.get("ANTHROPIC_MODEL")
        or DEFAULT_MODEL
    )
    api_key, api_key_env_candidates = _resolve_anthropic_api_key()
    return {
        "base_url": base_url,
        "model": model,
        "provider_profile": str(
            policy.get("x1d_provider_profile")
            or os.environ.get("APPS_LIC_X1D_JUDGE_PROVIDER_PROFILE")
            or DEFAULT_PROVIDER_PROFILE
        ),
        "api_key": api_key,
        "api_key_env_candidates": api_key_env_candidates,
        "anthropic_version": os.environ.get("APPS_LIC_X1D_ANTHROPIC_VERSION")
        or DEFAULT_ANTHROPIC_VERSION,
        "temperature": _float_env(
            "APPS_LIC_X1D_JUDGE_TEMPERATURE",
            float(policy.get("x1d_temperature") or DEFAULT_TEMPERATURE),
        ),
        "max_output_tokens": _int_env(
            "APPS_LIC_X1D_JUDGE_MAX_OUTPUT_TOKENS",
            DEFAULT_MAX_OUTPUT_TOKENS,
        ),
        "timeout_seconds": _float_env("APPS_LIC_X1D_JUDGE_TIMEOUT_SECONDS", 45.0),
    }


def _resolve_anthropic_api_key() -> tuple[str, list[str]]:
    candidates = ["APPS_LIC_X1D_JUDGE_API_KEY", "ANTHROPIC_API_KEY"]
    for name in candidates:
        raw = str(os.environ.get(name) or "").strip()
        if raw:
            return raw, candidates
    return "", candidates


def _call_anthropic_messages(
    *,
    prompt: str,
    settings: Mapping[str, Any],
) -> str:
    payload = {
        "model": settings["model"],
        "max_tokens": int(settings["max_output_tokens"]),
        "temperature": float(settings["temperature"]),
        "system": _system_prompt(),
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }
    req = urllib_request.Request(
        str(settings["base_url"]),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": str(settings["api_key"]),
            "anthropic-version": str(settings["anthropic_version"]),
        },
        method="POST",
    )
    with urllib_request.urlopen(req, timeout=float(settings["timeout_seconds"])) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    data = json.loads(raw)
    parts = data.get("content") if isinstance(data, dict) else None
    if not isinstance(parts, list):
        return ""
    text_parts: list[str] = []
    for part in parts:
        if isinstance(part, Mapping) and part.get("type") == "text":
            text_parts.append(str(part.get("text") or ""))
    return "\n".join(text_parts).strip()


def _model_backed_output(
    parsed: Mapping[str, Any],
    *,
    packet_hash: str,
    settings: Mapping[str, Any],
    latency_ms: float,
) -> LicX1DJudgeOutput:
    score_scale = str(parsed.get("score_scale") or "").strip()
    try:
        score = float(parsed.get("score", 0.0))
        threshold = float(parsed.get("threshold", DEFAULT_THRESHOLD))
    except (TypeError, ValueError):
        return _blocked_output(
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            "LIC X1D judge score or threshold was not numeric.",
            packet_hash=packet_hash,
            settings=settings,
            latency_ms=latency_ms,
        )
    normalized = _normalize_score(score, threshold, score_scale)
    if normalized is None:
        return _blocked_output(
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            f"Invalid LIC X1D score contract: scale={score_scale!r} score={score} threshold={threshold}",
            packet_hash=packet_hash,
            settings=settings,
            latency_ms=latency_ms,
        )
    normalized_score, normalized_threshold = normalized
    decisive = bool(parsed.get("decisive_failure", False))
    passed = normalized_score >= normalized_threshold and not decisive
    body = dict(parsed)
    output_hash = hashlib.sha256(
        json.dumps(body, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]
    return LicX1DJudgeOutput(
        judge_id=JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
        evaluator_mode="MODEL_BACKED",
        provider_status="MODEL_BACKED_PASS" if passed else "MODEL_BACKED_FAIL",
        provider_profile=str(settings["provider_profile"]),
        model_name=str(settings["model"]),
        provider_available=True,
        provider_blocked=False,
        score=score,
        score_scale=score_scale,
        normalized_score=normalized_score,
        threshold=threshold,
        normalized_threshold=normalized_threshold,
        pass_=passed,
        decisive_failure=decisive,
        findings=_string_list(parsed.get("findings"), limit=6),
        quality_flags=_string_list(parsed.get("quality_flags"), limit=6),
        cited_message_spans=_string_list(parsed.get("cited_message_spans"), limit=4),
        remediation_suggestions=_string_list(parsed.get("remediation_suggestions"), limit=4),
        packet_hash=packet_hash,
        output_hash=output_hash,
        latency_ms=round(float(latency_ms), 3),
    )


def _test_stub_output(
    packet: Mapping[str, Any],
    *,
    packet_hash: str,
    settings: Mapping[str, Any],
) -> LicX1DJudgeOutput:
    text = str((packet.get("candidate_output") or {}).get("message_text") or "")
    lowered = text.lower()
    generic = any(
        phrase in lowered
        for phrase in (
            "potential synergies",
            "i noticed your role",
            "i believe my background aligns",
            "given your expertise",
        )
    )
    specificity = any(
        term in lowered
        for term in ("aig", "underwriting", "claims", "agentic", "governance", "production ai")
    )
    thoughtful = any(
        term in lowered
        for term in ("operating-model", "operating model", "not slideware", "execution gap")
    )
    low_friction = any(
        term in lowered
        for term in ("worth a brief", "quick chat", "resume review", "open to")
    )
    score = 4.4
    findings: list[str] = ["test_stub_model_quality_pass"]
    flags: list[str] = []
    if generic:
        score -= 1.4
        findings.append("generic_phrase_detected")
        flags.append("generic")
    if not specificity:
        score -= 0.7
        findings.append("specificity_thin")
    if not thoughtful:
        score -= 0.5
        findings.append("thoughtfulness_thin")
    if not low_friction:
        score -= 0.4
        findings.append("low_friction_ask_missing")
    score = max(0.0, min(5.0, score))
    passed = score >= DEFAULT_THRESHOLD
    return LicX1DJudgeOutput(
        judge_id=JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
        evaluator_mode="TEST_STUB",
        provider_status="TEST_STUB_PASS" if passed else "TEST_STUB_FAIL",
        provider_profile=str(settings["provider_profile"]),
        model_name=str(settings["model"]),
        provider_available=True,
        provider_blocked=False,
        score=round(score, 3),
        score_scale="0_to_5",
        normalized_score=round(score / 5.0, 3),
        threshold=DEFAULT_THRESHOLD,
        normalized_threshold=DEFAULT_THRESHOLD / 5.0,
        pass_=passed,
        decisive_failure=False,
        findings=findings[:6],
        quality_flags=flags[:6],
        cited_message_spans=[],
        remediation_suggestions=[] if passed else ["Increase specificity and remove generic phrasing."],
        packet_hash=packet_hash,
        output_hash=_stable_hash({"score": score, "findings": findings})[:16],
        latency_ms=0.0,
    )


def _blocked_output(
    evaluator_mode: str,
    provider_status: str,
    error: str,
    *,
    packet_hash: str,
    settings: Mapping[str, Any],
    provider_blocked: bool = True,
    latency_ms: float = 0.0,
) -> LicX1DJudgeOutput:
    return LicX1DJudgeOutput(
        judge_id=JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
        evaluator_mode=evaluator_mode,
        provider_status=provider_status,
        provider_profile=str(settings["provider_profile"]),
        model_name=str(settings["model"]),
        provider_available=not provider_blocked,
        provider_blocked=provider_blocked,
        score=None,
        score_scale=None,
        normalized_score=None,
        threshold=DEFAULT_THRESHOLD,
        normalized_threshold=None,
        pass_=False,
        decisive_failure=False,
        findings=["LIC X1D judge did not produce a model-backed pass."],
        quality_flags=[provider_status],
        cited_message_spans=[],
        remediation_suggestions=["Review deterministic gates, evidence, and judge provider availability."],
        exact_provider_error=error,
        packet_hash=packet_hash,
        latency_ms=round(float(latency_ms), 3),
    )


def _normalize_score(score: float, threshold: float, score_scale: str) -> tuple[float, float] | None:
    if score_scale == "0_to_1" and 0.0 <= score <= 1.0 and 0.0 <= threshold <= 1.0:
        return score, threshold
    if score_scale == "0_to_5" and 0.0 <= score <= 5.0 and 0.0 <= threshold <= 5.0:
        return score / 5.0, threshold / 5.0
    return None


def _extract_json(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        parsed = json.loads(stripped)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass
    for pattern in (r"```json\s*(.*?)\s*```", r"```\s*(.*?)\s*```"):
        match = re.search(pattern, stripped, re.S)
        if not match:
            continue
        try:
            parsed = json.loads(match.group(1).strip())
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            continue
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(stripped[start : end + 1])
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def _stable_hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()


def _message_text(draft: Mapping[str, Any]) -> str:
    return str(draft.get("message_text") or draft.get("body") or "")


def _sentence_count(text: str) -> int:
    return len([part for part in re.split(r"[.!?]+", text) if part.strip()])


def _string_list(value: Any, *, limit: int) -> list[str]:
    if isinstance(value, list):
        return [str(v)[:240] for v in value if str(v).strip()][:limit]
    if isinstance(value, str) and value.strip():
        return [value[:240]]
    return []


def _truthy_env(name: str, *, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in _TRUTHY


def _float_env(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


__all__ = [
    "DEFAULT_PROVIDER_PROFILE",
    "JUDGE_RUBRIC_VERSION",
    "LicX1DJudgeOutput",
    "build_lic_x1d_judge_packet",
    "render_lic_x1d_judge_prompt",
    "run_lic_x1d_llm_judge",
]
