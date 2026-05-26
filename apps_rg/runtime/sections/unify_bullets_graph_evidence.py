"""Graph-bound evidence pack for unify_bullets Qwen compose prompts (apps_rg only)."""
from __future__ import annotations

from typing import Any, Sequence

from apps_rg.runtime.graph_skill_phrase_capsule import resolve_skill_rows_for_capsule
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS

GRAPH_BULLET_EVIDENCE_PACK_MARKER = "GRAPH_BULLET_EVIDENCE_PACK"

TRACK_RANKED_SELECTION_METHOD = "augmented_skills_graph_unify_bullets_track_ranked"

# Ledger facts that must appear in the six-pack when present (X2 metric anchors on 004/006 slots).
_UNIFY_METRIC_LEDGER_IDS: tuple[str, ...] = (
    "fact_engineering_platform_004",
    "fact_engineering_platform_006",
)

# Legacy base-resume six-pack in sorted candidate_fact_id order (forbidden allocation pattern).
LEGACY_SIX_PACK_LEDGER_ORDER: tuple[str, ...] = tuple(
    f"fact_engineering_platform_{i:03d}" for i in range(1, 7)
)

FORBIDDEN_C0_PROMPT_SUBSTRINGS: tuple[str, ...] = (
    "CANONICAL UNIFY FACTS",
    "rewrite from these",
    "archive_reference_only",
    "| theme:",
    "Agentic AI platform architecture — one outcome spine",
    "Dependency graph intelligence",
    "Governed runtime reliability",
)

FORBIDDEN_SELECTION_METHOD_MARKERS: tuple[str, ...] = (
    "company_hint",
    "hydrate_unify",
    "canonical_json_all_unify",
)

# Metric-anchor ledger rows must land on these canonical bullet slots (X2 ownership).
UNIFY_LEDGER_METRIC_ANCHOR_SLOTS: dict[str, str] = {
    "fact_engineering_platform_004": "bul_unify_004",
    "fact_engineering_platform_006": "bul_unify_006",
}


def max_consecutive_word_overlap(left: str, right: str) -> int:
    """Longest run of consecutive shared words (case-insensitive) between two strings."""
    import re

    lw = re.findall(r"[a-z0-9']+", str(left or "").lower())
    rw = re.findall(r"[a-z0-9']+", str(right or "").lower())
    if not lw or not rw:
        return 0
    best = 0
    for i in range(len(lw)):
        for j in range(len(rw)):
            n = 0
            while i + n < len(lw) and j + n < len(rw) and lw[i + n] == rw[j + n]:
                n += 1
            if n > best:
                best = n
    return best


