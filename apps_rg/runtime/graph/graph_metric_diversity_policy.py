"""C0.3 graph metric diversity policy helpers.

These helpers are intentionally pure-Python and side-effect free so they can be called from
C0.3 traversal/ranking without becoming a new source of truth. The canonical source remains
apps_rg/fact_inventory/master_skills_arsenal_ledger.json.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

DEFAULT_MAX_REPEAT_PER_RESUME = 1
DEFAULT_MAX_REPEAT_PER_SECTION = 1


def metric_bucket_for_skill(skill: dict[str, Any]) -> str:
    return str(skill.get("metric_bucket") or skill.get("subpillar") or "unknown_metric_bucket")


def build_metric_diversity_receipt(selected_skills: list[dict[str, Any]]) -> dict[str, Any]:
    buckets = [metric_bucket_for_skill(s) for s in selected_skills]
    by_section: dict[str, Counter[str]] = defaultdict(Counter)
    for skill in selected_skills:
        bucket = metric_bucket_for_skill(skill)
        sections = skill.get("selected_for_sections") or skill.get("allowed_sections") or ["unknown_section"]
        for section in sections:
            by_section[str(section)][bucket] += 1
    return {
        "schema": "graph_metric_diversity_receipt_v1",
        "selected_skill_count": len(selected_skills),
        "distinct_metric_bucket_count": len(set(buckets)),
        "metric_bucket_counts": dict(Counter(buckets)),
        "metric_bucket_counts_by_section": {k: dict(v) for k, v in by_section.items()},
        "repeated_metric_buckets": sorted([k for k, v in Counter(buckets).items() if v > DEFAULT_MAX_REPEAT_PER_RESUME]),
    }


def rank_with_metric_diversity(
    candidates: list[dict[str, Any]],
    *,
    already_selected: list[dict[str, Any]] | None = None,
    score_key: str = "score",
) -> list[dict[str, Any]]:
    """Rank candidates while preferring unseen metric buckets.

    Existing score is preserved; this only adds a deterministic diversity bonus/penalty field.
    """
    selected = already_selected or []
    used = Counter(metric_bucket_for_skill(s) for s in selected)
    ranked: list[dict[str, Any]] = []
    for idx, cand in enumerate(candidates):
        out = dict(cand)
        bucket = metric_bucket_for_skill(out)
        base = float(out.get(score_key) or out.get("weight") or 0.0)
        diversity_bonus = 0.25 if used[bucket] == 0 else -0.15 * used[bucket]
        out["metric_diversity_bucket"] = bucket
        out["metric_diversity_score"] = round(base + diversity_bonus, 6)
        out["metric_diversity_reason"] = "prefer_unseen_bucket" if used[bucket] == 0 else "penalize_repeated_bucket"
        out["_stable_input_order"] = idx
        ranked.append(out)
    ranked.sort(key=lambda r: (-float(r.get("metric_diversity_score") or 0.0), str(r.get("metric_diversity_bucket") or ""), r["_stable_input_order"]))
    for row in ranked:
        row.pop("_stable_input_order", None)
    return ranked


def build_rejected_sibling_receipts(
    selected_skills: list[dict[str, Any]],
    rejected_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    selected_buckets = Counter(metric_bucket_for_skill(s) for s in selected_skills)
    receipts: list[dict[str, Any]] = []
    for cand in rejected_candidates:
        bucket = metric_bucket_for_skill(cand)
        reason = str(cand.get("rejection_reason") or "")
        if not reason:
            reason = "metric_bucket_repeat" if selected_buckets[bucket] else "lower_graph_support_score"
        receipts.append(
            {
                "skill_id": cand.get("skill_id"),
                "metric_bucket": bucket,
                "rejection_reason": reason,
                "selected_bucket_count": selected_buckets[bucket],
            }
        )
    return receipts
