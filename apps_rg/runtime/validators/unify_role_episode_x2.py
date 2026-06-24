"""Unify role episode bundle X2 gate helpers (role_episode_bundle consumption mode).

Active only when proof_pool_metadata indicates role_episode_bundle_consumption for a unify
lane. Enforces that unify_bullets / unify_narrative are composed from graph-backed role
episode bundles (bundle id + graph skill node ids + source fact/lineage), preserve seniority
and technical specificity, carry an architecture mechanism and commercial/operating scope,
and do not demote into generic consulting language, flat skill-only packets, JD-only lifts,
unsupported new metric claims, or base/archive hydration.
"""
from __future__ import annotations

from functools import lru_cache
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
from apps_rg.runtime.sections.role_episode_metric_registry import metric_outcome_nodes_from_path
from apps_rg.runtime.sections.unify_graph_role_episode_registry import (
    BUNDLES_PATH as UNIFY_BUNDLES_PATH,
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
_SURFACE_NORM_RE = re.compile(r"[^a-z0-9%$]+")


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


def _bundle_index_by_fact(meta: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Role episode bundle records (id + linked facts/skills/metrics) from proof_pool_metadata."""
    m = meta if isinstance(meta, dict) else {}
    bundles = m.get("role_episode_bundles")
    out: list[dict[str, Any]] = []
    if isinstance(bundles, list):
        for rec in bundles:
            if isinstance(rec, dict) and rec.get("role_episode_bundle_id"):
                out.append(rec)
    return out


@lru_cache(maxsize=1)
def _unify_metric_outcome_nodes() -> dict[str, dict[str, Any]]:
    return metric_outcome_nodes_from_path(UNIFY_BUNDLES_PATH)


def _surface_norm(text: str) -> str:
    return _SURFACE_NORM_RE.sub(" ", str(text or "").lower()).strip()


def _metric_surface_tokens(metric_id: str) -> list[str]:
    node = _unify_metric_outcome_nodes().get(str(metric_id)) or {}
    tokens: list[str] = []
    for raw in [node.get("metric"), *(node.get("surface_tokens") or []), node.get("claim_text")]:
        token = str(raw or "").strip()
        if token and token not in tokens:
            tokens.append(token)
    return tokens


def _metric_token_visible_in_text(metric_id: str, text: str) -> str | None:
    low = str(text or "").lower()
    norm = _surface_norm(text)
    for token in _metric_surface_tokens(metric_id):
        t_low = token.lower()
        if t_low and t_low in low:
            return token
        t_norm = _surface_norm(token)
        if t_norm and t_norm in norm:
            return token
    return None


def _resolved_slot_bundle_map(
    parsed_output: dict[str, Any] | None,
    meta: dict[str, Any] | None,
) -> dict[str, str]:
    from apps_rg.runtime.sections.unify_role_episode_evidence import (
        UNIFY_BULLET_SLOT_BUNDLE_MAP,
    )

    candidates: list[Any] = []
    if isinstance(meta, dict):
        candidates.append(meta.get("unify_bullet_slot_bundle_map_resolved"))
    if isinstance(parsed_output, dict):
        candidates.append(parsed_output.get("unify_bullet_slot_bundle_map_resolved"))
    for candidate in candidates:
        if isinstance(candidate, dict) and candidate:
            return {str(k): str(v) for k, v in candidate.items() if str(k).strip() and str(v).strip()}
    return dict(UNIFY_BULLET_SLOT_BUNDLE_MAP)


def _slot_metric_allowlist(
    parsed_output: dict[str, Any] | None,
    meta: dict[str, Any] | None,
) -> dict[str, set[str]]:
    slot_map = _resolved_slot_bundle_map(parsed_output, meta)
    bundles = _bundle_index_by_fact(meta)
    by_id = {str(r.get("role_episode_bundle_id")): r for r in bundles}
    approved = {
        str(x).strip()
        for x in ((meta or {}).get("approved_metric_outcome_ids") or _unify_metric_outcome_nodes().keys())
        if str(x).strip()
    }
    out: dict[str, set[str]] = {}
    for slot_id, bundle_id in slot_map.items():
        rec = by_id.get(bundle_id) or {}
        mids = {
            str(x).strip()
            for x in (rec.get("linked_metric_outcome_ids") or rec.get("allowed_metric_outcome_ids") or [])
            if str(x).strip()
        }
        out[slot_id] = mids & approved if approved else mids
    return out


def _collect_change_log_bindings(
    parsed_output: dict[str, Any] | None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Collect role episode bindings from model output + derive from cited facts.

    derive_from_cited_facts (Author-Gate dec_19e9c91073ae4b5ab): a role episode bundle is *bound*
    to a bullet when the bullet cites one of the bundle's linked_source_fact_ids. We resolve
    role_episode_bundle_id + graph_skill_node_ids + matched source facts + approved
    metric_outcome_ids deterministically from the attached bundles, in addition to any binding the
    model echoed in change_log. The model variously emits source facts under `source_fact_ids` or
    `fact_ids_used`; both are honored.
    """
    bundle_ids: list[str] = []
    skill_ids: list[str] = []
    fact_or_lineage: list[str] = []
    metric_ids: list[str] = []
    per_bullet: dict[str, dict[str, Any]] = {}
    po = parsed_output if isinstance(parsed_output, dict) else {}

    def _bullet_cited_facts(entry: dict[str, Any]) -> list[str]:
        return [str(x) for x in (entry.get("source_fact_ids") or [])] + [
            str(x) for x in (entry.get("fact_ids_used") or [])
        ] + [str(x) for x in (entry.get("graph_lineage_refs") or [])]

    for entry in po.get("change_log") or []:
        if not isinstance(entry, dict):
            continue
        bid = str(entry.get("bullet_id") or "")
        reb = str(entry.get("role_episode_bundle_id") or "").strip()
        # A narrative synthesizes across several role episodes and binds them as a plural
        # list (change_log entry ``bundle_ids: [...]``) rather than one singular id per
        # bullet. Honor both so genuine narrative bundle bindings are not dropped.
        reb_plural = [str(x).strip() for x in (entry.get("bundle_ids") or []) if str(x).strip()]
        sk = [str(x) for x in (entry.get("graph_skill_node_ids") or entry.get("skill_ids_used") or [])]
        srcs = _bullet_cited_facts(entry)
        mids = [str(x) for x in (entry.get("metric_outcome_ids") or [])]
        if reb:
            bundle_ids.append(reb)
        bundle_ids.extend(reb_plural)
        skill_ids.extend(sk)
        fact_or_lineage.extend(srcs)
        metric_ids.extend(mids)
        if bid:
            per_bullet[bid] = {
                "role_episode_bundle_id": reb,
                "graph_skill_node_ids": list(sk),
                "source_fact_ids": list(srcs),
                "metric_outcome_ids": list(mids),
                "explicit_metric_outcome_ids": list(mids),
            }

    # Per-bullet source facts also live on the bullets list (bullet_text payload).
    for bullet in po.get("bullets") or []:
        if not isinstance(bullet, dict):
            continue
        bid = str(bullet.get("bullet_id") or "")
        if not bid:
            continue
        slot = per_bullet.setdefault(
            bid,
            {
                "role_episode_bundle_id": "",
                "graph_skill_node_ids": [],
                "source_fact_ids": [],
                "metric_outcome_ids": [],
                "explicit_metric_outcome_ids": [],
            },
        )
        slot["source_fact_ids"].extend(str(x) for x in (bullet.get("source_fact_ids") or []))

    # Aggregate facts cited in claim_ledger (narrative cites here, not in change_log).
    claim_ledger_facts: list[str] = []
    for entry in po.get("claim_ledger") or []:
        if isinstance(entry, dict):
            claim_ledger_facts.extend(str(x) for x in (entry.get("source_fact_ids") or []))
    top_ids = po.get("role_episode_bundle_ids")
    if isinstance(top_ids, list):
        bundle_ids.extend(str(x) for x in top_ids if str(x).strip())

    # Derive bindings from attached bundles via cited-fact intersection.
    bundles = _bundle_index_by_fact(meta)

    # Graph-era narrative binding (typed-edge role-facet guardrails): the narrative emits its
    # bundle selection under ``selected_fact_plan.primary_bundles`` and cites bundle ids
    # (``reb_unify_*``) + graph skill node ids (``skill_*``) directly in
    # ``claim_ledger.source_fact_ids`` — not the legacy ``bul_unify_*`` slot ids the maps below
    # resolve. Recognize those graph-era ids as first-class bindings so the graph-lineage gates
    # see the bindings the narrative already carries; the bundle-resolution block further down
    # then fills each bound bundle's graph_skill_node_ids + a lineage fact + metric outcomes.
    _known_bundle_ids = {str(r.get("role_episode_bundle_id")) for r in bundles}
    _sfp = po.get("selected_fact_plan")
    _cited_graph_ids: list[str] = list(claim_ledger_facts)
    if isinstance(_sfp, dict) and isinstance(_sfp.get("primary_bundles"), list):
        _cited_graph_ids.extend(str(x) for x in _sfp["primary_bundles"])
    for _gid in _cited_graph_ids:
        _gid = _gid.strip()
        if _gid in _known_bundle_ids:
            bundle_ids.append(_gid)
        elif _gid.startswith("skill_"):
            skill_ids.append(_gid)
            fact_or_lineage.append(_gid)

    # Narrative path: cited finalized bullet-slot ids (bul_unify_*) carry graph lineage to bundles
    # via the slot->bundle map; resolve bundle_id + skills + lineage from them.
    if claim_ledger_facts:
        slot_bundle_map = _resolved_slot_bundle_map(parsed_output, meta)
        bundle_by_id = {str(r.get("role_episode_bundle_id")): r for r in bundles}
        for fid in claim_ledger_facts:
            rid = slot_bundle_map.get(fid)
            rec = bundle_by_id.get(rid) if rid else None
            if rec:
                bundle_ids.append(str(rid))
                skill_ids.extend(str(x) for x in (rec.get("graph_skill_node_ids") or []))
                fact_or_lineage.append(fid)
            else:
                for rec2 in bundles:
                    linked = {str(f).strip() for f in (rec2.get("linked_source_fact_ids") or []) if str(f).strip()}
                    if fid in linked:
                        bundle_ids.append(str(rec2.get("role_episode_bundle_id")))
                        skill_ids.extend(str(x) for x in (rec2.get("graph_skill_node_ids") or []))
                        fact_or_lineage.append(fid)

    if bundles:
        # W5 (apps-rg-aig-remaining-lanes-closeout-d4e1f7): also derive via the canonical
        # slot->bundle map. Bullets cite their own slot ids / per-slot metric atoms
        # (``bul_unify_004``, ``bul_unify_004_metric_*``) rather than the bundle's
        # ``fact_engineering_platform_*`` linked facts, so the cited∩linked intersection alone
        # left metric_outcome_ids unbound for metric-protected slots. The narrative path already
        # resolves through this map; the per-bullet path now does too.
        slot_bundle_map = _resolved_slot_bundle_map(parsed_output, meta)
        bundle_by_id = {str(r.get("role_episode_bundle_id")): r for r in bundles}
        for bid, slot in per_bullet.items():
            cited = {f for f in slot.get("source_fact_ids") or [] if f}
            slot_recs: list[dict[str, Any]] = []
            # Map-bind ONLY when the bullet actually cites its own slot's proof-pool atoms
            # (``bul_unify_004`` / ``bul_unify_004_metric_*``); a bullet citing no slot atom
            # derives nothing here, so adversarial unbound-metric packets still fail the gate.
            cites_own_slot = any(c == bid or c.startswith(f"{bid}_") for c in cited)
            mapped_rid = slot_bundle_map.get(bid) if cites_own_slot else None
            if mapped_rid and mapped_rid in bundle_by_id:
                slot_recs.append(bundle_by_id[mapped_rid])
            for rec in bundles:
                linked = {str(f).strip() for f in (rec.get("linked_source_fact_ids") or []) if str(f).strip()}
                matched = cited & linked
                if not matched and rec not in slot_recs:
                    continue
                if rec not in slot_recs:
                    slot_recs.append(rec)
                fact_or_lineage.extend(sorted(matched))
            for rec in slot_recs:
                rid = str(rec.get("role_episode_bundle_id"))
                if not slot.get("role_episode_bundle_id"):
                    slot["role_episode_bundle_id"] = rid
                bundle_ids.append(rid)
                rsk = [str(x) for x in (rec.get("graph_skill_node_ids") or [])]
                slot["graph_skill_node_ids"].extend(rsk)
                skill_ids.extend(rsk)
                rmids = [str(x) for x in (rec.get("linked_metric_outcome_ids") or [])]
                slot["metric_outcome_ids"].extend(rmids)
                metric_ids.extend(rmids)

    # Narrative change_log binds whole bundles (plural ``bundle_ids``) without per-bullet
    # slot facts; resolve each bound bundle's graph_skill_node_ids + a lineage fact + metric
    # outcomes from the bundle index so the narrative graph-lineage gates see the genuine
    # bindings the model already emitted (a truly empty change_log still binds nothing).
    if bundles:
        _bundle_by_id = {str(r.get("role_episode_bundle_id")): r for r in bundles}
        for rid in list(bundle_ids):
            rec = _bundle_by_id.get(rid)
            if not rec:
                continue
            skill_ids.extend(str(x) for x in (rec.get("graph_skill_node_ids") or []))
            _lf = [str(f) for f in (rec.get("linked_source_fact_ids") or []) if str(f).strip()]
            if _lf:
                fact_or_lineage.append(_lf[0])
            metric_ids.extend(str(x) for x in (rec.get("linked_metric_outcome_ids") or []))

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

    b = _collect_change_log_bindings(parsed_output, meta)
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

    slot_metric_allowlist = _slot_metric_allowlist(parsed_output, meta)
    bullet_text_by_id = {
        str(bullet.get("bullet_id") or ""): str(bullet.get("bullet_text") or "")
        for bullet in (bullets or [])
        if isinstance(bullet, dict)
    }
    lineage_missing: list[str] = []
    lineage_unapproved: list[str] = []
    visible_missing: list[str] = []
    visible_matches: dict[str, list[dict[str, str]]] = {}
    unique_visible_metric_ids: set[str] = set()
    for bid, text in bullet_text_by_id.items():
        if not bid.startswith("bul_unify_"):
            continue
        row = b["per_bullet"].get(bid) or {}
        explicit_mids = [
            str(x).strip()
            for x in (row.get("explicit_metric_outcome_ids") or [])
            if str(x).strip()
        ]
        allowed_for_slot = slot_metric_allowlist.get(bid) or set()
        if not explicit_mids:
            lineage_missing.append(bid)
            visible_missing.append(bid)
            continue
        bad = [mid for mid in explicit_mids if allowed_for_slot and mid not in allowed_for_slot]
        if bad:
            lineage_unapproved.append(f"{bid}:{bad}")
        for mid in explicit_mids:
            token = _metric_token_visible_in_text(mid, text)
            if token:
                visible_matches.setdefault(bid, []).append({"metric_outcome_id": mid, "token": token})
                unique_visible_metric_ids.add(mid)
        if not visible_matches.get(bid):
            visible_missing.append(bid)
    add(
        "x2_unify_each_bullet_approved_metric_outcome_lineage",
        not lineage_missing and not lineage_unapproved and bool(bullet_text_by_id),
        {
            "missing_metric_outcome_ids": lineage_missing,
            "unapproved_metric_outcome_ids": lineage_unapproved,
            "slot_metric_allowlist": {k: sorted(v) for k, v in slot_metric_allowlist.items()},
        },
        "every bul_unify_* change_log row records >=1 approved slot metric_outcome_id",
        (
            f"Metric outcome lineage failures: missing={lineage_missing}, unapproved={lineage_unapproved}"
            if (lineage_missing or lineage_unapproved)
            else None
        ),
    )
    add(
        "x2_unify_each_bullet_metric_outcome_surface_visible",
        not visible_missing and bool(visible_matches),
        {
            "visible_matches": visible_matches,
            "missing_visible_metric_surface": visible_missing,
        },
        "every bul_unify_* bullet_text surfaces a metric/surface_token from its approved metric_outcome_id",
        (
            f"Bullet text missing visible approved metric outcome surface: {visible_missing}"
            if visible_missing
            else None
        ),
    )
    expected_metric_slots = len([bid for bid in bullet_text_by_id if bid.startswith("bul_unify_")])
    distribution_ok = expected_metric_slots > 0 and len(unique_visible_metric_ids) >= expected_metric_slots
    add(
        "x2_unify_metric_outcomes_distributed_by_slot",
        distribution_ok,
        {
            "unique_visible_metric_outcome_ids": sorted(unique_visible_metric_ids),
            "expected_metric_slots": expected_metric_slots,
        },
        ">=1 distinct visible metric_outcome_id per bul_unify_* slot",
        None
        if distribution_ok
        else "Metric outcome evidence is not distributed across all Unify bullet slots.",
    )

    receipt = meta.get("unify_graph_traversal_sufficiency_receipt") if isinstance(meta, dict) else {}
    receipt = receipt if isinstance(receipt, dict) else {}
    conservation = receipt.get("candidate_conservation") if isinstance(receipt.get("candidate_conservation"), dict) else {}
    traversal_ok = (
        bool(conservation.get("pass"))
        and int(receipt.get("selected_role_episode_root_count") or 0) >= 6
        and int(receipt.get("selected_unique_leaf_skill_count") or 0) >= 20
        and int(receipt.get("selected_unique_metric_count") or 0) >= 10
        and int(receipt.get("rejected_sibling_skill_count") or 0) > 0
        and int(receipt.get("rejected_sibling_metric_count") or 0) > 0
    )
    add(
        "x2_unify_graph_traversal_sufficiency",
        traversal_ok,
        {
            "candidate_conservation": conservation,
            "selected_role_episode_root_count": receipt.get("selected_role_episode_root_count"),
            "selected_unique_leaf_skill_count": receipt.get("selected_unique_leaf_skill_count"),
            "selected_unique_metric_count": receipt.get("selected_unique_metric_count"),
            "rejected_sibling_skill_count": receipt.get("rejected_sibling_skill_count"),
            "rejected_sibling_metric_count": receipt.get("rejected_sibling_metric_count"),
        },
        "candidate conservation + >=6 roots + >=20 skills + >=10 metrics + rejected sibling frontier",
        None if traversal_ok else "Unify graph traversal receipt is too shallow or missing candidate conservation.",
    )
    axis = receipt.get("role_specific_axis_coverage") if isinstance(receipt.get("role_specific_axis_coverage"), dict) else {}
    frontier = receipt.get("frontier_size_by_hop_depth") if isinstance(receipt.get("frontier_size_by_hop_depth"), dict) else {}
    root_count = int(receipt.get("selected_role_episode_root_count") or 0)
    granularity_ok = (
        not (axis.get("missing_axes") or [])
        and int(frontier.get("hop_1_graph_skill_nodes") or 0) >= root_count * 2
        and int(frontier.get("hop_2_metric_outcome_nodes") or 0) >= root_count
    )
    add(
        "x2_unify_graph_granularity_gates",
        granularity_ok,
        {"role_specific_axis_coverage": axis, "frontier_size_by_hop_depth": frontier},
        "no missing role axes; skill frontier >=2x roots; metric frontier >= roots",
        None if granularity_ok else "Unify graph evidence lacks role-axis coverage or leaf/metric granularity.",
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

    b = _collect_change_log_bindings(parsed_output, meta)
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
