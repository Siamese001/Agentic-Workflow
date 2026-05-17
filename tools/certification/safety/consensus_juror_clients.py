"""Real provider clients for the RTC-REQ-056 consensus-jury panel.

Exposes ``make_real_juror_call_impl`` which returns a ``JurorCallImpl``
closure compatible with ``ConsensusVeto``. The closure dispatches by
provider family to the correct SDK:

    google_gemini -> google.generativeai.GenerativeModel
    anthropic     -> anthropic.Anthropic
    openai        -> openai.OpenAI (chat.completions)

Design invariants:
  - Lazy SDK import: none of the SDKs are required unless its juror is
    actually invoked. Missing SDK -> JurorVerdict(verdict='ERROR', ...).
  - Fail-closed on every exception path. One juror's transport failure
    never raises out to the caller.
  - No secret values EVER logged or persisted. Only API-key presence
    booleans (via helpers in this module) and resolved model IDs.
  - Model-id override validation: if a provider_family's
    ``model_env_override`` env var is set, the value MUST match the
    registry's ``model_id`` or an explicit alias — else the juror
    returns verdict='ERROR' with rationale REJECT_UNREGISTERED_MODEL.
  - Raw responses are SHA-256 hashed for ``raw_response_sha256``; raw
    text is NOT stored in the JurorVerdict returned to ConsensusVeto.

Per operator directive 2026-05-01 13:39 UTC-04:00.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.certification.safety.consensus_veto import (
    JurorCallImpl,
    JurorVerdict,
    hash_raw_response,
)
from tools.certification.safety.rtc_req_056_panel import (
    JurorSpec,
    REQUIRED_JURORS,
    RejectReason,
    get_juror_by_family,
)


# ---------------------------------------------------------------------------
# Rubric loading (shared with LLMJudgeVeto; kept local for now)
# ---------------------------------------------------------------------------

DEFAULT_RUBRIC_PATH = REPO_ROOT / "config" / "certification" / "llm_judge_rubric.md"


def _load_rubric(rubric_path: Path | None = None) -> str:
    """Load the judge rubric. Missing file -> minimal built-in fallback."""
    p = rubric_path or DEFAULT_RUBRIC_PATH
    try:
        return p.read_text(encoding="utf-8")
    except (OSError, FileNotFoundError):
        return (
            "You are a safety judge for semantic cache reuse.\n\n"
            "Given:\n- Query: {query}\n- Cached query: {cached_query}\n"
            "- Cached answer: {cached_answer}\n\n"
            "Return ONLY valid JSON: "
            '{"verdict": "SAFE|UNSAFE_DIFFERENT_INTENT|UNSAFE_POLICY_DRIFT|UNCERTAIN",'
            ' "confidence": 0.0-1.0, "rationale": "..."}'
        )


def _build_prompt(
    rubric: str, query: str, cached_query: str, cached_answer: str | None
) -> str:
    """Substitute placeholders with JSON-escaped inputs. Literal replace
    so the rubric's own JSON example braces do not trigger str.format."""
    safe_query = json.dumps(query)[1:-1]
    safe_cached = json.dumps(cached_query)[1:-1]
    safe_answer = json.dumps(cached_answer or "N/A")[1:-1]
    return (
        rubric.replace("{query}", safe_query)
        .replace("{cached_query}", safe_cached)
        .replace("{cached_answer}", safe_answer)
    )


# ---------------------------------------------------------------------------
# Verdict parsing — returns "SAFE" / "UNSAFE_*" / "UNCERTAIN" / "ERROR"
# ---------------------------------------------------------------------------


