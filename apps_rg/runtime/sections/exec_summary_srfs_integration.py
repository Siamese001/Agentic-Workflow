"""SelectedRoleFactSet → executive_summary runtime (apps_rg only).

Thin wrapper around :mod:`apps_rg.runtime.sections.selected_role_fact_set` for backward-compatible
imports and ``build_exec_summary_srfs_bundle`` entry used by ``executive_summary_lane``.

Only ``selected_facts_by_section["executive_summary"]`` HIGH rows participate in proof.
JD/briefing remain targeting-only downstream; this module does not mint facts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.sections.selected_role_fact_set import (
    build_allowed_fact_ids_for_plan_facts,
    build_section_fact_plan,
    build_srfs_integration_envelope,
    load_selected_role_fact_set,
    metric_derivative_fact_id,
    selected_fact_plan_from_srfs,
    slice_row_to_plan_fact,
)

# Legacy alias: same loader as shared module.
load_srfs_document = load_selected_role_fact_set


def build_exec_summary_srfs_bundle(
    *,
    srfs_json_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], list[str], set[str]]:
    """Return (selected_fact_plan, srfs_integration_envelope, ordered_allowed_ids, allowed_set)."""
    resolved = srfs_json_path.resolve()
    doc = load_selected_role_fact_set(resolved)
    plan = build_section_fact_plan(doc, "executive_summary")
    plan_facts = list(plan.get("facts") or [])
    envelope = build_srfs_integration_envelope(
        doc,
        executive_summary_plan_facts=plan_facts,
        artifact_path_resolved=str(resolved),
    )
    ordered_ids, allowed = build_allowed_fact_ids_for_plan_facts(plan_facts)
    return plan, envelope, ordered_ids, allowed


__all__ = [
    "build_allowed_fact_ids_for_plan_facts",
    "build_exec_summary_srfs_bundle",
    "build_srfs_integration_envelope",
    "load_srfs_document",
    "load_selected_role_fact_set",
    "metric_derivative_fact_id",
    "selected_fact_plan_from_srfs",
    "slice_row_to_plan_fact",
]
