"""LIC independent X1D LLM judge for LinkedIn message quality."""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Mapping

from apps_lic.config.model_profiles import (
    resolve_x1d_judge_model,
    resolve_x1d_judge_provider_profile,
)
from apps_lic.policy.reasoning_intensity import (
    JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
)


JUDGE_RUBRIC_VERSION = "apps_lic.v1.LIC_X1D_RUBRIC"
JUDGE_PACKET_VERSION = "lic_x1d_message_quality_packet_v1"
_DEFAULT_THRESHOLD = 4.0


@dataclass
class LicX1DJudgeOutput:
    judge_id: str = JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D
    evaluator_mode: str = "BLOCKED_PROVIDER_UNAVAILABLE"
    provider_status: str = "NETWORK_TESTS_NOT_ENABLED"
    provider_profile: str = field(default_factory=resolve_x1d_judge_provider_profile)
    model_name: str = field(default_factory=resolve_x1d_judge_model)
    provider_available: bool = False
    provider_blocked: bool = True
    score: float | None = None
    score_scale: str = "0_to_5"
    normalized_score: float | None = None
    threshold: float = _DEFAULT_THRESHOLD
    normalized_threshold: float = _DEFAULT_THRESHOLD / 5.0
    pass_: bool = False
    decisive_failure: bool = False
    findings: list[str] = field(default_factory=list)
    quality_flags: list[str] = field(default_factory=list)
    cited_message_spans: list[str] = field(default_factory=list)
    remediation_suggestions: list[str] = field(default_factory=list)
    exact_provider_error: str = ""
    packet_hash: str = ""
    output_hash: str = ""
    rubric_version: str = JUDGE_RUBRIC_VERSION

    def to_dict(self) -> dict[str, Any]:
        data = {
            "judge_id": self.judge_id,
            "evaluator_mode": self.evaluator_mode,
            "provider_status": self.provider_status,
            "provider_profile": self.provider_profile,
            "model_name": self.model_name,
            "provider_available": self.provider_available,
            "provider_blocked": self.provider_blocked,
            "score": self.score,
            "score_scale": self.score_scale,
            "normalized_score": self.normalized_score,
            "threshold": self.threshold,
            "normalized_threshold": self.normalized_threshold,
            "pass": self.pass_,
            "decisive_failure": self.decisive_failure,
            "findings": list(self.findings),
            "quality_flags": list(self.quality_flags),
            "cited_message_spans": list(self.cited_message_spans),
            "remediation_suggestions": list(self.remediation_suggestions),
            "exact_provider_error": self.exact_provider_error,
            "packet_hash": self.packet_hash,
            "output_hash": self.output_hash,
            "rubric_version": self.rubric_version,
        }
        return data


def build_lic_x1d_judge_packet(
    *,
    draft: Mapping[str, Any],
    report: Mapping[str, Any],
    evidence: Mapping[str, Any],
    policy: Mapping[str, Any],
    x2_gate_summary: Mapping[str, Any],
    x2_gates_passed: bool,
) -> dict[str, Any]:
    message_text = str(draft.get("message_text") or draft.get("body") or "").strip()
    recipient_class = str(draft.get("recipient_class") or draft.get("recipient_category") or "").strip()
    return {
        "judge_packet_version": JUDGE_PACKET_VERSION,
        "judge_task": "GRADE_ONLY",
        "judge_id": JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
        "rubric_ref": JUDGE_RUBRIC_VERSION,
        "channel": str(draft.get("channel") or "linkedin").strip(),
        "candidate_output": {
            "message_text": message_text,
            "sentence_count": _sentence_count(message_text),
            "candidate_count": int(draft.get("candidate_count") or 1),
        },
        "target_contact": {
            "name": str(draft.get("target_contact_name") or "").strip(),
            "title": str(draft.get("target_contact_title") or "").strip(),
            "company": str(draft.get("target_contact_company") or "").strip(),
            "recipient_class": recipient_class,
        },
        "validation_passed": bool(report.get("passed", False)),
        "validation_issues": _string_list(report.get("issues")),
        "evidence": dict(evidence),
        "policy": dict(policy),
        "x2_gate_summary": dict(x2_gate_summary),
        "x2_gates_passed": bool(x2_gates_passed),
    }


