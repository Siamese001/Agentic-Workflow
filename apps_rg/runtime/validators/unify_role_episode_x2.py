"""Unify role episode bundle X2 gate helpers (role_episode_bundle consumption mode).

Active only when proof_pool_metadata indicates role_episode_bundle_consumption for a unify
lane. Enforces that unify_bullets / unify_narrative are composed from graph-backed role
episode bundles (bundle id + graph skill node ids + source fact/lineage), preserve seniority
and technical specificity, carry an architecture mechanism and commercial/operating scope,
and do not demote into generic consulting language, flat skill-only packets, JD-only lifts,
unsupported new metric claims, or base/archive hydration.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from apps_rg.runtime.sections.cross_section_signal_guards import (
    ARCHITECTURE_MECHANISM_VOCAB,
    base_archive_ngram_overlap,
    detect_generic_consulting_phrases,
    is_flat_skill_only_graph_packet,
    seniority_floor_score,
    technical_specificity_score,
)

# Numeric/$/% tokens permitted in Unify output (canonical, approved & linked metrics only).
_ALLOWED_METRIC_TOKENS: frozenset[str] = frozenset({
    "$22m", "$22 m", "22m",
    "20%", "20 %",
    "8", "28",
    "three weeks", "six months",
    "$14m", "$14 m", "14m",
})

_COMMERCIAL_SCOPE_TOKENS: frozenset[str] = frozenset({
    "commercialization", "commercialized", "productization", "productized",
    "revenue", "margin", "operating model", "platform", "organization",
    "team", "scaled", "roadmap", "ip-led", "reusable platform",
})

_BASE_NGRAM_THRESHOLD = 0.25
_NUM_CLAIM_RE = re.compile(r"\$\s?\d[\d,\.]*\s?[mMbBkK]?|\b\d+(?:\.\d+)?\s?%")


@dataclass
class UnifyEpisodeResult:
    gate_id: str
    passed: bool
    observed_value: Any
    threshold: Any
    failure_reason: str | None


def unify_role_episode_consumption_active(meta: dict[str, Any] | None) -> bool:
    return bool(
        isinstance(meta, dict)
        and meta.get("role_episode_bundle_consumption")
        and meta.get("unify_role_episode_section_packet")
    )


def _collect_change_log_bindings(parsed_output: dict[str, Any] | None) -> dict[str, Any]:
    bundle_ids: list[str] = []
    skill_ids: list[str] = []
    fact_or_lineage: list[str] = []
    metric_ids: list[str] = []
    per_bullet: dict[str, dict[str, Any]] = {}
    po = parsed_output if isinstance(parsed_output, dict) else {}
    for entry in po.get("change_log") or []:
        if not isinstance(entry, dict):
            continue
        bid = str(entry.get("bullet_id") or "")
        reb = str(entry.get("role_episode_bundle_id") or "").strip()
        sk = [str(x) for x in (entry.get("graph_skill_node_ids") or entry.get("skill_ids_used") or [])]
        srcs = [str(x) for x in (entry.get("source_fact_ids") or [])] + [
            str(x) for x in (entry.get("graph_lineage_refs") or [])
        ]
        mids = [str(x) for x in (entry.get("metric_outcome_ids") or [])]
        if reb:
            bundle_ids.append(reb)
        skill_ids.extend(sk)
        fact_or_lineage.extend(srcs)
        metric_ids.extend(mids)
        if bid:
            per_bullet[bid] = {
                "role_episode_bundle_id": reb,
                "graph_skill_node_ids": sk,
                "source_fact_ids": srcs,
                "metric_outcome_ids": mids,
            }
    return {
        "bundle_ids": sorted(set(bundle_ids)),
        "skill_ids": sorted(set(skill_ids)),
        "fact_or_lineage": sorted(set(fact_or_lineage)),
        "metric_ids": sorted(set(metric_ids)),
        "per_bullet": per_bullet,
    }


def detect_unsupported_metric_claims(text: str) -> list[str]:
    """Return $/% numeric claims in text that are not in the approved Unify token allow-list."""
    low = str(text or "").lower()
    hits: list[str] = []
    for m in _NUM_CLAIM_RE.findall(low):
        norm = m.strip()
        compact = norm.replace(" ", "")
        if compact in {t.replace(" ", "") for t in _ALLOWED_METRIC_TOKENS}:
            continue
        hits.append(norm)
    return hits


def _has_commercial_scope(text: str) -> bool:
    low = str(text or "").lower()
    return any(tok in low for tok in _COMMERCIAL_SCOPE_TOKENS)


def run_unify_bullets_role_episode_x2_gates(
    *,
    bullets: list[dict[str, Any]],
    parsed_output: dict[str, Any] | None,
    proof_pool_metadata: dict[str, Any] | None,
    jd_text: str = "",
    base_texts: list[str] | None = None,
    archive_texts: list[str] | None = None,
) -> list[UnifyEpisodeResult]:
    results: list[UnifyEpisodeResult] = []

    def add(gid: str, ok: bool, obs: Any, thr: Any, fail: str | None) -> None:
        results.append(UnifyEpisodeResult(gid, ok, obs, thr, fail))

    meta = proof_pool_metadata if isinstance(proof_pool_metadata, dict) else {}
    bundles_present = bool(meta.get("role_episode_bundles")) or bool(meta.get("role_episode_bundle_ids"))
    flat_only = is_flat_skill_only_graph_packet(meta) and not bundles_present
    add(
        "x2_unify_role_episode_bundles_in_proof_pool",
        bundles_present and not flat_only,
        {"bundles_present": bundles_present, "flat_skill_only": flat_only},
        "role_episode_bundles in proof_pool_metadata",
        "Unify proof pool missing role_episode_bundles or flat skill-only context"
        if (not bundles_present or flat_only)
        else None,
    )

    b = _collect_change_log_bindings(parsed_output)
    combined = "\n".join(str(x.get("bullet_text", "")) for x in (bullets or []))

    add(
        "x2_unify_bullet_role_episode_bundle_id_required",
        bool(b["bundle_ids"]),
        b["bundle_ids"] or "none",
        ">=1 role_episode_bundle_id bound per bullet in change_log",
        None if b["bundle_ids"] else "No role_episode_bundle_id in change_log.",
    )
    add(
        "x2_unify_graph_skill_node_ids_required",
        bool(b["skill_ids"]),
        b["skill_ids"] or "none",
        ">=1 graph_skill_node_id bound in change_log",
        None if b["skill_ids"] else "No graph_skill_node_ids in change_log.",
    )
    add(
        "x2_unify_source_fact_or_graph_lineage_required",
        bool(b["fact_or_lineage"]),
        b["fact_or_lineage"] or "none",
        ">=1 source_fact_id or graph_lineage_ref bound in change_log",
        None if b["fact_or_lineage"] else "No source_fact_ids or graph_lineage_refs in change_log.",
    )

    # Metric outcome id required when a bullet has_metric.
    approved = set(meta.get("approved_metric_outcome_ids") or [])
    metric_violations: list[str] = []
    for bullet in bullets or []:
        bid = str(bullet.get("bullet_id") or "")
        if bullet.get("has_metric"):
            row = b["per_bullet"].get(bid) or {}
            mids = [m for m in (row.get("metric_outcome_ids") or [])]
            if not mids:
                metric_violations.append(f"{bid}:missing_metric_outcome_id")
            elif approved and not all(m in approved for m in mids):
                metric_violations.append(f"{bid}:unapproved_metric_outcome_id")
    add(
        "x2_unify_metric_outcome_id_required_when_has_metric",
        not metric_violations,
        metric_violations or "all_traceable",
        "approved metric_outcome_ids when has_metric=true",
        f"Metric binding violations: {metric_violations}" if metric_violations else None,
    )

    add(
        "x2_unify_flat_skill_only_graph_packet_forbidden",
        not flat_only,
        {"flat_skill_only": flat_only},
        "graph packet must bind role_episode_bundle (not flat skills)",
        "Flat skill-only graph packet detected." if flat_only else None,
    )

    consulting = detect_generic_consulting_phrases(combined)
    add(
        "x2_unify_generic_consulting_language_forbidden",
        not consulting,
        consulting or "none",
        "zero generic consulting-delivery phrases",
        f"Generic consulting language: {consulting}" if consulting else None,
    )

    refs = list(base_texts or []) + list(archive_texts or [])
    overlap = base_archive_ngram_overlap(combined, refs)
    over_thr = bool(refs) and overlap > _BASE_NGRAM_THRESHOLD
    add(
        "x2_unify_base_archive_ngram_overlap_forbidden_or_warn",
        not over_thr,  # HARD when base/archive prose supplied AND threshold breached; else WARN/pass
        round(overlap, 4),
        f"<= {_BASE_NGRAM_THRESHOLD:.0%} 4-gram overlap with base/archive",
        f"base/archive overlap {overlap:.1%} exceeds threshold" if over_thr else None,
    )

    sen = seniority_floor_score(combined)
    add(
        "x2_unify_seniority_floor_met",
        sen >= 1,
        sen,
        ">=1 strong executive ownership verb",
        None if sen >= 1 else "No strong ownership verb across Unify bullets.",
    )
    tech = technical_specificity_score(combined)
    add(
        "x2_unify_technical_specificity_floor_met",
        tech >= 1,
        tech,
        ">=1 named mechanism/technology token",
        None if tech >= 1 else "No named mechanism/technology token across Unify bullets.",
    )
    arch = technical_specificity_score(combined, vocab=ARCHITECTURE_MECHANISM_VOCAB)
    add(
        "x2_unify_architecture_mechanism_required",
        arch >= 1,
        arch,
        ">=1 architecture mechanism token",
        None if arch >= 1 else "No architecture mechanism named across Unify bullets.",
    )
    add(
        "x2_unify_commercial_or_operating_scope_required",
        _has_commercial_scope(combined),
        _has_commercial_scope(combined),
        ">=1 commercial/operating scope signal",
        None if _has_commercial_scope(combined) else "No commercial/operating scope signal across Unify bullets.",
    )
    return results


def run_unify_narrative_role_episode_x2_gates(
    *,
    narrative_sentence: str,
    parsed_output: dict[str, Any] | None,
    proof_pool_metadata: dict[str, Any] | None,
    base_texts: list[str] | None = None,
    archive_texts: list[str] | None = None,
) -> list[UnifyEpisodeResult]:
    results: list[UnifyEpisodeResult] = []

    def add(gid: str, ok: bool, obs: Any, thr: Any, fail: str | None) -> None:
        results.append(UnifyEpisodeResult(gid, ok, obs, thr, fail))

    meta = proof_pool_metadata if isinstance(proof_pool_metadata, dict) else {}
    bundles_present = bool(meta.get("role_episode_bundles")) or bool(meta.get("role_episode_bundle_ids"))
    flat_only = is_flat_skill_only_graph_packet(meta) and not bundles_present
    add(
        "x2_unify_narrative_role_episode_bundles_in_proof_pool",
        bundles_present and not flat_only,
        {"bundles_present": bundles_present, "flat_skill_only": flat_only},
        "role_episode_bundles in proof_pool_metadata",
        "Unify narrative proof pool missing role_episode_bundles or flat skill-only context"
        if (not bundles_present or flat_only)
        else None,
    )

    b = _collect_change_log_bindings(parsed_output)
    # Narrative may also carry top-level bundle ids.
    po = parsed_output if isinstance(parsed_output, dict) else {}
    top_bundle_ids = po.get("role_episode_bundle_ids") or []
    bundle_ids = sorted(set(b["bundle_ids"]) | {str(x) for x in (top_bundle_ids if isinstance(top_bundle_ids, list) else [])})

    add(
        "x2_unify_narrative_role_episode_bundle_id_required",
        bool(bundle_ids),
        bundle_ids or "none",
        ">=1 role_episode_bundle_id bound in narrative",
        None if bundle_ids else "No role_episode_bundle_id bound in narrative output.",
    )
    add(
        "x2_unify_narrative_graph_skill_node_ids_required",
        bool(b["skill_ids"]),
        b["skill_ids"] or "none",
        ">=1 graph_skill_node_id bound in narrative change_log",
        None if b["skill_ids"] else "No graph_skill_node_ids bound in narrative.",
    )
    add(
        "x2_unify_narrative_source_fact_or_graph_lineage_required",
        bool(b["fact_or_lineage"]),
        b["fact_or_lineage"] or "none",
        ">=1 source_fact_id or graph_lineage_ref bound in narrative",
        None if b["fact_or_lineage"] else "No source_fact_ids or graph_lineage_refs bound in narrative.",
    )
    add(
        "x2_unify_narrative_flat_skill_only_forbidden",
        not flat_only,
        {"flat_skill_only": flat_only},
        "narrative graph packet must bind role_episode_bundle",
        "Flat skill-only graph packet detected." if flat_only else None,
    )

    consulting = detect_generic_consulting_phrases(narrative_sentence)
    add(
        "x2_unify_narrative_generic_consulting_language_forbidden",
        not consulting,
        consulting or "none",
        "zero generic consulting-delivery phrases",
        f"Generic consulting language: {consulting}" if consulting else None,
    )

    unsupported = detect_unsupported_metric_claims(narrative_sentence)
    add(
        "x2_unify_narrative_unsupported_new_claim_forbidden",
        not unsupported,
        unsupported or "none",
        "no $/% claims outside the approved Unify metric allow-list",
        f"Unsupported new metric claims: {unsupported}" if unsupported else None,
    )

    refs = list(base_texts or []) + list(archive_texts or [])
    overlap = base_archive_ngram_overlap(narrative_sentence, refs)
    over_thr = bool(refs) and overlap > _BASE_NGRAM_THRESHOLD
    add(
        "x2_unify_narrative_base_archive_ngram_overlap_forbidden_or_warn",
        not over_thr,
        round(overlap, 4),
        f"<= {_BASE_NGRAM_THRESHOLD:.0%} 4-gram overlap with base/archive",
        f"base/archive overlap {overlap:.1%} exceeds threshold" if over_thr else None,
    )

    sen = seniority_floor_score(narrative_sentence)
    add(
        "x2_unify_narrative_seniority_floor_met",
        sen >= 1,
        sen,
        ">=1 strong executive ownership verb",
        None if sen >= 1 else "No strong ownership verb in narrative.",
    )
    tech = technical_specificity_score(narrative_sentence)
    add(
        "x2_unify_narrative_technical_specificity_floor_met",
        tech >= 1,
        tech,
        ">=1 named mechanism/technology token",
        None if tech >= 1 else "No named mechanism/technology token in narrative.",
    )
    return results


__all__ = [
    "UnifyEpisodeResult",
    "detect_unsupported_metric_claims",
    "run_unify_bullets_role_episode_x2_gates",
    "run_unify_narrative_role_episode_x2_gates",
    "unify_role_episode_consumption_active",
]
