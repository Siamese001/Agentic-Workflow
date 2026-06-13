"""W2 fact-ledger authority fence for apps_rg graph evidence paths."""
from __future__ import annotations

from typing import Any, Mapping

BLOCKED_FACT_LEDGER_AUTHORITY = "BLOCKED_FACT_LEDGER_AUTHORITY"

FACT_LEDGER_AUTHORITY_LABELS: frozenset[str] = frozenset(
    {
        "fact_ledger",
        "candidate_fact_ledger",
        "master_candidate_skills_fact_ledger",
        "broad_skills_ledger",
    }
)

FACT_LEDGER_AUTHORITY_FLAGS: tuple[str, ...] = (
    "fact_ledger_authority",
    "fact_ledger_used_as_authority",
    "fact_ledger_skills_authority",
    "fact_ledger_skill_authority",
    "fact_ledger_metrics_authority",
    "fact_ledger_metric_authority",
    "fact_ledger_proof_authority",
    "fact_ledger_claim_authority",
    "candidate_fact_ledger_skills_authority",
    "candidate_fact_ledger_skill_authority",
    "candidate_fact_ledger_metrics_authority",
    "candidate_fact_ledger_metric_authority",
    "master_candidate_skills_fact_ledger_used_as_authority",
)

FACT_LEDGER_AUTHORITY_SOURCE_FIELDS: tuple[str, ...] = (
    "source_authority",
    "proof_source",
    "proof_pool_type",
    "skills_authority_source_type",
    "skills_source_type",
    "skill_authority_source_type",
    "skill_source_type",
    "metrics_authority_source_type",
    "metric_authority_source_type",
    "metrics_source_type",
    "metric_source_type",
    "claim_authority_source_type",
    "proof_authority_source_type",
    "weighting_authority_source_type",
    "targeting_weight_authority_source_type",
)


def normalize_authority_label(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def _method_uses_fact_ledger_as_authority(method: str) -> bool:
    if not method:
        return False
    if method in FACT_LEDGER_AUTHORITY_LABELS:
        return True
    return method.startswith(
        (
            "fact_ledger",
            "candidate_fact_ledger",
            "master_candidate_skills_fact_ledger",
            "broad_skills_ledger",
        )
    )


def fact_ledger_authority_violation_reason(
    *,
    proof_pool_metadata: Mapping[str, Any] | None,
    selected_fact_plan: Mapping[str, Any] | None = None,
) -> str | None:
    """Return a fail-closed reason when fact ledger is runtime authority.

    W2 still permits legacy substrate/audit references, such as
    ``claim_evidence_substrate_ref`` or ``evidence_authority.ledger_ref``, when
    GraphDB/``augmented_skills_graph`` is the actual authority. This check only
    rejects fields that admit, prove, weight, select, or source skills/metrics
    from a fact-ledger label.
    """
    meta = proof_pool_metadata if isinstance(proof_pool_metadata, Mapping) else {}
    plan = selected_fact_plan if isinstance(selected_fact_plan, Mapping) else {}

    for flag in FACT_LEDGER_AUTHORITY_FLAGS:
        if meta.get(flag) is True:
            return f"{flag}=true"
        if plan.get(flag) is True:
            return f"selected_fact_plan.{flag}=true"

    for field in FACT_LEDGER_AUTHORITY_SOURCE_FIELDS:
        label = normalize_authority_label(meta.get(field))
        if label in FACT_LEDGER_AUTHORITY_LABELS:
            return f"{field}={label!r}"
        plan_label = normalize_authority_label(plan.get(field))
        if plan_label in FACT_LEDGER_AUTHORITY_LABELS:
            return f"selected_fact_plan.{field}={plan_label!r}"

    evidence_authority = meta.get("evidence_authority")
    if isinstance(evidence_authority, Mapping):
        authority = normalize_authority_label(evidence_authority.get("authority"))
        if authority in FACT_LEDGER_AUTHORITY_LABELS:
            return f"evidence_authority.authority={authority!r}"

    selection_scope = meta.get("selection_scope")
    if isinstance(selection_scope, Mapping):
        selection_authority = normalize_authority_label(selection_scope.get("selection_authority"))
        if selection_authority in FACT_LEDGER_AUTHORITY_LABELS:
            return f"selection_scope.selection_authority={selection_authority!r}"
        method = normalize_authority_label(selection_scope.get("selection_method"))
        if _method_uses_fact_ledger_as_authority(method):
            return f"selection_scope.selection_method={method!r}"

    method = normalize_authority_label(plan.get("selection_method") or meta.get("selection_method"))
    if _method_uses_fact_ledger_as_authority(method):
        return f"selection_method={method!r}"

    return None


__all__ = [
    "BLOCKED_FACT_LEDGER_AUTHORITY",
    "FACT_LEDGER_AUTHORITY_FLAGS",
    "FACT_LEDGER_AUTHORITY_LABELS",
    "FACT_LEDGER_AUTHORITY_SOURCE_FIELDS",
    "fact_ledger_authority_violation_reason",
    "normalize_authority_label",
]
