"""IBM Role Episode Bundle registry — graph-backed, employer-bound bundles for ibm_bullets/ibm_narrative.

This module loads ibm_role_episode_bundles.json and exposes typed accessors. It enforces
the role_episode_bundle_id gating invariant: IBM bullets/narrative may only consume graph
context when a role_episode_bundle_id is explicitly bound, not from flat skill lists.

Config gate: ibm_bullets and ibm_narrative graph_expansion_allowed remain false in
section_retrieval_profile.yaml until role_episode_bundle consumption is wired into the
section generation path. This module is a prerequisite but NOT sufficient alone.

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
    / "ibm_role_episode_bundles.json"
)

_BUNDLES_CACHE: dict[str, Any] | None = None

# Immutable registry: employer and time window for all IBM role episode bundles.
IBM_EMPLOYER_ID: str = "IBM"
IBM_EMPLOYER_NODE_ID: str = "employment_exp_ibm_001"
IBM_TIME_WINDOW: str = "2017-04 to 2022-10"

# Required fields for a valid role episode bundle.
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

# Metrics forbidden from promotion per gap fill report.
HOLD_AND_DO_NOT_PROMOTE_METRICS: frozenset[str] = frozenset({
    "25%", "30%", "35%", "40%",
    "$15M", "$30M",
    "15M", "30M",
})


def _load_bundles(path: Path = BUNDLES_PATH) -> dict[str, Any]:
    global _BUNDLES_CACHE
    if _BUNDLES_CACHE is None:
        with open(path, encoding="utf-8") as fh:
            _BUNDLES_CACHE = json.load(fh)
    return _BUNDLES_CACHE


def get_all_bundles(path: Path = BUNDLES_PATH) -> list[dict[str, Any]]:
    """Return all IBM role episode bundles."""
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

    # Required fields
    missing = REQUIRED_BUNDLE_FIELDS - set(bundle.keys())
    if missing:
        violations.append(f"Missing required fields: {sorted(missing)}")

    # Employer binding
    if bundle.get("employer") != IBM_EMPLOYER_ID:
        violations.append(
            f"employer must be '{IBM_EMPLOYER_ID}', got '{bundle.get('employer')}'"
        )
    if bundle.get("employer_node_id") != IBM_EMPLOYER_NODE_ID:
        violations.append(
            f"employer_node_id must be '{IBM_EMPLOYER_NODE_ID}', got '{bundle.get('employer_node_id')}'"
        )

    # Time window binding
    if not bundle.get("time_window"):
        violations.append("time_window is required and must not be empty")

    # Must have at least one graph_skill_node_id
    if not bundle.get("graph_skill_node_ids"):
        violations.append("graph_skill_node_ids must not be empty")

    # Section eligibility — ibm_bullets or ibm_narrative
    section_elig = bundle.get("section_eligibility") or []
    valid_sections = {"ibm_bullets", "ibm_narrative"}
    unknown = set(section_elig) - valid_sections - {"competencies", "executive_summary", "headline"}
    if unknown:
        violations.append(f"Unknown section_eligibility values: {sorted(unknown)}")

    # HOLD/DO_NOT_PROMOTE metrics must not appear in promotable_metrics
    promotable = bundle.get("promotable_metrics") or []
    for metric_entry in promotable:
        metric_str = str(metric_entry).upper()
        for forbidden in HOLD_AND_DO_NOT_PROMOTE_METRICS:
            if forbidden.upper() in metric_str:
                violations.append(
                    f"Forbidden metric '{forbidden}' found in promotable_metrics: {metric_entry}"
                )

    # Must NOT be created from flat skill-only nodes (guard: executive_scope_signals required)
    if not bundle.get("executive_scope_signals"):
        violations.append(
            "executive_scope_signals required: bundles must not be created from flat skill-only nodes"
        )

    return len(violations) == 0, violations


def assert_role_episode_bundle_id_present(context: dict[str, Any]) -> None:
    """Raise ValueError if role_episode_bundle_id is absent from context dict.

    IBM bullets/narrative may not consume graph context unless a role_episode_bundle_id is present.
    This is the config-gate guard: consumers MUST call this before using graph context.
    """
    rid = context.get("role_episode_bundle_id")
    if not rid:
        raise ValueError(
            "IBM bullets/narrative graph context requires role_episode_bundle_id. "
            "Consuming flat skill lists without bundle_id binding is forbidden. "
            "Config gate: ibm_bullets/ibm_narrative graph_expansion_allowed=false until "
            "role_episode_bundle consumption is wired. STATUS: BLOCKED_FOR_CONFIG_ENABLEMENT."
        )


def check_no_archive_prose_in_allowed_phrases(skill_row: dict[str, Any]) -> tuple[bool, str]:
    """Check that allowed_phrases does not contain archive claim prose.

    Archive prose fingerprints: complete sentences with subject+verb, '.' at end,
    or phrases that match common archive resume sentence patterns.
    Returns (is_clean, reason).
    """
    phrases = skill_row.get("allowed_phrases") or []
    for phrase in phrases:
        s = str(phrase).strip()
        # Simple heuristic: complete sentences have verb+subject patterns and end with '.'
        if s.endswith(".") and len(s.split()) > 8:
            return False, f"Possible archive prose sentence in allowed_phrases: '{s[:80]}'"
        # Archive prose typically has names, % claims, and $-amounts in full sentence
        if ("%" in s or "$" in s) and len(s.split()) > 10:
            return False, f"Possible unanchored metric claim in allowed_phrases: '{s[:80]}'"
    return True, "clean"
