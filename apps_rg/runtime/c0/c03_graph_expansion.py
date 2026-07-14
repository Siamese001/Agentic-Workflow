"""C0.3 graph relationship expansion over C0.2 atoms only.

Product claim support is fail-closed to one of two direct graph authorities:

* a canonical ``selected_graph_evidence_plan`` already frozen by the section
  proof-pool selector, or
* SQLite-ranked direct ``skill -> fact`` paths from the generated graph
  projection.

Broad fact-link loading and label/tag claim fallbacks are forbidden. An
explicit tag-label diagnostic mode may emit adjacency context, but never claim
support.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping

from apps_rg.runtime.c0.c03_resume_graph_contracts import (
    TraversalRecorder,
    build_candidate_decision,
    build_candidate_receipt,
    evaluate_pretarget_authority,
    stable_digest,
)
from apps_rg.runtime.c0.constants import (
    GRAPH_STRENGTH_ADJACENT_ONLY,
    GRAPH_STRENGTH_DIRECT,
    GRAPH_STRENGTH_NONE,
    REL_ADJACENCY_ONLY,
    REL_DIRECT_SUPPORT,
    REL_SECTION_FIT,
)

C02Atom = dict[str, Any]
BINDING_MODE_FACT_LINKS_FIRST = "fact_links_first"  # compatibility name; strict direct paths
BINDING_MODE_SQLITE_RANKED_ONLY = "sqlite_ranked_only"
BINDING_MODE_TAG_LABEL_ONLY = "tag_label_only"


class C03GraphSelectionError(RuntimeError):
    """Required C0.3 direct graph selection could not be proven."""


def _index_skills(
    skill_rows: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_id: dict[str, dict[str, Any]] = {}
    by_label: dict[str, dict[str, Any]] = {}
    for row in skill_rows:
        if not isinstance(row, dict):
            continue
        skill_id = str(row.get("node_id") or row.get("skill_id") or "").strip()
        if skill_id:
            by_id[skill_id] = row
        label = str(row.get("label") or row.get("skill_name") or "").strip().lower()
        if label:
            by_label[label] = row
    return by_id, by_label


def _load_skill_pillar_index(repo_root: Any) -> dict[str, str]:
    if repo_root is None:
        return {}
    from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph

    graph = load_augmented_skills_graph(repo_root=repo_root)
    return {
        str(row.get("skill_id") or ""): str(row.get("pillar") or "")
        for row in graph.get("skill_rows") or []
        if isinstance(row, dict) and row.get("skill_id")
    }


def _fact_links_by_fact(inner: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Diagnostic count only; these links are never a selection fallback."""
    out: dict[str, list[dict[str, Any]]] = {}
    for key in ("fact_links", "selected_fact_links"):
        for link in inner.get(key) or []:
            if not isinstance(link, dict):
                continue
            fact_id = str(link.get("fact_id") or "").strip()
            if fact_id:
                out.setdefault(fact_id, []).append(link)
    return out


def _skill_ids_from_plan_fact(fact: Mapping[str, Any]) -> list[str]:
    values = (
        fact.get("graph_skill_node_ids")
        or fact.get("selected_skill_ids")
        or fact.get("source_skill_ids")
        or []
    )
    return list(dict.fromkeys(str(value).strip() for value in values if str(value).strip()))


def _plan_fact_id(fact: Mapping[str, Any]) -> str:
    return str(fact.get("fact_id") or fact.get("candidate_fact_id") or "").strip()


