"""GRAPH_TARGETING_CAPSULE — non-proof PA theming slice for executive_summary."""
from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.c0.c03_allowlist_coherence import GRAPH_NON_PROOF_STAMP, stamp_graph_non_proof

CAPSULE_MAX_SKILLS = 8
CAPSULE_MAX_LABEL_CHARS = 120
CAPSULE_MAX_TOTAL_CHARS = 960

NON_PROOF_BANNER = (
    "GRAPH_TARGETING_CAPSULE — graph_context_routing_support_not_claim_proof — "
    "theming/vocabulary only; NOT claim support; do not cite as evidence."
)

_FORBIDDEN_CAPSULE_PATTERNS = (
    re.compile(r"\$\s*\d"),
    re.compile(r"\b\d{4}\b"),
    re.compile(r"\b\d+%\b"),
    re.compile(r"\b(?:revenue|margin|ARR|MRR)\b", re.I),
    re.compile(r"\b(?:Inc\.|LLC|Corp\.)\b", re.I),
)


def _skill_label(skill_id: str, track_expansion: dict[str, Any]) -> str:
    for row in track_expansion.get("selected_skills") or []:
        if isinstance(row, dict) and str(row.get("skill_id") or "") == skill_id:
            pillar = str(row.get("pillar") or "").replace("pillar_", "").replace("_", " ").strip()
            track = str(row.get("career_track") or "").replace("career_track_", "").replace("_", " ")
            base = skill_id.replace("skill_", "").replace("_", " ")
            label = f"{base} ({pillar or track})".strip()
            return label[:CAPSULE_MAX_LABEL_CHARS]
    return skill_id.replace("skill_", "").replace("_", " ")[:CAPSULE_MAX_LABEL_CHARS]


def _skill_score(skill_id: str, track_expansion: dict[str, Any]) -> float:
    best = 0.0
    for row in track_expansion.get("selected_skills") or []:
        if isinstance(row, dict) and str(row.get("skill_id") or "") == skill_id:
            try:
                best = max(best, float(row.get("weight") or 0.0))
            except (TypeError, ValueError):  # guardian: allow-silent-swallow -- bounded score parse
                pass
    return best


def capsule_contains_forbidden_patterns(text: str) -> bool:
    return any(p.search(text) for p in _FORBIDDEN_CAPSULE_PATTERNS)


def build_graph_targeting_capsule(
    track_expansion: dict[str, Any],
    *,
    role_family_key: str,
    allowed_fact_ids: set[str] | None = None,
    max_skills: int = CAPSULE_MAX_SKILLS,
) -> dict[str, Any]:
    """Top-N track-weighted skills as non-proof theming capsule."""
    allowed = {str(x).strip() for x in (allowed_fact_ids or set()) if str(x).strip()}
    skill_ids = sorted(
        {str(x).strip() for x in (track_expansion.get("c03_selected_skill_ids") or []) if str(x).strip()}
    )
    ranked = sorted(skill_ids, key=lambda sid: (-_skill_score(sid, track_expansion), sid))
    entries: list[dict[str, str]] = []
    total_chars = 0
    for sid in ranked:
        if len(entries) >= max_skills:
            break
        label = _skill_label(sid, track_expansion)
        if capsule_contains_forbidden_patterns(label):
            continue
        if total_chars + len(label) > CAPSULE_MAX_TOTAL_CHARS:
            break
        entries.append({"skill_id": sid, "label": label})
        total_chars += len(label)

    lines = [e["label"] for e in entries]
    body = "; ".join(lines)
    if capsule_contains_forbidden_patterns(body) and not allowed:
        body = "; ".join(e["skill_id"].replace("skill_", "").replace("_", " ") for e in entries)

    capsule = stamp_graph_non_proof(
        {
            "schema": "graph_targeting_capsule_v1",
            "role_family_key": role_family_key,
            "skill_entries": entries,
            "skill_ids": [e["skill_id"] for e in entries],
            "capsule_text": body[:CAPSULE_MAX_TOTAL_CHARS],
            "capsule_char_count": min(len(body), CAPSULE_MAX_TOTAL_CHARS),
            "max_skills": max_skills,
            "max_label_chars": CAPSULE_MAX_LABEL_CHARS,
            "max_total_chars": CAPSULE_MAX_TOTAL_CHARS,
            "non_proof_banner": NON_PROOF_BANNER,
            **GRAPH_NON_PROOF_STAMP,
        }
    )
    if allowed:
        capsule["allowed_fact_ids_bound"] = sorted(allowed)
    return capsule


def canonical_graph_targeting_capsule_digest(capsule: dict[str, Any] | None) -> str:
    """Stable digest for parity binding (PA + judge must share the same capsule document)."""
    import hashlib
    import json

    if not isinstance(capsule, dict) or not capsule:
        return hashlib.sha256(b"").hexdigest()
    body = json.dumps(
        {
            "role_family_key": str(capsule.get("role_family_key") or ""),
            "skill_ids": sorted(str(x) for x in (capsule.get("skill_ids") or []) if str(x).strip()),
            "capsule_text": str(capsule.get("capsule_text") or ""),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def format_graph_targeting_capsule_for_pa(capsule: dict[str, Any]) -> str:
    text = str(capsule.get("capsule_text") or "").strip()
    skills = capsule.get("skill_entries") or []
    lines = [
        NON_PROOF_BANNER,
        "GRAPH_TARGETING_CAPSULE (theming only — not evidence):",
    ]
    for entry in skills:
        if isinstance(entry, dict):
            lines.append(f"- {entry.get('label') or entry.get('skill_id')}")
    if text and not skills:
        lines.append(f"- {text}")
    return "\n".join(lines)


__all__ = [
    "CAPSULE_MAX_LABEL_CHARS",
    "CAPSULE_MAX_SKILLS",
    "CAPSULE_MAX_TOTAL_CHARS",
    "NON_PROOF_BANNER",
    "build_graph_targeting_capsule",
    "canonical_graph_targeting_capsule_digest",
    "capsule_contains_forbidden_patterns",
    "format_graph_targeting_capsule_for_pa",
]
