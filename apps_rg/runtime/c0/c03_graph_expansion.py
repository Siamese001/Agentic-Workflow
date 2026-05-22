"""C0.3 — graph relationship expansion over C0.2 atoms only."""

from __future__ import annotations

from typing import Any

from apps_rg.runtime.c03_graph_sqlite_context import assemble_c03_graph_sqlite_context
from apps_rg.runtime.c0.c03_role_family import resolve_c0_pillar_hints
from apps_rg.runtime.c0.constants import (
    GRAPH_STRENGTH_ADJACENT_ONLY,
    GRAPH_STRENGTH_DIRECT,
    GRAPH_STRENGTH_NONE,
    REL_ADJACENCY_ONLY,
    REL_DIRECT_SUPPORT,
    REL_SECTION_FIT,
)

C02Atom = dict[str, Any]
BINDING_MODE_FACT_LINKS_FIRST = "fact_links_first"
BINDING_MODE_TAG_LABEL_ONLY = "tag_label_only"


def _index_skills(skill_rows: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_id: dict[str, dict[str, Any]] = {}
    by_label: dict[str, dict[str, Any]] = {}
    for s in skill_rows:
        if not isinstance(s, dict):
            continue
        sid = str(s.get("node_id") or s.get("skill_id") or "").strip()
        if sid:
            by_id[sid] = s
        label = str(s.get("label") or s.get("skill_name") or "").strip().lower()
        if label:
            by_label[label] = s
    return by_id, by_label


def _load_skill_pillar_index(repo_root: Any) -> dict[str, str]:
    if repo_root is None:
        return {}
    from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph

    graph = load_augmented_skills_graph(repo_root=repo_root)
    out: dict[str, str] = {}
    for row in graph.get("skill_rows") or []:
        if isinstance(row, dict):
            sid = str(row.get("skill_id") or "").strip()
            if sid:
                out[sid] = str(row.get("pillar") or "").strip()
    return out


def _link_sort_key(
    link: dict[str, Any],
    *,
    skill_pillar_by_id: dict[str, str],
    pillar_hints: tuple[str, ...],
) -> tuple[int, int, str]:
    sid = str(link.get("skill_id") or "")
    pillar = skill_pillar_by_id.get(sid, "")
    pillar_match = 0 if pillar_hints and pillar in pillar_hints else 1
    claim_rank = 0 if link.get("claim_eligibility") else 1
    return (claim_rank, pillar_match, sid)


def _fact_links_by_fact(inner: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for link in inner.get("fact_links") or []:
        if not isinstance(link, dict):
            continue
        fid = str(link.get("fact_id") or "").strip()
        if not fid:
            continue
        out.setdefault(fid, []).append(link)
    for link in inner.get("selected_fact_links") or []:
        if not isinstance(link, dict):
            continue
        fid = str(link.get("fact_id") or "").strip()
        if not fid:
            continue
        out.setdefault(fid, []).append(link)
    return out


def _bind_atom(
    *,
    atom: C02Atom,
    section_id: str,
    inner: dict[str, Any],
    skill_by_id: dict[str, dict[str, Any]],
    skill_by_label: dict[str, dict[str, Any]],
    links_by_fact: dict[str, list[dict[str, Any]]],
    binding_mode: str,
    skill_pillar_by_id: dict[str, str] | None = None,
    pillar_hints: tuple[str, ...] = (),
) -> dict[str, Any]:
    fid = str(atom.get("fact_id") or "")
    tags = [str(t).lower() for t in (atom.get("skill_tags") or [])]
    graph_nodes: list[str] = []
    adjacent: list[str] = []
    labels: list[str] = []
    strength = GRAPH_STRENGTH_NONE
    claim_support = False
    binding_source = "none"

    if binding_mode != BINDING_MODE_TAG_LABEL_ONLY:
        eligible_links = sorted(
            links_by_fact.get(fid) or [],
            key=lambda lk: _link_sort_key(
                lk,
                skill_pillar_by_id=skill_pillar_by_id or {},
                pillar_hints=pillar_hints,
            ),
        )
        for lk in eligible_links:
            sid = str(lk.get("skill_id") or "").strip()
            if not sid or sid in graph_nodes:
                continue
            sk = skill_by_id.get(sid)
            if sk or lk.get("claim_eligibility"):
                graph_nodes.append(sid)
                labels.append(REL_DIRECT_SUPPORT)
                strength = GRAPH_STRENGTH_DIRECT
                binding_source = "skill_fact_links"
                if atom.get("proof_status") == "proof_eligible" and bool(lk.get("claim_eligibility")):
                    claim_support = True

    if not graph_nodes:
        for tag in tags:
            sk = skill_by_label.get(tag)
            if sk:
                sid = str(sk.get("node_id") or sk.get("skill_id") or tag)
                if sid not in graph_nodes:
                    graph_nodes.append(sid)
                labels.append(REL_DIRECT_SUPPORT)
                strength = GRAPH_STRENGTH_DIRECT
                binding_source = "capability_tag_label"
                if atom.get("proof_status") == "proof_eligible":
                    claim_support = True

    if not graph_nodes and tags:
        labels.append(REL_ADJACENCY_ONLY)
        strength = GRAPH_STRENGTH_ADJACENT_ONLY
        adjacent = tags[:3]
        claim_support = False
        binding_source = "adjacency_only"

    if section_id:
        labels.append(REL_SECTION_FIT)

    return {
        "fact_id": fid,
        "graph_node_refs": graph_nodes,
        "career_phase_refs": list(atom.get("career_phase_refs") or []),
        "skill_cluster_refs": [
            str(p.get("node_id") or "")
            for p in (inner.get("pillars") or [])
            if isinstance(p, dict)
        ][:5],
        "adjacent_skill_refs": adjacent,
        "metric_binding_refs": list(atom.get("metric_refs") or []),
        "section_fit_refs": [section_id] if section_id else [],
        "lineage_refs": [str(atom.get("source_span_ref") or "")],
        "relationship_labels": sorted(set(labels)),
        "graph_support_strength": strength,
        "claim_support_allowed": claim_support,
        "binding_source": binding_source,
        "reason": "graph expansion over C0.2 atoms; no new facts minted",
    }


def expand_c03_graph_bindings(
    *,
    section_id: str,
    atoms: list[C02Atom],
    role_family_key: str = "SVP_ENGINEERING_AI_PLATFORM",
    repo_root: Any = None,
    binding_mode: str = BINDING_MODE_FACT_LINKS_FIRST,
) -> dict[str, Any]:
    """Map existing facts to graph relationships — no new atoms."""
    from apps_rg.runtime.c0.c03_graph_ref_policy import (
        aggregate_graph_ref_classes,
        compress_binding_for_executive_summary,
        resolve_role_family_projection,
    )

    fact_ids = [str(a.get("fact_id") or "") for a in atoms if a.get("fact_id")]
    projection = resolve_role_family_projection(role_family_key, repo_root=repo_root)
    ctx = assemble_c03_graph_sqlite_context(
        role_family_key=role_family_key,
        section_id=section_id,
        selected_fact_ids=fact_ids,
        repo_root=repo_root,
        pillar_hint_ids=list(projection.get("pillar_hint_ids") or []),
    )
    inner = ctx.get("context") if isinstance(ctx.get("context"), dict) else ctx
    skill_rows = list(inner.get("skills") or [])
    skill_by_id, skill_by_label = _index_skills(skill_rows)
    links_by_fact = _fact_links_by_fact(inner)
    pillar_hints = tuple(projection.get("pillar_hint_ids") or ()) or resolve_c0_pillar_hints(
        role_family_key, repo_root=repo_root
    )
    skill_pillar_by_id = _load_skill_pillar_index(repo_root)
    bindings = [
        _bind_atom(
            atom=atom,
            section_id=section_id,
            inner=inner,
            skill_by_id=skill_by_id,
            skill_by_label=skill_by_label,
            links_by_fact=links_by_fact,
            binding_mode=binding_mode,
            skill_pillar_by_id=skill_pillar_by_id,
            pillar_hints=pillar_hints,
        )
        for atom in atoms
    ]
    if section_id == "executive_summary":
        bindings = [
            compress_binding_for_executive_summary(
                b,
                role_family_projection=projection,
                skill_pillar_by_id=skill_pillar_by_id,
            )
            for b in bindings
        ]
    pillar_aligned = sum(
        1
        for b in bindings
        if b.get("binding_source") == "skill_fact_links"
        and any(
            skill_pillar_by_id.get(sid, "") in pillar_hints
            for sid in (b.get("graph_node_refs") or [])
        )
    )
    direct = sum(1 for b in bindings if b.get("graph_support_strength") == GRAPH_STRENGTH_DIRECT)
    link_direct = sum(
        1 for b in bindings if b.get("binding_source") == "skill_fact_links"
    )
    from apps_rg.runtime.c0.c0_section_authority import c03_skills_graph_receipt_flags

    flags = c03_skills_graph_receipt_flags(core_graph_rag_ran=False)
    ref_classes = aggregate_graph_ref_classes(bindings)
    return {
        "schema_version": "c03_skills_graph_v1",
        "step_id": "C0.3_skills_graph",
        "section_id": section_id,
        "role_family_key": role_family_key,
        "binding_mode": binding_mode,
        "bindings": bindings,
        **flags,
        "role_family_projection": projection,
        "graph_ref_classes": ref_classes,
        "binding_metrics": {
            "atom_count": len(bindings),
            "direct_support_count": direct,
            "skill_fact_link_direct_count": link_direct,
            "adjacent_only_count": sum(
                1
                for b in bindings
                if b.get("graph_support_strength") == GRAPH_STRENGTH_ADJACENT_ONLY
            ),
            "fact_links_available": sum(len(v) for v in links_by_fact.values()),
            "pillar_hint_count": len(pillar_hints),
            "pillar_aligned_direct_count": pillar_aligned,
        },
        "graph_context_ref": ctx.get("sqlite_db_path") or ctx.get("graph_sqlite_path") or "",
        "new_atoms_created": 0,
        "pending_trace_promoted": False,
    }


__all__ = [
    "BINDING_MODE_FACT_LINKS_FIRST",
    "BINDING_MODE_TAG_LABEL_ONLY",
    "expand_c03_graph_bindings",
]