def render_lic_x1d_judge_prompt(packet: Mapping[str, Any]) -> str:
    packed = json.dumps(packet, sort_keys=True, separators=(",", ":"))
    return (
        "LIC_X1D_RUBRIC\n"
        "Grade only LinkedIn originality, specificity, and thoughtfulness. "
        "Return one compact JSON object with score_scale, score, threshold, pass, "
        "decisive_failure, findings, quality_flags, cited_message_spans, and "
        "remediation_suggestions.\n"
        f"JUDGE_PACKET:\n{packed}"
    )


def run_lic_x1d_llm_judge(
    *,
    draft: Mapping[str, Any],
    report: Mapping[str, Any],
    evidence: Mapping[str, Any],
    policy: Mapping[str, Any],
    x2_gate_summary: Mapping[str, Any],
    x2_gates_passed: bool,
) -> LicX1DJudgeOutput:
    packet = build_lic_x1d_judge_packet(
        draft=draft,
        report=report,
        evidence=evidence,
        policy=policy,
        x2_gate_summary=x2_gate_summary,
        x2_gates_passed=x2_gates_passed,
    )
    packet_hash = _digest(packet)
    if not x2_gates_passed:
        return LicX1DJudgeOutput(
            evaluator_mode="SKIPPED_X2_FAILED",
            provider_status="SKIPPED_X2_FAILED",
            pass_=False,
            packet_hash=packet_hash,
        )

    support_status = str(evidence.get("support_status") or "").upper()
    if support_status in {"WEAK", "EMPTY"}:
        return LicX1DJudgeOutput(
            evaluator_mode="SKIPPED_C0_EVIDENCE_WEAK",
            provider_status="SKIPPED_C0_EVIDENCE_WEAK",
            pass_=False,
            exact_provider_error="C0 evidence support is weak or empty; X1D cannot override evidence authority.",
            packet_hash=packet_hash,
        )

    if _truthy(os.environ.get("APPS_LIC_TEST_X1D_JUDGE_STUB")):
        return _run_test_stub(packet, packet_hash)

    if os.environ.get("PYTEST_CURRENT_TEST"):
        return LicX1DJudgeOutput(
            evaluator_mode="BLOCKED_PROVIDER_UNAVAILABLE",
            provider_status="NETWORK_TESTS_NOT_ENABLED",
            provider_available=False,
            provider_blocked=True,
            packet_hash=packet_hash,
        )

    return _run_model_backed(packet, packet_hash)


def _run_test_stub(packet: Mapping[str, Any], packet_hash: str) -> LicX1DJudgeOutput:
    message = str(((packet.get("candidate_output") or {}) if isinstance(packet, Mapping) else {}).get("message_text") or "")
    generic = "potential synergies" in message.lower() or len(message.split()) < 12
    score = 2.0 if generic else 4.5
    findings = ["generic_phrase_detected"] if generic else ["specific_and_thoughtful"]
    return LicX1DJudgeOutput(
        evaluator_mode="TEST_STUB",
        provider_status="TEST_STUB_FAIL" if generic else "TEST_STUB_PASS",
        provider_available=True,
        provider_blocked=False,
        score=score,
        normalized_score=score / 5.0,
        pass_=not generic,
        findings=findings,
        packet_hash=packet_hash,
        output_hash=_digest({"packet_hash": packet_hash, "score": score, "findings": findings}),
    )