def _parse_verdict(raw: str) -> tuple[str, float, str]:
    """Extract (verdict, confidence, rationale) from a provider response.

    Tolerates markdown code-fence wrappers and embedded JSON objects.
    Returns verdict='ERROR' for unparseable output.
    """
    if not raw:
        return "ERROR", 0.0, "empty response"

    text = raw.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        text = m.group(1)
    else:
        m = re.search(r'\{[^{}]*"verdict"[^{}]*\}', text, re.DOTALL)
        if m:
            text = m.group(0)

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        return "ERROR", 0.0, f"JSON parse error: {e}"

    if not isinstance(parsed, dict):
        return "ERROR", 0.0, "response not a JSON object"

    verdict_raw = str(parsed.get("verdict", "")).strip().upper()
    try:
        confidence = float(parsed.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    rationale = str(parsed.get("rationale", ""))

    # Normalize to ConsensusVeto verdict values
    if verdict_raw == "SAFE":
        return "SAFE", confidence, rationale
    if verdict_raw in ("UNSAFE_DIFFERENT_INTENT", "UNSAFE_POLICY_DRIFT"):
        return verdict_raw, confidence, rationale
    if verdict_raw in ("UNSAFE", "VETO"):
        return "UNSAFE_DIFFERENT_INTENT", confidence, rationale or "generic unsafe"
    if verdict_raw in ("UNCERTAIN", "UNKNOWN", ""):
        return "UNCERTAIN", confidence, rationale or "uncertain/unknown verdict"
    return "ERROR", confidence, f"unrecognized verdict={verdict_raw!r}"


# ---------------------------------------------------------------------------
# API-key resolution
# ---------------------------------------------------------------------------


def resolve_api_key(juror: JurorSpec) -> str | None:
    """Return the first non-empty API key from the juror's primary env
    var or any alias. Returns None if no key is set. Never logs the
    value.
    """
    for key_env in (juror.env_key, *juror.env_key_aliases):
        v = os.environ.get(key_env)
        if v:
            return v
    return None


def api_key_presence(juror: JurorSpec) -> bool:
    """Boolean presence flag for redaction-safe reporting."""
    return resolve_api_key(juror) is not None


def resolve_model_id(juror: JurorSpec) -> tuple[str, str | None]:
    """Resolve effective model_id for this juror.

    Returns (effective_model_id, reject_reason_or_None). If the override
    env var is set to a non-registry value, returns the registry
    model_id unchanged and ``REJECT_UNREGISTERED_MODEL`` so the caller
    can refuse to invoke the juror.
    """
    if not juror.model_env_override:
        return juror.model_id, None
    ov_key = juror.model_env_override
    if ov_key in ("GEMINI_MODEL", "GOOGLE_AI_MODEL"):
        override_raw = (
            os.environ.get("GOOGLE_AI_MODEL") or os.environ.get("GEMINI_MODEL")
        )
    else:
        override_raw = os.environ.get(juror.model_env_override)
    override = None if override_raw is None else override_raw.strip()
    if override is None or override == "":
        return juror.model_id, None
    if override == juror.model_id or override in juror.model_aliases:
        return override, None
    # Override set but not registered — REJECT
    return juror.model_id, RejectReason.REJECT_UNREGISTERED_MODEL


# ---------------------------------------------------------------------------
# Per-provider SDK callers
# ---------------------------------------------------------------------------


def _error_verdict(
    juror: JurorSpec, rationale: str, latency_ms: float
) -> JurorVerdict:
    return JurorVerdict(
        juror_id=juror.juror_id,
        family=juror.provider_family,
        model_id=juror.model_id,
        verdict="ERROR",
        confidence=0.0,
        rationale=rationale,
        latency_ms=latency_ms,
        raw_response_sha256="",
    )


def _call_gemini(
    juror: JurorSpec, model_id: str, api_key: str, prompt: str, timeout_ms: int
) -> tuple[str, float]:
    """Invoke google.generativeai and return (raw_text, latency_ms)."""
    start = time.perf_counter()
    try:
        import google.generativeai as genai  # type: ignore
    except ImportError as e:
        raise RuntimeError(f"google-generativeai SDK not installed: {e}") from e

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=model_id,
        system_instruction=(
            "You are a safety judge. Respond ONLY with valid JSON."
        ),
    )
    # google.generativeai uses request_options for timeout (seconds)
    request_options = {"timeout": max(1.0, timeout_ms / 1000.0)}
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.0, "max_output_tokens": 256},
        request_options=request_options,
    )
    # response.text is the consolidated text; fall back to candidates
    text = ""
    if hasattr(response, "text") and response.text:
        text = response.text
    elif hasattr(response, "candidates") and response.candidates:
        parts = response.candidates[0].content.parts
        text = "".join(getattr(p, "text", "") for p in parts)
    latency_ms = (time.perf_counter() - start) * 1000
    return text, latency_ms


def _call_anthropic(
    juror: JurorSpec, model_id: str, api_key: str, prompt: str, timeout_ms: int
) -> tuple[str, float]:
    start = time.perf_counter()
    try:
        import anthropic  # type: ignore
    except ImportError as e:
        raise RuntimeError(f"anthropic SDK not installed: {e}") from e

    client = anthropic.Anthropic(api_key=api_key, timeout=timeout_ms / 1000.0)
    response = client.messages.create(
        model=model_id,
        max_tokens=256,
        temperature=0.0,
        system="You are a safety judge. Respond ONLY with valid JSON.",
        messages=[{"role": "user", "content": prompt}],
    )
    # Anthropic returns .content = list of ContentBlock; first text block
    text = ""
    for block in getattr(response, "content", []) or []:
        t = getattr(block, "text", None)
        if t:
            text += t
    latency_ms = (time.perf_counter() - start) * 1000
    return text, latency_ms


def _call_openai(
    juror: JurorSpec, model_id: str, api_key: str, prompt: str, timeout_ms: int
) -> tuple[str, float]:
    start = time.perf_counter()
    try:
        import openai  # type: ignore
    except ImportError as e:
        raise RuntimeError(f"openai SDK not installed: {e}") from e

    client = openai.OpenAI(api_key=api_key, timeout=timeout_ms / 1000.0)
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "system",
                "content": "You are a safety judge. Respond ONLY with valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=256,
    )
    text = ""
    if response.choices:
        text = response.choices[0].message.content or ""
    latency_ms = (time.perf_counter() - start) * 1000
    return text, latency_ms


# ---------------------------------------------------------------------------
# Juror call implementation factory
# ---------------------------------------------------------------------------


_FAMILY_DISPATCH = {
    "google_gemini": _call_gemini,
    "anthropic": _call_anthropic,
    "openai": _call_openai,
}


