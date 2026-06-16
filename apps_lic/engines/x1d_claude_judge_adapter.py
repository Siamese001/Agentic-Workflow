"""Claude X1D judge adapter for apps_lic W7.

The W7 Exit engine stays deterministic: it consumes X1DJudgeResult artifacts.
This adapter builds Claude judge prompts and converts a transport response into
those artifacts. Only the Anthropic live transport can produce a passing X1D
receipt; fake transports are rejected before Exit can clear.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from apps_lic.engines.validation_exit import (
    ANTHROPIC_MESSAGES_API,
    DEFAULT_X1D_JUDGE_MODEL,
    DEFAULT_X1D_JUDGE_PROVIDER,
    JUDGE_AVAILABLE,
    JUDGE_UNAVAILABLE,
    LIVE_CLAUDE_API_CALL,
    X1DJudgeProfile,
    X1DJudgeResult,
    required_x1d_profiles,
)
from apps_lic.config.model_profiles import resolve_x1d_judge_transport_model_id
from apps_lic.engines.whole_message_generation import (
    WholeMessageCandidate,
    WholeMessageGenerationRequest,
)


# Resolved from the model-profile SSOT (config/domain_contract/model_profiles.yaml);
# this is the model id actually sent on the Anthropic Messages API call.
DEFAULT_CLAUDE_TRANSPORT_MODEL_ID = resolve_x1d_judge_transport_model_id()
DEFAULT_CLAUDE_MAX_TOKENS = 1200


class ClaudeX1DTransport(Protocol):
    """Callable transport that sends one judge payload to Claude."""

    def __call__(self, payload: Mapping[str, Any]) -> Mapping[str, Any] | str:
        """Return a mapping or JSON string with score, passed, and issues."""


@dataclass(frozen=True)
class X1DClaudeJudgeRequest:
    judge_profile: X1DJudgeProfile
    request_id: str
    candidate_id: str
    system_prompt: str
    user_prompt: str
    transport_model_id: str = DEFAULT_CLAUDE_TRANSPORT_MODEL_ID
    temperature: float = 0.10
    max_tokens: int = DEFAULT_CLAUDE_MAX_TOKENS

    def to_transport_payload(self) -> dict[str, Any]:
        return {
            "provider": DEFAULT_X1D_JUDGE_PROVIDER,
            "model": self.judge_profile.model,
            "transport_model_id": self.transport_model_id,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "judge_id": self.judge_profile.judge_id,
            "rubric_id": self.judge_profile.rubric_id,
            "threshold": self.judge_profile.threshold,
            "request_id": self.request_id,
            "candidate_id": self.candidate_id,
            "system_prompt": self.system_prompt,
            "user_prompt": self.user_prompt,
            "response_schema": {
                "score": "float 0.0-1.0",
                "passed": "boolean",
                "issues": "list[str]",
                "required_repairs": "list[str]",
            },
        }


def build_claude_x1d_judge_request(
    *,
    request: WholeMessageGenerationRequest,
    candidate: WholeMessageCandidate,
    profile: X1DJudgeProfile,
    transport_model_id: str = DEFAULT_CLAUDE_TRANSPORT_MODEL_ID,
) -> X1DClaudeJudgeRequest:
    """Build one Claude X1D judge request from W6/W7 artifacts."""
    system_prompt = (
        "You are an independent LinkedIn outreach judge. Return only one valid JSON "
        "object with keys score, passed, issues, and required_repairs. Do not return "
        "markdown, prose, code fences, or explanations outside the JSON object. "
        "issues and required_repairs must be arrays of at most three short strings, "
        "not objects. Use compact snake_case reason strings. "
        "You cannot override deterministic X2 gates, C0 evidence, no-send policy, "
        "or Exit clearance."
    )
    user_prompt = json.dumps(
        {
            "judge_id": profile.judge_id,
            "rubric_id": profile.rubric_id,
            "rubric_role": profile.role,
            "threshold": profile.threshold,
            "channel": request.channel,
            "recipient_class": request.recipient_class,
            "message_type": request.message_type,
            "draft_text": candidate.draft_text,
            "candidate": candidate.to_packet(),
            "request": request.to_packet(),
            "proof_packet": request.proof_packet.to_packet(),
            "instructions": (
                "Score only the judge rubric. Penalize generic phrasing, unsupported "
                "claims, over-specificity without evidence, and weak LinkedIn fit. "
                "Respond only as JSON with numeric score, boolean passed, issues, "
                "and required_repairs. Keep issues and required_repairs as short "
                "string arrays, for example [\"generic_phrasing\"]."
            ),
        },
        sort_keys=True,
    )
    return X1DClaudeJudgeRequest(
        judge_profile=profile,
        request_id=request.request_id,
        candidate_id=candidate.candidate_id,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        transport_model_id=transport_model_id,
        temperature=request.reasoning_policy.judge_temperature,
    )


def _extract_json_mapping(raw: Mapping[str, Any] | str) -> dict[str, Any]:
    if isinstance(raw, Mapping):
        return dict(raw)
    text = str(raw or "").strip()
    first = text.find("{")
    last = text.rfind("}")
    if first < 0 or last <= first:
        return {}
    try:
        loaded = json.loads(text[first : last + 1])
    except json.JSONDecodeError:
        return {}
    return dict(loaded) if isinstance(loaded, Mapping) else {}


def raw_response_digest(raw: Mapping[str, Any] | str) -> str:
    """Return a non-secret digest for a Claude provider response."""
    if isinstance(raw, Mapping):
        payload = json.dumps(raw, sort_keys=True, separators=(",", ":"), default=str)
    else:
        payload = str(raw or "")
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _string_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,) if value.strip() else ()
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value if str(item).strip())
    return ()


def parse_claude_x1d_response(
    raw: Mapping[str, Any] | str,
    *,
    profile: X1DJudgeProfile,
    trust_transport_proof: bool = False,
) -> X1DJudgeResult:
    """Convert Claude JSON into the W7 X1DJudgeResult artifact."""
    payload = _extract_json_mapping(raw)
    if not payload:
        return X1DJudgeResult(
            judge_id=profile.judge_id,
            model=profile.model,
            provider=profile.provider,
            threshold=profile.threshold,
            availability_status=JUDGE_UNAVAILABLE,
            raw_response_digest=raw_response_digest(raw),
            issues=("judge_response_not_parseable",),
        )
    try:
        score = float(payload.get("score", 0.0))
    except (TypeError, ValueError):
        score = 0.0
    issues = _string_tuple(payload.get("issues"))
    repairs = _string_tuple(payload.get("required_repairs"))
    passed_raw = payload.get("passed")
    passed = bool(passed_raw) if isinstance(passed_raw, bool) else score >= profile.threshold
    transport_provenance = str(payload.get("transport_provenance") or "") if trust_transport_proof else ""
    transport_provider = str(payload.get("transport_provider") or "") if trust_transport_proof else ""
    transport_call_id = str(payload.get("transport_call_id") or "") if trust_transport_proof else ""
    return X1DJudgeResult(
        judge_id=profile.judge_id,
        model=str(payload.get("model") or profile.model or DEFAULT_X1D_JUDGE_MODEL),
        provider=str(payload.get("provider") or profile.provider or DEFAULT_X1D_JUDGE_PROVIDER),
        score=max(0.0, min(1.0, score)),
        threshold=profile.threshold,
        passed=passed,
        availability_status=str(payload.get("availability_status") or JUDGE_AVAILABLE),
        transport_provenance=transport_provenance,
        transport_provider=transport_provider,
        transport_call_id=transport_call_id,
        raw_response_digest=str(payload.get("raw_response_digest") or raw_response_digest(raw)),
        issues=issues,
        required_repairs=repairs,
    )


def run_claude_x1d_judges(
    request: WholeMessageGenerationRequest,
    candidate: WholeMessageCandidate,
    *,
    transport: ClaudeX1DTransport,
    transport_model_id: str = DEFAULT_CLAUDE_TRANSPORT_MODEL_ID,
) -> tuple[X1DJudgeResult, ...]:
    """Run required Claude X1D profiles through the supplied transport."""
    if not isinstance(transport, AnthropicClaudeX1DTransport) or not getattr(transport, "live_claude_transport", False):
        return tuple(
            X1DJudgeResult(
                judge_id=profile.judge_id,
                model=profile.model,
                provider=profile.provider,
                threshold=profile.threshold,
                availability_status=JUDGE_UNAVAILABLE,
                issues=("non_live_claude_transport_rejected",),
            )
            for profile in required_x1d_profiles(request)
        )

    results: list[X1DJudgeResult] = []
    for profile in required_x1d_profiles(request):
        judge_request = build_claude_x1d_judge_request(
            request=request,
            candidate=candidate,
            profile=profile,
            transport_model_id=transport_model_id,
        )
        try:
            raw = transport(judge_request.to_transport_payload())
        except Exception as exc:  # guardian: allow-broad-exception -- live provider transports raise heterogeneous SDK/network errors; W7 converts to unavailable judge artifact
            results.append(
                X1DJudgeResult(
                    judge_id=profile.judge_id,
                    model=profile.model,
                    provider=profile.provider,
                    threshold=profile.threshold,
                    availability_status=JUDGE_UNAVAILABLE,
                    issues=(f"judge_transport_error:{type(exc).__name__}",),
                )
            )
            continue
        results.append(parse_claude_x1d_response(raw, profile=profile, trust_transport_proof=True))
    return tuple(results)


class AnthropicClaudeX1DTransport:
    """Optional live transport backed by Anthropic's messages API."""

    live_claude_transport = True

    def __init__(
        self,
        *,
        api_key: str = "",
        model_id: str = DEFAULT_CLAUDE_TRANSPORT_MODEL_ID,
        timeout_s: float = 60.0,
        client: Any | None = None,
    ) -> None:
        self._api_key = api_key
        self._model_id = model_id
        self._timeout_s = timeout_s
        self._client = client
        self._client_injected = client is not None
        if self._client_injected:
            self.live_claude_transport = False

    def _ensure_client(self) -> Any | None:
        if self._client is not None:
            return self._client
        api_key = self._api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return None
        try:
            import anthropic  # type: ignore
        except ImportError:
            return None
        self._client = anthropic.Anthropic(api_key=api_key, timeout=self._timeout_s)
        return self._client

    def __call__(self, payload: Mapping[str, Any]) -> Mapping[str, Any] | str:
        if self._client_injected:
            return {
                "score": 0.0,
                "passed": False,
                "availability_status": JUDGE_UNAVAILABLE,
                "issues": ["injected_anthropic_client_not_live"],
            }
        client = self._ensure_client()
        if client is None:
            return {
                "score": 0.0,
                "passed": False,
                "availability_status": JUDGE_UNAVAILABLE,
                "issues": ["claude_transport_unavailable"],
            }
        try:
            response = client.messages.create(
                model=str(payload.get("transport_model_id") or self._model_id),
                max_tokens=int(payload.get("max_tokens") or DEFAULT_CLAUDE_MAX_TOKENS),
                temperature=float(payload.get("temperature") or 0.10),
                system=str(payload.get("system_prompt") or ""),
                messages=[{"role": "user", "content": str(payload.get("user_prompt") or "")}],
            )
        except Exception as exc:  # guardian: allow-broad-exception -- Anthropic SDK exposes provider/network subclasses that vary by version; surface as unavailable artifact
            return {
                "score": 0.0,
                "passed": False,
                "availability_status": JUDGE_UNAVAILABLE,
                "issues": [f"claude_transport_error:{type(exc).__name__}"],
            }
        text = ""
        for block in getattr(response, "content", []) or []:
            value = getattr(block, "text", None)
            if value:
                text += value
        parsed = _extract_json_mapping(text)
        if not parsed:
            return {
                "score": 0.0,
                "passed": False,
                "availability_status": JUDGE_UNAVAILABLE,
                "issues": ["judge_response_not_parseable"],
                "required_repairs": ["return_valid_json_with_score_passed_issues_required_repairs"],
                "raw_response_digest": raw_response_digest(text),
                "transport_provenance": LIVE_CLAUDE_API_CALL,
                "transport_provider": ANTHROPIC_MESSAGES_API,
                "transport_call_id": str(getattr(response, "id", "") or "anthropic_messages_api_response"),
                "model": DEFAULT_X1D_JUDGE_MODEL,
                "provider": DEFAULT_X1D_JUDGE_PROVIDER,
            }
        parsed["transport_provenance"] = LIVE_CLAUDE_API_CALL
        parsed["transport_provider"] = ANTHROPIC_MESSAGES_API
        parsed["transport_call_id"] = str(getattr(response, "id", "") or "anthropic_messages_api_response")
        parsed["model"] = DEFAULT_X1D_JUDGE_MODEL
        parsed["provider"] = DEFAULT_X1D_JUDGE_PROVIDER
        parsed["availability_status"] = JUDGE_AVAILABLE
        return parsed


__all__ = [
    "DEFAULT_CLAUDE_MAX_TOKENS",
    "DEFAULT_CLAUDE_TRANSPORT_MODEL_ID",
    "AnthropicClaudeX1DTransport",
    "ClaudeX1DTransport",
    "X1DClaudeJudgeRequest",
    "build_claude_x1d_judge_request",
    "parse_claude_x1d_response",
    "raw_response_digest",
    "run_claude_x1d_judges",
]
