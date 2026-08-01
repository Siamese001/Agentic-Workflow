"""Deterministic report and sanitized receipt construction."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Sequence

from apps_rg.evals.resume_graph.constants import (
    _CI_RECEIPT_SCHEMA,
    _METRIC_NAMES,
    _REPORT_SCHEMA,
)
from apps_rg.evals.resume_graph.dataset import _mapping
from apps_rg.evals.resume_graph.models import EvaluationDataError


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


def _empty_metrics() -> dict[str, None]:
    return dict.fromkeys(_METRIC_NAMES)


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
            "gate_k": int(retrieval_profile.get("gate_k", retrieval_profile.get("primary_k", 10))),
            "relevance_positive_floor": float(retrieval_profile.get("relevance_positive_floor", 2.0)),
            "recall_definition": str(retrieval_profile.get("recall_definition", "")),
            "frontier_k": int(retrieval_profile.get("frontier_k", 10)),
            "maximum_selected_audit_extras": int(retrieval_profile.get("maximum_selected_audit_extras", 1)),
            "allocator_candidate_budget": int(retrieval_profile.get("allocator_candidate_budget", 64)),
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
            re.sub(r"[^A-Z0-9_]+", "_", str(reason).split(":", 1)[0].split(";", 1)[0].upper()).strip("_")[:96]
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
        "official_evidence_chain_validated": report.get("official_evidence_chain_validated"),
        "unknown_is_pass": report.get("unknown_is_pass"),
        "evaluation_gate_pass": report.get("evaluation_gate_pass"),
        "promotion_eligible": report.get("promotion_eligible"),
        "current_run_mutated": report.get("current_run_mutated"),
        "future_run_only": report.get("future_run_only"),
        "target_alignment_authoritative": report.get("target_alignment_authoritative"),
        "reason_codes": reason_codes,
        "reason_count": len(report.get("reasons") or []),
        "dataset_summary": {
            "dataset_id": dataset.get("dataset_id"),
            "dataset_version": dataset.get("dataset_version"),
            "digest": dataset.get("digest"),
            "sample_count": dataset.get("sample_count"),
            "calibration_count": dataset.get("calibration_count"),
            "holdout_count": dataset.get("holdout_count"),
            "proof_total_split_group_count": coverage.get("proof_total_split_group_count"),
            "proof_calibration_split_group_count": coverage.get("proof_calibration_split_group_count"),
            "proof_holdout_split_group_count": coverage.get("proof_holdout_split_group_count"),
            "retrieval_total_count": coverage.get("retrieval_total_count"),
            "retrieval_calibration_count": coverage.get("retrieval_calibration_count"),
            "retrieval_holdout_count": coverage.get("retrieval_holdout_count"),
            "metric_binding_holdout_count": coverage.get("metric_binding_holdout_count"),
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
        "protected_full_report_deterministic_digest": report.get("deterministic_digest"),
    }
    receipt["record_digest"] = canonical_digest(receipt)
    return receipt