def _authority_decision_index(plan: Mapping[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for raw in plan.get("graph_candidate_decision_ledger") or []:
        if not isinstance(raw, Mapping) or str(raw.get("candidate_type") or "") != "leaf_skill":
            continue
        root_id = str(raw.get("root_id") or raw.get("parent_id") or "").strip()
        skill_id = str(raw.get("candidate_id") or "").strip()
        if root_id and skill_id:
            out[(root_id, skill_id)] = dict(raw)
    return out


def _selected_plan_graph_selection(
    *,
    selected_graph_plan: Mapping[str, Any] | None,
    section_id: str,
    repo_root: Any,
) -> dict[str, Any]:
    """Project a frozen section graph plan into the C0.3 direct-binding shape."""
    if not isinstance(selected_graph_plan, Mapping):
        return {"covered_fact_ids": set(), "selected_by_fact": {}, "rejected_by_fact": {}}

    facts = [row for row in selected_graph_plan.get("facts") or [] if isinstance(row, Mapping)]
    facts = [row for row in facts if _plan_fact_id(row) and _skill_ids_from_plan_fact(row)]
    if not facts:
        return {"covered_fact_ids": set(), "selected_by_fact": {}, "rejected_by_fact": {}}

    from apps_rg.fact_inventory.augmented_skills_graph import (
        graph_payload_digest,
        graph_version_from_payload,
        load_augmented_skills_graph,
    )
    from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
        skill_row_eligible_for_external_claim,
    )

    graph = load_augmented_skills_graph(repo_root=repo_root)
    graph_digest = graph_payload_digest(graph)
    skill_by_id = {
        str(row.get("skill_id") or ""): row
        for row in graph.get("skill_rows") or []
        if isinstance(row, dict) and row.get("skill_id")
    }
    upstream_index = _authority_decision_index(selected_graph_plan)
    selected_by_fact: dict[str, list[dict[str, Any]]] = {}
    rejected_by_fact: dict[str, list[dict[str, Any]]] = {}
    decisions: list[dict[str, Any]] = []
    recorder = TraversalRecorder(section_id=section_id, max_hop_depth=1)

    for fact in sorted(facts, key=_plan_fact_id):
        fact_id = _plan_fact_id(fact)
        linked_sources = list(
            fact.get("linked_source_fact_ids")
            or fact.get("linked_identity_fact_ids")
            or fact.get("source_fact_ids")
            or [fact_id]
        )
        selected_rows: list[dict[str, Any]] = []
        rejected_rows: list[dict[str, Any]] = []
        for skill_id in sorted(_skill_ids_from_plan_fact(fact)):
            row = skill_by_id.get(skill_id) or {}
            upstream = upstream_index.get((fact_id, skill_id)) or {}
            upstream_authority = upstream.get("authority")
            if isinstance(upstream_authority, Mapping):
                authority = dict(upstream_authority)
            else:
                allowed_sections = {
                    str(value) for value in row.get("allowed_sections") or [] if str(value).strip()
                }
                eligible = bool(row) and skill_row_eligible_for_external_claim(row)
                source_refs = list(row.get("fact_id_links") or []) + list(
                    row.get("source_snippets") or []
                ) + linked_sources
                authority = evaluate_pretarget_authority(
                    candidate_id=skill_id,
                    candidate_type="leaf_skill",
                    section_id=section_id,
                    section_allowed=(not allowed_sections or section_id in allowed_sections),
                    activation_status=str(row.get("activation_status") or ""),
                    support_level=str(row.get("support_level") or ""),
                    external_claim_policy=str(row.get("external_claim_policy") or ""),
                    external_eligible=eligible,
                    claim_eligible=eligible,
                    source_refs=source_refs,
                    path_present=True,
                    extra_reason_codes=[] if row else ["missing_skill_authority_row"],
                )

            path_id = str(upstream.get("candidate_path_id") or f"plan:{fact_id}/skill:{skill_id}")
            proof_strength = float(upstream.get("proof_strength_raw") or 1.0)
            target_alignment = float(upstream.get("target_alignment_score") or 0.0)
            ranking_score = float(upstream.get("ranking_score") or proof_strength + target_alignment)
            candidate = {
                "fact_id": fact_id,
                "skill_id": skill_id,
                "skill_label": str(row.get("label") or row.get("skill_name") or skill_id),
                "claim_eligibility": bool(authority.get("authority_pass")),
                "link_external_eligible": bool(authority.get("authority_pass")),
                "link_support_level": str(row.get("support_level") or ""),
                "pillar": str(row.get("pillar") or ""),
                "subpillar": str(row.get("subpillar") or ""),
                "domain_id": str(row.get("domain_id") or ""),
                "skill_family": str(row.get("skill_family") or row.get("subpillar") or "unclassified"),
                "metric_bucket": str(row.get("metric_bucket") or "general_business_outcome"),
                "confidence": str(row.get("confidence_grade") or row.get("confidence") or ""),
                "activation_status": str(row.get("activation_status") or ""),
                "support_level": str(row.get("support_level") or ""),
                "external_eligible": bool(authority.get("authority_pass")),
                "source_trace": list(authority.get("source_refs") or linked_sources),
                "section_allowed": bool(authority.get("section_allowed")),
                "path_signature": str(
                    upstream.get("path_signature")
                    or f"{fact_id}->selected_graph_plan_contains_skill->{skill_id}"
                ),
                "proof_strength_raw": proof_strength,
                "target_alignment_score": target_alignment,
                "base_score": round(proof_strength + target_alignment, 6),
                "score": ranking_score,
                "authority": authority,
                "authority_pass": bool(authority.get("authority_pass")),
                "selection_source": "selected_graph_evidence_plan",
                "upstream_plan_id": str(selected_graph_plan.get("plan_id") or ""),
                "upstream_plan_digest": str(selected_graph_plan.get("plan_digest") or ""),
            }
            selected = bool(authority.get("authority_pass"))
            if selected:
                selected_rows.append(candidate)
                reason_codes = ["selected_by_frozen_section_graph_plan"]
            else:
                candidate["rejection_reason"] = "authority_gate_failed"
                candidate["failed_gate"] = "pretarget_authority"
                rejected_rows.append(candidate)
                reason_codes = list(authority.get("reason_codes") or ["authority_gate_failed"])

            decision = build_candidate_decision(
                section_id=section_id,
                candidate_id=skill_id,
                candidate_type="leaf_skill",
                candidate_path_id=path_id,
                decision="selected" if selected else "rejected",
                reason_codes=reason_codes,
                authority=authority,
                hop_depth=1,
                parent_id=fact_id,
                root_id=fact_id,
                proof_strength_raw=proof_strength,
                target_alignment_score=target_alignment,
                ranking_score=ranking_score,
                path_signature=str(candidate["path_signature"]),
                extra={"selection_source": "selected_graph_evidence_plan"},
            )
            decisions.append(decision)
            recorder.record(
                event_type="edge_traversed",
                hop_depth=1,
                source_node_id=fact_id,
                target_node_id=skill_id,
                edge_type="selected_graph_plan_contains_skill",
                candidate_path_id=path_id,
            )
            recorder.record(
                event_type="authority_evaluated",
                hop_depth=1,
                source_node_id=fact_id,
                target_node_id=skill_id,
                edge_type="selected_graph_plan_contains_skill",
                candidate_path_id=path_id,
                authority_pass=bool(authority.get("authority_pass")),
                reason_codes=authority.get("reason_codes") or [],
            )
            recorder.record(
                event_type="candidate_terminal",
                hop_depth=1,
                source_node_id=fact_id,
                target_node_id=skill_id,
                edge_type="selected_graph_plan_contains_skill",
                candidate_path_id=path_id,
                authority_pass=bool(authority.get("authority_pass")),
                decision="selected" if selected else "rejected",
                reason_codes=reason_codes,
            )

        selected_by_fact[fact_id] = selected_rows
        rejected_by_fact[fact_id] = rejected_rows

    # Preserve rejected alternatives from a canonical upstream traversal when
    # they belong to selected facts and are not already represented above.
    represented = {
        (str(row.get("root_id") or ""), str(row.get("candidate_id") or ""))
        for row in decisions
    }
    covered = set(selected_by_fact)
    for raw in selected_graph_plan.get("graph_candidate_decision_ledger") or []:
        if not isinstance(raw, Mapping) or str(raw.get("candidate_type") or "") != "leaf_skill":
            continue
        root_id = str(raw.get("root_id") or raw.get("parent_id") or "").strip()
        skill_id = str(raw.get("candidate_id") or "").strip()
        if root_id not in covered or not skill_id or (root_id, skill_id) in represented:
            continue
        authority = dict(raw.get("authority") or {})
        candidate = {
            "fact_id": root_id,
            "skill_id": skill_id,
            "skill_label": skill_id,
            "metric_bucket": str(raw.get("metric_bucket") or "general_business_outcome"),
            "skill_family": str(raw.get("skill_family") or "unclassified"),
            "path_signature": str(raw.get("path_signature") or ""),
            "proof_strength_raw": float(raw.get("proof_strength_raw") or 0.0),
            "target_alignment_score": float(raw.get("target_alignment_score") or 0.0),
            "score": float(raw.get("ranking_score") or 0.0),
            "authority": authority,
            "authority_pass": bool(authority.get("authority_pass")),
            "rejection_reason": ",".join(str(value) for value in raw.get("reason_codes") or []),
            "failed_gate": "upstream_section_plan",
            "selection_source": "selected_graph_evidence_plan",
        }
        rejected_by_fact.setdefault(root_id, []).append(candidate)
        decision = dict(raw)
        decisions.append(decision)
        path_id = str(decision.get("candidate_path_id") or f"plan:{root_id}/skill:{skill_id}")
        recorder.record(
            event_type="edge_traversed",
            hop_depth=1,
            source_node_id=root_id,
            target_node_id=skill_id,
            edge_type="selected_graph_plan_contains_skill",
            candidate_path_id=path_id,
        )
        recorder.record(
            event_type="authority_evaluated",
            hop_depth=1,
            source_node_id=root_id,
            target_node_id=skill_id,
            edge_type="selected_graph_plan_contains_skill",
            candidate_path_id=path_id,
            authority_pass=bool(authority.get("authority_pass")),
            reason_codes=authority.get("reason_codes") or [],
        )
        recorder.record(
            event_type="candidate_terminal",
            hop_depth=1,
            source_node_id=root_id,
            target_node_id=skill_id,
            edge_type="selected_graph_plan_contains_skill",
            candidate_path_id=path_id,
            authority_pass=bool(authority.get("authority_pass")),
            decision=str(decision.get("decision") or "rejected"),
            reason_codes=decision.get("reason_codes") or [],
        )

    decisions.sort(key=lambda row: str(row.get("candidate_path_id") or ""))
    candidate_receipt = build_candidate_receipt(section_id=section_id, decisions=decisions)
    traversal_receipt = recorder.build_receipt(decisions=decisions)
    authority_rows = [dict(row.get("authority") or {}) for row in decisions]
    authority_receipt = {
        "schema_version": "c03_pretarget_authority_receipt_v1",
        "section_id": section_id,
        "candidate_count": len(authority_rows),
        "authority_pass_count": sum(1 for row in authority_rows if row.get("authority_pass")),
        "authority_block_count": sum(1 for row in authority_rows if not row.get("authority_pass")),
        "targeting_consulted_count": sum(1 for row in authority_rows if row.get("targeting_consulted")),
        "authority_before_targeting_pass": all(
            row.get("targeting_consulted") is False
            and row.get("authority_evaluated_before_targeting") is True
            for row in authority_rows
        ),
        "authority_decisions_digest": stable_digest(authority_rows),
    }
    return {
        "schema_version": "c03_selected_graph_plan_selection_v1",
        "selection_policy": "frozen_section_graph_plan_direct_paths_v1",
        "graph_source": "augmented_skills_graph",
        "graph_version": graph_version_from_payload(graph),
        "graph_hash": graph_digest,
        "covered_fact_ids": set(selected_by_fact),
        "selected_by_fact": selected_by_fact,
        "rejected_by_fact": rejected_by_fact,
        "selected_candidates": [row for rows in selected_by_fact.values() for row in rows],
        "rejected_siblings": [row for rows in rejected_by_fact.values() for row in rows],
        "candidate_decision_ledger": decisions,
        "graph_candidate_receipt": candidate_receipt,
        "graph_traversal_receipt": traversal_receipt,
        "pretarget_authority_receipt": authority_receipt,
        "source_authority_contract": {
            "schema_version": "c03_source_authority_contract_v1",
            "authority_source": "augmented_skills_graph",
            "graph_digest": graph_digest,
            "authority_evaluated_before_targeting": True,
            "targeting_inputs_are_non_authority": True,
            "missing_ranked_frontier_fails_closed": True,
            "upstream_plan_id": str(selected_graph_plan.get("plan_id") or ""),
            "upstream_plan_digest": str(selected_graph_plan.get("plan_digest") or ""),
        },
        "candidate_count": len(decisions),
        "selected_skill_count": sum(len(rows) for rows in selected_by_fact.values()),
        "rejected_sibling_skill_count": sum(len(rows) for rows in rejected_by_fact.values()),
        "authority_block_count": authority_receipt["authority_block_count"],
        "candidate_conservation_pass": bool(candidate_receipt["candidate_conservation_pass"]),
        "selection_contract_pass": bool(
            candidate_receipt["candidate_conservation_pass"]
            and traversal_receipt["pass"]
            and authority_receipt["authority_before_targeting_pass"]
        ),
    }



def _bundle_root_graph_selection(
    *, fact_ids: list[str], section_id: str, repo_root: Any
) -> dict[str, Any]:
    """Build direct candidates for role-episode roots present in C0.2 atoms."""
    wanted = {str(value).strip() for value in fact_ids if str(value).strip()}
    if not wanted or repo_root is None:
        return {"covered_fact_ids": set(), "selected_by_fact": {}, "rejected_by_fact": {}}
    import json
    from pathlib import Path

    root = Path(repo_root)
    facts: list[dict[str, Any]] = []
    for filename in (
        "unify_role_episode_bundles.json",
        "ibm_role_episode_bundles.json",
        "insurtech_role_episode_bundles.json",
        "ey_role_episode_bundles.json",
    ):
        path = root / "apps_rg" / "fact_inventory" / filename
        if not path.is_file():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        for bundle in doc.get("bundles") or []:
            if not isinstance(bundle, Mapping):
                continue
            bundle_id = str(bundle.get("role_episode_bundle_id") or "").strip()
            if bundle_id not in wanted:
                continue
            facts.append(
                {
                    "fact_id": bundle_id,
                    "candidate_fact_id": bundle_id,
                    "graph_skill_node_ids": list(bundle.get("graph_skill_node_ids") or []),
                    "linked_source_fact_ids": list(bundle.get("linked_source_fact_ids") or []),
                    "source_fact_ids": [bundle_id],
                }
            )
    if not facts:
        return {"covered_fact_ids": set(), "selected_by_fact": {}, "rejected_by_fact": {}}
    return _selected_plan_graph_selection(
        selected_graph_plan={
            "section_id": section_id,
            "selection_method": "c03_role_episode_root_direct_lookup",
            "facts": facts,
        },
        section_id=section_id,
        repo_root=repo_root,
    )


def _atom_query_fact_id(atom: Mapping[str, Any]) -> str:
    surface = str(atom.get("fact_id") or "").strip()
    span = str(atom.get("source_span_ref") or "").strip()
    if span.startswith("ledger:"):
        ledger_id = span.split("ledger:", 1)[1].strip()
        if ledger_id:
            return ledger_id
    return surface


def _remap_sqlite_selection(
    selection: dict[str, Any], *, query_to_surfaces: Mapping[str, list[str]]
) -> dict[str, Any]:
    """Map SQLite ledger fact IDs back to canonical section surface IDs."""
    if not selection or not query_to_surfaces:
        return selection
    out = dict(selection)
    selected_by_fact: dict[str, list[dict[str, Any]]] = {}
    rejected_by_fact: dict[str, list[dict[str, Any]]] = {}
    for query_id, surfaces in query_to_surfaces.items():
        for surface in surfaces:
            selected_rows: list[dict[str, Any]] = []
            for raw in (selection.get("selected_by_fact") or {}).get(query_id, []) or []:
                row = dict(raw)
                row["ledger_fact_id"] = query_id
                row["fact_id"] = surface
                selected_rows.append(row)
            rejected_rows: list[dict[str, Any]] = []
            for raw in (selection.get("rejected_by_fact") or {}).get(query_id, []) or []:
                row = dict(raw)
                row["ledger_fact_id"] = query_id
                row["fact_id"] = surface
                rejected_rows.append(row)
            selected_by_fact[surface] = selected_rows
            rejected_by_fact[surface] = rejected_rows
    decisions: list[dict[str, Any]] = []
    for raw in selection.get("candidate_decision_ledger") or []:
        if not isinstance(raw, Mapping):
            continue
        query_id = str(raw.get("root_id") or raw.get("parent_id") or "").strip()
        surfaces = query_to_surfaces.get(query_id) or [query_id]
        for surface in surfaces:
            row = dict(raw)
            row["ledger_fact_id"] = query_id
            row["root_id"] = surface
            row["parent_id"] = surface
            skill_id = str(row.get("candidate_id") or "")
            row["candidate_path_id"] = f"fact:{surface}/skill:{skill_id}"
            decisions.append(row)
    out["selected_by_fact"] = selected_by_fact
    out["rejected_by_fact"] = rejected_by_fact
    out["selected_candidates"] = [row for rows in selected_by_fact.values() for row in rows]
    out["rejected_siblings"] = [row for rows in rejected_by_fact.values() for row in rows]
    out["candidate_decision_ledger"] = decisions
    out["candidate_count"] = len(decisions)
    out["selected_skill_count"] = len(out["selected_candidates"])
    out["rejected_sibling_skill_count"] = len(out["rejected_siblings"])
    out["graph_candidate_receipt"] = build_candidate_receipt(
        section_id=str(out.get("section_id") or ""), decisions=decisions
    )
    return out

def _combine_component_receipts(
    *, section_id: str, components: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any]]:
    decisions: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    authority_rows: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    for component in components:
        if not component:
            continue
        decisions.extend(
            dict(row) for row in component.get("candidate_decision_ledger") or [] if isinstance(row, Mapping)
        )
        traversal = component.get("graph_traversal_receipt") or {}
        events.extend(dict(row) for row in traversal.get("events") or [] if isinstance(row, Mapping))
        authority = component.get("pretarget_authority_receipt") or {}
        component_rows.append(
            {
                "schema_version": component.get("schema_version"),
                "selection_policy": component.get("selection_policy"),
                "graph_source": component.get("graph_source"),
                "candidate_count": component.get("candidate_count", 0),
                "selection_contract_pass": bool(component.get("selection_contract_pass")),
            }
        )
        for decision in component.get("candidate_decision_ledger") or []:
            if isinstance(decision, Mapping):
                authority_rows.append(dict(decision.get("authority") or {}))

    decisions.sort(key=lambda row: str(row.get("candidate_path_id") or ""))
    for index, event in enumerate(events):
        event["event_index"] = index
    candidate_receipt = build_candidate_receipt(section_id=section_id, decisions=decisions)
    candidate_receipt["component_receipts"] = component_rows
    duplicate_paths = candidate_receipt.get("duplicate_candidate_path_ids") or []
    terminal_count = sum(1 for row in decisions if row.get("decision") in {"selected", "rejected"})
    traversal_pass = bool(
        all(row.get("selection_contract_pass") for row in component_rows)
        and terminal_count == len(decisions)
        and not duplicate_paths
    )
    traversal_receipt = {
        "schema_version": "graph_traversal_receipt_v1",
        "event_schema_version": "graph_traversal_event_v1",
        "producer": "apps_rg.runtime.c0.c03_graph_expansion._combine_component_receipts",
        "section_id": section_id,
        "traversal_mode": "combined_direct_path_components",
        "event_count": len(events),
        "events_digest": stable_digest(events),
        "events": events,
        "visited_edges_count": sum(1 for event in events if event.get("event_type") == "edge_traversed"),
        "authority_event_count": sum(1 for event in events if event.get("event_type") == "authority_evaluated"),
        "candidate_conservation": {
            "candidate_count": len(decisions),
            "terminal_decision_count": terminal_count,
            "unexplained_candidate_count": len(decisions) - terminal_count,
            "duplicate_candidate_path_ids": duplicate_paths,
            "pass": traversal_pass,
        },
        "component_receipts": component_rows,
        "replayable": True,
        "pass": traversal_pass,
    }
    authority_receipt = {
        "schema_version": "c03_pretarget_authority_receipt_v1",
        "section_id": section_id,
        "candidate_count": len(authority_rows),
        "authority_pass_count": sum(1 for row in authority_rows if row.get("authority_pass")),
        "authority_block_count": sum(1 for row in authority_rows if not row.get("authority_pass")),
        "targeting_consulted_count": sum(1 for row in authority_rows if row.get("targeting_consulted")),
        "authority_before_targeting_pass": all(
            row.get("targeting_consulted") is False
            and row.get("authority_evaluated_before_targeting") is True
            for row in authority_rows
        ),
        "authority_decisions_digest": stable_digest(authority_rows),
        "component_receipts": component_rows,
    }
    return decisions, candidate_receipt, traversal_receipt, authority_receipt


