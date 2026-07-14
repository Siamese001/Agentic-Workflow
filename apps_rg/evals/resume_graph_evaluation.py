"""Deterministic, fail-closed evaluation for the apps_rg resume graph.

The evaluator deliberately keeps calibration offline.  It fits a proof-score
mapping on the human-labelled calibration split, applies it only to the
holdout split, and never mutates a runtime threshold.  Missing or invalid
human evidence produces an UNKNOWN/INSUFFICIENT report with null metrics.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from apps_rg.evals.c03_human_eval._io import (
    controlled_path_error,
    digest_matches,
    private_path_error,
    repo_root_from_module,
    stable_digest,
)
from apps_rg.evals.c03_human_eval.export import COMPLETED_LABEL_FILES
from apps_rg.evals.c03_human_eval.packet import MANIFEST_SCHEMA
from apps_rg.evals.c03_human_eval.split_policy import (
    PROOF_SPLIT_POLICY_ID,
    ProofSplitPolicyError,
    proof_split_for_digest,
)
from apps_rg.evals.c03_human_eval.validation import validate_completed_packet


UNKNOWN = "UNKNOWN"
INSUFFICIENT = "INSUFFICIENT_DATA"
PASS = "PASS"
FAIL = "FAIL"

_ROW_SCHEMA = "apps_rg.resume_graph_evaluation_row.v1"
_ADJUDICATED_EXPORT_SCHEMA = "apps_rg.c03_human_eval.adjudicated_evaluation.v1"
_ADJUDICATED_EXPORT_RECEIPT_SCHEMA = (
    "apps_rg.c03_human_eval.adjudicated_export_receipt.v1"
)
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


class EvaluationDataError(ValueError):
    """Raised when evidence cannot support a valid evaluation."""


def canonical_digest(value: Any) -> str:
    """Return a deterministic SHA-256 digest for a JSON-compatible value."""

    payload = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def compute_row_content_digest(row: Mapping[str, Any]) -> str:
    """Digest a labelled row, excluding only its self-referential digest."""

    return canonical_digest({key: value for key, value in row.items() if key != "content_digest"})


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _mean(values: Sequence[float]) -> float:
    if not values:
        raise EvaluationDataError("cannot calculate a mean from no observations")
    return sum(values) / len(values)


def recall_at_k(
    ranked_ids: Sequence[str],
    relevance: Mapping[str, float],
    k: int,
    *,
    positive_floor: float = 1.0,
) -> float:
    """Calculate Recall@K using all labelled relevant candidates as recall base."""

    if k <= 0:
        raise EvaluationDataError("k must be positive")
    relevant = {candidate_id for candidate_id, score in relevance.items() if score >= positive_floor}
    if not relevant:
        raise EvaluationDataError("Recall@K is undefined without a relevant candidate")
    return len(relevant.intersection(ranked_ids[:k])) / len(relevant)


def ndcg_at_k(
    ranked_ids: Sequence[str],
    relevance: Mapping[str, float],
    k: int,
    *,
    ranks: Sequence[int] | None = None,
) -> float:
    """Calculate nDCG@K with exponential gain and true explicit-rank discount."""

    if k <= 0:
        raise EvaluationDataError("k must be positive")

    explicit_ranks = tuple(ranks) if ranks is not None else tuple(range(1, len(ranked_ids) + 1))
    if len(explicit_ranks) != len(ranked_ids) or any(
        not isinstance(rank, int) or isinstance(rank, bool) or rank <= 0
        for rank in explicit_ranks
    ):
        raise EvaluationDataError("explicit ranks must be positive integers aligned to candidates")

    def discounted_gain(scores: Iterable[tuple[int, float]]) -> float:
        return sum(
            (2.0 ** float(score) - 1.0) / math.log2(rank + 1.0)
            for rank, score in scores
        )

    actual = [
        (rank, float(relevance.get(candidate_id, 0.0)))
        for candidate_id, rank in zip(ranked_ids, explicit_ranks)
        if rank <= k
    ]
    ideal = enumerate(
        sorted((float(score) for score in relevance.values()), reverse=True)[:k],
        1,
    )
    ideal_gain = discounted_gain(ideal)
    if ideal_gain <= 0.0:
        raise EvaluationDataError("nDCG@K is undefined without positive relevance gain")
    return discounted_gain(actual) / ideal_gain


def reciprocal_rank(
    ranked_ids: Sequence[str],
    relevance: Mapping[str, float],
    *,
    positive_floor: float = 1.0,
    ranks: Sequence[int] | None = None,
) -> float:
    """Calculate reciprocal rank of the first labelled relevant candidate."""

    explicit_ranks = tuple(ranks) if ranks is not None else tuple(range(1, len(ranked_ids) + 1))
    if len(explicit_ranks) != len(ranked_ids) or any(
        not isinstance(rank, int) or isinstance(rank, bool) or rank <= 0
        for rank in explicit_ranks
    ):
        raise EvaluationDataError("explicit ranks must be positive integers aligned to candidates")
    for rank, candidate_id in zip(explicit_ranks, ranked_ids):
        if float(relevance.get(candidate_id, 0.0)) >= positive_floor:
            return 1.0 / rank
    return 0.0


def expected_calibration_error(
    probabilities: Sequence[float], labels: Sequence[bool], *, n_bins: int = 10
) -> float:
    """Calculate equal-width binary expected calibration error."""

    _validate_binary_inputs(probabilities, labels)
    if n_bins <= 0:
        raise EvaluationDataError("n_bins must be positive")
    count = len(probabilities)
    error = 0.0
    for bin_index in range(n_bins):
        lower = bin_index / n_bins
        upper = (bin_index + 1) / n_bins
        indices = [
            index
            for index, probability in enumerate(probabilities)
            if probability >= lower
            and (probability < upper or (bin_index == n_bins - 1 and probability <= 1.0))
        ]
        if not indices:
            continue
        confidence = _mean([float(probabilities[index]) for index in indices])
        accuracy = _mean([float(labels[index]) for index in indices])
        error += (len(indices) / count) * abs(accuracy - confidence)
    return error


def brier_score(probabilities: Sequence[float], labels: Sequence[bool]) -> float:
    """Calculate mean squared probability error for binary proof labels."""

    _validate_binary_inputs(probabilities, labels)
    return _mean(
        [(float(probability) - float(label)) ** 2 for probability, label in zip(probabilities, labels)]
    )


def _validate_binary_inputs(probabilities: Sequence[float], labels: Sequence[bool]) -> None:
    if not probabilities or len(probabilities) != len(labels):
        raise EvaluationDataError("probabilities and labels must be nonempty and equally sized")
    if any(not _is_number(probability) or not 0.0 <= float(probability) <= 1.0 for probability in probabilities):
        raise EvaluationDataError("probabilities must be finite values in [0, 1]")
    if any(type(label) is not bool for label in labels):
        raise EvaluationDataError("labels must be booleans")


def _validate_fit_inputs(scores: Sequence[float], labels: Sequence[bool]) -> None:
    if not scores or len(scores) != len(labels):
        raise EvaluationDataError("proof scores and labels must be nonempty and equally sized")
    if any(not _is_number(score) for score in scores):
        raise EvaluationDataError("raw proof scores must be finite numeric values")
    if any(type(label) is not bool for label in labels):
        raise EvaluationDataError("labels must be booleans")


@dataclass(frozen=True)
class IsotonicModel:
    """A deterministic piecewise-linear representation of a PAV fit."""

    x_values: tuple[float, ...]
    y_values: tuple[float, ...]

    def predict_one(self, score: float) -> float:
        if not _is_number(score):
            raise EvaluationDataError("proof score must be finite")
        value = float(score)
        if value <= self.x_values[0]:
            return self.y_values[0]
        if value >= self.x_values[-1]:
            return self.y_values[-1]
        for index in range(1, len(self.x_values)):
            right_x = self.x_values[index]
            if value <= right_x:
                left_x = self.x_values[index - 1]
                left_y = self.y_values[index - 1]
                right_y = self.y_values[index]
                portion = (value - left_x) / (right_x - left_x)
                return left_y + portion * (right_y - left_y)
        raise AssertionError("unreachable isotonic interpolation state")

    def predict(self, scores: Sequence[float]) -> tuple[float, ...]:
        return tuple(self.predict_one(score) for score in scores)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "method": "deterministic_isotonic_pav_v1",
            "x_values": list(self.x_values),
            "y_values": list(self.y_values),
        }


def fit_isotonic_pav(scores: Sequence[float], labels: Sequence[bool]) -> IsotonicModel:
    """Fit deterministic binary isotonic regression with pool-adjacent violators."""

    _validate_fit_inputs(scores, labels)
    if len(set(labels)) < 2:
        raise EvaluationDataError("isotonic calibration requires both proof-label classes")

    grouped: dict[float, list[bool]] = {}
    for score, label in zip(scores, labels):
        grouped.setdefault(float(score), []).append(label)
    if len(grouped) < 2:
        raise EvaluationDataError("isotonic calibration requires two distinct proof scores")

    blocks: list[dict[str, Any]] = []
    for score in sorted(grouped):
        group_labels = grouped[score]
        blocks.append(
            {
                "scores": [score],
                "weight": len(group_labels),
                "positive": sum(group_labels),
            }
        )
        while len(blocks) >= 2:
            left = blocks[-2]
            right = blocks[-1]
            left_mean = left["positive"] / left["weight"]
            right_mean = right["positive"] / right["weight"]
            if left_mean <= right_mean:
                break
            blocks[-2:] = [
                {
                    "scores": left["scores"] + right["scores"],
                    "weight": left["weight"] + right["weight"],
                    "positive": left["positive"] + right["positive"],
                }
            ]

    fitted: dict[float, float] = {}
    for block in blocks:
        probability = block["positive"] / block["weight"]
        for score in block["scores"]:
            fitted[score] = probability
    x_values = tuple(sorted(fitted))
    return IsotonicModel(x_values=x_values, y_values=tuple(fitted[x] for x in x_values))


def _empty_metrics() -> dict[str, None]:
    return {name: None for name in _METRIC_NAMES}


def _profile_digest(profile: Mapping[str, Any]) -> str:
    return canonical_digest(profile)


def _base_report(
    profile: Mapping[str, Any],
    *,
    status: str,
    reasons: Sequence[str],
    source_ref: str,
    dataset_digest: str | None = None,
    sample_count: int = 0,
    calibration_count: int = 0,
    holdout_count: int = 0,
) -> dict[str, Any]:
    dataset_profile = _mapping(profile, "dataset")
    calibration_profile = _mapping(profile, "calibration")
    retrieval_profile = _mapping(profile, "retrieval")
    output_profile = _mapping(profile, "output")
    report: dict[str, Any] = {
        "schema_version": str(output_profile.get("artifact_schema_version", _REPORT_SCHEMA)),
        "evaluation_id": str(profile.get("profile_id", "")),
        "profile_digest": _profile_digest(profile),
        "policy_version": str(profile.get("policy_version", "")),
        "policy_activation_status": str(calibration_profile.get("activation_status", "UNPROMOTED")),
        "status": status,
        "evaluation_mode": "ADVISORY_INTERNAL",
        "official_evidence_chain_validated": False,
        "evidence_chain": {
            "export_receipt_sha256": None,
            "prelabel_packet_manifest_sha256": None,
            "human_review_authority_receipt_sha256": None,
            "packet_manifest_sha256": None,
            "packet_manifest_digest": None,
            "completed_validation_digest": None,
        },
        "unknown_is_pass": False,
        "evaluation_gate_pass": False,
        "promotion_eligible": False,
        "reasons": list(reasons),
        "dataset": {
            "dataset_id": str(dataset_profile.get("dataset_id", "")),
            "dataset_version": str(dataset_profile.get("dataset_version", "")),
            "source_ref": source_ref,
            "digest": dataset_digest,
            "sample_count": sample_count,
            "calibration_count": calibration_count,
            "holdout_count": holdout_count,
        },
        "coverage": {
            "target_profiles": [],
            "sections": [],
            "proof_target_profiles_by_split": {},
            "proof_sections_by_split": {},
            "retrieval_target_profiles_by_split": {},
            "retrieval_sections_by_split": {},
            "metric_binding_holdout_count": 0,
            "authority_eligible_proof_holdout_identity_count": 0,
            "proof_calibration_row_count": 0,
            "proof_calibration_identity_count": 0,
            "proof_holdout_row_count": 0,
            "proof_holdout_identity_count": 0,
            "proof_holdout_context_count": 0,
            "proof_total_split_group_count": 0,
            "proof_calibration_split_group_count": 0,
            "proof_holdout_split_group_count": 0,
            "retrieval_total_count": 0,
            "retrieval_calibration_count": 0,
            "retrieval_holdout_count": 0,
        },
        "retrieval_contract": {
            "k_values": list(retrieval_profile.get("k_values", (1, 3, 5, 10))),
            "gate_k": int(
                retrieval_profile.get("gate_k", retrieval_profile.get("primary_k", 10))
            ),
            "relevance_positive_floor": float(
                retrieval_profile.get("relevance_positive_floor", 2.0)
            ),
            "recall_definition": str(retrieval_profile.get("recall_definition", "")),
            "frontier_k": int(retrieval_profile.get("frontier_k", 10)),
            "maximum_selected_audit_extras": int(
                retrieval_profile.get("maximum_selected_audit_extras", 1)
            ),
            "allocator_candidate_budget": int(
                retrieval_profile.get("allocator_candidate_budget", 64)
            ),
            "release_aliases": {
                "recall_at_k": f"pooled_recall_at_{int(retrieval_profile.get('gate_k', 10))}",
                "ndcg_at_k": f"ndcg_at_{int(retrieval_profile.get('gate_k', 10))}",
            },
        },
        "target_relevance_summary": {
            "authoritative": False,
            "mean_grade": None,
            "grade_distribution": {},
        },
        "future_release_candidate_summary": {
            "scope": "canonical_visible_unique_proof_identities_at_or_above_candidate_threshold",
            "precision": None,
            "recall": None,
            "support_count": None,
            "minimum_calibrated_confidence": None,
            "activation_status": "UNPROMOTED",
        },
        "metrics": _empty_metrics(),
        "calibration": {
            "method": str(calibration_profile.get("method", "")),
            "status": "NOT_RUN",
            "fit_split": "proof_split:calibration",
            "apply_split": "proof_split:holdout",
            "fit_sample_count": 0,
            "fit_row_count": 0,
            "holdout_sample_count": 0,
            "holdout_row_count": 0,
            "model": None,
            "candidate_threshold": None,
            "active_threshold": calibration_profile.get("active_threshold"),
        },
        "gate_results": {},
        "per_sample_results": [],
        "retrieval_sample_results": [],
        "current_run_mutated": False,
        "future_run_only": True,
        "target_alignment_authoritative": False,
        "promotion_blockers": [
            "candidate policy is UNPROMOTED",
            "active proof-confidence threshold is unset",
            "human approval is required before a future-run-only activation",
        ],
    }
    report["deterministic_digest"] = _report_digest(report)
    return report


def _report_digest(report: Mapping[str, Any]) -> str:
    return canonical_digest({key: value for key, value in report.items() if key != "deterministic_digest"})


def report_digest_is_valid(report: Mapping[str, Any]) -> bool:
    digest = report.get("deterministic_digest")
    try:
        return isinstance(digest, str) and digest == _report_digest(report)
    except (TypeError, ValueError):
        return False


def build_sanitized_ci_receipt(
    report: Mapping[str, Any], *, protected_full_report_sha256: str
) -> dict[str, Any]:
    """Emit the aggregate-only receipt allowed to cross the controlled boundary."""

    if not report_digest_is_valid(report):
        raise EvaluationDataError("protected full report digest is invalid")
    if not re.fullmatch(r"[0-9a-f]{64}", protected_full_report_sha256):
        raise EvaluationDataError("protected full report SHA-256 is invalid")
    dataset = report.get("dataset")
    dataset = dataset if isinstance(dataset, Mapping) else {}
    calibration = report.get("calibration")
    calibration = calibration if isinstance(calibration, Mapping) else {}
    coverage = report.get("coverage")
    coverage = coverage if isinstance(coverage, Mapping) else {}
    reason_codes = sorted(
        {
            re.sub(r"[^A-Z0-9_]+", "_", str(reason).split(":", 1)[0].split(";", 1)[0].upper())
            .strip("_")[:96]
            for reason in report.get("reasons") or []
            if str(reason).strip()
        }
    )
    receipt: dict[str, Any] = {
        "schema_version": _CI_RECEIPT_SCHEMA,
        "evaluation_id": report.get("evaluation_id"),
        "profile_digest": report.get("profile_digest"),
        "policy_version": report.get("policy_version"),
        "policy_activation_status": report.get("policy_activation_status"),
        "status": report.get("status"),
        "evaluation_mode": report.get("evaluation_mode"),
        "official_evidence_chain_validated": report.get(
            "official_evidence_chain_validated"
        ),
        "unknown_is_pass": report.get("unknown_is_pass"),
        "evaluation_gate_pass": report.get("evaluation_gate_pass"),
        "promotion_eligible": report.get("promotion_eligible"),
        "current_run_mutated": report.get("current_run_mutated"),
        "future_run_only": report.get("future_run_only"),
        "target_alignment_authoritative": report.get(
            "target_alignment_authoritative"
        ),
        "reason_codes": reason_codes,
        "reason_count": len(report.get("reasons") or []),
        "dataset_summary": {
            "dataset_id": dataset.get("dataset_id"),
            "dataset_version": dataset.get("dataset_version"),
            "digest": dataset.get("digest"),
            "sample_count": dataset.get("sample_count"),
            "calibration_count": dataset.get("calibration_count"),
            "holdout_count": dataset.get("holdout_count"),
            "proof_total_split_group_count": coverage.get(
                "proof_total_split_group_count"
            ),
            "proof_calibration_split_group_count": coverage.get(
                "proof_calibration_split_group_count"
            ),
            "proof_holdout_split_group_count": coverage.get(
                "proof_holdout_split_group_count"
            ),
            "retrieval_total_count": coverage.get("retrieval_total_count"),
            "retrieval_calibration_count": coverage.get(
                "retrieval_calibration_count"
            ),
            "retrieval_holdout_count": coverage.get("retrieval_holdout_count"),
            "metric_binding_holdout_count": coverage.get(
                "metric_binding_holdout_count"
            ),
        },
        "calibration_summary": {
            "method": calibration.get("method"),
            "status": calibration.get("status"),
            "fit_split": calibration.get("fit_split"),
            "apply_split": calibration.get("apply_split"),
            "fit_sample_count": calibration.get("fit_sample_count"),
            "fit_row_count": calibration.get("fit_row_count"),
            "holdout_sample_count": calibration.get("holdout_sample_count"),
            "holdout_row_count": calibration.get("holdout_row_count"),
            "active_threshold": calibration.get("active_threshold"),
        },
        "metrics": dict(report.get("metrics") or {}),
        "gate_results": dict(report.get("gate_results") or {}),
        "evidence_chain": dict(report.get("evidence_chain") or {}),
        "protected_full_report_sha256": protected_full_report_sha256,
        "protected_full_report_deterministic_digest": report.get(
            "deterministic_digest"
        ),
    }
    receipt["record_digest"] = canonical_digest(receipt)
    return receipt


def _mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    nested = value.get(key)
    if not isinstance(nested, Mapping):
        raise EvaluationDataError(f"profile field {key!r} must be a mapping")
    return nested


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvaluationDataError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise EvaluationDataError(f"{path}:{line_number}: row must be an object")
        rows.append(row)
    return rows


def _secure_private_file_bytes(path: Path) -> bytes:
    """Read one controlled file without following a final-component symlink."""

    candidate = Path(path)
    if candidate.is_symlink():
        raise EvaluationDataError(f"{candidate}: must not be a symlink")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(candidate, flags)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise EvaluationDataError(f"{candidate}: must be a regular file")
        if metadata.st_uid != os.getuid():
            raise EvaluationDataError(
                f"{candidate}: must be owned by the current user"
            )
        if metadata.st_nlink != 1:
            raise EvaluationDataError(f"{candidate}: must not be a hardlink alias")
        if stat.S_IMODE(metadata.st_mode) & 0o077:
            raise EvaluationDataError(f"{candidate}: must be owner-only (0600)")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _load_jsonl_bytes(payload: bytes, *, source: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvaluationDataError(f"{source}: invalid UTF-8: {exc}") from exc
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvaluationDataError(
                f"{source}:{line_number}: invalid JSON: {exc}"
            ) from exc
        if not isinstance(row, dict):
            raise EvaluationDataError(f"{source}:{line_number}: row must be an object")
        rows.append(row)
    return rows


def _mark_official_evidence(
    report: dict[str, Any],
    *,
    validated: bool,
    evidence_chain: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Bind an evaluation report to the externally trusted evidence decision."""

    report["evaluation_mode"] = "OFFICIAL"
    report["official_evidence_chain_validated"] = validated
    if evidence_chain is not None:
        report["evidence_chain"] = dict(evidence_chain)
    report["deterministic_digest"] = _report_digest(report)
    return report


