"""X1D LLM-as-Judge panel for executive summary runtime slice.

Provider-backed judges with full normalization per X1D adapter spec.
"""
from __future__ import annotations

import json
import os
import re
import hashlib
import time
import urllib.error
import urllib.request
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping


JUDGE_RUBRIC_VERSION = "executive_summary_x1d_v1"
DEFAULT_THRESHOLD = 0.80
VALID_SCORE_SCALES = frozenset({"0_to_1", "0_to_5"})
JUDGE_REQUIRED_FIELDS = ("score_scale", "score", "threshold", "pass")
def _resolved_apps_rg_google_judge_max_output_tokens() -> int:
    raw = (
        os.environ.get("APPS_RG_GOOGLE_JUDGE_MAX_OUTPUT_TOKENS", "").strip()
        or os.environ.get("APPS_RG_GEMINI_JUDGE_MAX_OUTPUT_TOKENS", "").strip()
    )
    default = os.environ.get("APPS_RG_GEMINI_JUDGE_MAX_OUTPUT_TOKENS", "4096").strip()
    use = raw or default
    try:
        return max(1, int(use))
    except ValueError:
        return 4096


GOOGLE_AI_JUDGE_MAX_OUTPUT_TOKENS = _resolved_apps_rg_google_judge_max_output_tokens()
# Back-compat alias for tests and external imports (same resolution as Google AI judge path).
GEMINI_JUDGE_MAX_OUTPUT_TOKENS = GOOGLE_AI_JUDGE_MAX_OUTPUT_TOKENS
ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS = int(os.environ.get("APPS_RG_ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS", "1024"))


def _resolved_openai_judge_max_completion_tokens(*, attempt: int = 1) -> int:
    """Budget for gpt-5.x judge completions; escalates on retry (reasoning can consume the cap)."""
    raw = os.environ.get("APPS_RG_OPENAI_JUDGE_MAX_COMPLETION_TOKENS", "4096").strip()
    try:
        base = max(512, int(raw))
    except ValueError:
        base = 4096
    return min(8192, base * min(max(1, attempt), 2))


def _x1d_judge_max_attempts() -> int:
    raw = os.environ.get("APPS_RG_X1D_JUDGE_MAX_ATTEMPTS", "3").strip()
    try:
        return max(1, min(5, int(raw)))
    except ValueError:
        return 3


def _judge_retry_backoff_seconds(attempt: int) -> float:
    return min(4.0, 0.5 * (2 ** max(0, attempt - 1)))


def _is_retriable_judge_output(output: JudgeOutput) -> bool:
    """True when another bounded judge attempt may recover (parse/empty/schema)."""
    if not output.provider_blocked:
        return False
    status = str(output.provider_status or "")
    err = str(output.exact_provider_error or "").lower()
    if status == "BLOCKED_RESPONSE_PARSE_ERROR":
        return any(
            needle in err
            for needle in (
                "extract json",
                "parse error",
                "no judge text",
                "empty",
                "finish_reason",
                "finishreason",
                "incomplete judge json",
                "completion token",
                "reasoning",
            )
        )
    if status == "BLOCKED_SCHEMA_VALIDATION_ERROR":
        return True
    return False


def _invoke_judge_with_bounded_retries(
    invoke: Callable[[int], JudgeOutput],
    *,
    provider_key: str,
) -> JudgeOutput:
    max_attempts = _x1d_judge_max_attempts()
    last: JudgeOutput | None = None
    for attempt in range(1, max_attempts + 1):
        last = invoke(attempt)
        if last is None:
            break
        if not _is_retriable_judge_output(last) or attempt >= max_attempts:
            return last
        time.sleep(_judge_retry_backoff_seconds(attempt))
    assert last is not None
    return last

JUDGE_COMPACT_OUTPUT = """
Return ONLY one compact JSON object. No markdown fences, no prose before or after, no nested objects.
Required shape (findings and remediation_suggestions must be arrays of short strings only):
{"score_scale":"0_to_5","score":0.0,"threshold":4.0,"pass":true,"decisive_failure":false,"findings":["..."],"cited_sentence_indexes":[1],"remediation_suggestions":[]}
At most 6 short strings in findings and 4 in remediation_suggestions.
""".strip()

JUDGE_COMPACT_SYSTEM = (
    "You are a strict executive resume judge. Output a single compact JSON object only. "
    "No markdown fences, no explanatory prose, no nested finding objects."
)

GEMINI_JUDGE_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "score_scale": {"type": "string", "enum": ["0_to_1", "0_to_5"]},
        "score": {"type": "number"},
        "threshold": {"type": "number"},
        "pass": {"type": "boolean"},
        "decisive_failure": {"type": "boolean"},
        "findings": {"type": "array", "items": {"type": "string"}},
        "cited_sentence_indexes": {"type": "array", "items": {"type": "integer"}},
        "remediation_suggestions": {"type": "array", "items": {"type": "string"}},
    },
    "required": list(JUDGE_REQUIRED_FIELDS)
    + ["decisive_failure", "findings", "cited_sentence_indexes", "remediation_suggestions"],
}

JUDGE_SCORE_SCHEMA = """
Score contract (mandatory - every judge response MUST comply):
- Include score_scale as exactly one of: "0_to_1" or "0_to_5". Do not omit score_scale.
- If score_scale is "0_to_1": score and threshold MUST each be a number from 0.0 through 1.0 inclusive.
- If score_scale is "0_to_5": score and threshold MUST each be a number from 0.0 through 5.0 inclusive.
- Forbidden: 0_to_10 scales, percentage scores (0–100), or values like score=9.2 with threshold=8.0.
- Do not infer scale from magnitude; declare score_scale explicitly and keep score/threshold within that scale.
""".strip()

RUBRIC = f"""
You are evaluating one executive resume **executive summary paragraph** against the same bar as the
``executive_summary.generate_scratch_v1`` north star: **polished SVP / agentic-AI-platform synthesis**, not bullet stacks,
not internal label/colon stitching, not one-sentence-per-fact proof, not meta narration.
Return JSON only with: score_scale, score, threshold, pass, decisive_failure, findings, cited_sentence_indexes, remediation_suggestions.

{JUDGE_SCORE_SCHEMA}

Rubric dimensions:
1. factual_support: claims appear supported by the provided claim ledger and source fact IDs (no JD/briefing-as-proof).
2. executive_signal: SVP/CTO-level narrative - platform, runtime, governance, retrieval, orchestration, evaluation, commercialization **woven**, not listed.
3. resume_voice: concise, credible, human executive style; **synthesis**, not recruiter filler, hype, or generic AI prose.
4. ats_alignment_without_keyword_stuffing: relevant to target role via emphasis only; no JD mirroring or stuffing.
5. anti_overfit: no JD-as-proof, no briefing-as-proof, no target company as candidate experience, no **copy-paste of style-example metrics/credentials** absent from claim ledger support.
6. synthesis_quality: **executive paragraph** flow; penalize sentence-stacked proofs, colon-label stitching, visible process language
   (e.g. “selected facts”, “active-voice delivery”, “governance discipline” as filler), and excessive naked capability lists without narrative.

**Target shape:** **exactly six dense sentences** (one executive paragraph, max 140 words); commercially aware technical platform story; metrics/credentials only when ledger-backed.

Decisive failure triggers:
- unsupported business metric or credential (including pasted gold-example numbers/titles not in ledger)
- target company presented as candidate experience
- first-person narrative
- copied JD phrase longer than four words
- generic opener or hype/filler
- summary is mechanically sentence-stacked proof rather than narrative synthesis
- obvious colon-label / fact-title stitching in prose
""".strip()


