from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

GRAPH_SKILL_CONCENTRATION_POLICY_SCHEMA = "graph_skill_concentration_policy_v1"
DEFAULT_WARNING_THRESHOLD_PCT = 75.0
DEFAULT_HITL_THRESHOLD_PCT = 80.0
DEFAULT_PROPOSAL_TARGET_PCT = 80.0


def _clean_bucket_ids(
    bucket_ids: Sequence[str] | None,
    counts: Mapping[str, Any],
) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    if bucket_ids is not None:
        for raw in bucket_ids:
            bucket_id = str(raw).strip()
            if bucket_id and bucket_id not in seen:
                ordered.append(bucket_id)
                seen.add(bucket_id)
    for raw in counts:
        bucket_id = str(raw).strip()
        if bucket_id and bucket_id not in seen:
            ordered.append(bucket_id)
            seen.add(bucket_id)
    return ordered


def _clean_counts(counts: Mapping[str, Any], bucket_ids: Sequence[str]) -> dict[str, int]:
    cleaned: dict[str, int] = {}
    for bucket_id in bucket_ids:
        value = counts.get(bucket_id, 0)
        try:
            numeric = int(value)
        except (TypeError, ValueError):
            numeric = 0
        cleaned[bucket_id] = max(0, numeric)
    return cleaned


def _humanize_bucket_id(bucket_id: str) -> str:
    return bucket_id.replace("_", " ").strip()