def _bind_atom(
    *,
    atom: C02Atom,
    section_id: str,
    inner: dict[str, Any],
    binding_mode: str,
    selected_by_fact: dict[str, list[dict[str, Any]]],
    rejected_by_fact: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    fact_id = str(atom.get("fact_id") or "")
    tags = [str(value).lower() for value in atom.get("skill_tags") or []]
    selected = list(selected_by_fact.get(fact_id) or [])
    rejected = list(rejected_by_fact.get(fact_id) or [])
    graph_nodes: list[str] = []
    adjacent: list[str] = []
    labels: list[str] = []
    strength = GRAPH_STRENGTH_NONE
    claim_support = False
    binding_source = "ranked_candidates_missing"

    if binding_mode != BINDING_MODE_TAG_LABEL_ONLY and selected:
        graph_nodes = list(
            dict.fromkeys(
                str(candidate.get("skill_id") or "").strip()
                for candidate in selected
                if str(candidate.get("skill_id") or "").strip()
            )
        )
        if graph_nodes:
            labels.append(REL_DIRECT_SUPPORT)
            strength = GRAPH_STRENGTH_DIRECT
            binding_source = "skill_fact_links"
            claim_support = bool(
                atom.get("proof_status") == "proof_eligible"
                and all(
                    bool((candidate.get("authority") or {}).get("authority_pass"))
                    for candidate in selected
                )
                and any(bool(candidate.get("claim_eligibility")) for candidate in selected)
            )
    elif binding_mode == BINDING_MODE_TAG_LABEL_ONLY and tags:
        labels.append(REL_ADJACENCY_ONLY)
        strength = GRAPH_STRENGTH_ADJACENT_ONLY
        adjacent = tags[:3]
        binding_source = "diagnostic_tag_label_only"
        claim_support = False

    if section_id:
        labels.append(REL_SECTION_FIT)
    selection_sources = sorted(
        {str(candidate.get("selection_source") or "sqlite_ranked_skill_fact_links") for candidate in selected}
    )
    return {
        "fact_id": fact_id,
        "graph_node_refs": graph_nodes,
        "career_phase_refs": list(atom.get("career_phase_refs") or []),
        "skill_cluster_refs": [
            str(pillar.get("node_id") or "")
            for pillar in inner.get("pillars") or []
            if isinstance(pillar, dict)
        ][:5],
        "adjacent_skill_refs": adjacent,
        "metric_binding_refs": list(atom.get("metric_refs") or []),
        "section_fit_refs": [section_id] if section_id else [],
        "lineage_refs": [str(atom.get("source_span_ref") or "")],
        "relationship_labels": sorted(set(labels)),
        "graph_support_strength": strength,
        "claim_support_allowed": claim_support,
        "binding_source": binding_source,
        "binding_query_source": "+".join(selection_sources) if selection_sources else binding_source,
        "ranked_selection_required": binding_mode != BINDING_MODE_TAG_LABEL_ONLY,
        "ranked_selection_present": bool(selected),
        "broad_fact_link_fallback_used": False,
        "label_tag_proof_fallback_used": False,
        "selected_metric_buckets": sorted(
            {
                str(candidate.get("metric_bucket") or "general_business_outcome")
                for candidate in selected
            }
        ),
        "rejected_sibling_skill_refs": [
            str(candidate.get("skill_id") or "")
            for candidate in rejected
            if str(candidate.get("skill_id") or "")
        ],
        "rejected_sibling_reasons": [
            {
                "skill_id": str(candidate.get("skill_id") or ""),
                "reason": str(candidate.get("rejection_reason") or ""),
                "failed_gate": str(candidate.get("failed_gate") or ""),
                "metric_bucket": str(
                    candidate.get("metric_bucket") or "general_business_outcome"
                ),
                "authority_reason_codes": list(
                    (candidate.get("authority") or {}).get("reason_codes") or []
                ),
            }
            for candidate in rejected
            if str(candidate.get("skill_id") or "")
        ],
        "sqlite_ranked_candidates": [
            {
                "skill_id": str(candidate.get("skill_id") or ""),
                "score": candidate.get("score"),
                "base_score": candidate.get("base_score"),
                "proof_strength_raw": candidate.get("proof_strength_raw"),
                "target_alignment_score": candidate.get("target_alignment_score"),
                "authority_pass": bool(
                    (candidate.get("authority") or {}).get("authority_pass")
                ),
                "metric_bucket": str(
                    candidate.get("metric_bucket") or "general_business_outcome"
                ),
                "skill_family": str(candidate.get("skill_family") or "unclassified"),
                "path_signature": str(candidate.get("path_signature") or ""),
                "prior_metric_usage": int(candidate.get("prior_metric_usage") or 0),
                "sibling_alternatives": list(candidate.get("sibling_alternatives") or [])[:5],
                "penalties": dict(candidate.get("penalties") or {}),
                "selection_source": str(candidate.get("selection_source") or ""),
            }
            for candidate in selected
            if str(candidate.get("skill_id") or "")
        ],
        "reason": "graph expansion over C0.2 atoms; no new facts minted; direct paths only",
    }


def expand_c03_graph_bindings(
    *,
    section_id: str,
    atoms: list[C02Atom],
    role_family_key: str = "SVP_ENGINEERING_AI_PLATFORM",
    repo_root: Any = None,
    binding_mode: str = BINDING_MODE_FACT_LINKS_FIRST,
    run_id: str = "",
    strict_ranked_selection: bool = True,
    selected_graph_plan: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Map existing facts to authority-passing graph paths without minting atoms."""
    from apps_rg.runtime.c0.c03_graph_ref_policy import (
        aggregate_graph_ref_classes,
        compress_binding_for_executive_summary,
        resolve_role_family_projection,
    )
    from apps_rg.runtime.c0.c03_sqlite_graph_selection import (
        SCHEMA_VERSION as SQLITE_SELECTION_SCHEMA_VERSION,
        select_c03_sqlite_graph_candidates,
    )
    from apps_rg.runtime.c0.c03_role_family import resolve_c0_pillar_hints

    fact_ids = [str(atom.get("fact_id") or "") for atom in atoms if atom.get("fact_id")]
    plan_selection = _selected_plan_graph_selection(
        selected_graph_plan=selected_graph_plan,
        section_id=section_id,
        repo_root=repo_root,
    )
    plan_covered = set(plan_selection.get("covered_fact_ids") or set())
    bundle_selection = _bundle_root_graph_selection(
        fact_ids=[fact_id for fact_id in fact_ids if fact_id not in plan_covered],
        section_id=section_id,
        repo_root=repo_root,
    )
    covered_fact_ids = plan_covered | set(bundle_selection.get("covered_fact_ids") or set())
    query_to_surfaces: dict[str, list[str]] = {}
    for atom in atoms:
        surface = str(atom.get("fact_id") or "").strip()
        if not surface or surface in covered_fact_ids:
            continue
        query_id = _atom_query_fact_id(atom)
        query_to_surfaces.setdefault(query_id, []).append(surface)

    # A frozen selected plan is the primary direct authority.  Do not eagerly
    # materialize or query SQLite when that plan (or a canonical role bundle)
    # already covers every atom.  Unknown IDs are also rejected before the
    # projection adapter so a nonexistent fact cannot force a fail-open query.
    from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph

    canonical_graph = load_augmented_skills_graph(repo_root=repo_root)
    canonical_fact_ids = {
        str(fact_id)
        for row in canonical_graph.get("skill_rows") or []
        if isinstance(row, Mapping)
        for fact_id in row.get("fact_id_links") or []
        if str(fact_id).strip()
    }
    canonical_fact_ids.update(
        str(row.get("node_id") or "")
        for row in canonical_graph.get("graph_nodes") or []
        if isinstance(row, Mapping)
        and str(row.get("node_type") or "") in {"fact", "source_fact"}
        and str(row.get("node_id") or "").strip()
    )
    query_to_surfaces = {
        query_id: surfaces
        for query_id, surfaces in query_to_surfaces.items()
        if query_id in canonical_fact_ids
    }
    pillar_hints = resolve_c0_pillar_hints(role_family_key, repo_root=repo_root)
    projection: dict[str, Any] = {
        "role_family_key": role_family_key,
        "pillar_hint_ids": list(pillar_hints),
        "sqlite_projection_row_found": False,
        "projection_source": "frozen_graph_plan_or_canonical_frontier",
        "release_eligible_targeting_proof": False,
        "targeting_degraded_explicit": False,
    }
    ctx: dict[str, Any] = {"sqlite_db_path": "", "context": {}}
    inner: dict[str, Any] = {}
    sqlite_selection: dict[str, Any] = {
        "schema_version": SQLITE_SELECTION_SCHEMA_VERSION,
        "section_id": section_id,
        "selection_policy": "not_needed_frozen_plan_or_no_canonical_frontier",
        "graph_source": "augmented_skills_graph_sqlite",
        "graph_version": "",
        "graph_hash": "",
        "selected_candidates": [],
        "selected_by_fact": {},
        "rejected_by_fact": {},
        "candidate_decision_ledger": [],
        "candidate_count": 0,
        "selected_skill_count": 0,
        "authority_block_count": 0,
        "candidate_conservation_pass": True,
        "selection_contract_pass": True,
        "missing_fact_frontier_ids": [],
        "metric_bucket_counts": {},
        "skill_family_counts": {},
        "rejection_receipts": [],
        "current_run_usage_only": True,
        "run_id_scope": run_id,
    }
    if query_to_surfaces:
        projection = resolve_role_family_projection(role_family_key, repo_root=repo_root)
        pillar_hints = tuple(projection.get("pillar_hint_ids") or ()) or pillar_hints
        # Keep the generated SQLite adapter behind the execution boundary.
        from apps_rg.runtime.c03_graph_sqlite_context import (
            assemble_c03_graph_sqlite_context,
        )

        ctx = assemble_c03_graph_sqlite_context(
            role_family_key=role_family_key,
            section_id=section_id,
            selected_fact_ids=sorted(query_to_surfaces),
            repo_root=repo_root,
            pillar_hint_ids=list(pillar_hints),
        )
        inner = ctx.get("context") if isinstance(ctx.get("context"), dict) else ctx
        sqlite_selection = select_c03_sqlite_graph_candidates(
            section_id=section_id,
            selected_fact_ids=sorted(query_to_surfaces),
            role_family_key=role_family_key,
            pillar_hints=pillar_hints,
            repo_root=repo_root,
            db_path=ctx.get("sqlite_db_path"),
            run_id=run_id,
        )
        sqlite_selection["section_id"] = section_id
        sqlite_selection = _remap_sqlite_selection(
            sqlite_selection, query_to_surfaces=query_to_surfaces
        )
        for candidate in sqlite_selection.get("selected_candidates") or []:
            if isinstance(candidate, dict):
                candidate["selection_source"] = "sqlite_ranked_skill_fact_links"
    links_by_fact = _fact_links_by_fact(inner)
    skill_pillar_by_id = _load_skill_pillar_index(repo_root)

    components = [
        component
        for component in (plan_selection, bundle_selection, sqlite_selection)
        if component and (component.get("candidate_count") or component.get("covered_fact_ids"))
    ]
    selected_by_fact: dict[str, list[dict[str, Any]]] = {}
    rejected_by_fact: dict[str, list[dict[str, Any]]] = {}
    for component in components:
        for fact_id, rows in (component.get("selected_by_fact") or {}).items():
            selected_by_fact.setdefault(str(fact_id), []).extend(list(rows))
        for fact_id, rows in (component.get("rejected_by_fact") or {}).items():
            rejected_by_fact.setdefault(str(fact_id), []).extend(list(rows))

    decisions, candidate_receipt, traversal_receipt, authority_receipt = (
        _combine_component_receipts(section_id=section_id, components=components)
    )
    proof_required_fact_ids = [
        str(atom.get("fact_id") or "")
        for atom in atoms
        if atom.get("proof_status") == "proof_eligible" and atom.get("fact_id")
    ]
    missing_required = [
        fact_id for fact_id in proof_required_fact_ids if not selected_by_fact.get(fact_id)
    ]
    conservation_pass = bool(candidate_receipt.get("candidate_conservation_pass"))
    boundary_pass = bool(authority_receipt.get("authority_before_targeting_pass", True))
    component_pass = all(
        bool(component.get("selection_contract_pass", True)) for component in components
    )
    if strict_ranked_selection and (
        missing_required or not conservation_pass or not boundary_pass or not component_pass
    ):
        reasons: list[str] = []
        if missing_required:
            reasons.append(f"missing_direct_frontier={','.join(sorted(missing_required))}")
        if not conservation_pass:
            reasons.append("candidate_conservation_failed")
        if not boundary_pass:
            reasons.append("authority_targeting_boundary_failed")
        if not component_pass:
            reasons.append("component_selection_contract_failed")
        raise C03GraphSelectionError(
            f"{section_id} C0.3 direct selection blocked: {'; '.join(reasons)}"
        )

    bindings = [
        _bind_atom(
            atom=atom,
            section_id=section_id,
            inner=inner,
            binding_mode=binding_mode,
            selected_by_fact=selected_by_fact,
            rejected_by_fact=rejected_by_fact,
        )
        for atom in atoms
    ]
    if section_id == "executive_summary":
        bindings = [
            compress_binding_for_executive_summary(
                binding,
                role_family_projection=projection,
                skill_pillar_by_id=skill_pillar_by_id,
            )
            for binding in bindings
        ]

    pillar_aligned = sum(
        1
        for binding in bindings
        if binding.get("binding_source") == "skill_fact_links"
        and any(
            skill_pillar_by_id.get(skill_id, "") in pillar_hints
            for skill_id in binding.get("graph_node_refs") or []
        )
    )
    direct = sum(
        1
        for binding in bindings
        if binding.get("graph_support_strength") == GRAPH_STRENGTH_DIRECT
    )
    link_direct = sum(
        1 for binding in bindings if binding.get("binding_source") == "skill_fact_links"
    )
    from apps_rg.runtime.c0.c0_section_authority import c03_skills_graph_receipt_flags

    flags = c03_skills_graph_receipt_flags(core_graph_rag_ran=False)
    ref_classes = aggregate_graph_ref_classes(bindings)
    source_contracts = [
        dict(component.get("source_authority_contract") or {}) for component in components
    ]
    source_authority_contract = {
        "schema_version": "c03_source_authority_contract_v1",
        "authority_source": "augmented_skills_graph",
        "authority_evaluated_before_targeting": True,
        "targeting_inputs_are_non_authority": True,
        "missing_ranked_frontier_fails_closed": True,
        "component_contracts": source_contracts,
        "component_contracts_digest": stable_digest(source_contracts),
    }
    selected_flat = [row for rows in selected_by_fact.values() for row in rows]
    rejected_flat = [row for rows in rejected_by_fact.values() for row in rows]
    metric_bucket_counts = dict(
        sorted(Counter(str(row.get("metric_bucket") or "general_business_outcome") for row in selected_flat).items())
    )
    skill_family_counts = dict(
        sorted(Counter(str(row.get("skill_family") or "unclassified") for row in selected_flat).items())
    )
    return {
        # Keep the historical top-level schema for existing app contracts. The
        # nested authority/candidate/traversal contracts carry the W1-W3 versions.
        "schema_version": "c03_skills_graph_v1",
        "contract_revision": "w1_w3_authority_first_direct_paths_v1",
        "step_id": "C0.3_skills_graph",
        "section_id": section_id,
        "role_family_key": role_family_key,
        "binding_mode": binding_mode,
        "selection_boundary": "frozen_plan_or_sqlite_direct_paths_fail_closed",
        "strict_ranked_selection": bool(strict_ranked_selection),
        "missing_required_fact_ids": missing_required,
        "bindings": bindings,
        **flags,
        "role_family_projection": projection,
        "graph_ref_classes": ref_classes,
        "source_authority_contract": source_authority_contract,
        "pretarget_authority_receipt": authority_receipt,
        "graph_candidate_decision_ledger": decisions,
        "graph_candidate_receipt": candidate_receipt,
        "graph_traversal_receipt": traversal_receipt,
        "binding_metrics": {
            "atom_count": len(bindings),
            "direct_support_count": direct,
            "skill_fact_link_direct_count": link_direct,
            "adjacent_only_count": sum(
                1
                for binding in bindings
                if binding.get("graph_support_strength") == GRAPH_STRENGTH_ADJACENT_ONLY
            ),
            "fact_links_available": sum(len(values) for values in links_by_fact.values()),
            "pillar_hint_count": len(pillar_hints),
            "pillar_aligned_direct_count": pillar_aligned,
            "sqlite_ranked_candidate_count": int(sqlite_selection.get("candidate_count") or 0),
            "selected_plan_candidate_count": int(plan_selection.get("candidate_count") or 0),
            "selected_skill_count": len(selected_flat),
            "rejected_sibling_skill_count": len(rejected_flat),
            "authority_block_count": int(authority_receipt.get("authority_block_count") or 0),
            "candidate_conservation_pass": conservation_pass,
            "metric_bucket_counts": metric_bucket_counts,
        },
        "sqlite_selection_receipt": {
            "schema_version": sqlite_selection.get("schema_version"),
            "selection_policy": sqlite_selection.get("selection_policy"),
            "graph_source": sqlite_selection.get("graph_source"),
            "graph_version": sqlite_selection.get("graph_version"),
            "graph_hash": sqlite_selection.get("graph_hash"),
            "metric_policy_version": sqlite_selection.get("metric_policy_version"),
            "run_id_scope": sqlite_selection.get("run_id_scope"),
            "current_run_usage_only": sqlite_selection.get("current_run_usage_only"),
            "candidate_count": sqlite_selection.get("candidate_count"),
            "selected_skill_count": sqlite_selection.get("selected_skill_count"),
            "authority_block_count": sqlite_selection.get("authority_block_count"),
            "candidate_conservation_pass": sqlite_selection.get("candidate_conservation_pass"),
            "selection_contract_pass": sqlite_selection.get("selection_contract_pass"),
            "missing_fact_frontier_ids": list(sqlite_selection.get("missing_fact_frontier_ids") or []),
            "metric_bucket_counts": dict(sqlite_selection.get("metric_bucket_counts") or {}),
            "skill_family_counts": dict(sqlite_selection.get("skill_family_counts") or {}),
            "rejection_receipts": list(sqlite_selection.get("rejection_receipts") or []),
        },
        "selected_graph_plan_receipt": {
            "schema_version": plan_selection.get("schema_version"),
            "selection_policy": plan_selection.get("selection_policy"),
            "graph_source": plan_selection.get("graph_source"),
            "graph_version": plan_selection.get("graph_version"),
            "graph_hash": plan_selection.get("graph_hash"),
            "covered_fact_ids": sorted(covered_fact_ids),
            "candidate_count": plan_selection.get("candidate_count", 0),
            "selected_skill_count": plan_selection.get("selected_skill_count", 0),
            "candidate_conservation_pass": plan_selection.get("candidate_conservation_pass", True),
            "selection_contract_pass": plan_selection.get("selection_contract_pass", True),
            "upstream_plan_id": str((selected_graph_plan or {}).get("plan_id") or ""),
            "upstream_plan_digest": str((selected_graph_plan or {}).get("plan_digest") or ""),
        },
        "graph_context_ref": ctx.get("sqlite_db_path") or ctx.get("graph_sqlite_path") or "",
        "broad_fact_link_fallback_used": False,
        "label_tag_proof_fallback_used": False,
        "new_atoms_created": 0,
        "pending_trace_promoted": False,
    }


__all__ = [
    "BINDING_MODE_FACT_LINKS_FIRST",
    "BINDING_MODE_SQLITE_RANKED_ONLY",
    "BINDING_MODE_TAG_LABEL_ONLY",
    "C03GraphSelectionError",
    "expand_c03_graph_bindings",
]
