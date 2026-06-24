"""Unify role episode bundle evidence — C0 consumption for unify_bullets and unify_narrative.

Proof authority is graph role episode bundles plus linked source facts, not flat skill
lists. Base resume and archive material are calibration/provenance only — never prose
hydration. Metrics require approved metric_outcome_ids.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.runtime.sections.graph_evidence_contract import (
    require_section_packet,
    require_selected_graph_evidence_plan,
)
from apps_rg.runtime.sections.unify_graph_role_episode_registry import (
    APPROVED_METRIC_OUTCOME_IDS,
    BUNDLES_PATH as UNIFY_BUNDLES_PATH,
    UNIFY_EMPLOYER_ID,
    UNIFY_EMPLOYER_NODE_ID,
    UNIFY_TIME_WINDOW,
    assert_role_episode_bundle_id_present,
    get_bundle_by_id,
    get_bundles_for_section,
    validate_bundle,
)
from apps_rg.runtime.sections.role_episode_metric_registry import (
    metric_outcome_nodes_from_path,
)

UNIFY_ROLE_EPISODE_EVIDENCE_MARKER = "UNIFY_ROLE_EPISODE_EVIDENCE_PACK"

UNIFY_BULLET_SLOT_IDS: tuple[str, ...] = (
    "bul_unify_001",
    "bul_unify_002",
    "bul_unify_003",
    "bul_unify_004",
    "bul_unify_005",
    "bul_unify_006",
)

UNIFY_BULLET_SLOT_BUNDLE_MAP: dict[str, str] = {
    "bul_unify_001": "reb_unify_agentic_platform_architecture",
    "bul_unify_002": "reb_unify_dependency_graph_accelerator",
    "bul_unify_003": "reb_unify_runtime_reliability_governance",
    "bul_unify_004": "reb_unify_production_adoption_lifecycle",
    "bul_unify_005": "reb_unify_distributed_ecosystem_engineering",
    "bul_unify_006": "reb_unify_platform_commercialization_leadership",
}

UNIFY_METRIC_PROTECTED_BULLET_SLOT_IDS: set[str] = {"bul_unify_004", "bul_unify_006"}

def resolve_unify_bullet_slot_bundle_map(
    role_family_key: str = "",
    *,
    repo_root: Path | None = None,
) -> dict[str, str]:
    """JD-fit slot→bundle map for unify_bullets (fail closed; no static default fallback)."""
    from apps_rg.runtime.sections.jd_fit_bundle_selection import (
        resolve_jd_fit_slot_bundle_map,
    )

    if not role_family_key:
        raise ValueError("unify_bullets: graph packet is mandatory; missing role_family_key")
    graph = load_augmented_skills_graph(repo_root=repo_root or _repo_root())
    return resolve_jd_fit_slot_bundle_map(
        role_family_key=role_family_key,
        default_map=UNIFY_BULLET_SLOT_BUNDLE_MAP,
        slot_ids=UNIFY_BULLET_SLOT_IDS,
        bundles_for_section=lambda sec: get_bundles_for_section(sec),
        section_id="unify_bullets",
        skill_index=_skill_rows_by_id(repo_root),
        graph=graph,
        protected_slots=UNIFY_METRIC_PROTECTED_BULLET_SLOT_IDS,
    )

UNIFY_FORBIDDEN_C0_PROMPT_SUBSTRINGS: tuple[str, ...] = (
    "CANONICAL UNIFY FACTS",
    "rewrite from these",
    "archive_reference_only",
    "claim_text:",
    "Agentic AI platform architecture — one outcome spine",
)

_AUTHORITY_HEADER_LINES: tuple[str, ...] = (
    "proof_authority = graph_role_episode_bundles_plus_linked_source_facts",
    "base_resume_usage = calibration_only",
    "jd_usage = targeting_only",
    "archive_usage = provenance_only",
    "examples_usage = style_only",
    "flat_skill_list_graph_context = forbidden",
    (
        "Generate organically from Unify role episode bundles. "
        "Do not copy or paraphrase base/archive prose. Do not demote into generic consulting delivery."
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


def _unify_metric_outcome_nodes() -> dict[str, dict[str, Any]]:
    return metric_outcome_nodes_from_path(UNIFY_BUNDLES_PATH)


def _bundle_allowed_metric_outcome_ids(bundle: dict[str, Any]) -> list[str]:
    return [str(x) for x in (bundle.get("linked_metric_outcome_ids") or []) if str(x).strip()]


def _metric_surface_tokens(metric_id: str) -> list[str]:
    node = _unify_metric_outcome_nodes().get(metric_id) or {}
    tokens: list[str] = []
    for raw in [node.get("metric"), *(node.get("surface_tokens") or []), node.get("claim_text")]:
        text = str(raw or "").strip()
        if text and text not in tokens:
            tokens.append(text)
    return tokens[:5]


def _metric_option_label(metric_id: str) -> str:
    node = _unify_metric_outcome_nodes().get(metric_id) or {}
    metric = str(node.get("metric") or "").strip()
    tokens = _metric_surface_tokens(metric_id)
    if metric:
        return f"{metric_id} | metric: {metric} | surface_tokens: {tokens}"
    return metric_id


def _mechanism_vocab_from_bundle(bundle: dict[str, Any]) -> list[str]:
    tokens: list[str] = []
    for sig in (bundle.get("architecture_scope_signals") or []):
        s = str(sig).strip()
        if not s:
            continue
        for kw in (
            "deterministic routing", "multi-agent orchestration", "GraphRAG",
            "sandboxed execution", "policy gates", "replayable execution traces",
            "telemetry", "rollback controls", "evaluation gates", "dependency graph",
            "architecture visibility", "vector services", "API gateways", "Databricks",
            "Lakehouse", "high availability", "parallel decision workflows",
            "reusable platform services", "commercialization",
        ):
            if kw.lower() in s.lower() and kw not in tokens:
                tokens.append(kw)
    return tokens[:8]


def _role_family_required_axes(target_role_profile: str) -> tuple[str, ...]:
    profile = str(target_role_profile or "").strip().upper()
    if profile == "PARTNER_APPLIED_AI_ARCHITECTURE":
        return (
            "agentic_platform_architecture",
            "partner_channel_cosell",
            "enterprise_adoption_revenue",
            "production_adoption_lifecycle",
            "distributed_ecosystem_engineering",
            "platform_commercialization_leadership",
        )
    return (
        "agentic_platform_architecture",
        "dependency_graph_accelerator",
        "runtime_reliability_governance",
        "production_adoption_lifecycle",
        "distributed_ecosystem_engineering",
        "platform_commercialization_leadership",
    )


def build_unify_graph_traversal_sufficiency_receipt(
    *,
    section_id: str,
    target_role_profile: str,
    slot_bundle_map: dict[str, str],
    packet: dict[str, Any],
) -> dict[str, Any]:
    """Receipt proving Unify bullets traverse role roots -> skills -> metric outcomes."""
    bundles = [
        b for b in (packet.get("role_episode_bundles") or [])
        if isinstance(b, dict) and b.get("role_episode_bundle_id")
    ]
    bundle_by_id = {str(b["role_episode_bundle_id"]): b for b in bundles}
    eligible_ids = [str(b["role_episode_bundle_id"]) for b in bundles]
    selected_ids: list[str] = []
    for slot_id in UNIFY_BULLET_SLOT_IDS:
        bid = str(slot_bundle_map.get(slot_id) or "").strip()
        if bid and bid not in selected_ids:
            selected_ids.append(bid)
    rejected_ids = [bid for bid in eligible_ids if bid not in selected_ids]
    unexplained_ids = [bid for bid in selected_ids if bid not in bundle_by_id]

    def _collect(ids: list[str], field: str) -> list[str]:
        out: list[str] = []
        seen: set[str] = set()
        for bid in ids:
            bundle = bundle_by_id.get(bid) or {}
            for raw in bundle.get(field) or []:
                item = str(raw).strip()
                if item and item not in seen:
                    seen.add(item)
                    out.append(item)
        return out

    selected_skill_ids = _collect(selected_ids, "graph_skill_node_ids")
    rejected_skill_ids = _collect(rejected_ids, "graph_skill_node_ids")
    selected_metric_ids = _collect(selected_ids, "linked_metric_outcome_ids")
    rejected_metric_ids = _collect(rejected_ids, "linked_metric_outcome_ids")
    selected_axes = [
        str((bundle_by_id.get(bid) or {}).get("root_capability_node_id") or bid.replace("reb_unify_", ""))
        for bid in selected_ids
    ]
    required_axes = list(_role_family_required_axes(target_role_profile))
    missing_axes = [axis for axis in required_axes if axis not in selected_axes]

    return {
        "receipt_schema": "unify_graph_traversal_sufficiency_v1",
        "section_id": section_id,
        "target_role_profile": target_role_profile,
        "unify_bullet_slot_bundle_map_resolved": dict(slot_bundle_map),
        "selected_role_episode_bundle_ids": selected_ids,
        "rejected_sibling_role_episode_bundle_ids": rejected_ids,
        "selected_role_episode_root_count": len(selected_ids),
        "selected_unique_leaf_skill_count": len(selected_skill_ids),
        "selected_unique_metric_count": len(selected_metric_ids),
        "rejected_sibling_skill_count": len(rejected_skill_ids),
        "rejected_sibling_metric_count": len(rejected_metric_ids),
        "selected_leaf_skill_ids": selected_skill_ids,
        "rejected_sibling_skill_ids": rejected_skill_ids,
        "selected_metric_outcome_ids": selected_metric_ids,
        "rejected_sibling_metric_ids": rejected_metric_ids,
        "frontier_size_by_hop_depth": {
            "hop_0_role_episode_roots": len(selected_ids),
            "hop_1_graph_skill_nodes": len(selected_skill_ids),
            "hop_2_metric_outcome_nodes": len(selected_metric_ids),
            "rejected_hop_0_sibling_roots": len(rejected_ids),
            "rejected_hop_1_sibling_skill_nodes": len(rejected_skill_ids),
            "rejected_hop_2_sibling_metric_nodes": len(rejected_metric_ids),
        },
        "candidate_conservation": {
            "eligible_role_episode_root_count": len(eligible_ids),
            "selected_role_episode_root_count": len(selected_ids),
            "rejected_role_episode_root_count": len(rejected_ids),
            "unexplained_selected_role_episode_bundle_ids": unexplained_ids,
            "pass": not unexplained_ids and (set(selected_ids) | set(rejected_ids)) == set(eligible_ids),
        },
        "role_specific_axis_coverage": {
            "required_axes": required_axes,
            "selected_axes": selected_axes,
            "missing_axes": missing_axes,
        },
    }


def build_unify_role_episode_section_packet(
    section_id: str,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Build machine-readable role episode packet for a Unify section."""
    bundles = get_bundles_for_section(section_id)
    skill_index = _skill_rows_by_id(repo_root)
    bundle_records: list[dict[str, Any]] = []
    for bundle in bundles:
        ok, violations = validate_bundle(bundle)
        if not ok:
            raise ValueError(
                f"Invalid Unify role episode bundle {bundle.get('role_episode_bundle_id')}: {violations}"
            )
        skill_nodes: list[dict[str, Any]] = []
        for sid in bundle.get("graph_skill_node_ids") or []:
            row = skill_index.get(str(sid))
            if row:
                skill_nodes.append(
                    {
                        "skill_id": sid,
                        "allowed_phrases": list(row.get("allowed_phrases") or [])[:6],
                        "activation_status": row.get("activation_status"),
                    }
                )
        bundle_records.append(
            {
                "role_episode_bundle_id": bundle["role_episode_bundle_id"],
                "employer": bundle["employer"],
                "employer_node_id": bundle["employer_node_id"],
                "title": bundle.get("title"),
                "time_window": UNIFY_TIME_WINDOW,
                "root_capability_node_id": bundle.get("root_capability_node_id"),
                "bundle_theme": bundle.get("bundle_theme"),
                "graph_skill_node_ids": list(bundle.get("graph_skill_node_ids") or []),
                "linked_source_fact_ids": list(bundle.get("linked_source_fact_ids") or []),
                "linked_metric_outcome_ids": list(bundle.get("linked_metric_outcome_ids") or []),
                "allowed_metric_outcome_ids": _bundle_allowed_metric_outcome_ids(bundle),
                "executive_scope_signals": list(bundle.get("executive_scope_signals") or []),
                "architecture_scope_signals": list(bundle.get("architecture_scope_signals") or []),
                "operating_context": bundle.get("operating_context"),
                "bullet_intent": bundle.get("bullet_intent"),
                "section_eligibility": list(bundle.get("section_eligibility") or []),
                "external_claim_policy": bundle.get("external_claim_policy"),
                "activation_status": bundle.get("activation_status"),
                "bound_skills": skill_nodes,
            }
        )
    return {
        "section_id": section_id,
        "employer": UNIFY_EMPLOYER_ID,
        "employer_node_id": UNIFY_EMPLOYER_NODE_ID,
        "time_window": UNIFY_TIME_WINDOW,
        "role_episode_bundles": bundle_records,
        "role_episode_bundle_ids": [b["role_episode_bundle_id"] for b in bundle_records],
        "consumption_mode": "role_episode_bundle_required",
        "flat_skill_only_forbidden": True,
        "approved_metric_outcome_ids": list(APPROVED_METRIC_OUTCOME_IDS),
    }


