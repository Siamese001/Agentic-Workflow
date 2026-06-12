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
from apps_rg.runtime.sections.unify_graph_role_episode_registry import (
    APPROVED_METRIC_OUTCOME_IDS,
    UNIFY_EMPLOYER_ID,
    UNIFY_EMPLOYER_NODE_ID,
    UNIFY_TIME_WINDOW,
    assert_role_episode_bundle_id_present,
    get_bundle_by_id,
    get_bundles_for_section,
    validate_bundle,
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

def resolve_unify_bullet_slot_bundle_map(
    role_family_key: str = "",
    *,
    repo_root: Path | None = None,
) -> dict[str, str]:
    """JD-fit slot→bundle map for unify_bullets (delegates to the shared selector)."""
    from apps_rg.runtime.sections.jd_fit_bundle_selection import (
        resolve_jd_fit_slot_bundle_map,
    )

    if not role_family_key:
        return dict(UNIFY_BULLET_SLOT_BUNDLE_MAP)
    graph = load_augmented_skills_graph(repo_root=repo_root or _repo_root())
    return resolve_jd_fit_slot_bundle_map(
        role_family_key=role_family_key,
        default_map=UNIFY_BULLET_SLOT_BUNDLE_MAP,
        slot_ids=UNIFY_BULLET_SLOT_IDS,
        bundles_for_section=lambda sec: get_bundles_for_section(sec),
        section_id="unify_bullets",
        skill_index=_skill_rows_by_id(repo_root),
        graph=graph,
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
                "graph_skill_node_ids": list(bundle.get("graph_skill_node_ids") or []),
                "linked_source_fact_ids": list(bundle.get("linked_source_fact_ids") or []),
                "linked_metric_outcome_ids": list(bundle.get("linked_metric_outcome_ids") or []),
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
    packet = build_unify_role_episode_section_packet(section_id)
    runtime_payload["unify_role_episode_section_packet"] = packet
    runtime_payload["role_episode_bundle_ids"] = packet["role_episode_bundle_ids"]

    plan = runtime_payload.get("selected_fact_plan") or {}
    selection_method = str(plan.get("selection_method") or "unify_role_episode_bundle")
    allowed_fact_ids_raw = list(runtime_payload.get("allowed_fact_ids") or [])

    header_lines = [
        f"{UNIFY_ROLE_EPISODE_EVIDENCE_MARKER} "
        "(proof substrate — compose from role_episode_bundle_id + bound_skills + proof atoms):",
        *_AUTHORITY_HEADER_LINES,
        f"- selection_method: {selection_method}",
        "- Each bullet/narrative claim MUST cite role_episode_bundle_id in change_log.",
        "- skill_id alone is not proof; linked_source_fact_ids and approved metric_outcome_ids bind claims.",
        "- Metric claims allowed only when bound to an approved metric_outcome_id.",
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
        header_lines.append(f"- {mid}")

    header = "\n".join(header_lines)

    if section_id == "unify_narrative":
        blocks = [_format_narrative_bundle_block(b) for b in packet["role_episode_bundles"]]
        out = header + "\n\n" + "\n\n".join(blocks)
        assert_unify_role_episode_evidence_pack_has_no_forbidden_leaks(out)
        return out

    skill_index = _skill_rows_by_id()
    # JD-fit slot→bundle map: a partnerships JD promotes the partner/co-sell bundle into a
    # slot; an engineering JD reproduces the static default. Resolved role family flows in
    # via proof_pool_metadata (set by the lane); absent → static default.
    _ppm = runtime_payload.get("proof_pool_metadata") or {}
    _tw = _ppm.get("track_weighted_graph_expansion") or {}
    _role_family_key = str(
        _tw.get("projection_role_family_key")
        or _ppm.get("projection_role_family_key")
        or ""
    )
    slot_bundle_map = resolve_unify_bullet_slot_bundle_map(_role_family_key)
    runtime_payload["unify_bullet_slot_bundle_map_resolved"] = slot_bundle_map
    slot_blocks: list[str] = []
    for slot_id in UNIFY_BULLET_SLOT_IDS:
        bundle_id = slot_bundle_map.get(slot_id, "")
        bundle = get_bundle_by_id(bundle_id) if bundle_id else None
        if not bundle:
            slot_blocks.append(f"{slot_id} | ERROR: missing bundle {bundle_id}")
            continue
        vocab = _mechanism_vocab_from_bundle(bundle)
        lines = [
            f"{slot_id} | compose_one_bullet_from:",
            f"  role_episode_bundle_id: {bundle_id}",
            f"  employer: {bundle.get('employer')} | time_window: {UNIFY_TIME_WINDOW}",
            f"  allowed_source_fact_ids: {list(bundle.get('linked_source_fact_ids') or []) + [slot_id]}",
            f"  allowed_metric_outcome_ids: {list(bundle.get('linked_metric_outcome_ids') or []) or '(none — qualitative only)'}",
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
    "UNIFY_ROLE_EPISODE_EVIDENCE_MARKER",
    "assert_unify_role_episode_evidence_pack_has_no_forbidden_leaks",
    "assert_unify_section_may_consume_graph_context",
    "attach_role_episode_bundles_to_proof_pool_metadata",
    "build_unify_role_episode_section_packet",
    "resolve_unify_bullet_slot_bundle_map",
    "format_unify_role_episode_evidence_pack",
    "is_flat_skill_only_graph_packet",
]
