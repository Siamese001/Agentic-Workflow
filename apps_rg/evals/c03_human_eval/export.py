"""Create the sealed adjudicated dataset consumed by W6 evaluation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ._io import (
    controlled_path_error,
    file_digest,
    read_json,
    read_jsonl,
    record_with_digest,
    repo_root_from_module,
    path_within,
    paths_refer_same,
    stable_digest,
    write_json,
    write_jsonl,
)
from .packet import FULL_UNIVERSE_JUDGING_SCOPE, INTERNAL_FILES, REVIEWER_FILES
from .validation import validate_completed_packet

EXPORT_SCHEMA = "apps_rg.c03_human_eval.adjudicated_evaluation.v1"
DEFAULT_EXPORT_PATH = Path("sealed_internal/adjudicated_evaluation.v1.jsonl")
DEFAULT_EXPORT_RECEIPT_SUFFIX = ".receipt.json"
COMPLETED_LABEL_FILES = (
    "claim_reviews.jsonl",
    "retrieval_reviews.jsonl",
    "w9_reviews.jsonl",
    "adjudications.jsonl",
)


class AdjudicatedExportError(ValueError):
    """Completed labels cannot be exported without weakening their evidence chain."""


def export_adjudicated_evaluation(
    *,
    packet_dir: Path,
    labels_dir: Path,
    out_path: Path | None = None,
    receipt_path: Path | None = None,
    require_w9: bool = False,
    trusted_source_freeze_receipt_digest: str | None = None,
    trusted_prelabel_packet_manifest_sha256: str | None = None,
    human_review_authority_receipt: dict[str, Any] | Path | None = None,
    trusted_human_review_authority_receipt_sha256: str | None = None,
    allow_test_only_provenance: bool = False,
) -> dict[str, Any]:
    """Export 282 claim rows after strict completed-packet validation passes."""

    if not allow_test_only_provenance:
        repository = repo_root_from_module()
        for label, controlled in (
            ("packet", packet_dir),
            ("completed labels", labels_dir),
            ("human-review authority receipt", human_review_authority_receipt),
        ):
            if isinstance(controlled, Path):
                path_error = controlled_path_error(controlled, repo_root=repository)
                if path_error:
                    raise AdjudicatedExportError(f"official {label} {path_error}")
        prospective_output = out_path or (
            Path(packet_dir) / DEFAULT_EXPORT_PATH
        )
        prospective_receipt = receipt_path or prospective_output.with_name(
            prospective_output.name + DEFAULT_EXPORT_RECEIPT_SUFFIX
        )
        for label, controlled in (
            ("export output", prospective_output),
            ("export receipt", prospective_receipt),
        ):
            path_error = controlled_path_error(controlled, repo_root=repository)
            if path_error:
                raise AdjudicatedExportError(f"official {label} {path_error}")
        if paths_refer_same(prospective_output, prospective_receipt):
            raise AdjudicatedExportError(
                "official export output and receipt must be distinct"
            )
        if path_within(prospective_output, labels_dir) or path_within(
            prospective_receipt, labels_dir
        ):
            raise AdjudicatedExportError(
                "official export outputs must not overwrite or enter completed labels"
            )
        if isinstance(human_review_authority_receipt, Path) and (
            paths_refer_same(prospective_output, human_review_authority_receipt)
            or paths_refer_same(prospective_receipt, human_review_authority_receipt)
        ):
            raise AdjudicatedExportError(
                "official export outputs must not alias the authority receipt"
            )

    validation = validate_completed_packet(
        packet_dir,
        labels_dir,
        require_w9=require_w9,
        trusted_source_freeze_receipt_digest=trusted_source_freeze_receipt_digest,
        trusted_prelabel_packet_manifest_sha256=(
            trusted_prelabel_packet_manifest_sha256
        ),
        human_review_authority_receipt=human_review_authority_receipt,
        trusted_human_review_authority_receipt_sha256=(
            trusted_human_review_authority_receipt_sha256
        ),
        allow_test_only_provenance=allow_test_only_provenance,
    )
    if not validation["pass"]:
        raise AdjudicatedExportError(
            "completed packet validation failed: " + "; ".join(validation["errors"][:10])
        )
    packet = packet_dir.resolve()
    manifest = read_json(packet / "packet_manifest.json")
    claims = read_jsonl(packet / REVIEWER_FILES[0])
    claim_mappings = {
        str(row["item_id"]): row for row in read_jsonl(packet / INTERNAL_FILES[0])
    }
    retrieval_mappings = read_jsonl(packet / INTERNAL_FILES[1])
    retrieval_by_claim = {
        (str(row["case_id"]), str(row["claim_unit_id"])): row
        for row in retrieval_mappings
    }
    all_claim_reviews: dict[str, list[dict[str, Any]]] = {}
    for row in read_jsonl(labels_dir / "claim_reviews.jsonl"):
        all_claim_reviews.setdefault(str(row["item_id"]), []).append(row)
    retrieval_reviews: dict[str, list[dict[str, Any]]] = {}
    if (labels_dir / "retrieval_reviews.jsonl").is_file():
        for row in read_jsonl(labels_dir / "retrieval_reviews.jsonl"):
            retrieval_reviews.setdefault(str(row["item_id"]), []).append(row)
    adjudications = {
        (str(row["item_type"]), str(row["item_id"])): row
        for row in read_jsonl(labels_dir / "adjudications.jsonl")
    }

    graph_digest = str(manifest.get("graph_digest") or "")
    policy_digest = str(manifest.get("policy_digest") or "")
    if len(graph_digest) != 64 or len(policy_digest) != 64:
        raise AdjudicatedExportError("graph_digest and policy_digest must be nonempty SHA-256 values")
    prelabel_checks = dict(validation.get("prelabel_validation", {}).get("checks") or {})
    leakage_required = {
        "reviewer_payloads_blinded",
        "identity_conservation",
        "target_case_retrieval_split_disjoint",
        "target_input_retrieval_split_disjoint",
        "proof_identity_split_disjoint",
        "proof_split_deterministic",
        "proof_split_strata_complete",
        "retrieval_split_strata_complete",
        "leakage_checks_pass",
    }
    if any(prelabel_checks.get(check) is not True for check in leakage_required):
        raise AdjudicatedExportError("completed packet lacks a passing split/blinding/leakage proof")
    leakage_receipt = record_with_digest(
        {
            "schema_version": "apps_rg.c03_human_eval.completed_leakage_check.v1",
            "packet_id": str(manifest["packet_id"]),
            "packet_manifest_digest": str(manifest["manifest_digest"]),
            "prelabel_packet_manifest_sha256": str(
                trusted_prelabel_packet_manifest_sha256
            ),
            "human_review_authority_receipt_sha256": str(
                trusted_human_review_authority_receipt_sha256
            ),
            "status": "PASS",
            "unknown_is_pass": False,
            "checks": {check: True for check in sorted(leakage_required)},
            "completed_validation_checks": dict(validation.get("checks") or {}),
        },
        "record_digest",
    )
    leakage_path = packet / "sealed_internal/completed_packet_leakage_check.v1.json"
    write_json(leakage_path, leakage_receipt)
    leakage_ref = (
        "artifact://sealed_internal/completed_packet_leakage_check.v1.json"
        f"#sha256:{file_digest(leakage_path)}"
    )
    label_policy = (
        "c03_claim_proof_v1@sha256:" + str(manifest["rubric_digests"]["claim"])
    )

    exported: list[dict[str, Any]] = []
    for claim in claims:
        item_id = str(claim["item_id"])
        mapping = claim_mappings[item_id]
        adjudication = adjudications[("claim", item_id)]
        final_labels = dict(adjudication["final_labels"])
        primary_reviews = sorted(
            all_claim_reviews[item_id], key=lambda row: str(row["review_id"])
        )
        system_fields = dict(mapping.get("system_fields") or {})
        target_context = dict(claim.get("target_context") or {})
        proof_score_source_field = (
            "proof_score_raw"
            if "proof_score_raw" in system_fields
            else "proof_strength_raw"
        )
        binding = dict(mapping.get("binding") or {})
        claim_metric_applicable = bool(mapping["metric_applicable"])
        if claim_metric_applicable is not any(
            value is not None and str(value).strip() != ""
            for field in (
                "metric_outcome_id",
                "normalized_metric_signature",
                "metric_text",
                "metric_value",
                "metric_unit",
            )
            for value in (binding.get(field),)
        ):
            raise AdjudicatedExportError(
                f"{item_id}: claim metric applicability binding mismatch"
            )
        if (
            claim_metric_applicable
            and final_labels.get("metric_binding") not in {"EXACT", "INEXACT"}
        ) or (
            not claim_metric_applicable
            and final_labels.get("metric_binding") != "NOT_APPLICABLE"
        ):
            raise AdjudicatedExportError(
                f"{item_id}: claim metric label disagrees with sealed applicability"
            )
        retrieval_mapping = retrieval_by_claim.get(
            (str(mapping["case_id"]), str(mapping["claim_unit_id"]))
        )
        retrieval_payload: list[dict[str, Any]] | None = None
        retrieval_refs: list[dict[str, str]] = []
        retrieval_adjudication_ref: dict[str, str] | None = None
        candidate_frontier_metadata: dict[str, Any] | None = None
        candidate_universe_size: int | None = None
        frontier_k: int | None = None
        frontier_exhausted: bool | None = None
        judged_top_count: int | None = None
        judged_candidate_count: int | None = None
        candidate_judging_scope: str | None = None
        selected_audit_extra: dict[str, Any] | None = None
        retrieval_recall_scope: str | None = None
        retrieval_query_id: str | None = None
        retrieval_query_content_digest: str | None = None
        if retrieval_mapping is not None:
            if retrieval_mapping.get("retrieval_split") != mapping.get("retrieval_split"):
                raise AdjudicatedExportError(
                    f"{item_id}: claim/query retrieval_split mismatch"
                )
            query_id = str(retrieval_mapping["query_id"])
            retrieval_query_id = query_id
            retrieval_query_content_digest = str(retrieval_mapping["content_digest"])
            candidate_frontier_metadata = dict(
                retrieval_mapping["candidate_frontier_metadata"]
            )
            candidate_universe_size = int(
                candidate_frontier_metadata["candidate_universe_size"]
            )
            frontier_k = int(candidate_frontier_metadata["frontier_k"])
            frontier_exhausted = bool(candidate_frontier_metadata["frontier_exhausted"])
            judged_top_count = int(candidate_frontier_metadata["judged_top_count"])
            judged_candidate_count = int(
                candidate_frontier_metadata["judged_candidate_count"]
            )
            candidate_judging_scope = str(
                candidate_frontier_metadata["candidate_judging_scope"]
            )
            if (
                candidate_judging_scope != FULL_UNIVERSE_JUDGING_SCOPE
                or judged_candidate_count != candidate_universe_size
                or len(retrieval_mapping["candidates"]) != candidate_universe_size
            ):
                raise AdjudicatedExportError(
                    f"{item_id}: retrieval labels do not cover the full finite universe"
                )
            selected_audit_extra = (
                dict(retrieval_mapping["selected_audit_extra"])
                if retrieval_mapping.get("selected_audit_extra") is not None
                else None
            )
            retrieval_recall_scope = FULL_UNIVERSE_JUDGING_SCOPE
            retrieval_adjudication = adjudications[("retrieval", query_id)]
            relevance_rows = {
                str(row["candidate_blind_id"]): row
                for row in retrieval_adjudication["final_labels"]["candidates"]
            }
            retrieval_payload = []
            for candidate in sorted(
                retrieval_mapping["candidates"],
                key=lambda row: (int(row["rank"]), str(row["candidate_id"])),
            ):
                blind_id = str(candidate["candidate_blind_id"])
                labels = relevance_rows[blind_id]
                candidate_metric_applicable = bool(candidate["metric_applicable"])
                if (
                    candidate_metric_applicable
                    and labels["metric_binding"] not in {"EXACT", "INEXACT"}
                ) or (
                    not candidate_metric_applicable
                    and labels["metric_binding"] != "NOT_APPLICABLE"
                ):
                    raise AdjudicatedExportError(
                        f"{item_id}/{blind_id}: metric label disagrees with sealed applicability"
                    )
                if (
                    int(labels["relevance_grade"]) != 0
                    and (
                        labels["path_valid"] is False
                        or labels["metric_binding"] == "INEXACT"
                    )
                ):
                    raise AdjudicatedExportError(
                        f"{item_id}/{blind_id}: invalid retrieval proof cannot be relevant"
                    )
                retrieval_payload.append(
                    {
                        "candidate_id": str(candidate["candidate_id"]),
                        "rank": int(candidate["rank"]),
                        "selected": bool(candidate["selected"]),
                        "relevance_grade": int(labels["relevance_grade"]),
                        "path_valid": bool(labels["path_valid"]),
                        "metric_binding": str(labels["metric_binding"]),
                        "metric_applicable": candidate_metric_applicable,
                        "system_fields": dict(candidate.get("system_fields") or {}),
                    }
                )
            retrieval_refs = [
                {
                    "review_id": str(row["review_id"]),
                    "reviewer_id_hash": str(row["reviewer_id_hash"]),
                    "reviewer_identity_ref": str(row["reviewer_identity_ref"]),
                    "review_digest": str(row["record_digest"]),
                }
                for row in sorted(
                    retrieval_reviews[query_id], key=lambda row: str(row["review_id"])
                )
            ]
            retrieval_adjudication_ref = {
                "adjudication_id": str(retrieval_adjudication["adjudication_id"]),
                "record_digest": str(retrieval_adjudication["record_digest"]),
            }
        proof_split = str(mapping["proof_split"])
        raw_retrieval_split = str(mapping["retrieval_split"])
        retrieval_split = (
            "holdout" if raw_retrieval_split == "release_holdout" else raw_retrieval_split
        )
        row: dict[str, Any] = {
            "schema_version": EXPORT_SCHEMA,
            "dataset_id": str(manifest["dataset_id"]),
            "dataset_version": str(manifest["dataset_version"]),
            "sample_id": item_id,
            "split": proof_split,
            "proof_split": proof_split,
            "retrieval_split": retrieval_split,
            "proof_identity_digest": str(mapping["proof_identity_digest"]),
            "proof_split_group_digest": str(
                mapping["proof_split_group_digest"]
            ),
            "proof_split_policy_id": str(mapping["proof_split_policy_id"]),
            "proof_split_policy_salt": int(mapping["proof_split_policy_salt"]),
            "target_profile_id": str(mapping["target_profile_id"]),
            "case_id": str(mapping["case_id"]),
            "target_jd_digest": str(target_context.get("jd_digest") or ""),
            "target_brief_digest": str(target_context.get("brief_digest") or ""),
            "run_id": str(mapping["run_id"]),
            "section_id": str(mapping["section_id"]),
            "claim_unit_id": str(mapping["claim_unit_id"]),
            "representation_mode": str(claim["representation_mode"]),
            "visible_claim_text": str(claim["visible_claim_text"]),
            "content_digest": str(claim["content_digest"]),
            "label_source": "human_semantic_review",
            "label_policy": label_policy,
            "human_score": 1.0 if final_labels["overall_proof_valid"] is True else 0.0,
            "authority_eligible": str(final_labels["authority_eligible"]),
            "claim_entailment_grade": int(final_labels["claim_entailment_grade"]),
            "path_accuracy": bool(final_labels["path_accuracy"]),
            "metric_binding": str(final_labels["metric_binding"]),
            "target_relevance_grade": int(final_labels["target_relevance_grade"]),
            "overall_proof_valid": bool(final_labels["overall_proof_valid"]),
            "metric_applicable": claim_metric_applicable,
            "reviewer_refs": [
                {
                    "review_id": str(review["review_id"]),
                    "reviewer_id_hash": str(review["reviewer_id_hash"]),
                    "reviewer_identity_ref": str(review["reviewer_identity_ref"]),
                    "review_digest": str(review["record_digest"]),
                }
                for review in primary_reviews
            ],
            "adjudication_ref": {
                "adjudication_id": str(adjudication["adjudication_id"]),
                "record_digest": str(adjudication["record_digest"]),
            },
            "created_at": str(adjudication["adjudicated_at"]),
            "graph_digest": graph_digest,
            "policy_digest": policy_digest,
            "leakage_check_ref": leakage_ref,
            "leakage_check_status": "PASS",
            "allocation_plan_digest": str(mapping["allocation_plan_digest"]),
            "prelabel_packet_manifest_sha256": str(
                trusted_prelabel_packet_manifest_sha256
            ),
            "human_review_authority_receipt_sha256": str(
                trusted_human_review_authority_receipt_sha256
            ),
            "selected_candidate_id": str(mapping["candidate_id"]),
            "gold_path_ids": list(binding.get("graph_path_ids") or []),
            "gold_path_semantics": "system_selected_binding_human_validated",
            "proof_score_raw": system_fields.get(proof_score_source_field),
            "proof_score_source_field": proof_score_source_field,
            "system_prediction": system_fields.get("system_prediction"),
            "selection_margin": system_fields.get("selection_margin"),
            "system_fields": system_fields,
            "retrieval_candidates": retrieval_payload,
            "retrieval_query_id": retrieval_query_id,
            "retrieval_query_content_digest": retrieval_query_content_digest,
            "candidate_frontier_metadata": candidate_frontier_metadata,
            "candidate_universe_size": candidate_universe_size,
            "frontier_k": frontier_k,
            "frontier_exhausted": frontier_exhausted,
            "judged_top_count": judged_top_count,
            "judged_candidate_count": judged_candidate_count,
            "candidate_judging_scope": candidate_judging_scope,
            "selected_audit_extra": selected_audit_extra,
            "retrieval_recall_scope": retrieval_recall_scope,
            "retrieval_reviewer_refs": retrieval_refs,
            "retrieval_adjudication_ref": retrieval_adjudication_ref,
        }
        exported.append(record_with_digest(row, "record_digest"))
    exported.sort(key=lambda row: str(row["sample_id"]))
    destination = (out_path or (packet / DEFAULT_EXPORT_PATH)).resolve()
    if not allow_test_only_provenance:
        destination_error = controlled_path_error(
            out_path or (packet / DEFAULT_EXPORT_PATH),
            repo_root=repo_root_from_module(),
        )
        if destination_error:
            raise AdjudicatedExportError(f"official export output {destination_error}")
    row_count = write_jsonl(destination, exported)
    manifest_path = packet / "packet_manifest.json"
    top_checksum_path = packet / "SHA256SUMS"
    label_file_sha256 = {
        name: file_digest(labels_dir.resolve() / name)
        for name in COMPLETED_LABEL_FILES
        if (labels_dir.resolve() / name).is_file()
    }
    receipt_destination = (
        receipt_path.resolve()
        if receipt_path is not None
        else destination.with_name(destination.name + DEFAULT_EXPORT_RECEIPT_SUFFIX)
    )
    if not allow_test_only_provenance:
        receipt_error = controlled_path_error(
            receipt_path or receipt_destination,
            repo_root=repo_root_from_module(),
        )
        if receipt_error:
            raise AdjudicatedExportError(
                f"official export receipt {receipt_error}"
            )
    receipt = record_with_digest({
        "schema_version": "apps_rg.c03_human_eval.adjudicated_export_receipt.v1",
        "status": (
            "PASS" if validation.get("official_pass") is True else "PASS_TEST_ONLY"
        ),
        "official_pass": validation.get("official_pass") is True,
        "unknown_is_pass": False,
        "dataset_id": str(manifest["dataset_id"]),
        "dataset_version": str(manifest["dataset_version"]),
        "packet_id": str(manifest["packet_id"]),
        "source_freeze_receipt_digest": str(
            manifest["source_freeze_receipt_digest"]
        ),
        "prelabel_packet_manifest_sha256": str(
            trusted_prelabel_packet_manifest_sha256
        ),
        "human_review_authority_receipt_sha256": str(
            trusted_human_review_authority_receipt_sha256
        ),
        "packet_manifest_digest": str(manifest["manifest_digest"]),
        "packet_manifest_sha256": file_digest(manifest_path),
        "packet_top_level_sha256s_sha256": file_digest(top_checksum_path),
        "completed_validation_digest": stable_digest(validation),
        "completed_validation_status": str(validation["status"]),
        "completed_label_file_sha256": dict(sorted(label_file_sha256.items())),
        "completed_leakage_check_sha256": file_digest(leakage_path),
        "require_w9": require_w9,
        "output_path": str(destination),
        "output_sha256": file_digest(destination),
        "row_count": row_count,
        "claim_rows_by_split": {
            split: sum(1 for row in exported if row["split"] == split)
            for split in ("calibration", "holdout")
        },
        "claim_rows_by_proof_split": {
            split: sum(1 for row in exported if row["proof_split"] == split)
            for split in ("calibration", "holdout")
        },
        "claim_rows_by_retrieval_split": {
            split: sum(1 for row in exported if row["retrieval_split"] == split)
            for split in ("calibration", "holdout")
        },
        "retrieval_bearing_row_count": sum(
            1 for row in exported if row["retrieval_candidates"] is not None
        ),
        "receipt_path": str(receipt_destination),
    }, "record_digest")
    write_json(receipt_destination, receipt)
    return {
        **receipt,
        "receipt_file_sha256": file_digest(receipt_destination),
    }


__all__ = [
    "AdjudicatedExportError",
    "COMPLETED_LABEL_FILES",
    "DEFAULT_EXPORT_RECEIPT_SUFFIX",
    "export_adjudicated_evaluation",
]
