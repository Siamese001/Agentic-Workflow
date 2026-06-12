"""Competency capability bundle evidence — C0 consumption for the competencies section.

Proof authority is graph-backed competency capability bundles plus linked source facts,
not generic taxonomy labels, flat skill lists, or default_fid backfill. Base resume and
archive material are calibration/provenance only — never prose hydration.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph

logger = logging.getLogger(__name__)
from apps_rg.runtime.sections.competency_capability_registry import (
    REQUIRED_CAPABILITY_FAMILIES,
    get_bundles_for_section,
    validate_competency_bundle,
)

COMPETENCY_CAPABILITY_EVIDENCE_PACK_MARKER = "COMPETENCY_CAPABILITY_EVIDENCE_PACK"

_AUTHORITY_HEADER_LINES: tuple[str, ...] = (
    "proof_authority = graph_competency_bundles_plus_linked_source_facts",
    "base_resume_usage = calibration_only",
    "archive_usage = provenance_inventory_only",
    "jd_usage = targeting_only",
    "examples_usage = style_only",
    "generic_taxonomy_label = display_wrapper_only_not_proof",
    "flat_skill_list_or_default_fid_support = forbidden",
    (
        "Generate the competencies section organically from competency capability bundles. "
        "Do not copy or paraphrase base resume or archive competency text. "
        "Preserve or exceed the base resume's rigor, specificity, and senior executive engineering signal."
    ),
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _skill_rows_by_id(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    graph = load_augmented_skills_graph(repo_root=repo_root or _repo_root())
    out: dict[str, dict[str, Any]] = {}
    for row in graph.get("skill_rows") or []:
        if isinstance(row, dict):
            sid = str(row.get("skill_id") or "").strip()
            if sid:
                out[sid] = row
    return out


def build_competency_capability_section_packet(
    section_id: str = "competencies",
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Build machine-readable competency capability packet (proof_pool metadata / C0)."""
    bundles = get_bundles_for_section(section_id)
    skill_index = _skill_rows_by_id(repo_root)
    records: list[dict[str, Any]] = []
    families_present: set[str] = set()
    graph_skill_node_ids_by_category: dict[str, list[str]] = {}
    source_fact_ids_by_category: dict[str, list[str]] = {}

    for bundle in bundles:
        ok, violations = validate_competency_bundle(bundle)
        if not ok:
            raise ValueError(
                f"Invalid competency bundle {bundle.get('competency_bundle_id')}: {violations}"
            )
        families_present.add(str(bundle.get("capability_family") or ""))
        skill_nodes: list[dict[str, Any]] = []
        for sid in bundle.get("graph_skill_node_ids") or []:
            row = skill_index.get(str(sid))
            if row:
                skill_nodes.append(
                    {
                        "skill_id": sid,
                        "allowed_phrases": list(row.get("allowed_phrases") or [])[:6],
                        "activation_status": row.get("activation_status"),
                        "confidence_grade": row.get("confidence_grade"),
                    }
                )
            else:
                skill_nodes.append({"skill_id": sid, "allowed_phrases": []})
        for cat_id in bundle.get("target_taxonomy_category_ids") or []:
            graph_skill_node_ids_by_category.setdefault(str(cat_id), [])
            for sid in bundle.get("graph_skill_node_ids") or []:
                if sid not in graph_skill_node_ids_by_category[str(cat_id)]:
                    graph_skill_node_ids_by_category[str(cat_id)].append(str(sid))
            source_fact_ids_by_category.setdefault(str(cat_id), [])
            for fid in bundle.get("linked_source_fact_ids") or []:
                if fid not in source_fact_ids_by_category[str(cat_id)]:
                    source_fact_ids_by_category[str(cat_id)].append(str(fid))
        records.append(
            {
                "competency_bundle_id": bundle["competency_bundle_id"],
                "capability_family": bundle["capability_family"],
                "display_label_candidate": bundle["display_label_candidate"],
                "target_taxonomy_category_ids": list(bundle.get("target_taxonomy_category_ids") or []),
                "graph_skill_node_ids": list(bundle.get("graph_skill_node_ids") or []),
                "linked_source_fact_ids": list(bundle.get("linked_source_fact_ids") or []),
                "employer_bindings": list(bundle.get("employer_bindings") or []),
                "role_episode_bindings": list(bundle.get("role_episode_bindings") or []),
                "evidence_strength": bundle.get("evidence_strength"),
                "external_claim_policy": bundle.get("external_claim_policy"),
                "activation_status": bundle.get("activation_status"),
                "base_rigor_family_match": bundle.get("base_rigor_family_match"),
                "seniority_signal": bundle.get("seniority_signal"),
                "technical_density_signal": bundle.get("technical_density_signal"),
                "commercial_or_operating_scope_signal": bundle.get("commercial_or_operating_scope_signal"),
                "target_relevance_rationale": bundle.get("target_relevance_rationale"),
                "vocabulary_anchors": list(bundle.get("vocabulary_anchors") or []),
                "bound_skills": skill_nodes,
            }
        )

    return {
        "section_id": section_id,
        "proof_authority": "graph_competency_bundles_plus_linked_source_facts",
        "base_resume_usage": "calibration_only",
        "archive_usage": "provenance_inventory_only",
        "jd_usage": "targeting_only",
        "examples_usage": "style_only",
        "competency_bundles": records,
        "competency_bundle_ids": [r["competency_bundle_id"] for r in records],
        "capability_families_present": sorted(f for f in families_present if f),
        "required_capability_families": list(REQUIRED_CAPABILITY_FAMILIES),
        "graph_skill_node_ids_by_category": graph_skill_node_ids_by_category,
        "source_fact_ids_by_category": source_fact_ids_by_category,
        "consumption_mode": "competency_bundle_required",
        "flat_taxonomy_only_forbidden": True,
        "default_fid_only_support_forbidden": True,
    }


