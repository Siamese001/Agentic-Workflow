"""Deterministic retrieval metrics."""

from __future__ import annotations

import math
from typing import Any, Iterable, Mapping, Sequence

from apps_rg.evals.resume_graph.constants import _SHA256_RE
from apps_rg.evals.resume_graph.metrics.coverage import build_retrieval_slices
from apps_rg.evals.resume_graph.models import EvaluationDataError
from apps_rg.evals.resume_graph.reporting import canonical_digest

_RETRIEVAL_SCHEMA = "apps_rg.retrieval_universe.v1"
_CANDIDATE_REQUIRED_FIELDS = frozenset(
    {
        "candidate_id",
        "rank",
        "score",
        "relevance_grade",
        "graph_path",
        "path_binding",
        "jd_concepts",
        "claim_ids",
        "employer",
        "role",
        "evidence_type",
        "metric_bearing",
        "hard_negative_class",
        "critical_hard_negative",
        "near_duplicate_of",
        "content_digest",
    }
)
_QUERY_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "query_id",
        "query_text",
        "target_profile",
        "section",
        "graph_lane",
        "employer",
        "evidence_density",
        "split",
        "candidate_count",
        "candidate_universe",
        "judging_scope",
        "k_values",
        "gate_k",
        "candidates",
        "query_digest",
    }
)
_HARD_NEGATIVE_CLASSES = frozenset(
    {
        "NONE",
        "WRONG_EMPLOYER",
        "WRONG_ROLE",
        "WRONG_DATE",
        "METRIC_SEMANTIC_MISMATCH",
        "SCOPE_MISMATCH",
        "PROJECTED_NOT_ACHIEVED",
        "JD_ONLY_NO_EVIDENCE",
        "DUPLICATE_GRAPH_PATH",
    }
)


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
        not isinstance(rank, int) or isinstance(rank, bool) or rank <= 0 for rank in explicit_ranks
    ):
        raise EvaluationDataError("explicit ranks must be positive integers aligned to candidates")

    def discounted_gain(scores: Iterable[tuple[int, float]]) -> float:
        return sum((2.0 ** float(score) - 1.0) / math.log2(rank + 1.0) for rank, score in scores)

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
        not isinstance(rank, int) or isinstance(rank, bool) or rank <= 0 for rank in explicit_ranks
    ):
        raise EvaluationDataError("explicit ranks must be positive integers aligned to candidates")
    for rank, candidate_id in zip(explicit_ranks, ranked_ids):
        if float(relevance.get(candidate_id, 0.0)) >= positive_floor:
            return 1.0 / rank
    return 0.0


def retrieval_candidate_digest(candidate: Mapping[str, Any]) -> str:
    """Digest one labelled candidate without its self-referential digest."""

    return canonical_digest({key: value for key, value in candidate.items() if key != "content_digest"})


def retrieval_query_digest(query: Mapping[str, Any]) -> str:
    """Digest one full query universe without its self-referential digest."""

    return canonical_digest({key: value for key, value in query.items() if key != "query_digest"})


def retrieval_universe_digest(universe: Mapping[str, Any]) -> str:
    """Digest the independently frozen candidate identity denominator."""

    return canonical_digest({key: value for key, value in universe.items() if key != "manifest_digest"})


def seal_retrieval_query(query: Mapping[str, Any]) -> dict[str, Any]:
    """Seal every candidate and the complete finite candidate universe."""

    sealed = dict(query)
    sealed["candidates"] = []
    for candidate in query.get("candidates", []):
        sealed_candidate = dict(candidate)
        sealed_candidate["content_digest"] = retrieval_candidate_digest(sealed_candidate)
        sealed["candidates"].append(sealed_candidate)
    universe = sealed.get("candidate_universe")
    if isinstance(universe, Mapping):
        sealed["candidate_universe"] = dict(universe)
        sealed["candidate_universe"]["manifest_digest"] = retrieval_universe_digest(
            sealed["candidate_universe"]
        )
    sealed["query_digest"] = retrieval_query_digest(sealed)
    return sealed


