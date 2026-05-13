"""End-to-end dispatch function for apps_underwriting_ai.

Wires the full governed pipeline:

  U0 (already run, ValidatedUnderwritingRequest in hand)
  → C0  (UnderwritingC0Adapter.run — document evidence extraction)
  → L2  Stage 1: EvidenceRegisterAdapter
  → L2  Stage 2: DocumentReconciliationAdapter
  → L2  Stage 3: FeatureDerivationAdapter
  → L2  Stage 4: RiskScoringAdapter
  → L2  Stage 5: DecisionAssemblyAdapter
  → PA  (pa_compose_underwriting — prompt compilation for rationale)
  → LLM (optional — only when UW_DISPATCH_SKIP_LLM != "1"; uses Qwen via vLLM)
  → Exit (UnderwritingExitFecProducer.produce_exit_bundle)
  → DispatchResult

agentic_core is immutable — all pipeline logic lives in apps_underwriting_ai.
No L4 writes. No open-web retrieval. SYNTHETIC_DEMO_ONLY data mode.

Plan: apps-underwriting-ai-kill-parallel-pipelines-a3f7e2 W4 (dispatch).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from apps_underwriting_ai.runtime.contracts.underwriting_ingress_payload import (
    ValidatedUnderwritingRequest,
)

# Env flag — set UW_DISPATCH_SKIP_LLM=1 to run deterministic pipeline without
# Qwen inference (useful for tests and dry-runs).
_SKIP_LLM_ENV = "UW_DISPATCH_SKIP_LLM"


@dataclass
class DispatchResult:
    """Full pipeline output for one underwriting request.

    Fields:
        request_id: Echoed from the validated request.
        applicant_id: Echoed from the validated request.
        product_class: Echoed from the validated request.
        verdict: APPROVE | REFER | DECLINE | INSUFFICIENT_EVIDENCE.
        aggregate_score: Numeric risk aggregate [0.0, 1.0].
        reason_codes: List of RC*** codes from Stage 5.
        dim_scores: Per-dimension scores from Stage 4.
        rationale: LLM-generated or stub rationale string.
        rationale_source: "LLM" | "STUB_NO_LLM" | "STUB_LLM_ERROR".
        c0_state: C0 evidence state: PASS | WEAK_WITH_CAVEATS | FAIL.
        support_score: C0 document coverage score.
        contradiction_flags: List of contradiction rule IDs triggered.
        missing_evidence_flags: Required doc classes absent.
        hitl_posture: HITL_REQUIRED | HITL_ADVISORY | HITL_NONE.
        x3_disposition: X3A–X3E Exit disposition code.
        exit_bundle: Full exit bundle dict from UnderwritingExitFecProducer.
        compiled_prompt: CompiledPromptArtifact dict from PA.
        stage_receipts: List of L2StepReceipt dicts in execution order.
        success: True if all 5 L2 stages + Exit succeeded.
        error: Error string if any stage failed; empty string on success.
    """

    request_id: str
    applicant_id: str
    product_class: str
    verdict: str = "INSUFFICIENT_EVIDENCE"
    aggregate_score: float = 0.0
    reason_codes: list[str] = field(default_factory=list)
    dim_scores: dict[str, float] = field(default_factory=dict)
    rationale: str = ""
    rationale_source: str = "STUB_NO_LLM"
    c0_state: str = ""
    support_score: float = 0.0
    contradiction_flags: list[str] = field(default_factory=list)
    missing_evidence_flags: list[str] = field(default_factory=list)
    hitl_posture: str = "HITL_NONE"
    x3_disposition: str = ""
    exit_bundle: dict[str, Any] = field(default_factory=dict)
    compiled_prompt: dict[str, Any] = field(default_factory=dict)
    stage_receipts: list[dict[str, Any]] = field(default_factory=list)
    success: bool = False
    error: str = ""


def _extract_fec_from_c0(c0_result: Any) -> dict[str, Any]:
    """Normalize C0 output to a plain dict for downstream stages."""
    if c0_result is None:
        return {}
    if hasattr(c0_result, "to_dict"):
        return c0_result.to_dict()
    if isinstance(c0_result, dict):
        return c0_result
    return {}


def _call_llm_for_rationale(
    compiled_prompt: dict[str, Any],
) -> tuple[str, str]:
    """Call Qwen vLLM for rationale generation.

    Returns (rationale_text, source) where source is "LLM" on success or
    "STUB_LLM_ERROR" on any failure. Fail-soft — never raises.
    """
    try:
        import urllib.request  # noqa: PLC0415
        import json as _json  # noqa: PLC0415

        system_prompt = compiled_prompt.get("system_prompt", "")
        user_prompt = compiled_prompt.get("user_prompt", "")
        target_model = compiled_prompt.get("target_model", "Qwen/Qwen2.5-32B-Instruct-AWQ")

        payload = {
            "model": target_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
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
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- LLM call must never crash the pipeline;
        # verdict + reason codes are already sealed by L2
        return "", "STUB_LLM_ERROR"


def run_underwriting_dispatch(
    validated_request: ValidatedUnderwritingRequest,
) -> DispatchResult:
    """Run the full governed underwriting pipeline from U0 output to Exit.

    Args:
        validated_request: U0-validated request with full
            runtime_customization_package loaded.

    Returns:
        DispatchResult with all stage outputs, verdict, rationale, and
        X3 exit disposition.

    Does NOT raise — all failures are captured in DispatchResult.error.
    """
    result = DispatchResult(
        request_id=validated_request.request_id,
        applicant_id=validated_request.applicant_id,
        product_class=validated_request.product_class,
    )

    try:
        # ------------------------------------------------------------------ #
        # C0 — submitted document evidence extraction
        # ------------------------------------------------------------------ #
        from apps_underwriting_ai.integrations.underwriting_c0_adapter import (  # noqa: PLC0415
            UnderwritingC0Adapter,
        )

        c0_adapter = UnderwritingC0Adapter()
        c0_raw = c0_adapter.run(
            submitted_documents=list(validated_request.documents),
            demo_policy_hash=validated_request.policy_hash,
            trace_id=validated_request.trace_id,
        )
        fec_dict = _extract_fec_from_c0(c0_raw)

        result.c0_state = str(fec_dict.get("c0_state", "FAIL"))
        result.support_score = float(fec_dict.get("support_score", 0.0))
        result.contradiction_flags = list(fec_dict.get("contradiction_flags") or [])
        result.missing_evidence_flags = list(fec_dict.get("missing_evidence_flags") or [])

        # ------------------------------------------------------------------ #
        # L2 — five sequential stages
        # ------------------------------------------------------------------ #
        from apps_underwriting_ai.integrations.underwriting_l2_step_adapters import (  # noqa: PLC0415
            EvidenceRegisterAdapter,
            DocumentReconciliationAdapter,
            FeatureDerivationAdapter,
            RiskScoringAdapter,
            DecisionAssemblyAdapter,
        )

        run_context: dict[str, Any] = {
            "request_id": validated_request.request_id,
            "policy_hash": validated_request.policy_hash,
            "blueprint_hash": validated_request.blueprint_hash,
            "final_evidence_contract": fec_dict,
        }

        # Stage 1 — EvidenceRegister
        s1 = EvidenceRegisterAdapter().run(run_context)
        result.stage_receipts.append(s1.__dict__ if hasattr(s1, "__dict__") else dict(s1))

        evidence_register = s1.payload.get("evidence_register", {}) if s1.success else {}

        # Stage 2 — DocumentReconciliation
        s2 = DocumentReconciliationAdapter().run(evidence_register, run_context)
        result.stage_receipts.append(s2.__dict__ if hasattr(s2, "__dict__") else dict(s2))

        reconciliation = s2.payload.get("reconciliation_result", {}) if s2.success else {}

        # Stage 3 — FeatureDerivation
        s3 = FeatureDerivationAdapter().run(reconciliation, run_context)
        result.stage_receipts.append(s3.__dict__ if hasattr(s3, "__dict__") else dict(s3))

        risk_features = s3.payload.get("risk_features", {}) if s3.success else {}

        # Stage 4 — RiskScoring
        s4 = RiskScoringAdapter().run(risk_features, run_context)
        result.stage_receipts.append(s4.__dict__ if hasattr(s4, "__dict__") else dict(s4))

        risk_scores = s4.payload.get("risk_dimension_scores", {}) if s4.success else {}
        result.dim_scores = dict(risk_scores.get("dim_scores") or {})
        result.aggregate_score = float(risk_scores.get("aggregate_score", 0.0))

        # Stage 5 — DecisionAssembly
        s5 = DecisionAssemblyAdapter().run(risk_scores, run_context)
        result.stage_receipts.append(s5.__dict__ if hasattr(s5, "__dict__") else dict(s5))

        decision_candidate = (
            s5.payload.get("decision_packet_candidate", {}) if s5.success else {}
        )
        result.verdict = str(decision_candidate.get("verdict", "INSUFFICIENT_EVIDENCE"))
        result.reason_codes = list(decision_candidate.get("reason_codes") or [])

        # ------------------------------------------------------------------ #
        # HITL posture (from L3 workflow adapter rules, applied here)
        # ------------------------------------------------------------------ #
        from apps_underwriting_ai.integrations.underwriting_l3_workflow_adapter import (  # noqa: PLC0415
            _resolve_hitl_posture,
        )

        hitl_posture, _triggers = _resolve_hitl_posture(
            c0_state=result.c0_state,
            contradiction_flags=result.contradiction_flags,
            missing_evidence_flags=result.missing_evidence_flags,
            support_score=result.support_score,
        )
        result.hitl_posture = hitl_posture

        # ------------------------------------------------------------------ #
        # PA — prompt assembly for rationale generation
        # ------------------------------------------------------------------ #
        from apps_underwriting_ai.runtime.bindings.pa_binding import (  # noqa: PLC0415
            pa_compose_underwriting,
        )

        compiled_prompt = pa_compose_underwriting(
            validated_request=validated_request,
            decision_packet=decision_candidate,
            final_evidence_contract=fec_dict,
        )
        result.compiled_prompt = compiled_prompt

        # ------------------------------------------------------------------ #
        # LLM rationale call (skip when UW_DISPATCH_SKIP_LLM=1)
        # ------------------------------------------------------------------ #
        skip_llm = os.environ.get(_SKIP_LLM_ENV, "0") == "1"
        if skip_llm:
            result.rationale = (
                f"[STUB] Verdict={result.verdict} | "
                f"Score={result.aggregate_score:.4f} | "
                f"Reason={', '.join(result.reason_codes)} | "
                f"C0={result.c0_state}({result.support_score:.2f}) | "
                f"HITL={result.hitl_posture}"
            )
            result.rationale_source = "STUB_NO_LLM"
        else:
            rationale_text, rationale_source = _call_llm_for_rationale(compiled_prompt)
            if rationale_text:
                result.rationale = rationale_text
                result.rationale_source = rationale_source
            else:
                result.rationale = (
                    f"[LLM_UNAVAILABLE] Verdict={result.verdict} | "
                    f"Reason={', '.join(result.reason_codes)} | "
                    f"Score={result.aggregate_score:.4f}"
                )
                result.rationale_source = "STUB_LLM_ERROR"

        # Inject rationale into the decision candidate for Exit.
        decision_candidate["rationale"] = result.rationale
        decision_candidate["rationale_source"] = result.rationale_source

        # ------------------------------------------------------------------ #
        # Exit — FEC producer / X3 disposition
        # ------------------------------------------------------------------ #
        from apps_underwriting_ai.integrations.underwriting_exit_fec_producer import (  # noqa: PLC0415
            UnderwritingExitFecProducer,
        )

        exit_run_context: dict[str, Any] = {
            "request_id": validated_request.request_id,
            "policy_hash": validated_request.policy_hash,
            "blueprint_hash": validated_request.blueprint_hash,
            "verdict": result.verdict,
            "reason_code_bundle": result.reason_codes,
            "hitl_posture": result.hitl_posture,
            "demo_policy_hash": validated_request.policy_hash,
            "demo_packet_id": validated_request.request_id,
            "route_contract": {
                "route_id": "apps_underwriting_ai.decision_packet_v1",
                "route_family": "R3R4_MANAGED_WORKFLOW",
            },
        }
        exit_bundle = UnderwritingExitFecProducer().produce_exit_bundle(
            final_evidence_contract=fec_dict,
            run_context=exit_run_context,
        )
        result.exit_bundle = exit_bundle
        result.x3_disposition = str(exit_bundle.get("x3_disposition", ""))
        result.success = True

    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- dispatch must never propagate exceptions;
        # caller reads result.error and result.success
        result.error = str(exc)
        result.success = False

    return result


__all__ = [
    "DispatchResult",
    "run_underwriting_dispatch",
]