def make_real_juror_call_impl(
    rubric_path: Path | None = None,
    timeout_ms_per_juror: int = 15000,
) -> JurorCallImpl:
    """Build a ``JurorCallImpl`` closure that calls real SDKs.

    Returned closure signature matches ConsensusVeto expectation:
        (family, model_id, query, cached_query, cached_answer, context)
        -> JurorVerdict

    The closure enforces all RTC-REQ-056 invariants:
      - Juror must be registered in ``REQUIRED_JURORS``
      - API key must be present (else ERROR with INFRASTRUCTURE_GAP hint)
      - Model override must resolve to a registered value
      - All exceptions captured as ERROR verdicts
      - Raw response text hashed but never stored
    """
    rubric = _load_rubric(rubric_path)

    def _impl(
        family: str,
        model_id: str,
        query: str,
        cached_query: str,
        cached_answer: str | None,
        context: dict[str, Any] | None,
    ) -> JurorVerdict:
        call_start = time.perf_counter()

        # 1. Validate the requested juror is in the registry
        juror = get_juror_by_family(family)
        if juror is None:
            return JurorVerdict(
                juror_id=f"{family}_{model_id}",
                family=family,
                model_id=model_id,
                verdict="ERROR",
                confidence=0.0,
                rationale=f"{RejectReason.REJECT_UNREGISTERED_PROVIDER}: "
                          f"family={family!r}",
                latency_ms=(time.perf_counter() - call_start) * 1000,
            )

        # 2. Validate model_id passed by ConsensusVeto matches registry
        if model_id != juror.model_id and model_id not in juror.model_aliases:
            return _error_verdict(
                juror,
                f"{RejectReason.REJECT_UNREGISTERED_MODEL}: "
                f"requested={model_id!r} registry={juror.model_id!r}",
                (time.perf_counter() - call_start) * 1000,
            )

        # 3. Resolve API key
        api_key = resolve_api_key(juror)
        if not api_key:
            return _error_verdict(
                juror,
                f"{RejectReason.INFRASTRUCTURE_GAP_MISSING_KEY}: "
                f"{juror.env_key} not set "
                f"(aliases={list(juror.env_key_aliases)})",
                (time.perf_counter() - call_start) * 1000,
            )

        # 4. Resolve effective model_id (check override env)
        effective_model, reject = resolve_model_id(juror)
        if reject is not None:
            return _error_verdict(
                juror,
                f"{reject}: {juror.model_env_override} override "
                f"points to non-registry model",
                (time.perf_counter() - call_start) * 1000,
            )

        # 5. Dispatch to the correct SDK
        caller = _FAMILY_DISPATCH.get(juror.provider_family)
        if caller is None:
            return _error_verdict(
                juror,
                f"{RejectReason.REJECT_UNREGISTERED_PROVIDER}: "
                f"no dispatcher for family={juror.provider_family!r}",
                (time.perf_counter() - call_start) * 1000,
            )

        prompt = _build_prompt(rubric, query, cached_query, cached_answer)

        try:
            raw_text, latency_ms = caller(
                juror, effective_model, api_key, prompt, timeout_ms_per_juror
            )
        except TimeoutError as e:
            return _error_verdict(
                juror,
                f"{RejectReason.REJECT_JUROR_TIMEOUT}: {e}",
                (time.perf_counter() - call_start) * 1000,
            )
        except Exception as e:  # noqa: BLE001 — fail-closed on ANY SDK failure
            return _error_verdict(
                juror,
                f"{RejectReason.REJECT_JUROR_ERROR}: {type(e).__name__}: {e}",
                (time.perf_counter() - call_start) * 1000,
            )

        # 6. Timeout post-check (some SDKs don't raise TimeoutError)
        if latency_ms > timeout_ms_per_juror:
            return _error_verdict(
                juror,
                f"{RejectReason.REJECT_JUROR_TIMEOUT}: "
                f"{latency_ms:.0f}ms > {timeout_ms_per_juror}ms",
                latency_ms,
            )

        # 7. Parse verdict
        verdict, confidence, rationale = _parse_verdict(raw_text)
        if verdict == "ERROR":
            # Parse failure specifically
            return JurorVerdict(
                juror_id=juror.juror_id,
                family=juror.provider_family,
                model_id=effective_model,
                verdict="ERROR",
                confidence=confidence,
                rationale=f"{RejectReason.REJECT_JUROR_PARSE_FAIL}: {rationale}",
                latency_ms=latency_ms,
                raw_response_sha256=hash_raw_response(raw_text),
            )

        return JurorVerdict(
            juror_id=juror.juror_id,
            family=juror.provider_family,
            model_id=effective_model,
            verdict=verdict,
            confidence=confidence,
            rationale=rationale,
            latency_ms=latency_ms,
            raw_response_sha256=hash_raw_response(raw_text),
        )

    return _impl


__all__ = [
    "DEFAULT_RUBRIC_PATH",
    "api_key_presence",
    "make_real_juror_call_impl",
    "resolve_api_key",
    "resolve_model_id",
]
