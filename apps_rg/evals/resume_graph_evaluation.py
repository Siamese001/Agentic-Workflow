"""Compatibility facade for deterministic, fail-closed resume-graph evaluation.

The implementation lives under :mod:`apps_rg.evals.resume_graph`. Calibration
remains offline, runtime thresholds are never mutated, and missing or invalid
human evidence remains non-pass.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any, Mapping, Sequence

from apps_rg.evals.c03_human_eval._io import (
    controlled_path_error,
    digest_matches,
    private_path_error,
    repo_root_from_module,
    stable_digest,
)
from apps_rg.evals.c03_human_eval.export import COMPLETED_LABEL_FILES
from apps_rg.evals.c03_human_eval.packet import MANIFEST_SCHEMA
from apps_rg.evals.c03_human_eval.validation import validate_completed_packet
from apps_rg.evals.resume_graph.constants import (
    _ADJUDICATED_EXPORT_RECEIPT_SCHEMA,
    _METRIC_NAMES,  # noqa: F401 - compatibility export used by the CI checker
    _RELEASE_TARGETS,  # noqa: F401 - compatibility export used by the CI checker
    FAIL,
    INSUFFICIENT,
    PASS,
    UNKNOWN,
)
from apps_rg.evals.resume_graph.dataset import (
    _load_jsonl_bytes,
    _mapping,
    load_jsonl,
)
from apps_rg.evals.resume_graph.gates import (
    _future_release_candidate_summary,
    _gate_results,
    _label_summary,
    _select_candidate_threshold,
)
from apps_rg.evals.resume_graph.metrics.calibration import (
    brier_score,
    expected_calibration_error,
    fit_isotonic_pav,
)
from apps_rg.evals.resume_graph.metrics.proof import (
    _proof_split,
    _proof_split_group,
    _retrieval_split,
    _unique_proof_context_rows,
    _unique_proof_rows,
)
from apps_rg.evals.resume_graph.metrics.retrieval import (
    _mean,
    ndcg_at_k,
    recall_at_k,
    reciprocal_rank,
)
from apps_rg.evals.resume_graph.models import (
    EvaluationDataError,
    IsotonicModel,
)
from apps_rg.evals.resume_graph.normalization import _normalize_rows
from apps_rg.evals.resume_graph.reporting import (
    _base_report,
    _report_digest,
    build_sanitized_ci_receipt,
    canonical_digest,
    compute_row_content_digest,
    report_digest_is_valid,
)
from apps_rg.evals.resume_graph.validation import _validate_dataset


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
            raise EvaluationDataError(f"{candidate}: must be owned by the current user")
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
    trusted_prelabel_digest = trusted_prelabel_packet_manifest_sha256.removeprefix("sha256:")
    trusted_authority_digest = trusted_human_review_authority_receipt_sha256.removeprefix("sha256:")
    errors: list[str] = []
    for label, path, directory in (
        ("DATASET", dataset_path, False),
        ("TRUSTED_EXPORT_RECEIPT", export_receipt_path, False),
        ("HUMAN_REVIEW_AUTHORITY_RECEIPT", authority_receipt_path, False),
        ("PACKET_ROOT", packet_dir, True),
        ("LABELS_ROOT", labels_dir, True),
    ):
        boundary_error = controlled_path_error(Path(path), repo_root=repo_root_from_module())
        if boundary_error is not None:
            errors.append(f"{label}_CONTROL_BOUNDARY_INVALID:{boundary_error}")
            continue
        privacy_error = private_path_error(path, directory=directory)
        if privacy_error is not None:
            errors.append(f"{label}_PRIVACY_INVALID:{privacy_error}")
            continue
        if directory:
            try:
                members = sorted(Path(path).rglob("*"), key=lambda candidate: str(candidate))
            except OSError as exc:
                errors.append(f"{label}_CONTROL_BOUNDARY_UNREADABLE:{exc}")
                continue
            for member in members:
                member_error = controlled_path_error(member, repo_root=repo_root_from_module())
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
    if receipt.get("human_review_authority_receipt_sha256") != trusted_authority_digest:
        errors.append("EXPORT_RECEIPT_HUMAN_REVIEW_AUTHORITY_SHA256_MISMATCH")
    if any(row.get("prelabel_packet_manifest_sha256") != trusted_prelabel_digest for row in rows):
        errors.append("DATASET_PRELABEL_PACKET_MANIFEST_SHA256_MISMATCH")
    if any(row.get("human_review_authority_receipt_sha256") != trusted_authority_digest for row in rows):
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
        or source_freeze_receipt_digest != manifest.get("source_freeze_receipt_digest")
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
                source_freeze_receipt_digest if isinstance(source_freeze_receipt_digest, str) else None
            ),
            trusted_prelabel_packet_manifest_sha256=trusted_prelabel_digest,
            human_review_authority_receipt=authority_receipt_path,
            trusted_human_review_authority_receipt_sha256=(trusted_authority_digest),
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
    if receipt.get("completed_label_file_sha256") != dict(sorted(observed_label_files.items())):
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
            f"artifact://sealed_internal/completed_packet_leakage_check.v1.json#sha256:{leakage_sha}"
        )
        if any(row.get("leakage_check_ref") != expected_ref for row in rows):
            errors.append("DATASET_COMPLETED_LEAKAGE_REFERENCE_MISMATCH")
    return sorted(set(errors)), evidence


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
                raise EvaluationDataError(f"DATASET_PRIVACY_INVALID:{privacy_error}")
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
    source_rows = sorted((dict(row) for row in rows), key=lambda row: str(row.get("sample_id", "")))
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
            trusted_prelabel_packet_manifest_sha256=(trusted_prelabel_packet_manifest_sha256),
            human_review_authority_receipt_path=(human_review_authority_receipt_path),
            trusted_human_review_authority_receipt_sha256=(trusted_human_review_authority_receipt_sha256),
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
    sorted_rows, normalization_errors = _normalize_rows(source_rows, allow_internal_rows=allow_internal_rows)
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
    holdout_row_probabilities = model.predict([float(row["proof_score_raw"]) for row in holdout_rows])
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
    pooled_recall_hits_by_k: dict[int, int] = dict.fromkeys(k_values, 0)
    pooled_recall_relevant_by_k: dict[int, int] = dict.fromkeys(k_values, 0)
    ndcg_values_by_k: dict[int, list[float]] = {k: [] for k in k_values}
    rr_values: list[float] = []
    path_values = [float(row["path_accuracy_label"]) for row in holdout_identity_rows]
    margins = [float(row["selection_margin"]) for row in holdout_context_rows]
    entailment_predictions = [row.get("claim_entailment_prediction") for row in holdout_identity_rows]
    entailment_labels = [bool(row["claim_entailment_label"]) for row in holdout_identity_rows]
    entailment_grades = [int(row["claim_entailment_grade"]) for row in holdout_identity_rows]
    applicable_metric_rows = [row for row in holdout_identity_rows if row.get("metric_applicable") is True]
    metric_predictions = [row.get("metric_binding_prediction") for row in applicable_metric_rows]
    metric_labels = [bool(row["metric_binding_label"]) for row in applicable_metric_rows]
    target_relevance_grades = [int(row["target_relevance_grade"]) for row in holdout_context_rows]
    authority_holdout_values = [row["authority_eligible"] == PASS for row in holdout_identity_rows]

    retrieval_holdout_rows = [
        row
        for row in sorted_rows
        if row.get("ranked_candidate_ids") is not None and _retrieval_split(row) == "holdout"
    ]
    retrieval_by_sample: dict[str, dict[str, Any]] = {}
    for row in retrieval_holdout_rows:
        ranked = list(row["ranked_candidate_ids"])
        explicit_ranks = list(row.get("retrieval_ranks") or range(1, len(ranked) + 1))
        relevance = {key: float(value) for key, value in row["relevance_labels"].items()}
        relevant_ids = {candidate_id for candidate_id, score in relevance.items() if score >= positive_floor}
        row_retrieval_by_k: dict[str, dict[str, float]] = {}
        for k in k_values:
            ranked_at_k = [candidate_id for candidate_id, rank in zip(ranked, explicit_ranks) if rank <= k]
            recall_value = recall_at_k(ranked_at_k, relevance, k, positive_floor=positive_floor)
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
                "recall_at_k": (retrieval_result["recall_at_k"] if retrieval_result is not None else None),
                "ndcg_at_k": (retrieval_result["ndcg_at_k"] if retrieval_result is not None else None),
                "retrieval_metrics_by_k": (
                    retrieval_result["retrieval_metrics_by_k"] if retrieval_result is not None else None
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
    pooled_recall_by_k = {k: pooled_recall_hits_by_k[k] / pooled_recall_relevant_by_k[k] for k in k_values}
    metrics: dict[str, float | None] = {
        "recall_at_k": pooled_recall_by_k[gate_k],
        "ndcg_at_k": _mean(ndcg_values),
        "mrr": _mean(rr_values),
        "authority_eligibility_accuracy": _mean([float(value) for value in authority_holdout_values]),
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
        "proof_confidence_candidate_minimum": future_release_summary["minimum_calibrated_confidence"],
    }
    for k in k_values:
        metrics[f"recall_at_{k}"] = _mean(recall_values_by_k[k])
        metrics[f"pooled_recall_at_{k}"] = pooled_recall_by_k[k]
        metrics[f"ndcg_at_{k}"] = _mean(ndcg_values_by_k[k])
    metrics.update(_label_summary("claim_entailment", entailment_labels, entailment_predictions))
    metrics["claim_entailment_mean_grade"] = _mean([float(grade) for grade in entailment_grades])
    metrics.update(_label_summary("metric_binding", metric_labels, metric_predictions))
    metrics["target_relevance_mean_grade"] = _mean([float(grade) for grade in target_relevance_grades])

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
                {str(row["target_profile_id"]) for row in sorted_rows if _proof_split(row) == split}
            )
            for split in ("calibration", "holdout")
        },
        "proof_sections_by_split": {
            split: sorted({str(row["section_id"]) for row in sorted_rows if _proof_split(row) == split})
            for split in ("calibration", "holdout")
        },
        "retrieval_target_profiles_by_split": {
            split: sorted(
                {
                    str(row["target_profile_id"])
                    for row in sorted_rows
                    if row.get("ranked_candidate_ids") is not None and _retrieval_split(row) == split
                }
            )
            for split in ("calibration", "holdout")
        },
        "retrieval_sections_by_split": {
            split: sorted(
                {
                    str(row["section_id"])
                    for row in sorted_rows
                    if row.get("ranked_candidate_ids") is not None and _retrieval_split(row) == split
                }
            )
            for split in ("calibration", "holdout")
        },
        "metric_binding_holdout_count": len(metric_labels),
        "authority_eligible_proof_holdout_identity_count": sum(authority_holdout_values),
        "proof_calibration_row_count": len(calibration_rows),
        "proof_calibration_identity_count": len(calibration_identity_rows),
        "proof_holdout_row_count": len(holdout_rows),
        "proof_holdout_identity_count": len(holdout_identity_rows),
        "proof_holdout_context_count": len(holdout_context_rows),
        "proof_total_split_group_count": len({_proof_split_group(row) for row in sorted_rows}),
        "proof_calibration_split_group_count": len({_proof_split_group(row) for row in calibration_rows}),
        "proof_holdout_split_group_count": len({_proof_split_group(row) for row in holdout_rows}),
        "retrieval_total_count": sum(row.get("ranked_candidate_ids") is not None for row in sorted_rows),
        "retrieval_calibration_count": sum(
            row.get("ranked_candidate_ids") is not None and _retrieval_split(row) == "calibration"
            for row in sorted_rows
        ),
        "retrieval_holdout_count": len(recall_values),
    }
    report["metrics"] = metrics
    report["target_relevance_summary"] = {
        "authoritative": False,
        "mean_grade": metrics["target_relevance_mean_grade"],
        "grade_distribution": {str(grade): target_relevance_grades.count(grade) for grade in range(4)},
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
