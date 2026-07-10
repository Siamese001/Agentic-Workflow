"""X1D LLM-as-Judge panel for executive summary runtime slice.

Provider-backed judges with full normalization per X1D adapter spec.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from agentic_core.config.model_catalog import (
    GEMINI_2_FAMILY_PREFIX,
    GEMINI_3_FAMILY_PREFIX,
    OPENAI_GPT5_FAMILY_PREFIX,
)
from apps_rg.runtime.env_bootstrap import bootstrap_process_env_if_needed
from apps_rg.runtime.judges.executive_summary_x1d_dimension_verdicts import (
    dimension_verdicts_json_schema_fragment,
    ensure_dimension_verdicts,
)
from apps_rg.runtime.providers.anthropic_prompt_cache import (
    anthropic_prompt_cache_enabled,
    anthropic_prompt_cache_telemetry_enabled,
    build_cache_receipt_from_usage,
)
from apps_rg.runtime.section_judge_policy import get_section_judge_policy
from apps_rg.runtime.section_model_limits import runtime_limit_float, runtime_limit_int

JUDGE_RUBRIC_VERSION = "executive_summary_x1d_v1"
DEFAULT_THRESHOLD = 0.80
VALID_SCORE_SCALES = frozenset({"0_to_1", "0_to_5"})
JUDGE_REQUIRED_FIELDS = ("score_scale", "score", "threshold", "pass")


def _is_openai_gpt5_chat_model(model: str) -> bool:
    return str(model or "").startswith(OPENAI_GPT5_FAMILY_PREFIX)


def _uses_gemini_preview_endpoint(model: str) -> bool:
    mid = str(model or "")
    return "preview" in mid or mid.startswith(GEMINI_2_FAMILY_PREFIX) or mid.startswith(GEMINI_3_FAMILY_PREFIX)


def _resolved_x1d_judge_max_output_tokens(*, attempt: int = 1) -> int:
    """Unified judge output token budget from provider_profiles.yaml runtime_limits."""
    base = max(512, runtime_limit_int("judge.x1d_max_output_tokens"))
    hard_cap = max(base, runtime_limit_int("judge.x1d_max_output_tokens_hard_cap"))
    return min(hard_cap, base * min(max(1, attempt), 2))


GOOGLE_AI_JUDGE_MAX_OUTPUT_TOKENS = _resolved_x1d_judge_max_output_tokens(attempt=1)
# Back-compat alias for tests and external imports (same unified resolution).
GEMINI_JUDGE_MAX_OUTPUT_TOKENS = GOOGLE_AI_JUDGE_MAX_OUTPUT_TOKENS
ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS = _resolved_x1d_judge_max_output_tokens(attempt=1)


def _resolved_openai_judge_max_completion_tokens(*, attempt: int = 1) -> int:
    """OpenAI chat completions cap — same unified budget as Gemini/Anthropic judges."""
    return _resolved_x1d_judge_max_output_tokens(attempt=attempt)


def _section_judge_runtime_profile(section_id: str) -> Any:
    return get_section_judge_policy(section_id).judge_runtime_profile


def _resolved_section_x1d_judge_max_output_tokens(
    section_id: str,
    *,
    attempt: int = 1,
) -> int:
    profile = _section_judge_runtime_profile(section_id)
    return profile.resolved_max_output_tokens(attempt=attempt)


def _section_x1d_judge_max_attempts(section_id: str) -> int:
    return _section_judge_runtime_profile(section_id).max_attempts


def _section_judge_retry_backoff_seconds(section_id: str, attempt: int) -> float:
    return _section_judge_runtime_profile(section_id).resolved_retry_backoff_seconds(attempt=attempt)


def _x1d_judge_max_attempts() -> int:
    return max(1, min(5, runtime_limit_int("judge.x1d_max_attempts")))


def _judge_retry_backoff_seconds(attempt: int) -> float:
    base = runtime_limit_float("judge.retry_backoff_base_seconds")
    hard_cap = runtime_limit_float("judge.retry_backoff_max_seconds")
    return min(hard_cap, base * (2 ** max(0, attempt - 1)))


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
    section_id: str | None = None,
) -> JudgeOutput:
    max_attempts = (
        _section_x1d_judge_max_attempts(section_id)
        if section_id
        else _x1d_judge_max_attempts()
    )
    last: JudgeOutput | None = None
    for attempt in range(1, max_attempts + 1):
        last = invoke(attempt)
        if last is None:
            break
        if not _is_retriable_judge_output(last) or attempt >= max_attempts:
            return last
        time.sleep(
            _section_judge_retry_backoff_seconds(section_id, attempt)
            if section_id
            else _judge_retry_backoff_seconds(attempt)
        )
    assert last is not None
    return last

JUDGE_COMPACT_OUTPUT = """
Return ONLY one compact JSON object. No markdown fences, no prose before or after, no nested objects.
Required shape (findings and remediation_suggestions must be arrays of short strings only):
{"score_scale":"0_to_5","score":0.0,"threshold":4.0,"pass":true,"decisive_failure":false,"findings":["..."],"cited_sentence_indexes":[1],"remediation_suggestions":[],"dimension_verdicts":{...8 rubric keys...}}
At most 6 short strings in findings and 4 in remediation_suggestions.
cited_sentence_indexes: 1-based indexes (S1=1 … S6=6) for every sentence your findings ask to change.
Include dimension_verdicts with all eight rubric dimension ids (pass/severity/codes per dimension).
""".strip()

JUDGE_COMPACT_SYSTEM = (
    "You are a strict executive resume judge. Output a single compact JSON object only. "
    "No markdown fences, no explanatory prose, no nested finding objects."
)

JUDGE_GRADE_ONLY_AUTHORITY = """
GRADE_ONLY authority (all providers — Gemini, OpenAI, Anthropic):
- Do NOT rewrite, replace, or edit candidate_output.resume_display_text.
- deterministic_gate_summary is authoritative: if a gate shows "pass": true, do NOT fail or cite that axis.
- Do NOT apply retired SRFS slot mandates as decisive failures: five-part S1–S5 arc, mandatory S5 credibility
  sentence, S2 mechanism-only / S4 outcomes slot shapes, srfs_sentence_responsibility.
