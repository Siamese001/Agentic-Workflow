"""IBM role episode bundle evidence — C0/C0.3 consumption for ibm_bullets and ibm_narrative.

Proof authority is graph role episode bundles plus linked source facts, not flat skill lists.
Base resume and archive material are calibration/provenance only — never prose hydration.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.runtime.sections.ibm_graph_role_episode_registry import (
    HOLD_AND_DO_NOT_PROMOTE_METRICS,
    IBM_EMPLOYER_ID,
    IBM_EMPLOYER_NODE_ID,
    IBM_TIME_WINDOW,
    assert_role_episode_bundle_id_present,
    get_all_bundles,
    get_bundle_by_id,
    get_bundles_for_section,
    validate_bundle,
)

# C0 marker — kept for template/X2 compatibility with ORGANIC_FROM_GRAPH_BUNDLE treatment.
GRAPH_BULLET_EVIDENCE_PACK_MARKER = "IBM_ROLE_EPISODE_EVIDENCE_PACK"
IBM_ROLE_EPISODE_EVIDENCE_MARKER = GRAPH_BULLET_EVIDENCE_PACK_MARKER

IBM_BULLET_SLOT_IDS: tuple[str, ...] = (
    "bul_ibm_001",
    "bul_ibm_002",
    "bul_ibm_003",
    "bul_ibm_004",
    "bul_ibm_005",
)

# One primary role episode bundle per bullet slot (employer-bound themes).
IBM_BULLET_SLOT_BUNDLE_MAP: dict[str, str] = {
    "bul_ibm_001": "reb_ibm_cloud_modernization",
    "bul_ibm_002": "reb_ibm_cloud_modernization",
    "bul_ibm_003": "reb_ibm_devsecops_reliability",
    "bul_ibm_004": "reb_ibm_metadata_audit_governance",
    "bul_ibm_005": "reb_ibm_hyperscaler_alliance_partner",
}

# Promotable metric outcome IDs (explicit allow-list for X2 metric binding).
PROMOTABLE_METRIC_OUTCOME_IDS: tuple[str, ...] = (
    "metric_ibm_20pct_joint_revenue_growth",
    "metric_ibm_10m_arr",
    "metric_ibm_10pct_finops_savings_gated",
)

# FinOps metric requires second-source confirmation before metric-bearing claims.
FINOPS_METRIC_OUTCOME_ID = "metric_ibm_10pct_finops_savings_gated"
FINOPS_CONFIRMED_OUTCOME_ID = "metric_ibm_10pct_finops_savings_confirmed"

FORBIDDEN_METRIC_SUBSTRINGS: tuple[str, ...] = (
    "$15m",
    "$15 m",
    "$30m",
    "$30 m",
    "15m incremental",
    "30m cloud pak",
    "25%",
    "30%",
    "35%",
    "40%",
    "50%",
)

# Watson Studio: supporting technical context only — not metric-bearing authority.
WATSON_STUDIO_SKILL_ID = "skill_ibm_watson_studio_analytics"

IBM_FORBIDDEN_C0_PROMPT_SUBSTRINGS: tuple[str, ...] = (
    "CANONICAL IBM FACTS",
    "REWRITE_FROM_FACT_POOL",
    "rewrite from these",
    "archive_reference_only",
    "claim_text:",
)

_AUTHORITY_HEADER_LINES: tuple[str, ...] = (
    "proof_authority = graph_role_episode_bundles_plus_linked_source_facts",
    "base_resume_usage = calibration_only",
    "jd_usage = targeting_only",
    "archive_usage = provenance_only",
    "examples_usage = style_only",
    "flat_skill_list_graph_context = forbidden",
    (
        "Generate organically from IBM role episode bundles. "
        "Do not copy or paraphrase base/archive prose."
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


def _bundle_allowed_metric_outcome_ids(bundle: dict[str, Any]) -> list[str]:
    """Map bundle promotable_metrics strings to stable outcome IDs."""
    ids: list[str] = []
    for entry in bundle.get("promotable_metrics") or []:
        s = str(entry).lower()
        if "20%" in s and "joint" in s:
            ids.append("metric_ibm_20pct_joint_revenue_growth")
        elif "$10m" in s or "10m arr" in s:
            ids.append("metric_ibm_10m_arr")
        elif "10%" in s and "finops" in s:
            ids.append(FINOPS_METRIC_OUTCOME_ID)
    return ids


def _mechanism_vocab_from_bundle(bundle: dict[str, Any]) -> list[str]:
    """Structured tokens from bundle scope signals — not archive/base prose."""
    tokens: list[str] = []
    for sig in (bundle.get("architecture_scope_signals") or []) + (
        bundle.get("executive_scope_signals") or []
    ):
        s = str(sig).strip()
        if not s:
            continue
        # Short keyword phrases only (max 6 words per token).
        words = s.split()
        if len(words) <= 6:
            tokens.append(s)
        else:
            # Extract known tech tokens from longer signals.
            for kw in (
                "microservices",
                "cloud-native",
                "DevSecOps",
                "CI/CD",
                "streaming",
                "Confluent",
                "metadata",
                "audit",
                "RBAC",
                "HPC",
                "stress testing",
                "IBM-AWS",
                "alliance",
                "co-sell",
            ):
                if kw.lower() in s.lower() and kw not in tokens:
                    tokens.append(kw)
    return tokens[:8]


def build_ibm_role_episode_section_packet(
    section_id: str,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Build machine-readable role episode packet for a section (C0.3 / proof_pool metadata)."""
    bundles = get_bundles_for_section(section_id)
    skill_index = _skill_rows_by_id(repo_root)
    bundle_records: list[dict[str, Any]] = []
    for bundle in bundles:
        is_valid, violations = validate_bundle(bundle)
        if not is_valid:
            raise ValueError(
                f"Invalid role episode bundle {bundle.get('role_episode_bundle_id')}: {violations}"
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
                        "confidence_grade": row.get("confidence_grade"),
                    }
                )
        bundle_records.append(
            {
                "role_episode_bundle_id": bundle["role_episode_bundle_id"],
                "employer": bundle["employer"],
                "employer_node_id": bundle["employer_node_id"],
                "title": bundle.get("title"),
                "time_window": bundle["time_window"],
                "graph_skill_node_ids": list(bundle.get("graph_skill_node_ids") or []),
                "linked_source_fact_ids": list(bundle.get("linked_source_fact_ids") or []),
                "linked_archive_signal_ids": list(bundle.get("linked_archive_signal_ids") or []),
                "allowed_metric_outcome_ids": _bundle_allowed_metric_outcome_ids(bundle),
                "held_metrics": list(bundle.get("held_metrics") or []),
                "excluded_metrics": list(bundle.get("excluded_metrics") or []),
                "executive_scope_signals": list(bundle.get("executive_scope_signals") or []),
                "architecture_scope_signals": list(bundle.get("architecture_scope_signals") or []),
                "operating_context": bundle.get("operating_context"),
                "bullet_intent": bundle.get("bullet_intent"),
                "section_eligibility": list(bundle.get("section_eligibility") or []),
                "bound_skills": skill_nodes,
            }
        )
    return {
        "section_id": section_id,
        "employer": IBM_EMPLOYER_ID,
        "employer_node_id": IBM_EMPLOYER_NODE_ID,
        "time_window": IBM_TIME_WINDOW,
        "role_episode_bundles": bundle_records,
        "role_episode_bundle_ids": [b["role_episode_bundle_id"] for b in bundle_records],
        "consumption_mode": "role_episode_bundle_required",
        "flat_skill_only_forbidden": True,
        "promotable_metric_outcome_ids": list(PROMOTABLE_METRIC_OUTCOME_IDS),
        "forbidden_metric_substrings": list(FORBIDDEN_METRIC_SUBSTRINGS),
    }


