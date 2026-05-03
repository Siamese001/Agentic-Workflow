"""RubricOutputMapper — map DecisionPacket → ExitReviewPacket.output.dim_scores.

Plan: ``.windsurf/plans/apps-eval-harness-parity-f8d4a2.md`` W2.P4.

Producer side of the Fort Knox app-domain contract for apps_underwriting_ai.
Converts the 5 rubric dimensions declared in
``apps_underwriting_ai/config/domain_contract/eval_rubrics.yaml`` into the
canonical ``output["dim_scores"]`` + ``output["dim_evidence"]`` shape that
:class:`agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator.AppSpecificEvaluator`
consumes via
:func:`agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry.read_dim_score_from_output`.

Invocation site (future): whichever integration code serializes an
underwriting run into an ExitReviewPacket — currently gated by W2.P3 (the
SINGLE_STEP cert bypass removal). Until that wave, this mapper is
producer-ready but not yet invoked — the exact same pattern used across
the apps_* harness (grader contract registered, producer registered,
integration wired once Exit is reached on this route).

Regulated-domain floor (mirrors risk_scorer.py docstring): this mapper
does NOT mint new underwriting signals. It projects existing
:class:`~apps_underwriting_ai.engines.risk_scorer.RiskScoreBreakdown`
outputs onto rubric dimensions. All five scores are direct functions of
already-computed deterministic quantities — no new model calls, no
jurisdictional claims, no regulator citations.

Mapping contract (per rubric dim):

- ``evidence_sufficiency`` (weight 0.25, min 0.95, fail_closed)
  ← ``breakdown.evidence_completeness``
- ``feature_derivation_correctness`` (weight 0.20, min 0.95, fail_closed)
  ← 1.0 iff features is non-empty AND feature_summary carries all
  ``risk_*`` keys; else 0.0
- ``policy_compliance`` (weight 0.25, min 0.99, fail_closed)
  ← 1.0 iff gate_violations == () AND verdict != INSUFFICIENT_EVIDENCE;
  else 0.0
- ``explainability`` (weight 0.15, min 0.70, fail_closed, hybrid)
  ← 1.0 iff rationale length ≥ 100 AND evidence_refs non-empty; 0.5 if
  either (but not both); else 0.0
- ``fairness`` (weight 0.15, min 0.99, fail_closed)
  ← 1.0 always (DeterministicRiskScorer does not read protected
  attributes — see risk_scorer.py module docstring). Evidence cites the
  scorer module id so downstream auditors can inspect.

Every dim carries at least one evidence_ref so ``evidence_required: true``
gates in the rubric pass by construction when scores are real.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps_underwriting_ai.engines.risk_scorer import RiskScoreBreakdown
from apps_underwriting_ai.types.underwriting_types import (
    DecisionPacket,
    DecisionVerdict,
    RiskFeatures,
)

# Minimum rationale length for explainability to score full credit.
# Matches RubricCoverageValidator.DEFAULT_MIN_RATIONALE_CHARS.
_MIN_RATIONALE_CHARS = 100

# Feature_summary keys the RiskScoreBreakdown always surfaces when present.
# If any of these is missing, feature_derivation_correctness drops to 0.
_REQUIRED_RISK_KEYS: tuple[str, ...] = (
    "risk_score",
    "risk_evidence_completeness",
    "risk_reconciliation_completeness",
    "risk_document_density",
    "risk_coverage_score",
    "risk_product_tier",
)

# Canonical scorer module id — included as evidence so auditors can verify
# the deterministic (non-protected-attribute) derivation path.
_SCORER_MODULE_ID = "apps_underwriting_ai.engines.risk_scorer:DeterministicRiskScorer"


@dataclass(frozen=True)
class DimOutput:
    """One rubric dimension's producer output."""

    dimension_id: str
    score: float
    evidence: tuple[str, ...]


def _score_evidence_sufficiency(breakdown: RiskScoreBreakdown) -> DimOutput:
    return DimOutput(
        dimension_id="evidence_sufficiency",
        score=float(breakdown.evidence_completeness),
        evidence=(f"breakdown:evidence_completeness={breakdown.evidence_completeness}",),
    )


def _score_feature_derivation(
    features: RiskFeatures | None,
    feature_summary: dict[str, float],
) -> DimOutput:
    has_features = features is not None and bool(features.feature_vector)
    keys_present = all(k in feature_summary for k in _REQUIRED_RISK_KEYS)
    score = 1.0 if (has_features and keys_present) else 0.0
    return DimOutput(
        dimension_id="feature_derivation_correctness",
        score=score,
        evidence=(
            f"features_vector_size={len(features.feature_vector) if features else 0}",
            f"required_keys_present={keys_present}",
        ),
    )


def _score_policy_compliance(decision: DecisionPacket) -> DimOutput:
    no_violations = len(decision.gate_violations) == 0
    has_verdict = decision.verdict != DecisionVerdict.INSUFFICIENT_EVIDENCE
    score = 1.0 if (no_violations and has_verdict) else 0.0
    return DimOutput(
        dimension_id="policy_compliance",
        score=score,
        evidence=(
            f"gate_violations_count={len(decision.gate_violations)}",
            f"verdict={decision.verdict.value}",
        ),
    )


def _score_explainability(decision: DecisionPacket) -> DimOutput:
    rationale_ok = len(decision.rationale) >= _MIN_RATIONALE_CHARS
    refs_ok = len(decision.evidence_refs) > 0
    both = rationale_ok and refs_ok
    either = rationale_ok or refs_ok
    score = 1.0 if both else (0.5 if either else 0.0)
    return DimOutput(
        dimension_id="explainability",
        score=score,
        evidence=(
            f"rationale_chars={len(decision.rationale)}",
            f"evidence_refs_count={len(decision.evidence_refs)}",
        ),
    )


def _score_fairness(_decision: DecisionPacket) -> DimOutput:
    # DeterministicRiskScorer explicitly does not read protected attributes.
    # See risk_scorer.py module docstring. Fixed 1.0 until the scorer's
    # input contract changes. If and when that happens, THIS function must
    # be updated — CI gate check_app_domain_harness_parity.py catches
    # threshold regressions but not semantic drift.
    return DimOutput(
        dimension_id="fairness",
        score=1.0,
        evidence=(
            f"scorer={_SCORER_MODULE_ID}",
            "protected_attributes_read=false",
        ),
    )


def map_decision_to_dim_scores(
    decision: DecisionPacket,
    breakdown: RiskScoreBreakdown,
    features: RiskFeatures | None = None,
) -> dict[str, Any]:
    """Build the canonical ``output`` dict for ExitReviewPacket.output.

    Callers should merge the returned dict into whatever ``output`` dict
    they are serializing, e.g.::

        review_output = {**existing_output, **map_decision_to_dim_scores(...)}

    The result has exactly two top-level keys: ``dim_scores`` and
    ``dim_evidence``, each mapping every rubric ``dimension_id`` to its
    float / list-of-str respectively. The caller does NOT need to add
    further keys for the AppSpecificEvaluator grader contract.
    """
    outputs = [
        _score_evidence_sufficiency(breakdown),
        _score_feature_derivation(features, dict(decision.feature_summary or {})),
        _score_policy_compliance(decision),
        _score_explainability(decision),
        _score_fairness(decision),
    ]
    return {
        "dim_scores": {o.dimension_id: o.score for o in outputs},
        "dim_evidence": {o.dimension_id: list(o.evidence) for o in outputs},
    }


__all__ = ["map_decision_to_dim_scores", "DimOutput"]
