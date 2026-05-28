"""Unify Role Episode Bundle registry — graph-backed, employer-bound bundles for unify lanes.

Loads unify_role_episode_bundles.json and exposes typed accessors plus guards. Enforces
the role_episode_bundle_id gating invariant: unify_bullets/unify_narrative may only consume
graph context when a role_episode_bundle_id is explicitly bound, not from flat skill lists.

Phase status: ENABLED_WITH_ROLE_EPISODE_BUNDLE_GUARDS — graph_expansion consumes bundles only.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BUNDLES_PATH: Path = (
    Path(__file__).resolve().parents[3]
    / "apps_rg"
    / "fact_inventory"
    / "unify_role_episode_bundles.json"
)

_BUNDLES_CACHE: dict[str, Any] | None = None

UNIFY_EMPLOYER_ID: str = "Unify"
UNIFY_EMPLOYER_NODE_ID: str = "employment_exp_unify_001"
UNIFY_TIME_WINDOW: str = "2023-02 to present"

# Accept either canonical short label or full firm label on bundle.employer.
_VALID_EMPLOYER_LABELS: frozenset[str] = frozenset({"Unify", "Unify Consulting"})

REQUIRED_BUNDLE_FIELDS: frozenset[str] = frozenset({
    "role_episode_bundle_id",
    "employer",
    "title",
    "time_window",
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

# Approved & linked metric outcome ids (allow-list for metric-bearing claims).
APPROVED_METRIC_OUTCOME_IDS: tuple[str, ...] = (
    "metric_unify_22m_ip_led_revenue",
    "metric_unify_20pct_gross_margin_expansion",
    "metric_unify_team_scaled_8_to_28",
    "metric_unify_cycle_six_months_to_three_weeks",
)

# Conditional — only if already canonical and linked; HOLD by default.
CONDITIONAL_METRIC_OUTCOME_IDS: tuple[str, ...] = (
    "metric_unify_14m_operating_capacity",
)

VALID_ACTIVATION_STATUS: frozenset[str] = frozenset({
    "ACTIVE_CONFIRMED",
    "ACTIVE_INTERNAL_ONLY",
    "DRAFT",
    "BLOCKED_NO_SOURCE",
    "SUPPORTING_CONTEXT_ONLY",
})


def _load_bundles(path: Path = BUNDLES_PATH) -> dict[str, Any]:
    global _BUNDLES_CACHE
    if _BUNDLES_CACHE is None:
        with open(path, encoding="utf-8") as fh:
            _BUNDLES_CACHE = json.load(fh)
    return _BUNDLES_CACHE


def get_all_bundles(path: Path = BUNDLES_PATH) -> list[dict[str, Any]]:
    return list(_load_bundles(path).get("bundles", []))


def get_bundle_by_id(bundle_id: str, path: Path = BUNDLES_PATH) -> dict[str, Any] | None:
    for b in get_all_bundles(path):
        if b.get("role_episode_bundle_id") == bundle_id:
            return b
    return None


def get_bundles_for_section(section_id: str, path: Path = BUNDLES_PATH) -> list[dict[str, Any]]:
    return [
        b for b in get_all_bundles(path)
        if section_id in (b.get("section_eligibility") or [])
    ]


def validate_bundle(bundle: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a Unify role episode bundle against required schema and invariants."""
    violations: list[str] = []
    missing = REQUIRED_BUNDLE_FIELDS - set(bundle.keys())
    if missing:
        violations.append(f"Missing required fields: {sorted(missing)}")

    if bundle.get("employer") not in _VALID_EMPLOYER_LABELS:
        violations.append(
            f"employer must be one of {sorted(_VALID_EMPLOYER_LABELS)}, got {bundle.get('employer')!r}"
        )
    if bundle.get("employer_node_id") != UNIFY_EMPLOYER_NODE_ID:
        violations.append(
            f"employer_node_id must be '{UNIFY_EMPLOYER_NODE_ID}', got {bundle.get('employer_node_id')!r}"
        )
    if not bundle.get("time_window"):
        violations.append("time_window is required and must not be empty")
    if not bundle.get("graph_skill_node_ids"):
        violations.append("graph_skill_node_ids must not be empty")
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

    # Metric outcome ids must be approved (or conditional).
    allowed = set(APPROVED_METRIC_OUTCOME_IDS) | set(CONDITIONAL_METRIC_OUTCOME_IDS)
    for mid in bundle.get("linked_metric_outcome_ids") or []:
        if str(mid) not in allowed:
            violations.append(f"Unapproved metric_outcome_id in bundle: {mid}")

    section_elig = set(bundle.get("section_eligibility") or [])
    valid_sections = {"unify_bullets", "unify_narrative", "competencies", "headline"}
    unknown = section_elig - valid_sections
    if unknown:
        violations.append(f"Unknown section_eligibility values: {sorted(unknown)}")

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
    "CONDITIONAL_METRIC_OUTCOME_IDS",
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
