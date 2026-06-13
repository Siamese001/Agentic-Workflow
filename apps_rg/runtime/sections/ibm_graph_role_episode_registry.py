"""IBM Role Episode Bundle registry — graph-backed, employer-bound bundles for ibm_bullets/ibm_narrative.

This module loads ibm_role_episode_bundles.json and exposes typed accessors. It enforces
the role_episode_bundle_id gating invariant: IBM bullets/narrative may only consume graph
context when a role_episode_bundle_id is explicitly bound, not from flat skill lists.

Config gate: ibm_bullets and ibm_narrative graph_expansion_allowed remain false in
section_retrieval_profile.yaml until role_episode_bundle consumption is wired into the
section generation path. This module is a prerequisite but NOT sufficient alone.

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

BUNDLES_PATH: Path = (
    Path(__file__).resolve().parents[3]
    / "apps_rg"
    / "fact_inventory"
    / "ibm_role_episode_bundles.json"
)

# Immutable registry: employer and time window for all IBM role episode bundles.
IBM_EMPLOYER_ID: str = "IBM"
IBM_EMPLOYER_NODE_ID: str = "employment_exp_ibm_001"
IBM_TIME_WINDOW: str = "2017-04 to 2022-10"

# Required fields for a valid role episode bundle.
REQUIRED_BUNDLE_FIELDS: frozenset[str] = frozenset({
    "role_episode_bundle_id",
    "employer",
    "title",
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
    return load_role_episode_bundle_doc(path)


def get_all_bundles(path: Path = BUNDLES_PATH) -> list[dict[str, Any]]:
    """Return all IBM role episode bundles."""
    return get_all_role_episode_bundles(path)


def get_bundle_by_id(bundle_id: str, path: Path = BUNDLES_PATH) -> dict[str, Any] | None:
    """Return a single role episode bundle by ID, or None if not found."""
    return get_role_episode_bundle_by_id(path, bundle_id)


def get_bundles_for_section(section_id: str, path: Path = BUNDLES_PATH) -> list[dict[str, Any]]:
    """Return bundles eligible for the given section_id."""
    return get_role_episode_bundles_for_section(path, section_id)


def validate_bundle(bundle: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a role episode bundle against required schema and invariants.

    Returns (is_valid, list_of_violations).
    """
    violations = validate_role_episode_bundle_base(
        bundle,
        required_fields=REQUIRED_BUNDLE_FIELDS,
        employer_id=IBM_EMPLOYER_ID,
        employer_node_id=IBM_EMPLOYER_NODE_ID,
        valid_sections={"ibm_bullets", "ibm_narrative"},
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
