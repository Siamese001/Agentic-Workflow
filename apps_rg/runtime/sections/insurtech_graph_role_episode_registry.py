"""InsurTech Role Episode Bundle registry — graph-backed, employer-bound bundles.

Loads insurtech_role_episode_bundles.json and exposes typed accessors for
insurtech_bullets/insurtech_narrative. Enforces the role_episode_bundle_id gating invariant:
InsurTech bullets/narrative may only consume graph context when a role_episode_bundle_id is
explicitly bound, not from flat skill lists.

Mirror of ibm_graph_role_episode_registry.py (plan apps-rg-insurtech-ey-unlock-a4c0f0 W2/P2).
Identity is limited to the employment spine (company/title/location/dates); skills and claims are
grounded in graph role-episode bundles for the 2014-2017 window.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BUNDLES_PATH: Path = (
    Path(__file__).resolve().parents[3]
    / "apps_rg"
    / "fact_inventory"
    / "insurtech_role_episode_bundles.json"
)

_BUNDLES_CACHE: dict[str, Any] | None = None

# Immutable registry: employer and time window for all InsurTech role episode bundles.
INSURTECH_EMPLOYER_ID: str = "InsurTech Cloud Solutions"
INSURTECH_EMPLOYER_NODE_ID: str = "employment_exp_insurtech_001"
INSURTECH_TIME_WINDOW: str = "2014-04 to 2017-03"

# Required fields for a valid role episode bundle (mirrors IBM registry).
REQUIRED_BUNDLE_FIELDS: frozenset[str] = frozenset({
    "role_episode_bundle_id",
    "employer",
    "title",
    "employer_node_id",
    "bundle_theme",
    "claim_text",
    "support_level",
    "executive_scope_signals",
    "architecture_scope_signals",
    "graph_skill_node_ids",
    "linked_source_fact_ids",
    "linked_archive_signal_ids",
    "linked_metric_outcome_ids",
    "metric_candidates",
    "graph_edge_contract",
    "operating_context",
    "bullet_intent",
    "section_eligibility",
})

# Metrics forbidden from promotion (overloaded / insufficiently sourced). InsurTech TCO and
# uptime percentages remain HELD; graph-native metric outcome nodes carry the approved surface.
HOLD_AND_DO_NOT_PROMOTE_METRICS: frozenset[str] = frozenset({
    "25%", "30%", "35%", "40%",
    "99.99%",
    "SAVED $10M",
    "$10M TCO",
    "10M TCO",
    "GENERIC TCO",
})

VALID_SECTIONS: frozenset[str] = frozenset({"insurtech_bullets", "insurtech_narrative"})


def _load_bundles(path: Path = BUNDLES_PATH) -> dict[str, Any]:
    global _BUNDLES_CACHE
    if _BUNDLES_CACHE is None:
        with open(path, encoding="utf-8") as fh:
            _BUNDLES_CACHE = json.load(fh)
    return _BUNDLES_CACHE


def get_all_bundles(path: Path = BUNDLES_PATH) -> list[dict[str, Any]]:
    """Return all InsurTech role episode bundles."""
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

    if bundle.get("employer") != INSURTECH_EMPLOYER_ID:
        violations.append(
            f"employer must be '{INSURTECH_EMPLOYER_ID}', got '{bundle.get('employer')}'"
        )
    if bundle.get("employer_node_id") != INSURTECH_EMPLOYER_NODE_ID:
        violations.append(
            f"employer_node_id must be '{INSURTECH_EMPLOYER_NODE_ID}', got '{bundle.get('employer_node_id')}'"
        )

    if not bundle.get("graph_skill_node_ids"):
        violations.append("graph_skill_node_ids must not be empty")
    if not bundle.get("linked_metric_outcome_ids"):
        violations.append("linked_metric_outcome_ids must not be empty")

    bundle_blob = json.dumps(bundle, sort_keys=True)
    if "bul_insurtech_" in bundle_blob:
        violations.append(
            "base-resume bullet ids are forbidden as InsurTech graph proof; use role_episode_bundle_id"
        )

    section_elig = bundle.get("section_eligibility") or []
    unknown = set(section_elig) - VALID_SECTIONS - {"competencies", "executive_summary"}
    if unknown:
        violations.append(f"Unknown section_eligibility values: {sorted(unknown)}")

    for candidate in bundle.get("metric_candidates") or []:
        candidate_text = str(candidate).upper()
        if "METRIC_ID" not in candidate_text or "CLAIM_TEXT_PATTERN" not in candidate_text:
            violations.append(
                f"metric_candidates must be structured metric records: {candidate}"
            )
        for forbidden in ("SAVED $10M", "$10M TCO", "10M TCO"):
            if forbidden in candidate_text:
                violations.append(
                    f"Generic absolute TCO claim '{forbidden}' found in metric_candidates: {candidate}"
                )

    edge_contract = bundle.get("graph_edge_contract") or {}
    if not isinstance(edge_contract, dict) or not edge_contract.get("root_to_skill_edges"):
        violations.append("graph_edge_contract.root_to_skill_edges must bind root bundle to skills")

    if not bundle.get("executive_scope_signals"):
        violations.append(
            "executive_scope_signals required: bundles must not be created from flat skill-only nodes"
        )

    return len(violations) == 0, violations


def assert_role_episode_bundle_id_present(context: dict[str, Any]) -> None:
    """Raise ValueError if role_episode_bundle_id is absent from context dict.

    InsurTech bullets/narrative may not consume graph context unless a role_episode_bundle_id
    is present. This is the config-gate guard: consumers MUST call this before using graph context.
    """
    rid = context.get("role_episode_bundle_id")
    if not rid:
        raise ValueError(
            "InsurTech bullets/narrative graph context requires role_episode_bundle_id. "
            "Consuming flat skill lists without bundle_id binding is forbidden. "
            "STATUS: ROLE_EPISODE_BUNDLE_ID_REQUIRED."
        )