@dataclass
class JudgeOutput:
    """Complete judge output with provider status tracking."""
    judge_id: str
    provider_name: str
    provider_key: str
    evaluator_mode: str  # MODEL_BACKED | MOCKED | BLOCKED_*
    provider_status: str  # MODEL_BACKED_PASS | MODEL_BACKED_FAIL | BLOCKED_*
    model_name: str
    provider_available: bool
    provider_blocked: bool  # True for BLOCKED_* modes, False otherwise
    exact_provider_error: str | None
    raw_response_ref: str | None = None  # Path to preserved raw response
    original_model: str | None = None  # For fallback tracking
    fallback_model: str | None = None  # For fallback tracking
    rubric_version: str = JUDGE_RUBRIC_VERSION
    input_hash: str = ""
    output_hash: str = ""
    score: float | None = None
    score_scale: str | None = None  # "0_to_5" or "0_to_1"
    normalized_score: float | None = None  # 0.0 to 1.0
    threshold: float = DEFAULT_THRESHOLD
    normalized_threshold: float | None = None  # 0.0 to 1.0
    pass_: bool = False
    decisive_failure: bool = False  # False for blocked providers
    findings: list[str] = field(default_factory=list)
    cited_sentence_indexes: list[int] = field(default_factory=list)
    remediation_suggestions: list[str] = field(default_factory=list)
    model_requested: str | None = None
    model_actual: str | None = None
    reasoning_effort: str | None = None
    judge_packet_hash: str | None = None
    judge_packet_ref: str | None = None
    candidate_output_ref: str | None = None
    allowed_fact_packet_ref: str | None = None
    rubric_ref: str | None = None
    rationale: str | None = None
    fail_reasons: list[str] = field(default_factory=list)
    unsupported_claims: list[str] = field(default_factory=list)
    quality_flags: list[str] = field(default_factory=list)
    mocked: bool = False
    advisory_only: bool = False
    model_tier: str | None = None
    proof_eligible_judge: bool = False
    fallback_used: bool = False
    section_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["pass"] = data.pop("pass_")
        if data.get("model_actual") is None:
            data["model_actual"] = data.get("model_name")
        if data.get("model_requested") is None:
            data["model_requested"] = data.get("model_name")
        data["mocked"] = data.get("evaluator_mode") == "MOCKED"
        if data.get("fallback_model"):
            data["fallback_used"] = True
        return data


# Provider configuration
PROVIDERS = {
    "gemini_pro": {
        "provider_name": "Gemini Pro",
        "env": "GOOGLE_API_KEY",
        # GEMINI_API_KEY is a deprecated legacy alias (same credential as Google AI Gemini).
        "env_fallbacks": ("GEMINI_API_KEY",),
        "model_env": "APPS_RG_GOOGLE_JUDGE_MODEL",
        "model_env_aliases": ("APPS_RG_GEMINI_JUDGE_MODEL",),
        "fallback_env": "GOOGLE_AI_PRO_MODEL",
        "fallback_env_aliases": ("GEMINI_PRO_MODEL", "GOOGLE_AI_MODEL", "GEMINI_MODEL"),
        "default_model": "gemini-2.0-flash",
    },
    "openai_chatgpt": {
        "provider_name": "OpenAI ChatGPT",
        "env": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL",
        "default_model": "gpt-4o",
    },
    "anthropic_claude": {
        "provider_name": "Anthropic Claude",
        "env": "ANTHROPIC_API_KEY",
        "model_env": "APPS_RG_ANTHROPIC_JUDGE_MODEL",  # Specific judge model env
        "fallback_env": "ANTHROPIC_MODEL",  # Fallback to general model
        "default_model": "claude-3-5-sonnet-20241022",
    },
}


def resolve_x1d_provider_credentials(provider_key: str, environ: Mapping[str, str]) -> tuple[str, list[str]]:
    """Return `(api_key, env_vars_consulted_in_order)` for preflight parity with lane judge execution."""
    meta = PROVIDERS.get(provider_key)
    if not meta:
        return "", []
    primary = str(meta.get("env") or "")
    consulted: list[str] = []

    # Gemini: canonical GOOGLE_API_KEY; GEMINI_API_KEY is a deprecated alias.
    if provider_key == "gemini_pro":
        for name in (primary, *[str(x) for x in (meta.get("env_fallbacks") or ())]):
            if not name or name in consulted:
                continue
            consulted.append(name)
            raw = str(environ.get(name) or "").strip()
            if raw:
                return raw, consulted
        return "", consulted if consulted else ([primary] if primary else [])

    if primary:
        consulted.append(primary)
        return str(environ.get(primary) or "").strip(), consulted
    return "", consulted


def _artifact_path(
    provider_key: str,
    suffix: str,
    *,
    artifact_base: Path | None = None,
) -> Path:
    """Generate artifact path for provider artifacts.

    When ``artifact_base`` is set, files are written under that directory (per-run bundle).
    Otherwise preserve legacy layout under ``artifacts/.../executive_summary/``.
    """
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")[:-3]
    if artifact_base is not None:
        base = artifact_base
    else:
        base = Path("artifacts/apps_rg/runtime_proofs/executive_summary")
    base.mkdir(parents=True, exist_ok=True)
    return base / f"x1d_{provider_key}_{suffix}_{ts}.json"


