"""L2 execution binding for apps_underwriting_ai.

This binding owns LLM rationale generation — the only network-touching
stage in the underwriting pipeline. It wraps the Qwen vLLM call that
generates the rationale string for the already-sealed verdict.

AppIngressRunner calls: l2_fn(prompt_artifact) → UWSealedArtifact
where prompt_artifact is the dict returned by pa_compose_underwriting_profile.

The LLM call is optional: set UW_DISPATCH_SKIP_LLM=1 to skip it and
receive a deterministic STUB rationale. This matches the existing env-var
convention from underwriting_dispatch.py.

Pattern: fail-soft on LLM error — never raises; rationale_source records
the actual source ("LLM" | "STUB_NO_LLM" | "STUB_LLM_ERROR").

Plan: apps-underwriting-ai-profile-migration (Bundle B).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from agentic_core.config.model_catalog import QWEN_LOCAL_MODEL_ID

UW_L2_CERT_REF: str = "l2-apps-underwriting-ai-underwriting-decision-v1"

_SKIP_LLM_ENV: str = "UW_DISPATCH_SKIP_LLM"


@dataclass
class UWSealedArtifact:
    """Sealed output of L2 — carries rationale + prompt provenance.

    Consumed by exit_binding.exit_finalize_underwriting.
    The UWEvidenceResult is carried inside via evidence_result field
    so the Exit stage can build the full underwriting disposition / X3 packet.
    """

    request_id: str
    applicant_id: str
    product_class: str

    rationale: str = ""
    rationale_source: str = "STUB_NO_LLM"
    compiled_prompt: dict[str, Any] = field(default_factory=dict)

    verdict: str = "INSUFFICIENT_EVIDENCE"
    aggregate_score: float = 0.0
    reason_codes: list[str] = field(default_factory=list)
    dim_scores: dict[str, float] = field(default_factory=dict)

    c0_state: str = ""
    support_score: float = 0.0
    contradiction_flags: list[str] = field(default_factory=list)
    missing_evidence_flags: list[str] = field(default_factory=list)
    hitl_posture: str = "HITL_NONE"
    stage_receipts: list[dict[str, Any]] = field(default_factory=list)
    fec_dict: dict[str, Any] = field(default_factory=dict)
    decision_candidate: dict[str, Any] = field(default_factory=dict)
    run_context: dict[str, Any] = field(default_factory=dict)

    compilation_hash: str = ""
    l5_certification_ref: str = UW_L2_CERT_REF
    l2_cert_ref: str = UW_L2_CERT_REF


def _call_llm_for_rationale(compiled_prompt: dict[str, Any]) -> tuple[str, str]:
    """Call Qwen vLLM for rationale. Fail-soft — returns (text, source)."""
    try:
        import urllib.request  # noqa: PLC0415
        import json as _json  # noqa: PLC0415

        payload = {
            "model": compiled_prompt.get("target_model", QWEN_LOCAL_MODEL_ID),
            "messages": [
                {"role": "system", "content": compiled_prompt.get("system_prompt", "")},
                {"role": "user", "content": compiled_prompt.get("user_prompt", "")},
            ],
            "max_tokens": 512,
            "temperature": 0.1,
        }
        data = _json.dumps(payload).encode()
        req = urllib.request.Request(
            "http://localhost:8000/v1/chat/completions",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            body = _json.loads(resp.read().decode())
        text = body["choices"][0]["message"]["content"]
        return text, "LLM"
    except Exception:  # noqa: BLE001  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        # guardian: allow-broad-except -- LLM call must never crash the pipeline;
        # verdict + reason codes are already sealed by deterministic L2 stages
        return "", "STUB_LLM_ERROR"


def l2_execute_underwriting(prompt_artifact: dict[str, Any]) -> UWSealedArtifact:
    """Execute LLM rationale generation for underwriting.

    Accepts the CompiledPromptArtifact dict from pa_compose_underwriting_profile
    (which embeds all pipeline state via _evidence_result_snapshot). Calls the
    Qwen vLLM endpoint unless UW_DISPATCH_SKIP_LLM=1. Fail-soft on LLM error.

    Called by AppIngressRunner as l2_fn(prompt_artifact).

    Args:
        prompt_artifact: CompiledPromptArtifact dict from PA stage,
            extended with _evidence_result_snapshot carrying C0 outputs.

    Returns:
        UWSealedArtifact with rationale, provenance, and all pipeline state
        needed by the Exit stage.
    """
    evidence = prompt_artifact.get("_evidence_result_snapshot", {})

    sealed = UWSealedArtifact(
        request_id=prompt_artifact.get("request_id", ""),
        applicant_id=prompt_artifact.get("applicant_id", ""),
        product_class=prompt_artifact.get("product_class", ""),
        compiled_prompt=prompt_artifact,
        verdict=evidence.get("verdict", "INSUFFICIENT_EVIDENCE"),
        aggregate_score=float(evidence.get("aggregate_score", 0.0)),
        reason_codes=list(evidence.get("reason_codes") or []),
        dim_scores=dict(evidence.get("dim_scores") or {}),
        c0_state=str(evidence.get("c0_state", "")),
        support_score=float(evidence.get("support_score", 0.0)),
        contradiction_flags=list(evidence.get("contradiction_flags") or []),
        missing_evidence_flags=list(evidence.get("missing_evidence_flags") or []),
        hitl_posture=str(evidence.get("hitl_posture", "HITL_NONE")),
        stage_receipts=list(evidence.get("stage_receipts") or []),
        fec_dict=dict(evidence.get("fec_dict") or {}),
        decision_candidate=dict(evidence.get("decision_candidate") or {}),
        run_context=dict(evidence.get("run_context") or {}),
        compilation_hash=str(prompt_artifact.get("compilation_hash", "")),
        l5_certification_ref=str(prompt_artifact.get("l5_certification_ref", UW_L2_CERT_REF)),
    )

    skip_llm = os.environ.get(_SKIP_LLM_ENV, "0") == "1"
    if skip_llm:
        sealed.rationale = (
            f"[STUB] Verdict={sealed.verdict} | "
            f"Score={sealed.aggregate_score:.4f} | "
            f"Reason={', '.join(sealed.reason_codes)} | "
            f"C0={sealed.c0_state}({sealed.support_score:.2f}) | "
            f"HITL={sealed.hitl_posture}"
        )
        sealed.rationale_source = "STUB_NO_LLM"
    else:
        rationale_text, rationale_source = _call_llm_for_rationale(prompt_artifact)
        if rationale_text:
            sealed.rationale = rationale_text
            sealed.rationale_source = rationale_source
        else:
            sealed.rationale = (
                f"[LLM_UNAVAILABLE] Verdict={sealed.verdict} | "
                f"Reason={', '.join(sealed.reason_codes)} | "
                f"Score={sealed.aggregate_score:.4f}"
            )
            sealed.rationale_source = "STUB_LLM_ERROR"

    sealed.decision_candidate["rationale"] = sealed.rationale
    sealed.decision_candidate["rationale_source"] = sealed.rationale_source

    return sealed


__all__ = [
    "UW_L2_CERT_REF",
    "UWSealedArtifact",
    "l2_execute_underwriting",
]
