"""EY Role Episode Bundle registry — graph-backed, employer-bound bundles.

Loads ey_role_episode_bundles.json and exposes typed accessors for ey_bullets/ey_narrative.
Enforces the role_episode_bundle_id gating invariant: EY bullets/narrative may only consume
graph context when a role_episode_bundle_id is explicitly bound, not from flat skill lists.

Mirror of ibm_graph_role_episode_registry.py (plan apps-rg-insurtech-ey-unlock-a4c0f0 W2/P2).
Identity is limited to the employment spine (company/title/location/dates); skills and claims are
grounded in graph role-episode bundles for the 2009-2014 window.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.sections.role_episode_bundle_registry import (
    get_all_role_episode_bundles,
    get_role_episode_bundle_by_id,
    get_role_episode_bundles_for_section,
    load_role_episode_bundle_doc,
    validate_no_surface_bullet_ids,
    validate_role_episode_bundle_base,
)

BUNDLES_PATH: Path = (
    Path(__file__).resolve().parents[3]
    / "apps_rg"
    / "fact_inventory"
    / "ey_role_episode_bundles.json"
)

# Immutable registry: employer and time window for all EY role episode bundles.
EY_EMPLOYER_ID: str = "Ernst & Young"
EY_EMPLOYER_NODE_ID: str = "employment_exp_ey_001"
EY_TIME_WINDOW: str = "2009-10 to 2014-03"

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
    "operating_context",
    "bullet_intent",
    "section_eligibility",
})

# EY held numeric claims ($15M, 40%, 12%) remain non-promotable. Graph-native metric outcome
# nodes carry the approved surface without those overloaded numeric claims.
HOLD_AND_DO_NOT_PROMOTE_METRICS: frozenset[str] = frozenset({
    "25%", "30%", "35%", "40%",
    "$15M", "15M", "12%",
})

VALID_SECTIONS: frozenset[str] = frozenset({"ey_bullets", "ey_narrative"})


def _load_bundles(path: Path = BUNDLES_PATH) -> dict[str, Any]:
    return load_role_episode_bundle_doc(path)


def get_all_bundles(path: Path = BUNDLES_PATH) -> list[dict[str, Any]]:
    """Return all EY role episode bundles."""
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
        employer_id=EY_EMPLOYER_ID,
        employer_node_id=EY_EMPLOYER_NODE_ID,
        valid_sections=VALID_SECTIONS,
        shared_sections={"competencies", "executive_summary"},
        require_linked_metric_outcome_ids=True,
    )

    violations.extend(
        validate_no_surface_bullet_ids(
            bundle,
            bullet_prefix="bul_ey_",
            label="EY",
        )
    )
    typed_edge_fields = {
        "graph_edge_contract",
        "root_to_skill_edges",
        "selected_edges",
        "selected_graph_edges",
        "edge_type",
        "typed_edges",
    }
    leaked_edge_fields = sorted(typed_edge_fields & set(bundle.keys()))
    if leaked_edge_fields:
        violations.append(
            f"typed-edge fields are excluded by EY edge policy: {leaked_edge_fields}"
        )

    for candidate in bundle.get("metric_candidates") or []:
        if not isinstance(candidate, dict):
            violations.append(f"metric_candidates must be structured metric records: {candidate}")
            continue
        for required in ("metric_id", "claim_text_pattern", "proof_shape", "approval_status"):
            if not str(candidate.get(required) or "").strip():
                violations.append(
                    f"metric candidate missing {required}: {candidate}"
                )
        if str(candidate.get("approval_status") or "").upper() == "PROMOTABLE":
            violations.append(
                f"metric candidate cannot be PROMOTABLE under EY metric policy: {candidate.get('metric_id')}"
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