def assign_unify_metric_anchor_slots(facts: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reorder plan facts so metric ledger rows occupy bul_unify_004 / bul_unify_006."""
    rows = [dict(f) for f in facts if isinstance(f, dict)]
    if not rows:
        return []

    anchored: dict[str, dict[str, Any]] = {}
    remainder: list[dict[str, Any]] = []
    for fact in rows:
        lid = str(
            fact.get("ledger_candidate_fact_id")
            or fact.get("candidate_fact_id")
            or fact.get("fact_id")
            or ""
        ).strip()
        slot = UNIFY_LEDGER_METRIC_ANCHOR_SLOTS.get(lid)
        if slot:
            anchored[slot] = fact
        else:
            remainder.append(fact)

    out: list[dict[str, Any] | None] = [None] * len(UNIFY_BULLET_IDS)
    for slot, fact in anchored.items():
        if slot in UNIFY_BULLET_IDS:
            out[UNIFY_BULLET_IDS.index(slot)] = fact
    ri = 0
    for i, slot in enumerate(UNIFY_BULLET_IDS):
        if out[i] is not None:
            continue
        if ri < len(remainder):
            out[i] = remainder[ri]
            ri += 1
    placed = [f for f in out if f is not None]
    return placed[: len(UNIFY_BULLET_IDS)]


def is_legacy_six_pack_ledger_order(ledger_ids: Sequence[str]) -> bool:
    """True when allocation is exactly the old sorted engineering_platform_001..006 pack."""
    normalized = [str(x).strip() for x in ledger_ids if str(x).strip()]
    return normalized == list(LEGACY_SIX_PACK_LEDGER_ORDER)


def is_allowed_unify_selection_method(method: str) -> bool:
    m = str(method or "").strip()
    if not m:
        return False
    if any(marker in m for marker in FORBIDDEN_SELECTION_METHOD_MARKERS):
        return False
    if m == TRACK_RANKED_SELECTION_METHOD:
        return True
    return m.startswith("augmented_skills_graph_unify_bullets")


def assert_c0_pack_has_no_forbidden_template_leaks(pack_text: str) -> None:
    blob = str(pack_text or "")
    hits = [s for s in FORBIDDEN_C0_PROMPT_SUBSTRINGS if s in blob]
    if hits:
        raise ValueError(f"GRAPH_BULLET_EVIDENCE_PACK contains forbidden template leakage: {hits}")


def _ledger_fact_id(fact: dict[str, Any]) -> str:
    for key in ("ledger_candidate_fact_id", "candidate_fact_id"):
        val = str(fact.get(key) or "").strip()
        if val:
            return val
    fid = str(fact.get("fact_id") or "").strip()
    if fid.startswith("bul_unify_") and "_metric_" not in fid:
        return fid
    return ""


def _skills_for_ledger_ids(
    skill_rows: Sequence[dict[str, Any]],
    ledger_ids: set[str],
    *,
    max_skills: int = 8,
) -> list[dict[str, Any]]:
    if not ledger_ids:
        return []
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in skill_rows:
        if not isinstance(row, dict):
            continue
        links = {str(x).strip() for x in (row.get("fact_id_links") or []) if str(x).strip()}
        if not links.intersection(ledger_ids):
            continue
        sid = str(row.get("skill_id") or row.get("node_id") or "").strip()
        if not sid or sid in seen:
            continue
        seen.add(sid)
        phrases = row.get("allowed_phrases") or []
        phrase_list = [str(p).strip() for p in phrases if str(p).strip()]
        label = str(row.get("label") or "").strip()
        out.append(
            {
                "skill_id": sid,
                "label": label,
                "allowed_phrases": phrase_list,
            }
        )
        if len(out) >= max_skills:
            break
    return out


def _format_c03_neighbor_hints(pp_meta: dict[str, Any], *, max_refs: int = 8) -> str:
    c03 = pp_meta.get("c03_graphrag_bound")
    if not isinstance(c03, dict):
        return ""
    refs = list(c03.get("graph_expansion_refs") or [])[:max_refs]
    if not refs:
        return ""
    lines = ["C0.3_GRAPH_NEIGHBOR_HINTS (context only — not extra proof IDs):"]
    lines.extend(f"  - {r}" for r in refs)
    return "\n".join(lines)


def _jd_framing_excerpt(runtime_payload: dict[str, Any], *, max_chars: int = 200) -> str:
    jd = str(runtime_payload.get("jd_text") or "").strip()
    briefing = str(runtime_payload.get("briefing") or runtime_payload.get("briefing_text") or "").strip()
    bits = [b for b in (jd[:max_chars], briefing[:max_chars]) if b]
    return " | ".join(bits) if bits else "(no JD/briefing excerpt)"


def format_unify_graph_bullet_evidence_pack(
    runtime_payload: dict[str, Any],
    *,
    allowed_block: str,
    unify_id_hygiene: str,
) -> str:
    """C0 body: graph skills + fact atoms per bul_unify_* slot — no legacy theme map or claim_text."""
    plan = runtime_payload.get("selected_fact_plan") or {}
    facts = list(plan.get("facts") or [])
    by_slot: dict[str, dict[str, Any]] = {}
    for fact in facts:
        if not isinstance(fact, dict):
            continue
        fid = str(fact.get("fact_id") or "").strip()
        if fid in UNIFY_BULLET_IDS:
            by_slot[fid] = fact

    pp_meta = runtime_payload.get("proof_pool_metadata") if isinstance(runtime_payload.get("proof_pool_metadata"), dict) else {}
    skill_rows = resolve_skill_rows_for_capsule(runtime_payload, section_id="unify_bullets")
    selection_method = str(plan.get("selection_method") or pp_meta.get("selection_method") or "")

    header = (
        f"{allowed_block}{unify_id_hygiene}\n"
        f"{GRAPH_BULLET_EVIDENCE_PACK_MARKER} "
        "(proof substrate — compose six bullets from bound_skills + proof_atoms only):\n"
        f"- selection_method: {selection_method or 'augmented_skills_graph'}\n"
        "- Do NOT use legacy base-resume bullet wording or fixed theme templates.\n"
        "- No claim_text / archive prose in this pack — synthesize executive lines from skills + atoms.\n"
        "- skill_id alone is not proof; every claim needs allowed_source_fact_ids for that slot.\n"
        "- JD/briefing (U0) choose emphasis only; do not invent facts from JD.\n"
    )

    slot_blocks: list[str] = []
    for slot_id in UNIFY_BULLET_IDS:
        fact = by_slot.get(slot_id) or {}
        ledger_id = _ledger_fact_id(fact)
        ledger_ids = {ledger_id} if ledger_id else set()
        skills = _skills_for_ledger_ids(skill_rows, ledger_ids)
        allowed_ids = [slot_id]
        mr = str(fact.get("metric_raw") or "").strip()
        if mr:
            from apps_rg.runtime.sections.selected_role_fact_set import metric_derivative_fact_id

            allowed_ids.append(metric_derivative_fact_id(slot_id, mr))

        lines = [
            f"{slot_id} | compose_one_bullet_from:",
            f"  allowed_source_fact_ids: {allowed_ids}",
        ]
        if skills:
            lines.append("  bound_skills (graph authority — primary vocabulary):")
            for sk in skills:
                sid = sk["skill_id"]
                phrases = sk.get("allowed_phrases") or []
                phrase_s = ", ".join(phrases[:6]) if phrases else str(sk.get("label") or sid)
                lines.append(f"    - {sid} | allowed_phrases: {phrase_s}")
        else:
            lines.append("  bound_skills: (none linked — omit or use proof_atoms tags only)")

        lines.append("  proof_atoms (metrics/tags only — no prose):")
        if ledger_id:
            tags: list[str] = []
            tech = fact.get("technologies")
            if isinstance(tech, list):
                tags.extend(str(t) for t in tech if str(t).strip())
            rf = fact.get("role_families_supported")
            if isinstance(rf, list):
                tags.extend(str(t) for t in rf if str(t).strip())
            domain = str(fact.get("domain") or "").strip()
            if domain:
                tags.append(domain)
            tag_s = ", ".join(tags) if tags else "(none)"
            metric_s = mr or "(none)"
            lines.append(f"    - ledger_fact_id: {ledger_id} | tags: {tag_s} | locked_metrics: {metric_s}")
        else:
            lines.append("    - (no ledger fact mapped for this slot)")

        slot_blocks.append("\n".join(lines))

    c03_block = _format_c03_neighbor_hints(pp_meta)
    parts = [header, "\n\n".join(slot_blocks)]
    if c03_block:
        parts.append(c03_block)
    out = "\n\n".join(parts)
    assert_c0_pack_has_no_forbidden_template_leaks(out)
    return out


def append_unify_path_framing_to_messages(
    messages: list[dict[str, Any]],
    *,
    path_index: int,
    temperature: float,
    runtime_payload: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Per-path JD-driven framing — not the legacy six-theme template."""
    if not messages:
        return messages
    payload = runtime_payload if isinstance(runtime_payload, dict) else {}
    jd_excerpt = _jd_framing_excerpt(payload)
    suffix = (
        f"\n\nPATH_FRAMING (path_index={path_index}, temperature={temperature:.2f}):\n"
        f"Targeting excerpt (emphasis only): {jd_excerpt}\n"
        "Vary executive framing and verb choice across paths; each path must produce six distinct "
        "bullets grounded in GRAPH_BULLET_EVIDENCE_PACK skills/atoms — not a reorder of the same "
        "six legacy resume themes.\n"
    )
    out = [dict(m) for m in messages]
    last = out[-1]
    prev = str(last.get("content") or "").rstrip()
    out[-1] = {**last, "content": f"{prev}{suffix}" if prev else suffix.strip()}
    return out


__all__ = [
    "FORBIDDEN_C0_PROMPT_SUBSTRINGS",
    "FORBIDDEN_SELECTION_METHOD_MARKERS",
    "GRAPH_BULLET_EVIDENCE_PACK_MARKER",
    "LEGACY_SIX_PACK_LEDGER_ORDER",
    "TRACK_RANKED_SELECTION_METHOD",
    "UNIFY_LEDGER_METRIC_ANCHOR_SLOTS",
    "_UNIFY_METRIC_LEDGER_IDS",
    "append_unify_path_framing_to_messages",
    "assign_unify_metric_anchor_slots",
    "assert_c0_pack_has_no_forbidden_template_leaks",
    "format_unify_graph_bullet_evidence_pack",
    "is_allowed_unify_selection_method",
    "is_legacy_six_pack_ledger_order",
    "max_consecutive_word_overlap",
]
