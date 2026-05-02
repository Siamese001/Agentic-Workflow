"""DeterministicRiskScorer \u2014 transparent, auditable underwriting verdict logic.

Replaces the placeholder ``"Real verdict logic TBD"`` stub in
:class:`DecisionPacketAssembler`. Plan:
:file:`.windsurf/plans/apps-fort-knox-parity-c5d9a3.md` W8 (OPEN-2).

================================================================================
NOT REGULATORY-GRADE \u2014 READ BEFORE USE
================================================================================
This scorer is a DETERMINISTIC, TRANSPARENT, AUDITABLE rubric with named
thresholds. It is intentionally simple. It is NOT:

  - An actuarial credit-scoring model
  - Approved for any regulated insurance / lending decision
  - Free of bias \u2014 it inherits whatever bias is in its inputs
  - A substitute for human underwriter review

It exists to give the apps_underwriting_ai package a REAL verdict path that
can be tested, audited, and extended \u2014 not to ship underwriting decisions
to production. Any consumer treating a verdict from this scorer as a
regulated underwriting decision is misusing it. The ``rationale`` field
on every output explicitly cites this module so the synthetic provenance
is loud and traceable.

Promotion to a regulated scorer would require: (1) replacement with an
actuarial model approved by the relevant jurisdiction; (2) bias / fairness
audit; (3) regulatory review; (4) ongoing monitoring. None of those are
in scope for the apps_underwriting_ai reference implementation.
================================================================================

Algorithm \u2014 deterministic and inspectable:

1. Compute an ``evidence_completeness`` score in [0, 1] from how many of
   the expected evidence kinds are registered.
2. Compute a ``reconciliation_completeness`` score in [0, 1] from
   reconciled / (reconciled + unresolved).
3. Compute a ``document_density`` score in [0, 1] from document count
   capped at ``MAX_EXPECTED_DOCUMENTS``.
4. Combine the three into a weighted ``coverage_score`` using
   ``COVERAGE_WEIGHTS``.
5. Apply ``PRODUCT_CLASS_RISK_TIER`` lookup to a base risk tier.
6. Combine ``coverage_score`` + risk tier into a final ``risk_score`` in
   [0, 100], where higher = riskier.
7. Threshold the risk_score into a verdict:

   - ``risk_score < APPROVE_CEILING``  \u2192 ``APPROVE``
   - ``APPROVE_CEILING \u2264 risk_score < REFER_CEILING`` \u2192 ``REFER``
   - ``REFER_CEILING \u2264 risk_score \u2264 100`` \u2192 ``DECLINE``
   - Insufficient inputs (no evidence + no features) \u2192 ``INSUFFICIENT_EVIDENCE``

Every threshold below is a named module constant and can be tuned without
editing scorer logic. Tests in
``tests/unit/apps_underwriting_ai/test_risk_scorer.py`` pin every branch.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from apps_underwriting_ai.types.underwriting_types import (
    DecisionVerdict,
    EvidenceRegister,
    ReconciliationResult,
    RiskFeatures,
    UnderwritingRequest,
)


# ---------------------------------------------------------------------------
# Tunable thresholds (module-level constants \u2014 inspect via REPL or tests).
# ---------------------------------------------------------------------------

#: Above this risk_score the verdict is REFER.
APPROVE_CEILING: float = 35.0

#: Above this risk_score the verdict is DECLINE.
REFER_CEILING: float = 70.0

#: Documents above this count don't increase document_density score.
MAX_EXPECTED_DOCUMENTS: int = 6

#: Expected distinct evidence kinds for a fully-evidenced application.
#: Used to compute evidence_completeness in [0, 1].
EXPECTED_EVIDENCE_KINDS: tuple[str, ...] = (
    "financial",
    "credit",
    "collateral",
    "relationship",
    "policy",
)

#: Weights for the coverage_score sub-components. Must sum to 1.0.
COVERAGE_WEIGHTS: Mapping[str, float] = {
    "evidence_completeness": 0.4,
    "reconciliation_completeness": 0.4,
    "document_density": 0.2,
}

#: Product-class risk tiers. Higher = riskier baseline. Range [0, 100].
#: Unknown product classes default to ``UNKNOWN_PRODUCT_RISK_TIER``.
PRODUCT_CLASS_RISK_TIER: Mapping[str, float] = {
    "auto": 30.0,
    "home": 25.0,
    "small_business_loan": 50.0,
    "commercial_loan": 60.0,
    "life": 35.0,
    "property": 40.0,
}

#: Used when the request's product_class is not in PRODUCT_CLASS_RISK_TIER.
UNKNOWN_PRODUCT_RISK_TIER: float = 55.0

#: Minimum evidence records required to even consider scoring.
MIN_EVIDENCE_FOR_SCORING: int = 1

#: Stable string surfaced in every rationale so consumers can detect the
#: synthetic-scorer provenance via grep.
SYNTHETIC_SCORER_TAG: str = (
    "[apps_underwriting_ai.risk_scorer/deterministic-v1; "
    "NOT regulatory-grade; see module docstring]"
)


# ---------------------------------------------------------------------------
# Score breakdown \u2014 returned alongside the verdict for full transparency.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RiskScoreBreakdown:
    """Inspectable breakdown of a risk-scoring decision.

    Every field is deterministic given the same inputs \u2014 no clocks, no
    randomness, no network. Designed to be JSON-serializable for audit
    surfaces.
    """

    risk_score: float
    verdict: DecisionVerdict
    evidence_completeness: float
    reconciliation_completeness: float
    document_density: float
    coverage_score: float
    product_class: str
    product_risk_tier: float
    rationale: str
    threshold_band: str  # "approve" | "refer" | "decline" | "insufficient"

    def to_dict(self) -> dict[str, Any]:
        """Return a stable dict shape for JSON emission."""
        return {
            "risk_score": self.risk_score,
            "verdict": self.verdict.value,
            "evidence_completeness": self.evidence_completeness,
            "reconciliation_completeness": self.reconciliation_completeness,
            "document_density": self.document_density,
            "coverage_score": self.coverage_score,
            "product_class": self.product_class,
            "product_risk_tier": self.product_risk_tier,
            "rationale": self.rationale,
            "threshold_band": self.threshold_band,
            "scorer": "apps_underwriting_ai.risk_scorer/deterministic-v1",
        }


class DeterministicRiskScorer:
    """Synthetic, transparent, auditable risk scorer. NOT regulatory-grade.

    See the module docstring for non-use guidance. This class has no
    constructor parameters because the scorer is fully driven by module
    constants \u2014 tune those, not arbitrary instance state.
    """

    # The class-vs-module-constant split is intentional: instances are
    # cheap and stateless, so callers can pass them around. Configuration
    # lives at module level so it shows up in tests + diff-review.

    def score(
        self,
        *,
        request: UnderwritingRequest,
        register: EvidenceRegister | None = None,
        features: RiskFeatures | None = None,
        reconciliation: ReconciliationResult | None = None,
    ) -> RiskScoreBreakdown:
        """Compute a deterministic risk score and verdict.

        Args:
            request: The originating UnderwritingRequest (provides product_class).
            register: Evidence register from stage 1 (or None).
            features: Risk features from stage 3 (or None).
            reconciliation: Reconciliation result from stage 2 (or None).

        Returns:
            RiskScoreBreakdown with verdict, score, and per-component breakdown.
        """
        evidence_count = len(register.records) if register else 0
        feature_count = len(features.feature_vector) if features else 0

        # Insufficient-input short circuit \u2014 do not score, do not infer.
        if evidence_count < MIN_EVIDENCE_FOR_SCORING and feature_count == 0:
            return RiskScoreBreakdown(
                risk_score=0.0,
                verdict=DecisionVerdict.INSUFFICIENT_EVIDENCE,
                evidence_completeness=0.0,
                reconciliation_completeness=0.0,
                document_density=0.0,
                coverage_score=0.0,
                product_class=request.product_class,
                product_risk_tier=0.0,
                rationale=(
                    f"INSUFFICIENT_EVIDENCE: 0 evidence records and 0 features "
                    f"derived. {SYNTHETIC_SCORER_TAG}"
                ),
                threshold_band="insufficient",
            )

        evidence_completeness = self._evidence_completeness(register)
        reconciliation_completeness = self._reconciliation_completeness(
            reconciliation
        )
        document_density = self._document_density(request)
        coverage_score = (
            COVERAGE_WEIGHTS["evidence_completeness"] * evidence_completeness
            + COVERAGE_WEIGHTS["reconciliation_completeness"]
            * reconciliation_completeness
            + COVERAGE_WEIGHTS["document_density"] * document_density
        )

        product_risk_tier = PRODUCT_CLASS_RISK_TIER.get(
            request.product_class.lower(), UNKNOWN_PRODUCT_RISK_TIER
        )

        # Risk score: high coverage REDUCES risk; low coverage AMPLIFIES the
        # product-class baseline. coverage_score \u2208 [0, 1]. Scale to [0, 100].
        risk_score = product_risk_tier * (1.0 - coverage_score) + (
            product_risk_tier * coverage_score * 0.5
        )
        # Equivalent simplification: risk_score = product_risk_tier * (1 - 0.5 * coverage_score)
        # Kept verbose above so readers can trace each contribution.

        # Bound just in case anything weird happened upstream.
        risk_score = max(0.0, min(100.0, risk_score))

        if risk_score < APPROVE_CEILING:
            verdict = DecisionVerdict.APPROVE
            band = "approve"
        elif risk_score < REFER_CEILING:
            verdict = DecisionVerdict.REFER
            band = "refer"
        else:
            verdict = DecisionVerdict.DECLINE
            band = "decline"

        rationale = (
            f"{verdict.value.upper()}: risk_score={risk_score:.2f} "
            f"(band={band}, ceiling_approve={APPROVE_CEILING}, "
            f"ceiling_refer={REFER_CEILING}). "
            f"product_class={request.product_class!r} \u2192 baseline_tier={product_risk_tier:.1f}. "
            f"coverage={coverage_score:.2f} "
            f"(evidence={evidence_completeness:.2f}, "
            f"reconciliation={reconciliation_completeness:.2f}, "
            f"documents={document_density:.2f}). "
            f"{SYNTHETIC_SCORER_TAG}"
        )

        return RiskScoreBreakdown(
            risk_score=risk_score,
            verdict=verdict,
            evidence_completeness=evidence_completeness,
            reconciliation_completeness=reconciliation_completeness,
            document_density=document_density,
            coverage_score=coverage_score,
            product_class=request.product_class,
            product_risk_tier=product_risk_tier,
            rationale=rationale,
            threshold_band=band,
        )

    # ----------------------- sub-component scorers ------------------------

    @staticmethod
    def _evidence_completeness(register: EvidenceRegister | None) -> float:
        """Fraction of EXPECTED_EVIDENCE_KINDS covered by the register."""
        if register is None or not register.records:
            return 0.0
        observed_kinds = {r.kind.lower() for r in register.records}
        expected = set(k.lower() for k in EXPECTED_EVIDENCE_KINDS)
        if not expected:
            return 1.0
        return len(observed_kinds & expected) / len(expected)

    @staticmethod
    def _reconciliation_completeness(
        reconciliation: ReconciliationResult | None,
    ) -> float:
        """reconciled / (reconciled + unresolved); 0 if both are zero."""
        if reconciliation is None:
            return 0.0
        total = reconciliation.reconciled_count + reconciliation.unresolved_count
        if total == 0:
            return 0.0
        return reconciliation.reconciled_count / total

    @staticmethod
    def _document_density(request: UnderwritingRequest) -> float:
        """Documents submitted / MAX_EXPECTED_DOCUMENTS, capped at 1.0."""
        if MAX_EXPECTED_DOCUMENTS <= 0:
            return 0.0
        return min(1.0, len(request.documents) / MAX_EXPECTED_DOCUMENTS)


__all__ = [
    "APPROVE_CEILING",
    "COVERAGE_WEIGHTS",
    "DeterministicRiskScorer",
    "EXPECTED_EVIDENCE_KINDS",
    "MAX_EXPECTED_DOCUMENTS",
    "MIN_EVIDENCE_FOR_SCORING",
    "PRODUCT_CLASS_RISK_TIER",
    "REFER_CEILING",
    "RiskScoreBreakdown",
    "SYNTHETIC_SCORER_TAG",
    "UNKNOWN_PRODUCT_RISK_TIER",
]