def _share_pct(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return (float(count) / float(total)) * 100.0


def _redistribute_excess_evenly(
    *,
    current_share_pct_by_bucket: dict[str, float],
    bucket_ids: list[str],
    target_dominant_share_pct: float,
) -> dict[str, float]:
    """Cap the dominant bucket and spread the excess across the rest."""
    if not bucket_ids:
        return {}
    rank = {bucket_id: idx for idx, bucket_id in enumerate(bucket_ids)}
    dominant_bucket_id = max(
        bucket_ids,
        key=lambda bucket_id: (current_share_pct_by_bucket.get(bucket_id, 0.0), -rank[bucket_id]),
    )
    dominant_share = float(current_share_pct_by_bucket.get(dominant_bucket_id, 0.0))
    if len(bucket_ids) <= 1 or dominant_share <= target_dominant_share_pct:
        return dict(current_share_pct_by_bucket)

    excess = dominant_share - target_dominant_share_pct
    support_bucket_ids = [bucket_id for bucket_id in bucket_ids if bucket_id != dominant_bucket_id]
    if not support_bucket_ids:
        return dict(current_share_pct_by_bucket)

    proposed = dict(current_share_pct_by_bucket)
    proposed[dominant_bucket_id] = target_dominant_share_pct
    even_share = excess / float(len(support_bucket_ids))
    for bucket_id in support_bucket_ids:
        proposed[bucket_id] = proposed.get(bucket_id, 0.0) + even_share
    return proposed


def build_graph_skill_concentration_policy(
    *,
    counts: Mapping[str, Any],
    distribution_kind: str,
    bucket_ids: Sequence[str] | None = None,
    bucket_labels: Mapping[str, str] | None = None,
    context: Mapping[str, Any] | None = None,
    warning_threshold_pct: float = DEFAULT_WARNING_THRESHOLD_PCT,
    hitl_threshold_pct: float = DEFAULT_HITL_THRESHOLD_PCT,
    proposal_target_pct: float = DEFAULT_PROPOSAL_TARGET_PCT,
) -> dict[str, Any]:
    """Summarize concentration, verdict, and a reallocation proposal.

    The returned structure is designed to be attached to any section plan or
    track expansion payload so the same policy applies consistently across
    all section lanes.
    """
    bucket_order = _clean_bucket_ids(bucket_ids, counts)
    cleaned_counts = _clean_counts(counts, bucket_order)
    total_count = sum(cleaned_counts.values())
    labels = dict(bucket_labels or {})
    current_share_pct_by_bucket = {
        bucket_id: _share_pct(cleaned_counts[bucket_id], total_count) for bucket_id in bucket_order
    }
    proposed_share_pct_by_bucket = _redistribute_excess_evenly(
        current_share_pct_by_bucket=current_share_pct_by_bucket,
        bucket_ids=bucket_order,
        target_dominant_share_pct=proposal_target_pct,
    )

    dominant_bucket_id = ""
    dominant_share_pct = 0.0
    if bucket_order:
        dominant_bucket_id = max(
            bucket_order,
            key=lambda bucket_id: (current_share_pct_by_bucket.get(bucket_id, 0.0), -bucket_order.index(bucket_id)),
        )
        dominant_share_pct = float(current_share_pct_by_bucket.get(dominant_bucket_id, 0.0))

    if total_count <= 0:
        policy_status = "empty"
        policy_reason = "no_selected_skills"
    elif dominant_share_pct > hitl_threshold_pct:
        policy_status = "hitl"
        policy_reason = "dominant_share_above_hitl_threshold"
    elif dominant_share_pct > warning_threshold_pct:
        policy_status = "warning"
        policy_reason = "dominant_share_above_warning_threshold"
    else:
        policy_status = "ok"
        policy_reason = "dominant_share_within_threshold"

    bucket_rows: list[dict[str, Any]] = []
    for rank, bucket_id in enumerate(
        sorted(
            bucket_order,
            key=lambda bucket_id: (-current_share_pct_by_bucket.get(bucket_id, 0.0), bucket_id),
        ),
        start=1,
    ):
        current_share = current_share_pct_by_bucket.get(bucket_id, 0.0)
        proposed_share = proposed_share_pct_by_bucket.get(bucket_id, current_share)
        bucket_rows.append(
            {
                "rank": rank,
                "bucket_id": bucket_id,
                "bucket_label": labels.get(bucket_id, _humanize_bucket_id(bucket_id)),
                "count": cleaned_counts.get(bucket_id, 0),
                "current_share_pct": round(current_share, 2),
                "proposed_share_pct": round(proposed_share, 2),
                "delta_pp": round(proposed_share - current_share, 2),
                "is_dominant": bucket_id == dominant_bucket_id,
                "row_status": "dominant" if bucket_id == dominant_bucket_id else "supporting",
            }
        )

    reallocation_feasible = total_count > 0 and len(bucket_order) > 1 and dominant_share_pct > warning_threshold_pct
    reallocation_proposal: dict[str, Any] | None = None
    if reallocation_feasible:
        reallocation_proposal = {
            "method": "even_redistribution_from_dominant_bucket",
            "target_dominant_share_pct": proposal_target_pct,
            "dominant_bucket_id": dominant_bucket_id,
            "current_share_pct_by_bucket": current_share_pct_by_bucket,
            "proposed_share_pct_by_bucket": proposed_share_pct_by_bucket,
            "dominant_gap_to_warning_pp": round(dominant_share_pct - warning_threshold_pct, 2),
            "dominant_gap_to_hitl_pp": round(dominant_share_pct - hitl_threshold_pct, 2),
        }

    policy = {
        "schema": GRAPH_SKILL_CONCENTRATION_POLICY_SCHEMA,
        "distribution_kind": distribution_kind,
        "context": dict(context or {}),
        "bucket_ids": bucket_order,
        "total_count": total_count,
        "thresholds": {
            "warning_pct": warning_threshold_pct,
            "hitl_pct": hitl_threshold_pct,
            "proposal_target_pct": proposal_target_pct,
        },
        "current_share_pct_by_bucket": current_share_pct_by_bucket,
        "proposed_share_pct_by_bucket": proposed_share_pct_by_bucket,
        "dominant_bucket_id": dominant_bucket_id,
        "dominant_bucket_label": labels.get(dominant_bucket_id, _humanize_bucket_id(dominant_bucket_id))
        if dominant_bucket_id
        else "",
        "dominant_share_pct": round(dominant_share_pct, 2),
        "dominant_gap_to_warning_pp": round(dominant_share_pct - warning_threshold_pct, 2)
        if dominant_bucket_id
        else 0.0,
        "dominant_gap_to_hitl_pp": round(dominant_share_pct - hitl_threshold_pct, 2)
        if dominant_bucket_id
        else 0.0,
        "policy_status": policy_status,
        "policy_reason": policy_reason,
        "policy_message": (
            "No selected skills, so no concentration verdict was computed."
            if policy_status == "empty"
            else (
                f"Dominant bucket {dominant_bucket_id!r} is at {round(dominant_share_pct, 2)}%"
                f" ({policy_status})."
            )
        ),
        "rows": bucket_rows,
        "reallocation_feasible": reallocation_feasible,
        "reallocation_proposal": reallocation_proposal,
    }
    return policy


__all__ = [
    "DEFAULT_HITL_THRESHOLD_PCT",
    "DEFAULT_PROPOSAL_TARGET_PCT",
    "DEFAULT_WARNING_THRESHOLD_PCT",
    "GRAPH_SKILL_CONCENTRATION_POLICY_SCHEMA",
    "build_graph_skill_concentration_policy",
]
