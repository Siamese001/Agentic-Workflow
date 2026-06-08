"""EY Role Episode Bundle registry — graph-backed, employer-bound bundles.

Loads ey_role_episode_bundles.json and exposes typed accessors for ey_bullets/ey_narrative.
Enforces the role_episode_bundle_id gating invariant: EY bullets/narrative may only consume
graph context when a role_episode_bundle_id is explicitly bound, not from flat skill lists.

Mirror of ibm_graph_role_episode_registry.py (plan apps-rg-insurtech-ey-unlock-a4c0f0 W2/P2).
Identity is verbatim from the base resume (employment block exp_ey_001); skills are grounded in
master_skills_arsenal_ledger graph nodes for the 2009-2014 window.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BUNDLES_PATH: Path = (
    Path(__file__).resolve().parents[3]
    / "apps_rg"
    / "fact_inventory"
    / "ey_role_episode_bundles.json"
)

_BUNDLES_CACHE: dict[str, Any] | None = None

# Immutable registry: employer and time window for all EY role episode bundles.
EY_EMPLOYER_ID: str = "Ernst & Young"
EY_EMPLOYER_NODE_ID: str = "employment_exp_ey_001"
EY_TIME_WINDOW: str = "2009-10 to 2014-03"

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
    "linked_archive_signal_ids",
    "operating_context",
    "bullet_intent",
    "section_eligibility",
})

# Base-resume EY metrics ($15M, 40%, 12%) are HELD, never promotable, until X2 rules (P4).
HOLD_AND_DO_NOT_PROMOTE_METRICS: frozenset[str] = frozenset({
    "25%", "30%", "35%", "40%",
    "$15M", "15M", "12%",
})

VALID_SECTIONS: frozenset[str] = frozenset({"ey_bullets", "ey_narrative"})


def _load_bundles(path: Path = BUNDLES_PATH) -> dict[str, Any]:
    global _BUNDLES_CACHE
    if _BUNDLES_CACHE is None:
        with open(path, encoding="utf-8") as fh:
            _BUNDLES_CACHE = json.load(fh)
    return _BUNDLES_CACHE


def get_all_bundles(path: Path = BUNDLES_PATH) -> list[dict[str, Any]]:
    """Return all EY role episode bundles."""
    return list(_load_bundles(path).get("bundles", []))


def get_bundle_by_id(bundle_id: str, path: Path = BUNDLES_PATH) -> dict[str, Any] | None:
    """Return a single role episode bundle by ID, or None if not found."""
    for b in get_all_bundles(path):
        if b.get("role_episode_bundle_id") == bundle_id:
            return b
    return None


def get_bundles_for_section(section_id: str, path: Path = BUNDLES_PATH) -> list[dict[str, Any]]:
    """Return bundles eligible for the given section_id."""
    return [
        b for b in get_all_bundles(path)
        if section_id in (b.get("section_eligibility") or [])
    ]


def validate_bundle(bundle: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a role episode bundle against required schema and invariants.

    Returns (is_valid, list_of_violations).
    """
    violations: list[str] = []

    missing = REQUIRED_BUNDLE_FIELDS - set(bundle.keys())
    if missing:
        violations.append(f"Missing required fields: {sorted(missing)}")

    if bundle.get("employer") != EY_EMPLOYER_ID:
        violations.append(
            f"employer must be '{EY_EMPLOYER_ID}', got '{bundle.get('employer')}'"
        )
    if bundle.get("employer_node_id") != EY_EMPLOYER_NODE_ID:
        violations.append(
            f"employer_node_id must be '{EY_EMPLOYER_NODE_ID}', got '{bundle.get('employer_node_id')}'"
        )

    if not bundle.get("time_window"):
        violations.append("time_window is required and must not be empty")

    if not bundle.get("graph_skill_node_ids"):
        violations.append("graph_skill_node_ids must not be empty")

    section_elig = bundle.get("section_eligibility") or []
    unknown = set(section_elig) - VALID_SECTIONS - {"competencies", "executive_summary"}
    if unknown:
        violations.append(f"Unknown section_eligibility values: {sorted(unknown)}")

    promotable = bundle.get("promotable_metrics") or []
    for metric_entry in promotable:
        metric_str = str(metric_entry).upper()
        for forbidden in HOLD_AND_DO_NOT_PROMOTE_METRICS:
            if forbidden.upper() in metric_str:
                violations.append(
                    f"Forbidden metric '{forbidden}' found in promotable_metrics: {metric_entry}"
                )

    if not bundle.get("executive_scope_signals"):
        violations.append(
            "executive_scope_signals required: bundles must not be created from flat skill-only nodes"
        )

    return len(violations) == 0, violations


def assert_role_episode_bundle_id_present(context: dict[str, Any]) -> None:
    """Raise ValueError if role_episode_bundle_id is absent from context dict."""
    rid = context.get("role_episode_bundle_id")
    if not rid:
        raise ValueError(
            "EY bullets/narrative graph context requires role_episode_bundle_id. "
            "Consuming flat skill lists without bundle_id binding is forbidden. "
            "STATUS: BLOCKED_FOR_CONFIG_ENABLEMENT."
        )
