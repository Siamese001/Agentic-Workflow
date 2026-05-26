"""Graph-bound evidence pack for unify_bullets Qwen compose prompts (apps_rg only)."""
from __future__ import annotations

from typing import Any, Sequence

from apps_rg.runtime.graph_skill_phrase_capsule import resolve_skill_rows_for_capsule
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS

GRAPH_BULLET_EVIDENCE_PACK_MARKER = "GRAPH_BULLET_EVIDENCE_PACK"

UNIFY_SLOT_THEMES: dict[str, str] = {
    "bul_unify_001": (
        "Agentic AI platform architecture — one outcome spine (regulated enterprise platform delivery)"
    ),
    "bul_unify_002": "Dependency graph intelligence",
    "bul_unify_003": "Governed runtime reliability",
    "bul_unify_004": "AI systems lifecycle standardization (metric anchor: six months to three weeks)",
    "bul_unify_005": "Distributed ecosystem engineering",
    "bul_unify_006": (
        "Platform commercialization and engineering leadership "
        "(protected metrics: $22M IP-led revenue, 20% gross margin, 8 to 28 specialists)"
    ),
}

_PATH_FRAMING_ANGLES: tuple[str, ...] = (
    "Foreground regulated enterprise platform delivery and governed agentic outcomes; "
    "use JD IT-strategy themes for verb choice only.",
    "Foreground dependency-graph intelligence, legacy analysis, and architecture visibility; "
    "stay within proof atoms for this path.",
    "Foreground runtime reliability, evaluation gates, retrieval quality, and operational controls; "
    "avoid duplicating mechanism stacks from other paths.",
    "Foreground lab-to-production lifecycle and cycle-time outcomes; preserve bul_unify_004 metric anchor if applicable.",
    "Foreground cloud, data platform, and distributed engineering patterns supported by linked facts.",
    "Foreground commercialization, engineering leadership scale, and business outcomes; "
    "preserve bul_unify_006 protected metrics when evidenced.",
)


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


def _archive_reference_snippet(claim_text: str, *, max_len: int = 100) -> str:
    text = " ".join(str(claim_text or "").split())
    if not text:
        return "(none)"
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


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


def format_unify_graph_bullet_evidence_pack(
    runtime_payload: dict[str, Any],
    *,
    allowed_block: str,
    unify_id_hygiene: str,
) -> str:
    """C0 body: graph skills + fact atoms per bul_unify_* slot (no copy-source claim_text)."""
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

    header = (
        f"{allowed_block}{unify_id_hygiene}\n"
        f"{GRAPH_BULLET_EVIDENCE_PACK_MARKER} "
        "(proof substrate — compose bullets from this pack; do not copy verbatim):\n"
        "- claim_text fields below are ARCHIVE_REFERENCE_ONLY (wording hint), not bullet_text source.\n"
        "- Authenticity: bind material claims to allowed_source_fact_ids; prefer bound_skills allowed_phrases "
        "when supported by linked ledger facts.\n"
        "- skill_id alone is not proof; every claim needs fact_id backing.\n"
    )

    slot_blocks: list[str] = []
    for slot_id in UNIFY_BULLET_IDS:
        fact = by_slot.get(slot_id) or {}
        ledger_id = _ledger_fact_id(fact)
        ledger_ids = {ledger_id} if ledger_id else set()
        skills = _skills_for_ledger_ids(skill_rows, ledger_ids)
        theme = UNIFY_SLOT_THEMES.get(slot_id, "Unify employment theme")
        allowed_ids = [slot_id]
        mr = str(fact.get("metric_raw") or "").strip()
        if mr:
            from apps_rg.runtime.sections.selected_role_fact_set import metric_derivative_fact_id

            allowed_ids.append(metric_derivative_fact_id(slot_id, mr))

        lines = [
            f"{slot_id} | theme: {theme}",
            f"  allowed_source_fact_ids: {allowed_ids}",
        ]
        if skills:
            lines.append("  bound_skills (C0.3 graph — vocabulary when fact-linked):")
            for sk in skills:
                sid = sk["skill_id"]
                phrases = sk.get("allowed_phrases") or []
                phrase_s = ", ".join(phrases[:4]) if phrases else str(sk.get("label") or sid)
                lines.append(f"    - {sid} | allowed_phrases: {phrase_s}")
        else:
            lines.append("  bound_skills: (none linked — use proof_atoms only)")

        lines.append("  proof_atoms:")
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
            tag_s = ", ".join(tags) if tags else "(tags not listed)"
            metric_s = mr or "(none)"
            snippet = _archive_reference_snippet(str(fact.get("claim_text") or ""))
            lines.append(f"    - {ledger_id} | tags: {tag_s} | locked_metrics: {metric_s}")
            lines.append(f"      | archive_reference_only: \"{snippet}\"")
        else:
            lines.append("    - (no ledger fact mapped for this slot)")

        slot_blocks.append("\n".join(lines))

    c03_block = _format_c03_neighbor_hints(pp_meta)
    parts = [header, "\n\n".join(slot_blocks)]
    if c03_block:
        parts.append(c03_block)
    return "\n\n".join(parts)


def append_unify_path_framing_to_messages(
    messages: list[dict[str, Any]],
    *,
    path_index: int,
    temperature: float,
) -> list[dict[str, Any]]:
    """Append per-path targeting angle so SC paths are not temperature-only clones."""
    if not messages:
        return messages
    angle = _PATH_FRAMING_ANGLES[path_index % len(_PATH_FRAMING_ANGLES)]
    suffix = (
        f"\n\nPATH_FRAMING (path_index={path_index}, temperature={temperature:.2f}):\n"
        f"{angle}\n"
        "Produce a semantically distinct six-bullet set for this path — not a synonym swap of other paths."
    )
    out = [dict(m) for m in messages]
    last = out[-1]
    prev = str(last.get("content") or "").rstrip()
    out[-1] = {**last, "content": f"{prev}{suffix}" if prev else suffix.strip()}
    return out


__all__ = [
    "GRAPH_BULLET_EVIDENCE_PACK_MARKER",
    "UNIFY_SLOT_THEMES",
    "append_unify_path_framing_to_messages",
    "format_unify_graph_bullet_evidence_pack",
]
