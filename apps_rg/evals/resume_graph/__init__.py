"""Modular implementation of deterministic resume-graph evaluation."""

from apps_rg.evals.resume_graph.constants import FAIL, INSUFFICIENT, PASS, UNKNOWN
from apps_rg.evals.resume_graph.metrics.calibration import (
    brier_score,
    expected_calibration_error,
    fit_isotonic_pav,
)
from apps_rg.evals.resume_graph.metrics.retrieval import (
    ndcg_at_k,
    recall_at_k,
    reciprocal_rank,
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
    "fit_isotonic_pav",
    "ndcg_at_k",
    "recall_at_k",
    "reciprocal_rank",
    "report_digest_is_valid",
]
