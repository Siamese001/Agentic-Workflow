"""Shared BCG-style briefing helpers for ADG reports.

The adapter keeps the presentation contract consistent across reports:

* business-first summary
* plain-English technical evidence
* explicit priority order
* short rationale for why each item is ranked where it is

Reports provide the data; this module standardizes the wording and layout.
"""

from __future__ import annotations

from typing import Any

BCG_NORTH_STAR = (
    "Maintain SVP engineer-level repo standards: business-first decisions, "
    "explicit prioritization, and technical evidence a layperson can follow."
)


def _fmt_int(value: Any) -> str:
    try:
        return f"{int(value or 0):,}"
    except (TypeError, ValueError):
        return "0"


def _md(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def _text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    out: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            out.append(text)
    return out


def _row_value(row: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return _md(value)
    return ""


def build_bcg_brief(
    *,
    title: str,
    business_read: str,
    technical_read: str | list[str] | None = None,
    priority_rule: str | None = None,
    priority_rows: list[dict[str, Any]] | None = None,
    why_this_order: list[str] | None = None,
    next_step: str | None = None,
    status: str | None = None,
    status_label: str | None = None,
    secondary_statuses: dict[str, Any] | None = None,
    table_limit: int = 6,
) -> dict[str, Any]:
    """Create a normalized BCG brief payload for rendering."""
    return {
        "title": title,
        "north_star": BCG_NORTH_STAR,
        "business_read": business_read,
        "technical_read": _text_list(technical_read),
        "priority_rule": priority_rule or "",
        "priority_rows": list(priority_rows or []),
        "why_this_order": [item for item in _text_list(why_this_order)],
        "next_step": next_step or "",
        "status": status or "",
        "status_label": status_label or "Status",
        "secondary_statuses": dict(secondary_statuses or {}),
        "table_limit": table_limit,
    }


def render_bcg_brief_md(brief: dict[str, Any]) -> str:
    """Render a compact BCG-style brief as markdown."""
    lines: list[str] = []
    a = lines.append
    title = str(brief.get("title") or "BCG Brief")
    a(f"### {title}")
    a("")
    a(f"- **North star:** {_md(brief.get('north_star') or BCG_NORTH_STAR)}")
    status = str(brief.get("status") or "").strip()
    if status:
        status_label = str(brief.get("status_label") or "Status").strip() or "Status"
        a(f"- **{_md(status_label)}:** {_md(status)}")
    for label, value in (brief.get("secondary_statuses") or {}).items():
        if value not in (None, ""):
            a(f"- **{_md(label)}:** {_md(value)}")
    business_read = str(brief.get("business_read") or "").strip()
    if business_read:
        a(f"- **Business read:** {_md(business_read)}")
    technical_read = _text_list(brief.get("technical_read"))
    if technical_read:
        a("- **Technical evidence:**")
        for item in technical_read:
            a(f"  - {_md(item)}")
    priority_rule = str(brief.get("priority_rule") or "").strip()
    if priority_rule:
        a(f"- **Priority rule:** {_md(priority_rule)}")
    priority_rows = list(brief.get("priority_rows") or [])
    if priority_rows:
        a("")
        a("| Priority | Move | Scope | Business reason | Technical reason | Why this order | Decision |")
        a("|---------:|------|-------|----------------|-----------------|----------------|----------|")
        limit = brief.get("table_limit")
        if not isinstance(limit, int) or limit < 0:
            limit = len(priority_rows)
        for row in priority_rows[:limit]:
            a(
                f"| {_row_value(row, 'priority', 'rank')} | "
                f"{_row_value(row, 'move', 'work', 'priority_work', 'action')} | "
                f"{_row_value(row, 'scope', 'band', 'target')} | "
                f"{_row_value(row, 'business_reason', 'business')} | "
                f"{_row_value(row, 'technical_reason', 'technical')} | "
                f"{_row_value(row, 'why_this_rank', 'why', 'why_this_priority')} | "
                f"{_row_value(row, 'decision', 'next_step')} |"
            )
    why_this_order = _text_list(brief.get("why_this_order"))
    if why_this_order:
        a("")
        a("Why this order:")
        for item in why_this_order:
            a(f"- {_md(item)}")
    next_step = str(brief.get("next_step") or "").strip()
    if next_step:
        a("")
        a(f"Next step: {_md(next_step)}")
    return "\n".join(lines)


def _defer_delete(
    mv_usefulness_audit: dict[str, Any] | None,
    artifact_usage_matrix: dict[str, Any] | None,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for r in (mv_usefulness_audit or {}).get("rows", [])[:20]:
        if r.get("recommendation") != "keep":
            rows.append(
                {
                    "item": r["mv_name"],
                    "item_type": "mv",
                    "current_value": f"{r.get('row_count')} rows; {r.get('category')}",
                    "recommendation": "deprecate"
                    if r.get("recommendation") == "deprecate_candidate"
                    else r.get("recommendation", "keep"),
                    "rationale": r.get("why_not_used_if_suppressed")
                    or r.get("decision_impact"),
                    "revisit_condition": (
                        "Promote only when tied to blocker, test gap, critical path, or planned slice."
                    ),
                }
            )
    for r in (artifact_usage_matrix or {}).get("rows", []):
        if r.get("used_for") == ["none"]:
            rows.append(
                {
                    "item": r["artifact_key"],
                    "item_type": "artifact",
                    "current_value": "unused or missing",
                    "recommendation": "hide_inline",
                    "rationale": r.get("rationale"),
                    "revisit_condition": (
                        "Use when it changes next action, audit, consistency, or test placement."
                    ),
                }
            )
    return {"status": "present", "rows": rows[:25]}


def build_deprecation_deletion_plan(
    dead_code_report: dict[str, Any] | None,
    mv_usefulness_audit: dict[str, Any] | None,
    artifact_usage_matrix: dict[str, Any] | None,
) -> dict[str, Any]:
    report = dead_code_report or {}
    summary = report.get("summary") or {}
    dead_code = report.get("dead_code_candidates") or {}
    dead_imports = report.get("dead_imports") or {}
    unresolved = report.get("unresolved_imports") or {}
    low_conf = report.get("low_confidence_zones") or {}
    inferred = report.get("inferred_symbols") or {}
    cleanup_candidates = _defer_delete(mv_usefulness_audit, artifact_usage_matrix).get("rows", [])
    dead_hotspots = dead_code.get("dead_code_hotspots") or dead_imports.get("dead_import_hotspots") or []
    unresolved_hotspots = unresolved.get("unresolved_hotspots") or []
    unresolved_lead = unresolved_hotspots[0] if unresolved_hotspots else ("none", 0)
    priority_rows: list[dict[str, Any]] = []

    if dead_hotspots:
        for module, count in dead_hotspots[:3]:
            priority_rows.append(
                {
                    "priority": len(priority_rows) + 1,
                    "move": "Deprecate then delete confirmed dead code",
                    "scope": module,
                    "business_reason": (
                        "This is the highest-confidence waste to remove because ADG already "
                        "marked it as a dead-code or dead-import hotspot."
                    ),
                    "technical_reason": f"{count} dead-code hotspot(s) point at this module.",
                    "why_this_rank": (
                        "Delete the most certain waste first so we do not spend time cleaning speculative targets."
                    ),
                    "decision": "delete_after_deprecation",
                }
            )
    else:
        priority_rows.append(
            {
                "priority": 1,
                "move": "Hold all deletion",
                "scope": "whole codebase",
                "business_reason": (
                    "The scan found no confirmed dead code, so deleting anything now would be "
                    "speculative and could break working paths."
                ),
                "technical_reason": (
                    f"Dead-code candidates = {summary.get('total_dead_code_candidates', 0)} "
                    f"and dead imports = {summary.get('total_dead_imports', 0)}."
                ),
                "why_this_rank": "No proven target means the safest action is to pause deletion.",
                "decision": "defer",
            }
        )

    priority_rows.extend(
        [
            {
                "priority": len(priority_rows) + 1,
                "move": "Triage unresolved imports",
                "scope": unresolved_lead[0],
                "business_reason": (
                    "Unresolved imports are the biggest uncertainty and can hide real cleanup opportunities."
                ),
                "technical_reason": (
                    f"{summary.get('total_unresolved_imports', 0)} unresolved imports; "
                    f"lead hotspot {unresolved_lead[0]} ({unresolved_lead[1]})."
                ),
                "why_this_rank": "We need a cleaner signal before we can trust deletion decisions.",
                "decision": "investigate",
            },
            {
                "priority": len(priority_rows) + 2,
                "move": "Reduce low-confidence noise",
                "scope": "first-party nodes",
                "business_reason": (
                    "Cleaner evidence makes later reviews faster and lowers the risk of deleting the wrong thing."
                ),
                "technical_reason": (
                    "First-party low-confidence ratio = "
                    f"{float(low_conf.get('first_party_low_confidence_ratio', 0) or 0):.2f}% "
                    "and inferred-symbol ratio = "
                    f"{float(inferred.get('inferred_symbol_ratio', 0) or 0):.2f}%."
                ),
                "why_this_rank": "Noise reduction improves the quality of the next scan and makes future deletions safer.",
                "decision": "stabilize",
            },
            {
                "priority": len(priority_rows) + 3,
                "move": "Deprecate low-value ADG signals",
                "scope": "materialized views and unused artifacts",
                "business_reason": (
                    "Remove empty or low-value diagnostics to cut review overhead once the evidence layer is stable."
                ),
                "technical_reason": (
                    f"{len([r for r in cleanup_candidates if r.get('item_type') == 'mv'])} MV candidates and "
                    f"{len([r for r in cleanup_candidates if r.get('item_type') == 'artifact'])} unused artifacts "
                    "surfaced by the report."
                ),
                "why_this_rank": "This is cheap cleanup, but it should follow the evidence cleanup work above.",
                "decision": "deprecate",
            },
        ]
    )

    executive_read = (
        "ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics."
        if dead_hotspots
        else "No deletions are approved in this run because ADG found 0 confirmed dead-code candidates; reduce uncertainty first, then deprecate noisy diagnostics."
    )

    deletion_status = "DELETION_CANDIDATES" if dead_hotspots else "NO_DELETIONS_APPROVED"
    source_status = str(report.get("status") or "").strip()

    brief = build_bcg_brief(
        title="BCG Deletion Brief",
        status=deletion_status,
        status_label="Deletion status",
        secondary_statuses={"Source report status": source_status} if source_status else None,
        business_read=executive_read,
        technical_read=[
            f"Dead code candidates: {_fmt_int(summary.get('total_dead_code_candidates', 0))}",
            f"Dead imports: {_fmt_int(summary.get('total_dead_imports', 0))}",
            f"Unresolved imports: {_fmt_int(summary.get('total_unresolved_imports', 0))}",
            (
                "First-party low-confidence ratio: "
                f"{float(low_conf.get('first_party_low_confidence_ratio', 0) or 0):.2f}%"
            ),
            (
                "Inferred-symbol ratio: "
                f"{float(inferred.get('inferred_symbol_ratio', 0) or 0):.2f}%"
            ),
            f"Cleanup candidates surfaced: {_fmt_int(len(cleanup_candidates))}",
        ],
        priority_rule=(
            "Confirmed dead code first, then unresolved imports, then low-confidence noise, "
            "then low-value diagnostics."
        ),
        priority_rows=priority_rows[:6],
        why_this_order=[
            "Confirmed dead code is the highest-confidence waste and should be removed first.",
            "Unresolved imports are the biggest uncertainty and can hide real cleanup work.",
            "Low-confidence and inferred-symbol noise should be reduced before taking more aggressive action.",
            "Low-value diagnostics are cheap to deprecate once the evidence layer is cleaner.",
        ],
        next_step="Deprecate first, then delete after the evidence stays clean.",
        table_limit=6,
    )

    return {
        "status": "present",
        "summary": {
            "executive_read": executive_read,
            "why_this_order": [
                "Confirmed dead code is the highest-confidence waste and should be removed first.",
                "Unresolved imports are the biggest uncertainty and can hide real cleanup work.",
                "Low-confidence and inferred-symbol noise should be reduced before taking more aggressive action.",
                "Low-value diagnostics are cheap to deprecate once the evidence layer is cleaner.",
            ],
            "dead_code_candidates": int(summary.get("total_dead_code_candidates", 0) or 0),
            "dead_imports": int(summary.get("total_dead_imports", 0) or 0),
            "unresolved_imports": int(summary.get("total_unresolved_imports", 0) or 0),
            "first_party_low_confidence_ratio": float(low_conf.get("first_party_low_confidence_ratio", 0) or 0),
            "inferred_symbol_ratio": float(inferred.get("inferred_symbol_ratio", 0) or 0),
            "cleanup_candidate_count": len(cleanup_candidates),
        },
        "brief": brief,
        "priority_rows": priority_rows[:6],
        "cleanup_candidates": cleanup_candidates[:12],
    }
