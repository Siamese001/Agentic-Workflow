"""IBM role episode bundle evidence — C0/C0.3 consumption for ibm_bullets and ibm_narrative.

Proof authority is graph role episode bundles plus linked source facts, not flat skill lists.
Base resume and archive material are calibration/provenance only — never prose hydration.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.runtime.sections.ibm_graph_role_episode_registry import (
    BUNDLES_PATH as IBM_BUNDLES_PATH,
    HOLD_AND_DO_NOT_PROMOTE_METRICS,
    IBM_EMPLOYER_ID,
    IBM_EMPLOYER_NODE_ID,
    IBM_TIME_WINDOW,
    assert_role_episode_bundle_id_present,
    get_bundle_by_id,
    get_bundles_for_section,
    validate_bundle,
)
from apps_rg.runtime.sections.role_episode_metric_registry import (
    approved_metric_outcome_ids_from_path,
    metric_outcome_nodes_from_path,
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

# One primary role episode bundle per bullet slot. The full IBM graph has more
# roots than five bullets; these are the highest-signal bullet lanes.
IBM_BULLET_SLOT_BUNDLE_MAP: dict[str, str] = {
    "bul_ibm_001": "reb_ibm_aws_modernization_architecture",
    "bul_ibm_002": "reb_ibm_cognitive_business_decision_support",
    "bul_ibm_003": "reb_ibm_presales_solution_engineering",
    "bul_ibm_004": "reb_ibm_data_modeling_bi_decision_support",
    "bul_ibm_005": "reb_ibm_aws_alliance_partner_cosell_gtm",
}

def _ibm_metric_outcome_nodes() -> dict[str, dict[str, Any]]:
    return metric_outcome_nodes_from_path(IBM_BUNDLES_PATH)


# Promotable metric outcome IDs are graph-native: presence in metric_outcome_nodes.
PROMOTABLE_METRIC_OUTCOME_IDS: tuple[str, ...] = approved_metric_outcome_ids_from_path(
    IBM_BUNDLES_PATH
)

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


def approved_promotable_metric_evidence(section_id: str) -> list[dict[str, Any]]:
    """X1D judge evidence for approved, promotable, section-eligible metric_outcomes.

    Typed-edge role-facet guardrails: per-bundle metric selection is capped for section
    DISPLAY budgeting (``graph_role_episode_selector`` ``metric_cap``), which can drop an
    approved metric from a low-weight bundle's contribution to the proof pool. But an
    approved, promotable, section-eligible metric_outcome that a bullet legitimately
    surfaces must remain SUPPORTABLE by the X1D grader — otherwise a graph-approved figure
    (e.g. the IBM-AWS alliance "20% joint revenue growth", capped out of ``bul_ibm_005``'s
    bundle contribution when that bundle lands in a low-weight band) reads as
    ``unsupported_metric`` to the judge even though X2 accepts it. This surfaces those nodes
    as allowed-evidence facts (``claim_text`` carries the figure) for the X1D judge ONLY —
    it does not change selection, display, the X2 allowed-fact scope, or generation.
    """
    nodes = _ibm_metric_outcome_nodes()
    out: list[dict[str, Any]] = []
    for mid in PROMOTABLE_METRIC_OUTCOME_IDS:
        node = nodes.get(mid) or {}
        if section_id not in (node.get("section_eligibility") or []):
            continue
        metric_text = str(node.get("metric") or "").strip()
        low = metric_text.lower()
        if any(f in low for f in FORBIDDEN_METRIC_SUBSTRINGS):
            continue
        claim = str(node.get("claim_text") or metric_text).strip()
        if not claim:
            continue
        out.append(
            {
                "fact_id": mid,
                "kind": "approved_metric_outcome",
                "claim_text": claim,
                "metric_raw": metric_text,
                "has_metric": True,
                "metric_outcome_ids": [mid],
                "metric_outcome_id": mid,
                "surface_tokens": list(node.get("surface_tokens") or []),
                "approval_status": str(node.get("approval_status") or "APPROVED_GRAPH_SSOT"),
                "bundle_bindings": list(node.get("bundle_bindings") or []),
            }
        )
    return out

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
    """Return graph-native metric outcome IDs linked to this bundle."""
    return [str(x) for x in (bundle.get("linked_metric_outcome_ids") or []) if str(x).strip()]


def _metric_label(metric_id: str) -> str:
    node = _ibm_metric_outcome_nodes().get(metric_id) or {}
    label = str(node.get("metric") or "").strip()
    return f"{metric_id} | {label}" if label else metric_id


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
                "AWS",
                "microservices",
                "cloud-native",
                "DevSecOps",
                "CI/CD",
                "HPC",
                "BI",
                "data models",
                "decision support",
                "reference architecture",
                "accelerator",
                "pre-sales",
                "offering",
                "metadata",
                "audit",
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
                "time_window": IBM_TIME_WINDOW,
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
                "graph_bundle_story": {
                    "claim_action": bundle.get("claim_action"),
                    "claim_scope": bundle.get("claim_scope"),
                    "claim_outcome": bundle.get("claim_outcome"),
                },
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
    from apps_rg.runtime.sections.graph_evidence_contract import metric_derivative_fact_id

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
        header_lines.append(f"- {_metric_label(mid)}")

    header = "\n".join(header_lines)

    if section_id == "ibm_narrative":
        blocks = [_format_narrative_bundle_block(b, skill_index=_skill_rows_by_id()) for b in packet["role_episode_bundles"]]
        out = header + "\n\n" + "\n\n".join(blocks)
        assert_ibm_role_episode_evidence_pack_has_no_forbidden_leaks(out)
        return out

    # ibm_bullets: one block per bul_ibm_* slot bound to primary bundle.
    skill_index = _skill_rows_by_id()
    # Per-slot PLAN FACT stories (W4-residual, plan apps-rg-aig-remaining-lanes-closeout-d4e1f7):
    # the X1D judge grades each bullet against its selected_fact_plan fact's claim_text, but the
    # pack only carried bundle intent + skills vocabulary — the generator literally never saw the
    # story it was graded on (gemini decisive-failed "bullet describes X; source fact says Y" on
    # every run). Surface each slot's plan fact so composition can restate its activity.
    _plan_fact_by_slot: dict[str, dict[str, Any]] = {}
    for _pf in (plan.get("facts") or []):
        if isinstance(_pf, dict):
            _plan_fact_by_slot[str(_pf.get("fact_id") or "").strip()] = _pf
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
            f"  employer: {bundle.get('employer')} | time_window: {IBM_TIME_WINDOW}",
            f"  title: {bundle.get('title')}",
            f"  allowed_source_fact_ids: {list(bundle.get('linked_source_fact_ids') or []) + [slot_id]}",
            f"  allowed_metric_outcome_ids: {[_metric_label(mid) for mid in allowed_metrics] or '(none)'}",
            "  executive_scope_signals:",
        ]
        for sig in bundle.get("executive_scope_signals") or []:
            lines.append(f"    - {sig}")
        lines.append("  architecture_scope_signals:")
        for sig in bundle.get("architecture_scope_signals") or []:
            lines.append(f"    - {sig}")
        lines.append(f"  operating_context: {bundle.get('operating_context')}")
        lines.append(f"  bullet_intent: {bundle.get('bullet_intent')}")
        lines.append("  graph_bundle_story:")
        lines.append(f"    claim_action: {bundle.get('claim_action')}")
        lines.append(f"    claim_scope: {bundle.get('claim_scope')}")
        lines.append(f"    claim_outcome: {bundle.get('claim_outcome')}")
        _slot_fact = _plan_fact_by_slot.get(slot_id) or {}
        _story = str(_slot_fact.get("claim_text") or "").strip()
        if _story:
            lines.append(
                "  slot_fact_story (X1D GRADING ANCHOR — this bullet MUST restate THIS activity; "
                "do not substitute the bundle theme for it. EVERY bullet must ALSO satisfy ALL of: "
                "(1) open with a STRONG executive verb (Led/Directed/Drove/Owned/Architected — never "
                "the ledger's weak verb like 'Conducted'); (2) carry an organizational scale signal "
                "(enterprise/portfolio/cross-functional); (3) name >=1 concrete technology or "
                "mechanism token IN the sentence (e.g. platform, architecture, AWS, BI, "
                "microservices, pipeline, infrastructure) — a bullet with zero named tech fails "
                "the deterministic specificity gate even when the story is faithful):"
            )
            lines.append(f"    activity: {_story[:400]}")
            _mr = str(_slot_fact.get("metric_raw") or "").strip()
            lines.append(f"    approved_metric: {_mr or '(none — qualitative bullet)'}")

        skill_ids = list(bundle.get("graph_skill_node_ids") or [])
        if skill_ids:
            lines.append("  bound_skills (graph authority — vocabulary anchors only):")
            for sid in skill_ids:
                sk = skill_index.get(sid) or {}
                phrases = ", ".join(list(sk.get("allowed_phrases") or [])[:5])
                lines.append(f"    - {sid} | allowed_phrases: {phrases}")
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
        f"  employer: {bundle_record.get('employer')} | time_window: {bundle_record.get('time_window') or IBM_TIME_WINDOW}",
        f"  title: {bundle_record.get('title')}",
        f"  graph_skill_node_ids: {bundle_record.get('graph_skill_node_ids')}",
        f"  linked_source_fact_ids: {bundle_record.get('linked_source_fact_ids')}",
        f"  allowed_metric_outcome_ids: {[_metric_label(str(mid)) for mid in (bundle_record.get('allowed_metric_outcome_ids') or [])]}",
        f"  operating_context: {bundle_record.get('operating_context')}",
        f"  bullet_intent: {bundle_record.get('bullet_intent')}",
        f"  graph_bundle_story: {bundle_record.get('graph_bundle_story')}",
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
            lines.append(f"    - {sid} | allowed_phrases: {phrases}")
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
    "attach_role_episode_bundles_to_proof_pool_metadata",
    "assert_ibm_role_episode_evidence_pack_has_no_forbidden_leaks",
    "assert_ibm_section_may_consume_graph_context",
    "build_ibm_role_episode_section_packet",
    "format_ibm_graph_bullet_evidence_pack",
    "format_ibm_role_episode_evidence_pack",
    "is_flat_skill_only_graph_packet",
    "scan_forbidden_metrics_in_text",
]
