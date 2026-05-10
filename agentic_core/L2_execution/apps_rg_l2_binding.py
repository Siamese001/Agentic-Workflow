"""L2 execution binding for apps_rg `resume_generation` task class.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §6 W3.P5.

L2 is the SIXTH stage. Its job is to invoke the LLM gateway against the
CompiledPromptArtifact produced by PA, capture the generated content,
and emit a typed SealedL2Artifact for Exit to finalize.

W3.P5 SCOPE — STUB MODE: emit a shape-valid SealedL2Artifact carrying a
minimal placeholder resume JSON in proposed_state_diff. Real LLM dispatch
through SovereignLLMGateway against Qwen/Qwen2.5-32B-Instruct-AWQ via vllm
lands in W5.

The stub:
- Surfaces a fully-typed SealedL2Artifact (no caller-side type errors)
- Populates execution_status='completed_stub' so Exit can recognize the
  difference between a stub run and a real LLM run
- Echoes target_company / target_role / target_level into the placeholder
  resume so that downstream artifact writers can verify identity threading
- Builds a deterministic compilation_hash binding the prompt artifact +
  stub output (downstream cache reuse + tampering detection)
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping

from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
)
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact


APPS_RG_L2_CERT_REF: str = "l2-apps-rg-resume-generation-w3p5"


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


def l2_execute_apps_rg(prompt: CompiledPromptArtifact) -> SealedL2Artifact:
    """Execute the LLM call described by a CompiledPromptArtifact.

    Args:
        prompt: PA output carrying prompt blocks, target model/provider,
                and provenance digests.

    Returns:
        SealedL2Artifact with execution_status, generated_content, and
        proposed_state_diff (the resume JSON document, in stub form for W3.P5).

    Raises:
        TypeError: if prompt is not a CompiledPromptArtifact.

    W3.P5 STUB: real LLM dispatch deferred to W5. The stub emits a
    placeholder artifact that exercises the full Exit chain without
    requiring a running vllm container.
    """
    if not isinstance(prompt, CompiledPromptArtifact):
        raise TypeError(
            f"l2_execute_apps_rg expected CompiledPromptArtifact, got "
            f"{type(prompt).__name__}"
        )

    timestamp_iso = datetime.now(timezone.utc).isoformat()

    # Reconstruct the payload echo from the PA user_instruction. The PA
    # binding writes "Company: {x}\n  Role: {y}\n  Level: {z}" so we can
    # cheaply recover the identity tuple without re-threading the payload.
    payload_echo: dict[str, str] = {}
    for line in prompt.user_instruction.splitlines():
        stripped = line.strip()
        if stripped.startswith("Company:"):
            payload_echo["target_company"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Role:"):
            payload_echo["target_role"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Level:"):
            payload_echo["target_level"] = stripped.split(":", 1)[1].strip()

    resume_doc = _build_stub_resume(payload_echo)
    generated_content = json.dumps(resume_doc, indent=2)

    canonical = json.dumps(
        {
            "prompt_hash": prompt.compilation_hash,
            "model": prompt.target_model,
            "provider": prompt.target_provider,
            "output_len": len(generated_content),
            "stub": True,
        },
        sort_keys=True,
    )
    compilation_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return SealedL2Artifact(
        request_id=prompt.request_id,
        run_id=prompt.run_id,
        app_id=prompt.app_id,
        trace_id=prompt.trace_id,
        execution_status="completed_stub",
        generated_content=generated_content,
        proposed_state_diff=resume_doc,
        state_diff_authorized=False,  # apps_rg doesn't write durable state
        execution_timestamp=timestamp_iso,
        execution_duration_ms=0,
        sovereign_execution_receipt="stub-no-llm-call-w3p5",
        # W1 P1.2: thread identity quad from CompiledPromptArtifact (D6)
        tenant_id=prompt.tenant_id or "apps_rg",
        # W2 P2.3: thread capability/sandbox/egress from CompiledPromptArtifact
        sandbox_required=prompt.sandbox_required,
        egress_policy_ref=prompt.egress_policy_ref,
        allowed_tools=prompt.allowed_tools,
        allowed_models=prompt.allowed_models,
        allowed_networks=prompt.allowed_networks,
        allowed_file_roots=prompt.allowed_file_roots,
        prompt_artifact_digest=prompt.compilation_hash,
        contract_version="W3.P5",
        compilation_hash=compilation_hash,
        l5_certification_ref=APPS_RG_L2_CERT_REF,
    )


__all__ = [
    "APPS_RG_L2_CERT_REF",
    "l2_execute_apps_rg",
]
