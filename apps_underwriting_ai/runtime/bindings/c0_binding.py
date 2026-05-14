"""C0 grounding binding for apps_underwriting_ai.

This binding owns the ENTIRE deterministic underwriting pipeline:

  C0  — UnderwritingC0Adapter: document evidence extraction
  L2 Stage 1 — EvidenceRegisterAdapter
  L2 Stage 2 — DocumentReconciliationAdapter
  L2 Stage 3 — FeatureDerivationAdapter
  L2 Stage 4 — RiskScoringAdapter
  L2 Stage 5 — DecisionAssemblyAdapter
  L3 — _resolve_hitl_posture

AppIngressRunner calls: c0_fn(route, validated) → UWEvidenceResult
The returned UWEvidenceResult carries all deterministic pipeline
outputs needed by the PA binding for rationale compilation.

Pattern: pure function at the boundary; adapter calls may do I/O
within the underwriting demo data layer. No LLM calls. No L4 writes.
Fail-closed on stage failure — raises UWC0PipelineError.

Plan: apps-underwriting-ai-profile-migration (Bundle B).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_underwriting_ai.runtime.bindings.l0_binding import UWRoute
from apps_underwriting_ai.runtime.contracts.underwriting_ingress_payload import (
    ValidatedUnderwritingRequest,
)

UW_C0_CERT_REF: str = "c0-apps-underwriting-ai-underwriting-decision-v1"


class UWC0PipelineError(RuntimeError):
    """Raised when the deterministic underwriting pipeline fails a stage."""


@dataclass
class UWEvidenceResult:
    """Full output of the deterministic underwriting pipeline (C0 + 5 L2 + HITL).

    Consumed by:
    - pa_binding.pa_compose_underwriting_profile (PA stage)
    - l2_binding.l2_execute_underwriting (LLM rationale stage)
    - exit_binding.exit_finalize_underwriting (Exit stage)
    """

    request_id: str
    applicant_id: str
    product_class: str

    c0_state: str = "FAIL"
    support_score: float = 0.0
    contradiction_flags: list[str] = field(default_factory=list)
    missing_evidence_flags: list[str] = field(default_factory=list)
    fec_dict: dict[str, Any] = field(default_factory=dict)

    verdict: str = "INSUFFICIENT_EVIDENCE"
    aggregate_score: float = 0.0
    reason_codes: list[str] = field(default_factory=list)
    dim_scores: dict[str, float] = field(default_factory=dict)
    decision_candidate: dict[str, Any] = field(default_factory=dict)

    hitl_posture: str = "HITL_NONE"
    stage_receipts: list[dict[str, Any]] = field(default_factory=list)

    l5_certification_ref: str = UW_C0_CERT_REF
    run_context: dict[str, Any] = field(default_factory=dict)


def _extract_fec(c0_result: Any) -> dict[str, Any]:
    if c0_result is None:
        return {}
    if hasattr(c0_result, "to_dict"):
        return c0_result.to_dict()
    if isinstance(c0_result, dict):
        return c0_result
    return {}


def c0_run_underwriting(
    route: UWRoute,
    validated: ValidatedUnderwritingRequest,
) -> UWEvidenceResult:
    """Run the full deterministic underwriting pipeline.

    Executes C0 → L2(×5) → HITL resolution in order. Fail-closed:
    raises UWC0PipelineError on any stage failure.

    Called by AppIngressRunner as c0_fn(route, validated).

    Args:
        route: L0 route output (carries request metadata).
        validated: U0-validated underwriting request.

    Returns:
        UWEvidenceResult with all pipeline outputs.

    Raises:
        UWC0PipelineError: If any pipeline stage fails.
    """
    result = UWEvidenceResult(
        request_id=validated.request_id,
        applicant_id=validated.applicant_id,
        product_class=validated.product_class,
        l5_certification_ref=validated.u0_cert_ref or UW_C0_CERT_REF,
    )

    # ------------------------------------------------------------------ #
    # C0 — document evidence extraction
    # ------------------------------------------------------------------ #
    from apps_underwriting_ai.integrations.underwriting_c0_adapter import (  # noqa: PLC0415
        UnderwritingC0Adapter,
    )

    c0_adapter = UnderwritingC0Adapter()
    c0_raw = c0_adapter.run(
        submitted_documents=list(validated.documents),
        demo_policy_hash=validated.policy_hash,
        trace_id=validated.trace_id,
    )
    fec_dict = _extract_fec(c0_raw)

    result.fec_dict = fec_dict
    result.c0_state = str(fec_dict.get("c0_state", "FAIL"))
    result.support_score = float(fec_dict.get("support_score", 0.0))
    result.contradiction_flags = list(fec_dict.get("contradiction_flags") or [])
    result.missing_evidence_flags = list(fec_dict.get("missing_evidence_flags") or [])

    # ------------------------------------------------------------------ #
    # L2 — five sequential deterministic stages
    # ------------------------------------------------------------------ #
    from apps_underwriting_ai.integrations.underwriting_l2_step_adapters import (  # noqa: PLC0415
        EvidenceRegisterAdapter,
        DocumentReconciliationAdapter,
        FeatureDerivationAdapter,
        RiskScoringAdapter,
        DecisionAssemblyAdapter,
    )

    run_context: dict[str, Any] = {
        "request_id": validated.request_id,
        "policy_hash": validated.policy_hash,
        "blueprint_hash": validated.blueprint_hash,
        "final_evidence_contract": fec_dict,
    }
    result.run_context = run_context

    s1 = EvidenceRegisterAdapter().run(run_context)
    result.stage_receipts.append(s1.__dict__ if hasattr(s1, "__dict__") else dict(s1))
    if not s1.success:
        raise UWC0PipelineError(f"Stage 1 EvidenceRegister failed: {getattr(s1, 'error', '')}")
    evidence_register = s1.payload.get("evidence_register", {})

    s2 = DocumentReconciliationAdapter().run(evidence_register, run_context)
    result.stage_receipts.append(s2.__dict__ if hasattr(s2, "__dict__") else dict(s2))
    if not s2.success:
        raise UWC0PipelineError(f"Stage 2 DocumentReconciliation failed: {getattr(s2, 'error', '')}")
    reconciliation = s2.payload.get("reconciliation_result", {})

    s3 = FeatureDerivationAdapter().run(reconciliation, run_context)
    result.stage_receipts.append(s3.__dict__ if hasattr(s3, "__dict__") else dict(s3))
    if not s3.success:
        raise UWC0PipelineError(f"Stage 3 FeatureDerivation failed: {getattr(s3, 'error', '')}")
    risk_features = s3.payload.get("risk_features", {})

    s4 = RiskScoringAdapter().run(risk_features, run_context)
    result.stage_receipts.append(s4.__dict__ if hasattr(s4, "__dict__") else dict(s4))
    if not s4.success:
        raise UWC0PipelineError(f"Stage 4 RiskScoring failed: {getattr(s4, 'error', '')}")
    risk_scores = s4.payload.get("risk_dimension_scores", {})
    result.dim_scores = dict(risk_scores.get("dim_scores") or {})
    result.aggregate_score = float(risk_scores.get("aggregate_score", 0.0))

    s5 = DecisionAssemblyAdapter().run(risk_scores, run_context)
    result.stage_receipts.append(s5.__dict__ if hasattr(s5, "__dict__") else dict(s5))
    if not s5.success:
        raise UWC0PipelineError(f"Stage 5 DecisionAssembly failed: {getattr(s5, 'error', '')}")
    decision_candidate = s5.payload.get("decision_packet_candidate", {}) if s5.success else {}
    result.verdict = str(decision_candidate.get("verdict", "INSUFFICIENT_EVIDENCE"))
    result.reason_codes = list(decision_candidate.get("reason_codes") or [])
    result.decision_candidate = decision_candidate

    # ------------------------------------------------------------------ #
    # HITL posture resolution
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

    return result


__all__ = [
    "UW_C0_CERT_REF",
    "UWC0PipelineError",
    "UWEvidenceResult",
    "c0_run_underwriting",
]
