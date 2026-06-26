"""C0.3 graph metric heterogeneity policy for apps_rg.

This module is intentionally data-first: it does not replace graph authority.
It defines typed metric/outcome buckets and deterministic checks used by the
canonical graph overwrite materializer and C0.3 traversal hardening.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

POLICY_VERSION = "c03_graph_metric_heterogeneity_policy_v1"

METRIC_BUCKETS: dict[str, tuple[str, ...]] = {
    "revenue_growth": ("revenue", "arr", "renewal", "pipeline", "booking", "sales"),
    "cost_efficiency": ("cost", "savings", "efficiency", "latency", "cycle time", "automation"),
    "risk_governance": ("risk", "governance", "audit", "control", "compliance", "lineage"),
    "platform_scale": ("platform", "scale", "reuse", "throughput", "slo", "availability"),
    "adoption_enablement": ("adoption", "enablement", "training", "nps", "self-service"),
    "delivery_velocity": ("delivery", "release", "deployment", "ci/cd", "pipeline"),
    "model_quality": ("accuracy", "precision", "recall", "eval", "quality", "hallucination"),
    "partner_gtm": ("partner", "hyperscaler", "co-sell", "marketplace", "alliance"),
    "insurance_risk": ("actuarial", "claims", "underwriting", "capital", "reserving"),
    "financial_services": ("bank", "basel", "ccar", "wealth", "trading", "derivatives"),
}

MAX_SAME_METRIC_BUCKET_SHARE = 0.34
MIN_DISTINCT_METRIC_BUCKETS = 5
MIN_DISTINCT_FACT_IDS = 10
MIN_DISTINCT_SKILL_IDS = 12


def normalize_token(value: Any) -> str:
    return str(value or "").strip().lower()


def infer_metric_bucket(text: str, fallback: str = "general_business_outcome") -> str:
    haystack = normalize_token(text)
    for bucket, needles in METRIC_BUCKETS.items():
        if any(n in haystack for n in needles):
            return bucket
    return fallback


def metric_bucket_for_row(row: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in (
        "metric_bucket",
        "business_outcome_bucket",
        "rationale",
        "description",
        "label",
        "allowed_phrases",
        "source_snippets",
        "pillar",
        "subpillar",
    ):
        val = row.get(key)
        if isinstance(val, list):
            parts.extend(str(v) for v in val)
        elif val is not None:
            parts.append(str(val))
    return infer_metric_bucket(" ".join(parts))


def diversity_summary(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    materialized = list(rows)
    buckets = [metric_bucket_for_row(r) for r in materialized]
    skill_ids = {str(r.get("skill_id") or r.get("node_id") or "") for r in materialized if r.get("skill_id") or r.get("node_id")}
    fact_ids: set[str] = set()
    for row in materialized:
        for fid in row.get("fact_id_links") or row.get("source_fact_ids") or []:
            if str(fid).strip():
                fact_ids.add(str(fid))
    counts = Counter(buckets)
    total = max(1, len(buckets))
    max_share = max((c / total for c in counts.values()), default=0.0)
    return {
        "policy_version": POLICY_VERSION,
        "row_count": len(materialized),
        "distinct_metric_buckets": len(counts),
        "metric_bucket_counts": dict(sorted(counts.items())),
        "max_same_metric_bucket_share": round(max_share, 4),
        "distinct_skill_ids": len(skill_ids),
        "distinct_fact_ids": len(fact_ids),
    }


def validate_metric_heterogeneity(rows: Iterable[dict[str, Any]], *, strict: bool = False) -> list[str]:
    summary = diversity_summary(rows)
    errors: list[str] = []
    if summary["distinct_metric_buckets"] < MIN_DISTINCT_METRIC_BUCKETS:
        errors.append(
            f"metric buckets too narrow: {summary['distinct_metric_buckets']} < {MIN_DISTINCT_METRIC_BUCKETS}"
        )
    if summary["max_same_metric_bucket_share"] > MAX_SAME_METRIC_BUCKET_SHARE:
        errors.append(
            f"single metric bucket dominates: {summary['max_same_metric_bucket_share']} > {MAX_SAME_METRIC_BUCKET_SHARE}"
        )
    if strict and summary["distinct_skill_ids"] < MIN_DISTINCT_SKILL_IDS:
        errors.append(f"skill diversity too low: {summary['distinct_skill_ids']} < {MIN_DISTINCT_SKILL_IDS}")
    if strict and summary["distinct_fact_ids"] < MIN_DISTINCT_FACT_IDS:
        errors.append(f"fact diversity too low: {summary['distinct_fact_ids']} < {MIN_DISTINCT_FACT_IDS}")
    return errors


__all__ = [
    "POLICY_VERSION",
    "METRIC_BUCKETS",
    "MAX_SAME_METRIC_BUCKET_SHARE",
    "MIN_DISTINCT_METRIC_BUCKETS",
    "MIN_DISTINCT_FACT_IDS",
    "MIN_DISTINCT_SKILL_IDS",
    "diversity_summary",
    "infer_metric_bucket",
    "metric_bucket_for_row",
    "validate_metric_heterogeneity",
]
