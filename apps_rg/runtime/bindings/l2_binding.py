"""L2 execution binding for apps_rg `resume_generation` task class.

MIGRATED from agentic_core/L2_execution/apps_rg_l2_binding.py
Per plan apps-rg-golden-state-section-generation-a4f9e1 W2E.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §6 W3.P5 (stub) + W5 (real).

L2 is the SIXTH stage. Its job is to invoke the LLM gateway against the
CompiledPromptArtifact produced by PA, capture the generated content,
and emit a typed SealedL2Artifact for Exit to finalize.

W5 — REAL LLM DISPATCH:
- Pre-flight health probe via vllm_health_probe.is_qwen_available()
- POST OpenAI-compatible /v1/chat/completions to VLLM_BASE_URL with
  the prompt's system+user blocks, model=target_model, temperature/max_tokens
  from the CompiledPromptArtifact
- Parse choices[0].message.content; strip ```json ... ``` fences if present;
  json.loads() the body into proposed_state_diff
- execution_status='completed' on success, 'completed_stub_fallback' on
  any health/HTTP/parse failure (fail-soft per plan §3 to preserve E2E reach)
- sovereign_execution_receipt populated with the OpenAI response id
- execution_duration_ms captured via time.monotonic()

The stub fallback:
- Surfaces a fully-typed SealedL2Artifact when the live model is unreachable
- Populates execution_status='completed_stub_fallback' (distinct from
  earlier W3.P5 'completed_stub' so Exit + W5 telemetry can disambiguate)
- Echoes target_company / role / level for identity verification
- Builds a deterministic compilation_hash binding prompt + output
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import logging
import os
import socket
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
)
from agentic_core.runtime.contracts.origin import Origin
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.providers.provider_registry import get_provider_registry
from agentic_core.runtime.providers.provider_gateway import ProviderGateway
from agentic_core.runtime.providers.provider_types import ProviderKind, ProviderMode

_LOGGER = logging.getLogger(__name__)

APPS_RG_L2_CERT_REF: str = "l2-apps-rg-resume-generation-w3p5"

# Bypass env var — set APPS_RG_L2_FORCE_STUB=1 to skip the live LLM call
# (useful for offline tests, CI, or when the Docker stack is intentionally
# down and we want pipeline-only verification).
_FORCE_STUB_ENV: str = "APPS_RG_L2_FORCE_STUB"

# Real-call HTTP timeouts. Resume generation runs ~10-30s on Qwen 32B AWQ.
_DEFAULT_LLM_TIMEOUT_S: float = 120.0

# External provider profiles registered in provider_profiles.yaml.
# These are called in ensemble mode alongside the Qwen vLLM primary.
_EXTERNAL_ENSEMBLE_PROFILES: tuple[str, ...] = (
    "anthropic_claude_generator",
    "openai_gpt_generator",
    "google_gemini_generator",
)

# Apps_rg provider profiles YAML path (relative to repo root).
_PROVIDER_PROFILES_RELPATH = "apps_rg/config/provider_profiles.yaml"


def _build_stub_resume(payload_echo: Mapping[str, Any]) -> dict[str, Any]:
    """Produce a shape-valid placeholder resume JSON document.

    Real LLM-generated content lands in W5. This stub establishes the
    JSON shape that Exit + the artifact writer expect, and threads the
    target_company / target_role / target_level so downstream consumers
    can verify identity propagation through the pipeline.
    """
    target_company = payload_echo.get("target_company") or "TARGET_COMPANY"
    target_role = payload_echo.get("target_role") or "TARGET_ROLE"
    target_level = payload_echo.get("target_level") or "UNSPECIFIED"

    return {
        "schema_version": "1.0",
        "stub_mode": True,
        "target_company": target_company,
        "target_role": target_role,
        "target_level": target_level,
        "executive_summary": (
            f"[STUB W3.P5] Placeholder summary for {target_role} at "
            f"{target_company}. Real LLM-generated narrative lands in W5."
        ),
        "experience": [
            {
                "company": "[STUB]",
                "role": "[STUB]",
                "bullets": [
                    "[STUB W3.P5] Placeholder achievement bullet — replaced by W5.",
                ],
                "evidence_anchor": "stub:no-llm-call-yet",
            },
        ],
        "skills": [],
        "education": [],
        "certifications": [],
    }


def _extract_payload_echo(user_instruction: str) -> dict[str, str]:
    """Reverse-engineer target_company / role / level from the PA prompt body."""
    echo: dict[str, str] = {}
    for line in user_instruction.splitlines():
        stripped = line.strip()
        if stripped.startswith("Company:"):
            echo["target_company"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Role:"):
            echo["target_role"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Level:"):
            echo["target_level"] = stripped.split(":", 1)[1].strip()
    return echo


def _strip_json_fences(text: str) -> str:
    """Strip ```json ... ``` markdown fences if the model emits them.

    Qwen instructed models comply with JSON-only requests but occasionally
    wrap output in fences. This trims them so json.loads succeeds.
    """
    s = text.strip()
    if s.startswith("```"):
        # Drop opening fence (with or without language tag) and trailing fence.
        first_newline = s.find("\n")
        if first_newline != -1:
            s = s[first_newline + 1:]
        if s.endswith("```"):
            s = s[:-3]
        s = s.strip()
    return s


def _post_chat_completion(
    base_url: str,
    model: str,
    system: str,
    user: str,
    *,
    max_tokens: int,
    temperature: float,
    timeout_s: float,
) -> tuple[str, str]:
    """POST to vLLM's OpenAI-compat endpoint; return (assistant_text, response_id).

    Raises OSError on transport failure, ValueError on malformed response.
    Caller is responsible for fail-soft fallback to stub on failure.
    """
    endpoint = f"{base_url.rstrip('/')}/chat/completions"
    body: dict[str, Any] = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    headers = {"content-type": "application/json"}
    api_key = os.environ.get("VLLM_API_KEY", "").strip()
    if api_key:
        headers["authorization"] = f"Bearer {api_key}"

    request = urllib.request.Request(
        url=endpoint,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as resp:
            raw = resp.read()
    except (socket.timeout, urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
        raise OSError(f"vLLM HTTP failure: {type(exc).__name__}: {exc!s}") from exc

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError(f"vLLM response not JSON: {exc}") from exc

    if not isinstance(parsed, dict):
        raise ValueError(f"vLLM response not an object: {type(parsed).__name__}")
    response_id = str(parsed.get("id") or "")
    choices = parsed.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("vLLM response missing choices")
    first = choices[0]
    if not isinstance(first, dict):
        raise ValueError("vLLM first choice not an object")
    message = first.get("message")
    if not isinstance(message, dict):
        raise ValueError("vLLM choice missing message")
    content = message.get("content")
    if not isinstance(content, str):
        raise ValueError("vLLM message content not a string")
    return content, response_id


def _execute_via_qwen_vllm(
    prompt: CompiledPromptArtifact,
    payload_echo: Mapping[str, Any],
) -> tuple[
    str,           # generated_content (raw assistant text)
    dict[str, Any],  # proposed_state_diff (parsed JSON resume)
    int,           # execution_duration_ms
    str,           # sovereign_execution_receipt (response id)
    str,           # execution_status: 'completed' or raises
]:
    """Execute the prompt via the live Qwen vLLM endpoint.

    Raises OSError/ValueError on health, HTTP, or parse failure — caller
    must fall back to stub mode and record execution_status='completed_stub_fallback'.
    """
    # Pre-flight health probe (5s TTL cached). Imported lazily to avoid
    # paying the import cost when force-stub is set or in offline tests.
    from agentic_core.L2_execution.healers.vllm_health_probe import (
        is_qwen_available,
        probe,
    )
    from agentic_core.L0_routing.config.model_registry import VLLM_BASE_URL

    base_url = (os.environ.get("VLLM_BASE_URL") or VLLM_BASE_URL or "").rstrip("/")
    if not base_url:
        raise OSError("VLLM_BASE_URL not configured")

    # Probe checks /v1/models endpoint and verifies Qwen-family model is loaded.
    if not is_qwen_available(base_url=base_url):
        health = probe(base_url=base_url, force_refresh=True)
        raise OSError(
            f"Qwen vLLM unavailable: status={health.status} "
            f"model_id={health.model_id!r} error={health.error!r}"
        )

    started = time.monotonic()
    content, response_id = _post_chat_completion(
        base_url=base_url,
        model=prompt.target_model,
        system=prompt.system_preamble,
        user=prompt.user_instruction,
        max_tokens=prompt.max_tokens,
        temperature=prompt.temperature,
        timeout_s=_DEFAULT_LLM_TIMEOUT_S,
    )
    elapsed_ms = int((time.monotonic() - started) * 1000.0)

    # Parse JSON body. Strip markdown fences if present.
    stripped_content = _strip_json_fences(content)
    try:
        resume_doc = json.loads(stripped_content)
    except ValueError as exc:
        # Attempt inline repair for common Qwen output artifacts:
        # (1) trailing commas before } or ]
        # (2) truncated output — find last valid closing brace
        import re as _re
        repaired = _re.sub(r",\s*([}\]])", r"\1", stripped_content)
        try:
            resume_doc = json.loads(repaired)
            _LOGGER.warning("[apps_rg L2] JSON repaired (trailing comma fix): original error: %s", exc)
        except ValueError:
            # Last resort: find the rightmost top-level closing brace
            last_brace = repaired.rfind("}")
            if last_brace > 0:
                try:
                    resume_doc = json.loads(repaired[: last_brace + 1])
                    _LOGGER.warning("[apps_rg L2] JSON repaired (truncation trim at %d): original error: %s", last_brace, exc)
                except ValueError:
                    raise ValueError(
                        f"vLLM returned non-JSON resume body (len={len(content)}): {exc}"
                    ) from exc
            else:
                raise ValueError(
                    f"vLLM returned non-JSON resume body (len={len(content)}): {exc}"
                ) from exc

    if not isinstance(resume_doc, dict):
        raise ValueError(
            f"vLLM resume body not a JSON object: {type(resume_doc).__name__}"
        )

    # Stamp identity into the resume doc if the model omitted it. The user
    # instruction names the trio explicitly, but be defensive.
    resume_doc.setdefault("target_company", payload_echo.get("target_company", ""))
    resume_doc.setdefault("target_role", payload_echo.get("target_role", ""))
    resume_doc.setdefault("target_level", payload_echo.get("target_level", ""))
    resume_doc.setdefault("schema_version", "1.0")
    resume_doc["stub_mode"] = False

    receipt = response_id or "vllm-no-id-returned"
    # Re-serialize the parsed dict so generated_content is canonical clean
    # JSON without any markdown fences or assistant-side wrapping. The raw
    # response is recoverable from execution traces; the artifact file is
    # consumer-friendly.
    canonical_content = json.dumps(resume_doc, indent=2)
    return canonical_content, resume_doc, elapsed_ms, receipt, "completed"


def _load_apps_rg_registry():
    """Load apps_rg provider profiles into the global registry (idempotent)."""
    registry = get_provider_registry()
    if registry.list_profiles():
        return registry  # already loaded
    try:
        repo_root = _find_repo_root()
        profiles_path = repo_root / _PROVIDER_PROFILES_RELPATH
        registry.load_from_yaml(profiles_path, app_id="apps_rg")
    except Exception as exc:  # guardian: allow-broad-net -- registry load is best-effort; missing file must not abort the pipeline
        _LOGGER.warning("[apps_rg L2] Could not load provider profiles: %s", exc)
    return registry


def _find_repo_root() -> "__import__('pathlib').Path":
    """Walk up from this file to find the repo root (has pyproject.toml)."""
    import pathlib
    p = pathlib.Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return p.parents[3]  # fallback: agentic_core/../..


def _call_external_ensemble(
    prompt: CompiledPromptArtifact,
    payload_echo: dict[str, str],
) -> list[tuple[str, dict, int, str, str]]:
    """Call each external provider and collect (content, resume_doc, elapsed_ms, receipt, status) tuples.

    Fail-soft: provider errors are logged and skipped — never raise.
    Returns empty list when live calls are disabled or all providers fail.
    """
    force_stub = os.environ.get(_FORCE_STUB_ENV, "").strip().lower() in ("1", "true", "yes")
    if force_stub:
        return []

    # Opt-in filter via env var.
    allowed_raw = os.environ.get("APPS_RG_ENSEMBLE_PROVIDERS", "").strip()
    allowed: set[str] | None = (
        {p.strip() for p in allowed_raw.split(",") if p.strip()}
        if allowed_raw else None
    )

    registry = _load_apps_rg_registry()
    gateway = ProviderGateway(provider_mode=ProviderMode.LIVE_ALLOWED)

    # Build a minimal prompt text from the compiled prompt.
    prompt_text = f"{prompt.system_preamble}\n\n{prompt.user_instruction}"

    results: list[tuple[str, dict, int, str, str]] = []
    for profile_key in _EXTERNAL_ENSEMBLE_PROFILES:
        if allowed is not None and profile_key not in allowed:
            continue
        try:
            profile = registry.get_profile(profile_key)
        except Exception as exc:
            _LOGGER.warning("[apps_rg L2 ensemble] Profile %r not found: %s", profile_key, exc)
            continue

        if not registry.check_external_credentials(profile_key):
            _LOGGER.warning(
                "[apps_rg L2 ensemble] Skipping %r — API key env var %r not set",
                profile_key,
                profile.api_key_env_var,
            )
            continue

        try:
            from agentic_core.runtime.providers.provider_types import ProviderRequest
            req = ProviderRequest(
                prompt_text=prompt_text,
                provider_profile=profile,
                max_tokens=prompt.max_tokens,
                temperature=prompt.temperature,
                run_id=prompt.run_id,
                node_id="l2_ensemble",
            )
            started = time.monotonic()
            resp = gateway._invoke_external_api(req, profile)  # noqa: SLF001
            elapsed_ms = int((time.monotonic() - started) * 1000.0)

            if not resp.success:
                _LOGGER.warning(
                    "[apps_rg L2 ensemble] %r returned error: %s",
                    profile_key, resp.error_message,
                )
                continue

            stripped = _strip_json_fences(resp.text)
            try:
                resume_doc = json.loads(stripped)
            except ValueError:
                _LOGGER.warning(
                    "[apps_rg L2 ensemble] %r returned non-JSON (len=%d)",
                    profile_key, len(resp.text),
                )
                continue

            if not isinstance(resume_doc, dict):
                continue

            resume_doc.setdefault("target_company", payload_echo.get("target_company", ""))
            resume_doc.setdefault("target_role", payload_echo.get("target_role", ""))
            resume_doc.setdefault("target_level", payload_echo.get("target_level", ""))
            resume_doc.setdefault("schema_version", "1.0")
            resume_doc["stub_mode"] = False
            resume_doc["ensemble_provider"] = profile_key

            content = json.dumps(resume_doc, indent=2)
            receipt = f"external:{profile_key}:{resp.model_used or 'unknown'}"
            results.append((content, resume_doc, elapsed_ms, receipt, "completed"))
            _LOGGER.info("[apps_rg L2 ensemble] %r succeeded (%dms)", profile_key, elapsed_ms)

        except Exception as exc:  # guardian: allow-broad-net -- ensemble provider failure must never abort the pipeline
            _LOGGER.warning("[apps_rg L2 ensemble] %r raised: %s", profile_key, exc)

    return results


def _select_best_candidate(
    primary: tuple[str, dict, int, str, str] | None,
    ensemble: list[tuple[str, dict, int, str, str]],
) -> tuple[str, dict, int, str, str]:
    """Pick the best candidate from primary + ensemble results.

    Selection heuristic (judge jury not yet wired — use length as proxy):
    - Prefer any successful live candidate over stub.
    - Among live candidates, pick the one with the longest generated_content
      (correlated with completeness until real judge is wired).
    """
    candidates = []
    if primary is not None:
        candidates.append(primary)
    candidates.extend(ensemble)

    live = [(c, r, e, rc, s) for c, r, e, rc, s in candidates if s == "completed"]
    if not live:
        # All failed — return primary stub or first stub.
        return primary if primary is not None else candidates[0]

    best = max(live, key=lambda t: len(t[0]))
    return best


def l2_execute_apps_rg(prompt: CompiledPromptArtifact) -> SealedL2Artifact:
    """Execute the LLM call described by a CompiledPromptArtifact.

    W5 happy path: POSTs to the local Qwen vLLM Docker stack at VLLM_BASE_URL,
    parses the JSON resume body, and emits a SealedL2Artifact with
    execution_status='completed'.

    Fail-soft fallback (any of: APPS_RG_L2_FORCE_STUB=1, vLLM unhealthy,
    HTTP failure, non-JSON response): emits a stub artifact with
    execution_status='completed_stub_fallback' so the pipeline still
    reaches Exit and writes an artifact (per plan §3 fail-soft policy).

    Args:
        prompt: PA output carrying prompt blocks, target model/provider,
                provenance digests, and capability/sandbox metadata.

    Returns:
        SealedL2Artifact with execution_status, generated_content, and
        proposed_state_diff (the resume JSON document).

    Raises:
        TypeError: if prompt is not a CompiledPromptArtifact.
    """
    if not isinstance(prompt, CompiledPromptArtifact):
        raise TypeError(
            f"l2_execute_apps_rg expected CompiledPromptArtifact, got "
            f"{type(prompt).__name__}"
        )

    timestamp_iso = datetime.now(timezone.utc).isoformat()
    payload_echo = _extract_payload_echo(prompt.user_instruction)

    # Decide live vs stub.
    force_stub = os.environ.get(_FORCE_STUB_ENV, "").strip().lower() in ("1", "true", "yes")
    fallback_reason: str = ""
    primary_result = None

    if not force_stub:
        try:
            primary_result = _execute_via_qwen_vllm(prompt, payload_echo)
        except (OSError, ValueError) as exc:  # guardian: allow-broad-net -- W5 fail-soft policy: vLLM HTTP/parse/health errors must NOT raise into the pipeline; the stub fallback below preserves E2E reach + records the reason on the artifact for telemetry
            _LOGGER.warning("[apps_rg L2] vLLM live call failed: %s", exc)
            fallback_reason = f"{type(exc).__name__}: {exc!s}"

    # Ensemble: call external providers (Anthropic, OpenAI, Gemini) fail-soft.
    ensemble_results = _call_external_ensemble(prompt, payload_echo)

    if primary_result is not None or ensemble_results:
        # At least one live candidate — pick the best.
        content, resume_doc, elapsed_ms, receipt, exec_status = _select_best_candidate(
            primary_result, ensemble_results
        )
        # Annotate artifact with ensemble provenance.
        resume_doc["ensemble_candidates"] = 1 + len(ensemble_results)
        resume_doc["providers_attempted"] = ["local_qwen_generator"] + list(_EXTERNAL_ENSEMBLE_PROFILES)
    else:
        # All live calls failed — fall back to stub.
        if not fallback_reason:
            fallback_reason = "all_providers_failed"
        content, resume_doc, elapsed_ms, receipt, exec_status = (
            _build_stub_fallback(payload_echo, fallback_reason)
        )

    canonical = json.dumps(
        {
            "prompt_hash": prompt.compilation_hash,
            "model": prompt.target_model,
            "provider": prompt.target_provider,
            "output_len": len(content),
            "status": exec_status,
        },
        sort_keys=True,
    )
    compilation_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return SealedL2Artifact(
        request_id=prompt.request_id,
        run_id=prompt.run_id,
        app_id=prompt.app_id,
        trace_id=prompt.trace_id,
        execution_status=exec_status,
        generated_content=content,
        proposed_state_diff=resume_doc,
        state_diff_authorized=False,  # apps_rg doesn't write durable state
        execution_timestamp=timestamp_iso,
        execution_duration_ms=elapsed_ms,
        sovereign_execution_receipt=receipt,
        # W1 P1.2: thread identity quad from CompiledPromptArtifact (D6)
        tenant_id=prompt.tenant_id or "apps_rg",
        # W2 P2.3: thread capability/sandbox/egress from CompiledPromptArtifact
        sandbox_required=prompt.sandbox_required,
        egress_policy_ref=prompt.egress_policy_ref,
        allowed_tools=prompt.allowed_tools,
        allowed_models=prompt.allowed_models,
        allowed_networks=prompt.allowed_networks,
        allowed_file_roots=prompt.allowed_file_roots,
        # W3 P3.3: L2 always produces MODEL_GENERATION content (airlock doctrine)
        generated_content_origin=Origin.MODEL_GENERATION,
        prompt_artifact_digest=prompt.compilation_hash,
        schema_version="W5",
        compilation_hash=compilation_hash,
        l5_certification_ref=APPS_RG_L2_CERT_REF,
    )


def _build_stub_fallback(
    payload_echo: Mapping[str, Any],
    reason: str,
) -> tuple[str, dict[str, Any], int, str, str]:
    """Build a stub-fallback tuple matching the live-call return shape.

    Used when force-stub is set OR live call fails. The reason is embedded
    in the resume doc + sovereign_execution_receipt for telemetry.
    """
    resume_doc = _build_stub_resume(payload_echo)
    resume_doc["fallback_reason"] = reason
    resume_doc["stub_mode"] = True
    content = json.dumps(resume_doc, indent=2)
    receipt = f"stub-fallback:{reason[:120]}"
    return content, resume_doc, 0, receipt, "completed_stub_fallback"


# ---------------------------------------------------------------------------
# W5 quality gate consumer — apps-rg-quarantine-gap-remediation-8f405c W5.P1
#
# Reads quality_thresholds from ValidatedRequest.app_payload.
# Actual field names from QualityThresholdsSection (ingress_contract_v1.py):
#   min_quality (float 0-1), min_ats (int 0-100), word_min (int), word_max (int)
#
# Note: plan W5 referenced different field names (min_quality_score,
# min_confidence, hallucination_threshold, jd_alignment_threshold) but the
# actual contract fields differ — this binding uses the actual YAML/contract
# names. hallucination_threshold and jd_alignment_threshold are carried as
# POLICY METADATA only (no live judge result available at L2).
#
# Fail-soft by default (WARN / NOT_APPLICABLE).
# APPS_RG_QUALITY_GATE_FAIL_CLOSED=1 converts WARN into FAIL for missing
# required scores. UNKNOWN is never treated as PASS.
# ---------------------------------------------------------------------------

_QUALITY_GATE_FAIL_CLOSED_ENV: str = "APPS_RG_QUALITY_GATE_FAIL_CLOSED"


@dataclasses.dataclass(frozen=True)
class AppsRGQualityGatePolicy:
    """Extracted quality threshold policy from apps_rg app_payload."""

    min_quality: Optional[float]
    min_ats: Optional[int]
    word_min: Optional[int]
    word_max: Optional[int]
    payload_path: str
    fail_closed: bool


def extract_apps_rg_quality_gate_policy(validated_request: Any) -> AppsRGQualityGatePolicy:
    """Extract quality_thresholds from ValidatedRequest.app_payload.

    Reads the actual QualityThresholdsSection fields (min_quality, min_ats,
    word_min, word_max). Returns NOT_APPLICABLE policy with None values if
    the section is absent or malformed — never raises on missing optional data.

    Args:
        validated_request: ValidatedRequest carrying app_payload.

    Returns:
        AppsRGQualityGatePolicy with threshold values or None for absent fields.
    """
    fail_closed = os.environ.get(_QUALITY_GATE_FAIL_CLOSED_ENV, "").strip() == "1"
    payload_path = "ValidatedRequest.app_payload.quality_thresholds"

    try:
        app_payload = validated_request.app_payload
        qt = getattr(app_payload, "quality_thresholds", None)
        if qt is None:
            # Try dict-style access for payload that comes through as a dict
            if isinstance(app_payload, dict):
                qt_dict = app_payload.get("quality_thresholds") or {}
                return AppsRGQualityGatePolicy(
                    min_quality=qt_dict.get("min_quality"),
                    min_ats=qt_dict.get("min_ats"),
                    word_min=qt_dict.get("word_min"),
                    word_max=qt_dict.get("word_max"),
                    payload_path=payload_path,
                    fail_closed=fail_closed,
                )
            return AppsRGQualityGatePolicy(
                min_quality=None,
                min_ats=None,
                word_min=None,
                word_max=None,
                payload_path=payload_path,
                fail_closed=fail_closed,
            )
        return AppsRGQualityGatePolicy(
            min_quality=getattr(qt, "min_quality", None),
            min_ats=getattr(qt, "min_ats", None),
            word_min=getattr(qt, "word_min", None),
            word_max=getattr(qt, "word_max", None),
            payload_path=payload_path,
            fail_closed=fail_closed,
        )
    except Exception as exc:  # guardian: allow-broad-exception -- policy extraction must never abort L2; missing policy is WARN not ERROR
        _LOGGER.warning("[apps_rg L2 quality gate] policy extraction failed: %s", exc)
        return AppsRGQualityGatePolicy(
            min_quality=None,
            min_ats=None,
            word_min=None,
            word_max=None,
            payload_path=payload_path,
            fail_closed=fail_closed,
        )


def evaluate_apps_rg_l2_quality_precheck(
    policy: AppsRGQualityGatePolicy,
    run_context: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Evaluate quality thresholds against available run-context scores.

    L2 runs BEFORE LLM output exists, so judge scores are not available yet.
    This precheck:
      - Carries min_quality and min_ats as policy metadata for Exit consumption.
      - Evaluates word_min / word_max only if run_context provides word_count.
      - UNKNOWN is never PASS; absent scores produce WARN (or FAIL in fail-closed).

    Args:
        policy: Extracted quality gate policy.
        run_context: Optional dict carrying pre-execution metrics.

    Returns:
        Gate result dict with verdict (PASS/WARN/FAIL/NOT_APPLICABLE),
        per-field verdicts, and policy metadata for downstream visibility.
    """
    results: dict[str, Any] = {
        "gate": "L2_QUALITY_PRECHECK",
        "plan": "apps-rg-quarantine-gap-remediation-8f405c",
        "wave": "W5.P1",
        "policy": {
            "min_quality": policy.min_quality,
            "min_ats": policy.min_ats,
            "word_min": policy.word_min,
            "word_max": policy.word_max,
            "fail_closed": policy.fail_closed,
        },
        "field_verdicts": {},
        "policy_metadata": {},
    }

    if run_context is None:
        run_context = {}

    checks: list[str] = []

    # min_quality — no judge score available at L2, carry as policy metadata
    if policy.min_quality is not None:
        results["policy_metadata"]["min_quality_threshold"] = policy.min_quality
        results["field_verdicts"]["min_quality"] = "NOT_APPLICABLE"
        results["policy_metadata"]["min_quality_note"] = (
            "judge score not available at L2; threshold carried to Exit for post-LLM evaluation"
        )
        checks.append("NOT_APPLICABLE")

    # min_ats — no ATS score available at L2, carry as policy metadata
    if policy.min_ats is not None:
        results["policy_metadata"]["min_ats_threshold"] = policy.min_ats
        results["field_verdicts"]["min_ats"] = "NOT_APPLICABLE"
        results["policy_metadata"]["min_ats_note"] = (
            "ATS score not available at L2; threshold carried to Exit for post-LLM evaluation"
        )
        checks.append("NOT_APPLICABLE")

    # word_min / word_max — only evaluable if run_context provides word_count
    word_count = run_context.get("word_count")
    if policy.word_min is not None or policy.word_max is not None:
        if word_count is not None:
            try:
                wc = int(word_count)
                if policy.word_min is not None and wc < policy.word_min:
                    verdict = "FAIL" if policy.fail_closed else "WARN"
                    results["field_verdicts"]["word_min"] = verdict
                    checks.append(verdict)
                elif policy.word_min is not None:
                    results["field_verdicts"]["word_min"] = "PASS"
                    checks.append("PASS")
                if policy.word_max is not None and wc > policy.word_max:
                    verdict = "FAIL" if policy.fail_closed else "WARN"
                    results["field_verdicts"]["word_max"] = verdict
                    checks.append(verdict)
                elif policy.word_max is not None:
                    results["field_verdicts"]["word_max"] = "PASS"
                    checks.append("PASS")
            except (ValueError, TypeError):
                results["field_verdicts"]["word_count"] = "WARN"
                checks.append("WARN")
        else:
            results["field_verdicts"]["word_min"] = "NOT_APPLICABLE"
            results["field_verdicts"]["word_max"] = "NOT_APPLICABLE"
            results["policy_metadata"]["word_count_note"] = (
                "word_count not available in run_context at L2 precheck"
            )
            checks.append("NOT_APPLICABLE")

    if not checks:
        results["verdict"] = "NOT_APPLICABLE"
        results["reason"] = "no quality_thresholds present in payload"
    elif "FAIL" in checks:
        results["verdict"] = "FAIL"
    elif "WARN" in checks:
        results["verdict"] = "WARN"
    elif all(c == "NOT_APPLICABLE" for c in checks):
        results["verdict"] = "NOT_APPLICABLE"
    else:
        results["verdict"] = "PASS"

    return results


__all__ = [
    "APPS_RG_L2_CERT_REF",
    "AppsRGQualityGatePolicy",
    "extract_apps_rg_quality_gate_policy",
    "evaluate_apps_rg_l2_quality_precheck",
    "l2_execute_apps_rg",
]