def attach_role_episode_bundles_to_proof_pool_metadata(
    meta: dict[str, Any],
    *,
    section_id: str,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Merge Unify role episode bundle packet into proof_pool_metadata (unify_* sections only)."""
    if section_id not in ("unify_bullets", "unify_narrative"):
        return meta
    packet = build_unify_role_episode_section_packet(section_id, repo_root=repo_root)
    out = dict(meta)
    out["role_episode_bundle_consumption"] = True
    out["role_episode_bundle_consumption_mode"] = "role_episode_bundle_required"
    out["role_episode_bundles"] = packet["role_episode_bundles"]
    out["role_episode_bundle_ids"] = packet["role_episode_bundle_ids"]
    out["unify_role_episode_section_packet"] = packet
    out["graph_expansion_consumes_role_episode_bundles"] = True
    out["flat_skill_only_graph_context_forbidden"] = True
    out["approved_metric_outcome_ids"] = packet["approved_metric_outcome_ids"]
    if section_id == "unify_bullets":
        plan = out.get("selected_graph_evidence_plan") if isinstance(out.get("selected_graph_evidence_plan"), dict) else {}
        target_role_profile = str(
            plan.get("role_family_key")
            or plan.get("target_role_profile")
            or out.get("role_family_key")
            or out.get("target_role_profile")
            or ""
        ).strip()
        if target_role_profile:
            try:
                slot_bundle_map = resolve_unify_bullet_slot_bundle_map(
                    target_role_profile,
                    repo_root=repo_root,
                )
            except ValueError:
                slot_bundle_map = dict(UNIFY_BULLET_SLOT_BUNDLE_MAP)
        else:
            slot_bundle_map = dict(UNIFY_BULLET_SLOT_BUNDLE_MAP)
        out["unify_bullet_slot_bundle_map_resolved"] = slot_bundle_map
        out["unify_graph_traversal_sufficiency_receipt"] = build_unify_graph_traversal_sufficiency_receipt(
            section_id=section_id,
            target_role_profile=target_role_profile or "DEFAULT",
            slot_bundle_map=slot_bundle_map,
            packet=packet,
        )
    return out


def is_flat_skill_only_graph_packet(packet: dict[str, Any]) -> bool:
    if not isinstance(packet, dict):
        return False
    if packet.get("role_episode_bundle_id") or packet.get("role_episode_bundle_ids"):
        return False
    if packet.get("role_episode_bundles"):
        return False
    nested = packet.get("unify_role_episode_section_packet") or {}
    if isinstance(nested, dict) and nested.get("role_episode_bundles"):
        return False
    if packet.get("graph_skill_node_ids") or packet.get("bound_skills"):
        return True
    return False


def assert_unify_role_episode_evidence_pack_has_no_forbidden_leaks(pack_text: str) -> None:
    blob = str(pack_text or "")
    hits = [s for s in UNIFY_FORBIDDEN_C0_PROMPT_SUBSTRINGS if s in blob]
    if hits:
        raise ValueError(
            f"Unify role episode evidence pack contains forbidden template leakage: {hits}"
        )


def format_unify_role_episode_evidence_pack(
    runtime_payload: dict[str, Any],
    *,
    section_id: str = "unify_bullets",
) -> str:
    """C0 body: Unify role episode bundles as proof authority (bullets slots or narrative list)."""
    plan = runtime_payload.get("selected_fact_plan") or {}
    selection_method = str(plan.get("selection_method") or "unify_role_episode_bundle")
    allowed_fact_ids_raw = list(runtime_payload.get("allowed_fact_ids") or [])

    if section_id == "unify_narrative":
        packet = build_unify_role_episode_section_packet(section_id)
        runtime_payload["unify_role_episode_section_packet"] = packet
        runtime_payload["role_episode_bundle_ids"] = packet["role_episode_bundle_ids"]
    else:
        packet = require_section_packet(
            runtime_payload,
            section_id=section_id,
            packet_key="unify_role_episode_section_packet",
        )
        runtime_payload["unify_role_episode_section_packet"] = packet
        runtime_payload["role_episode_bundle_ids"] = packet["role_episode_bundle_ids"]

    header_lines = [
        f"{UNIFY_ROLE_EPISODE_EVIDENCE_MARKER} "
        "(proof substrate — compose from role_episode_bundle_id + bound_skills + proof atoms):",
        *_AUTHORITY_HEADER_LINES,
        f"- selection_method: {selection_method}",
        "- Each bullet/narrative claim MUST cite role_episode_bundle_id in change_log.",
        "- skill_id alone is not proof; linked_source_fact_ids and approved metric_outcome_ids bind claims.",
        (
            "- metric_outcome_usage_contract: every bul_unify_* bullet MUST choose >=1 "
            "approved metric_outcome_id from its slot bundle, surface one of that node's metric/"
            "surface_tokens in bullet_text, set metric_raw to the chosen metric_outcome_id(s), "
            "and record it in change_log.metric_outcome_ids[]."
        ),
        "- Internal-only signals (dependency graph accelerator, identity controls) are supporting context — not external metrics.",
    ]
    if allowed_fact_ids_raw:
        header_lines.append(
            "\nALLOWED_SOURCE_FACT_IDS (claim_ledger.source_fact_ids must cite only these IDs):"
        )
        for fid in sorted(str(x) for x in allowed_fact_ids_raw):
            header_lines.append(f"- {fid}")
    header_lines.append(
        "\nAPPROVED_METRIC_OUTCOME_IDS (metric claims allowed only when bound to these IDs):"
    )
    for mid in APPROVED_METRIC_OUTCOME_IDS:
        header_lines.append(f"- {_metric_option_label(mid)}")

    header = "\n".join(header_lines)

    if section_id == "unify_narrative":
        blocks = [_format_narrative_bundle_block(b) for b in packet["role_episode_bundles"]]
        out = header + "\n\n" + "\n\n".join(blocks)
        assert_unify_role_episode_evidence_pack_has_no_forbidden_leaks(out)
        return out

    skill_index = _skill_rows_by_id()
    selected_graph_plan = require_selected_graph_evidence_plan(runtime_payload, section_id=section_id)
    _role_family_key = str(
        selected_graph_plan.get("role_family_key")
        or selected_graph_plan.get("target_role_profile")
        or ""
    ).strip()
    if not _role_family_key:
        raise ValueError(
            f"{section_id}: graph packet is mandatory; selected_graph_evidence_plan missing role_family_key"
        )
    graph_profile_keys = set(
        (load_augmented_skills_graph(repo_root=_repo_root()).get("role_family_projection_profiles") or {}).keys()
    )
    if _role_family_key not in graph_profile_keys:
        from apps_rg.fact_inventory.track_weighted_graph_expansion import (
            infer_projection_role_family_key,
        )

        inferred_role_family_key = infer_projection_role_family_key(
            target_role=str(runtime_payload.get("target_title") or runtime_payload.get("target_role") or ""),
            jd_text=str(runtime_payload.get("jd_text") or ""),
            briefing_text=str(runtime_payload.get("briefing") or runtime_payload.get("briefing_text") or ""),
        )
        if inferred_role_family_key in graph_profile_keys:
            _role_family_key = inferred_role_family_key
    meta = runtime_payload.get("proof_pool_metadata") if isinstance(runtime_payload.get("proof_pool_metadata"), dict) else {}
    slot_bundle_map = meta.get("unify_bullet_slot_bundle_map_resolved")
    if not isinstance(slot_bundle_map, dict) or not slot_bundle_map:
        slot_bundle_map = resolve_unify_bullet_slot_bundle_map(_role_family_key)
    runtime_payload["unify_bullet_slot_bundle_map_resolved"] = slot_bundle_map
    if isinstance(meta, dict):
        meta["unify_bullet_slot_bundle_map_resolved"] = slot_bundle_map
        meta.setdefault(
            "unify_graph_traversal_sufficiency_receipt",
            build_unify_graph_traversal_sufficiency_receipt(
                section_id=section_id,
                target_role_profile=_role_family_key,
                slot_bundle_map=slot_bundle_map,
                packet=packet,
            ),
        )
    slot_blocks: list[str] = []
    for slot_id in UNIFY_BULLET_SLOT_IDS:
        bundle_id = slot_bundle_map.get(slot_id, "")
        bundle = get_bundle_by_id(bundle_id) if bundle_id else None
        if not bundle:
            slot_blocks.append(f"{slot_id} | ERROR: missing bundle {bundle_id}")
            continue
        vocab = _mechanism_vocab_from_bundle(bundle)
        allowed_metrics = _bundle_allowed_metric_outcome_ids(bundle)
        lines = [
            f"{slot_id} | compose_one_bullet_from:",
            f"  role_episode_bundle_id: {bundle_id}",
            f"  employer: {bundle.get('employer')} | time_window: {UNIFY_TIME_WINDOW}",
            f"  allowed_source_fact_ids: {list(bundle.get('linked_source_fact_ids') or []) + [slot_id]}",
            f"  allowed_metric_outcome_ids: {[_metric_option_label(mid) for mid in allowed_metrics]}",
            (
                "  metric_outcome_usage_contract: choose >=1 approved metric_outcome_id for this "
                "bullet; surface its metric/surface_tokens in bullet_text; record it in "
                "change_log.metric_outcome_ids; set metric_raw to the chosen metric_outcome_id(s)."
            ),
            "  metric_outcome_options:",
            *[f"    - {_metric_option_label(mid)}" for mid in allowed_metrics],
            "  executive_scope_signals:",
        ]
        for sig in bundle.get("executive_scope_signals") or []:
            lines.append(f"    - {sig}")
        lines.append("  architecture_scope_signals:")
        for sig in bundle.get("architecture_scope_signals") or []:
            lines.append(f"    - {sig}")
        lines.append(f"  operating_context: {bundle.get('operating_context')}")
        lines.append(f"  bullet_intent: {bundle.get('bullet_intent')}")
        skill_ids = list(bundle.get("graph_skill_node_ids") or [])
        if skill_ids:
            lines.append("  bound_skills (graph authority — vocabulary anchors only):")
            for sid in skill_ids:
                sk = skill_index.get(sid) or {}
                phrases = ", ".join(list(sk.get("allowed_phrases") or [])[:5])
                lines.append(f"    - {sid} | allowed_phrases: {phrases}")
        if vocab:
            lines.append("  proof_atoms (structured tokens only — no prose):")
            lines.append(f"    - mechanism_vocab: {vocab}")
        slot_blocks.append("\n".join(lines))

    out = header + "\n\n" + "\n\n".join(slot_blocks)
    assert_unify_role_episode_evidence_pack_has_no_forbidden_leaks(out)
    return out


def _format_narrative_bundle_block(bundle_record: dict[str, Any]) -> str:
    bid = bundle_record.get("role_episode_bundle_id", "")
    lines = [
        f"ROLE_EPISODE_BUNDLE {bid}:",
        f"  employer: {bundle_record.get('employer')} | time_window: {bundle_record.get('time_window') or UNIFY_TIME_WINDOW}",
        f"  graph_skill_node_ids: {bundle_record.get('graph_skill_node_ids')}",
        f"  linked_source_fact_ids: {bundle_record.get('linked_source_fact_ids')}",
        f"  allowed_metric_outcome_ids: {bundle_record.get('linked_metric_outcome_ids')}",
        f"  operating_context: {bundle_record.get('operating_context')}",
        f"  bullet_intent: {bundle_record.get('bullet_intent')}",
        "  Synthesize the Unify role arc from these bundles — do not recap each bullet line.",
    ]
    bound = bundle_record.get("bound_skills") or []
    if bound:
        lines.append("  bound_skills (graph authority — vocabulary anchors only):")
        for sk in bound:
            if not isinstance(sk, dict):
                continue
            sid = str(sk.get("skill_id") or "")
            phrases = ", ".join(list(sk.get("allowed_phrases") or [])[:5])
            lines.append(f"    - {sid} | allowed_phrases: {phrases}")
    return "\n".join(lines)


def assert_unify_section_may_consume_graph_context(context: dict[str, Any]) -> None:
    assert_role_episode_bundle_id_present(context)
    if is_flat_skill_only_graph_packet(context):
        raise ValueError(
            "Unify section graph context is flat skill-only; role_episode_bundle_id required."
        )


__all__ = [
    "UNIFY_BULLET_SLOT_BUNDLE_MAP",
    "UNIFY_BULLET_SLOT_IDS",
    "UNIFY_METRIC_PROTECTED_BULLET_SLOT_IDS",
    "UNIFY_ROLE_EPISODE_EVIDENCE_MARKER",
    "assert_unify_role_episode_evidence_pack_has_no_forbidden_leaks",
    "assert_unify_section_may_consume_graph_context",
    "attach_role_episode_bundles_to_proof_pool_metadata",
    "build_unify_graph_traversal_sufficiency_receipt",
    "build_unify_role_episode_section_packet",
    "resolve_unify_bullet_slot_bundle_map",
    "format_unify_role_episode_evidence_pack",
    "is_flat_skill_only_graph_packet",
]
