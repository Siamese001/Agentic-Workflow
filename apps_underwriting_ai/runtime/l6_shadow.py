"""L6 shadow learning wiring for apps_underwriting_ai.

Called AFTER the full dispatch chain completes (post-Exit). Builds a
RuntimeExhaustBundle from the completed dispatch result and runs it through the
agentic_core PackageDrivenL6Binding to produce:

  - CompletedEvalRecord  — learning observations from this run
  - RCAPacket            — root-cause hypotheses for any failures
  - ProposalPackets      — inert future-run improvement proposals
  - L6GauntletResult     — promotion eligibility verdict
  - ObserverLawReceipt   — confirms L6 is post-run / read-only

Observer law invariants (hardcoded, never relaxed):
  - L6 is FUTURE_RUN_ONLY — never mutates the current run
  - No L4 direct write — UWG_ONLY path only
  - No open-web access from L6 path
  - Fail-soft — any exception returns a L6ShadowResult with success=False
    and logs the error; it must never crash the caller

Best-practice grounding (OpenAI/Anthropic/Google research 2025):
  - Shadow evaluation runs post-Exit, decoupled from decisioning
  - Promotion requires gauntlet pass (threshold 0.75, z=2.576, n≥100)
  - Judge calibration cadence enforced via learning_profiles.yaml
  - HITL_REQUIRED posture is fed into L6 as a learning signal
    (high escalation rate → proposal to tune scoring thresholds)

Plan: apps-underwriting-ai-l6-shadow-wiring (inline, no separate plan needed
for this isolated post-run consumer).
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

_log = logging.getLogger(__name__)

_L6_CERT_REF = "cert://apps_underwriting_ai/l6_shadow/v1"


@dataclass
class L6ShadowResult:
    """Output of the L6 shadow pass."""

    run_id: str
    success: bool

    # Core L6 outputs (all read-only, inert)
    eval_record_seal: str = ""
    gauntlet_passed: bool = False
    gauntlet_receipt: str = ""
    rca_root_causes: list[str] | None = None
    proposal_count: int = 0
    observer_law_compliant: bool = False
    future_run_activation_candidate: str = ""

    # Promotion signal summary
    promotion_eligible: bool = False
    ingest_quality_score: float = 0.0

    error: str | None = None


def run_l6_shadow(
    dispatch_result: Any,
    u0_package: dict[str, Any],
) -> L6ShadowResult:
    """Run L6 shadow learning on a completed underwriting dispatch result.

    Args:
        dispatch_result: result object from run_underwriting_dispatch().
        u0_package: runtime_customization_package from ValidatedUnderwritingRequest.

    Returns:
        L6ShadowResult — always returns, never raises.
    """
    run_id = getattr(dispatch_result, "request_id", f"uw-{int(time.time())}")

    try:
        from agentic_core.L6_system_learning.future_run_promotion.package_driven_l6_binding import (  # noqa: PLC0415
            PackageDrivenL6Binding,
        )
        from agentic_core.L6_system_learning.future_run_promotion.completed_run_evaluator import (  # noqa: PLC0415
            RuntimeExhaustBundle as L6ExhaustBundle,
        )
    except ImportError as exc:
        _log.warning("[l6_shadow] agentic_core L6 import failed: %s", exc)
        return L6ShadowResult(run_id=run_id, success=False, error=f"import_error: {exc}")

    try:
        # ── Build L6 exhaust bundle from DispatchResult ────────────────────
        # Each field maps a stage output to the L6 read-only evidence surface.
        # judge_evidence_results carries per-dimension score + rationale signal.
        exit_bundle = getattr(dispatch_result, "exit_bundle", {}) or {}
        stage_receipts = getattr(dispatch_result, "stage_receipts", {}) or {}
        fec = getattr(dispatch_result, "fec_dict", None) or {}

        judge_evidence: list[dict[str, Any]] = []
        for dim, score in (getattr(dispatch_result, "dim_scores", None) or {}).items():
            judge_evidence.append({
                "dimension": dim,
                "score": score,
                "rationale_source": getattr(dispatch_result, "rationale_source", "UNKNOWN"),
                "verdict": getattr(dispatch_result, "verdict", "UNKNOWN"),
            })
        # Add rationale quality as a judge signal
        rationale = getattr(dispatch_result, "rationale", "") or ""
        judge_evidence.append({
            "dimension": "rationale_quality",
            "score": min(1.0, len(rationale) / 500.0),  # proxy: length vs 500 chars
            "rationale_source": getattr(dispatch_result, "rationale_source", "UNKNOWN"),
            "verdict": "PASS" if len(rationale) > 50 else "FAIL",
        })

        gate_mesh = {
            "verdict": getattr(dispatch_result, "verdict", "UNKNOWN"),
            "x3_disposition": getattr(dispatch_result, "x3_disposition", ""),
            "hitl_posture": getattr(dispatch_result, "hitl_posture", "HITL_NONE"),
            "exit_bundle_violations": exit_bundle.get("violations", []),
            "cache_metrics": {
                "hit_rate": 0.0,  # UW pipeline has no cache layer yet
            },
            "stage_receipts": stage_receipts,
        }

        sealed_l2 = {
            "aggregate_score": getattr(dispatch_result, "aggregate_score", 0.0),
            "reason_codes": list(getattr(dispatch_result, "reason_codes", [])),
            "dim_scores": dict(getattr(dispatch_result, "dim_scores", None) or {}),
        }

        learning_profile = u0_package.get("learning_profiles", {})
        meta_feedback_profile = u0_package.get("orchestration_profiles", {})

        exhaust_bundle = L6ExhaustBundle(
            run_id=run_id,
            trace_root=getattr(dispatch_result, "trace_id", run_id),
            exit_disposition_receipt=exit_bundle,
            gate_mesh_result=gate_mesh,
            x1_checkout_result={},   # Not wired for UW pipeline yet
            x2_aggregation_result={},
            sealed_l2_artifact=sealed_l2,
            final_evidence_contract=dict(fec),
            judge_evidence_results=judge_evidence,
            u0_package_refs={
                k: f"u0://{k}" for k in u0_package if isinstance(u0_package[k], dict)
            },
            learning_profile_ref="learning_profiles",
            meta_feedback_profile_ref="orchestration_profiles",
        )

        # ── Run PackageDrivenL6Binding ─────────────────────────────────────
        l6_package = dict(u0_package)
        l6_package["learning_profile"] = learning_profile
        l6_package["meta_feedback_profile"] = meta_feedback_profile
        l6_package["promotion_policy"] = {
            "threshold": learning_profile.get("promotion_threshold", 0.75),
            "min_n": learning_profile.get("min_n_each_arm", 100),
            "z_score": learning_profile.get("z_score", 2.576),
        }

        binding = PackageDrivenL6Binding(l6_package)
        l6_result = binding.process_completed_run(exhaust_bundle)

        # ── Emit structured log for OTEL span pickup ───────────────────────
        rca_causes = []
        if hasattr(l6_result.rca_packet, "root_causes"):
            rca_causes = [str(c) for c in (l6_result.rca_packet.root_causes or [])]

        _log.info(
            "[l6_shadow] completed run=%s gauntlet=%s proposals=%d rca_causes=%d",
            run_id,
            l6_result.gauntlet_result.passed,
            len(l6_result.proposal_packets),
            len(rca_causes),
        )

        # ── Emit OTEL span (fail-soft) ─────────────────────────────────────
        try:
            from apps_underwriting_ai.integrations.observability_adapter import (  # noqa: PLC0415
                ObservabilityAdapter,
            )
            ObservabilityAdapter().emit(
                "l6_shadow.complete",
                run_id=run_id,
                gauntlet_passed=l6_result.gauntlet_result.passed,
                proposal_count=len(l6_result.proposal_packets),
                ingest_quality=exhaust_bundle.final_evidence_contract.get("support_score", 0.0),
                hitl_posture=gate_mesh["hitl_posture"],
                observer_law_compliant=l6_result.observer_law_receipt.compliant
                    if hasattr(l6_result.observer_law_receipt, "compliant") else True,
            )
        except Exception:  # noqa: BLE001  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            # guardian: allow-broad-except -- OTEL emit must never crash L6 path
            pass

        return L6ShadowResult(
            run_id=run_id,
            success=True,
            eval_record_seal=l6_result.eval_record_seal,
            gauntlet_passed=l6_result.gauntlet_result.passed,
            gauntlet_receipt=l6_result.gauntlet_receipt,
            rca_root_causes=rca_causes,
            proposal_count=len(l6_result.proposal_packets),
            observer_law_compliant=(
                l6_result.observer_law_receipt.compliant
                if hasattr(l6_result.observer_law_receipt, "compliant") else True
            ),
            future_run_activation_candidate=l6_result.future_run_activation_receipt_candidate,
            promotion_eligible=l6_result.gauntlet_result.passed,
            ingest_quality_score=getattr(dispatch_result, "aggregate_score", 0.0),
        )

    except Exception as exc:  # noqa: BLE001  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        # guardian: allow-broad-except -- L6 shadow must never crash the main dispatch path
        _log.warning("[l6_shadow] failed run=%s error=%s", run_id, exc)
        return L6ShadowResult(run_id=run_id, success=False, error=str(exc))