def _official_evidence_chain(
    *,
    dataset_path: Path,
    dataset_sha256: str,
    rows: Sequence[Mapping[str, Any]],
    profile: Mapping[str, Any],
    export_receipt_path: Path | None,
    trusted_export_receipt_sha256: str | None,
    trusted_prelabel_packet_manifest_sha256: str | None,
    human_review_authority_receipt_path: Path | None,
    trusted_human_review_authority_receipt_sha256: str | None,
    packet_dir: Path | None,
    labels_dir: Path | None,
) -> tuple[list[str], dict[str, Any]]:
    """Validate the protected trust root and its packet-to-dataset chain.

    The receipt digest is intentionally supplied out of band.  A JSONL file or
    a self-authored receipt cannot make itself official merely by recomputing
    unkeyed hashes.
    """

    evidence = {
        "export_receipt_sha256": None,
        "prelabel_packet_manifest_sha256": None,
        "human_review_authority_receipt_sha256": None,
        "packet_manifest_sha256": None,
        "packet_manifest_digest": None,
        "completed_validation_digest": None,
    }
    missing = []
    if export_receipt_path is None:
        missing.append("EXPORT_RECEIPT_PATH")
    if trusted_export_receipt_sha256 is None:
        missing.append("TRUSTED_EXPORT_RECEIPT_SHA256")
    if trusted_prelabel_packet_manifest_sha256 is None:
        missing.append("TRUSTED_PRELABEL_PACKET_MANIFEST_SHA256")
    if human_review_authority_receipt_path is None:
        missing.append("HUMAN_REVIEW_AUTHORITY_RECEIPT_PATH")
    if trusted_human_review_authority_receipt_sha256 is None:
        missing.append("TRUSTED_HUMAN_REVIEW_AUTHORITY_RECEIPT_SHA256")
    if packet_dir is None:
        missing.append("PACKET_DIR")
    if labels_dir is None:
        missing.append("LABELS_DIR")
    if missing:
        return ["OFFICIAL_EVIDENCE_CHAIN_REQUIRED:" + ",".join(missing)], evidence

    assert export_receipt_path is not None
    assert trusted_export_receipt_sha256 is not None
    assert trusted_prelabel_packet_manifest_sha256 is not None
    assert human_review_authority_receipt_path is not None
    assert trusted_human_review_authority_receipt_sha256 is not None
    assert packet_dir is not None
    assert labels_dir is not None
    receipt_path = Path(export_receipt_path)
    packet_root = Path(packet_dir)
    labels_root = Path(labels_dir)
    authority_receipt_path = Path(human_review_authority_receipt_path)
    trusted_digest = trusted_export_receipt_sha256.removeprefix("sha256:")
    trusted_prelabel_digest = trusted_prelabel_packet_manifest_sha256.removeprefix(
        "sha256:"
    )
    trusted_authority_digest = (
        trusted_human_review_authority_receipt_sha256.removeprefix("sha256:")
    )
    errors: list[str] = []
    for label, path, directory in (
        ("DATASET", dataset_path, False),
        ("TRUSTED_EXPORT_RECEIPT", export_receipt_path, False),
        ("HUMAN_REVIEW_AUTHORITY_RECEIPT", authority_receipt_path, False),
        ("PACKET_ROOT", packet_dir, True),
        ("LABELS_ROOT", labels_dir, True),
    ):
        boundary_error = controlled_path_error(
            Path(path), repo_root=repo_root_from_module()
        )
        if boundary_error is not None:
            errors.append(f"{label}_CONTROL_BOUNDARY_INVALID:{boundary_error}")
            continue
        privacy_error = private_path_error(path, directory=directory)
        if privacy_error is not None:
            errors.append(f"{label}_PRIVACY_INVALID:{privacy_error}")
            continue
        if directory:
            try:
                members = sorted(
                    Path(path).rglob("*"), key=lambda candidate: str(candidate)
                )
            except OSError as exc:
                errors.append(f"{label}_CONTROL_BOUNDARY_UNREADABLE:{exc}")
                continue
            for member in members:
                member_error = controlled_path_error(
                    member, repo_root=repo_root_from_module()
                )
                if member_error is not None:
                    errors.append(
                        f"{label}_MEMBER_CONTROL_BOUNDARY_INVALID:"
                        f"{member_error}:{member.relative_to(Path(path))}"
                    )
    if errors:
        return sorted(set(errors)), evidence
    if not re.fullmatch(r"[0-9a-f]{64}", trusted_digest):
        errors.append("TRUSTED_EXPORT_RECEIPT_SHA256_INVALID")
    if not re.fullmatch(r"[0-9a-f]{64}", trusted_prelabel_digest):
        errors.append("TRUSTED_PRELABEL_PACKET_MANIFEST_SHA256_INVALID")
    if not re.fullmatch(r"[0-9a-f]{64}", trusted_authority_digest):
        errors.append("TRUSTED_HUMAN_REVIEW_AUTHORITY_RECEIPT_SHA256_INVALID")

    try:
        receipt_bytes = _secure_private_file_bytes(receipt_path)
        observed_receipt_sha = hashlib.sha256(receipt_bytes).hexdigest()
        receipt = json.loads(receipt_bytes)
    except (OSError, ValueError, TypeError, EvaluationDataError) as exc:
        return [f"TRUSTED_EXPORT_RECEIPT_UNREADABLE:{exc}"], evidence
    evidence["export_receipt_sha256"] = observed_receipt_sha
    if observed_receipt_sha != trusted_digest:
        errors.append("TRUSTED_EXPORT_RECEIPT_SHA256_MISMATCH")
    try:
        authority_receipt_bytes = _secure_private_file_bytes(authority_receipt_path)
        observed_authority_sha = hashlib.sha256(authority_receipt_bytes).hexdigest()
    except (OSError, EvaluationDataError) as exc:
        return errors + [f"HUMAN_REVIEW_AUTHORITY_RECEIPT_UNREADABLE:{exc}"], evidence
    if observed_authority_sha != trusted_authority_digest:
        errors.append("HUMAN_REVIEW_AUTHORITY_RECEIPT_SHA256_MISMATCH")
    else:
        evidence["human_review_authority_receipt_sha256"] = observed_authority_sha
    if not isinstance(receipt, Mapping):
        return errors + ["TRUSTED_EXPORT_RECEIPT_NOT_OBJECT"], evidence
    if receipt.get("schema_version") != _ADJUDICATED_EXPORT_RECEIPT_SCHEMA:
        errors.append("TRUSTED_EXPORT_RECEIPT_SCHEMA_INVALID")
    if (
        receipt.get("status") != PASS
        or receipt.get("official_pass") is not True
        or receipt.get("unknown_is_pass") is not False
    ):
        errors.append("TRUSTED_EXPORT_RECEIPT_NONPASS")
    if not digest_matches(receipt, "record_digest"):
        errors.append("TRUSTED_EXPORT_RECEIPT_RECORD_DIGEST_MISMATCH")

    if receipt.get("output_sha256") != dataset_sha256:
        errors.append("EXPORT_RECEIPT_DATASET_SHA256_MISMATCH")
    if receipt.get("row_count") != len(rows):
        errors.append("EXPORT_RECEIPT_ROW_COUNT_MISMATCH")
    dataset_profile = _mapping(profile, "dataset")
    if receipt.get("dataset_id") != dataset_profile.get("dataset_id"):
        errors.append("EXPORT_RECEIPT_DATASET_ID_MISMATCH")
    if receipt.get("dataset_version") != dataset_profile.get("dataset_version"):
        errors.append("EXPORT_RECEIPT_DATASET_VERSION_MISMATCH")

    manifest_path = packet_root / "packet_manifest.json"
    checksum_path = packet_root / "SHA256SUMS"
    try:
        manifest_bytes = _secure_private_file_bytes(manifest_path)
        checksum_bytes = _secure_private_file_bytes(checksum_path)
        manifest = json.loads(manifest_bytes)
        manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
        checksum_sha = hashlib.sha256(checksum_bytes).hexdigest()
    except (OSError, ValueError, TypeError, EvaluationDataError) as exc:
        return errors + [f"PACKET_EVIDENCE_UNREADABLE:{exc}"], evidence
    evidence["packet_manifest_sha256"] = manifest_sha
    if manifest_sha != trusted_prelabel_digest:
        errors.append("TRUSTED_PRELABEL_PACKET_MANIFEST_SHA256_MISMATCH")
    else:
        evidence["prelabel_packet_manifest_sha256"] = trusted_prelabel_digest
    if not isinstance(manifest, Mapping):
        return errors + ["PACKET_MANIFEST_NOT_OBJECT"], evidence
    evidence["packet_manifest_digest"] = manifest.get("manifest_digest")
    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        errors.append("PACKET_MANIFEST_SCHEMA_INVALID")
    if not digest_matches(manifest, "manifest_digest"):
        errors.append("PACKET_MANIFEST_RECORD_DIGEST_MISMATCH")
    if receipt.get("packet_manifest_sha256") != manifest_sha:
        errors.append("EXPORT_RECEIPT_PACKET_MANIFEST_SHA256_MISMATCH")
    if receipt.get("prelabel_packet_manifest_sha256") != trusted_prelabel_digest:
        errors.append("EXPORT_RECEIPT_PRELABEL_PACKET_MANIFEST_SHA256_MISMATCH")
    if (
        receipt.get("human_review_authority_receipt_sha256")
        != trusted_authority_digest
    ):
        errors.append("EXPORT_RECEIPT_HUMAN_REVIEW_AUTHORITY_SHA256_MISMATCH")
    if any(
        row.get("prelabel_packet_manifest_sha256") != trusted_prelabel_digest
        for row in rows
    ):
        errors.append("DATASET_PRELABEL_PACKET_MANIFEST_SHA256_MISMATCH")
    if any(
        row.get("human_review_authority_receipt_sha256")
        != trusted_authority_digest
        for row in rows
    ):
        errors.append("DATASET_HUMAN_REVIEW_AUTHORITY_SHA256_MISMATCH")
    if receipt.get("packet_manifest_digest") != manifest.get("manifest_digest"):
        errors.append("EXPORT_RECEIPT_PACKET_MANIFEST_DIGEST_MISMATCH")
    if receipt.get("packet_top_level_sha256s_sha256") != checksum_sha:
        errors.append("EXPORT_RECEIPT_PACKET_SHA256SUMS_MISMATCH")
    for field in ("packet_id", "dataset_id", "dataset_version"):
        if receipt.get(field) != manifest.get(field):
            errors.append(f"EXPORT_RECEIPT_{field.upper()}_MISMATCH")
    source_freeze_receipt_digest = receipt.get("source_freeze_receipt_digest")
    if (
        not isinstance(source_freeze_receipt_digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", source_freeze_receipt_digest)
        or source_freeze_receipt_digest
        != manifest.get("source_freeze_receipt_digest")
    ):
        errors.append("EXPORT_RECEIPT_SOURCE_FREEZE_DIGEST_MISMATCH")

    receipt_requires_w9 = receipt.get("require_w9")
    if type(receipt_requires_w9) is not bool:
        errors.append("EXPORT_RECEIPT_REQUIRE_W9_INVALID")
        receipt_requires_w9 = False
    try:
        completed_validation = validate_completed_packet(
            packet_root,
            labels_root,
            require_w9=receipt_requires_w9,
            trusted_source_freeze_receipt_digest=(
                source_freeze_receipt_digest
                if isinstance(source_freeze_receipt_digest, str)
                else None
            ),
            trusted_prelabel_packet_manifest_sha256=trusted_prelabel_digest,
            human_review_authority_receipt=authority_receipt_path,
            trusted_human_review_authority_receipt_sha256=(
                trusted_authority_digest
            ),
        )
    except (OSError, ValueError, TypeError) as exc:
        errors.append(f"COMPLETED_PACKET_REVALIDATION_ERROR:{exc}")
        completed_validation = None
    if completed_validation is not None:
        validation_digest = stable_digest(completed_validation)
        evidence["completed_validation_digest"] = validation_digest
        if completed_validation.get("pass") is not True:
            errors.append("COMPLETED_PACKET_REVALIDATION_NONPASS")
        if receipt.get("completed_validation_status") != PASS:
            errors.append("EXPORT_RECEIPT_COMPLETED_VALIDATION_NONPASS")
        if receipt.get("completed_validation_digest") != validation_digest:
            errors.append("EXPORT_RECEIPT_COMPLETED_VALIDATION_DIGEST_MISMATCH")

    observed_label_files: dict[str, str] = {}
    try:
        for name in COMPLETED_LABEL_FILES:
            label_path = labels_root / name
            if label_path.is_file() and not label_path.is_symlink():
                observed_label_files[name] = hashlib.sha256(
                    _secure_private_file_bytes(label_path)
                ).hexdigest()
    except (OSError, EvaluationDataError) as exc:
        errors.append(f"COMPLETED_LABEL_INVENTORY_UNREADABLE:{exc}")
    if receipt.get("completed_label_file_sha256") != dict(
        sorted(observed_label_files.items())
    ):
        errors.append("EXPORT_RECEIPT_COMPLETED_LABEL_INVENTORY_MISMATCH")

    leakage_path = packet_root / "sealed_internal/completed_packet_leakage_check.v1.json"
    try:
        leakage_bytes = _secure_private_file_bytes(leakage_path)
        leakage_sha = hashlib.sha256(leakage_bytes).hexdigest()
        leakage_receipt = json.loads(leakage_bytes)
    except (OSError, ValueError, TypeError, EvaluationDataError) as exc:
        errors.append(f"COMPLETED_LEAKAGE_RECEIPT_UNREADABLE:{exc}")
    else:
        if receipt.get("completed_leakage_check_sha256") != leakage_sha:
            errors.append("EXPORT_RECEIPT_COMPLETED_LEAKAGE_SHA256_MISMATCH")
        if (
            not isinstance(leakage_receipt, Mapping)
            or not digest_matches(leakage_receipt, "record_digest")
            or leakage_receipt.get("status") != PASS
        ):
            errors.append("COMPLETED_LEAKAGE_RECEIPT_INVALID")
        expected_ref = (
            "artifact://sealed_internal/completed_packet_leakage_check.v1.json"
            f"#sha256:{leakage_sha}"
        )
        if any(row.get("leakage_check_ref") != expected_ref for row in rows):
            errors.append("DATASET_COMPLETED_LEAKAGE_REFERENCE_MISMATCH")
    return sorted(set(errors)), evidence


def _proof_split(row: Mapping[str, Any]) -> Any:
    return row.get("proof_split", row.get("split"))


def _retrieval_split(row: Mapping[str, Any]) -> Any:
    return row.get("retrieval_split", row.get("split"))


def _proof_identity(row: Mapping[str, Any]) -> str:
    value = row.get("proof_identity_digest")
    return str(value) if value else f"internal-sample::{row.get('sample_id', '')}"


def _proof_split_group(row: Mapping[str, Any]) -> str:
    value = row.get("proof_split_group_digest")
    return str(value) if value else _proof_identity(row)


def _proof_context_identity(row: Mapping[str, Any]) -> str:
    """Group alternative renderings without collapsing distinct target contexts."""

    target_jd = str(row.get("target_jd_digest") or "")
    target_brief = str(row.get("target_brief_digest") or "")
    case_id = str(row.get("case_id") or "")
    if not (target_jd or target_brief or case_id):
        case_id = str(row.get("sample_id") or "")
    return "::".join((_proof_identity(row), target_jd, target_brief, case_id))


def _unique_proof_rows(rows: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    unique: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        identity = _proof_identity(row)
        existing = unique.get(identity)
        if existing is None or (
            row.get("representation_mode") == "CANONICAL_VISIBLE"
            and existing.get("representation_mode") != "CANONICAL_VISIBLE"
        ):
            unique[identity] = row
    return [unique[identity] for identity in sorted(unique)]


def _unique_proof_context_rows(
    rows: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    unique: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        identity = _proof_context_identity(row)
        existing = unique.get(identity)
        if existing is None or (
            row.get("representation_mode") == "CANONICAL_VISIBLE"
            and existing.get("representation_mode") != "CANONICAL_VISIBLE"
        ):
            unique[identity] = row
    return [unique[identity] for identity in sorted(unique)]


def evaluate_file(
    dataset_path: Path,
    profile: Mapping[str, Any],
    *,
    source_ref: str | None = None,
    export_receipt_path: Path | None = None,
    trusted_export_receipt_sha256: str | None = None,
    trusted_prelabel_packet_manifest_sha256: str | None = None,
    human_review_authority_receipt_path: Path | None = None,
    trusted_human_review_authority_receipt_sha256: str | None = None,
    packet_dir: Path | None = None,
    labels_dir: Path | None = None,
) -> dict[str, Any]:
    """Evaluate an official, externally trusted packet export.

    A standalone JSONL file is never official evidence, even when all of its
    unkeyed row digests are internally consistent.  The caller must provide an
    out-of-band trusted receipt digest and the packet/label roots needed to
    revalidate the complete evidence chain.
    """

    ref = source_ref if source_ref is not None else str(dataset_path)
    if dataset_path.is_symlink():
        return _mark_official_evidence(
            _base_report(
                profile,
                status=INSUFFICIENT,
                reasons=["DATASET_PRIVACY_INVALID:must not be a symlink"],
                source_ref=ref,
            ),
            validated=False,
        )
    if not dataset_path.is_file():
        return _mark_official_evidence(
            _base_report(
                profile,
                status=UNKNOWN,
                reasons=["DATASET_NOT_FOUND"],
                source_ref=ref,
            ),
            validated=False,
        )
    evidence_args_complete = all(
        value is not None
        for value in (
            export_receipt_path,
            trusted_export_receipt_sha256,
            trusted_prelabel_packet_manifest_sha256,
            human_review_authority_receipt_path,
            trusted_human_review_authority_receipt_sha256,
            packet_dir,
            labels_dir,
        )
    )
    try:
        if evidence_args_complete:
            privacy_error = private_path_error(dataset_path, directory=False)
            if privacy_error is not None:
                raise EvaluationDataError(
                    f"DATASET_PRIVACY_INVALID:{privacy_error}"
                )
            dataset_bytes = _secure_private_file_bytes(dataset_path)
        else:
            dataset_bytes = dataset_path.read_bytes()
        rows = _load_jsonl_bytes(dataset_bytes, source=dataset_path)
    except (OSError, EvaluationDataError) as exc:
        return _mark_official_evidence(
            _base_report(
                profile,
                status=INSUFFICIENT,
                reasons=[f"DATASET_UNREADABLE: {exc}"],
                source_ref=ref,
            ),
            validated=False,
        )
    dataset_sha256 = hashlib.sha256(dataset_bytes).hexdigest()
    source_rows = sorted(
        (dict(row) for row in rows), key=lambda row: str(row.get("sample_id", ""))
    )
    try:
        dataset_digest = canonical_digest(source_rows)
    except (TypeError, ValueError) as exc:
        return _mark_official_evidence(
            _base_report(
                profile,
                status=INSUFFICIENT,
                reasons=[f"DATASET_NOT_CANONICAL_JSON: {exc}"],
                source_ref=ref,
                sample_count=len(source_rows),
            ),
            validated=False,
        )
    try:
        evidence_errors, evidence = _official_evidence_chain(
            dataset_path=dataset_path,
            dataset_sha256=dataset_sha256,
            rows=source_rows,
            profile=profile,
            export_receipt_path=export_receipt_path,
            trusted_export_receipt_sha256=trusted_export_receipt_sha256,
            trusted_prelabel_packet_manifest_sha256=(
                trusted_prelabel_packet_manifest_sha256
            ),
            human_review_authority_receipt_path=(
                human_review_authority_receipt_path
            ),
            trusted_human_review_authority_receipt_sha256=(
                trusted_human_review_authority_receipt_sha256
            ),
            packet_dir=packet_dir,
            labels_dir=labels_dir,
        )
    except EvaluationDataError as exc:
        evidence_errors = [f"OFFICIAL_EVIDENCE_PROFILE_INVALID:{exc}"]
        evidence = None
    if evidence_errors:
        return _mark_official_evidence(
            _base_report(
                profile,
                status=INSUFFICIENT,
                reasons=evidence_errors,
                source_ref=ref,
                dataset_digest=dataset_digest,
                sample_count=len(source_rows),
            ),
            validated=False,
            evidence_chain=evidence,
        )
    return _mark_official_evidence(
        evaluate_rows(rows, profile, source_ref=ref, allow_internal_rows=False),
        validated=True,
        evidence_chain=evidence,
    )


def evaluate_rows(
    rows: Sequence[Mapping[str, Any]],
    profile: Mapping[str, Any],
    *,
    source_ref: str = "memory",
    allow_internal_rows: bool = False,
) -> dict[str, Any]:
    """Validate evidence, fit on calibration, and score only the holdout split.

    Production callers must supply the sealed adjudicated packet export.
    ``allow_internal_rows`` exists only for focused unit tests of metric math.
    """

    source_rows = sorted((dict(row) for row in rows), key=lambda row: str(row.get("sample_id", "")))
    try:
        dataset_digest = canonical_digest(source_rows)
    except (TypeError, ValueError) as exc:
        return _base_report(
            profile,
            status=INSUFFICIENT,
            reasons=[f"DATASET_NOT_CANONICAL_JSON: {exc}"],
            source_ref=source_ref,
        )
    sorted_rows, normalization_errors = _normalize_rows(
        source_rows, allow_internal_rows=allow_internal_rows
    )
    calibration_rows = [row for row in sorted_rows if _proof_split(row) == "calibration"]
    holdout_rows = [row for row in sorted_rows if _proof_split(row) == "holdout"]
    calibration_identity_rows = _unique_proof_rows(calibration_rows)
    holdout_identity_rows = _unique_proof_rows(holdout_rows)
    holdout_context_rows = _unique_proof_context_rows(holdout_rows)
    errors = normalization_errors + _validate_dataset(sorted_rows, profile)
    if errors:
        return _base_report(
            profile,
            status=INSUFFICIENT,
            reasons=errors,
            source_ref=source_ref,
            dataset_digest=dataset_digest,
            sample_count=len(sorted_rows),
            calibration_count=len(calibration_identity_rows),
            holdout_count=len(holdout_identity_rows),
        )

    calibration_profile = _mapping(profile, "calibration")
    calibration_scores = [float(row["proof_score_raw"]) for row in calibration_identity_rows]
    calibration_labels = [bool(row["proof_label"]) for row in calibration_identity_rows]
    try:
        model = fit_isotonic_pav(calibration_scores, calibration_labels)
    except EvaluationDataError as exc:
        return _base_report(
            profile,
            status=INSUFFICIENT,
            reasons=[f"CALIBRATION_NOT_IDENTIFIABLE: {exc}"],
            source_ref=source_ref,
            dataset_digest=dataset_digest,
            sample_count=len(sorted_rows),
            calibration_count=len(calibration_identity_rows),
            holdout_count=len(holdout_identity_rows),
        )

    calibration_probabilities = model.predict(calibration_scores)
    holdout_identity_probabilities = model.predict(
        [float(row["proof_score_raw"]) for row in holdout_identity_rows]
    )
    holdout_row_probabilities = model.predict(
        [float(row["proof_score_raw"]) for row in holdout_rows]
    )
    candidate_threshold = _select_candidate_threshold(
        calibration_probabilities,
        calibration_labels,
        precision_floor=float(calibration_profile.get("threshold_precision_floor", 0.9)),
        minimum_threshold=float(calibration_profile.get("minimum_candidate_threshold", 0.9)),
        minimum_positive_count=int(calibration_profile.get("minimum_predicted_positive_count", 1)),
    )
    future_release_summary = _future_release_candidate_summary(
        holdout_identity_rows,
        holdout_identity_probabilities,
        candidate_threshold=candidate_threshold,
    )

    retrieval_profile = _mapping(profile, "retrieval")
    k_values = tuple(int(value) for value in retrieval_profile.get("k_values", (1, 3, 5, 10)))
    gate_k = int(retrieval_profile.get("gate_k", retrieval_profile.get("primary_k", 10)))
    if gate_k not in k_values:
        k_values = tuple(sorted(set(k_values + (gate_k,))))
    positive_floor = float(retrieval_profile.get("relevance_positive_floor", 1.0))
    per_sample_results: list[dict[str, Any]] = []
    retrieval_sample_results: list[dict[str, Any]] = []
    recall_values: list[float] = []
    ndcg_values: list[float] = []
    recall_values_by_k: dict[int, list[float]] = {k: [] for k in k_values}
    pooled_recall_hits_by_k: dict[int, int] = {k: 0 for k in k_values}
    pooled_recall_relevant_by_k: dict[int, int] = {k: 0 for k in k_values}
    ndcg_values_by_k: dict[int, list[float]] = {k: [] for k in k_values}
    rr_values: list[float] = []
    path_values = [float(row["path_accuracy_label"]) for row in holdout_identity_rows]
    margins = [float(row["selection_margin"]) for row in holdout_context_rows]
    entailment_predictions = [
        row.get("claim_entailment_prediction") for row in holdout_identity_rows
    ]
    entailment_labels = [
        bool(row["claim_entailment_label"]) for row in holdout_identity_rows
    ]
    entailment_grades = [
        int(row["claim_entailment_grade"]) for row in holdout_identity_rows
    ]
    applicable_metric_rows = [
        row for row in holdout_identity_rows if row.get("metric_applicable") is True
    ]
    metric_predictions = [
        row.get("metric_binding_prediction") for row in applicable_metric_rows
    ]
    metric_labels = [
        bool(row["metric_binding_label"]) for row in applicable_metric_rows
    ]
    target_relevance_grades = [
        int(row["target_relevance_grade"]) for row in holdout_context_rows
    ]
    authority_holdout_values = [
        row["authority_eligible"] == PASS for row in holdout_identity_rows
    ]

    retrieval_holdout_rows = [
        row
        for row in sorted_rows
        if row.get("ranked_candidate_ids") is not None
        and _retrieval_split(row) == "holdout"
    ]
    retrieval_by_sample: dict[str, dict[str, Any]] = {}
    for row in retrieval_holdout_rows:
        ranked = list(row["ranked_candidate_ids"])
        explicit_ranks = list(row.get("retrieval_ranks") or range(1, len(ranked) + 1))
        relevance = {key: float(value) for key, value in row["relevance_labels"].items()}
        relevant_ids = {
            candidate_id
            for candidate_id, score in relevance.items()
            if score >= positive_floor
        }
        row_retrieval_by_k: dict[str, dict[str, float]] = {}
        for k in k_values:
            ranked_at_k = [
                candidate_id
                for candidate_id, rank in zip(ranked, explicit_ranks)
                if rank <= k
            ]
            recall_value = recall_at_k(
                ranked_at_k, relevance, k, positive_floor=positive_floor
            )
            ndcg_value = ndcg_at_k(
                ranked,
                relevance,
                k,
                ranks=explicit_ranks,
            )
            pooled_recall_hits_by_k[k] += len(relevant_ids.intersection(ranked_at_k))
            pooled_recall_relevant_by_k[k] += len(relevant_ids)
            recall_values_by_k[k].append(recall_value)
            ndcg_values_by_k[k].append(ndcg_value)
            row_retrieval_by_k[str(k)] = {
                "recall": recall_value,
                "ndcg": ndcg_value,
            }
        row_recall = row_retrieval_by_k[str(gate_k)]["recall"]
        row_ndcg = row_retrieval_by_k[str(gate_k)]["ndcg"]
        row_rr = reciprocal_rank(
            ranked,
            relevance,
            positive_floor=positive_floor,
            ranks=explicit_ranks,
        )
        recall_values.append(row_recall)
        ndcg_values.append(row_ndcg)
        rr_values.append(row_rr)
        retrieval_result = {
            "sample_id": row["sample_id"],
            "retrieval_split": "holdout",
            "target_profile_id": row["target_profile_id"],
            "section_id": row["section_id"],
            "recall_at_k": row_recall,
            "ndcg_at_k": row_ndcg,
            "retrieval_metrics_by_k": row_retrieval_by_k,
            "reciprocal_rank": row_rr,
        }
        retrieval_sample_results.append(retrieval_result)
        retrieval_by_sample[str(row["sample_id"])] = retrieval_result

    for row, probability in zip(holdout_rows, holdout_row_probabilities):
        path_exact = bool(row["path_accuracy_label"])
        retrieval_result = retrieval_by_sample.get(str(row["sample_id"]))
        per_sample_results.append(
            {
                "sample_id": row["sample_id"],
                "split": "holdout",
                "proof_split": "holdout",
                "retrieval_split": _retrieval_split(row),
                "target_profile_id": row["target_profile_id"],
                "section_id": row["section_id"],
                "recall_at_k": (
                    retrieval_result["recall_at_k"] if retrieval_result is not None else None
                ),
                "ndcg_at_k": (
                    retrieval_result["ndcg_at_k"] if retrieval_result is not None else None
                ),
                "retrieval_metrics_by_k": (
                    retrieval_result["retrieval_metrics_by_k"]
                    if retrieval_result is not None
                    else None
                ),
                "reciprocal_rank": (
                    retrieval_result["reciprocal_rank"] if retrieval_result is not None else None
                ),
                "exact_path": path_exact,
                "proof_score_raw": float(row["proof_score_raw"]),
                "proof_confidence_calibrated": probability,
                "proof_label": row["proof_label"],
                "authority_eligible": row["authority_eligible"],
                "target_relevance_grade": row["target_relevance_grade"],
                "candidate_threshold_prediction": (
                    probability >= candidate_threshold["threshold"]
                    if candidate_threshold is not None
                    else None
                ),
            }
        )

    ece_bins = int(calibration_profile.get("ece_bins", 10))
    pooled_recall_by_k = {
        k: pooled_recall_hits_by_k[k] / pooled_recall_relevant_by_k[k]
        for k in k_values
    }
    metrics: dict[str, float | None] = {
        "recall_at_k": pooled_recall_by_k[gate_k],
        "ndcg_at_k": _mean(ndcg_values),
        "mrr": _mean(rr_values),
        "authority_eligibility_accuracy": _mean(
            [float(value) for value in authority_holdout_values]
        ),
        "exact_path_accuracy": _mean(path_values),
        "selection_margin_mean": _mean(margins),
        "selection_margin_minimum": min(margins),
        "ece": expected_calibration_error(
            holdout_identity_probabilities,
            [row["proof_label"] for row in holdout_identity_rows],
            n_bins=ece_bins,
        ),
        "brier": brier_score(
            holdout_identity_probabilities,
            [row["proof_label"] for row in holdout_identity_rows],
        ),
        "proof_confidence_candidate_precision": future_release_summary["precision"],
        "proof_confidence_candidate_recall": future_release_summary["recall"],
        "proof_confidence_candidate_support_count": future_release_summary["support_count"],
        "proof_confidence_candidate_minimum": future_release_summary[
            "minimum_calibrated_confidence"
        ],
    }
    for k in k_values:
        metrics[f"recall_at_{k}"] = _mean(recall_values_by_k[k])
        metrics[f"pooled_recall_at_{k}"] = pooled_recall_by_k[k]
        metrics[f"ndcg_at_{k}"] = _mean(ndcg_values_by_k[k])
    metrics.update(_label_summary("claim_entailment", entailment_labels, entailment_predictions))
    metrics["claim_entailment_mean_grade"] = _mean(
        [float(grade) for grade in entailment_grades]
    )
    metrics.update(_label_summary("metric_binding", metric_labels, metric_predictions))
    metrics["target_relevance_mean_grade"] = _mean(
        [float(grade) for grade in target_relevance_grades]
    )

    gate_results, targets_pass = _gate_results(metrics, _mapping(profile, "release_targets"))
    threshold_pass = candidate_threshold is not None
    evaluation_gate_pass = targets_pass and threshold_pass
    reasons: list[str] = []
    if not targets_pass:
        reasons.append("ONE_OR_MORE_RELEASE_TARGETS_FAILED")
    if not threshold_pass:
        reasons.append("NO_CALIBRATION_THRESHOLD_MEETS_PRECISION_AND_SUPPORT_POLICY")
    if not reasons:
        reasons.append("EVALUATION_TARGETS_PASS; POLICY_REMAINS_UNPROMOTED")

    report = _base_report(
        profile,
        status=PASS if evaluation_gate_pass else FAIL,
        reasons=reasons,
        source_ref=source_ref,
        dataset_digest=dataset_digest,
        sample_count=len(sorted_rows),
        calibration_count=len(calibration_identity_rows),
        holdout_count=len(holdout_identity_rows),
    )
    report["evaluation_gate_pass"] = evaluation_gate_pass
    report["coverage"] = {
        "target_profiles": sorted({str(row["target_profile_id"]) for row in sorted_rows}),
        "sections": sorted({str(row["section_id"]) for row in sorted_rows}),
        "proof_target_profiles_by_split": {
            split: sorted(
                {
                    str(row["target_profile_id"])
                    for row in sorted_rows
                    if _proof_split(row) == split
                }
            )
            for split in ("calibration", "holdout")
        },
        "proof_sections_by_split": {
            split: sorted(
                {str(row["section_id"]) for row in sorted_rows if _proof_split(row) == split}
            )
            for split in ("calibration", "holdout")
        },
        "retrieval_target_profiles_by_split": {
            split: sorted(
                {
                    str(row["target_profile_id"])
                    for row in sorted_rows
                    if row.get("ranked_candidate_ids") is not None
                    and _retrieval_split(row) == split
                }
            )
            for split in ("calibration", "holdout")
        },
        "retrieval_sections_by_split": {
            split: sorted(
                {
                    str(row["section_id"])
                    for row in sorted_rows
                    if row.get("ranked_candidate_ids") is not None
                    and _retrieval_split(row) == split
                }
            )
            for split in ("calibration", "holdout")
        },
        "metric_binding_holdout_count": len(metric_labels),
        "authority_eligible_proof_holdout_identity_count": sum(
            authority_holdout_values
        ),
        "proof_calibration_row_count": len(calibration_rows),
        "proof_calibration_identity_count": len(calibration_identity_rows),
        "proof_holdout_row_count": len(holdout_rows),
        "proof_holdout_identity_count": len(holdout_identity_rows),
        "proof_holdout_context_count": len(holdout_context_rows),
        "proof_total_split_group_count": len(
            {_proof_split_group(row) for row in sorted_rows}
        ),
        "proof_calibration_split_group_count": len(
            {_proof_split_group(row) for row in calibration_rows}
        ),
        "proof_holdout_split_group_count": len(
            {_proof_split_group(row) for row in holdout_rows}
        ),
        "retrieval_total_count": sum(
            row.get("ranked_candidate_ids") is not None for row in sorted_rows
        ),
        "retrieval_calibration_count": sum(
            row.get("ranked_candidate_ids") is not None
            and _retrieval_split(row) == "calibration"
            for row in sorted_rows
        ),
        "retrieval_holdout_count": len(recall_values),
    }
    report["metrics"] = metrics
    report["target_relevance_summary"] = {
        "authoritative": False,
        "mean_grade": metrics["target_relevance_mean_grade"],
        "grade_distribution": {
            str(grade): target_relevance_grades.count(grade)
            for grade in range(4)
        },
    }
    report["future_release_candidate_summary"] = future_release_summary
    report["calibration"] = {
        "method": str(calibration_profile.get("method", "")),
        "status": "FIT_ON_CALIBRATION_APPLIED_TO_HOLDOUT",
        "fit_split": "proof_split:calibration",
        "apply_split": "proof_split:holdout",
        "fit_sample_count": len(calibration_identity_rows),
        "fit_row_count": len(calibration_rows),
        "holdout_sample_count": len(holdout_identity_rows),
        "holdout_row_count": len(holdout_rows),
        "model": model.to_mapping(),
        "candidate_threshold": candidate_threshold,
        "active_threshold": calibration_profile.get("active_threshold"),
    }
    report["gate_results"] = gate_results
    report["per_sample_results"] = per_sample_results
    report["retrieval_sample_results"] = retrieval_sample_results
    report["deterministic_digest"] = _report_digest(report)
    return report


def _normalize_rows(
    rows: Sequence[Mapping[str, Any]], *, allow_internal_rows: bool
) -> tuple[list[dict[str, Any]], list[str]]:
    normalized: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, source in enumerate(rows, 1):
        if source.get("schema_version") != _ADJUDICATED_EXPORT_SCHEMA:
            if not allow_internal_rows:
                errors.append(
                    f"SOURCE_ROW_{index}:schema_version:SEALED_ADJUDICATED_EXPORT_REQUIRED"
                )
            normalized.append(dict(source))
            continue
        record_digest = source.get("record_digest")
        expected_digest = canonical_digest(
            {key: value for key, value in source.items() if key != "record_digest"}
        )
        if not isinstance(record_digest, str) or record_digest != expected_digest:
            errors.append(f"SOURCE_ROW_{index}:record_digest:MISMATCH")

        retrieval = source.get("retrieval_candidates")
        ranked_ids: list[str] | None = None
        relevance: dict[str, float] | None = None
        retrieval_path_validity: dict[str, bool] | None = None
        retrieval_metric_bindings: dict[str, str] | None = None
        retrieval_metric_applicability: dict[str, bool] | None = None
        if retrieval is not None:
            if not isinstance(retrieval, list):
                errors.append(f"SOURCE_ROW_{index}:retrieval_candidates:EXPECTED_ARRAY_OR_NULL")
                retrieval = []
            candidates = [dict(item) for item in retrieval if isinstance(item, Mapping)]
            if len(candidates) != len(retrieval):
                errors.append(f"SOURCE_ROW_{index}:retrieval_candidates:INVALID_ENTRY")
            ranks: list[int] = []
            for item in candidates:
                rank = item.get("rank")
                if not isinstance(rank, int) or isinstance(rank, bool) or rank <= 0:
                    errors.append(f"SOURCE_ROW_{index}:retrieval_candidates:INVALID_RANK")
                    item["rank"] = len(candidates) + 1
                ranks.append(int(item["rank"]))
            candidates.sort(key=lambda item: (item["rank"], str(item.get("candidate_id", ""))))
            if len(set(ranks)) != len(ranks):
                errors.append(f"SOURCE_ROW_{index}:retrieval_candidates:DUPLICATE_RANK")
            ranks = [int(item["rank"]) for item in candidates]
            selected_ids = [
                str(item.get("candidate_id", ""))
                for item in candidates
                if item.get("selected") is True
            ]
            if selected_ids != [str(source.get("selected_candidate_id", ""))]:
                errors.append(f"SOURCE_ROW_{index}:retrieval_candidates:SELECTED_ID_MISMATCH")
            ranked_ids = [str(item.get("candidate_id", "")) for item in candidates]
            relevance = {
                str(item.get("candidate_id", "")): item.get("relevance_grade")
                for item in candidates
            }
            retrieval_path_validity = {}
            retrieval_metric_bindings = {}
            retrieval_metric_applicability = {}
            for item in candidates:
                candidate_id = str(item.get("candidate_id", ""))
                path_valid = item.get("path_valid")
                metric_binding = item.get("metric_binding")
                metric_applicable = item.get("metric_applicable")
                if type(path_valid) is not bool:
                    errors.append(
                        f"SOURCE_ROW_{index}:retrieval_candidates:path_valid:INVALID"
                    )
                if metric_binding not in {"EXACT", "INEXACT", "NOT_APPLICABLE"}:
                    errors.append(
                        f"SOURCE_ROW_{index}:retrieval_candidates:metric_binding:INVALID"
                    )
                if type(metric_applicable) is not bool:
                    errors.append(
                        f"SOURCE_ROW_{index}:retrieval_candidates:"
                        "metric_applicable:INVALID"
                    )
                elif (metric_applicable and metric_binding == "NOT_APPLICABLE") or (
                    not metric_applicable and metric_binding != "NOT_APPLICABLE"
                ):
                    errors.append(
                        f"SOURCE_ROW_{index}:retrieval_candidates:"
                        "METRIC_APPLICABILITY_DISPOSITION_MISMATCH"
                    )
                retrieval_path_validity[candidate_id] = path_valid
                retrieval_metric_bindings[candidate_id] = metric_binding
                retrieval_metric_applicability[candidate_id] = metric_applicable
                if (
                    (path_valid is False or metric_binding == "INEXACT")
                    and item.get("relevance_grade") != 0
                ):
                    errors.append(
                        f"SOURCE_ROW_{index}:retrieval_candidates:"
                        "INELIGIBLE_CANDIDATE_MUST_HAVE_ZERO_RELEVANCE"
                    )

        final_metric = source.get("metric_binding")
        if final_metric == "EXACT":
            metric_label: bool | None = True
        elif final_metric == "INEXACT":
            metric_label = False
        elif final_metric == "NOT_APPLICABLE":
            metric_label = None
        else:
            errors.append(f"SOURCE_ROW_{index}:metric_binding:INVALID_FINAL_LABEL")
            metric_label = source.get("metric_binding_label")
        metric_applicable = source.get("metric_applicable")
        if type(metric_applicable) is not bool:
            errors.append(f"SOURCE_ROW_{index}:metric_applicable:INVALID")
        elif (metric_applicable and final_metric == "NOT_APPLICABLE") or (
            not metric_applicable and final_metric != "NOT_APPLICABLE"
        ):
            errors.append(
                f"SOURCE_ROW_{index}:metric_applicable:DISPOSITION_MISMATCH"
            )

        authority_eligible = source.get("authority_eligible")
        if authority_eligible not in {"PASS", "FAIL"}:
            errors.append(f"SOURCE_ROW_{index}:authority_eligible:INVALID_FINAL_LABEL")

        system_fields = source.get("system_fields")
        system_fields = dict(system_fields) if isinstance(system_fields, Mapping) else {}
        system_prediction = source.get("system_prediction")
        prediction_mapping = (
            dict(system_prediction) if isinstance(system_prediction, Mapping) else {}
        )
        proof_label = source.get("overall_proof_valid")
        entailment_grade = source.get("claim_entailment_grade")
        proof_split = source.get("proof_split")
        retrieval_split = source.get("retrieval_split")
        if proof_split not in {"calibration", "holdout"}:
            errors.append(f"SOURCE_ROW_{index}:proof_split:REQUIRED")
        if retrieval_split not in {"calibration", "holdout"}:
            errors.append(f"SOURCE_ROW_{index}:retrieval_split:REQUIRED")
        if source.get("split") != proof_split:
            errors.append(f"SOURCE_ROW_{index}:split:PROOF_SPLIT_ALIAS_MISMATCH")
        proof_identity_digest = source.get("proof_identity_digest")
        if not isinstance(proof_identity_digest, str) or not _SHA256_RE.fullmatch(
            proof_identity_digest
        ):
            errors.append(f"SOURCE_ROW_{index}:proof_identity_digest:INVALID_SHA256")
        proof_split_group_digest = source.get("proof_split_group_digest")
        if not isinstance(proof_split_group_digest, str) or not _SHA256_RE.fullmatch(
            proof_split_group_digest
        ):
            errors.append(
                f"SOURCE_ROW_{index}:proof_split_group_digest:INVALID_SHA256"
            )
        proof_split_policy_id = source.get("proof_split_policy_id")
        if proof_split_policy_id != PROOF_SPLIT_POLICY_ID:
            errors.append(f"SOURCE_ROW_{index}:proof_split_policy_id:INVALID")
        proof_split_policy_salt = source.get("proof_split_policy_salt")
        if (
            not isinstance(proof_split_policy_salt, int)
            or isinstance(proof_split_policy_salt, bool)
            or proof_split_policy_salt < 0
        ):
            errors.append(f"SOURCE_ROW_{index}:proof_split_policy_salt:INVALID")
        reviewer_refs = source.get("reviewer_refs")
        reviewer_refs = reviewer_refs if isinstance(reviewer_refs, list) else []
        adjudication_ref = source.get("adjudication_ref")
        if not _valid_review_ref_pair(reviewer_refs):
            errors.append(f"SOURCE_ROW_{index}:reviewer_refs:INVALID_HUMAN_REVIEW_RECEIPTS")
        if not _valid_adjudication_ref(adjudication_ref):
            errors.append(f"SOURCE_ROW_{index}:adjudication_ref:INVALID_RECEIPT")
        source_content_digest = source.get("content_digest")
        if not isinstance(source_content_digest, str) or not _SHA256_RE.fullmatch(
            source_content_digest
        ):
            errors.append(f"SOURCE_ROW_{index}:content_digest:INVALID_SHA256")
        if source.get("gold_path_semantics") != "system_selected_binding_human_validated":
            errors.append(f"SOURCE_ROW_{index}:gold_path_semantics:INVALID")
        leakage_ref = source.get("leakage_check_ref")
        if not isinstance(leakage_ref, str) or not _ARTIFACT_SHA256_REF_RE.fullmatch(leakage_ref):
            errors.append(f"SOURCE_ROW_{index}:leakage_check_ref:INVALID_DIGEST_BOUND_ARTIFACT")
        if type(proof_label) is bool and source.get("human_score") != float(proof_label):
            errors.append(f"SOURCE_ROW_{index}:human_score:DISAGREES_WITH_PROOF_LABEL")
        frontier_metadata = source.get("candidate_frontier_metadata")
        frontier_metadata = (
            dict(frontier_metadata) if isinstance(frontier_metadata, Mapping) else {}
        )
        row: dict[str, Any] = {
            "schema_version": _ROW_SCHEMA,
            "source_schema_version": _ADJUDICATED_EXPORT_SCHEMA,
            "sample_id": source.get("sample_id"),
            "dataset_id": source.get("dataset_id"),
            "dataset_version": source.get("dataset_version"),
            "split": proof_split,
            "proof_split": proof_split,
            "retrieval_split": retrieval_split,
            "proof_identity_digest": proof_identity_digest,
            "proof_split_group_digest": proof_split_group_digest,
            "proof_split_policy_id": proof_split_policy_id,
            "proof_split_policy_salt": proof_split_policy_salt,
            "target_profile_id": source.get("target_profile_id"),
            "case_id": source.get("case_id"),
            "target_jd_digest": source.get("target_jd_digest"),
            "target_brief_digest": source.get("target_brief_digest"),
            "section_id": source.get("section_id"),
            "claim_unit_id": source.get("claim_unit_id"),
            "representation_mode": source.get("representation_mode"),
            "ranked_candidate_ids": ranked_ids,
            "retrieval_query_id": source.get("retrieval_query_id"),
            "retrieval_query_content_digest": source.get(
                "retrieval_query_content_digest"
            ),
            "retrieval_ranks": ranks if ranked_ids is not None else None,
            "candidate_universe_size": source.get(
                "candidate_universe_size", frontier_metadata.get("candidate_universe_size")
            ),
            "raw_eligible_candidate_count": source.get(
                "raw_eligible_candidate_count",
                frontier_metadata.get("raw_eligible_candidate_count"),
            ),
            "allocator_candidate_budget": source.get(
                "allocator_candidate_budget",
                frontier_metadata.get("allocator_candidate_budget"),
            ),
            "allocator_budget_truncated": source.get(
                "allocator_budget_truncated",
                frontier_metadata.get("allocator_budget_truncated"),
            ),
            "frontier_k": source.get("frontier_k", frontier_metadata.get("frontier_k")),
            "frontier_exhausted": source.get(
                "frontier_exhausted", frontier_metadata.get("frontier_exhausted")
            ),
            "judged_top_count": source.get(
                "judged_top_count", frontier_metadata.get("judged_top_count")
            ),
            "judged_candidate_count": source.get(
                "judged_candidate_count",
                frontier_metadata.get("judged_candidate_count"),
            ),
            "candidate_judging_scope": source.get(
                "candidate_judging_scope",
                frontier_metadata.get("candidate_judging_scope"),
            ),
            "selected_audit_extra": source.get("selected_audit_extra"),
            "retrieval_recall_scope": source.get("retrieval_recall_scope"),
            "relevance_labels": relevance,
            "retrieval_path_validity": retrieval_path_validity,
            "retrieval_metric_bindings": retrieval_metric_bindings,
            "retrieval_metric_applicability": retrieval_metric_applicability,
            "selected_candidate_id": source.get("selected_candidate_id"),
            "predicted_path_ids": list(source.get("gold_path_ids") or []),
            "gold_path_ids": None,
            "path_accuracy_label": source.get("path_accuracy"),
            "claim_entailment_prediction": prediction_mapping.get(
                "claim_entailment_prediction",
                system_fields.get("claim_entailment_prediction"),
            ),
            "claim_entailment_label": (
                entailment_grade >= 2 if isinstance(entailment_grade, int) else None
            ),
            "claim_entailment_grade": entailment_grade,
            "target_relevance_grade": source.get("target_relevance_grade"),
            "metric_binding_prediction": prediction_mapping.get(
                "metric_binding_prediction",
                system_fields.get("metric_binding_prediction"),
            ),
            "metric_binding_label": metric_label,
            "metric_binding_disposition": final_metric,
            "metric_applicable": metric_applicable,
            "authority_eligible": authority_eligible,
            "proof_score_raw": source.get("proof_score_raw"),
            "proof_label": proof_label,
            "selection_margin": source.get("selection_margin"),
            "label_source": source.get("label_source"),
            "proof_reviewer_id_hashes": [
                str(ref.get("reviewer_id_hash") or "")
                for ref in reviewer_refs
                if isinstance(ref, Mapping)
            ],
            "proof_reviewer_identity_refs": [
                str(ref.get("reviewer_identity_ref") or "")
                for ref in reviewer_refs
                if isinstance(ref, Mapping)
            ],
            "retrieval_reviewer_id_hashes": [
                str(ref.get("reviewer_id_hash") or "")
                for ref in (source.get("retrieval_reviewer_refs") or [])
                if isinstance(ref, Mapping)
            ],
            "retrieval_reviewer_identity_refs": [
                str(ref.get("reviewer_identity_ref") or "")
                for ref in (source.get("retrieval_reviewer_refs") or [])
                if isinstance(ref, Mapping)
            ],
            "reviewer_refs": [
                f"{ref.get('review_id', '')}::{ref.get('review_digest', '')}"
                if isinstance(ref, Mapping)
                else str(ref)
                for ref in reviewer_refs
            ],
            "adjudication_ref": _receipt_ref(adjudication_ref),
            "leakage_check_ref": source.get("leakage_check_ref"),
            "leakage_check_status": source.get("leakage_check_status"),
            "label_policy": source.get("label_policy"),
            "created_at": source.get("created_at"),
            "graph_digest": source.get("graph_digest"),
            "policy_digest": source.get("policy_digest"),
            "allocation_plan_digest": source.get("allocation_plan_digest"),
            "source_record_digest": record_digest,
            "source_item_content_digest": source_content_digest,
        }
        if ranked_ids is not None:
            retrieval_reviewers = source.get("retrieval_reviewer_refs")
            retrieval_adjudication = source.get("retrieval_adjudication_ref")
            if (
                not isinstance(retrieval_reviewers, list)
                or not _valid_review_ref_pair(retrieval_reviewers)
            ):
                errors.append(f"SOURCE_ROW_{index}:retrieval_reviewer_refs:INVALID_RECEIPTS")
            if not _valid_adjudication_ref(retrieval_adjudication):
                errors.append(f"SOURCE_ROW_{index}:retrieval_adjudication_ref:INVALID_RECEIPT")
        row["content_digest"] = compute_row_content_digest(row)
        normalized.append(row)
    return normalized, errors


def _receipt_ref(value: Any) -> str:
    if isinstance(value, Mapping):
        receipt_id = str(value.get("adjudication_id") or value.get("receipt_id") or "")
        digest = str(value.get("record_digest") or value.get("digest") or "")
        return f"{receipt_id}::{digest}" if receipt_id and digest else ""
    return str(value or "")


def _valid_review_ref(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    review_id = value.get("review_id")
    reviewer_hash = value.get("reviewer_id_hash")
    reviewer_identity_ref = value.get("reviewer_identity_ref")
    digest = value.get("review_digest")
    return (
        isinstance(review_id, str)
        and bool(review_id)
        and isinstance(reviewer_hash, str)
        and bool(_SHA256_RE.fullmatch(reviewer_hash))
        and isinstance(reviewer_identity_ref, str)
        and reviewer_identity_ref.startswith("human-reviewer://")
        and reviewer_hash
        == hashlib.sha256(reviewer_identity_ref.encode("utf-8")).hexdigest()
        and isinstance(digest, str)
        and bool(_SHA256_RE.fullmatch(digest))
    )


def _valid_review_ref_pair(values: Any) -> bool:
    if not isinstance(values, list) or len(values) != 2:
        return False
    if any(not _valid_review_ref(value) for value in values):
        return False
    for field in (
        "review_id",
        "reviewer_id_hash",
        "reviewer_identity_ref",
        "review_digest",
    ):
        if len({str(value[field]) for value in values}) != 2:
            return False
    return True


def _valid_adjudication_ref(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    receipt_id = value.get("adjudication_id")
    digest = value.get("record_digest")
    return (
        isinstance(receipt_id, str)
        and bool(receipt_id)
        and isinstance(digest, str)
        and bool(_SHA256_RE.fullmatch(digest))
    )


def _label_summary(
    prefix: str, labels: Sequence[bool], predictions: Sequence[bool | None]
) -> dict[str, float | None]:
    if not labels:
        return {
            f"{prefix}_accuracy": None,
            f"{prefix}_prediction_accuracy": None,
            f"{prefix}_precision": None,
            f"{prefix}_recall": None,
            f"{prefix}_predicted_positive_rate": None,
            f"{prefix}_labeled_positive_rate": None,
        }
    count = len(labels)
    positive_rate = sum(labels) / count
    if len(predictions) != count or any(type(value) is not bool for value in predictions):
        return {
            f"{prefix}_accuracy": positive_rate,
            f"{prefix}_prediction_accuracy": None,
            f"{prefix}_precision": None,
            f"{prefix}_recall": None,
            f"{prefix}_predicted_positive_rate": None,
            f"{prefix}_labeled_positive_rate": positive_rate,
        }
    true_positive = sum(prediction and label for prediction, label in zip(predictions, labels))
    predicted_positive = sum(predictions)
    labeled_positive = sum(labels)
    return {
        # The release accuracy is the human-confirmed success rate.  Prediction
        # diagnostics are separate so a trivial negative classifier cannot pass.
        f"{prefix}_accuracy": positive_rate,
        f"{prefix}_prediction_accuracy": sum(
            prediction == label for prediction, label in zip(predictions, labels)
        )
        / count,
        f"{prefix}_precision": true_positive / predicted_positive if predicted_positive else None,
        f"{prefix}_recall": true_positive / labeled_positive if labeled_positive else None,
        f"{prefix}_predicted_positive_rate": predicted_positive / count,
        f"{prefix}_labeled_positive_rate": labeled_positive / count,
    }


def _select_candidate_threshold(
    probabilities: Sequence[float],
    labels: Sequence[bool],
    *,
    precision_floor: float,
    minimum_threshold: float,
    minimum_positive_count: int,
) -> dict[str, Any] | None:
    candidates = sorted(
        {float(probability) for probability in probabilities if probability >= minimum_threshold}
        | ({minimum_threshold} if minimum_threshold <= 1.0 else set())
    )
    eligible: list[dict[str, Any]] = []
    total_positive = sum(labels)
    for threshold in candidates:
        selected = [index for index, probability in enumerate(probabilities) if probability >= threshold]
        if len(selected) < minimum_positive_count:
            continue
        true_positive = sum(labels[index] for index in selected)
        precision = true_positive / len(selected)
        recall = true_positive / total_positive if total_positive else 0.0
        if precision >= precision_floor:
            eligible.append(
                {
                    "threshold": threshold,
                    "precision": precision,
                    "recall": recall,
                    "predicted_positive_count": len(selected),
                    "true_positive_count": true_positive,
                    "selection_split": "proof_split:calibration",
                }
            )
    if not eligible:
        return None
    return sorted(
        eligible,
        key=lambda item: (-item["recall"], -item["precision"], item["threshold"]),
    )[0]


def _future_release_candidate_summary(
    holdout_rows: Sequence[Mapping[str, Any]],
    probabilities: Sequence[float],
    *,
    candidate_threshold: Mapping[str, Any] | None,
) -> dict[str, Any]:
    scope = "canonical_visible_unique_proof_identities_at_or_above_candidate_threshold"
    canonical = [
        (row, float(probability))
        for row, probability in zip(holdout_rows, probabilities)
        if row.get("representation_mode", "CANONICAL_VISIBLE") == "CANONICAL_VISIBLE"
    ]
    if candidate_threshold is None:
        return {
            "scope": scope,
            "precision": None,
            "recall": None,
            "support_count": 0,
            "minimum_calibrated_confidence": None,
            "activation_status": "UNPROMOTED",
        }
    threshold = float(candidate_threshold["threshold"])
    selected = [(row, probability) for row, probability in canonical if probability >= threshold]
    support = len(selected)
    true_positive = sum(bool(row["proof_label"]) for row, _ in selected)
    total_positive = sum(bool(row["proof_label"]) for row, _ in canonical)
    return {
        "scope": scope,
        "precision": true_positive / support if support else None,
        "recall": true_positive / total_positive if total_positive else None,
        "support_count": support,
        "minimum_calibrated_confidence": (
            min(probability for _, probability in selected) if selected else None
        ),
        "activation_status": "UNPROMOTED",
    }


def _gate_results(
    metrics: Mapping[str, float | None], release_targets: Mapping[str, Any]
) -> tuple[dict[str, Any], bool]:
    results: dict[str, Any] = {}
    passed = True
    for target_name, (metric_name, direction) in _RELEASE_TARGETS.items():
        threshold = release_targets.get(target_name)
        value = metrics.get(metric_name)
        if threshold is None:
            results[target_name] = {
                "metric": metric_name,
                "direction": direction,
                "threshold": None,
                "value": value,
                "status": "NOT_GATED",
            }
            continue
        if value is None:
            target_pass = False
        elif direction == "minimum":
            target_pass = value >= float(threshold)
        else:
            target_pass = value <= float(threshold)
        passed = passed and target_pass
        results[target_name] = {
            "metric": metric_name,
            "direction": direction,
            "threshold": float(threshold),
            "value": value,
            "status": PASS if target_pass else FAIL,
        }
    return results, passed


def _validate_dataset(rows: Sequence[Mapping[str, Any]], profile: Mapping[str, Any]) -> list[str]:
    dataset_profile = _mapping(profile, "dataset")
    retrieval_profile = _mapping(profile, "retrieval")
    errors: list[str] = []
    if dataset_profile.get("proof_split_policy_id") != PROOF_SPLIT_POLICY_ID:
        errors.append("PROFILE_PROOF_SPLIT_POLICY_ID_MISMATCH")
    if not rows:
        return sorted(set([*errors, "DATASET_EMPTY"]))

    for index, row in enumerate(rows, 1):
        errors.extend(_validate_row(row, dataset_profile, retrieval_profile, index=index))

    sample_ids = [str(row.get("sample_id")) for row in rows]
    content_digests = [str(row.get("content_digest")) for row in rows]
    if len(set(sample_ids)) != len(sample_ids):
        errors.append("DUPLICATE_SAMPLE_ID")
    if len(set(content_digests)) != len(content_digests):
        errors.append("DUPLICATE_CONTENT_DIGEST")

    canonical_exports = [
        row
        for row in rows
        if row.get("source_schema_version") == _ADJUDICATED_EXPORT_SCHEMA
    ]
    if canonical_exports:
        for field, code in (
            ("leakage_check_ref", "MIXED_LEAKAGE_CHECK_RECEIPTS"),
            ("label_policy", "MIXED_LABEL_POLICIES"),
            ("graph_digest", "MIXED_GRAPH_DIGESTS"),
            ("policy_digest", "MIXED_POLICY_DIGESTS"),
        ):
            if len({row.get(field) for row in canonical_exports}) != 1:
                errors.append(code)
        proof_identity_splits: dict[str, set[str]] = {}
        proof_split_group_splits: dict[str, set[str]] = {}
        for row in canonical_exports:
            proof_identity_splits.setdefault(str(row.get("proof_identity_digest")), set()).add(
                str(_proof_split(row))
            )
            proof_split_group_splits.setdefault(_proof_split_group(row), set()).add(
                str(_proof_split(row))
            )
        if any(len(splits) != 1 for splits in proof_identity_splits.values()):
            errors.append("PROOF_IDENTITY_CROSSES_CALIBRATION_AND_HOLDOUT")
        if any(len(splits) != 1 for splits in proof_split_group_splits.values()):
            errors.append("PROOF_SPLIT_GROUP_CROSSES_CALIBRATION_AND_HOLDOUT")
        salts = {row.get("proof_split_policy_salt") for row in canonical_exports}
        if (
            len(salts) != 1
            or any(not isinstance(salt, int) or isinstance(salt, bool) or salt < 0 for salt in salts)
        ):
            errors.append("MISSING_OR_MIXED_PROOF_SPLIT_POLICY_SALT")
        else:
            salt = next(iter(salts))
            try:
                if any(
                    proof_split_for_digest(_proof_split_group(row), salt=salt)
                    != _proof_split(row)
                    for row in canonical_exports
                ):
                    errors.append("NONDETERMINISTIC_PROOF_SPLIT_ASSIGNMENT")
            except ProofSplitPolicyError:
                errors.append("NONDETERMINISTIC_PROOF_SPLIT_ASSIGNMENT")
        proof_identity_signatures: dict[str, set[str]] = {}
        for row in canonical_exports:
            identity = _proof_identity(row)
            signature = canonical_digest(
                {
                    "proof_score_raw": row.get("proof_score_raw"),
                    "proof_label": row.get("proof_label"),
                    "authority_eligible": row.get("authority_eligible"),
                    "predicted_path_ids": row.get("predicted_path_ids"),
                    "path_accuracy_label": row.get("path_accuracy_label"),
                    "claim_entailment_grade": row.get("claim_entailment_grade"),
                    "claim_entailment_label": row.get("claim_entailment_label"),
                    "metric_binding_disposition": row.get(
                        "metric_binding_disposition"
                    ),
                    "metric_applicable": row.get("metric_applicable"),
                    "metric_binding_label": row.get("metric_binding_label"),
                }
            )
            proof_identity_signatures.setdefault(identity, set()).add(signature)
        if any(len(signatures) != 1 for signatures in proof_identity_signatures.values()):
            errors.append("DUPLICATE_PROOF_IDENTITY_HAS_INCONSISTENT_SCORE_LABEL_OR_BINDING")
        proof_context_signatures: dict[str, set[str]] = {}
        for row in canonical_exports:
            context_identity = _proof_context_identity(row)
            signature = canonical_digest(
                {
                    "selection_margin": row.get("selection_margin"),
                    "claim_entailment_prediction": row.get(
                        "claim_entailment_prediction"
                    ),
                    "metric_binding_prediction": row.get(
                        "metric_binding_prediction"
                    ),
                    "target_relevance_grade": row.get("target_relevance_grade"),
                }
            )
            proof_context_signatures.setdefault(context_identity, set()).add(signature)
        if any(len(signatures) != 1 for signatures in proof_context_signatures.values()):
            errors.append(
                "DUPLICATE_PROOF_CONTEXT_HAS_INCONSISTENT_TARGET_OR_PREDICTION_FIELDS"
            )

        proof_reviewer_hashes = {
            str(value)
            for row in canonical_exports
            for value in row.get("proof_reviewer_id_hashes") or []
        }
        retrieval_reviewer_hashes = {
            str(value)
            for row in canonical_exports
            for value in row.get("retrieval_reviewer_id_hashes") or []
        }
        proof_reviewer_refs = {
            str(value)
            for row in canonical_exports
            for value in row.get("proof_reviewer_identity_refs") or []
        }
        retrieval_reviewer_refs = {
            str(value)
            for row in canonical_exports
            for value in row.get("retrieval_reviewer_identity_refs") or []
        }
        if proof_reviewer_hashes & retrieval_reviewer_hashes:
            errors.append("PROOF_RETRIEVAL_REVIEWER_HASH_COHORTS_OVERLAP")
        if proof_reviewer_refs & retrieval_reviewer_refs:
            errors.append("PROOF_RETRIEVAL_REVIEWER_IDENTITY_REF_COHORTS_OVERLAP")

        for field, code in (
            ("case_id", "RETRIEVAL_CASE_CROSSES_CALIBRATION_AND_HOLDOUT"),
            ("target_jd_digest", "TARGET_JD_CROSSES_CALIBRATION_AND_HOLDOUT"),
            (
                "target_brief_digest",
                "TARGET_BRIEF_CROSSES_CALIBRATION_AND_HOLDOUT",
            ),
        ):
            split_groups: dict[str, set[str]] = {}
            for row in canonical_exports:
                split_groups.setdefault(str(row.get(field) or ""), set()).add(
                    str(_retrieval_split(row))
                )
            if "" in split_groups or any(
                len(splits) != 1 for splits in split_groups.values()
            ):
                errors.append(code)

        retrieval_exports = [
            row
            for row in canonical_exports
            if row.get("ranked_candidate_ids") is not None
        ]
        query_ids = [str(row.get("retrieval_query_id") or "") for row in retrieval_exports]
        query_digests = [
            str(row.get("retrieval_query_content_digest") or "")
            for row in retrieval_exports
        ]
        if any(not value for value in query_ids):
            errors.append("RETRIEVAL_QUERY_ID_MISSING")
        elif len(set(query_ids)) != len(query_ids):
            errors.append("DUPLICATE_RETRIEVAL_QUERY_ID")
        if any(not _SHA256_RE.fullmatch(value) for value in query_digests):
            errors.append("RETRIEVAL_QUERY_CONTENT_DIGEST_INVALID")
        elif len(set(query_digests)) != len(query_digests):
            errors.append("DUPLICATE_RETRIEVAL_QUERY_CONTENT_DIGEST")

    calibration_rows = [row for row in rows if _proof_split(row) == "calibration"]
    holdout_rows = [row for row in rows if _proof_split(row) == "holdout"]
    calibration_identity_rows = _unique_proof_rows(calibration_rows)
    holdout_identity_rows = _unique_proof_rows(holdout_rows)
    minimum_total = int(dataset_profile.get("minimum_total_samples", 1))
    minimum_calibration = int(dataset_profile.get("minimum_calibration_samples", 1))
    minimum_holdout = int(dataset_profile.get("minimum_holdout_samples", 1))
    unique_split_group_count = len({_proof_split_group(row) for row in rows})
    calibration_split_group_count = len(
        {_proof_split_group(row) for row in calibration_rows}
    )
    holdout_split_group_count = len(
        {_proof_split_group(row) for row in holdout_rows}
    )
    if unique_split_group_count < minimum_total:
        errors.append(
            "TOTAL_UNIQUE_PROOF_SPLIT_GROUP_COUNT_BELOW_MINIMUM:"
            f"{unique_split_group_count}<{minimum_total}"
        )
    if calibration_split_group_count < minimum_calibration:
        errors.append(
            "CALIBRATION_UNIQUE_PROOF_SPLIT_GROUP_COUNT_BELOW_MINIMUM:"
            f"{calibration_split_group_count}<{minimum_calibration}"
        )
    if holdout_split_group_count < minimum_holdout:
        errors.append(
            "HOLDOUT_UNIQUE_PROOF_SPLIT_GROUP_COUNT_BELOW_MINIMUM:"
            f"{holdout_split_group_count}<{minimum_holdout}"
        )

    if dataset_profile.get("require_both_proof_labels_per_split", True):
        for split_name, split_rows in (
            ("calibration", calibration_identity_rows),
            ("holdout", holdout_identity_rows),
        ):
            labels = {
                row.get("proof_label") if type(row.get("proof_label")) is bool else None
                for row in split_rows
            }
            if labels != {False, True}:
                errors.append(f"{split_name.upper()}_MISSING_BOTH_PROOF_LABEL_CLASSES")

    required_profiles = {
        str(value) for value in dataset_profile.get("required_target_profiles", ())
    }
    actual_profiles = {str(row.get("target_profile_id")) for row in rows}
    for required in required_profiles:
        if required not in actual_profiles:
            errors.append(f"MISSING_TARGET_PROFILE:{required}")
    required_sections = {str(value) for value in dataset_profile.get("required_sections", ())}
    actual_sections = {str(row.get("section_id")) for row in rows}
    for required in required_sections:
        if required not in actual_sections:
            errors.append(f"MISSING_SECTION:{required}")
    for split_name, split_rows in (("calibration", calibration_rows), ("holdout", holdout_rows)):
        split_profiles = {str(row.get("target_profile_id")) for row in split_rows}
        split_sections = {str(row.get("section_id")) for row in split_rows}
        for missing in sorted(required_profiles - split_profiles):
            errors.append(f"PROOF_{split_name.upper()}_MISSING_TARGET_PROFILE:{missing}")
        for missing in sorted(required_sections - split_sections):
            errors.append(f"PROOF_{split_name.upper()}_MISSING_SECTION:{missing}")

    metric_holdout_count = sum(
        row.get("metric_applicable") is True for row in holdout_identity_rows
    )
    minimum_metric = int(dataset_profile.get("minimum_metric_binding_samples", 1))
    if metric_holdout_count < minimum_metric:
        errors.append(f"METRIC_BINDING_HOLDOUT_COUNT_BELOW_MINIMUM:{metric_holdout_count}<{minimum_metric}")

    retrieval_rows = [row for row in rows if row.get("ranked_candidate_ids") is not None]
    calibration_retrieval = [
        row for row in retrieval_rows if _retrieval_split(row) == "calibration"
    ]
    holdout_retrieval = [row for row in retrieval_rows if _retrieval_split(row) == "holdout"]
    required_retrieval_sections = {
        str(value) for value in dataset_profile.get("required_retrieval_sections", ())
    }
    for split_name, split_rows in (
        ("calibration", calibration_retrieval),
        ("holdout", holdout_retrieval),
    ):
        split_profiles = {str(row.get("target_profile_id")) for row in split_rows}
        split_sections = {str(row.get("section_id")) for row in split_rows}
        for missing in sorted(required_profiles - split_profiles):
            errors.append(f"RETRIEVAL_{split_name.upper()}_MISSING_TARGET_PROFILE:{missing}")
        for missing in sorted(required_retrieval_sections - split_sections):
            errors.append(f"RETRIEVAL_{split_name.upper()}_MISSING_SECTION:{missing}")
    retrieval_minima = (
        (
            "RETRIEVAL_SAMPLE_COUNT_BELOW_MINIMUM",
            len(retrieval_rows),
            int(dataset_profile.get("minimum_retrieval_samples", 1)),
        ),
        (
            "CALIBRATION_RETRIEVAL_COUNT_BELOW_MINIMUM",
            len(calibration_retrieval),
            int(dataset_profile.get("minimum_calibration_retrieval_samples", 1)),
        ),
        (
            "HOLDOUT_RETRIEVAL_COUNT_BELOW_MINIMUM",
            len(holdout_retrieval),
            int(dataset_profile.get("minimum_holdout_retrieval_samples", 1)),
        ),
    )
    for code, actual, minimum in retrieval_minima:
        if actual < minimum:
            errors.append(f"{code}:{actual}<{minimum}")

    return sorted(set(errors))


def _validate_row(
    row: Mapping[str, Any],
    dataset_profile: Mapping[str, Any],
    retrieval_profile: Mapping[str, Any],
    *,
    index: int,
) -> list[str]:
    prefix = f"ROW_{index}"
    errors: list[str] = []

    def require_text(field: str, expected: str | None = None) -> str:
        value = row.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{prefix}:{field}:REQUIRED_NONEMPTY_STRING")
            return ""
        if expected is not None and value != expected:
            errors.append(f"{prefix}:{field}:EXPECTED:{expected}")
        return value

    # Canonical packet exports are normalized to the app-local evaluation row
    # before this validator runs.
    require_text("schema_version", _ROW_SCHEMA)
    require_text("sample_id")
    require_text("dataset_id", str(dataset_profile.get("dataset_id", "")))
    require_text("dataset_version", str(dataset_profile.get("dataset_version", "")))
    split = require_text("split")
    if split not in {"calibration", "holdout"}:
        errors.append(f"{prefix}:split:EXPECTED_CALIBRATION_OR_HOLDOUT")
    if row.get("source_schema_version") == _ADJUDICATED_EXPORT_SCHEMA:
        proof_split = require_text("proof_split")
        retrieval_split = require_text("retrieval_split")
        if proof_split not in {"calibration", "holdout"}:
            errors.append(f"{prefix}:proof_split:EXPECTED_CALIBRATION_OR_HOLDOUT")
        if retrieval_split not in {"calibration", "holdout"}:
            errors.append(f"{prefix}:retrieval_split:EXPECTED_CALIBRATION_OR_HOLDOUT")
        if proof_split != split:
            errors.append(f"{prefix}:split:PROOF_SPLIT_ALIAS_MISMATCH")
        proof_identity = require_text("proof_identity_digest")
        if proof_identity and not _SHA256_RE.fullmatch(proof_identity):
            errors.append(f"{prefix}:proof_identity_digest:INVALID_SHA256")
        proof_split_group = require_text("proof_split_group_digest")
        if proof_split_group and not _SHA256_RE.fullmatch(proof_split_group):
            errors.append(f"{prefix}:proof_split_group_digest:INVALID_SHA256")
        require_text("proof_split_policy_id", PROOF_SPLIT_POLICY_ID)
        proof_split_salt = row.get("proof_split_policy_salt")
        if (
            not isinstance(proof_split_salt, int)
            or isinstance(proof_split_salt, bool)
            or proof_split_salt < 0
        ):
            errors.append(f"{prefix}:proof_split_policy_salt:INVALID")
    require_text("target_profile_id")
    if row.get("source_schema_version") == _ADJUDICATED_EXPORT_SCHEMA:
        require_text("case_id")
        for target_digest_field in ("target_jd_digest", "target_brief_digest"):
            target_digest = require_text(target_digest_field)
            if target_digest and not _SHA256_RE.fullmatch(target_digest):
                errors.append(f"{prefix}:{target_digest_field}:INVALID_SHA256")
    require_text("section_id")
    require_text("claim_unit_id")
    representation_mode = require_text("representation_mode")
    if representation_mode not in {"CANONICAL_VISIBLE", "DERIVED_ALTERNATIVE"}:
        errors.append(f"{prefix}:representation_mode:INVALID")
    require_text("selected_candidate_id")
    require_text("label_policy")
    require_text("adjudication_ref")
    require_text("leakage_check_ref")
    require_text("leakage_check_status", "PASS")
    require_text("label_source", str(dataset_profile.get("required_label_source", "human_semantic_review")))

    for digest_field in ("graph_digest", "policy_digest", "allocation_plan_digest"):
        digest = require_text(digest_field)
        if digest and not _SHA256_RE.fullmatch(digest):
            errors.append(f"{prefix}:{digest_field}:INVALID_SHA256")

    ranked = row.get("ranked_candidate_ids")
    relevance = row.get("relevance_labels")
    if ranked is None:
        if relevance is not None:
            errors.append(f"{prefix}:relevance_labels:MUST_BE_NULL_WITHOUT_RETRIEVAL_RANKING")
        if row.get("source_schema_version") == _ADJUDICATED_EXPORT_SCHEMA:
            if row.get("retrieval_query_id") is not None:
                errors.append(f"{prefix}:retrieval_query_id:MUST_BE_NULL_WITHOUT_RANKING")
            if row.get("retrieval_query_content_digest") is not None:
                errors.append(
                    f"{prefix}:retrieval_query_content_digest:MUST_BE_NULL_WITHOUT_RANKING"
                )
    else:
        if row.get("source_schema_version") == _ADJUDICATED_EXPORT_SCHEMA:
            require_text("retrieval_query_id")
            query_digest = require_text("retrieval_query_content_digest")
            if query_digest and not _SHA256_RE.fullmatch(query_digest):
                errors.append(f"{prefix}:retrieval_query_content_digest:INVALID_SHA256")
        if not isinstance(ranked, list) or not ranked or any(
            not isinstance(item, str) or not item for item in ranked
        ):
            errors.append(f"{prefix}:ranked_candidate_ids:EXPECTED_NONEMPTY_STRING_LIST")
            ranked = []
        elif len(set(ranked)) != len(ranked):
            errors.append(f"{prefix}:ranked_candidate_ids:DUPLICATE_CANDIDATE")
        if not isinstance(relevance, dict) or not relevance:
            errors.append(f"{prefix}:relevance_labels:EXPECTED_NONEMPTY_MAPPING")
            relevance = {}
        else:
            minimum_grade = float(retrieval_profile.get("relevance_grade_minimum", 0.0))
            maximum_grade = float(retrieval_profile.get("relevance_grade_maximum", 3.0))
            for candidate_id, score in relevance.items():
                if (
                    not isinstance(candidate_id, str)
                    or not candidate_id
                    or not _is_number(score)
                    or not minimum_grade <= float(score) <= maximum_grade
                ):
                    errors.append(f"{prefix}:relevance_labels:INVALID_ENTRY")
                    break
            if set(relevance) != set(ranked):
                errors.append(f"{prefix}:relevance_labels:MUST_LABEL_EVERY_AND_ONLY_RANKED_CANDIDATE")
            floor = float(retrieval_profile.get("relevance_positive_floor", 1.0))
            if not any(_is_number(score) and float(score) >= floor for score in relevance.values()):
                errors.append(f"{prefix}:relevance_labels:NO_RELEVANT_CANDIDATE")
        if ranked and row.get("selected_candidate_id") not in ranked:
            errors.append(f"{prefix}:selected_candidate_id:NOT_IN_RANKING")
        retrieval_ranks = row.get("retrieval_ranks")
        if retrieval_ranks is None and row.get("source_schema_version") != _ADJUDICATED_EXPORT_SCHEMA:
            retrieval_ranks = list(range(1, len(ranked) + 1))
        if (
            not isinstance(retrieval_ranks, list)
            or len(retrieval_ranks) != len(ranked)
            or any(
                not isinstance(rank, int) or isinstance(rank, bool) or rank <= 0
                for rank in retrieval_ranks
            )
        ):
            errors.append(f"{prefix}:retrieval_ranks:EXPECTED_ALIGNED_POSITIVE_INTEGERS")
        else:
            if len(set(retrieval_ranks)) != len(retrieval_ranks):
                errors.append(f"{prefix}:retrieval_ranks:DUPLICATE_RANK")
            if retrieval_ranks != sorted(retrieval_ranks):
                errors.append(f"{prefix}:retrieval_ranks:NOT_SORTED_BY_EXPLICIT_RANK")
            configured_frontier_k = int(retrieval_profile.get("frontier_k", 10))
            if row.get("source_schema_version") == _ADJUDICATED_EXPORT_SCHEMA:
                universe_size = row.get("candidate_universe_size")
                frontier_k = row.get("frontier_k")
                frontier_exhausted = row.get("frontier_exhausted")
                judged_top_count = row.get("judged_top_count")
                judged_candidate_count = row.get("judged_candidate_count")
                candidate_judging_scope = row.get("candidate_judging_scope")
                recall_scope = row.get("retrieval_recall_scope")
                selected_audit_extra = row.get("selected_audit_extra")
                raw_eligible_count = row.get("raw_eligible_candidate_count")
                allocator_budget = row.get("allocator_candidate_budget")
                allocator_truncated = row.get("allocator_budget_truncated")
            else:
                universe_size = len(ranked)
                frontier_k = configured_frontier_k
                frontier_exhausted = universe_size <= frontier_k
                judged_top_count = min(frontier_k, universe_size)
                judged_candidate_count = universe_size
                candidate_judging_scope = "FULL_FINITE_UNIVERSE"
                recall_scope = "FULL_FINITE_UNIVERSE"
                selected_audit_extra = None
                raw_eligible_count = universe_size
                allocator_budget = int(
                    retrieval_profile.get("allocator_candidate_budget", 64)
                )
                allocator_truncated = raw_eligible_count > allocator_budget
            configured_budget = int(retrieval_profile.get("allocator_candidate_budget", 64))
            if (
                not isinstance(raw_eligible_count, int)
                or isinstance(raw_eligible_count, bool)
                or raw_eligible_count <= 0
            ):
                errors.append(
                    f"{prefix}:raw_eligible_candidate_count:EXPECTED_POSITIVE_INTEGER"
                )
                raw_eligible_count = len(ranked)
            if allocator_budget != configured_budget:
                errors.append(f"{prefix}:allocator_candidate_budget:PROFILE_MISMATCH")
                allocator_budget = configured_budget
            if allocator_truncated is not (raw_eligible_count > allocator_budget):
                errors.append(f"{prefix}:allocator_budget_truncated:COUNT_MISMATCH")
            if (
                not isinstance(universe_size, int)
                or isinstance(universe_size, bool)
                or universe_size <= 0
            ):
                errors.append(f"{prefix}:candidate_universe_size:EXPECTED_POSITIVE_INTEGER")
                universe_size = len(ranked)
            if universe_size != min(raw_eligible_count, allocator_budget):
                errors.append(f"{prefix}:candidate_universe_size:ALLOCATOR_BOUNDARY_MISMATCH")
            if frontier_k != configured_frontier_k:
                errors.append(f"{prefix}:frontier_k:PROFILE_MISMATCH")
                frontier_k = configured_frontier_k
            expected_top_count = min(frontier_k, universe_size)
            if judged_top_count != expected_top_count:
                errors.append(f"{prefix}:judged_top_count:FINITE_UNIVERSE_MISMATCH")
            if judged_candidate_count != universe_size:
                errors.append(
                    f"{prefix}:judged_candidate_count:FINITE_UNIVERSE_MISMATCH"
                )
            expected_exhausted = universe_size <= frontier_k
            if frontier_exhausted is not expected_exhausted:
                errors.append(f"{prefix}:frontier_exhausted:FINITE_UNIVERSE_MISMATCH")
            if candidate_judging_scope != "FULL_FINITE_UNIVERSE":
                errors.append(
                    f"{prefix}:candidate_judging_scope:FINITE_UNIVERSE_MISMATCH"
                )
            if recall_scope != "FULL_FINITE_UNIVERSE":
                errors.append(f"{prefix}:retrieval_recall_scope:FINITE_UNIVERSE_MISMATCH")
            required_ranks = set(range(1, universe_size + 1))
            observed_ranks = set(retrieval_ranks)
            for missing_rank in sorted(required_ranks - observed_ranks):
                errors.append(f"{prefix}:retrieval_ranks:MISSING_REQUIRED_RANK:{missing_rank}")
            if observed_ranks - required_ranks:
                errors.append(f"{prefix}:retrieval_ranks:OUTSIDE_FINITE_UNIVERSE")
            if len(ranked) != universe_size:
                errors.append(f"{prefix}:ranked_candidate_ids:FINITE_UNIVERSE_INCOMPLETE")
            expected_selected_extra = None
            if row.get("selected_candidate_id") in ranked:
                selected_index = ranked.index(row.get("selected_candidate_id"))
                selected_rank = retrieval_ranks[selected_index]
                if selected_rank > frontier_k:
                    expected_selected_extra = {
                        "candidate_id": row.get("selected_candidate_id"),
                        "rank": selected_rank,
                    }
            if selected_audit_extra != expected_selected_extra:
                errors.append(f"{prefix}:selected_audit_extra:BINDING_MISMATCH")

    predicted_path = row.get("predicted_path_ids")
    if not isinstance(predicted_path, list) or not predicted_path or any(
        not isinstance(item, str) or not item for item in predicted_path
    ):
        errors.append(f"{prefix}:predicted_path_ids:EXPECTED_NONEMPTY_STRING_LIST")
    elif len(set(predicted_path)) != len(predicted_path):
        errors.append(f"{prefix}:predicted_path_ids:DUPLICATE_PATH_NODE")
    gold_path = row.get("gold_path_ids")
    if gold_path is not None:
        if not isinstance(gold_path, list) or not gold_path or any(
            not isinstance(item, str) or not item for item in gold_path
        ):
            errors.append(f"{prefix}:gold_path_ids:EXPECTED_NONEMPTY_STRING_LIST_OR_NULL")
        elif len(set(gold_path)) != len(gold_path):
            errors.append(f"{prefix}:gold_path_ids:DUPLICATE_PATH_NODE")

    for bool_field in ("path_accuracy_label", "claim_entailment_label", "proof_label"):
        if type(row.get(bool_field)) is not bool:
            errors.append(f"{prefix}:{bool_field}:EXPECTED_BOOLEAN")

    authority_eligible = row.get("authority_eligible")
    if authority_eligible not in {"PASS", "FAIL"}:
        errors.append(f"{prefix}:authority_eligible:EXPECTED_PASS_OR_FAIL")

    if isinstance(gold_path, list) and type(row.get("path_accuracy_label")) is bool:
        if (predicted_path == gold_path) != row["path_accuracy_label"]:
            errors.append(f"{prefix}:path_accuracy_label:DISAGREES_WITH_GOLD_PATH")

    entailment_grade = row.get("claim_entailment_grade")
    if (
        not isinstance(entailment_grade, int)
        or isinstance(entailment_grade, bool)
        or not 0 <= entailment_grade <= 3
    ):
        errors.append(f"{prefix}:claim_entailment_grade:EXPECTED_INTEGER_0_TO_3")
    elif type(row.get("claim_entailment_label")) is bool:
        if (entailment_grade >= 2) != row["claim_entailment_label"]:
            errors.append(f"{prefix}:claim_entailment_label:DISAGREES_WITH_GRADE")

    target_relevance_grade = row.get("target_relevance_grade")
    if (
        not isinstance(target_relevance_grade, int)
        or isinstance(target_relevance_grade, bool)
        or not 0 <= target_relevance_grade <= 3
    ):
        errors.append(f"{prefix}:target_relevance_grade:EXPECTED_INTEGER_0_TO_3")

    entailment_prediction = row.get("claim_entailment_prediction")
    if entailment_prediction is not None and type(entailment_prediction) is not bool:
        errors.append(f"{prefix}:claim_entailment_prediction:EXPECTED_BOOLEAN_OR_NULL")

    metric_prediction = row.get("metric_binding_prediction")
    metric_label = row.get("metric_binding_label")
    metric_applicable = row.get("metric_applicable")
    if type(metric_applicable) is not bool:
        errors.append(f"{prefix}:metric_applicable:EXPECTED_BOOLEAN")
    if metric_label is not None and type(metric_label) is not bool:
        errors.append(f"{prefix}:metric_binding_label:EXPECTED_BOOLEAN_OR_NULL")
    if metric_prediction is not None and type(metric_prediction) is not bool:
        errors.append(f"{prefix}:metric_binding_prediction:EXPECTED_BOOLEAN_OR_NULL")
    metric_disposition = row.get("metric_binding_disposition")
    if row.get("source_schema_version") == _ADJUDICATED_EXPORT_SCHEMA:
        if metric_disposition not in {"EXACT", "INEXACT", "NOT_APPLICABLE"}:
            errors.append(f"{prefix}:metric_binding_disposition:INVALID")
    elif metric_disposition is None:
        metric_disposition = (
            "EXACT"
            if metric_label is True
            else "INEXACT"
            if metric_label is False
            else "NOT_APPLICABLE"
        )
    expected_metric_label = {
        "EXACT": True,
        "INEXACT": False,
        "NOT_APPLICABLE": None,
    }.get(metric_disposition)
    if metric_disposition in {"EXACT", "INEXACT", "NOT_APPLICABLE"}:
        if metric_label is not expected_metric_label:
            errors.append(f"{prefix}:metric_binding_label:DISAGREES_WITH_DISPOSITION")
        if type(metric_applicable) is bool and (
            (metric_applicable and metric_disposition == "NOT_APPLICABLE")
            or (not metric_applicable and metric_disposition != "NOT_APPLICABLE")
        ):
            errors.append(
                f"{prefix}:metric_applicable:DISAGREES_WITH_DISPOSITION"
            )

    if (
        authority_eligible in {"PASS", "FAIL"}
        and isinstance(entailment_grade, int)
        and not isinstance(entailment_grade, bool)
        and 0 <= entailment_grade <= 3
        and type(row.get("path_accuracy_label")) is bool
        and metric_disposition in {"EXACT", "INEXACT", "NOT_APPLICABLE"}
        and type(row.get("proof_label")) is bool
    ):
        expected_proof = (
            authority_eligible == "PASS"
            and entailment_grade >= 2
            and row["path_accuracy_label"] is True
            and metric_disposition in {"EXACT", "NOT_APPLICABLE"}
        )
        if row["proof_label"] is not expected_proof:
            errors.append(f"{prefix}:proof_label:DISAGREES_WITH_FROZEN_PROOF_RUBRIC")

    proof_score = row.get("proof_score_raw")
    if not _is_number(proof_score):
        errors.append(f"{prefix}:proof_score_raw:EXPECTED_FINITE_NUMERIC")
    margin = row.get("selection_margin")
    if not _is_number(margin):
        errors.append(f"{prefix}:selection_margin:EXPECTED_FINITE_NUMERIC")

    reviewers = row.get("reviewer_refs")
    minimum_reviewers = 2 if dataset_profile.get("require_two_reviewers", True) else 1
    if (
        not isinstance(reviewers, list)
        or len(reviewers) < minimum_reviewers
        or any(not isinstance(ref, str) or not ref for ref in reviewers)
        or len(set(reviewers)) != len(reviewers)
    ):
        errors.append(f"{prefix}:reviewer_refs:INSUFFICIENT_UNIQUE_REVIEWERS")

    created_at = require_text("created_at")
    if created_at:
        try:
            parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError("timezone missing")
        except ValueError:
            errors.append(f"{prefix}:created_at:EXPECTED_TIMEZONE_AWARE_ISO8601")

    content_digest = row.get("content_digest")
    if not isinstance(content_digest, str) or content_digest != compute_row_content_digest(row):
        errors.append(f"{prefix}:content_digest:MISMATCH")

    return errors


__all__ = [
    "FAIL",
    "INSUFFICIENT",
    "PASS",
    "UNKNOWN",
    "EvaluationDataError",
    "IsotonicModel",
    "brier_score",
    "build_sanitized_ci_receipt",
    "canonical_digest",
    "compute_row_content_digest",
    "evaluate_file",
    "evaluate_rows",
    "expected_calibration_error",
    "fit_isotonic_pav",
    "load_jsonl",
    "ndcg_at_k",
    "recall_at_k",
    "reciprocal_rank",
    "report_digest_is_valid",
]
