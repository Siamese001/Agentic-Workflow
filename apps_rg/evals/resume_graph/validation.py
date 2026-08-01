"""Fail-closed dataset and row validation."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping, Sequence

from apps_rg.evals.c03_human_eval.split_policy import (
    PROOF_SPLIT_POLICY_ID,
    ProofSplitPolicyError,
    proof_split_for_digest,
)
from apps_rg.evals.resume_graph.constants import (
    _ADJUDICATED_EXPORT_SCHEMA,
    _ROW_SCHEMA,
    _SHA256_RE,
)
from apps_rg.evals.resume_graph.dataset import _mapping
from apps_rg.evals.resume_graph.metrics.proof import (
    _proof_context_identity,
    _proof_identity,
    _proof_split,
    _proof_split_group,
    _retrieval_split,
    _unique_proof_rows,
)
from apps_rg.evals.resume_graph.models import _is_number
from apps_rg.evals.resume_graph.reporting import (
    canonical_digest,
    compute_row_content_digest,
)


def _validate_dataset(rows: Sequence[Mapping[str, Any]], profile: Mapping[str, Any]) -> list[str]:
    dataset_profile = _mapping(profile, "dataset")
    retrieval_profile = _mapping(profile, "retrieval")
    errors: list[str] = []
    if dataset_profile.get("proof_split_policy_id") != PROOF_SPLIT_POLICY_ID:
        errors.append("PROFILE_PROOF_SPLIT_POLICY_ID_MISMATCH")
    if not rows:
        return sorted({*errors, "DATASET_EMPTY"})

    for index, row in enumerate(rows, 1):
        errors.extend(_validate_row(row, dataset_profile, retrieval_profile, index=index))

    sample_ids = [str(row.get("sample_id")) for row in rows]
    content_digests = [str(row.get("content_digest")) for row in rows]
    if len(set(sample_ids)) != len(sample_ids):
        errors.append("DUPLICATE_SAMPLE_ID")
    if len(set(content_digests)) != len(content_digests):
        errors.append("DUPLICATE_CONTENT_DIGEST")

    canonical_exports = [
        row for row in rows if row.get("source_schema_version") == _ADJUDICATED_EXPORT_SCHEMA
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
            proof_split_group_splits.setdefault(_proof_split_group(row), set()).add(str(_proof_split(row)))
        if any(len(splits) != 1 for splits in proof_identity_splits.values()):
            errors.append("PROOF_IDENTITY_CROSSES_CALIBRATION_AND_HOLDOUT")
        if any(len(splits) != 1 for splits in proof_split_group_splits.values()):
            errors.append("PROOF_SPLIT_GROUP_CROSSES_CALIBRATION_AND_HOLDOUT")
        salts = {row.get("proof_split_policy_salt") for row in canonical_exports}
        if len(salts) != 1 or any(
            not isinstance(salt, int) or isinstance(salt, bool) or salt < 0 for salt in salts
        ):
            errors.append("MISSING_OR_MIXED_PROOF_SPLIT_POLICY_SALT")
        else:
            salt = next(iter(salts))
            try:
                if any(
                    proof_split_for_digest(_proof_split_group(row), salt=salt) != _proof_split(row)
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
                    "metric_binding_disposition": row.get("metric_binding_disposition"),
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
                    "claim_entailment_prediction": row.get("claim_entailment_prediction"),
                    "metric_binding_prediction": row.get("metric_binding_prediction"),
                    "target_relevance_grade": row.get("target_relevance_grade"),
                }
            )
            proof_context_signatures.setdefault(context_identity, set()).add(signature)
        if any(len(signatures) != 1 for signatures in proof_context_signatures.values()):
            errors.append("DUPLICATE_PROOF_CONTEXT_HAS_INCONSISTENT_TARGET_OR_PREDICTION_FIELDS")

        proof_reviewer_hashes = {
            str(value) for row in canonical_exports for value in row.get("proof_reviewer_id_hashes") or []
        }
        retrieval_reviewer_hashes = {
            str(value) for row in canonical_exports for value in row.get("retrieval_reviewer_id_hashes") or []
        }
        proof_reviewer_refs = {
            str(value) for row in canonical_exports for value in row.get("proof_reviewer_identity_refs") or []
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
                split_groups.setdefault(str(row.get(field) or ""), set()).add(str(_retrieval_split(row)))
            if "" in split_groups or any(len(splits) != 1 for splits in split_groups.values()):
                errors.append(code)

        retrieval_exports = [row for row in canonical_exports if row.get("ranked_candidate_ids") is not None]
        query_ids = [str(row.get("retrieval_query_id") or "") for row in retrieval_exports]
        query_digests = [str(row.get("retrieval_query_content_digest") or "") for row in retrieval_exports]
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
    calibration_split_group_count = len({_proof_split_group(row) for row in calibration_rows})
    holdout_split_group_count = len({_proof_split_group(row) for row in holdout_rows})
    if unique_split_group_count < minimum_total:
        errors.append(
            f"TOTAL_UNIQUE_PROOF_SPLIT_GROUP_COUNT_BELOW_MINIMUM:{unique_split_group_count}<{minimum_total}"
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
                row.get("proof_label") if type(row.get("proof_label")) is bool else None for row in split_rows
            }
            if labels != {False, True}:
                errors.append(f"{split_name.upper()}_MISSING_BOTH_PROOF_LABEL_CLASSES")

    required_profiles = {str(value) for value in dataset_profile.get("required_target_profiles", ())}
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

    metric_holdout_count = sum(row.get("metric_applicable") is True for row in holdout_identity_rows)
    minimum_metric = int(dataset_profile.get("minimum_metric_binding_samples", 1))
    if metric_holdout_count < minimum_metric:
        errors.append(f"METRIC_BINDING_HOLDOUT_COUNT_BELOW_MINIMUM:{metric_holdout_count}<{minimum_metric}")

    retrieval_rows = [row for row in rows if row.get("ranked_candidate_ids") is not None]
    calibration_retrieval = [row for row in retrieval_rows if _retrieval_split(row) == "calibration"]
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
                errors.append(f"{prefix}:retrieval_query_content_digest:MUST_BE_NULL_WITHOUT_RANKING")
    else:
        if row.get("source_schema_version") == _ADJUDICATED_EXPORT_SCHEMA:
            require_text("retrieval_query_id")
            query_digest = require_text("retrieval_query_content_digest")
            if query_digest and not _SHA256_RE.fullmatch(query_digest):
                errors.append(f"{prefix}:retrieval_query_content_digest:INVALID_SHA256")
        if (
            not isinstance(ranked, list)
            or not ranked
            or any(not isinstance(item, str) or not item for item in ranked)
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
                not isinstance(rank, int) or isinstance(rank, bool) or rank <= 0 for rank in retrieval_ranks
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
                allocator_budget = int(retrieval_profile.get("allocator_candidate_budget", 64))
                allocator_truncated = raw_eligible_count > allocator_budget
            configured_budget = int(retrieval_profile.get("allocator_candidate_budget", 64))
            if (
                not isinstance(raw_eligible_count, int)
                or isinstance(raw_eligible_count, bool)
                or raw_eligible_count <= 0
            ):
                errors.append(f"{prefix}:raw_eligible_candidate_count:EXPECTED_POSITIVE_INTEGER")
                raw_eligible_count = len(ranked)
            if allocator_budget != configured_budget:
                errors.append(f"{prefix}:allocator_candidate_budget:PROFILE_MISMATCH")
                allocator_budget = configured_budget
            if allocator_truncated is not (raw_eligible_count > allocator_budget):
                errors.append(f"{prefix}:allocator_budget_truncated:COUNT_MISMATCH")
            if not isinstance(universe_size, int) or isinstance(universe_size, bool) or universe_size <= 0:
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
                errors.append(f"{prefix}:judged_candidate_count:FINITE_UNIVERSE_MISMATCH")
            expected_exhausted = universe_size <= frontier_k
            if frontier_exhausted is not expected_exhausted:
                errors.append(f"{prefix}:frontier_exhausted:FINITE_UNIVERSE_MISMATCH")
            if candidate_judging_scope != "FULL_FINITE_UNIVERSE":
                errors.append(f"{prefix}:candidate_judging_scope:FINITE_UNIVERSE_MISMATCH")
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
    if (
        not isinstance(predicted_path, list)
        or not predicted_path
        or any(not isinstance(item, str) or not item for item in predicted_path)
    ):
        errors.append(f"{prefix}:predicted_path_ids:EXPECTED_NONEMPTY_STRING_LIST")
    elif len(set(predicted_path)) != len(predicted_path):
        errors.append(f"{prefix}:predicted_path_ids:DUPLICATE_PATH_NODE")
    gold_path = row.get("gold_path_ids")
    if gold_path is not None:
        if (
            not isinstance(gold_path, list)
            or not gold_path
            or any(not isinstance(item, str) or not item for item in gold_path)
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
            "EXACT" if metric_label is True else "INEXACT" if metric_label is False else "NOT_APPLICABLE"
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
            errors.append(f"{prefix}:metric_applicable:DISAGREES_WITH_DISPOSITION")

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