def _write_artifact(path: Path, data: Any) -> str:
    """Write artifact and return path string."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    return str(path)


def _validate_judge_score_contract(
    raw_score: float,
    raw_threshold: float,
    declared: str | None,
) -> tuple[str | None, str | None]:
    """Validate declared score_scale and numeric ranges; never infer scale from magnitude."""
    if not declared or declared not in VALID_SCORE_SCALES:
        return None, (
            f"Invalid or missing score_scale: {declared!r}; "
            f"must be one of {sorted(VALID_SCORE_SCALES)}"
        )
    if declared == "0_to_1":
        if not (0.0 <= raw_score <= 1.0 and 0.0 <= raw_threshold <= 1.0):
            return None, (
                f"score/threshold out of range for 0_to_1: score={raw_score}, threshold={raw_threshold}"
            )
    elif declared == "0_to_5":
        if not (0.0 <= raw_score <= 5.0 and 0.0 <= raw_threshold <= 5.0):
            return None, (
                f"score/threshold out of range for 0_to_5: score={raw_score}, threshold={raw_threshold}"
            )
    return declared, None


def _compute_normalized(
    raw_score: float,
    raw_threshold: float,
    score_scale: str,
) -> tuple[float, float]:
    """Map raw judge score/threshold to 0..1 using an explicit scale."""
    if score_scale == "0_to_1":
        return raw_score, raw_threshold
    if score_scale == "0_to_5":
        return raw_score / 5.0, raw_threshold / 5.0
    raise ValueError(f"invalid score_scale: {score_scale}")


def _resolve_gemini_model(
    meta: dict[str, Any],
    *,
    section_id: str = "executive_summary",
) -> tuple[str, str]:
    """Resolve Google AI judge model via section_judge_profile tier matrix."""
    from apps_rg.runtime.judges.section_judge_profile import resolve_section_proof_judge_model

    resolution = resolve_section_proof_judge_model(section_id, "gemini_pro")
    if resolution.model_actual and not resolution.blocked:
        return resolution.model_actual, resolution.model_source
    return str(meta.get("default_model", "gemini-2.0-flash")), "default"


def _resolve_anthropic_model(
    meta: dict[str, Any],
    *,
    section_id: str = "executive_summary",
) -> tuple[str, str]:
    """Resolve Anthropic judge model via section_judge_profile tier matrix."""
    from apps_rg.runtime.judges.section_judge_profile import resolve_section_proof_judge_model

    resolution = resolve_section_proof_judge_model(section_id, "anthropic_claude")
    if resolution.model_actual and not resolution.blocked:
        return resolution.model_actual, resolution.model_source
    default = str(meta.get("default_model", "claude-3-5-sonnet-20241022"))
    return default, "default"


def _normalize_judge_result(raw: dict[str, Any]) -> dict[str, Any]:
    """Coerce provider-native judge JSON into the executive_summary_x1d schema."""
    result = dict(raw)
    result["score"] = float(result.get("score", 0.0))
    result["threshold"] = float(result.get("threshold", DEFAULT_THRESHOLD))

    decisive = result.get("decisive_failure", False)
    if isinstance(decisive, str):
        result["decisive_failure"] = decisive.strip().lower() not in ("", "false", "none", "[]", "{}")
    else:
        result["decisive_failure"] = bool(decisive)

    findings = result.get("findings", [])
    if isinstance(findings, dict):
        flat: list[str] = []
        for key, value in findings.items():
            if isinstance(value, dict):
                note = value.get("notes") or value.get("note") or json.dumps(value, sort_keys=True)
                flat.append(f"{key}: {note}")
            else:
                flat.append(f"{key}: {value}")
        result["findings"] = flat
    elif not isinstance(findings, list):
        result["findings"] = [str(findings)] if findings else []

    cited = result.get("cited_sentence_indexes", [])
    if isinstance(cited, dict):
        result["cited_sentence_indexes"] = [int(k) if str(k).isdigit() else k for k in cited.keys()]
    elif not isinstance(cited, list):
        result["cited_sentence_indexes"] = []

    remed = result.get("remediation_suggestions", [])
    if not isinstance(remed, list):
        result["remediation_suggestions"] = [remed] if remed else []

    if "pass" not in result:
        result["pass"] = (
            float(result["score"]) >= float(result["threshold"]) and not result["decisive_failure"]
        )
    return result


def _build_judge_user_prompt(resume_display_text: str, claim_ledger: list[dict[str, Any]]) -> str:
    """Build provider judge user prompt with compact JSON-only output contract."""
    return (
        f"{RUBRIC}\n\n{JUDGE_COMPACT_OUTPUT}\n\n"
        f"RESUME_DISPLAY_TEXT:\n{resume_display_text}\n\n"
        f"CLAIM_LEDGER:\n{json.dumps(claim_ledger, separators=(',', ':'))}"
    )


def _gemini_generation_config() -> dict[str, Any]:
    """Gemini generationConfig for compact schema-valid judge JSON."""
    return {
        "temperature": 0.1,
        "maxOutputTokens": GOOGLE_AI_JUDGE_MAX_OUTPUT_TOKENS,
        "responseMimeType": "application/json",
        "responseSchema": GEMINI_JUDGE_RESPONSE_SCHEMA,
    }


def _extract_anthropic_message_text(data: dict[str, Any]) -> str:
    """Extract assistant text from Anthropic messages API content blocks."""
    chunks: list[str] = []
    for block in data.get("content") or []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text" and block.get("text"):
            chunks.append(str(block["text"]))
    return "".join(chunks)


def _gemini_judge_max_retries() -> int:
    raw = (
        os.environ.get("APPS_RG_GOOGLE_JUDGE_MAX_RETRIES", "").strip()
        or os.environ.get("APPS_RG_GEMINI_JUDGE_MAX_RETRIES", "4").strip()
    )
    try:
        return max(0, min(12, int(raw)))
    except ValueError:
        return 4


# Query parameter names whose values must never appear in X1D provider_request URL artifacts.
_SENSITIVE_URL_QUERY_KEYS = frozenset(
    {
        "key",
        "api_key",
        "access_token",
        "token",
        "authorization",
        "auth",
        "client_secret",
    }
)


def _sanitize_request_url_for_x1d_artifact(url: str) -> tuple[str, tuple[str, ...]]:
    """Strip credential-bearing query keys entirely (omit names and values from serialized URL).

    Returns ``(safe_url, omitted_param_names_sorted_unique)``. Host, path, scheme unchanged.
    Non-sensitive query pairs are preserved for observability.
    """
    stripped = str(url or "").strip()
    if not stripped:
        return "", ()
    try:
        parsed = urlparse(stripped)
    except ValueError:
        return stripped, ()
    if not parsed.query:
        return stripped, ()
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    omitted: list[str] = []
    kept: list[tuple[str, str]] = []
    for name, value in pairs:
        lk = name.lower()
        if lk in _SENSITIVE_URL_QUERY_KEYS:
            omitted.append(name)
            continue
        kept.append((name, value))
    new_query = urlencode(kept)
    safe = urlunparse(parsed._replace(query=new_query))
    uniq = tuple(sorted({str(x) for x in omitted}))
    return safe, uniq


def _parse_gemini_retry_delay_seconds(error_body: str) -> float | None:
    """Best-effort parse of RetryInfo / prose retry hints from Gemini error JSON."""
    delay: float | None = None
    try:
        data = json.loads(error_body)
    except json.JSONDecodeError:
        data = {}
    err = data.get("error") if isinstance(data.get("error"), dict) else {}
    msg = str(err.get("message") or "")
    details = err.get("details")
    if isinstance(details, list):
        for detail in details:
            if not isinstance(detail, dict):
                continue
            if detail.get("@type", "").endswith("RetryInfo"):
                rd = detail.get("retryDelay")
                if rd is None:
                    continue
                if isinstance(rd, (int, float)):
                    delay = float(rd)
                    break
                s = str(rd).strip().rstrip("s")
                try:
                    delay = float(s)
                    break
                except ValueError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
                    continue
    if delay is None and msg:
        m = re.search(r"retry\s+in\s+([0-9]+(?:\.[0-9]+)?)\s*s", msg, flags=re.I)
        if m:
            try:
                delay = float(m.group(1))
            except ValueError:
                delay = None
    return delay


def _classify_gemini_http_block(status_code: int, error_body: str) -> tuple[str, str, str]:
    """Return (evaluator_mode, provider_status, short_message) for non-success HTTP."""
    body_l = error_body.lower()
    if status_code == 429 or "resource_exhausted" in body_l:
        snippet = (
            error_body[:900] + ("…" if len(error_body) > 900 else "")
            if error_body
            else "Gemini quota or rate limited (HTTP 429)."
        )
        return "BLOCKED_RATE_LIMIT", "BLOCKED_RATE_LIMIT", snippet
    if status_code in (401, 403):
        snippet = (
            error_body[:500] + ("…" if len(error_body) > 500 else "")
            if error_body
            else f"Gemini authorization error ({status_code})."  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
        )
        return (
            "BLOCKED_PROVIDER_UNAVAILABLE",
            "BLOCKED_PROVIDER_UNAVAILABLE",
            f"Gemini API error {status_code}: {snippet}",
        )
    snippet = (
        error_body[:900] + ("…" if len(error_body) > 900 else "")
        if error_body
        else f"Gemini API error ({status_code})."
    )
    return (
        "BLOCKED_PROVIDER_UNAVAILABLE",
        "BLOCKED_PROVIDER_UNAVAILABLE",
        f"Gemini API error {status_code}: {snippet}",
    )


def _extract_gemini_text(data: dict[str, Any]) -> tuple[str, str | None]:
    """Extract model text and finishReason from a Gemini generateContent response."""
    finish_reason = None
    candidates = data.get("candidates") or []
    if not candidates:
        return "", "NO_CANDIDATES"
    candidate = candidates[0]
    finish_reason = candidate.get("finishReason")
    content = candidate.get("content") or {}
    parts = content.get("parts") or []
    text_chunks: list[str] = []
    for part in parts:
        if isinstance(part, dict) and part.get("text"):
            text_chunks.append(str(part["text"]))
    return "".join(text_chunks), finish_reason


def _extract_json_from_text(text: str) -> dict[str, Any] | None:
    """Robust JSON extraction from text with markdown code blocks."""
    text = text.strip()
    
    # Try direct JSON parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
        pass
    
    # Try removing markdown code blocks
    patterns = [
        r"```json\s*(.*?)\s*```",
        r"```\s*(.*?)\s*```",
        r"`\s*(.*?)\s*`",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                continue
    
    # Try to find JSON object boundaries
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end+1])
    except json.JSONDecodeError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
        pass
    
    return None


_NETWORK_TESTS_TRUTHY = frozenset({"1", "true", "yes", "on"})


def _judge_live_https_allowed_under_pytest() -> bool:
    """Under pytest, outbound judge HTTPS is opt-in to avoid hanging unit runs on real sockets.

    Production and non-pytest entrypoints do not set ``PYTEST_CURRENT_TEST`` and are unaffected.
    """
    if not os.environ.get("PYTEST_CURRENT_TEST"):
        return True
    return (
        str(os.environ.get("APPS_RG_ENABLE_NETWORK_TESTS", "") or "").strip().lower() in _NETWORK_TESTS_TRUTHY
    )


def _pytest_network_disabled_blocked_output(
    *,
    provider_key: str,
    input_hash: str,
    model: str,
    service_label: str,
) -> JudgeOutput:
    return _make_blocked_output(
        provider_key,
        input_hash,
        "BLOCKED_PROVIDER_UNAVAILABLE",
        "NETWORK_TESTS_NOT_ENABLED",
        (
            f"{service_label} judge HTTPS is disabled under pytest "
            "(set APPS_RG_ENABLE_NETWORK_TESTS=1 to enable live network for judge calls)."
        ),
        raw_response_ref=None,
        model_name=model,
    )


def _make_blocked_output(
    provider_key: str,
    input_hash: str,
    evaluator_mode: str,
    provider_status: str,
    error: str,
    raw_response_ref: str | None = None,
    model_name: str = "",
    original_model: str | None = None,
    fallback_model: str | None = None,
) -> JudgeOutput:
    """Create a blocked judge output with full context."""
    meta = PROVIDERS.get(provider_key, {
        "provider_name": provider_key,
        "default_model": model_name or "unknown",
    })
    return JudgeOutput(
        judge_id=f"x1d_{provider_key}_exec_summary",
        provider_name=meta["provider_name"],
        provider_key=provider_key,
        evaluator_mode=evaluator_mode,
        provider_status=provider_status,
        model_name=model_name or meta.get("default_model", "unknown"),
        provider_available=False,
        provider_blocked=True,  # Blocked providers are marked as such
        exact_provider_error=error,
        raw_response_ref=raw_response_ref,
        original_model=original_model,
        fallback_model=fallback_model,
        rubric_version=JUDGE_RUBRIC_VERSION,
        input_hash=input_hash,
        output_hash="",
        score=None,
        score_scale=None,
        normalized_score=None,
        threshold=DEFAULT_THRESHOLD,
        normalized_threshold=None,
        pass_=False,
        decisive_failure=False,  # Blocked providers are NOT decisive failures
        findings=["Judge blocked - see exact_provider_error and raw_response_ref for details."],
        cited_sentence_indexes=[],
        remediation_suggestions=["Review provider configuration and raw response artifact."],
    )


def _make_model_backed_output(
    provider_key: str,
    input_hash: str,
    model_name: str,
    result: dict[str, Any],
    raw_response_ref: str | None = None,
    original_model: str | None = None,
    fallback_model: str | None = None,
    *,
    deterministic_gate_summary: dict[str, Any] | None = None,
) -> JudgeOutput:
    """Create a model-backed judge output from parsed result."""
    result = _normalize_judge_result(result)
    if deterministic_gate_summary:
        from apps_rg.runtime.judges.executive_summary_judge_packet import (
            reconcile_grade_only_judge_result,
        )

        result = reconcile_grade_only_judge_result(result, deterministic_gate_summary)
    raw_score = float(result.get("score", 0.0))
    raw_threshold = float(result.get("threshold", DEFAULT_THRESHOLD))
    declared_scale = result.get("score_scale")
    declared = declared_scale.strip() if isinstance(declared_scale, str) else None
    score_scale, err = _validate_judge_score_contract(raw_score, raw_threshold, declared)
    if err:
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            err,
            raw_response_ref=raw_response_ref,
            model_name=model_name,
            original_model=original_model,
            fallback_model=fallback_model,
        )

    assert score_scale is not None  # validated above
    try:
        normalized_score, normalized_threshold = _compute_normalized(
            raw_score, raw_threshold, score_scale
        )
    except ValueError as exc:
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            str(exc),
            raw_response_ref=raw_response_ref,
            model_name=model_name,
            original_model=original_model,
            fallback_model=fallback_model,
        )

    decisive = bool(result.get("decisive_failure", False))
    passed = normalized_score >= normalized_threshold and not decisive
    output_hash = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()[:16]
    meta = PROVIDERS[provider_key]

    provider_status = "MODEL_BACKED_PASS" if passed else "MODEL_BACKED_FAIL"

    return JudgeOutput(
        judge_id=f"x1d_{provider_key}_exec_summary",
        provider_name=meta["provider_name"],
        provider_key=provider_key,
        evaluator_mode="MODEL_BACKED",
        provider_status=provider_status,
        model_name=model_name,
        provider_available=True,
        provider_blocked=False,  # Model-backed providers are not blocked
        exact_provider_error=None,
        raw_response_ref=raw_response_ref,
        original_model=original_model,
        fallback_model=fallback_model,
        rubric_version=JUDGE_RUBRIC_VERSION,
        input_hash=input_hash,
        output_hash=output_hash,
        score=raw_score,
        score_scale=score_scale,
        normalized_score=normalized_score,
        threshold=raw_threshold,
        normalized_threshold=normalized_threshold,
        pass_=passed,
        decisive_failure=decisive,
        findings=list(result.get("findings", [])),
        cited_sentence_indexes=list(result.get("cited_sentence_indexes", [])),
        remediation_suggestions=list(result.get("remediation_suggestions", [])),
        rationale=str(result.get("rationale") or "").strip() or None,
        fail_reasons=[str(x) for x in (result.get("fail_reasons") or []) if str(x).strip()],
        unsupported_claims=[str(x) for x in (result.get("unsupported_claims") or []) if str(x).strip()],
        quality_flags=[str(x) for x in (result.get("quality_flags") or []) if str(x).strip()],
        model_requested=model_name,
        model_actual=model_name,
    )


def _openai_reasoning_effort_supported(model: str) -> bool:
    """True only for OpenAI model families that accept reasoning.effort in chat completions."""
    mid = str(model or "").strip().lower()
    # gpt-5.5 / gpt-5.5-pro chat endpoints reject the reasoning parameter (400 unknown_parameter).
    return mid.startswith("o3") or mid.startswith("o4")


def _call_openai(
    api_key: str,
    prompt: str,
    model: str,
    input_hash: str,
    provider_key: str,
    *,
    artifact_base: Path | None = None,
    reasoning_effort: str | None = None,
    model_requested: str | None = None,
    judge_receipt: dict[str, Any] | None = None,
    attempt: int = 1,
) -> JudgeOutput:
    """Call OpenAI API with full artifact preservation."""
    compact = attempt >= 2
    system_content = (
        f"{JUDGE_COMPACT_SYSTEM}\n\n{JUDGE_COMPACT_OUTPUT}\n\n{JUDGE_SCORE_SCHEMA}"
        if compact
        else (
            "You are a strict executive resume judge. Return JSON only.\n\n"
            f"{JUDGE_SCORE_SCHEMA}"
        )
    )
    # Build request payload
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt},
        ],
    }
    # gpt-5.x: max_completion_tokens only; temperature/reasoning rejected on current chat SKUs.
    if model.startswith("gpt-5"):
        payload["max_completion_tokens"] = _resolved_openai_judge_max_completion_tokens(
            attempt=attempt
        )
        effort = (reasoning_effort or "").strip()
        if effort and _openai_reasoning_effort_supported(model):
            payload["reasoning"] = {"effort": effort}
    else:
        payload["max_tokens"] = _resolved_openai_judge_max_completion_tokens(attempt=attempt)
        payload["temperature"] = 0.1
        payload["response_format"] = {"type": "json_object"}
    
    # Write request artifact
    req_path = _artifact_path(provider_key, "provider_request", artifact_base=artifact_base)
    req_doc: dict[str, Any] = {
        "payload": payload,
        "input_hash": input_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_requested": model_requested or model,
        "model_actual": model,
        "reasoning_effort": reasoning_effort,
        "judge_attempt": attempt,
        "judge_max_attempts": _x1d_judge_max_attempts(),
        "compact_system_prompt": compact,
    }
    if judge_receipt:
        req_doc["judge_receipt"] = judge_receipt
    _write_artifact(req_path, req_doc)
    
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )

    if not _judge_live_https_allowed_under_pytest():
        return _pytest_network_disabled_blocked_output(
            provider_key=provider_key,
            input_hash=input_hash,
            model=model,
            service_label="OpenAI",
        )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw_response = response.read().decode()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        # Write error response artifact
        err_path = _artifact_path(provider_key, "provider_response_raw", artifact_base=artifact_base)
        _write_artifact(err_path, {"error": True, "status_code": e.code, "body": error_body, "input_hash": input_hash})
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_PROVIDER_UNAVAILABLE",
            "BLOCKED_PROVIDER_UNAVAILABLE", f"OpenAI API error {e.code}: {error_body}",
            raw_response_ref=str(err_path), model_name=model
        )
    
    # Write raw response artifact
    raw_path = _artifact_path(provider_key, "provider_response_raw", artifact_base=artifact_base)
    _write_artifact(raw_path, {"raw_response": raw_response, "input_hash": input_hash})
    
    try:
        data = json.loads(raw_response)
        choice = data["choices"][0]
        message = choice.get("message") or {}
        content = str(message.get("content") or "")
        finish_reason = str(choice.get("finish_reason") or "")
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
        parse_err_path = _artifact_path(provider_key, "provider_parse_result", artifact_base=artifact_base)
        _write_artifact(
            parse_err_path,
            {"error": "response_structure", "detail": str(e), "raw_response_ref": str(raw_path)},
        )
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            f"OpenAI response parse error: {e}",
            raw_response_ref=str(raw_path),
            model_name=model,
        )

    if not content.strip() and finish_reason.lower() == "length":
        parse_err_path = _artifact_path(provider_key, "provider_parse_result", artifact_base=artifact_base)
        usage = data.get("usage") or {}
        _write_artifact(
            parse_err_path,
            {
                "error": "empty_content_length",
                "finish_reason": finish_reason,
                "usage": usage,
                "raw_response_ref": str(raw_path),
                "judge_attempt": attempt,
            },
        )
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            (
                "OpenAI judge returned empty content (finish_reason=length); "
                "completion token budget likely consumed by reasoning — retriable"
            ),
            raw_response_ref=str(raw_path),
            model_name=model,
        )

    out = _finish_judge_text_parse(
        provider_key=provider_key,
        input_hash=input_hash,
        model_name=model,
        raw_path=raw_path,
        text=content,
        finish_reason=finish_reason if provider_key == "gemini_pro" else None,
        artifact_base=artifact_base,
        judge_receipt=judge_receipt,
        model_requested=model_requested,
    )
    return _attach_judge_receipt_fields(out, judge_receipt, model_requested=model_requested or model)


def _attach_judge_receipt_fields(
    output: JudgeOutput,
    judge_receipt: dict[str, Any] | None,
    *,
    model_requested: str | None = None,
) -> JudgeOutput:
    if judge_receipt:
        output.judge_packet_hash = judge_receipt.get("judge_packet_hash")
        output.judge_packet_ref = judge_receipt.get("judge_packet_ref")
        output.candidate_output_ref = judge_receipt.get("candidate_output_ref")
        output.allowed_fact_packet_ref = judge_receipt.get("allowed_fact_packet_ref")
        output.rubric_ref = judge_receipt.get("rubric_ref")
    if model_requested:
        output.model_requested = model_requested
        output.model_actual = output.model_name
    return output


def _validate_judge_parse_result(
    provider_key: str,
    input_hash: str,
    model_name: str,
    result: dict[str, Any],
    raw_response_ref: str,
    *,
    artifact_base: Path | None = None,
) -> JudgeOutput | None:
    """Return a blocked JudgeOutput when required judge fields are missing; else None."""
    missing = [f for f in JUDGE_REQUIRED_FIELDS if f not in result]
    if missing:
        schema_err_path = _artifact_path(provider_key, "provider_parse_result", artifact_base=artifact_base)
        _write_artifact(
            schema_err_path,
            {
                "error": "schema_validation",
                "missing_fields": missing,
                "result_keys": list(result.keys()),
                "raw_response_ref": raw_response_ref,
            },
        )
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
            f"Missing required fields: {missing}",
            raw_response_ref=raw_response_ref,
            model_name=model_name,
        )
    return None


def _call_anthropic(
    api_key: str,
    prompt: str,
    model: str,
    input_hash: str,
    provider_key: str,
    *,
    model_source: str = "unknown",
    artifact_base: Path | None = None,
    allow_model_fallback: bool | None = None,
    model_requested: str | None = None,
    judge_receipt: dict[str, Any] | None = None,
) -> JudgeOutput:
    """Call Anthropic API with full artifact preservation and model fallback handling."""
    original_model = model
    fallback_model = None
    
    # Check for fallback permission (disabled on executive_summary GRADE_ONLY proof path)
    if allow_model_fallback is None:
        allow_fallback = os.environ.get("APPS_RG_ANTHROPIC_ALLOW_MODEL_FALLBACK", "").lower() == "true"
    else:
        allow_fallback = bool(allow_model_fallback)
    
    payload = {
        "model": model,
        "max_tokens": ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS,
        "system": JUDGE_COMPACT_SYSTEM,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }
    
    # Write request artifact
    req_path = _artifact_path(provider_key, "provider_request", artifact_base=artifact_base)
    req_doc = {
        "payload": payload,
        "input_hash": input_hash,
        "original_model": original_model,
        "resolved_model": model,
        "resolved_model_source": model_source,
        "model_requested": model_requested or model,
        "model_actual": model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if judge_receipt:
        req_doc["judge_receipt"] = judge_receipt
    _write_artifact(req_path, req_doc)

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    if not _judge_live_https_allowed_under_pytest():
        return _pytest_network_disabled_blocked_output(
            provider_key=provider_key,
            input_hash=input_hash,
            model=model,
            service_label="Anthropic",
        )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw_response = response.read().decode()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()

        # Check for 404 model not found
        if e.code == 404 or "not_found_error" in error_body:
            err_path = _artifact_path(provider_key, "provider_response_raw", artifact_base=artifact_base)
            _write_artifact(err_path, {
                "error": True,
                "status_code": e.code,
                "requested_model": model,
                "body": error_body,
                "input_hash": input_hash
            })
            
            if allow_fallback:
                fallback_candidates = [
                    os.environ.get("ANTHROPIC_MODEL", "").strip(),
                    str(PROVIDERS["anthropic_claude"]["default_model"]),
                ]
                for fallback in fallback_candidates:
                    if fallback and fallback != model:
                        return _call_anthropic_fallback(
                            api_key,
                            prompt,
                            fallback,
                            input_hash,
                            provider_key,
                            original_model,
                            fallback,
                            "APPS_RG_ANTHROPIC_ALLOW_MODEL_FALLBACK=true after 404 not_found",
                            artifact_base=artifact_base,
                        )
            
            return _make_blocked_output(
                provider_key, input_hash, "BLOCKED_MODEL_NOT_FOUND",
                "BLOCKED_MODEL_NOT_FOUND", f"Model not found: {model}",
                raw_response_ref=str(err_path), model_name=model,
                original_model=original_model, fallback_model=fallback_model
            )
        
        # Other HTTP errors
        err_path = _artifact_path(provider_key, "provider_response_raw", artifact_base=artifact_base)
        _write_artifact(err_path, {"error": True, "status_code": e.code, "body": error_body, "input_hash": input_hash})
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_PROVIDER_UNAVAILABLE",
            "BLOCKED_PROVIDER_UNAVAILABLE", f"Anthropic API error {e.code}: {error_body}",
            raw_response_ref=str(err_path), model_name=model,
            original_model=original_model, fallback_model=fallback_model
        )
    
    # Write raw response artifact
    raw_path = _artifact_path(provider_key, "provider_response_raw", artifact_base=artifact_base)
    _write_artifact(raw_path, {"raw_response": raw_response, "input_hash": input_hash})
    
    try:
        data = json.loads(raw_response)
        text = _extract_anthropic_message_text(data)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        parse_err_path = _artifact_path(provider_key, "provider_parse_result", artifact_base=artifact_base)
        _write_artifact(parse_err_path, {
            "error": "response_structure",
            "detail": str(exc),
            "raw_response_ref": str(raw_path),
        })
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            f"Anthropic response parse error: {exc}",
            raw_response_ref=str(raw_path),
            model_name=model,
            original_model=original_model,
            fallback_model=fallback_model,
        )

    out = _finish_judge_text_parse(
        provider_key=provider_key,
        input_hash=input_hash,
        model_name=model,
        raw_path=raw_path,
        text=text,
        original_model=original_model,
        fallback_model=fallback_model,
        artifact_base=artifact_base,
        judge_receipt=judge_receipt,
        model_requested=model_requested,
    )
    return _attach_judge_receipt_fields(out, judge_receipt, model_requested=model_requested or model)


def _call_anthropic_fallback(
    api_key: str,
    prompt: str,
    model: str,
    input_hash: str,
    provider_key: str,
    original_model: str,
    fallback_model: str,
    fallback_reason: str,
    *,
    artifact_base: Path | None = None,
) -> JudgeOutput:
    """Fallback call for Anthropic when original model not found."""
    payload = {
        "model": model,
        "max_tokens": ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS,
        "system": JUDGE_COMPACT_SYSTEM,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }

    req_path = _artifact_path(provider_key, "provider_request", artifact_base=artifact_base)
    _write_artifact(req_path, {
        "payload": payload,
        "input_hash": input_hash,
        "original_model": original_model,
        "fallback_model": fallback_model,
        "fallback_reason": fallback_reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    if not _judge_live_https_allowed_under_pytest():
        return _pytest_network_disabled_blocked_output(
            provider_key=provider_key,
            input_hash=input_hash,
            model=model,
            service_label="Anthropic",
        )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw_response = response.read().decode()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        err_path = _artifact_path(provider_key, "provider_response_raw", artifact_base=artifact_base)
        _write_artifact(err_path, {
            "error": True,
            "status_code": e.code,
            "original_model": original_model,
            "fallback_model": fallback_model,
            "fallback_reason": fallback_reason,
            "body": error_body,
            "input_hash": input_hash,
        })
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_MODEL_NOT_FOUND",
            "BLOCKED_MODEL_NOT_FOUND", f"Fallback model also failed: {e.code}: {error_body}",
            raw_response_ref=str(err_path), model_name=model,
            original_model=original_model, fallback_model=fallback_model
        )

    raw_path = _artifact_path(provider_key, "provider_response_raw", artifact_base=artifact_base)
    _write_artifact(raw_path, {
        "raw_response": raw_response,
        "original_model": original_model,
        "fallback_model": fallback_model,
        "input_hash": input_hash,
    })

    try:
        data = json.loads(raw_response)
        text = _extract_anthropic_message_text(data)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        parse_err_path = _artifact_path(provider_key, "provider_parse_result", artifact_base=artifact_base)
        _write_artifact(parse_err_path, {
            "error": "response_structure",
            "detail": str(exc),
            "raw_response_ref": str(raw_path),
        })
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            f"Fallback response parse error: {exc}",
            raw_response_ref=str(raw_path),
            model_name=model,
            original_model=original_model,
            fallback_model=fallback_model,
        )

    return _finish_judge_text_parse(
        provider_key=provider_key,
        input_hash=input_hash,
        model_name=model,
        raw_path=raw_path,
        text=text,
        original_model=original_model,
        fallback_model=fallback_model,
        artifact_base=artifact_base,
    )


def _finish_judge_text_parse(
    *,
    provider_key: str,
    input_hash: str,
    model_name: str,
    raw_path: Path,
    text: str,
    finish_reason: str | None = None,
    original_model: str | None = None,
    fallback_model: str | None = None,
    artifact_base: Path | None = None,
    judge_receipt: dict[str, Any] | None = None,
    model_requested: str | None = None,
) -> JudgeOutput:
    """Parse extracted judge text into JudgeOutput or blocked status."""
    if (
        provider_key == "gemini_pro"
        and finish_reason
        and str(finish_reason).upper() not in ("STOP",)
    ):
        parse_err_path = _artifact_path(provider_key, "provider_parse_result", artifact_base=artifact_base)
        _write_artifact(parse_err_path, {
            "error": "finish_reason",
            "finish_reason": finish_reason,
            "text_preview": text[:500],
            "raw_response_ref": str(raw_path),
        })
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            f"Gemini finishReason={finish_reason} (incomplete judge JSON)",
            raw_response_ref=str(raw_path),
            model_name=model_name,
            original_model=original_model,
            fallback_model=fallback_model,
        )

    if not str(text).strip():
        parse_err_path = _artifact_path(provider_key, "provider_parse_result", artifact_base=artifact_base)
        _write_artifact(parse_err_path, {"error": "empty_text", "raw_response_ref": str(raw_path)})
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "Response contained no judge text",
            raw_response_ref=str(raw_path),
            model_name=model_name,
            original_model=original_model,
            fallback_model=fallback_model,
        )

    result = _extract_json_from_text(text)
    if result is None:
        parse_err_path = _artifact_path(provider_key, "provider_parse_result", artifact_base=artifact_base)
        _write_artifact(parse_err_path, {
            "error": "json_extraction",
            "text_preview": text[:500],
            "raw_response_ref": str(raw_path),
        })
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            f"Failed to extract JSON from {provider_key} response",
            raw_response_ref=str(raw_path),
            model_name=model_name,
            original_model=original_model,
            fallback_model=fallback_model,
        )

    blocked = _validate_judge_parse_result(
        provider_key, input_hash, model_name, result, str(raw_path), artifact_base=artifact_base
    )
    if blocked is not None:
        return blocked

    parse_path = _artifact_path(provider_key, "provider_parse_result", artifact_base=artifact_base)
    _write_artifact(parse_path, {
        "result": result,
        "raw_response_ref": str(raw_path),
        "original_model": original_model,
        "fallback_model": fallback_model,
    })

    gate_summary = (judge_receipt or {}).get("deterministic_gate_summary") if judge_receipt else None
    out = _make_model_backed_output(
        provider_key,
        input_hash,
        model_name,
        result,
        raw_response_ref=str(raw_path),
        original_model=original_model,
        fallback_model=fallback_model,
        deterministic_gate_summary=gate_summary,
    )
    return _attach_judge_receipt_fields(out, judge_receipt, model_requested=model_requested or model_name)


def _call_gemini(
    api_key: str,
    prompt: str,
    model: str,
    input_hash: str,
    provider_key: str,
    *,
    model_source: str = "unknown",
    artifact_base: Path | None = None,
    model_requested: str | None = None,
    judge_receipt: dict[str, Any] | None = None,
) -> JudgeOutput:
    """Call Gemini API with full artifact preservation."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": _gemini_generation_config(),
    }

    endpoint_version = "v1beta" if "preview" in model or model.startswith("gemini-2") or model.startswith("gemini-3") else "v1"
    url = f"https://generativelanguage.googleapis.com/{endpoint_version}/models/{model}:generateContent?key={api_key}"

    retries = _gemini_judge_max_retries()
    safe_url, omitted_q = _sanitize_request_url_for_x1d_artifact(url)

    # Write request artifact (never persist raw API keys in URLs or elsewhere).
    req_path = _artifact_path(provider_key, "provider_request", artifact_base=artifact_base)
    artifact_body: dict[str, Any] = {
        "payload": payload,
        "url": safe_url,
        "resolved_model": model,
        "resolved_model_source": model_source,
        "model_requested": model_requested or model,
        "model_actual": model,
        "provider_key": provider_key,
        "request_timeout_seconds": 60,
        "gemini_max_retries_configured": retries,
        "input_hash": input_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if judge_receipt:
        artifact_body["judge_receipt"] = judge_receipt
    if omitted_q:
        artifact_body["redacted_query_param_names"] = list(omitted_q)
    _write_artifact(req_path, artifact_body)

    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    raw_response = ""

    if not _judge_live_https_allowed_under_pytest():
        return _pytest_network_disabled_blocked_output(
            provider_key=provider_key,
            input_hash=input_hash,
            model=model,
            service_label="Gemini",
        )

    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                raw_response = response.read().decode()
            break
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            if attempt < retries and e.code == 429:
                wait_s = _parse_gemini_retry_delay_seconds(body)
                if wait_s is None:
                    wait_s = min(30.0, 2.0**attempt)
                sleep_for = min(45.0, max(1.5, float(wait_s)))
                time.sleep(sleep_for)
                continue

            eval_mode, prov_status, msg = _classify_gemini_http_block(e.code, body)
            err_path = _artifact_path(provider_key, "provider_response_raw", artifact_base=artifact_base)
            _write_artifact(
                err_path,
                {
                    "error": True,
                    "status_code": e.code,
                    "body": body,
                    "input_hash": input_hash,
                    "attempt": attempt,
                    "retries_configured": retries,
                },
            )
            return _make_blocked_output(
                provider_key,
                input_hash,
                eval_mode,
                prov_status,
                msg,
                raw_response_ref=str(err_path),
                model_name=model,
            )
    
    # Write raw response artifact
    raw_path = _artifact_path(provider_key, "provider_response_raw", artifact_base=artifact_base)
    _write_artifact(raw_path, {"raw_response": raw_response, "input_hash": input_hash})
    
    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError as e:
        parse_err_path = _artifact_path(provider_key, "provider_parse_result", artifact_base=artifact_base)
        _write_artifact(parse_err_path, {
            "error": "response_structure",
            "detail": str(e),
            "raw_response_ref": str(raw_path),
        })
        return _make_blocked_output(
            provider_key, input_hash, "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR", f"Gemini response envelope parse error: {e}",
            raw_response_ref=str(raw_path), model_name=model,
        )

    text, finish_reason = _extract_gemini_text(data)
    return _finish_judge_text_parse(
        provider_key=provider_key,
        input_hash=input_hash,
        model_name=model,
        raw_path=raw_path,
        text=text,
        finish_reason=finish_reason,
        artifact_base=artifact_base,
        judge_receipt=judge_receipt,
        model_requested=model_requested,
    )


def _mocked_output(provider_key: str, input_hash: str) -> JudgeOutput:
    """Create a mocked judge output."""
    meta = PROVIDERS[provider_key]
    return JudgeOutput(
        judge_id=f"x1d_{provider_key}_exec_summary",
        provider_name=meta["provider_name"],
        provider_key=provider_key,
        evaluator_mode="MOCKED",
        provider_status="MOCKED",
        model_name=meta.get("default_model", "unknown"),
        provider_available=False,
        provider_blocked=False,  # Mocked is not blocked
        exact_provider_error=None,
        raw_response_ref=None,
        rubric_version=JUDGE_RUBRIC_VERSION,
        input_hash=input_hash,
        output_hash="mocked-output",
        score=0.80,
        score_scale="0_to_1",
        normalized_score=0.80,
        threshold=DEFAULT_THRESHOLD,
        normalized_threshold=0.80,
        pass_=True,
        decisive_failure=False,
        findings=["MOCKED plumbing judge. Not valid for X3_ALLOW."],
        cited_sentence_indexes=[],
        remediation_suggestions=[],
    )


def run_llm_judges(
    *,
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
    judge_keys: list[str],
    mode: str = "blocked_if_unavailable",
    artifact_base: Path | None = None,
    judge_packet: dict[str, Any] | None = None,
    judge_packet_ref: str | None = None,
    compiled_prompt: str | None = None,
    section_id: str = "executive_summary",
) -> list[JudgeOutput]:
    """Run or block the requested provider judges.

    mode values:
    - blocked_if_unavailable: attempt real providers only when credentials exist, otherwise block.
    - mocked: emit clearly mocked rows for plumbing tests.

    When ``judge_packet`` is provided (executive_summary GRADE_ONLY path), judges grade the packet
    candidate and use enhanced proof model resolution — not the generator ``compiled_prompt``.
    """
    from apps_rg.runtime.judges.executive_summary_judge_packet import judge_packet_hash as _exec_hash
    from apps_rg.runtime.judges.executive_summary_judge_packet import (
        render_judge_prompt_from_packet as _exec_render_packet,
    )
    from apps_rg.runtime.judges.grade_only_judge_packet import (
        judge_packet_hash as _generic_hash,
        render_judge_prompt_from_packet as _generic_render_packet,
    )
    from apps_rg.runtime.judges.section_judge_profile import resolve_section_proof_judge_model
    from apps_rg.runtime.section_judge_policy import normalize_section_id

    sid = normalize_section_id(section_id or (judge_packet or {}).get("section", "executive_summary"))
    use_grade_only_packet = judge_packet is not None
    if use_grade_only_packet:
        render_packet = (
            _exec_render_packet
            if str(judge_packet.get("judge_packet_version", "")).startswith("executive_summary")
            else _generic_render_packet
        )
        hash_packet = _exec_hash if "executive_summary" in str(judge_packet.get("judge_packet_version", "")) else _generic_hash
    else:
        render_packet = _generic_render_packet
        hash_packet = _generic_hash
    if use_grade_only_packet:
        input_hash = hash_packet(judge_packet)
        prompt = render_packet(judge_packet)
        if compiled_prompt and compiled_prompt.strip()[:500] in prompt:
            pass  # packet path must not embed generator prompt
    else:
        input_payload = {
            "resume_display_text": resume_display_text,
            "claim_ledger": claim_ledger,
            "rubric": RUBRIC,
        }
        input_hash = hashlib.sha256(json.dumps(input_payload, sort_keys=True).encode()).hexdigest()[:16]
        prompt = _build_judge_user_prompt(resume_display_text, claim_ledger)

    base_receipt: dict[str, Any] | None = None
    if use_grade_only_packet:
        base_receipt = {
            "judge_packet_hash": input_hash,
            "judge_packet_ref": judge_packet_ref,
            "candidate_output_ref": "candidate_output.resume_display_text",
            "allowed_fact_packet_ref": "allowed_fact_packet",
            "rubric_ref": judge_packet.get("rubric_ref") if judge_packet else None,
            "deterministic_gate_summary": judge_packet.get("deterministic_gate_summary"),
        }

    outputs: list[JudgeOutput] = []
    proof_eligible_judge = False
    model_tier: str | None = None
    for key in judge_keys:
        if key not in PROVIDERS:
            outputs.append(_make_blocked_output(
                key, input_hash, "BLOCKED_PROVIDER_UNAVAILABLE",
                "BLOCKED_PROVIDER_UNAVAILABLE", f"Unknown judge provider key: {key}"
            ))
            continue
        
        if mode == "mocked":
            outputs.append(_mocked_output(key, input_hash))
            continue
        
        meta = PROVIDERS[key]
        api_key, env_checked = resolve_x1d_provider_credentials(key, os.environ)
        if not api_key:
            outputs.append(_make_blocked_output(
                key, input_hash, "BLOCKED_PROVIDER_UNAVAILABLE",
                "BLOCKED_PROVIDER_UNAVAILABLE",
                (
                    f"No non-empty API credential in {env_checked}; "
                    f"Gemini resolves GOOGLE_API_KEY then deprecated GEMINI_API_KEY alias."
                    if key == "gemini_pro"  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
                    else f"{meta['env']} environment variable not set"
                ),
            ))
            continue
        
        reasoning_effort: str | None = None
        model_requested = ""
        if use_grade_only_packet:
            resolution = resolve_section_proof_judge_model(sid, key)
            if resolution.blocked:
                outputs.append(
                    _make_blocked_output(
                        key,
                        input_hash,
                        "BLOCKED_MODEL_CONFIG",
                        "BLOCKED_MODEL_CONFIG",
                        resolution.block_reason or "proof judge model unavailable",
                        model_name=resolution.model_requested or "unconfigured",
                    )
                )
                blocked = outputs[-1]
                if base_receipt:
                    blocked.judge_packet_hash = base_receipt.get("judge_packet_hash")
                    blocked.judge_packet_ref = base_receipt.get("judge_packet_ref")
                    blocked.model_requested = resolution.model_requested
                blocked.section_id = sid
                blocked.model_tier = resolution.model_tier
                blocked.proof_eligible_judge = False
                continue
            model = resolution.model_actual
            model_source = resolution.model_source
            model_requested = resolution.model_requested
            reasoning_effort = resolution.reasoning_effort
            proof_eligible_judge = resolution.proof_eligible_judge
            model_tier = resolution.model_tier
        else:
            model_source = "unknown"
            if key == "gemini_pro":
                model, model_source = _resolve_gemini_model(meta)
            elif key == "anthropic_claude":
                model, model_source = _resolve_anthropic_model(meta)
            else:
                model_env = meta.get("model_env", meta["env"].replace("_API_KEY", "_MODEL"))
                model = os.environ.get(model_env, "").strip()
                model_source = model_env if model else "unknown"
                if not model:
                    model = meta.get("default_model", "unknown")
                    model_source = "default"
            model_requested = model

        receipt = dict(base_receipt) if base_receipt else None

        try:
            if key == "openai_chatgpt":
                output = _invoke_judge_with_bounded_retries(
                    lambda attempt, _api=api_key, _prompt=prompt, _model=model: _call_openai(
                        _api,
                        _prompt,
                        _model,
                        input_hash,
                        key,
                        artifact_base=artifact_base,
                        reasoning_effort=reasoning_effort,
                        model_requested=model_requested,
                        judge_receipt=receipt,
                        attempt=attempt,
                    ),
                    provider_key=key,
                )
            elif key == "anthropic_claude":
                output = _invoke_judge_with_bounded_retries(
                    lambda attempt, _api=api_key, _prompt=prompt, _model=model: _call_anthropic(
                        _api,
                        _prompt,
                        _model,
                        input_hash,
                        key,
                        model_source=model_source,
                        artifact_base=artifact_base,
                        allow_model_fallback=not use_grade_only_packet,
                        model_requested=model_requested,
                        judge_receipt=receipt,
                    ),
                    provider_key=key,
                )
            else:
                output = _invoke_judge_with_bounded_retries(
                    lambda attempt, _api=api_key, _prompt=prompt, _model=model: _call_gemini(
                        _api,
                        _prompt,
                        _model,
                        input_hash,
                        key,
                        model_source=model_source,
                        artifact_base=artifact_base,
                        model_requested=model_requested,
                        judge_receipt=receipt,
                    ),
                    provider_key=key,
                )
            if use_grade_only_packet:
                output.section_id = sid
                output.model_tier = model_tier
                output.proof_eligible_judge = bool(
                    proof_eligible_judge
                    and output.evaluator_mode == "MODEL_BACKED"
                    and not output.provider_blocked
                )
                if output.fallback_model:
                    from apps_rg.runtime.judges.section_judge_profile import (
                        is_forbidden_proof_judge_model,
                    )

                    if is_forbidden_proof_judge_model(str(output.fallback_model)):
                        output.proof_eligible_judge = False
                        output.fallback_used = True
            outputs.append(output)
        except Exception as exc:  # noqa: BLE001  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            # Catch any unexpected errors and mark as blocked
            outputs.append(_make_blocked_output(
                key, input_hash, "BLOCKED_PROVIDER_UNAVAILABLE",
                "BLOCKED_PROVIDER_UNAVAILABLE", f"{meta['provider_name']} judge call failed: {type(exc).__name__}: {exc}",
                model_name=model
            ))
    
    return outputs
