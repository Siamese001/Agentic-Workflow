"""Headline positioning bundle registry — graph-backed positioning for the headline lane.

Loads headline_positioning_bundles.json and exposes typed accessors plus guards.
Positioning bundles draw from graph-backed competency capability bundles and graph
skill nodes; they are the proof authority for the headline. Base headline is calibration
only; JD/briefing are targeting only; E0 examples are style only.

Phase status: ENABLED_WITH_HEADLINE_POSITIONING_BUNDLE_GUARDS — graph_expansion consumes
positioning bundles only (never flat skill lists or JD-only phrases).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BUNDLES_PATH: Path = (
    Path(__file__).resolve().parents[3]
    / "apps_rg"
    / "fact_inventory"
    / "headline_positioning_bundles.json"
)

_BUNDLES_CACHE: dict[str, Any] | None = None

HEADLINE_SECTION_ID = "headline"

REQUIRED_POSITIONING_FAMILIES: tuple[str, ...] = (
    "svp_engineering_leadership",
    "agentic_ai_platforms",
    "distributed_ai_infrastructure",
    "runtime_governance",
    "enterprise_ai_architecture",
    "platform_productization",
    "regulated_ai_systems",
)

REQUIRED_BUNDLE_FIELDS: frozenset[str] = frozenset({
    "headline_positioning_bundle_id",
    "positioning_family",
    "display_phrase_candidate",
    "source_competency_bundle_ids",
    "graph_skill_node_ids",
    "seniority_signal",
    "technical_specificity_signal",
    "platform_signal",
    "governance_signal",
    "target_relevance_rationale",
    "allowed_sections",
    "activation_status",
    "external_claim_policy",
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
        if b.get("headline_positioning_bundle_id") == bundle_id:
            return b
    return None


def get_bundles_for_section(section_id: str = HEADLINE_SECTION_ID, path: Path = BUNDLES_PATH) -> list[dict[str, Any]]:
    return [b for b in get_all_bundles(path) if section_id in (b.get("allowed_sections") or [])]


def get_bundle_by_family(family: str, path: Path = BUNDLES_PATH) -> dict[str, Any] | None:
    for b in get_all_bundles(path):
        if b.get("positioning_family") == family:
            return b
    return None


def validate_bundle(bundle: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a headline positioning bundle against required schema and invariants."""
    violations: list[str] = []
    missing = REQUIRED_BUNDLE_FIELDS - set(bundle.keys())
    if missing:
        violations.append(f"Missing required fields: {sorted(missing)}")

    if bundle.get("allowed_sections") != [HEADLINE_SECTION_ID]:
        violations.append(
            f"allowed_sections must be ['headline'], got {bundle.get('allowed_sections')!r}"
        )
    if not bundle.get("graph_skill_node_ids"):
        violations.append("graph_skill_node_ids must not be empty (flat positioning forbidden)")
    if not bundle.get("source_competency_bundle_ids"):
        violations.append(
            "source_competency_bundle_ids must not be empty: positioning must draw from competency bundles"
        )
    # Must have source fact lineage OR graph lineage.
    has_facts = bool(bundle.get("linked_source_fact_ids"))
    has_lineage = bool(bundle.get("graph_lineage_refs"))
    if not (has_facts or has_lineage):
        violations.append("linked_source_fact_ids or graph_lineage_refs required (no bare positioning)")
    fam = bundle.get("positioning_family")
    if fam not in REQUIRED_POSITIONING_FAMILIES:
        violations.append(f"Unknown positioning_family: {fam!r}")
    return len(violations) == 0, violations


def assert_headline_positioning_bundle_id_present(context: dict[str, Any]) -> None:
    """Raise if headline graph context lacks a positioning bundle id binding."""
    rid = context.get("headline_positioning_bundle_id") or context.get(
        "headline_positioning_bundle_ids"
    )
    if not rid:
        raise ValueError(
            "Headline graph context requires headline_positioning_bundle_id(s). "
            "Consuming flat skill lists or JD-only phrases without bundle binding is forbidden."
        )


def reject_jd_only_positioning(display_phrase: str, jd_text: str, *, min_run: int = 5) -> None:
    """Raise when a display phrase is a long verbatim lift from JD (JD-as-proof leakage)."""
    from apps_rg.runtime.sections.cross_section_signal_guards import detect_jd_only_phrases

    hits = detect_jd_only_phrases(display_phrase, jd_text, min_run=min_run)
    if hits:
        raise ValueError(f"Headline positioning phrase lifted verbatim from JD: {hits}")


__all__ = [
    "BUNDLES_PATH",
    "HEADLINE_SECTION_ID",
    "REQUIRED_BUNDLE_FIELDS",
    "REQUIRED_POSITIONING_FAMILIES",
    "assert_headline_positioning_bundle_id_present",
    "get_all_bundles",
    "get_bundle_by_family",
    "get_bundle_by_id",
    "get_bundles_for_section",
    "reject_jd_only_positioning",
    "validate_bundle",
]
