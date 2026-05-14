"""Exit binding for apps_underwriting_ai.

Runs UnderwritingExitFecProducer and builds the X3Disposition that
AppIngressRunner._run_profile_stages returns as the final pipeline result.

AppIngressRunner calls:
    exit_fn(sealed=sealed, target_company=..., target_role=...,
            output_directory=None, writeback_policy=None)

The underwriting domain does not use target_company / target_role (it uses
applicant_id / product_class). Those kwargs are accepted but ignored.

Pattern: pure function at the boundary; UnderwritingExitFecProducer may
read demo data. No L4 writes. Fail-closed on error.

Plan: apps-underwriting-ai-profile-migration (Bundle B).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from apps_underwriting_ai.runtime.bindings.l2_binding import UWSealedArtifact

UW_EXIT_CERT_REF: str = "exit-apps-underwriting-ai-underwriting-decision-v1"


@dataclass
class UWExitResult:
    """Full exit output for one underwriting run.

    Compatible with AppIngressRunner._run_profile_stages which returns
    exit_result.disposition. Here disposition IS the UWExitResult itself
    since underwriting does not produce a generic X3Disposition.

    Also exposes a .disposition property for runner compatibility.
    """

    request_id: str
    applicant_id: str
    product_class: str
    verdict: str
    aggregate_score: float
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
    success: bool = True
    error: str = ""
    exit_timestamp: str = ""
    l5_certification_ref: str = UW_EXIT_CERT_REF

    @property
    def disposition(self) -> "UWExitResult":
        """Return self — AppIngressRunner reads exit_result.disposition."""
        return self


def exit_finalize_underwriting(
    *,
    sealed: UWSealedArtifact,
    target_company: str = "",
    target_role: str = "",
    output_directory: str | None = None,
    writeback_policy: Any | None = None,
) -> UWExitResult:
    """Run UnderwritingExitFecProducer and return the final UWExitResult.

    Called by AppIngressRunner as:
        exit_fn(sealed=sealed, target_company=..., target_role=...,
                output_directory=None, writeback_policy=None)

    target_company and target_role are accepted for interface compatibility
    but ignored — underwriting uses applicant_id and product_class.

    Args:
        sealed: UWSealedArtifact from L2 binding.
        target_company: Ignored (interface compat with apps_rg exit shape).
        target_role: Ignored (interface compat with apps_rg exit shape).
        output_directory: Ignored.
        writeback_policy: Ignored.

    Returns:
        UWExitResult with all pipeline outputs and .disposition = self.

    Raises:
        RuntimeError: If UnderwritingExitFecProducer raises.
    """
    from apps_underwriting_ai.integrations.underwriting_exit_fec_producer import (  # noqa: PLC0415
        UnderwritingExitFecProducer,
    )

    exit_run_context: dict[str, Any] = {
        "request_id": sealed.request_id,
        "policy_hash": sealed.run_context.get("policy_hash", ""),
        "blueprint_hash": sealed.run_context.get("blueprint_hash", ""),
        "verdict": sealed.verdict,
        "reason_code_bundle": sealed.reason_codes,
        "hitl_posture": sealed.hitl_posture,
        "demo_policy_hash": sealed.run_context.get("policy_hash", ""),
        "demo_packet_id": sealed.request_id,
        "route_contract": {
            "route_id": "apps_underwriting_ai.decision_packet_v1",
            "route_family": "R3R4_MANAGED_WORKFLOW",
        },
    }

    exit_bundle = UnderwritingExitFecProducer().produce_exit_bundle(
        final_evidence_contract=sealed.fec_dict,
        run_context=exit_run_context,
    )

    return UWExitResult(
        request_id=sealed.request_id,
        applicant_id=sealed.applicant_id,
        product_class=sealed.product_class,
        verdict=sealed.verdict,
        aggregate_score=sealed.aggregate_score,
        reason_codes=sealed.reason_codes,
        dim_scores=sealed.dim_scores,
        rationale=sealed.rationale,
        rationale_source=sealed.rationale_source,
        c0_state=sealed.c0_state,
        support_score=sealed.support_score,
        contradiction_flags=sealed.contradiction_flags,
        missing_evidence_flags=sealed.missing_evidence_flags,
        hitl_posture=sealed.hitl_posture,
        x3_disposition=str(exit_bundle.get("x3_disposition", "")),
        exit_bundle=exit_bundle,
        compiled_prompt=sealed.compiled_prompt,
        stage_receipts=sealed.stage_receipts,
        success=True,
        error="",
        exit_timestamp=datetime.now(timezone.utc).isoformat(),
        l5_certification_ref=sealed.l5_certification_ref or UW_EXIT_CERT_REF,
    )


__all__ = [
    "UW_EXIT_CERT_REF",
    "UWExitResult",
    "exit_finalize_underwriting",
]
