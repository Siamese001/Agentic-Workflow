"""L2 step adapters for apps_underwriting_ai five-stage workflow.

Each adapter wraps one stage of the underwriting workflow and emits
the canonical L2 E-stage receipt. Stage ordering:

  E1 — EvidenceRegisterAdapter      (L2.E1.underwriting_execution_context_bound)
  E2 — DocumentReconciliationAdapter (L2.E2.underwriting_evidence_validated)
  E3a — FeatureDerivationAdapter     (L2.E3.underwriting_stage_executed)
  E3b — RiskScoringAdapter           (L2.E3.underwriting_stage_executed)
  E5 — DecisionAssemblyAdapter       (L2.E5.underwriting_artifact_sealed)

Invariants (enforced here):
  - No new retrieval inside any step adapter (C0 ran before L2; all
    evidence comes from run_context["final_evidence_contract"])
  - No L4 writes inside any step adapter (UWG-only path)
  - Each adapter emits exactly one receipt before returning
  - Adapters never raise — fail-soft returning success=False receipt

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 W3.2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

L2_RECEIPT_E1 = "L2.E1.underwriting_execution_context_bound"
L2_RECEIPT_E2 = "L2.E2.underwriting_evidence_validated"
L2_RECEIPT_E3 = "L2.E3.underwriting_stage_executed"
L2_RECEIPT_E5 = "L2.E5.underwriting_artifact_sealed"

# Canonical risk dimension IDs scored in Stage 4.
RISK_DIMENSIONS = (
    "creditworthiness",
    "income_stability",
    "debt_service_capacity",
    "document_completeness",
    "contradiction_risk",
)


@dataclass
class L2StepReceipt:
    """Receipt emitted by each L2 step adapter.

    Fields:
      receipt_type: Canonical L2 E-stage receipt identifier.
      stage_id: Stage identifier matching the L3 stage contract.
      output_type: Type name of the primary output artifact.
      success: True when the stage completed without errors.
      evidence_refs: Evidence IDs consumed/produced by this stage.
      payload: Stage-specific output data (read-only artifact).
      no_retrieval: Always True — no new retrieval in L2.
      no_l4_write: Always True — no durable writes in L2.
    """

    receipt_type: str
    stage_id: str
    output_type: str
    success: bool = False
    evidence_refs: list[str] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)
    no_retrieval: bool = True
    no_l4_write: bool = True


def _extract_fec(run_context: dict[str, Any]) -> dict[str, Any]:
    """Extract FinalEvidenceContract dict from run_context. Never raises."""
    fec = run_context.get("final_evidence_contract") or {}
    if hasattr(fec, "to_dict"):
        fec = fec.to_dict()
    return fec if isinstance(fec, dict) else {}


class EvidenceRegisterAdapter:
    """Stage 1 — binds execution context; initializes EvidenceRegister.

    Reads FinalEvidenceContract from run_context to initialize the register.
    Stage 1 is the only stage that does NOT require prior evidence_refs —
    it bootstraps the register from the FEC directly.

    No retrieval. No L4 write.
    """

    RECEIPT = L2_RECEIPT_E1

    def run(self, run_context: dict[str, Any]) -> L2StepReceipt:
        """Bind execution context and initialize EvidenceRegister.

        Args:
            run_context: Runtime context with final_evidence_contract, request_id.

        Returns:
            L2StepReceipt with EvidenceRegister payload.
        """
        try:
            fec = _extract_fec(run_context)
            evidence_ids = fec.get("evidence_ids", [])
            c0_state = fec.get("c0_state", "FAIL")
            evidence_contract_id = fec.get("evidence_contract_id", "")
            document_count = fec.get("document_count", 0)
            required_present = fec.get("required_classes_present", [])
            optional_present = fec.get("optional_classes_present", [])

            register = {
                "evidence_contract_id": evidence_contract_id,
                "c0_state": c0_state,
                "evidence_ids": evidence_ids,
                "document_count": document_count,
                "required_classes_present": required_present,
                "optional_classes_present": optional_present,
                "context_bound": True,
                "request_id": run_context.get("request_id", ""),
                "capability_id": run_context.get("capability_id", ""),
            }
            return L2StepReceipt(
                receipt_type=self.RECEIPT,
                stage_id="stage_1_evidence_register",
                output_type="EvidenceRegister",
                success=True,
                evidence_refs=[],
                payload={"evidence_register": register},
                no_retrieval=True,
                no_l4_write=True,
            )
        except Exception:  # noqa: BLE001
            # guardian: allow-broad-except -- L2 adapters are fail-soft
            return L2StepReceipt(
                receipt_type=self.RECEIPT,
                stage_id="stage_1_evidence_register",
                output_type="EvidenceRegister",
                success=False,
                no_retrieval=True,
                no_l4_write=True,
            )


class DocumentReconciliationAdapter:
    """Stage 2 — reconciles submitted documents against the EvidenceRegister.

    Requires evidence_refs from Stage 1 EvidenceRegister (via injected_evidence_refs
    in the L3 stage contract). Builds a reconciliation map from extracted span data.

    No retrieval. No L4 write.
    """

    RECEIPT = L2_RECEIPT_E2

    def run(
        self,
        evidence_register: dict[str, Any],
        run_context: dict[str, Any],
    ) -> L2StepReceipt:
        """Reconcile documents against the evidence register.

        Args:
            evidence_register: EvidenceRegister dict from Stage 1.
            run_context: Runtime context with final_evidence_contract.

        Returns:
            L2StepReceipt with ReconciliationResult payload.
        """
        try:
            fec = _extract_fec(run_context)
            evidence_ids = fec.get("evidence_ids", [])
            span_map = fec.get("extracted_span_map", {})
            coverage_map = fec.get("document_coverage_map", {})
            missing_flags = fec.get("missing_evidence_flags", [])
            contradiction_flags = fec.get("contradiction_flags", [])

            # Build reconciliation result from extracted spans.
            reconciled_spans: dict[str, Any] = {}
            for ev_id in evidence_ids:
                span = span_map.get(ev_id)
                if span:
                    reconciled_spans[ev_id] = {
                        "evidence_id": ev_id,
                        "document_class": span.get("document_class"),
                        "field_name": span.get("field_name"),
                        "value": span.get("value"),
                        "confidence": span.get("confidence", 0.75),
                        "reconciled": True,
                    }

            reconciliation_result = {
                "reconciled_span_count": len(reconciled_spans),
                "reconciled_spans": reconciled_spans,
                "document_coverage_map": coverage_map,
                "missing_required_classes": missing_flags,
                "contradiction_flags": contradiction_flags,
                "evidence_ids": evidence_ids,
                "reconciliation_status": (
                    "DEGRADED" if missing_flags and not evidence_ids else
                    "PARTIAL" if missing_flags else
                    "COMPLETE"
                ),
            }
            return L2StepReceipt(
                receipt_type=self.RECEIPT,
                stage_id="stage_2_document_reconciliation",
                output_type="ReconciliationResult",
                success=True,
                evidence_refs=list(evidence_ids),
                payload={"reconciliation_result": reconciliation_result},
                no_retrieval=True,
                no_l4_write=True,
            )
        except Exception:  # noqa: BLE001
            # guardian: allow-broad-except -- L2 adapters are fail-soft
            return L2StepReceipt(
                receipt_type=self.RECEIPT,
                stage_id="stage_2_document_reconciliation",
                output_type="ReconciliationResult",
                success=False,
                no_retrieval=True,
                no_l4_write=True,
            )


class FeatureDerivationAdapter:
    """Stage 3 — derives risk features from reconciled evidence spans.

    Requires evidence_refs from Stage 2 ReconciliationResult. All feature
    values are derived from extracted spans — no new retrieval.

    No retrieval. No L4 write.
    """

    RECEIPT = L2_RECEIPT_E3

    def run(
        self,
        reconciliation_result: dict[str, Any],
        run_context: dict[str, Any],
    ) -> L2StepReceipt:
        """Derive risk features from reconciled evidence.

        Args:
            reconciliation_result: ReconciliationResult dict from Stage 2.
            run_context: Runtime context.

        Returns:
            L2StepReceipt with RiskFeatures payload.
        """
        try:
            reconciled_spans: dict[str, Any] = reconciliation_result.get("reconciled_spans", {})
            evidence_ids = reconciliation_result.get("evidence_ids", [])

            # Extract field values from reconciled spans for feature derivation.
            field_values: dict[str, Any] = {
                span["field_name"]: span["value"]
                for span in reconciled_spans.values()
                if "field_name" in span and "value" in span
            }

            risk_features: dict[str, Any] = {
                "credit_score": field_values.get("credit_score"),
                "annual_gross_income": field_values.get("annual_gross_income"),
                "average_monthly_balance": field_values.get("average_monthly_balance"),
                "account_tenure_months": field_values.get("account_tenure_months"),
                "derogatory_mark_count": field_values.get("derogatory_mark_count"),
                "utilization_rate": field_values.get("utilization_rate"),
                "overdraft_count_12m": field_values.get("overdraft_count_12m"),
                "employment_status": field_values.get("employment_status"),
                "debt_service_capacity": _derive_dsc(field_values),
                "income_stability_indicator": _derive_income_stability(field_values),
                "evidence_ids": evidence_ids,
                "derived_from_evidence": True,
                "open_web_features": False,
            }
            return L2StepReceipt(
                receipt_type=self.RECEIPT,
                stage_id="stage_3_feature_derivation",
                output_type="RiskFeatures",
                success=True,
                evidence_refs=list(evidence_ids),
                payload={"risk_features": risk_features},
                no_retrieval=True,
                no_l4_write=True,
            )
        except Exception:  # noqa: BLE001
            # guardian: allow-broad-except -- L2 adapters are fail-soft
            return L2StepReceipt(
                receipt_type=self.RECEIPT,
                stage_id="stage_3_feature_derivation",
                output_type="RiskFeatures",
                success=False,
                no_retrieval=True,
                no_l4_write=True,
            )


def _derive_dsc(field_values: dict[str, Any]) -> float | None:
    """Derive debt-service capacity ratio from income and balance fields."""
    try:
        income = float(field_values.get("annual_gross_income") or 0)
        balance = float(field_values.get("average_monthly_balance") or 0)
        if income > 0 and balance > 0:
            monthly_income = income / 12.0
            return round(balance / monthly_income, 4) if monthly_income > 0 else None
    except (TypeError, ValueError):
        pass
    return None


def _derive_income_stability(field_values: dict[str, Any]) -> str:
    """Derive income stability indicator from available features."""
    status = str(field_values.get("employment_status") or "").upper()
    tenure = field_values.get("account_tenure_months")
    overdraft = field_values.get("overdraft_count_12m")

    if status == "UNEMPLOYED":
        return "UNSTABLE"
    if tenure is not None and int(tenure) >= 24 and (overdraft is None or int(overdraft) <= 2):
        return "STABLE"
    if tenure is not None and int(tenure) >= 12:
        return "MODERATE"
    return "INSUFFICIENT_DATA"


class RiskScoringAdapter:
    """Stage 4 — scores risk dimensions from derived features.

    Requires evidence_refs from Stage 3 RiskFeatures. All scores are
    computed deterministically from feature values — no LLM calls.

    No retrieval. No L4 write.
    """

    RECEIPT = L2_RECEIPT_E3

    def run(
        self,
        risk_features: dict[str, Any],
        run_context: dict[str, Any],
    ) -> L2StepReceipt:
        """Score risk dimensions from derived features.

        Args:
            risk_features: RiskFeatures dict from Stage 3.
            run_context: Runtime context.

        Returns:
            L2StepReceipt with RiskDimensionScores payload.
        """
        try:
            evidence_ids = risk_features.get("evidence_ids", [])
            dim_scores: dict[str, float] = {}
            dim_evidence: dict[str, list[str]] = {}

            # creditworthiness: credit_score 300–850 → normalized [0,1].
            cs = risk_features.get("credit_score")
            if cs is not None:
                dim_scores["creditworthiness"] = round(
                    min(max((float(cs) - 300) / 550, 0.0), 1.0), 4
                )
                dim_evidence["creditworthiness"] = list(evidence_ids)

            # income_stability: derived indicator → score.
            isi = risk_features.get("income_stability_indicator", "INSUFFICIENT_DATA")
            isi_map = {"STABLE": 1.0, "MODERATE": 0.65, "UNSTABLE": 0.15, "INSUFFICIENT_DATA": 0.0}
            dim_scores["income_stability"] = isi_map.get(isi, 0.0)
            dim_evidence["income_stability"] = list(evidence_ids)

            # debt_service_capacity: DSC ratio → score (higher ratio = better).
            dsc = risk_features.get("debt_service_capacity")
            if dsc is not None:
                dim_scores["debt_service_capacity"] = round(min(float(dsc) / 3.0, 1.0), 4)
                dim_evidence["debt_service_capacity"] = list(evidence_ids)

            # document_completeness: from FEC support_score via run_context.
            fec = _extract_fec(run_context)
            support_score = float(fec.get("support_score", 0.0))
            dim_scores["document_completeness"] = support_score
            dim_evidence["document_completeness"] = list(evidence_ids)

            # contradiction_risk: inverse of contradiction flag count.
            contradiction_count = len(fec.get("contradiction_flags", []))
            dim_scores["contradiction_risk"] = round(
                max(1.0 - contradiction_count * 0.40, 0.0), 4
            )
            dim_evidence["contradiction_risk"] = list(evidence_ids)

            aggregate_score = (
                sum(dim_scores.values()) / len(dim_scores) if dim_scores else 0.0
            )

            risk_dimension_scores = {
                "dim_scores": dim_scores,
                "dim_evidence": dim_evidence,
                "aggregate_score": round(aggregate_score, 4),
                "scored_dimensions": list(dim_scores.keys()),
                "evidence_ids": evidence_ids,
            }
            return L2StepReceipt(
                receipt_type=self.RECEIPT,
                stage_id="stage_4_risk_scoring",
                output_type="RiskDimensionScores",
                success=True,
                evidence_refs=list(evidence_ids),
                payload={"risk_dimension_scores": risk_dimension_scores},
                no_retrieval=True,
                no_l4_write=True,
            )
        except Exception:  # noqa: BLE001
            # guardian: allow-broad-except -- L2 adapters are fail-soft
            return L2StepReceipt(
                receipt_type=self.RECEIPT,
                stage_id="stage_4_risk_scoring",
                output_type="RiskDimensionScores",
                success=False,
                no_retrieval=True,
                no_l4_write=True,
            )


class DecisionAssemblyAdapter:
    """Stage 5 — seals the DecisionPacket artifact.

    Requires evidence_refs from Stage 4 RiskDimensionScores. Assembles
    verdict, reason_codes, and evidence_refs into a sealed candidate.
    PA compiler (LLM firewall) must precede any rationale generation
    (enforced in W4). This adapter produces the deterministic verdict
    and reason_codes; rationale enrichment is handled by the PA compiler.

    No retrieval. No L4 write.
    """

    RECEIPT = L2_RECEIPT_E5

    # Verdict thresholds.
    APPROVE_THRESHOLD = 0.70
    REFER_THRESHOLD = 0.45

    def run(
        self,
        risk_scores: dict[str, Any],
        run_context: dict[str, Any],
    ) -> L2StepReceipt:
        """Seal the DecisionPacket artifact.

        Args:
            risk_scores: RiskDimensionScores dict from Stage 4.
            run_context: Runtime context.

        Returns:
            L2StepReceipt with DecisionPacketCandidate payload.
        """
        try:
            evidence_ids = risk_scores.get("evidence_ids", [])
            dim_scores: dict[str, float] = risk_scores.get("dim_scores", {})
            aggregate_score: float = float(risk_scores.get("aggregate_score", 0.0))

            verdict = self._derive_verdict(aggregate_score, dim_scores)
            reason_codes = self._derive_reason_codes(dim_scores, run_context)

            candidate = {
                "verdict": verdict,
                "aggregate_score": aggregate_score,
                "dim_scores": dim_scores,
                "reason_codes": reason_codes,
                "evidence_refs": evidence_ids,
                "rationale": "",
                "rationale_source": "PENDING_PA_COMPILER",
                "artifact_sealed": True,
                "verdict_locked": True,
                "reason_codes_locked": True,
            }
            return L2StepReceipt(
                receipt_type=self.RECEIPT,
                stage_id="stage_5_decision_assembly",
                output_type="DecisionPacketCandidate",
                success=True,
                evidence_refs=list(evidence_ids),
                payload={"decision_packet_candidate": candidate},
                no_retrieval=True,
                no_l4_write=True,
            )
        except Exception:  # noqa: BLE001
            # guardian: allow-broad-except -- L2 adapters are fail-soft
            return L2StepReceipt(
                receipt_type=self.RECEIPT,
                stage_id="stage_5_decision_assembly",
                output_type="DecisionPacketCandidate",
                success=False,
                no_retrieval=True,
                no_l4_write=True,
            )

    def _derive_verdict(
        self, aggregate_score: float, dim_scores: dict[str, float]
    ) -> str:
        """Derive verdict deterministically from aggregate score and dim scores."""
        if aggregate_score >= self.APPROVE_THRESHOLD:
            return "APPROVE"
        if aggregate_score >= self.REFER_THRESHOLD:
            return "REFER"
        return "DECLINE"

    def _derive_reason_codes(
        self, dim_scores: dict[str, float], run_context: dict[str, Any]
    ) -> list[str]:
        """Derive reason codes from dim scores and FEC fields."""
        codes: list[str] = []
        fec = _extract_fec(run_context)

        if dim_scores.get("creditworthiness", 1.0) < 0.40:
            codes.append("RC001_LOW_CREDIT_SCORE")
        if dim_scores.get("income_stability", 1.0) < 0.50:
            codes.append("RC002_INCOME_INSTABILITY")
        if dim_scores.get("debt_service_capacity", 1.0) < 0.40:
            codes.append("RC003_INSUFFICIENT_DSC")
        if dim_scores.get("document_completeness", 1.0) < 0.60:
            codes.append("RC004_INCOMPLETE_DOCUMENTATION")
        if fec.get("contradiction_flags"):
            codes.append("RC005_CONTRADICTION_DETECTED")
        if not codes:
            codes.append("RC000_ALL_DIMENSIONS_PASS")
        return codes


ALL_ADAPTERS: list[type] = [
    EvidenceRegisterAdapter,
    DocumentReconciliationAdapter,
    FeatureDerivationAdapter,
    RiskScoringAdapter,
    DecisionAssemblyAdapter,
]
