"""Slice aggregation for retrieval coverage and hard-negative visibility."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

_REQUIRED_SLICE_DIMENSIONS = (
    "target_profile",
    "section",
    "graph_lane",
    "employer",
    "evidence_type",
    "metric_bearing",
    "evidence_density",
    "candidate_pool_size",
    "split",
    "hard_negative_class",
)


def _slice_status(results: Sequence[Mapping[str, Any]]) -> str:
    statuses = {str(result["status"]) for result in results}
    if "UNKNOWN" in statuses:
        return "UNKNOWN"
    if "FAIL" in statuses:
        return "FAIL"
    return "PASS"


def build_retrieval_slices(results: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """Build every governed slice, retaining worst-case query status."""

    buckets: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for result in results:
        for dimension, values in result.get("slice_attributes", {}).items():
            for value in values:
                buckets[(dimension, str(value))].append(result)

    slices: dict[str, dict[str, Any]] = {dimension: {} for dimension in _REQUIRED_SLICE_DIMENSIONS}
    for (dimension, value), members in sorted(buckets.items()):
        metrics: dict[str, float] = {}
        for name in (
            "relevant_evidence_coverage",
            "jd_concept_coverage",
            "hard_negative_rejection_rate",
            "exact_path_accuracy",
        ):
            observations = [
                float(member["metrics"][name])
                for member in members
                if member.get("metrics", {}).get(name) is not None
            ]
            if observations:
                metrics[name] = sum(observations) / len(observations)
        slices.setdefault(dimension, {})[value] = {
            "status": _slice_status(members),
            "query_count": len(members),
            "metrics": metrics,
            "failure_codes": sorted({code for member in members for code in member.get("failure_codes", [])}),
            "unknown_reasons": sorted(
                {reason for member in members for reason in member.get("unknown_reasons", [])}
            ),
        }
    return slices