- When x2_exec_summary_evidence_utilization.pass is true, unused_fact_ids are optional weave targets, not defects.
""".strip()


def build_x1d_judge_system_prompt(*, compact: bool = True) -> str:
    """Canonical system prompt shared by all proof judge providers."""
    if compact:
        return (
            f"{JUDGE_COMPACT_SYSTEM}\n\n{JUDGE_GRADE_ONLY_AUTHORITY}\n\n"
            f"{JUDGE_COMPACT_OUTPUT}\n\n{JUDGE_SCORE_SCHEMA}"
        )
    return f"You are a strict executive resume judge. Return JSON only.\n\n{JUDGE_SCORE_SCHEMA}"

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
        "dimension_verdicts": dimension_verdicts_json_schema_fragment(),
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

def _build_rubric() -> str:
    from apps_rg.runtime.judges.executive_summary_x1d_dimension_verdicts import (
        build_executive_summary_x1d_rubric_text,
    )

    return build_executive_summary_x1d_rubric_text(include_score_schema=JUDGE_SCORE_SCHEMA)


RUBRIC = _build_rubric()


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
    dimension_verdicts: dict[str, Any] | None = None
    dimension_verdicts_inferred: bool = False
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
        "provider_name": "Google Gemini 3.1 Pro Preview",
        "env": "GOOGLE_API_KEY",
        # GEMINI_API_KEY is a deprecated legacy alias (same credential as Google AI Gemini).
        "env_fallbacks": ("GEMINI_API_KEY",),
    },
    "openai_chatgpt": {
        "provider_name": "OpenAI ChatGPT",
        "env": "OPENAI_API_KEY",
    },
    "anthropic_claude": {
        "provider_name": "Anthropic Claude",
        "env": "ANTHROPIC_API_KEY",
    },
}

_ARTIFACT_PROVIDER_FILENAME_ALIASES = {
    "gemini_pro": "gemini",
    "openai_chatgpt": "openai",
    "anthropic_claude": "claude",
}


def _filesystem_path(path: Path) -> str:
    """Return a local filesystem path safe for long Windows artifact names."""
    if os.name != "nt":
        return str(path)
    try:
        absolute = str(path.resolve(strict=False))
    except OSError:
        absolute = str(path.absolute())
    if absolute.startswith("\\\\?\\"):
        return absolute
    if absolute.startswith("\\\\"):
        return "\\\\?\\UNC\\" + absolute.lstrip("\\")
    return "\\\\?\\" + absolute


def _ensure_dir(path: Path) -> None:
    Path(_filesystem_path(path)).mkdir(parents=True, exist_ok=True)


def _policy_model_name(provider_key: str, section_id: str, fallback: str = "unknown") -> str:
    """Return the section policy model name for evidence-only blocked/mocked rows."""
    from apps_rg.runtime.judges.section_judge_profile import resolve_section_proof_judge_model

    try:
        resolution = resolve_section_proof_judge_model(section_id, provider_key)
    except (ImportError, AttributeError, KeyError, RuntimeError, TypeError, ValueError):
        return fallback or "unknown"
    return (
        resolution.model_requested
        or resolution.model_actual
        or fallback
        or "unknown"
    )


def resolve_x1d_provider_credentials(provider_key: str, environ: Mapping[str, str]) -> tuple[str, list[str]]:
    """Return `(api_key, env_vars_consulted_in_order)` for preflight parity with lane judge execution."""
    bootstrap_process_env_if_needed(environ)
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
    _ensure_dir(base)
    leaf_provider = (
        provider_key
        if suffix == "anthropic_judge_cache_receipt"
        else _ARTIFACT_PROVIDER_FILENAME_ALIASES.get(provider_key, provider_key)
    )
    return base / f"x1d_{leaf_provider}_{suffix}_{ts}.json"


def _write_artifact(path: Path, data: Any) -> str:
    """Write artifact and return path string."""
    _ensure_dir(path.parent)
    with open(_filesystem_path(path), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    return str(path)


def _x1d_hash16(value: str) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]


def _anthropic_judge_cache_seed(
    *,
    model: str,
    system_prompt: str,
    user_prompt: str,
    input_hash: str,
    packet_hash: str | None,
    canonical_contract_hash: str | None,
    section_id: str | None,
) -> dict[str, Any]:
    stable_hash = _x1d_hash16(system_prompt)
    candidate_hash = _x1d_hash16(user_prompt)
    contract_hash = str(canonical_contract_hash or stable_hash)
    return {
        "provider": "anthropic_claude",
        "model": str(model or ""),
        "section_id": str(section_id or "executive_summary"),
        "cache_enabled": True,
        "cache_strategy": "x1d_judge_system_v1",
        "stable_prefix_hash": stable_hash,
        "c0_prefix_hash": "",
        "volatile_tail_hash": candidate_hash,
        "x1d_cache_group_hash": _x1d_hash16(f"x1d:{contract_hash}:{stable_hash}"),
        "judge_contract_hash": contract_hash,
        "candidate_hash": candidate_hash,
        "packet_hash": str(packet_hash or input_hash or ""),
        "cache_marker_count": 1,
        "input_tokens": None,
        "output_tokens": None,
        "cache_creation_input_tokens": None,
        "cache_read_input_tokens": None,
        "cache_hit_ratio": None,
        "estimated_uncached_input_tokens": None,
        "estimated_cached_input_tokens": None,
        "cache_savings_estimate_source": "pending_anthropic_usage",
    }


def _anthropic_judge_system_for_payload(system_prompt: str) -> str | list[dict[str, Any]]:
    if not anthropic_prompt_cache_enabled():
        return system_prompt
    return [
        {
            "type": "text",
            "text": system_prompt,
            "cache_control": {"type": "ephemeral"},
        }
    ]


def _write_anthropic_judge_cache_receipt(
    *,
    provider_key: str,
    artifact_base: Path | None,
    receipt: dict[str, Any],
) -> None:
    if not (anthropic_prompt_cache_enabled() or anthropic_prompt_cache_telemetry_enabled()):
        return
    receipt_path = _artifact_path(provider_key, "anthropic_judge_cache_receipt", artifact_base=artifact_base)
    _write_artifact(receipt_path, receipt)


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
    raise RuntimeError(
        resolution.block_reason
        or f"proof judge model unavailable for section={section_id} provider=gemini_pro"
    )


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
    raise RuntimeError(
        resolution.block_reason
        or f"proof judge model unavailable for section={section_id} provider=anthropic_claude"
    )


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


def _gemini_generation_config(*, attempt: int = 1, section_id: str | None = None) -> dict[str, Any]:
    """Gemini generationConfig for compact schema-valid judge JSON."""
    max_tokens = (
        _resolved_section_x1d_judge_max_output_tokens(section_id, attempt=attempt)
        if section_id
        else _resolved_x1d_judge_max_output_tokens(attempt=attempt)
    )
    return {
        "temperature": 0.1,
        "maxOutputTokens": max_tokens,
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
    })
    evidence_model = model_name or _policy_model_name(provider_key, "executive_summary")
    return JudgeOutput(
        judge_id=f"x1d_{provider_key}_exec_summary",
        provider_name=meta["provider_name"],
        provider_key=provider_key,
        evaluator_mode=evaluator_mode,
        provider_status=provider_status,
        model_name=evidence_model,
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
    result, _dv_inferred = ensure_dimension_verdicts(
        result, deterministic_gate_summary=deterministic_gate_summary
    )
    raw_score = float(result.get("score", 0.0))
    raw_threshold = float(result.get("threshold", 4.0))
    from apps_rg.runtime.sections.executive_summary_repair_policy import judge_pass_floor_0_to_5

    operator_floor = judge_pass_floor_0_to_5()
    if operator_floor is not None:
        raw_threshold = float(operator_floor)
        result["threshold"] = raw_threshold
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
        dimension_verdicts=dict(result.get("dimension_verdicts") or {}),
        dimension_verdicts_inferred=bool(result.get("dimension_verdicts_inferred")),
        model_requested=model_name,
        model_actual=model_name,
    )


def _openai_reasoning_effort_supported(model: str) -> bool:
    """True only for OpenAI model families that accept reasoning.effort in chat completions."""
    mid = str(model or "").strip().lower()
    # Catalog OpenAI chat judge models reject the reasoning parameter (400 unknown_parameter).
    return mid.startswith("o3") or mid.startswith("o4")


def _x1d_provider_request_receipt_fields(
    judge_receipt: dict[str, Any] | None,
    *,
    provider_name: str,
    model_env_source: str,
    input_hash: str,
    max_tokens: int,
    response_format: str,
) -> dict[str, Any]:
    receipt = judge_receipt or {}
    return {
        "provider_name": provider_name,
        "model_env_source": model_env_source,
        "canonical_contract_hash": receipt.get("canonical_contract_hash"),
        "packet_hash": receipt.get("packet_hash") or input_hash,
        "schema_hash": hashlib.sha256(
            json.dumps(GEMINI_JUDGE_RESPONSE_SCHEMA, sort_keys=True).encode()
        ).hexdigest()[:16],
        "max_tokens": max_tokens,
        "temperature": 0.1,
        "response_format": response_format,
    }


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
    model_env_source: str = "openai",
    section_id: str | None = None,
) -> JudgeOutput:
    """Call OpenAI API with full artifact preservation."""
    system_content = build_x1d_judge_system_prompt(compact=True)
    # Build request payload
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt},
        ],
    }
    # GPT-5 family: max_completion_tokens only; temperature/reasoning rejected on current chat SKUs.
    max_tokens = (
        _resolved_section_x1d_judge_max_output_tokens(section_id, attempt=attempt)
        if section_id
        else _resolved_x1d_judge_max_output_tokens(attempt=attempt)
    )
    judge_max_attempts = _section_x1d_judge_max_attempts(section_id) if section_id else _x1d_judge_max_attempts()
    if _is_openai_gpt5_chat_model(model):
        payload["max_completion_tokens"] = max_tokens
        effort = (reasoning_effort or "").strip()
        if effort and _openai_reasoning_effort_supported(model):
            payload["reasoning"] = {"effort": effort}
    else:
        payload["max_tokens"] = max_tokens
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
        "judge_max_attempts": judge_max_attempts,
        "compact_system_prompt": True,
        **_x1d_provider_request_receipt_fields(
            judge_receipt,
            provider_name="openai",
            model_env_source=model_env_source,
            input_hash=input_hash,
            max_tokens=max_tokens,
            response_format="json_object" if not _is_openai_gpt5_chat_model(model) else "gpt5_completion",
        ),
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
    model_requested: str | None = None,
    judge_receipt: dict[str, Any] | None = None,
    attempt: int = 1,
    packet_hash: str | None = None,
    canonical_contract_hash: str | None = None,
    section_id: str | None = None,
) -> JudgeOutput:
    """Call Anthropic API with full artifact preservation."""
    original_model = model
    fallback_model = None
    section_max_attempts = (
        _section_x1d_judge_max_attempts(section_id)
        if section_id
        else max(1, min(2, _x1d_judge_max_attempts()))
    )
    max_tokens = (
        _resolved_section_x1d_judge_max_output_tokens(section_id, attempt=attempt)
        if section_id
        else _resolved_x1d_judge_max_output_tokens(attempt=attempt)
    )
    system_prompt = build_x1d_judge_system_prompt(compact=True)
    cache_seed = (
        _anthropic_judge_cache_seed(
            model=model,
            system_prompt=system_prompt,
            user_prompt=prompt,
            input_hash=input_hash,
            packet_hash=packet_hash,
            canonical_contract_hash=canonical_contract_hash,
            section_id=section_id,
        )
        if anthropic_prompt_cache_enabled()
        else None
    )
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "system": _anthropic_judge_system_for_payload(system_prompt),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }
    from apps_rg.runtime.providers.external_provider import apply_anthropic_temperature_capability

    apply_anthropic_temperature_capability(payload)

    # Write request artifact
    req_path = _artifact_path(provider_key, "provider_request", artifact_base=artifact_base)
    req_doc = {
        "payload": payload,
        "input_hash": input_hash,
        "packet_hash": packet_hash,
        "canonical_contract_hash": canonical_contract_hash,
        "provider_name": "anthropic",
        "model_env_source": model_source,
        "max_tokens": max_tokens,
        "temperature": payload.get("temperature"),
        "response_format": "system_json_instruction",
        "judge_attempt": attempt,
        "judge_max_attempts": section_max_attempts,
        "original_model": original_model,
        "resolved_model": model,
        "resolved_model_source": model_source,
        "model_requested": model_requested or model,
        "model_actual": model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "anthropic_judge_cache_receipt_seed": cache_seed,
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
        stop_reason = str(data.get("stop_reason") or "")
        if cache_seed is not None:
            usage = data.get("usage") if isinstance(data, dict) else None
            _write_anthropic_judge_cache_receipt(
                provider_key=provider_key,
                artifact_base=artifact_base,
                receipt=build_cache_receipt_from_usage(
                    seed=cache_seed,
                    provider="anthropic_claude",
                    model=model,
                    section_id=section_id or "executive_summary",
                    usage=usage if isinstance(usage, dict) else None,
                ),
            )
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        parse_err_path = _artifact_path(provider_key, "provider_parse_result", artifact_base=artifact_base)
        _write_artifact(parse_err_path, {
            "error": "response_structure",
            "detail": str(exc),
            "raw_response_ref": str(raw_path),
        })
        if attempt < section_max_attempts and attempt < 2 and canonical_contract_hash and packet_hash:
            retry_path = _artifact_path(provider_key, "anthropic_judge_retry_receipt", artifact_base=artifact_base)
            _write_artifact(
                retry_path,
                {
                    "reason": "parse_error_retry",
                    "canonical_contract_hash": canonical_contract_hash,
                    "packet_hash": packet_hash,
                    "attempt": attempt,
                    "next_attempt": attempt + 1,
                    "retry_authority": "JudgePanelRunner",
                },
            )
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

    if stop_reason == "max_tokens":
        if attempt < section_max_attempts and attempt < 2 and canonical_contract_hash and packet_hash:
            retry_path = _artifact_path(provider_key, "anthropic_judge_retry_receipt", artifact_base=artifact_base)
            _write_artifact(
                retry_path,
                {
                    "reason": "max_tokens_truncation",
                    "stop_reason": stop_reason,
                    "canonical_contract_hash": canonical_contract_hash,
                    "packet_hash": packet_hash,
                    "attempt": attempt,
                    "next_attempt": attempt + 1,
                    "retry_authority": "JudgePanelRunner",
                    "next_max_tokens": (
                        _resolved_section_x1d_judge_max_output_tokens(section_id, attempt=2)
                        if section_id
                        else _resolved_x1d_judge_max_output_tokens(attempt=2)
                    ),
                },
            )
        return _make_blocked_output(
            provider_key,
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            f"Anthropic truncated (finish_reason={stop_reason}); not a content-quality judge verdict",
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
    attempt: int = 1,
    section_id: str | None = None,
) -> JudgeOutput:
    """Call Gemini API with full artifact preservation."""
    judge_max_attempts = _section_x1d_judge_max_attempts(section_id) if section_id else _x1d_judge_max_attempts()
    max_tokens = (
        _resolved_section_x1d_judge_max_output_tokens(section_id, attempt=attempt)
        if section_id
        else _resolved_x1d_judge_max_output_tokens(attempt=attempt)
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": build_x1d_judge_system_prompt(compact=True)}]},
        "generationConfig": _gemini_generation_config(attempt=attempt, section_id=section_id),
    }

    endpoint_version = "v1beta" if _uses_gemini_preview_endpoint(model) else "v1"
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
        "judge_max_attempts": judge_max_attempts,
        "input_hash": input_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "judge_attempt": attempt,
        **_x1d_provider_request_receipt_fields(
            judge_receipt,
            provider_name="gemini",
            model_env_source=model_source,
            input_hash=input_hash,
            max_tokens=max_tokens,
            response_format="responseSchema",
        ),
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
    model_name = _policy_model_name(provider_key, "executive_summary")
    return JudgeOutput(
        judge_id=f"x1d_{provider_key}_exec_summary",
        provider_name=meta["provider_name"],
        provider_key=provider_key,
        evaluator_mode="MOCKED",
        provider_status="MOCKED",
        model_name=model_name,
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
    from apps_rg.runtime.judges.executive_summary_judge_packet import (
        judge_contract_hash as _exec_contract_hash,
    )
    from apps_rg.runtime.judges.executive_summary_judge_packet import judge_packet_hash as _exec_hash
    from apps_rg.runtime.judges.executive_summary_judge_packet import (
        render_judge_prompt_from_packet as _exec_render_packet,
    )
    from apps_rg.runtime.judges.grade_only_judge_packet import (
        judge_packet_hash as _generic_hash,
    )
    from apps_rg.runtime.judges.grade_only_judge_packet import (
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
    contract_hash: str | None = None
    if use_grade_only_packet and judge_packet:
        if str(judge_packet.get("judge_packet_version", "")).startswith("executive_summary"):
            contract_hash = _exec_contract_hash(judge_packet)
        base_receipt = {
            "judge_packet_hash": input_hash,
            "packet_hash": input_hash,
            "canonical_contract_hash": contract_hash,
            "judge_packet_ref": judge_packet_ref,
            "candidate_output_ref": "candidate_output.resume_display_text",
            "allowed_fact_packet_ref": "allowed_fact_packet",
            "rubric_ref": judge_packet.get("rubric_ref") if judge_packet else None,
            "deterministic_gate_summary": judge_packet.get("deterministic_gate_summary"),
        }

    if use_grade_only_packet and judge_packet is not None and mode != "mocked":
        from apps_rg.runtime.judges.x1d_panel_bridge import run_grade_only_judges_via_core_panel

        return run_grade_only_judges_via_core_panel(
            judge_keys=judge_keys,
            judge_packet=judge_packet,
            user_prompt=prompt,
            input_hash=input_hash,
            section_id=sid,
            mode=mode,
            artifact_base=artifact_base,
            judge_packet_ref=judge_packet_ref,
            contract_hash=contract_hash,
        )

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
                    if key == "gemini_pro"
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
            resolution = resolve_section_proof_judge_model(sid, key)
            if resolution.blocked:
                outputs.append(
                    _make_blocked_output(
                        key,
                        input_hash,
                        "BLOCKED_MODEL_CONFIG",
                        "BLOCKED_MODEL_CONFIG",
                        resolution.block_reason or "judge model unavailable",
                        model_name=resolution.model_requested or "unconfigured",
                    )
                )
                continue
            model = resolution.model_actual
            model_source = resolution.model_source
            reasoning_effort = resolution.reasoning_effort
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
                        model_env_source=model_source,
                        section_id=sid,
                    ),
                    provider_key=key,
                    section_id=sid,
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
                        model_requested=model_requested,
                        judge_receipt=receipt,
                        attempt=attempt,
                        packet_hash=input_hash,
                        canonical_contract_hash=contract_hash,
                        section_id=sid,
                    ),
                    provider_key=key,
                    section_id=sid,
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
                        attempt=attempt,
                        section_id=sid,
                    ),
                    provider_key=key,
                    section_id=sid,
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
        except (
            ImportError,
            AttributeError,
            KeyError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
            urllib.error.URLError,
        ) as exc:
            # Catch any unexpected errors and mark as blocked
            outputs.append(_make_blocked_output(
                key, input_hash, "BLOCKED_PROVIDER_UNAVAILABLE",
                "BLOCKED_PROVIDER_UNAVAILABLE", f"{meta['provider_name']} judge call failed: {type(exc).__name__}: {exc}",
                model_name=model
            ))
    
    return outputs
