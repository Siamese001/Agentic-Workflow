"""apps_rg augmented_skills_graph -> apps_qna ExperienceLibrary adapter.

The base resume (``apps_shared/data/master_resume*.json``) is now IDENTITY-ONLY:
it carries no bullets/context/competencies/executive_summary. The single source
of truth for experience facts/claims/metrics is the apps_rg
``augmented_skills_graph`` (built from
``apps_rg/fact_inventory/master_skills_arsenal_ledger.json``).

This bridge mirrors the established cross-app consumption pattern in
``apps_lic/integrations/apps_rg_proof_bridge.py``: it imports
``from apps_rg.fact_inventory.augmented_skills_graph import
load_augmented_skills_graph`` and projects the graph's approved/active skill
rows onto the apps_qna spine types. It does NOT import apps_lic — both apps
consume the SHARED graph SSOT directly.

Projection (per eligible/active skill row):
    ExperiencePoint
        title                = allowed_phrases[0] (skill name) or humanized skill_id
        one_liner            = best source snippet (metric-bearing preferred)
        technical_depth_tags = [pillar, subpillar, role-family tags...]

Competency areas:
    group eligible skills by pillar name -> [{"area": pillar, "skills": "a, b, c"}]

Executive summary:
    a short, metric-grounded synthesis line drawn from the top pillars (by
    eligible-skill count); only graph-derived metric phrases are used.

Fail-soft by construction: if apps_rg is unavailable (import error or missing
artifact) every function returns an empty projection rather than raising, so
apps_qna degrades gracefully (no experience facts) instead of crashing.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

from apps_qna.types.qna_types import ExperienceLibrary, ExperiencePoint

# A skill row anchors an external claim only when activated (not blocked/draft).
_ACTIVE_ACTIVATION = frozenset({"ACTIVE", "ACTIVE_CONFIRMED"})

# Metric detector (mirrors apps_lic proof bridge): $amounts, %, k/m/b magnitude.
_METRIC_RE = re.compile(
    r"\$\s?\d|\d+(?:\.\d+)?\s?%|\b\d+(?:\.\d+)?\s?(?:m|mm|k|b|bn)\b",
    re.IGNORECASE,
)

# Cap on competency areas / executive-summary pillars so downstream cards are
# not flooded. The graph has ~25 eligible pillars; surface the densest.
_MAX_COMPETENCY_AREAS = 16
_EXEC_SUMMARY_TOP_PILLARS = 4


def _has_metric(text: Any) -> bool:
    return bool(_METRIC_RE.search(str(text or "")))


def _humanize_skill_id(skill_id: str) -> str:
    """Fallback title from a skill_id when allowed_phrases is empty."""
    raw = str(skill_id or "").strip()
    if raw.startswith("skill_"):
        raw = raw[len("skill_") :]
    return raw.replace("_", " ").strip().title() or "Skill"


def _clean_str_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [str(v).strip() for v in value if str(v).strip()]


def _is_active(row: dict[str, Any]) -> bool:
    return str(row.get("activation_status") or "").strip().upper() in _ACTIVE_ACTIVATION


@lru_cache(maxsize=1)
def _load_graph() -> dict[str, Any] | None:
    """Load the shared augmented_skills_graph once (cached; fail-soft)."""
    try:
        from apps_rg.fact_inventory.augmented_skills_graph import (  # noqa: PLC0415
            load_augmented_skills_graph,
        )

        return load_augmented_skills_graph()
    except Exception:  # guardian: allow-broad-exception -- shared apps_rg SSOT is optional; any load failure degrades apps_qna to an empty (graph-unavailable) projection rather than crashing the wizard/builder
        return None


def _eligible_active_rows(graph: dict[str, Any]) -> list[dict[str, Any]]:
    """Skill rows eligible for external claim AND activated.

    Eligibility uses the apps_rg ledger gate (the same predicate apps_rg's own
    competency projection uses) so apps_qna never claims a skill apps_rg would
    block. Activation filters out DRAFT rows.
    """
    try:
        from apps_rg.fact_inventory.master_skills_arsenal_ledger import (  # noqa: PLC0415
            skill_row_eligible_for_external_claim,
        )
    except Exception:  # guardian: allow-broad-exception -- if the eligibility gate is unavailable, fall back to activation-only filtering rather than crashing
        skill_row_eligible_for_external_claim = None  # type: ignore[assignment]

    rows: list[dict[str, Any]] = []
    for row in graph.get("skill_rows") or []:
        if not isinstance(row, dict):
            continue
        if not str(row.get("skill_id") or "").strip():
            continue
        if not _is_active(row):
            continue
        if skill_row_eligible_for_external_claim is not None:
            try:
                if not skill_row_eligible_for_external_claim(row):
                    continue
            except Exception:  # guardian: allow-broad-exception -- a malformed row must not abort the whole projection
                continue
        rows.append(row)
    return rows


def _pillar_name_map(graph: dict[str, Any]) -> dict[str, str]:
    """pillar_id -> human pillar name (falls back to the id when unnamed)."""
    out: dict[str, str] = {}
    for pillar in graph.get("pillars") or []:
        if not isinstance(pillar, dict):
            continue
        pid = str(pillar.get("pillar_id") or pillar.get("id") or "").strip()
        if not pid:
            continue
        out[pid] = str(pillar.get("name") or pid).strip() or pid
    return out


def _skill_name(row: dict[str, Any]) -> str:
    phrases = _clean_str_list(row.get("allowed_phrases"))
    if phrases:
        return phrases[0]
    return _humanize_skill_id(str(row.get("skill_id") or ""))


def _best_snippet(row: dict[str, Any]) -> str:
    """Pick the most descriptive source snippet (metric-bearing preferred).

    The snippet IS the achievement text — the only narrative the graph permits
    apps_qna to surface (skill_id is not proof; metrics come only from snippets
    that carry them). Falls back to the skill name when no snippet exists.
    """
    snippets = _clean_str_list(row.get("source_snippets"))
    if not snippets:
        return _skill_name(row)
    metric_snips = [s for s in snippets if _has_metric(s)]
    pool = metric_snips or snippets
    # Prefer the longest (most descriptive) candidate in the chosen pool.
    return max(pool, key=len)


def _role_family_tags(row: dict[str, Any]) -> list[str]:
    """Role-family weight keys for a row, ordered by weight descending."""
    weights = row.get("role_family_weights")
    if not isinstance(weights, dict):
        return []
    scored = [
        (str(k), float(v))
        for k, v in weights.items()
        if isinstance(v, (int, float)) and not isinstance(v, bool)
    ]
    scored.sort(key=lambda kv: (-kv[1], kv[0]))
    return [k for k, _w in scored]


def _depth_tags(row: dict[str, Any], pillar_name_map: dict[str, str]) -> list[str]:
    """technical_depth_tags = [pillar name, subpillar, role-family tags...]."""
    tags: list[str] = []
    pid = str(row.get("pillar") or "").strip()
    if pid:
        tags.append(pillar_name_map.get(pid, pid))
    sub = str(row.get("subpillar") or "").strip()
    if sub:
        tags.append(sub)
    tags.extend(_role_family_tags(row))
    # De-dup, preserve order.
    return list(dict.fromkeys(t for t in tags if t))


def _point_from_row(
    row: dict[str, Any],
    pillar_name_map: dict[str, str],
) -> ExperiencePoint:
    return ExperiencePoint(
        title=_skill_name(row),
        one_liner=_best_snippet(row),
        technical_depth_tags=_depth_tags(row, pillar_name_map),
    )


# ----------------------------------------------------------------------------
# Public surface
# ----------------------------------------------------------------------------


def experience_library_from_graph() -> ExperienceLibrary:
    """Project the augmented_skills_graph onto an ExperienceLibrary.

    One ExperiencePoint per eligible/active skill row. StoryBank and RCA bank
    are returned empty — STAR synthesis (``star_synthesis.py``) fills them from
    these points. Returns an EMPTY library when the shared graph is unavailable.
    """
    graph = _load_graph()
    if graph is None:
        return ExperienceLibrary()
    pillar_name_map = _pillar_name_map(graph)
    points = [
        _point_from_row(row, pillar_name_map)
        for row in _eligible_active_rows(graph)
    ]
    return ExperienceLibrary(points=points)


def competency_areas_from_graph() -> list[dict]:
    """Group eligible/active skills by pillar -> [{"area", "skills"}].

    ``skills`` is a comma-joined, de-duplicated list of the pillar's skill
    names (allowed_phrases[0]). Areas are ordered by eligible-skill density
    (densest first) and capped. Returns ``[]`` when the graph is unavailable.
    """
    graph = _load_graph()
    if graph is None:
        return []
    pillar_name_map = _pillar_name_map(graph)
    by_area: dict[str, list[str]] = {}
    for row in _eligible_active_rows(graph):
        pid = str(row.get("pillar") or "").strip()
        area = pillar_name_map.get(pid, pid) if pid else "General"
        by_area.setdefault(area, [])
        name = _skill_name(row)
        if name not in by_area[area]:
            by_area[area].append(name)
    ordered = sorted(by_area.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    return [
        {"area": area, "skills": ", ".join(skills)}
        for area, skills in ordered[:_MAX_COMPETENCY_AREAS]
        if skills
    ]


def executive_summary_from_graph() -> str | None:
    """Synthesize a short, metric-grounded executive-summary line from the graph.

    Drawn from the top pillars (by eligible-skill count). Only graph-derived
    metric phrases (from pillar ``allowed_phrases``/``archive_snippets`` and
    skill snippets that carry numbers) are admitted. Returns ``None`` when the
    graph is unavailable or yields no eligible skills.
    """
    graph = _load_graph()
    if graph is None:
        return None
    rows = _eligible_active_rows(graph)
    if not rows:
        return None
    pillar_name_map = _pillar_name_map(graph)

    # Rank pillars by eligible-skill density.
    pillar_counts: dict[str, int] = {}
    for row in rows:
        pid = str(row.get("pillar") or "").strip()
        if pid:
            pillar_counts[pid] = pillar_counts.get(pid, 0) + 1
    top_pids = [
        pid
        for pid, _n in sorted(
            pillar_counts.items(), key=lambda kv: (-kv[1], kv[0])
        )[:_EXEC_SUMMARY_TOP_PILLARS]
    ]
    top_names = [pillar_name_map.get(pid, pid) for pid in top_pids]
    if not top_names:
        return None

    # Collect graph-approved metric phrases for the top pillars (the ONLY
    # numbers the summary may carry).
    pillar_by_id = {
        str(p.get("pillar_id") or "").strip(): p
        for p in (graph.get("pillars") or [])
        if isinstance(p, dict)
    }
    metric_phrases: list[str] = []
    for pid in top_pids:
        pillar = pillar_by_id.get(pid, {})
        for phrase in _clean_str_list(pillar.get("allowed_phrases")):
            if _has_metric(phrase) and phrase not in metric_phrases:
                metric_phrases.append(phrase)
        for snip in _clean_str_list(pillar.get("archive_snippets")):
            if _has_metric(snip) and snip not in metric_phrases:
                metric_phrases.append(snip)
    # Also admit metric-bearing skill snippets in the top pillars.
    for row in rows:
        if str(row.get("pillar") or "").strip() not in top_pids:
            continue
        for snip in _clean_str_list(row.get("source_snippets")):
            if _has_metric(snip) and snip not in metric_phrases:
                metric_phrases.append(snip)

    areas = "; ".join(top_names)
    summary = (
        f"Engineering executive whose graph-grounded proof spans {areas}."
    )
    if metric_phrases:
        summary += " Metric-bound proof includes: " + "; ".join(metric_phrases[:3]) + "."
    return summary


def role_context_map_from_graph() -> dict[str, str]:
    """Map ExperiencePoint.title (skill name) -> pillar/domain context prose.

    This is the graph-derived replacement for the base-resume
    ``professional_experience[].context`` lookup that
    ``star_synthesis._load_role_context_map`` used to build. The context is the
    skill's pillar description (or domain), which frames the STAR ``situation``.
    Returns ``{}`` when the graph is unavailable.
    """
    graph = _load_graph()
    if graph is None:
        return {}
    pillar_by_id = {
        str(p.get("pillar_id") or "").strip(): p
        for p in (graph.get("pillars") or [])
        if isinstance(p, dict)
    }
    pillar_name_map = _pillar_name_map(graph)
    out: dict[str, str] = {}
    for row in _eligible_active_rows(graph):
        name = _skill_name(row)
        pid = str(row.get("pillar") or "").strip()
        pillar = pillar_by_id.get(pid, {})
        context = str(pillar.get("description") or "").strip()
        if not context:
            domain = str(row.get("domain") or "").strip()
            pillar_name = pillar_name_map.get(pid, pid)
            context = (
                f"{domain} — {pillar_name}".strip(" —")
                if domain or pillar_name
                else ""
            )
        if context:
            out[name] = context
    return out


__all__ = [
    "competency_areas_from_graph",
    "executive_summary_from_graph",
    "experience_library_from_graph",
    "role_context_map_from_graph",
]
