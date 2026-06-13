"""Unify Role Episode Bundle registry — graph-backed, employer-bound bundles for unify lanes.

Loads unify_role_episode_bundles.json and exposes typed accessors plus guards. Enforces
the role_episode_bundle_id gating invariant: unify_bullets/unify_narrative may only consume
graph context when a role_episode_bundle_id is explicitly bound, not from flat skill lists.

Runtime status: ENABLED_WITH_ROLE_EPISODE_BUNDLE_GUARDS — graph_expansion consumes bundles only.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.sections.role_episode_bundle_registry import (
    get_all_role_episode_bundles,
    get_role_episode_bundle_by_id,
    get_role_episode_bundles_for_section,
    load_role_episode_bundle_doc,
    validate_role_episode_bundle_base,
)
from apps_rg.runtime.sections.role_episode_metric_registry import (
    approved_metric_outcome_ids_from_path,
)

BUNDLES_PATH: Path = (
    Path(__file__).resolve().parents[3]
    / "apps_rg"
    / "fact_inventory"
    / "unify_role_episode_bundles.json"
)

UNIFY_EMPLOYER_ID: str = "Unify"
UNIFY_EMPLOYER_NODE_ID: str = "employment_exp_unify_001"
UNIFY_TIME_WINDOW: str = "2023-02 to present"

# Accept either canonical short label or full firm label on bundle.employer.
_VALID_EMPLOYER_LABELS: frozenset[str] = frozenset({"Unify", "Unify Consulting"})

REQUIRED_BUNDLE_FIELDS: frozenset[str] = frozenset({
    "role_episode_bundle_id",
    "employer",
    "title",
    "employer_node_id",
    "executive_scope_signals",
    "architecture_scope_signals",
    "graph_skill_node_ids",
    "linked_source_fact_ids",
    "operating_context",
    "bullet_intent",
    "section_eligibility",
    "external_claim_policy",
    "activation_status",
})

# Metric approval is graph-native: presence in metric_outcome_nodes.
APPROVED_METRIC_OUTCOME_IDS: tuple[str, ...] = approved_metric_outcome_ids_from_path(BUNDLES_PATH)

VALID_ACTIVATION_STATUS: frozenset[str] = frozenset({
    "ACTIVE_CONFIRMED",
    "ACTIVE_INTERNAL_ONLY",
    "DRAFT",
    "BLOCKED_NO_SOURCE",
    "SUPPORTING_CONTEXT_ONLY",
})


def _load_bundles(path: Path = BUNDLES_PATH) -> dict[str, Any]:
    return load_role_episode_bundle_doc(path)


def get_all_bundles(path: Path = BUNDLES_PATH) -> list[dict[str, Any]]:
    return get_all_role_episode_bundles(path)


def get_bundle_by_id(bundle_id: str, path: Path = BUNDLES_PATH) -> dict[str, Any] | None:
    return get_role_episode_bundle_by_id(path, bundle_id)


def get_bundles_for_section(section_id: str, path: Path = BUNDLES_PATH) -> list[dict[str, Any]]:
    return get_role_episode_bundles_for_section(path, section_id)


def validate_bundle(bundle: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a Unify role episode bundle against required schema and invariants."""
    violations = validate_role_episode_bundle_base(
        bundle,
        required_fields=REQUIRED_BUNDLE_FIELDS,
        employer_id=UNIFY_EMPLOYER_ID,
        employer_node_id=UNIFY_EMPLOYER_NODE_ID,
        valid_sections={"unify_bullets", "unify_narrative", "competencies", "headline"},
        valid_employer_labels=_VALID_EMPLOYER_LABELS,
        shared_sections=(),
    )
    # Source fact lineage OR explicit internal-only classification with graph nodes.
    if not bundle.get("linked_source_fact_ids") and bundle.get("external_claim_policy") not in (
        "internal_only_not_external_claim",
    ):
        violations.append(
            "linked_source_fact_ids required unless external_claim_policy=internal_only_not_external_claim"
        )
    if not bundle.get("executive_scope_signals"):
        violations.append(
            "executive_scope_signals required: bundles must not be created from flat skill-only nodes"
        )
    if bundle.get("activation_status") not in VALID_ACTIVATION_STATUS:
        violations.append(f"Unknown activation_status: {bundle.get('activation_status')!r}")

    # Metric outcome ids must be present in metric_outcome_nodes.
    allowed = set(APPROVED_METRIC_OUTCOME_IDS)
    for mid in bundle.get("linked_metric_outcome_ids") or []:
        if str(mid) not in allowed:
            violations.append(f"Unapproved metric_outcome_id in bundle: {mid}")

    return len(violations) == 0, violations


def assert_role_episode_bundle_id_present(context: dict[str, Any]) -> None:
    """Raise if Unify graph context lacks a role_episode_bundle_id binding."""
    rid = context.get("role_episode_bundle_id") or context.get("role_episode_bundle_ids")
    if not rid:
        raise ValueError(
            "Unify bullets/narrative graph context requires role_episode_bundle_id. "
            "Consuming flat skill lists without bundle binding is forbidden."
        )


__all__ = [
    "APPROVED_METRIC_OUTCOME_IDS",
    "BUNDLES_PATH",
    "REQUIRED_BUNDLE_FIELDS",
    "UNIFY_EMPLOYER_ID",
    "UNIFY_EMPLOYER_NODE_ID",
    "UNIFY_TIME_WINDOW",
    "VALID_ACTIVATION_STATUS",
    "assert_role_episode_bundle_id_present",
    "get_all_bundles",
    "get_bundle_by_id",
    "get_bundles_for_section",
    "validate_bundle",
]
