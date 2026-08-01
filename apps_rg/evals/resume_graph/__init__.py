"""Modular implementation of deterministic resume-graph evaluation."""

from apps_rg.evals.resume_graph.constants import FAIL, INSUFFICIENT, PASS, UNKNOWN
from apps_rg.evals.resume_graph.metrics.calibration import (
    brier_score,
    expected_calibration_error,
    fit_isotonic_pav,
)
from apps_rg.evals.resume_graph.metrics.grounding import (
    evaluate_binding_gate,
    evaluate_claim_evidence,
    evaluate_grounding_gate,
    seal_claim_evidence_record,
)
from apps_rg.evals.resume_graph.metrics.retrieval import (
    evaluate_retrieval_gate,
    evaluate_retrieval_query,
    ndcg_at_k,
    recall_at_k,
    reciprocal_rank,
    seal_retrieval_query,
)
from apps_rg.evals.resume_graph.models import EvaluationDataError, IsotonicModel
from apps_rg.evals.resume_graph.reporting import (
    canonical_digest,
    compute_row_content_digest,
    report_digest_is_valid,
)

__all__ = [
    "FAIL",
    "INSUFFICIENT",
    "PASS",
    "UNKNOWN",
    "EvaluationDataError",
    "IsotonicModel",
    "brier_score",
    "canonical_digest",
    "compute_row_content_digest",
    "expected_calibration_error",
    "evaluate_binding_gate",
    "evaluate_claim_evidence",
    "evaluate_grounding_gate",
    "evaluate_retrieval_gate",
    "evaluate_retrieval_query",
    "fit_isotonic_pav",
    "ndcg_at_k",
    "recall_at_k",
    "reciprocal_rank",
    "report_digest_is_valid",
    "seal_claim_evidence_record",
    "seal_retrieval_query",
]