def attach_role_episode_bundles_to_proof_pool_metadata(
    meta: dict[str, Any],
    *,
    section_id: str,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Merge role episode bundle packet into proof_pool_metadata (ibm_* sections only)."""
    if section_id not in ("ibm_bullets", "ibm_narrative"):
        return meta
    packet = build_ibm_role_episode_section_packet(section_id, repo_root=repo_root)
    out = dict(meta)
    out["role_episode_bundle_consumption"] = True
    out["role_episode_bundle_consumption_mode"] = "role_episode_bundle_required"
    out["role_episode_bundles"] = packet["role_episode_bundles"]
    out["role_episode_bundle_ids"] = packet["role_episode_bundle_ids"]
    out["ibm_role_episode_section_packet"] = packet
    out["graph_expansion_consumes_role_episode_bundles"] = True
    out["flat_skill_only_graph_context_forbidden"] = True
    return out


def is_flat_skill_only_graph_packet(packet: dict[str, Any]) -> bool:
    """True when graph context is only flat skills without role episode bundle binding."""
    if packet.get("role_episode_bundle_id") or packet.get("role_episode_bundle_ids"):
        return False
    if packet.get("role_episode_bundles"):
        return False
    bundles = packet.get("ibm_role_episode_section_packet") or {}
    if isinstance(bundles, dict) and bundles.get("role_episode_bundles"):
        return False
    # Flat skill list only: has graph_skill_node_ids but no bundle id.
    if packet.get("graph_skill_node_ids") and not packet.get("role_episode_bundle_id"):
        return True
    if packet.get("bound_skills") and not packet.get("role_episode_bundle_id"):
        return True
    return False


def assert_ibm_section_may_consume_graph_context(context: dict[str, Any]) -> None:
    """Guard: IBM sections require role_episode_bundle_id before graph context use."""
    assert_role_episode_bundle_id_present(context)
    if is_flat_skill_only_graph_packet(context):
        raise ValueError(
            "IBM section graph context is flat skill-only; "
            "role_episode_bundle_id and bundle packet required."
        )


def assert_ibm_role_episode_evidence_pack_has_no_forbidden_leaks(pack_text: str) -> None:
    blob = str(pack_text or "")
    hits = [s for s in IBM_FORBIDDEN_C0_PROMPT_SUBSTRINGS if s in blob]
    if hits:
        raise ValueError(
            f"IBM role episode evidence pack contains forbidden template leakage: {hits}"
        )


def format_ibm_role_episode_evidence_pack(
    runtime_payload: dict[str, Any],
    *,
    section_id: str = "ibm_bullets",
) -> str:
    """C0 body: IBM role episode bundles as proof authority (ibm_bullets slot layout or narrative list)."""
    from apps_rg.runtime.sections.selected_role_fact_set import metric_derivative_fact_id

    packet = build_ibm_role_episode_section_packet(section_id)
    runtime_payload["ibm_role_episode_section_packet"] = packet
    runtime_payload["role_episode_bundle_ids"] = packet["role_episode_bundle_ids"]

    plan = runtime_payload.get("selected_fact_plan") or {}
    selection_method = str(plan.get("selection_method") or "ibm_role_episode_bundle")
    allowed_fact_ids_raw = list(runtime_payload.get("allowed_fact_ids") or [])

    header_lines = [
        f"{IBM_ROLE_EPISODE_EVIDENCE_MARKER} "
        "(proof substrate — compose from role_episode_bundle_id + bound_skills + proof atoms):",
        *_AUTHORITY_HEADER_LINES,
        f"- selection_method: {selection_method}",
        "- Each bullet/narrative claim MUST cite role_episode_bundle_id in change_log.",
        "- skill_id alone is not proof; linked_source_fact_ids and allowed_metric_outcome_ids bind claims.",
        "- Do NOT copy, paraphrase, or lightly rewrite base-resume or archive bullet wording.",
        "- HOLD and DO_NOT_PROMOTE metrics are forbidden in output (25/30/35/40%, $15M, $30M).",
        f"- {WATSON_STUDIO_SKILL_ID}: supporting technical context only — not metric-bearing authority.",
    ]
    if allowed_fact_ids_raw:
        ordered = sorted(str(x) for x in allowed_fact_ids_raw)
        header_lines.append(
            "\nALLOWED_SOURCE_FACT_IDS "
            "(claim_ledger.source_fact_ids must cite only these IDs):"
        )
        for fid in ordered:
            header_lines.append(f"- {fid}")

    header_lines.append(
        "\nPROMOTABLE_METRIC_OUTCOME_IDS "
        "(metric claims allowed only when bound to these IDs):"
    )
    for mid in PROMOTABLE_METRIC_OUTCOME_IDS:
        header_lines.append(f"- {mid}")
    header_lines.append(
        f"- {FINOPS_METRIC_OUTCOME_ID} requires base-resume second-source confirmation "
        f"before metric-bearing use (else use {FINOPS_CONFIRMED_OUTCOME_ID} only if confirmed)."
    )

    header = "\n".join(header_lines)

    if section_id == "ibm_narrative":
        blocks = [_format_narrative_bundle_block(b, skill_index=_skill_rows_by_id()) for b in packet["role_episode_bundles"]]
        out = header + "\n\n" + "\n\n".join(blocks)
        assert_ibm_role_episode_evidence_pack_has_no_forbidden_leaks(out)
        return out

    # ibm_bullets: one block per bul_ibm_* slot bound to primary bundle.
    skill_index = _skill_rows_by_id()
    slot_blocks: list[str] = []
    for slot_id in IBM_BULLET_SLOT_IDS:
        bundle_id = IBM_BULLET_SLOT_BUNDLE_MAP.get(slot_id, "")
        bundle = get_bundle_by_id(bundle_id) if bundle_id else None
        if not bundle:
            slot_blocks.append(f"{slot_id} | ERROR: missing bundle {bundle_id}")
            continue

        allowed_metrics = _bundle_allowed_metric_outcome_ids(bundle)
        slot_allowed: list[str] = [slot_id]
        vocab = _mechanism_vocab_from_bundle(bundle)

        lines = [
            f"{slot_id} | compose_one_bullet_from:",
            f"  role_episode_bundle_id: {bundle_id}",
            f"  employer: {bundle.get('employer')} | time_window: {bundle.get('time_window')}",
            f"  title: {bundle.get('title')}",
            f"  allowed_source_fact_ids: {list(bundle.get('linked_source_fact_ids') or []) + [slot_id]}",
            f"  allowed_metric_outcome_ids: {allowed_metrics or '(none — qualitative only)'}",
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
                conf = sk.get("confidence_grade", "")
                note = ""
                if sid == WATSON_STUDIO_SKILL_ID:
                    note = " | SUPPORTING_CONTEXT_ONLY — no metric-bearing claims"
                lines.append(f"    - {sid} | allowed_phrases: {phrases}{note}")
        lines.append("  proof_atoms (structured tokens only — no prose):")
        if vocab:
            lines.append(f"    - mechanism_vocab: {vocab}")

        slot_blocks.append("\n".join(lines))

    out = header + "\n\n" + "\n\n".join(slot_blocks)
    assert_ibm_role_episode_evidence_pack_has_no_forbidden_leaks(out)
    return out


def _format_narrative_bundle_block(
    bundle_record: dict[str, Any],
    *,
    skill_index: dict[str, dict[str, Any]],
) -> str:
    bid = bundle_record.get("role_episode_bundle_id", "")
    lines = [
        f"ROLE_EPISODE_BUNDLE {bid}:",
        f"  employer: {bundle_record.get('employer')} | time_window: {bundle_record.get('time_window')}",
        f"  title: {bundle_record.get('title')}",
        f"  graph_skill_node_ids: {bundle_record.get('graph_skill_node_ids')}",
        f"  linked_source_fact_ids: {bundle_record.get('linked_source_fact_ids')}",
        f"  allowed_metric_outcome_ids: {bundle_record.get('allowed_metric_outcome_ids')}",
        f"  operating_context: {bundle_record.get('operating_context')}",
        f"  bullet_intent: {bundle_record.get('bullet_intent')}",
        "  Synthesize one IBM role arc sentence from these bundles — do not recap each bullet line.",
    ]
    bound = bundle_record.get("bound_skills") or []
    if bound:
        lines.append("  bound_skills (graph authority — vocabulary anchors only):")
        for sk in bound:
            if not isinstance(sk, dict):
                continue
            sid = str(sk.get("skill_id") or "")
            phrases = ", ".join(list(sk.get("allowed_phrases") or [])[:5])
            note = " (supporting context only — no metrics)" if sid == WATSON_STUDIO_SKILL_ID else ""
            lines.append(f"    - {sid} | allowed_phrases: {phrases}{note}")
    return "\n".join(lines)


def scan_forbidden_metrics_in_text(text: str) -> list[str]:
    """Return forbidden metric substrings found in output text."""
    lower = str(text or "").lower()
    hits: list[str] = []
    for forbidden in FORBIDDEN_METRIC_SUBSTRINGS:
        if forbidden.lower() in lower:
            hits.append(forbidden)
    for held in HOLD_AND_DO_NOT_PROMOTE_METRICS:
        if held.lower() in lower and held not in hits:
            # Only flag $15M/$30M as whole phrases
            if "$" in held or "%" in held:
                hits.append(held)
    return hits


def check_watson_studio_metric_bearing_claim(
    *,
    graph_skill_node_ids: list[str],
    text: str,
    metric_outcome_ids: list[str] | None = None,
) -> tuple[bool, str]:
    """Watson Studio may appear as supporting context only — not as sole metric authority."""
    sids = {str(x) for x in (graph_skill_node_ids or [])}
    if WATSON_STUDIO_SKILL_ID not in sids:
        return True, "watson_not_used"
    # If Watson is the only skill and text has metrics, fail.
    if len(sids) == 1 and re.search(r"[\$%]|\d+\s*%", text):
        return False, "watson_only_skill_with_metric_claim"
    allowed = set(metric_outcome_ids or [])
    if WATSON_STUDIO_SKILL_ID in sids and re.search(r"watson.*(\$|%|\d+%)", text, re.I):
        if not allowed:
            return False, "watson_metric_claim_without_outcome_id"
    return True, "ok"


# Backward-compatible alias used by ibm_bullets_graph_evidence / PA.
def format_ibm_graph_bullet_evidence_pack(runtime_payload: dict[str, Any]) -> str:
    return format_ibm_role_episode_evidence_pack(runtime_payload, section_id="ibm_bullets")


__all__ = [
    "GRAPH_BULLET_EVIDENCE_PACK_MARKER",
    "IBM_BULLET_SLOT_BUNDLE_MAP",
    "IBM_BULLET_SLOT_IDS",
    "IBM_ROLE_EPISODE_EVIDENCE_MARKER",
    "PROMOTABLE_METRIC_OUTCOME_IDS",
    "FORBIDDEN_METRIC_SUBSTRINGS",
    "WATSON_STUDIO_SKILL_ID",
    "attach_role_episode_bundles_to_proof_pool_metadata",
    "assert_ibm_role_episode_evidence_pack_has_no_forbidden_leaks",
    "assert_ibm_section_may_consume_graph_context",
    "build_ibm_role_episode_section_packet",
    "check_watson_studio_metric_bearing_claim",
    "format_ibm_graph_bullet_evidence_pack",
    "format_ibm_role_episode_evidence_pack",
    "is_flat_skill_only_graph_packet",
    "scan_forbidden_metrics_in_text",
]
