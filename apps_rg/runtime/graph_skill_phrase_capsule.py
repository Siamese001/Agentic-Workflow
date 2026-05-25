"""Skill phrase capsule — lexical guidance only (W2 graph-skills quality plan)."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Sequence

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.fact_inventory.track_weighted_graph_expansion import (
    build_track_weighted_expansion,
    infer_projection_role_family_key,
)
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt

SKILL_PHRASE_CAPSULE_MARKER = "SKILL_PHRASE_CAPSULE_NOT_EVIDENCE"
DEFAULT_MAX_PHRASES = 32


def _phrases_from_skill_row(row: dict[str, Any]) -> list[str]:
    raw = row.get("allowed_phrases") or []
    out = [str(p).strip() for p in raw if str(p).strip()]
    if not out:
        label = str(row.get("label") or "").strip()
        if label:
            out.append(label)
    return out


def collect_capsule_phrases(skill_rows: Sequence[dict[str, Any]], *, max_phrases: int = DEFAULT_MAX_PHRASES) -> list[str]:
    seen: set[str] = set()
    phrases: list[str] = []
    for row in skill_rows:
        if not isinstance(row, dict):
            continue
        for phrase in _phrases_from_skill_row(row):
            key = phrase.lower()
            if key in seen:
                continue
            seen.add(key)
            phrases.append(phrase)
            if len(phrases) >= max_phrases:
                return phrases
    return phrases


def resolve_skill_rows_for_capsule(
    runtime_payload: dict[str, Any],
    *,
    section_id: str,
    repo_root: Path | None = None,
) -> list[dict[str, Any]]:
    """Skill rows for capsule text — from proof metadata or track-weighted graph expansion."""
    meta = runtime_payload.get("proof_pool_metadata") if isinstance(runtime_payload.get("proof_pool_metadata"), dict) else {}
    rows = meta.get("selected_skill_rows")
    if isinstance(rows, list) and rows:
        return [r for r in rows if isinstance(r, dict)]

    root = repo_root or Path(__file__).resolve().parents[2]
    graph = load_augmented_skills_graph(repo_root=root)
    role_family_key = infer_projection_role_family_key(
        target_role=str(runtime_payload.get("target_role") or runtime_payload.get("target_title") or ""),
        jd_text=str(runtime_payload.get("jd_text") or ""),
        briefing_text=str(runtime_payload.get("briefing") or runtime_payload.get("briefing_text") or ""),
    )
    expansion = build_track_weighted_expansion(
        graph=graph,
        role_family_key=role_family_key,
        jd_text=str(runtime_payload.get("jd_text") or ""),
        briefing_text=str(runtime_payload.get("briefing") or runtime_payload.get("briefing_text") or ""),
        repo_root=root,
        min_tracks_with_facts=1,
    )
    from apps_rg.fact_inventory.track_weighted_graph_expansion import _skill_rows_by_id

    rows_by_id = _skill_rows_by_id(graph)
    enriched: list[dict[str, Any]] = []
    seen: set[str] = set()
    for sk in expansion.get("selected_skills") or []:
        if not isinstance(sk, dict):
            continue
        sid = str(sk.get("skill_id") or "")
        if not sid or sid in seen:
            continue
        seen.add(sid)
        row = rows_by_id.get(sid) or {}
        enriched.append(
            {
                "skill_id": sid,
                "label": str((row.get("allowed_phrases") or [""])[0]).strip() if row.get("allowed_phrases") else sid,
                "allowed_phrases": list(row.get("allowed_phrases") or []),
                "fact_id_links": list(row.get("fact_id_links") or []),
            }
        )
    return enriched


def format_skill_phrase_capsule_block(
    *,
    section_id: str,
    phrases: Sequence[str],
) -> str:
    lines = [
        SKILL_PHRASE_CAPSULE_MARKER,
        "LEXICAL GUIDANCE ONLY — not evidence, not allowed_fact_ids, not claim_ledger proof.",
        f"section_id: {section_id}",
        "Use phrasing below only when a claim is already supported by ALLOWED_SOURCE_FACT_IDS / graph facts.",
        "Do not invent skills or metrics from this block alone.",
        "",
        "allowed_phrases (guidance):",
    ]
    if phrases:
        lines.extend(f"  - {p}" for p in phrases)
    else:
        lines.append("  - (none — graph skill rows had no phrases for this section)")
    return "\n".join(lines)


def augment_section_compiled_with_skill_phrase_capsule(
    compiled: SectionCompiledPrompt,
    *,
    runtime_payload: dict[str, Any],
    max_phrases: int = DEFAULT_MAX_PHRASES,
) -> SectionCompiledPrompt:
    """Append skill phrase capsule to the last compiled message."""
    rows = resolve_skill_rows_for_capsule(runtime_payload, section_id=compiled.section_id)
    block = format_skill_phrase_capsule_block(
        section_id=compiled.section_id,
        phrases=collect_capsule_phrases(rows, max_phrases=max_phrases),
    )
    art = compiled.artifact
    msgs = [dict(m) for m in art.messages]
    if not msgs:
        return compiled
    last = msgs[-1]
    prev = str(last.get("content") or "").rstrip()
    last["content"] = f"{prev}\n\n{block}" if prev else block
    msgs[-1] = last
    new_art = replace(art, messages=msgs)
    return SectionCompiledPrompt(
        section_id=compiled.section_id,
        apps_rg_prompt_template_ref=compiled.apps_rg_prompt_template_ref,
        artifact=new_art,
    )


__all__ = [
    "DEFAULT_MAX_PHRASES",
    "SKILL_PHRASE_CAPSULE_MARKER",
    "augment_section_compiled_with_skill_phrase_capsule",
    "collect_capsule_phrases",
    "format_skill_phrase_capsule_block",
    "resolve_skill_rows_for_capsule",
]
