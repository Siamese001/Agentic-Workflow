"""Validate the apps_rg W6 evaluation receipt.

The gate is advisory by default while the human dataset is outstanding.  Set
``APPS_RG_RESUME_GRAPH_W6_FAIL_CLOSED=1`` to make UNKNOWN, INSUFFICIENT, FAIL,
or an unsafe/malformed receipt block CI.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Any, Mapping

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_rg.evals.resume_graph_evaluation import (  # noqa: E402
    FAIL,
    INSUFFICIENT,
    PASS,
    UNKNOWN,
    _METRIC_NAMES,
    _RELEASE_TARGETS,
    canonical_digest,
)
from apps_rg.evals.c03_human_eval.split_policy import (  # noqa: E402
    PROOF_SPLIT_POLICY_ID,
)
from ops_scripts.ci._apps_rg_spearman_gate_common import finish  # noqa: E402


DEFAULT_ARTIFACT = REPO_ROOT / "artifacts/calibration/apps_rg_resume_graph_w6.json"
CANONICAL_PROFILE = (
    REPO_ROOT / "apps_rg/config/domain_contract/resume_graph_evaluation_profile.yaml"
)
FAIL_CLOSED_ENV = "APPS_RG_RESUME_GRAPH_W6_FAIL_CLOSED"
TRUSTED_REPORT_SHA256_ENV = "APPS_RG_RESUME_GRAPH_W6_TRUSTED_CI_RECEIPT_SHA256"
TRUSTED_FULL_REPORT_SHA256_ENV = (
    "APPS_RG_RESUME_GRAPH_W6_TRUSTED_FULL_REPORT_SHA256"
)
_CI_RECEIPT_SCHEMA = "apps_rg.resume_graph_w6_ci_receipt.v1"
_CONTROLLED_ONLY_KEYS = (
    "per_sample_results",
    "retrieval_sample_results",
    "coverage",
    "model",
    "candidate_threshold",
    "proof_score_raw",
    "proof_confidence_calibrated",
    "source_ref",
    "future_release_candidate_summary",
    "reasons",
    "reviewer_refs",
    "visible_claim_text",
)
_TOP_LEVEL_KEYS = {
    "schema_version",
    "evaluation_id",
    "profile_digest",
    "policy_version",
    "policy_activation_status",
    "status",
    "evaluation_mode",
    "official_evidence_chain_validated",
    "unknown_is_pass",
    "evaluation_gate_pass",
    "promotion_eligible",
    "current_run_mutated",
    "future_run_only",
    "target_alignment_authoritative",
    "reason_codes",
    "reason_count",
    "dataset_summary",
    "calibration_summary",
    "metrics",
    "gate_results",
    "evidence_chain",
    "protected_full_report_sha256",
    "protected_full_report_deterministic_digest",
    "record_digest",
}
_DATASET_SUMMARY_KEYS = {
    "dataset_id",
    "dataset_version",
    "digest",
    "sample_count",
    "calibration_count",
    "holdout_count",
    "proof_total_split_group_count",
    "proof_calibration_split_group_count",
    "proof_holdout_split_group_count",
    "retrieval_total_count",
    "retrieval_calibration_count",
    "retrieval_holdout_count",
    "metric_binding_holdout_count",
}
_CALIBRATION_SUMMARY_KEYS = {
    "method",
    "status",
    "fit_split",
    "apply_split",
    "fit_sample_count",
    "fit_row_count",
    "holdout_sample_count",
    "holdout_row_count",
    "active_threshold",
}
_EVIDENCE_CHAIN_KEYS = {
    "export_receipt_sha256",
    "prelabel_packet_manifest_sha256",
    "human_review_authority_receipt_sha256",
    "packet_manifest_sha256",
    "packet_manifest_digest",
    "completed_validation_digest",
}
_GATE_RESULT_KEYS = {"metric", "direction", "threshold", "value", "status"}
_PASS_REQUIRED_FINITE_METRICS = set(_METRIC_NAMES) - {
    "claim_entailment_prediction_accuracy",
    "claim_entailment_precision",
    "claim_entailment_recall",
    "claim_entailment_predicted_positive_rate",
    "metric_binding_prediction_accuracy",
    "metric_binding_precision",
    "metric_binding_recall",
    "metric_binding_predicted_positive_rate",
}


def _inventory_error(value: Any, expected: set[str], label: str) -> str | None:
    if not isinstance(value, Mapping):
        return f"{label} must be an object"
    observed = set(value)
    if observed != expected:
        missing = sorted(expected - observed)
        extra = sorted(observed - expected)
        return f"{label} key inventory mismatch (missing={missing}, extra={extra})"
    return None


def _finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _count_at_least(value: Any, minimum: Any) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value >= int(minimum)
    )


def _contains_key(value: Any, target: str) -> bool:
    if isinstance(value, Mapping):
        return target in value or any(_contains_key(item, target) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, target) for item in value)
    return False


def validate_artifact(
    path: Path = DEFAULT_ARTIFACT,
    *,
    trusted_report_sha256: str | None = None,
    trusted_full_report_sha256: str | None = None,
) -> list[str]:
    if not path.is_file():
        return [f"W6 evaluation receipt is missing: {path}"]
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"W6 evaluation receipt is unreadable: {exc}"]
    if not isinstance(report, dict):
        return ["W6 evaluation receipt must be a JSON object"]

    errors: list[str] = []
    inventory_error = _inventory_error(report, _TOP_LEVEL_KEYS, "sanitized CI receipt")
    if inventory_error is not None:
        errors.append(inventory_error)
    if report.get("schema_version") != _CI_RECEIPT_SCHEMA:
        errors.append("unexpected W6 sanitized CI receipt schema")
    receipt_digest = report.get("record_digest")
    try:
        expected_receipt_digest = canonical_digest(
            {key: value for key, value in report.items() if key != "record_digest"}
        )
    except (TypeError, ValueError):
        expected_receipt_digest = None
    if not isinstance(receipt_digest, str) or receipt_digest != expected_receipt_digest:
        errors.append("sanitized CI receipt digest is missing or invalid")
    for controlled_key in _CONTROLLED_ONLY_KEYS:
        if _contains_key(report, controlled_key):
            errors.append(
                f"sanitized CI receipt exposes controlled-only key: {controlled_key}"
            )
    reason_codes = report.get("reason_codes")
    if (
        not isinstance(reason_codes, list)
        or any(not isinstance(code, str) or not code for code in reason_codes)
        or reason_codes != sorted(set(reason_codes))
    ):
        errors.append("sanitized CI receipt reason_codes must be sorted unique strings")
    reason_count = report.get("reason_count")
    if not isinstance(reason_count, int) or isinstance(reason_count, bool) or reason_count < 0:
        errors.append("sanitized CI receipt reason_count must be a nonnegative integer")

    dataset = report.get("dataset_summary")
    inventory_error = _inventory_error(
        dataset, _DATASET_SUMMARY_KEYS, "dataset_summary"
    )
    if inventory_error is not None:
        errors.append(inventory_error)
    calibration = report.get("calibration_summary")
    inventory_error = _inventory_error(
        calibration, _CALIBRATION_SUMMARY_KEYS, "calibration_summary"
    )
    if inventory_error is not None:
        errors.append(inventory_error)
    evidence_chain = report.get("evidence_chain")
    inventory_error = _inventory_error(
        evidence_chain, _EVIDENCE_CHAIN_KEYS, "evidence_chain"
    )
    if inventory_error is not None:
        errors.append(inventory_error)
    metrics = report.get("metrics")
    inventory_error = _inventory_error(metrics, set(_METRIC_NAMES), "metrics")
    if inventory_error is not None:
        errors.append(inventory_error)

    try:
        canonical_profile = yaml.safe_load(CANONICAL_PROFILE.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"canonical W6 evaluation profile is unreadable: {exc}")
        canonical_profile = None
    if not isinstance(canonical_profile, Mapping):
        if canonical_profile is not None:
            errors.append("canonical W6 evaluation profile must be a mapping")
        canonical_profile = None
    elif not isinstance(canonical_profile.get("dataset"), Mapping):
        errors.append("canonical W6 dataset profile must be a mapping")
    elif (
        canonical_profile["dataset"].get("proof_split_policy_id")
        != PROOF_SPLIT_POLICY_ID
    ):
        errors.append(
            "canonical W6 proof split policy differs from the shared evaluator contract"
        )
    if report.get("unknown_is_pass") is not False:
        errors.append("unknown_is_pass must be false")
    if report.get("current_run_mutated") is not False:
        errors.append("offline calibration must not mutate the current run")
    if report.get("target_alignment_authoritative") is not False:
        errors.append("target alignment must remain non-authoritative")
    if report.get("policy_activation_status") != "UNPROMOTED":
        errors.append("W6 may evaluate only an UNPROMOTED future-run policy")
    if report.get("promotion_eligible") is not False:
        errors.append("W6 evaluation cannot make a policy promotion eligible")
    if report.get("future_run_only") is not True:
        errors.append("W6 calibration must remain future-run-only")
    if not isinstance(calibration, Mapping) or calibration.get("active_threshold") is not None:
        errors.append("W6 evaluation cannot contain an active threshold")

    status = report.get("status")
    if status in {UNKNOWN, INSUFFICIENT}:
        if not isinstance(metrics, Mapping) or any(value is not None for value in metrics.values()):
            errors.append("UNKNOWN/INSUFFICIENT receipts must contain only null metrics")
        if not isinstance(calibration, Mapping):
            errors.append("UNKNOWN/INSUFFICIENT receipt lacks calibration summary")
        if _contains_key(report, "proof_confidence_calibrated"):
            errors.append("UNKNOWN/INSUFFICIENT receipt exposes calibrated confidence")

    if status != PASS:
        errors.append(f"W6 evaluation disposition is nonpass: {status}")
    else:
        trusted_report_digest = (
            trusted_report_sha256
            if trusted_report_sha256 is not None
            else os.environ.get(TRUSTED_REPORT_SHA256_ENV, "")
        ).removeprefix("sha256:")
        if len(trusted_report_digest) != 64 or any(
            char not in "0123456789abcdef" for char in trusted_report_digest
        ):
            errors.append(
                "PASS receipt requires an out-of-band trusted sanitized-receipt SHA-256"
            )
        elif hashlib.sha256(path.read_bytes()).hexdigest() != trusted_report_digest:
            errors.append(
                "PASS receipt differs from the out-of-band trusted sanitized-receipt SHA-256"
            )
        trusted_full_digest = (
            trusted_full_report_sha256
            if trusted_full_report_sha256 is not None
            else os.environ.get(TRUSTED_FULL_REPORT_SHA256_ENV, "")
        ).removeprefix("sha256:")
        if len(trusted_full_digest) != 64 or any(
            char not in "0123456789abcdef" for char in trusted_full_digest
        ):
            errors.append(
                "PASS receipt requires an out-of-band trusted protected full-report SHA-256"
            )
        elif report.get("protected_full_report_sha256") != trusted_full_digest:
            errors.append(
                "PASS receipt does not bind the out-of-band trusted protected full-report SHA-256"
            )
        for full_report_field in (
            "protected_full_report_sha256",
            "protected_full_report_deterministic_digest",
        ):
            value = report.get(full_report_field)
            if not isinstance(value, str) or len(value) != 64:
                errors.append(
                    f"PASS receipt lacks protected full-report binding: {full_report_field}"
                )
        if report.get("evaluation_mode") != "OFFICIAL":
            errors.append("W6 release receipt must come from official evaluation mode")
        if report.get("official_evidence_chain_validated") is not True:
            errors.append("W6 release receipt lacks a validated trusted export evidence chain")
        if not isinstance(evidence_chain, Mapping) or any(
            not isinstance(evidence_chain.get(field), str)
            or not all(char in "0123456789abcdef" for char in evidence_chain.get(field, ""))
            or len(evidence_chain.get(field, "")) != 64
            for field in (
                "export_receipt_sha256",
                "prelabel_packet_manifest_sha256",
                "human_review_authority_receipt_sha256",
                "packet_manifest_sha256",
                "packet_manifest_digest",
                "completed_validation_digest",
            )
        ):
            errors.append("W6 release receipt has incomplete evidence-chain digest binding")
        if report.get("evaluation_gate_pass") is not True:
            errors.append("PASS receipt does not assert evaluation_gate_pass")
        if (
            not isinstance(metrics, Mapping)
            or metrics.get("authority_eligibility_accuracy") != 1.0
        ):
            errors.append("PASS receipt does not prove 100% holdout authority eligibility")
        if isinstance(metrics, Mapping):
            for metric_name in _METRIC_NAMES:
                metric_value = metrics.get(metric_name)
                if metric_value is not None and not _finite_number(metric_value):
                    errors.append(f"PASS receipt metric is not finite or null: {metric_name}")
                elif (
                    metric_name in _PASS_REQUIRED_FINITE_METRICS
                    and not _finite_number(metric_value)
                ):
                    errors.append(f"PASS receipt metric must be finite: {metric_name}")

        gate_results = report.get("gate_results")
        inventory_error = _inventory_error(
            gate_results, set(_RELEASE_TARGETS), "gate_results"
        )
        if inventory_error is not None:
            errors.append(inventory_error)

        if canonical_profile is not None:
            if report.get("profile_digest") != canonical_digest(canonical_profile):
                errors.append("PASS receipt does not bind the canonical W6 evaluation profile")
            if report.get("evaluation_id") != canonical_profile.get("profile_id"):
                errors.append("PASS receipt evaluation_id differs from the canonical profile")
            if report.get("policy_version") != canonical_profile.get("policy_version"):
                errors.append("PASS receipt policy_version differs from the canonical profile")

            dataset_profile = canonical_profile.get("dataset")
            calibration_profile = canonical_profile.get("calibration")
            release_targets = canonical_profile.get("release_targets")
            if not isinstance(dataset_profile, Mapping):
                errors.append("canonical W6 dataset profile must be a mapping")
            elif isinstance(dataset, Mapping):
                if dataset.get("dataset_id") != dataset_profile.get("dataset_id"):
                    errors.append("PASS receipt dataset_id differs from the canonical profile")
                if dataset.get("dataset_version") != dataset_profile.get("dataset_version"):
                    errors.append("PASS receipt dataset_version differs from the canonical profile")
                digest = dataset.get("digest")
                if (
                    not isinstance(digest, str)
                    or len(digest) != 64
                    or any(char not in "0123456789abcdef" for char in digest)
                ):
                    errors.append("PASS receipt dataset digest must be a lowercase SHA-256")
                count_minima = {
                    "proof_total_split_group_count": "minimum_total_samples",
                    "proof_calibration_split_group_count": "minimum_calibration_samples",
                    "proof_holdout_split_group_count": "minimum_holdout_samples",
                    "retrieval_total_count": "minimum_retrieval_samples",
                    "retrieval_calibration_count": "minimum_calibration_retrieval_samples",
                    "retrieval_holdout_count": "minimum_holdout_retrieval_samples",
                    "metric_binding_holdout_count": "minimum_metric_binding_samples",
                }
                for count_field, profile_field in count_minima.items():
                    if not _count_at_least(
                        dataset.get(count_field), dataset_profile.get(profile_field, 0)
                    ):
                        errors.append(
                            f"PASS receipt {count_field} is below canonical {profile_field}"
                        )
                count_fields = tuple(count_minima) + (
                    "sample_count",
                    "calibration_count",
                    "holdout_count",
                )
                if all(
                    isinstance(dataset.get(field), int)
                    and not isinstance(dataset.get(field), bool)
                    for field in count_fields
                ):
                    if dataset["proof_total_split_group_count"] != (
                        dataset["proof_calibration_split_group_count"]
                        + dataset["proof_holdout_split_group_count"]
                    ):
                        errors.append("PASS receipt proof split-group counts do not sum to total")
                    if dataset["retrieval_total_count"] != (
                        dataset["retrieval_calibration_count"]
                        + dataset["retrieval_holdout_count"]
                    ):
                        errors.append("PASS receipt retrieval split counts do not sum to total")
                    if dataset["metric_binding_holdout_count"] > dataset["holdout_count"]:
                        errors.append("PASS receipt metric-binding support exceeds holdout identities")

            if not isinstance(calibration_profile, Mapping):
                errors.append("canonical W6 calibration profile must be a mapping")
            elif isinstance(calibration, Mapping):
                expected_calibration = {
                    "method": calibration_profile.get("method"),
                    "status": "FIT_ON_CALIBRATION_APPLIED_TO_HOLDOUT",
                    "fit_split": "proof_split:calibration",
                    "apply_split": "proof_split:holdout",
                    "active_threshold": None,
                }
                for field, expected in expected_calibration.items():
                    if calibration.get(field) != expected:
                        errors.append(
                            f"PASS receipt calibration {field} differs from canonical evaluation"
                        )
                for count_field in (
                    "fit_sample_count",
                    "fit_row_count",
                    "holdout_sample_count",
                    "holdout_row_count",
                ):
                    if (
                        not isinstance(calibration.get(count_field), int)
                        or isinstance(calibration.get(count_field), bool)
                        or calibration[count_field] < 0
                    ):
                        errors.append(
                            f"PASS receipt calibration {count_field} must be a nonnegative integer"
                        )
                if isinstance(dataset, Mapping) and all(
                    isinstance(calibration.get(field), int)
                    and not isinstance(calibration.get(field), bool)
                    for field in (
                        "fit_sample_count",
                        "fit_row_count",
                        "holdout_sample_count",
                        "holdout_row_count",
                    )
                ):
                    if calibration["fit_sample_count"] != dataset.get("calibration_count"):
                        errors.append("PASS receipt calibration identity count is inconsistent")
                    if calibration["holdout_sample_count"] != dataset.get("holdout_count"):
                        errors.append("PASS receipt holdout identity count is inconsistent")
                    if calibration["fit_row_count"] < calibration["fit_sample_count"]:
                        errors.append("PASS receipt fit rows are fewer than fit identities")
                    if calibration["holdout_row_count"] < calibration["holdout_sample_count"]:
                        errors.append("PASS receipt holdout rows are fewer than holdout identities")
                    if (
                        calibration["fit_row_count"] + calibration["holdout_row_count"]
                        != dataset.get("sample_count")
                    ):
                        errors.append("PASS receipt calibration row counts do not sum to dataset")

            if not isinstance(release_targets, Mapping):
                errors.append("canonical W6 release_targets must be a mapping")
            elif isinstance(gate_results, Mapping) and isinstance(metrics, Mapping):
                for target_name, (metric_name, direction) in _RELEASE_TARGETS.items():
                    gate = gate_results.get(target_name)
                    if not isinstance(gate, Mapping):
                        continue
                    inventory_error = _inventory_error(
                        gate, _GATE_RESULT_KEYS, f"gate_results.{target_name}"
                    )
                    if inventory_error is not None:
                        errors.append(inventory_error)
                        continue
                    threshold = release_targets.get(target_name)
                    expected_threshold = None if threshold is None else float(threshold)
                    value = metrics.get(metric_name)
                    if gate.get("metric") != metric_name:
                        errors.append(f"gate {target_name} metric binding is invalid")
                    if gate.get("direction") != direction:
                        errors.append(f"gate {target_name} direction is invalid")
                    if gate.get("threshold") != expected_threshold:
                        errors.append(f"gate {target_name} threshold differs from canonical profile")
                    if gate.get("value") != value:
                        errors.append(f"gate {target_name} value differs from its canonical metric")
                    if threshold is None:
                        expected_status = "NOT_GATED"
                    elif not _finite_number(value):
                        expected_status = FAIL
                    elif direction == "minimum":
                        expected_status = PASS if float(value) >= float(threshold) else FAIL
                    else:
                        expected_status = PASS if float(value) <= float(threshold) else FAIL
                    if gate.get("status") != expected_status:
                        errors.append(f"gate {target_name} status is not recomputed correctly")
                    if threshold is not None and expected_status != PASS:
                        errors.append(f"PASS receipt fails canonical release target: {target_name}")
    return errors


def main() -> int:
    configured = os.environ.get("APPS_RG_RESUME_GRAPH_W6_ARTIFACT", "").strip()
    artifact = Path(configured) if configured else DEFAULT_ARTIFACT
    if not artifact.is_absolute():
        artifact = REPO_ROOT / artifact
    return finish(
        "APPS-RG-RESUME-GRAPH-W6",
        validate_artifact(artifact),
        fail_closed_env=FAIL_CLOSED_ENV,
    )


if __name__ == "__main__":
    raise SystemExit(main())