def _run_model_backed(packet: Mapping[str, Any], packet_hash: str) -> LicX1DJudgeOutput:
    prompt = render_lic_x1d_judge_prompt(packet)
    try:
        llm_client = importlib.import_module("apps_lic.integrations.llm_client")
        client = llm_client.OpenAI()
        response = client.chat.completions.create(
            model=resolve_x1d_judge_model(),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
    except Exception as exc:  # guardian: provider SDK/client doubles expose heterogeneous runtime failures
        return LicX1DJudgeOutput(
            evaluator_mode="BLOCKED_PROVIDER_UNAVAILABLE",
            provider_status="PROVIDER_UNAVAILABLE",
            provider_available=False,
            provider_blocked=True,
            exact_provider_error=f"{type(exc).__name__}: {exc}",
            packet_hash=packet_hash,
        )

    text = ""
    if getattr(response, "choices", None):
        text = str(getattr(response.choices[0].message, "content", "") or "")
    payload = _parse_json_object(text)
    if payload is None:
        return LicX1DJudgeOutput(
            evaluator_mode="MODEL_BACKED",
            provider_status="BLOCKED_RESPONSE_PARSE_ERROR",
            provider_available=True,
            provider_blocked=True,
            pass_=False,
            exact_provider_error="model response was not parseable JSON",
            packet_hash=packet_hash,
        )

    normalized = _normalize_provider_payload(payload)
    if normalized is None:
        return LicX1DJudgeOutput(
            evaluator_mode="MODEL_BACKED",
            provider_status="BLOCKED_SCHEMA_VALIDATION_ERROR",
            provider_available=True,
            provider_blocked=True,
            pass_=False,
            exact_provider_error="model response failed LIC X1D schema validation",
            packet_hash=packet_hash,
            output_hash=_digest(payload),
        )

    passed = bool(normalized["pass"]) and not bool(normalized["decisive_failure"])
    return LicX1DJudgeOutput(
        evaluator_mode="MODEL_BACKED",
        provider_status="MODEL_BACKED_PASS" if passed else "MODEL_BACKED_FAIL",
        provider_available=True,
        provider_blocked=False,
        score=normalized["score"],
        score_scale=normalized["score_scale"],
        normalized_score=normalized["normalized_score"],
        threshold=normalized["threshold"],
        normalized_threshold=normalized["normalized_threshold"],
        pass_=passed,
        decisive_failure=normalized["decisive_failure"],
        findings=normalized["findings"],
        quality_flags=normalized["quality_flags"],
        cited_message_spans=normalized["cited_message_spans"],
        remediation_suggestions=normalized["remediation_suggestions"],
        packet_hash=packet_hash,
        output_hash=_digest(payload),
    )


def _normalize_provider_payload(payload: Mapping[str, Any]) -> dict[str, Any] | None:
    scale = str(payload.get("score_scale") or "").strip()
    if scale not in {"0_to_5", "0_to_1"}:
        return None
    try:
        score = float(payload["score"])
        threshold = float(payload["threshold"])
    except (KeyError, TypeError, ValueError):
        return None
    if scale == "0_to_5":
        if not (0.0 <= score <= 5.0 and 0.0 <= threshold <= 5.0):
            return None
        normalized_score = score / 5.0
        normalized_threshold = threshold / 5.0
    else:
        if not (0.0 <= score <= 1.0 and 0.0 <= threshold <= 1.0):
            return None
        normalized_score = score
        normalized_threshold = threshold
    return {
        "score_scale": scale,
        "score": score,
        "threshold": threshold,
        "normalized_score": normalized_score,
        "normalized_threshold": normalized_threshold,
        "pass": bool(payload.get("pass", score >= threshold)),
        "decisive_failure": bool(payload.get("decisive_failure", False)),
        "findings": _string_list(payload.get("findings")),
        "quality_flags": _string_list(payload.get("quality_flags")),
        "cited_message_spans": _string_list(payload.get("cited_message_spans")),
        "remediation_suggestions": _string_list(payload.get("remediation_suggestions")),
    }


def _parse_json_object(text: str) -> dict[str, Any] | None:
    cleaned = str(text or "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end < start:
        return None
    try:
        loaded = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError:
        return None
    return dict(loaded) if isinstance(loaded, Mapping) else None


def _sentence_count(text: str) -> int:
    parts = [p for p in re.split(r"[.!?]+", str(text or "")) if p.strip()]
    return len(parts)


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item).strip()]
    return []


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


__all__ = [
    "JUDGE_RUBRIC_VERSION",
    "LicX1DJudgeOutput",
    "build_lic_x1d_judge_packet",
    "render_lic_x1d_judge_prompt",
    "run_lic_x1d_llm_judge",
]
