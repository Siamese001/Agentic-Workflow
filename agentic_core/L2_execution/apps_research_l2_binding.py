"""L2 execution binding for apps_research `company_brief` task class.

Per plan apps-research-golden-template-adoption-ag9.

L2 is the SIXTH stage. Its job is to:
1. Invoke the LLM gateway against the CompiledPromptArtifact produced by PA.
2. Parse the generated company_brief JSON.
3. Emit a typed SealedL2Artifact for Exit to finalize.

Real LLM dispatch:
- Pre-flight health probe via vllm_health_probe.is_qwen_available().
- POST OpenAI-compatible /v1/chat/completions to VLLM_BASE_URL with
  system+user blocks, model=APPS_RESEARCH_TARGET_MODEL.
- Parse choices[0].message.content; strip ```json fences; json.loads().
- execution_status='completed' on success, 'completed_stub_fallback' on
  any health/HTTP/parse failure (fail-soft to preserve E2E reach).

Stub fallback surfaces a typed SealedL2Artifact with shape-valid content
when the live model is unreachable (offline CI, --dry-run, etc.).

Bypass: APPS_RESEARCH_L2_FORCE_STUB=1 skips the live LLM call.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Mapping

from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
)
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

_LOGGER = logging.getLogger(__name__)

APPS_RESEARCH_L2_CERT_REF: str = "l2-apps-research-company-brief-ag9"

_FORCE_STUB_ENV: str = "APPS_RESEARCH_L2_FORCE_STUB"
_DEFAULT_LLM_TIMEOUT_S: float = 120.0

_VLLM_BASE_URL_DEFAULT: str = "http://localhost:8000"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _get_vllm_base_url() -> str:
    return os.environ.get("VLLM_BASE_URL", _VLLM_BASE_URL_DEFAULT).rstrip("/")


def _is_qwen_available() -> bool:
    """Quick health probe — returns True if vLLM endpoint responds."""
    try:
        url = f"{_get_vllm_base_url()}/v1/models"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def _build_stub_brief(prompt: CompiledPromptArtifact) -> dict[str, Any]:
    """Produce a shape-valid placeholder company_brief JSON."""
    # Extract target company from the user instruction
    user_text = prompt.user_instruction or ""
    company = "TARGET_COMPANY"
    for line in user_text.splitlines():
        if line.startswith("Research target:"):
            company = line.split(":", 1)[-1].strip().split("|")[0].strip()
            break

    return {
        "schema_version": "company_brief_v1",
        "stub_mode": True,
        "company_name": company,
        "role_context": "",
        "sections": {
            "company_overview": f"[STUB] Placeholder overview for {company}.",
            "culture_values": "[STUB]",
            "technology_stack": "[STUB]",
            "leadership_team": "[STUB]",
            "recent_news": "[STUB]",
            "competitive_position": "[STUB]",
        },
        "sources_consulted": [],
        "synthesis_confidence": 0.0,
    }


def _strip_json_fence(text: str) -> str:
    """Strip ```json ... ``` fences if present."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # Remove opening fence line
        lines = lines[1:]
        # Remove trailing fence
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _call_llm(prompt: CompiledPromptArtifact) -> tuple[dict[str, Any], str]:
    """Invoke vLLM and return (parsed_json, response_id)."""
    vllm_url = f"{_get_vllm_base_url()}/v1/chat/completions"

    messages: list[dict[str, str]] = []
    for block in prompt.prompt_blocks:
        messages.append({"role": block.role, "content": block.content})

    if not messages:
        # Fallback to flat fields
        if prompt.system_preamble:
            messages.append({"role": "system", "content": prompt.system_preamble})
        if prompt.user_instruction:
            messages.append({"role": "user", "content": prompt.user_instruction})

    request_body = json.dumps(
        {
            "model": prompt.target_model or "Qwen/Qwen2.5-32B-Instruct-AWQ",
            "messages": messages,
            "max_tokens": prompt.max_tokens or 2048,
            "temperature": prompt.temperature if prompt.temperature is not None else 0.3,
        },
        ensure_ascii=False,
    ).encode("utf-8")

    req = urllib.request.Request(
        vllm_url,
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=_DEFAULT_LLM_TIMEOUT_S) as resp:
        response_json = json.loads(resp.read().decode("utf-8"))

    response_id = response_json.get("id", "")
    raw_content = response_json["choices"][0]["message"]["content"]
    clean_content = _strip_json_fence(raw_content)
    parsed = json.loads(clean_content)
    return parsed, response_id