def _validate_retrieval_query(query: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if set(query) != _QUERY_REQUIRED_FIELDS:
        reasons.append("RETRIEVAL_QUERY_SCHEMA_INVALID")
    if query.get("schema_version") != _RETRIEVAL_SCHEMA:
        reasons.append("RETRIEVAL_QUERY_SCHEMA_INVALID")
    if not all(
        isinstance(query.get(field), str) and query[field]
        for field in (
            "query_id",
            "query_text",
            "target_profile",
            "section",
            "graph_lane",
            "employer",
        )
    ):
        reasons.append("RETRIEVAL_QUERY_IDENTITY_INVALID")
    if query.get("evidence_density") not in {"SPARSE", "MEDIUM", "DENSE"}:
        reasons.append("EVIDENCE_DENSITY_INVALID")
    if query.get("judging_scope") != "FULL_FINITE_UNIVERSE":
        reasons.append("FULL_CANDIDATE_UNIVERSE_REQUIRED")
    candidates = query.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        reasons.append("CANDIDATE_UNIVERSE_EMPTY")
        return sorted(set(reasons))
    if query.get("candidate_count") != len(candidates):
        reasons.append("CANDIDATE_COUNT_MISMATCH")
    universe = query.get("candidate_universe")
    universe_ids: list[str] = []
    if not isinstance(universe, Mapping) or set(universe) != {
        "authority",
        "candidate_ids",
        "candidate_count",
        "manifest_digest",
    }:
        reasons.append("CANDIDATE_UNIVERSE_MANIFEST_INVALID")
    else:
        if universe.get("authority") != "FROZEN_HUMAN_LABELLED":
            reasons.append("CANDIDATE_UNIVERSE_AUTHORITY_INVALID")
        if isinstance(universe.get("candidate_ids"), list):
            universe_ids = universe["candidate_ids"]
        if (
            not universe_ids
            or any(not isinstance(value, str) or not value for value in universe_ids)
            or len(set(universe_ids)) != len(universe_ids)
            or universe.get("candidate_count") != len(universe_ids)
        ):
            reasons.append("CANDIDATE_UNIVERSE_IDENTITY_INVALID")
        manifest_digest = universe.get("manifest_digest")
        if (
            not isinstance(manifest_digest, str)
            or not _SHA256_RE.fullmatch(manifest_digest)
            or manifest_digest != retrieval_universe_digest(universe)
        ):
            reasons.append("CANDIDATE_UNIVERSE_DIGEST_INVALID")
    if query.get("split") not in {"CALIBRATION", "HOLDOUT"}:
        reasons.append("SPLIT_INVALID")
    k_values = query.get("k_values")
    if not isinstance(k_values, list) or k_values != [1, 3, 5, 10]:
        reasons.append("K_VALUES_INVALID")
    gate_k = query.get("gate_k")
    if not isinstance(gate_k, int) or isinstance(gate_k, bool) or gate_k <= 0 or gate_k > len(candidates):
        reasons.append("GATE_K_INVALID")
    query_digest = query.get("query_digest")
    if (
        not isinstance(query_digest, str)
        or not _SHA256_RE.fullmatch(query_digest)
        or query_digest != retrieval_query_digest(query)
    ):
        reasons.append("QUERY_DIGEST_INVALID")

    candidate_ids: list[str] = []
    ranks: list[int] = []
    for candidate in candidates:
        if not isinstance(candidate, Mapping) or set(candidate) != _CANDIDATE_REQUIRED_FIELDS:
            reasons.append("RETRIEVAL_CANDIDATE_SCHEMA_INVALID")
            continue
        candidate_ids.append(str(candidate.get("candidate_id", "")))
        ranks.append(candidate.get("rank"))
        digest = candidate.get("content_digest")
        if (
            not isinstance(digest, str)
            or not _SHA256_RE.fullmatch(digest)
            or digest != retrieval_candidate_digest(candidate)
        ):
            reasons.append("CANDIDATE_DIGEST_INVALID")
        if (
            not isinstance(candidate.get("score"), (int, float))
            or isinstance(candidate.get("score"), bool)
            or not math.isfinite(float(candidate["score"]))
        ):
            reasons.append("CANDIDATE_SCORE_INVALID")
        if candidate.get("relevance_grade") not in {0, 1, 2, 3}:
            reasons.append("RELEVANCE_GRADE_INVALID")
        if candidate.get("path_binding") not in {"EXACT", "MISMATCH", "UNKNOWN"}:
            reasons.append("PATH_BINDING_INVALID")
        graph_path = candidate.get("graph_path")
        if (
            not isinstance(graph_path, list)
            or not graph_path
            or any(not isinstance(node, str) or not node for node in graph_path)
        ):
            reasons.append("GRAPH_PATH_INVALID")
        for field in ("jd_concepts", "claim_ids"):
            values = candidate.get(field)
            if not isinstance(values, list) or any(
                not isinstance(value, str) or not value for value in values
            ):
                reasons.append(f"{field.upper()}_INVALID")
        if not all(
            isinstance(candidate.get(field), str) and candidate[field]
            for field in ("employer", "role", "evidence_type")
        ):
            reasons.append("CANDIDATE_BINDING_IDENTITY_INVALID")
        if not isinstance(candidate.get("metric_bearing"), bool) or not isinstance(
            candidate.get("critical_hard_negative"), bool
        ):
            reasons.append("CANDIDATE_BOOLEAN_FIELD_INVALID")
        if candidate.get("hard_negative_class") not in _HARD_NEGATIVE_CLASSES:
            reasons.append("HARD_NEGATIVE_CLASS_INVALID")
        elif (
            candidate.get("hard_negative_class") == "NONE" and candidate.get("critical_hard_negative") is True
        ) or (
            candidate.get("hard_negative_class") != "NONE" and candidate.get("relevance_grade") in {1, 2, 3}
        ):
            reasons.append("HARD_NEGATIVE_LABEL_CONFLICT")
        near_duplicate = candidate.get("near_duplicate_of")
        if near_duplicate is not None and (not isinstance(near_duplicate, str) or not near_duplicate):
            reasons.append("NEAR_DUPLICATE_REFERENCE_INVALID")
    if len(set(candidate_ids)) != len(candidate_ids) or any(not value for value in candidate_ids):
        reasons.append("CANDIDATE_IDENTITY_INVALID")
    if universe_ids and (
        set(candidate_ids) != set(universe_ids)
        or query.get("candidate_count") != universe.get("candidate_count")
    ):
        reasons.append("CANDIDATE_UNIVERSE_MISMATCH")
    if ranks != list(range(1, len(candidates) + 1)):
        reasons.append("CANDIDATE_RANKS_NOT_CONTIGUOUS")
    scores = [candidate.get("score") for candidate in candidates if isinstance(candidate, Mapping)]
    if len(scores) == len(candidates) and all(
        isinstance(score, (int, float)) and not isinstance(score, bool) for score in scores
    ):
        if any(float(left) < float(right) for left, right in zip(scores, scores[1:])):
            reasons.append("RANK_SCORE_INCONSISTENT")
    candidate_id_set = set(candidate_ids)
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            continue
        near_duplicate = candidate.get("near_duplicate_of")
        if near_duplicate is not None and (
            near_duplicate not in candidate_id_set or near_duplicate == candidate.get("candidate_id")
        ):
            reasons.append("NEAR_DUPLICATE_REFERENCE_INVALID")
        if candidate.get("hard_negative_class") == "DUPLICATE_GRAPH_PATH" and near_duplicate is None:
            reasons.append("DUPLICATE_GRAPH_PATH_REFERENCE_MISSING")
    return sorted(set(reasons))


def _coverage(numerator: set[str], denominator: set[str]) -> float | None:
    return len(numerator & denominator) / len(denominator) if denominator else None


def evaluate_retrieval_query(query: Mapping[str, Any], *, positive_floor: float = 2.0) -> dict[str, Any]:
    """Evaluate one sealed ranking against its complete labelled universe."""

    unknown_reasons = _validate_retrieval_query(query)
    if unknown_reasons:
        return {
            "gate_id": "G1",
            "query_id": str(query.get("query_id", "")),
            "status": "UNKNOWN",
            "metrics": {},
            "failure_codes": [],
            "unknown_reasons": unknown_reasons,
            "slice_attributes": {},
        }

    candidates = query["candidates"]
    ranked_ids = [candidate["candidate_id"] for candidate in candidates]
    relevance = {candidate["candidate_id"]: candidate["relevance_grade"] for candidate in candidates}
    ranks = [candidate["rank"] for candidate in candidates]
    relevant = [candidate for candidate in candidates if candidate["relevance_grade"] >= positive_floor]
    if not relevant:
        return {
            "gate_id": "G1",
            "query_id": query["query_id"],
            "status": "UNKNOWN",
            "metrics": {},
            "failure_codes": [],
            "unknown_reasons": ["RELEVANT_CANDIDATE_DENOMINATOR_EMPTY"],
            "slice_attributes": {},
        }
    gate_k = query["gate_k"]
    top_k = candidates[:gate_k]
    top_relevant = [candidate for candidate in top_k if candidate["relevance_grade"] >= positive_floor]
    hard_negatives = [candidate for candidate in candidates if candidate["hard_negative_class"] != "NONE"]
    selected_hard_negatives = [candidate for candidate in top_k if candidate["hard_negative_class"] != "NONE"]
    critical_hard_negatives = [candidate for candidate in candidates if candidate["critical_hard_negative"]]
    selected_critical = [candidate for candidate in top_k if candidate["critical_hard_negative"]]
    all_concepts = {concept for candidate in relevant for concept in candidate["jd_concepts"]}
    selected_concepts = {concept for candidate in top_relevant for concept in candidate["jd_concepts"]}
    all_claims = {claim for candidate in relevant for claim in candidate["claim_ids"]}
    selected_claims = {claim for candidate in top_relevant for claim in candidate["claim_ids"]}
    all_employers = {candidate["employer"] for candidate in relevant}
    selected_employers = {candidate["employer"] for candidate in top_relevant}
    metric_relevant = [candidate for candidate in relevant if candidate["metric_bearing"]]
    metric_selected = [candidate for candidate in top_relevant if candidate["metric_bearing"]]
    relevant_scores = [float(candidate["score"]) for candidate in top_relevant]
    irrelevant_scores = [
        float(candidate["score"]) for candidate in candidates if candidate["relevance_grade"] < positive_floor
    ]

    metrics: dict[str, Any] = {}
    for k in (1, 3, 5, 10):
        metrics[f"recall_at_{k}"] = recall_at_k(ranked_ids, relevance, k, positive_floor=positive_floor)
        metrics[f"ndcg_at_{k}"] = ndcg_at_k(ranked_ids, relevance, k, ranks=ranks)
    metrics.update(
        {
            "mrr": reciprocal_rank(ranked_ids, relevance, positive_floor=positive_floor, ranks=ranks),
            "relevant_evidence_coverage": len(top_relevant) / len(relevant),
            "jd_concept_coverage": _coverage(selected_concepts, all_concepts),
            "top_k_sufficiency": float(len(top_relevant) == len(relevant)),
            "top_k_redundancy_rate": sum(candidate["near_duplicate_of"] is not None for candidate in top_k)
            / len(top_k),
            "unique_claim_coverage": _coverage(selected_claims, all_claims),
            "employer_diversity": _coverage(selected_employers, all_employers),
            "metric_bearing_recall": len(metric_selected) / len(metric_relevant) if metric_relevant else None,
            "hard_negative_rejection_rate": (
                (len(hard_negatives) - len(selected_hard_negatives)) / len(hard_negatives)
                if hard_negatives
                else None
            ),
            "wrong_employer_top_k_rate": sum(
                candidate["hard_negative_class"] == "WRONG_EMPLOYER" for candidate in top_k
            )
            / len(top_k),
            "wrong_role_top_k_rate": sum(
                candidate["hard_negative_class"] == "WRONG_ROLE" for candidate in top_k
            )
            / len(top_k),
            "near_duplicate_top_k_rate": sum(
                candidate["hard_negative_class"] == "DUPLICATE_GRAPH_PATH" for candidate in top_k
            )
            / len(top_k),
            "relevant_omitted_beyond_k": len(relevant) - len(top_relevant),
            "exact_path_accuracy": sum(candidate["path_binding"] == "EXACT" for candidate in top_relevant)
            / len(top_relevant)
            if top_relevant
            else 0.0,
            "selection_margin": min(relevant_scores) - max(irrelevant_scores)
            if relevant_scores and irrelevant_scores
            else None,
        }
    )
    failure_codes = []
    if selected_critical:
        failure_codes.append("CRITICAL_HARD_NEGATIVE_SELECTED")
    if metrics["relevant_omitted_beyond_k"]:
        failure_codes.append("RELEVANT_EVIDENCE_OMITTED")
    if metrics["exact_path_accuracy"] != 1.0:
        failure_codes.append("EXACT_PATH_ACCURACY_FAILED")
    if metrics["top_k_redundancy_rate"]:
        failure_codes.append("TOP_K_REDUNDANCY")
    if any(candidate["path_binding"] == "UNKNOWN" for candidate in top_relevant):
        return {
            "gate_id": "G1",
            "query_id": query["query_id"],
            "status": "UNKNOWN",
            "metrics": metrics,
            "failure_codes": [],
            "unknown_reasons": ["SELECTED_PATH_BINDING_UNKNOWN"],
            "slice_attributes": {},
        }

    evidence_types = sorted({candidate["evidence_type"] for candidate in relevant})
    hard_negative_classes = sorted({candidate["hard_negative_class"] for candidate in hard_negatives})
    return {
        "gate_id": "G1",
        "query_id": query["query_id"],
        "status": "FAIL" if failure_codes else "PASS",
        "metrics": metrics,
        "failure_codes": sorted(set(failure_codes)),
        "unknown_reasons": [],
        "slice_attributes": {
            "target_profile": [query["target_profile"]],
            "section": [query["section"]],
            "graph_lane": [query["graph_lane"]],
            "employer": [query["employer"]],
            "evidence_type": evidence_types,
            "metric_bearing": [str(bool(metric_relevant)).lower()],
            "evidence_density": [query["evidence_density"]],
            "candidate_pool_size": [
                "SMALL" if len(candidates) <= 8 else "MEDIUM" if len(candidates) <= 32 else "LARGE"
            ],
            "split": [query["split"]],
            "hard_negative_class": hard_negative_classes or ["NONE"],
        },
    }


def evaluate_retrieval_gate(
    queries: Sequence[Mapping[str, Any]], *, positive_floor: float = 2.0
) -> dict[str, Any]:
    """Evaluate retrieval with explicit calibration/holdout and slice separation."""

    if not queries:
        return {
            "gate_id": "G1",
            "score_groups": ["retrieval_quality"],
            "status": "UNKNOWN",
            "metrics": {},
            "failure_codes": [],
            "unknown_reasons": ["RETRIEVAL_QUERY_SET_EMPTY"],
            "query_results": [],
            "slices": {},
            "authority": "ADVISORY_FUTURE_RUN_ONLY",
        }
    results = [evaluate_retrieval_query(query, positive_floor=positive_floor) for query in queries]
    unknown_reasons = {reason for result in results for reason in result["unknown_reasons"]}
    failure_codes = {code for result in results for code in result["failure_codes"]}
    split_ids: dict[str, set[str]] = {"CALIBRATION": set(), "HOLDOUT": set()}
    split_candidates: dict[str, set[str]] = {"CALIBRATION": set(), "HOLDOUT": set()}
    for query in queries:
        split = query.get("split")
        if split in split_ids:
            split_ids[split].add(str(query.get("query_id", "")))
            candidates = query.get("candidates")
            if isinstance(candidates, list):
                split_candidates[split].update(
                    str(candidate.get("candidate_id", "")) for candidate in candidates
                )
    if not all(split_ids.values()):
        unknown_reasons.add("CALIBRATION_HOLDOUT_SPLIT_INCOMPLETE")
    if (
        split_ids["CALIBRATION"] & split_ids["HOLDOUT"]
        or split_candidates["CALIBRATION"] & split_candidates["HOLDOUT"]
    ):
        failure_codes.add("CALIBRATION_HOLDOUT_LEAKAGE")

    valid_results = [result for result in results if result["metrics"]]
    metric_names = sorted({name for result in valid_results for name in result["metrics"]})
    aggregate_metrics = {
        name: _mean(
            [
                float(result["metrics"][name])
                for result in valid_results
                if result["metrics"].get(name) is not None
            ]
        )
        for name in metric_names
        if any(result["metrics"].get(name) is not None for result in valid_results)
    }
    for k in (1, 3, 5, 10):
        relevant_total = 0
        recovered_total = 0
        for query, result in zip(queries, results):
            if not result["metrics"]:
                continue
            relevant_ids = {
                candidate["candidate_id"]
                for candidate in query["candidates"]
                if candidate["relevance_grade"] >= positive_floor
            }
            ranked_ids = [candidate["candidate_id"] for candidate in query["candidates"]]
            relevant_total += len(relevant_ids)
            recovered_total += len(relevant_ids.intersection(ranked_ids[:k]))
        if relevant_total:
            aggregate_metrics[f"pooled_recall_at_{k}"] = recovered_total / relevant_total
    if unknown_reasons:
        status = "UNKNOWN"
        failure_codes = set()
    elif failure_codes:
        status = "FAIL"
    else:
        status = "PASS"
    return {
        "gate_id": "G1",
        "score_groups": ["retrieval_quality"],
        "status": status,
        "metrics": aggregate_metrics,
        "failure_codes": sorted(failure_codes),
        "unknown_reasons": sorted(unknown_reasons),
        "query_results": results,
        "slices": build_retrieval_slices(results),
        "split_summary": {
            split.lower(): {
                "query_count": len(split_ids[split]),
                "candidate_count": len(split_candidates[split]),
            }
            for split in ("CALIBRATION", "HOLDOUT")
        },
        "authority": "ADVISORY_FUTURE_RUN_ONLY",
    }
