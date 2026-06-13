"""Generic registry helpers for employer role episode bundle graphs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

DEFAULT_SHARED_SECTIONS: frozenset[str] = frozenset(
    {"competencies", "executive_summary", "headline"}
)

COMMON_ROLE_EPISODE_BUNDLE_FIELDS: tuple[str, ...] = (
    "role_episode_bundle_id",
    "employer",
    "title",
    "employer_node_id",
    "root_capability_node_id",
    "bundle_theme",
    "claim_text",
    "claim_action",
    "claim_scope",
    "claim_outcome",
    "support_level",
    "executive_scope_signals",
    "architecture_scope_signals",
    "graph_skill_node_ids",
    "linked_source_fact_ids",
    "linked_archive_signal_ids",
    "linked_metric_outcome_ids",
    "held_metrics",
    "excluded_metrics",
    "metric_candidates",
    "operating_context",
    "bullet_intent",
    "section_eligibility",
    "external_claim_policy",
    "activation_status",
    "config_gate",
    "notes",
)

def load_role_episode_bundle_doc(path: Path) -> dict[str, Any]:
    """Load a role-episode graph document from disk."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def get_all_role_episode_bundles(path: Path) -> list[dict[str, Any]]:
    """Return all role episode bundles from a graph document."""
    return list(load_role_episode_bundle_doc(path).get("bundles", []))


def get_role_episode_bundle_by_id(path: Path, bundle_id: str) -> dict[str, Any] | None:
    """Return one role episode bundle by ID."""
    target = str(bundle_id or "").strip()
    for bundle in get_all_role_episode_bundles(path):
        if bundle.get("role_episode_bundle_id") == target:
            return bundle
    return None


def get_role_episode_bundles_for_section(path: Path, section_id: str) -> list[dict[str, Any]]:
    """Return bundles eligible for a section."""
    section = str(section_id or "").strip()
    return [
        bundle
        for bundle in get_all_role_episode_bundles(path)
        if section in (bundle.get("section_eligibility") or [])
    ]


def validate_role_episode_bundle_base(
    bundle: dict[str, Any],
    *,
    required_fields: Iterable[str],
    employer_id: str,
    employer_node_id: str,
    valid_sections: Iterable[str],
    valid_employer_labels: Iterable[str] | None = None,
    shared_sections: Iterable[str] = DEFAULT_SHARED_SECTIONS,
    require_graph_skill_node_ids: bool = True,
    require_linked_metric_outcome_ids: bool = False,
    require_executive_scope_signals: bool = True,
) -> list[str]:
    """Common role-episode bundle validation shared by employer wrappers."""
    violations: list[str] = []

    missing = set(required_fields) - set(bundle.keys())
    if missing:
        violations.append(f"Missing required fields: {sorted(missing)}")

    labels = set(valid_employer_labels or (employer_id,))
    if bundle.get("employer") not in labels:
        violations.append(
            f"employer must be one of {sorted(labels)}, got {bundle.get('employer')!r}"
        )
    if bundle.get("employer_node_id") != employer_node_id:
        violations.append(
            f"employer_node_id must be '{employer_node_id}', got {bundle.get('employer_node_id')!r}"
        )

    if require_graph_skill_node_ids and not bundle.get("graph_skill_node_ids"):
        violations.append("graph_skill_node_ids must not be empty")
    if require_linked_metric_outcome_ids and not bundle.get("linked_metric_outcome_ids"):
        violations.append("linked_metric_outcome_ids must not be empty")
    if require_executive_scope_signals and not bundle.get("executive_scope_signals"):
        violations.append(
            "executive_scope_signals required: bundles must not be created from flat skill-only nodes"
        )

    allowed_sections = set(valid_sections) | set(shared_sections)
    unknown = set(bundle.get("section_eligibility") or []) - allowed_sections
    if unknown:
        violations.append(f"Unknown section_eligibility values: {sorted(unknown)}")

    return violations


def validate_no_surface_bullet_ids(
    bundle: dict[str, Any],
    *,
    bullet_prefix: str,
    label: str,
) -> list[str]:
    """Ensure presentation bullet IDs do not appear inside graph proof bundles."""
    if bullet_prefix and bullet_prefix in json.dumps(bundle, sort_keys=True):
        return [
            f"base-resume bullet ids are forbidden as {label} graph proof; use role_episode_bundle_id"
        ]
    return []
