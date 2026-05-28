"""Headline positioning bundle X2 gate helpers (graph-positioning consumption mode).

Active only when proof_pool_metadata indicates headline_positioning_bundle_consumption.
Enforces that the headline is composed from graph-backed positioning bundles (bundle id +
graph skill node ids + source fact/lineage), preserves SVP Engineering seniority, carries
platform/runtime and governance/regulated signals, and does not demote into generic IT
strategy labels, JD-only phrase stuffing, or E0/base hydration.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps_rg.runtime.validators.headline_quality_x2 import (
    HEADLINE_E0_REFERENCE_TEXTS,
    POSITIONING_FAMILIES,
    _POSITIONING_SIGNAL_TOKENS,
    check_headline_base_ngram_overlap,
    check_headline_e0_ngram_overlap,
    check_headline_no_narrowing_it_labels,
    check_headline_positioning_families,
    check_headline_seniority_floor,
)


@dataclass
class HeadlinePositioningResult:
    gate_id: str
    passed: bool
    observed_value: Any
    threshold: Any
    failure_reason: str | None


def headline_positioning_consumption_active(meta: dict[str, Any] | None) -> bool:
    return bool(isinstance(meta, dict) and meta.get("headline_positioning_bundle_consumption"))


def _collect_bindings(parsed_output: dict[str, Any] | None) -> dict[str, list[str]]:
    """Gather positioning bundle ids, graph skill ids, source fact/lineage ids from output."""
    bundle_ids: list[str] = []
    skill_ids: list[str] = []
    fact_or_lineage: list[str] = []
    po = parsed_output if isinstance(parsed_output, dict) else {}

    def _extend(dst: list[str], val: Any) -> None:
        if isinstance(val, str) and val.strip():
            dst.append(val.strip())
        elif isinstance(val, list):
            dst.extend(str(x).strip() for x in val if str(x).strip())

    _extend(bundle_ids, po.get("headline_positioning_bundle_ids"))
    _extend(bundle_ids, po.get("headline_positioning_bundle_id"))
    _extend(skill_ids, po.get("graph_skill_node_ids"))
    _extend(fact_or_lineage, po.get("source_fact_ids"))
    _extend(fact_or_lineage, po.get("graph_lineage_refs"))

    for entry in po.get("change_log") or []:
        if not isinstance(entry, dict):
            continue
        _extend(bundle_ids, entry.get("headline_positioning_bundle_id"))
        _extend(bundle_ids, entry.get("headline_positioning_bundle_ids"))
        _extend(skill_ids, entry.get("graph_skill_node_ids"))
        _extend(skill_ids, entry.get("skill_ids_used"))
        _extend(fact_or_lineage, entry.get("source_fact_ids"))
        _extend(fact_or_lineage, entry.get("graph_lineage_refs"))

    ja = po.get("jd_alignment")
    if isinstance(ja, dict):
        _extend(bundle_ids, ja.get("headline_positioning_bundle_ids"))
        _extend(skill_ids, ja.get("graph_skill_node_ids"))

    return {
        "bundle_ids": sorted(set(bundle_ids)),
        "skill_ids": sorted(set(skill_ids)),
        "fact_or_lineage": sorted(set(fact_or_lineage)),
    }


def run_headline_positioning_x2_gates(
    *,
    headline_line: str,
    parsed_output: dict[str, Any] | None,
    proof_pool_metadata: dict[str, Any] | None,
    jd_text: str = "",
    base_headline_texts: list[str] | None = None,
) -> list[HeadlinePositioningResult]:
    """Return the headline positioning bundle gate results (HARD where specified)."""
    results: list[HeadlinePositioningResult] = []

    def add(gate_id: str, passed: bool, observed: Any, threshold: Any, failure: str | None) -> None:
        results.append(HeadlinePositioningResult(gate_id, passed, observed, threshold, failure))

    meta = proof_pool_metadata if isinstance(proof_pool_metadata, dict) else {}
    packet = meta.get("headline_positioning_section_packet") or {}
    bundles_present = bool(meta.get("headline_positioning_bundles")) or bool(
        meta.get("headline_positioning_bundle_ids")
    )
    add(
        "x2_headline_positioning_bundles_in_proof_pool",
        bundles_present,
        {"bundles_present": bundles_present, "mode": meta.get("headline_positioning_bundle_consumption_mode")},
        "headline_positioning_bundles in proof_pool_metadata",
        None if bundles_present else "Headline proof pool missing positioning bundles.",
    )

    bindings = _collect_bindings(parsed_output)
    add(
        "x2_headline_positioning_bundle_id_required",
        bool(bindings["bundle_ids"]),
        bindings["bundle_ids"] or "none",
        ">=1 headline_positioning_bundle_id bound in output",
        None if bindings["bundle_ids"] else "No headline_positioning_bundle_id in output/change_log.",
    )
    add(
        "x2_headline_graph_skill_node_ids_required",
        bool(bindings["skill_ids"]),
        bindings["skill_ids"] or "none",
        ">=1 graph_skill_node_id bound in output",
        None if bindings["skill_ids"] else "No graph_skill_node_ids bound in output/change_log.",
    )
    add(
        "x2_headline_source_fact_or_graph_lineage_required",
        bool(bindings["fact_or_lineage"]),
        bindings["fact_or_lineage"] or "none",
        ">=1 source_fact_id or graph_lineage_ref bound in output",
        None if bindings["fact_or_lineage"] else "No source_fact_ids or graph_lineage_refs bound in output.",
    )

    # SVP Engineering seniority (HARD)
    sen0 = check_headline_seniority_floor(headline_line)
    add(
        "x2_headline_svp_engineering_seniority_required",
        sen0.passed,
        sen0.observed_value,
        sen0.threshold,
        sen0.failure_reason,
    )
    add(
        "x2_headline_seniority_floor_met",
        sen0.passed,
        sen0.observed_value,
        "segment 0 == 'SVP Engineering'",
        sen0.failure_reason,
    )

    # Platform OR runtime signal present (HARD)
    blob = " ".join(headline_line.split(" | ")[1:]).lower() if " | " in headline_line else headline_line.lower()
    tokens = set(blob.replace("|", " ").split())
    platform_runtime_families = ("agentic_ai_platforms", "distributed_ai_infrastructure", "runtime_governance", "platform_productization", "enterprise_ai_architecture")
    pr_hit = _families_matched(blob, tokens, platform_runtime_families)
    add(
        "x2_headline_platform_or_runtime_signal_required",
        bool(pr_hit),
        pr_hit or "none",
        ">=1 platform/runtime positioning family in headline",
        None if pr_hit else "Headline missing platform/runtime positioning signal.",
    )

    gov_families = ("runtime_governance", "regulated_ai_systems")
    gov_hit = _families_matched(blob, tokens, gov_families)
    add(
        "x2_headline_governance_or_regulated_ai_signal_required",
        bool(gov_hit),
        gov_hit or "none",
        ">=1 governance/regulated-AI positioning family in headline",
        None if gov_hit else "Headline missing governance/regulated-AI positioning signal.",
    )

    # Generic IT-strategy demotion forbidden (HARD)
    narrowing = check_headline_no_narrowing_it_labels(headline_line)
    add(
        "x2_headline_generic_it_strategy_demote_forbidden",
        narrowing.passed,
        narrowing.observed_value,
        narrowing.threshold,
        narrowing.failure_reason,
    )

    # JD-only phrase stuffing forbidden (HARD)
    from apps_rg.runtime.sections.cross_section_signal_guards import detect_jd_only_phrases

    jd_hits = detect_jd_only_phrases(headline_line, jd_text, min_run=4)
    add(
        "x2_headline_jd_only_phrase_forbidden",
        not jd_hits,
        jd_hits or "none",
        "no >=4-token verbatim JD lift in headline",
        f"JD-only phrase lift detected: {jd_hits}" if jd_hits else None,
    )

    # Technical specificity floor (HARD): >=2 positioning families
    fam = check_headline_positioning_families(headline_line, min_families=2)
    add(
        "x2_headline_technical_specificity_floor_met",
        fam.passed,
        fam.observed_value,
        fam.threshold,
        fam.failure_reason,
    )

    # E0 overlap forbidden (HARD in bundle mode)
    e0 = check_headline_e0_ngram_overlap(headline_line, HEADLINE_E0_REFERENCE_TEXTS, warn_only=False)
    add(
        "x2_headline_e0_ngram_overlap_forbidden",
        e0.passed,
        e0.observed_value,
        e0.threshold,
        e0.failure_reason,
    )

    # Base overlap forbidden-or-warn (WARN: tolerate calibration unless extreme)
    base = check_headline_base_ngram_overlap(headline_line, base_headline_texts or [], warn_only=True)
    add(
        "x2_headline_base_ngram_overlap_forbidden_or_warn",
        base.passed,
        base.observed_value,
        base.threshold,
        base.failure_reason,
    )

    return results


def _families_matched(blob: str, tokens: set[str], families: tuple[str, ...]) -> list[str]:
    matched: list[str] = []
    for fam in families:
        phrases = POSITIONING_FAMILIES.get(fam, frozenset())
        if any(p in blob for p in phrases):
            matched.append(fam)
            continue
        signal_tokens = _POSITIONING_SIGNAL_TOKENS.get(fam, frozenset())
        if signal_tokens & tokens:
            matched.append(fam)
    return list(dict.fromkeys(matched))


__all__ = [
    "HeadlinePositioningResult",
    "headline_positioning_consumption_active",
    "run_headline_positioning_x2_gates",
]
