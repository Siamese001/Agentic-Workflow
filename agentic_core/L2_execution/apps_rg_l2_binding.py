"""L2 execution binding for apps_rg `resume_generation` task class.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §6 W3.P5 (stub) + W5 (real).

L2 is the SIXTH stage. Its job is to invoke the LLM gateway against the
CompiledPromptArtifact produced by PA, capture the generated content,
and emit a typed SealedL2Artifact for Exit to finalize.

W5 — REAL LLM DISPATCH:
- Pre-flight health probe via vllm_health_probe.is_qwen_available()
- POST OpenAI-compatible /v1/chat/completions to VLLM_BASE_URL with
  the prompt's system+user blocks, model=target_model, temperature/max_tokens
  from the CompiledPromptArtifact
- Parse choices[0].message.content; strip ```json ...``` fences if present;
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

import hashlib
import json
import logging
import os
import socket
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Mapping

from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
)
from agentic_core.runtime.contracts.origin import Origin
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

_LOGGER = logging.getLogger(__name__)

APPS_RG_L2_CERT_REF: str = "l2-apps-rg-resume-generation-w3p5"

# Bypass env var — set APPS_RG_L2_FORCE_STUB=1 to skip the live LLM call
# (useful for offline tests, CI, or when the Docker stack is intentionally
# down and we want pipeline-only verification).
_FORCE_STUB_ENV: str = "APPS_RG_L2_FORCE_STUB"

# Real-call HTTP timeouts. Resume generation runs ~10-30s on Qwen 32B AWQ.
_DEFAULT_LLM_TIMEOUT_S: float = 120.0


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

    if not force_stub:
        try:
            content, resume_doc, elapsed_ms, receipt, exec_status = (
                _execute_via_qwen_vllm(prompt, payload_echo)
            )
        except (OSError, ValueError) as exc:  # guardian: allow-broad-net -- W5 fail-soft policy: vLLM HTTP/parse/health errors must NOT raise into the pipeline; the stub fallback below preserves E2E reach + records the reason on the artifact for telemetry
            _LOGGER.warning("[apps_rg L2] vLLM live call failed: %s", exc)
            fallback_reason = f"{type(exc).__name__}: {exc!s}"
            content, resume_doc, elapsed_ms, receipt, exec_status = (
                _build_stub_fallback(payload_echo, fallback_reason)
            )
    else:
        fallback_reason = "APPS_RG_L2_FORCE_STUB=1"
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


__all__ = [
    "APPS_RG_L2_CERT_REF",
    "l2_execute_apps_rg",
]