def _selected_graph_plan(source: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(source, dict):
        return {}
    plan = source.get("selected_graph_evidence_plan")
    if isinstance(plan, dict):
        return plan
    pp_meta = source.get("proof_pool_metadata")
    if isinstance(pp_meta, dict) and isinstance(pp_meta.get("selected_graph_evidence_plan"), dict):
        return pp_meta["selected_graph_evidence_plan"]
    return {}


def _filter_packet_by_selected_graph_plan(
    packet: dict[str, Any],
    selected_graph_plan: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(selected_graph_plan, dict) or not selected_graph_plan:
        return packet
    selected_families = {
        str(x).strip()
        for x in (selected_graph_plan.get("selected_competency_families") or [])
        if str(x).strip()
    }
    selected_skills = {
        str(x).strip()
        for x in (selected_graph_plan.get("selected_skill_ids") or [])
        if str(x).strip()
    }
    if not selected_families and not selected_skills:
        return packet

    filtered: list[dict[str, Any]] = []
    for rec in packet.get("competency_bundles") or []:
        if not isinstance(rec, dict):
            continue
        family = str(rec.get("capability_family") or "").strip()
        skills = {str(x).strip() for x in (rec.get("graph_skill_node_ids") or []) if str(x).strip()}
        if selected_families:
            include = family in selected_families
        else:
            include = bool(selected_skills and skills.intersection(selected_skills))
        if include:
            filtered.append(rec)
    if not filtered:
        return packet

    graph_skill_node_ids_by_category: dict[str, list[str]] = {}
    source_fact_ids_by_category: dict[str, list[str]] = {}
    families_present: set[str] = set()
    for rec in filtered:
        family = str(rec.get("capability_family") or "").strip()
        if family:
            families_present.add(family)
        for cat_id in rec.get("target_taxonomy_category_ids") or []:
            cat = str(cat_id)
            graph_skill_node_ids_by_category.setdefault(cat, [])
            for sid in rec.get("graph_skill_node_ids") or []:
                sid_s = str(sid)
                if sid_s not in graph_skill_node_ids_by_category[cat]:
                    graph_skill_node_ids_by_category[cat].append(sid_s)
            source_fact_ids_by_category.setdefault(cat, [])
            for fid in rec.get("linked_source_fact_ids") or []:
                fid_s = str(fid)
                if fid_s not in source_fact_ids_by_category[cat]:
                    source_fact_ids_by_category[cat].append(fid_s)

    out = dict(packet)
    out["competency_bundles"] = filtered
    out["competency_bundle_ids"] = [str(r.get("competency_bundle_id") or "") for r in filtered]
    out["capability_families_present"] = sorted(families_present)
    out["graph_skill_node_ids_by_category"] = graph_skill_node_ids_by_category
    out["source_fact_ids_by_category"] = source_fact_ids_by_category
    out["selected_graph_evidence_plan_applied"] = True
    out["selected_competency_families"] = sorted(selected_families)
    return out


def attach_competency_bundles_to_proof_pool_metadata(
    meta: dict[str, Any],
    *,
    section_id: str = "competencies",
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Merge competency capability packet into proof_pool_metadata (competencies only)."""
    if section_id != "competencies":
        return meta
    packet = build_competency_capability_section_packet(section_id, repo_root=repo_root)
    packet = _filter_packet_by_selected_graph_plan(packet, _selected_graph_plan(meta))
    out = dict(meta)
    out["competency_capability_bundle_consumption"] = True
    out["competency_capability_bundle_consumption_mode"] = "competency_bundle_required"
    out["competency_capability_bundles"] = packet["competency_bundles"]
    out["competency_bundle_ids"] = packet["competency_bundle_ids"]
    out["competency_capability_section_packet"] = packet
    out["graph_expansion_consumes_competency_bundles"] = True
    out["flat_taxonomy_only_graph_context_forbidden"] = True
    return out


def is_flat_taxonomy_only_packet(packet: dict[str, Any]) -> bool:
    """True when graph context is only generic taxonomy with no bundle/skill binding."""
    if packet.get("competency_bundle_id") or packet.get("competency_bundle_ids"):
        return False
    if packet.get("competency_bundles"):
        return False
    inner = packet.get("competency_capability_section_packet") or {}
    if isinstance(inner, dict) and inner.get("competency_bundles"):
        return False
    if packet.get("graph_skill_node_ids") and not packet.get("competency_bundle_id"):
        return True
    return True


def format_competency_capability_evidence_pack(
    runtime_payload: dict[str, Any],
    *,
    section_id: str = "competencies",
) -> str:
    """C0 body: competency capability bundles as proof authority (graph-backed, per family)."""
    packet = build_competency_capability_section_packet(section_id)
    packet = _filter_packet_by_selected_graph_plan(packet, _selected_graph_plan(runtime_payload))
    runtime_payload["competency_capability_section_packet"] = packet
    runtime_payload["competency_bundle_ids"] = packet["competency_bundle_ids"]

    header_lines = [
        f"{COMPETENCY_CAPABILITY_EVIDENCE_PACK_MARKER} "
        "(proof substrate — compose categories from competency_bundle_id + bound_skills + linked source facts):",
        *_AUTHORITY_HEADER_LINES,
        "- Each emitted category MUST cite a competency_bundle_id and its graph_skill_node_ids.",
        "- Each major term MUST bind to graph_skill_node_ids and linked source_fact_ids or approved graph lineage.",
        "- Generic taxonomy labels may be display wrappers only — never proof on their own.",
        "- A term attached only to default_fid is NOT proof.",
        "- Required capability families to cover (>=7): "
        + ", ".join(REQUIRED_CAPABILITY_FAMILIES[:7]) + ".",
    ]
    header = "\n".join(header_lines)

    blocks: list[str] = []
    for rec in packet["competency_bundles"]:
        lines = [
            f"COMPETENCY_BUNDLE {rec['competency_bundle_id']} | family: {rec['capability_family']}",
            f"  display_label_candidate: {rec['display_label_candidate']}",
            f"  target_taxonomy_category_ids: {rec['target_taxonomy_category_ids']}",
            f"  graph_skill_node_ids: {rec['graph_skill_node_ids']}",
            f"  linked_source_fact_ids: {rec['linked_source_fact_ids']}",
            f"  evidence_strength: {rec['evidence_strength']} | activation: {rec['activation_status']}",
            f"  base_rigor_family_match: {rec['base_rigor_family_match']}",
            f"  seniority_signal: {rec['seniority_signal']} | technical_density_signal: {rec['technical_density_signal']}",
            f"  target_relevance_rationale: {rec['target_relevance_rationale']}",
            "  bound_skills (graph authority — vocabulary anchors only, not proof on their own):",
        ]
        for sk in rec.get("bound_skills") or []:
            if not isinstance(sk, dict):
                continue
            sid = sk.get("skill_id")
            phrases = ", ".join(list(sk.get("allowed_phrases") or [])[:5])
            if phrases:
                lines.append(f"    - {sid} | allowed_phrases: {phrases}")
            else:
                lines.append(f"    - {sid}")
        lines.append("  vocabulary_anchors (structured anchors only — no base/archive prose):")
        for anchor in rec.get("vocabulary_anchors") or []:
            lines.append(f"    - {anchor}")
        if rec.get("employer_bindings") or rec.get("role_episode_bindings"):
            lines.append(
                f"  bindings: employer={rec.get('employer_bindings')} role_episode={rec.get('role_episode_bindings')}"
            )
        blocks.append("\n".join(lines))

    return header + "\n\n" + "\n\n".join(blocks)


def stamp_competency_bundle_bindings(
    competencies: list[dict[str, Any]],
    *,
    packet: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Stamp competency_bundle_id + graph_skill_node_ids onto categories by taxonomy mapping.

    Runtime seam: makes the final output bind each category to a graph-backed bundle. Does
    not invent terms; only attaches graph lineage metadata for categories whose category_id
    is a target of a competency bundle.
    """
    if not isinstance(competencies, list):
        return competencies
    pkt = packet or build_competency_capability_section_packet("competencies")
    by_category: dict[str, dict[str, Any]] = {}
    by_family: dict[str, dict[str, Any]] = {}
    for rec in pkt.get("competency_bundles") or []:
        for cat_id in rec.get("target_taxonomy_category_ids") or []:
            by_category.setdefault(str(cat_id), rec)
        # Family fallback: a category whose id/label names a capability family (e.g.
        # "llmops_reliability") but is not a bundle taxonomy *target* still binds to that
        # family's bundle (ccb_llmops_reliability) — it is graph-backed, just not a top taxonomy slot.
        fam = str(rec.get("capability_family") or "").strip()
        if fam:
            by_family.setdefault(fam, rec)
        bid = str(rec.get("competency_bundle_id") or "").strip()
        if bid.startswith("ccb_"):
            by_family.setdefault(bid[len("ccb_"):], rec)
    for cat in competencies:
        if not isinstance(cat, dict):
            continue
        cid = str(cat.get("category_id") or "").strip()
        rec = by_category.get(cid) or by_family.get(cid)
        if not rec:
            label_key = re.sub(r"[^a-z0-9]+", "_", str(cat.get("category_label") or "").lower()).strip("_")
            rec = by_family.get(label_key)
        if not rec:
            # Coverage violation: an emitted competency category whose taxonomy
            # category_id is not a target of ANY competency bundle. Previously a silent
            # skip — now surfaced so an orphaned taxonomy category (E2E-07) is observable
            # instead of quietly dropping its graph lineage. Stamp the category too so the
            # gap is visible in the artifact, not just the logs.
            if cid:
                logger.warning(
                    "COMPETENCY_BUNDLE_BINDING_MISSING: category_id=%r has no competency "
                    "bundle target (orphaned taxonomy category) — graph lineage not stamped",
                    cid,
                )
                cat["competency_bundle_binding_missing"] = True
            continue
        cat["competency_bundle_id"] = rec["competency_bundle_id"]
        cat["capability_family"] = rec["capability_family"]
        existing_nodes = list(cat.get("graph_skill_node_ids") or [])
        for sid in rec.get("graph_skill_node_ids") or []:
            if sid not in existing_nodes:
                existing_nodes.append(sid)
        cat["graph_skill_node_ids"] = existing_nodes
    return competencies


# Map bundle capability_family -> the family key used by the X2 coverage gate
# (apps_rg.runtime.validators.competencies_quality_x2.REQUIRED_CAPABILITY_FAMILIES).
_BUNDLE_TO_GATE_FAMILY: dict[str, str] = {
    "agentic_platforms": "agentic_platform",
    "runtime_governance": "runtime_governance",
    "retrieval_context_engineering": "retrieval_context",
    "llmops_reliability": "llmops",
    "distributed_systems_engineering": "distributed_infra",
    "platform_productization": "productization",
    "engineering_leadership": "engineering_leadership",
}


def _family_tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", str(text or "").lower()))


def _make_anchor_term(rec: dict[str, Any], anchor: str, fid: str) -> dict[str, Any]:
    display = str(anchor)
    if display.islower():
        display = display.title()
    skill_ids = [str(s) for s in (rec.get("graph_skill_node_ids") or []) if str(s).strip()]
    return {
        "text": display,
        "term": display,
        "source_fact_id": fid,
        "source_fact_ids": [fid],
        "source_skill_ids": skill_ids,
        "support_class": "FACT_ONLY",
    }


def _nonempty_term_count(cat: dict[str, Any]) -> int:
    n = 0
    for t in cat.get("terms") or []:
        if isinstance(t, dict) and str(t.get("text") or t.get("term") or "").strip():
            n += 1
        elif isinstance(t, str) and t.strip():
            n += 1
    return n


def _existing_term_norms(cat: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for t in cat.get("terms") or []:
        txt = t.get("text") or t.get("term") if isinstance(t, dict) else str(t)
        if txt:
            out.add(str(txt).strip().lower())
    return out


def augment_bound_category_family_terms(
    categories: list[dict[str, Any]],
    *,
    packet: dict[str, Any] | None,
    allowed_fact_ids: set[str] | None,
) -> list[dict[str, Any]]:
    """Inject bundle-approved, fact-grounded anchor terms into bound categories (Author-Gate
    dec_19e9daa115a62cf3a, anchor_injection).

    The live model reliably frames the LLMOps-bound category as leadership (omitting
    observability/evaluation vocabulary) and under-generates some categories below the 3-term
    executive floor. This deterministic augmentation runs after bundle stamping and does two
    fact-grounded things using each category's *bound bundle* only:

    1. Capability-family coverage: when a required family is not lexically covered across the
       emitted competencies, append one of the bound bundle's ``vocabulary_anchors`` whose tokens
       hit that family.
    2. Per-category term floor: top each bound category up to ``MIN_ITEMS_PER_CATEGORY`` graph-backed
       terms using its bundle's remaining anchors.

    Injected terms carry the bundle's genuine ``linked_source_fact_ids`` (restricted to the allowed
    pool) plus its ``graph_skill_node_ids`` as ``source_skill_ids`` — so they are graph-backed and
    not ``default_fid_backfill``. No anchor is injected when the bundle has no allowed linked fact
    (no fabricated provenance).
    """
    if not isinstance(categories, list):
        return categories
    pkt = packet or build_competency_capability_section_packet("competencies")
    by_id: dict[str, dict[str, Any]] = {
        str(r.get("competency_bundle_id")): r
        for r in (pkt.get("competency_bundles") or [])
        if isinstance(r, dict) and r.get("competency_bundle_id")
    }
    if not by_id:
        return categories

    try:
        from apps_rg.runtime.validators.competencies_quality_x2 import (
            REQUIRED_CAPABILITY_FAMILIES as _GATE_FAMILY_TOKENS,
        )
    except (ImportError, AttributeError):  # guardian: allow-default-fallback -- optional coverage augmentation
        return categories
    try:
        from apps_rg.runtime.sections.competencies_rigor import MAX_ITEMS_PER_CATEGORY, MIN_ITEMS_PER_CATEGORY
    except (ImportError, AttributeError):  # guardian: allow-default-fallback -- optional coverage augmentation
        MIN_ITEMS_PER_CATEGORY, MAX_ITEMS_PER_CATEGORY = 2, 6

    allowed = {str(x) for x in (allowed_fact_ids or set())}

    def _allowed_fid(rec: dict[str, Any]) -> str | None:
        for f in rec.get("linked_source_fact_ids") or []:
            if str(f) in allowed:
                return str(f)
        return None

    def _append(cat: dict[str, Any], rec: dict[str, Any], anchor: str, fid: str) -> None:
        cat.setdefault("terms", []).append(_make_anchor_term(rec, anchor, fid))
        existing = list(cat.get("source_fact_ids") or [])
        if fid not in existing:
            existing.append(fid)
        cat["source_fact_ids"] = existing

    covered_tokens: set[str] = set()
    for cat in categories:
        if not isinstance(cat, dict):
            continue
        for term in cat.get("terms") or []:
            if isinstance(term, dict):
                covered_tokens |= _family_tokenize(term.get("text") or term.get("term") or "")
            else:
                covered_tokens |= _family_tokenize(str(term))
        covered_tokens |= _family_tokenize(cat.get("category_label") or "")

    # Pass 0: required-family coverage even when NO category is bound to the missing family's
    # bundle. The live model does not deterministically bind a category to every required
    # capability family (e.g. distributed_infra may be omitted entirely). For each required
    # gate family not lexically covered, locate its bundle (by _BUNDLE_TO_GATE_FAMILY), then
    # inject one of its fact-grounded vocabulary_anchors into the bound category for that
    # bundle if present, else into the category with the most headroom — stamping the bundle
    # binding so the injected term is graph-backed. No injection without an allowed linked fact.
    rec_by_gate_family: dict[str, dict[str, Any]] = {}
    for _rec in by_id.values():
        gf = _BUNDLE_TO_GATE_FAMILY.get(str(_rec.get("capability_family") or ""))
        if gf and gf not in rec_by_gate_family and _allowed_fid(_rec):
            rec_by_gate_family[gf] = _rec
    bound_gate_families: set[str] = set()
    for cat in categories:
        if isinstance(cat, dict):
            _r = by_id.get(str(cat.get("competency_bundle_id") or ""))
            if _r:
                _gf = _BUNDLE_TO_GATE_FAMILY.get(str(_r.get("capability_family") or ""))
                if _gf:
                    bound_gate_families.add(_gf)
    for gate_family, family_tokens in _GATE_FAMILY_TOKENS.items():
        if covered_tokens & set(family_tokens):
            continue
        if gate_family in bound_gate_families:
            continue  # Pass 1 will handle bound categories
        rec = rec_by_gate_family.get(gate_family)
        if not rec:
            continue
        fid = _allowed_fid(rec)
        if not fid:
            continue
        anchor = next(
            (
                a
                for a in (rec.get("vocabulary_anchors") or [])
                if _family_tokenize(a) & set(family_tokens)
            ),
            None,
        )
        if not anchor:
            continue
        target = None
        for cat in categories:
            if not isinstance(cat, dict):
                continue
            if _nonempty_term_count(cat) < MAX_ITEMS_PER_CATEGORY and str(anchor).strip().lower() not in _existing_term_norms(cat):
                if target is None or _nonempty_term_count(cat) < _nonempty_term_count(target):
                    target = cat
        if target is None:
            continue
        _append(target, rec, anchor, fid)
        covered_tokens |= _family_tokenize(anchor)

    # Pass 1: capability-family coverage.
    for cat in categories:
        if not isinstance(cat, dict):
            continue
        rec = by_id.get(str(cat.get("competency_bundle_id") or ""))
        if not rec:
            continue
        gate_family = _BUNDLE_TO_GATE_FAMILY.get(str(rec.get("capability_family") or ""))
        family_tokens = _GATE_FAMILY_TOKENS.get(gate_family) if gate_family else None
        if not family_tokens or (covered_tokens & set(family_tokens)):
            continue
        fid = _allowed_fid(rec)
        if not fid:
            continue
        seen = _existing_term_norms(cat)
        anchor = next(
            (
                a
                for a in (rec.get("vocabulary_anchors") or [])
                if (_family_tokenize(a) & set(family_tokens)) and str(a).strip().lower() not in seen
            ),
            None,
        )
        if not anchor or _nonempty_term_count(cat) >= MAX_ITEMS_PER_CATEGORY:
            continue
        _append(cat, rec, anchor, fid)
        covered_tokens |= _family_tokenize(anchor)

    # Pass 2: per-category term floor (graph-backed bundle anchors only).
    for cat in categories:
        if not isinstance(cat, dict):
            continue
        rec = by_id.get(str(cat.get("competency_bundle_id") or ""))
        if not rec:
            continue
        fid = _allowed_fid(rec)
        if not fid:
            continue
        for anchor in rec.get("vocabulary_anchors") or []:
            if _nonempty_term_count(cat) >= MIN_ITEMS_PER_CATEGORY:
                break
            if str(anchor).strip().lower() in _existing_term_norms(cat):
                continue
            _append(cat, rec, anchor, fid)

    return categories


__all__ = [
    "COMPETENCY_CAPABILITY_EVIDENCE_PACK_MARKER",
    "attach_competency_bundles_to_proof_pool_metadata",
    "augment_bound_category_family_terms",
    "build_competency_capability_section_packet",
    "format_competency_capability_evidence_pack",
    "is_flat_taxonomy_only_packet",
    "stamp_competency_bundle_bindings",
]
