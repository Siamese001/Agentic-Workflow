"""Normalization of sealed adjudicated rows into evaluator rows."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from apps_rg.evals.c03_human_eval.split_policy import PROOF_SPLIT_POLICY_ID
from apps_rg.evals.resume_graph.constants import (
    _ADJUDICATED_EXPORT_SCHEMA,
    _ARTIFACT_SHA256_REF_RE,
    _ROW_SCHEMA,
    _SHA256_RE,
)
from apps_rg.evals.resume_graph.metrics.binding import (
    _receipt_ref,
    _valid_adjudication_ref,
    _valid_review_ref_pair,
)
from apps_rg.evals.resume_graph.reporting import (
    canonical_digest,
    compute_row_content_digest,
)


def _normalize_rows(
    rows: Sequence[Mapping[str, Any]], *, allow_internal_rows: bool
) -> tuple[list[dict[str, Any]], list[str]]:
    normalized: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, source in enumerate(rows, 1):
        if source.get("schema_version") != _ADJUDICATED_EXPORT_SCHEMA:
            if not allow_internal_rows:
                errors.append(f"SOURCE_ROW_{index}:schema_version:SEALED_ADJUDICATED_EXPORT_REQUIRED")
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
                str(item.get("candidate_id", "")) for item in candidates if item.get("selected") is True
            ]
            if selected_ids != [str(source.get("selected_candidate_id", ""))]:
                errors.append(f"SOURCE_ROW_{index}:retrieval_candidates:SELECTED_ID_MISMATCH")
            ranked_ids = [str(item.get("candidate_id", "")) for item in candidates]
            relevance = {
                str(item.get("candidate_id", "")): item.get("relevance_grade") for item in candidates
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
                    errors.append(f"SOURCE_ROW_{index}:retrieval_candidates:path_valid:INVALID")
                if metric_binding not in {"EXACT", "INEXACT", "NOT_APPLICABLE"}:
                    errors.append(f"SOURCE_ROW_{index}:retrieval_candidates:metric_binding:INVALID")
                if type(metric_applicable) is not bool:
                    errors.append(f"SOURCE_ROW_{index}:retrieval_candidates:metric_applicable:INVALID")
                elif (metric_applicable and metric_binding == "NOT_APPLICABLE") or (
                    not metric_applicable and metric_binding != "NOT_APPLICABLE"
                ):
                    errors.append(
                        f"SOURCE_ROW_{index}:retrieval_candidates:METRIC_APPLICABILITY_DISPOSITION_MISMATCH"
                    )
                retrieval_path_validity[candidate_id] = path_valid
                retrieval_metric_bindings[candidate_id] = metric_binding
                retrieval_metric_applicability[candidate_id] = metric_applicable
                if (path_valid is False or metric_binding == "INEXACT") and item.get("relevance_grade") != 0:
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
            errors.append(f"SOURCE_ROW_{index}:metric_applicable:DISPOSITION_MISMATCH")

        authority_eligible = source.get("authority_eligible")
        if authority_eligible not in {"PASS", "FAIL"}:
            errors.append(f"SOURCE_ROW_{index}:authority_eligible:INVALID_FINAL_LABEL")

        system_fields = source.get("system_fields")
        system_fields = dict(system_fields) if isinstance(system_fields, Mapping) else {}
        system_prediction = source.get("system_prediction")
        prediction_mapping = dict(system_prediction) if isinstance(system_prediction, Mapping) else {}
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
        if not isinstance(proof_identity_digest, str) or not _SHA256_RE.fullmatch(proof_identity_digest):
            errors.append(f"SOURCE_ROW_{index}:proof_identity_digest:INVALID_SHA256")
        proof_split_group_digest = source.get("proof_split_group_digest")
        if not isinstance(proof_split_group_digest, str) or not _SHA256_RE.fullmatch(
            proof_split_group_digest
        ):
            errors.append(f"SOURCE_ROW_{index}:proof_split_group_digest:INVALID_SHA256")
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
        if not isinstance(source_content_digest, str) or not _SHA256_RE.fullmatch(source_content_digest):
            errors.append(f"SOURCE_ROW_{index}:content_digest:INVALID_SHA256")
        if source.get("gold_path_semantics") != "system_selected_binding_human_validated":
            errors.append(f"SOURCE_ROW_{index}:gold_path_semantics:INVALID")
        leakage_ref = source.get("leakage_check_ref")
        if not isinstance(leakage_ref, str) or not _ARTIFACT_SHA256_REF_RE.fullmatch(leakage_ref):
            errors.append(f"SOURCE_ROW_{index}:leakage_check_ref:INVALID_DIGEST_BOUND_ARTIFACT")
        if type(proof_label) is bool and source.get("human_score") != float(proof_label):
            errors.append(f"SOURCE_ROW_{index}:human_score:DISAGREES_WITH_PROOF_LABEL")
        frontier_metadata = source.get("candidate_frontier_metadata")
        frontier_metadata = dict(frontier_metadata) if isinstance(frontier_metadata, Mapping) else {}
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
            "retrieval_query_content_digest": source.get("retrieval_query_content_digest"),
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
            "judged_top_count": source.get("judged_top_count", frontier_metadata.get("judged_top_count")),
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
            "claim_entailment_label": (entailment_grade >= 2 if isinstance(entailment_grade, int) else None),
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
                str(ref.get("reviewer_id_hash") or "") for ref in reviewer_refs if isinstance(ref, Mapping)
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
            if not isinstance(retrieval_reviewers, list) or not _valid_review_ref_pair(retrieval_reviewers):
                errors.append(f"SOURCE_ROW_{index}:retrieval_reviewer_refs:INVALID_RECEIPTS")
            if not _valid_adjudication_ref(retrieval_adjudication):
                errors.append(f"SOURCE_ROW_{index}:retrieval_adjudication_ref:INVALID_RECEIPT")
        row["content_digest"] = compute_row_content_digest(row)
        normalized.append(row)
    return normalized, errors
