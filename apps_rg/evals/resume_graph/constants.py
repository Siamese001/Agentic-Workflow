"""Stable constants for resume-graph evaluation."""

from __future__ import annotations

import re

UNKNOWN = "UNKNOWN"
INSUFFICIENT = "INSUFFICIENT_DATA"
PASS = "PASS"
FAIL = "FAIL"

_ROW_SCHEMA = "apps_rg.resume_graph_evaluation_row.v1"
_ADJUDICATED_EXPORT_SCHEMA = "apps_rg.c03_human_eval.adjudicated_evaluation.v1"
_ADJUDICATED_EXPORT_RECEIPT_SCHEMA = "apps_rg.c03_human_eval.adjudicated_export_receipt.v1"
_REPORT_SCHEMA = "apps_rg.resume_graph_w6_evaluation.v1"
_CI_RECEIPT_SCHEMA = "apps_rg.resume_graph_w6_ci_receipt.v1"
_SHA256_RE = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")
_ARTIFACT_SHA256_REF_RE = re.compile(r"^artifact://[^#]+#sha256:[0-9a-f]{64}$")

_METRIC_NAMES = (
    "pooled_recall_at_1",
    "pooled_recall_at_3",
    "pooled_recall_at_5",
    "pooled_recall_at_10",
    "recall_at_1",
    "recall_at_3",
    "recall_at_5",
    "recall_at_10",
    "ndcg_at_1",
    "ndcg_at_3",
    "ndcg_at_5",
    "ndcg_at_10",
    "recall_at_k",
    "ndcg_at_k",
    "mrr",
    "authority_eligibility_accuracy",
    "exact_path_accuracy",
    "claim_entailment_accuracy",
    "claim_entailment_mean_grade",
    "claim_entailment_prediction_accuracy",
    "claim_entailment_precision",
    "claim_entailment_recall",
    "claim_entailment_predicted_positive_rate",
    "claim_entailment_labeled_positive_rate",
    "metric_binding_accuracy",
    "metric_binding_prediction_accuracy",
    "metric_binding_precision",
    "metric_binding_recall",
    "metric_binding_predicted_positive_rate",
    "metric_binding_labeled_positive_rate",
    "target_relevance_mean_grade",
    "proof_confidence_candidate_precision",
    "proof_confidence_candidate_recall",
    "proof_confidence_candidate_support_count",
    "proof_confidence_candidate_minimum",
    "selection_margin_mean",
    "selection_margin_minimum",
    "ece",
    "brier",
)

_RELEASE_TARGETS = {
    "recall_at_k_minimum": ("recall_at_k", "minimum"),
    "ndcg_at_k_minimum": ("ndcg_at_k", "minimum"),
    "mrr_minimum": ("mrr", "minimum"),
    "authority_eligibility_accuracy_minimum": (
        "authority_eligibility_accuracy",
        "minimum",
    ),
    "exact_path_accuracy_minimum": ("exact_path_accuracy", "minimum"),
    "claim_entailment_accuracy_minimum": (
        "claim_entailment_accuracy",
        "minimum",
    ),
    "metric_binding_accuracy_minimum": ("metric_binding_accuracy", "minimum"),
    "ece_maximum": ("ece", "maximum"),
    "brier_maximum": ("brier", "maximum"),
    "proof_confidence_candidate_precision_minimum": (
        "proof_confidence_candidate_precision",
        "minimum",
    ),
    "proof_confidence_candidate_floor_minimum": (
        "proof_confidence_candidate_minimum",
        "minimum",
    ),
    "proof_confidence_candidate_support_minimum": (
        "proof_confidence_candidate_support_count",
        "minimum",
    ),
}