def l2_execute_apps_research(
    prompt: CompiledPromptArtifact,
) -> SealedL2Artifact:
    """Execute the LLM call and emit a SealedL2Artifact.

    Fails-soft on network/parse errors — returns stub fallback so the
    pipeline remains reachable for offline CI and dry-run verification.

    Returns a fully-typed SealedL2Artifact. Raises TypeError on bad input.
    """
    if not isinstance(prompt, CompiledPromptArtifact):
        raise TypeError(
            f"l2_execute_apps_research: expected CompiledPromptArtifact, got {type(prompt)}"
        )

    force_stub = os.environ.get(_FORCE_STUB_ENV, "").strip() in ("1", "true", "True")
    execution_ts = datetime.now(timezone.utc).isoformat()
    start_mono = time.monotonic()

    generated_content: str
    proposed_state_diff: dict[str, Any]
    execution_status: str
    sovereign_receipt: str = ""

    if not force_stub and _is_qwen_available():
        try:
            parsed_brief, response_id = _call_llm(prompt)
            generated_content = json.dumps(parsed_brief, ensure_ascii=False, indent=2)
            proposed_state_diff = parsed_brief
            execution_status = "completed"
            sovereign_receipt = response_id
            _LOGGER.info(
                "L2 apps_research: LLM call succeeded, response_id=%s", response_id
            )
        except (urllib.error.URLError, json.JSONDecodeError, KeyError, ValueError) as exc:
            _LOGGER.warning(
                "L2 apps_research: LLM call failed (%s), using stub fallback", exc
            )
            stub = _build_stub_brief(prompt)
            generated_content = json.dumps(stub, ensure_ascii=False, indent=2)
            proposed_state_diff = stub
            execution_status = "completed_stub_fallback"
    else:
        if force_stub:
            _LOGGER.info("L2 apps_research: APPS_RESEARCH_L2_FORCE_STUB=1, using stub")
        else:
            _LOGGER.info("L2 apps_research: Qwen not available, using stub fallback")
        stub = _build_stub_brief(prompt)
        generated_content = json.dumps(stub, ensure_ascii=False, indent=2)
        proposed_state_diff = stub
        execution_status = "completed_stub_fallback"

    duration_ms = int((time.monotonic() - start_mono) * 1000)

    # Computation hashes
    prompt_artifact_digest = prompt.compilation_hash
    compilation_hash = _sha256(
        json.dumps(
            {
                "prompt_artifact_digest": prompt_artifact_digest,
                "generated_content_hash": _sha256(generated_content),
                "execution_status": execution_status,
            },
            sort_keys=True,
        )
    )

    _LOGGER.debug(
        "L2 apps_research: status=%s duration_ms=%d compilation_hash=%s",
        execution_status,
        duration_ms,
        compilation_hash[:16],
    )

    return SealedL2Artifact(
        request_id=prompt.request_id,
        run_id=prompt.run_id,
        app_id="apps_research",
        trace_id=prompt.trace_id,
        execution_status=execution_status,
        generated_content=generated_content,
        proposed_state_diff=proposed_state_diff,
        state_diff_authorized=True,
        execution_timestamp=execution_ts,
        execution_duration_ms=duration_ms,
        sovereign_execution_receipt=sovereign_receipt,
        tenant_id=prompt.tenant_id,
        allowed_file_roots=("artifacts/",),
        prompt_artifact_digest=prompt_artifact_digest,
        schema_version="AG9.L2.1",
        compilation_hash=compilation_hash,
        l5_certification_ref=APPS_RESEARCH_L2_CERT_REF,
    )


__all__ = [
    "APPS_RESEARCH_L2_CERT_REF",
    "l2_execute_apps_research",
]
