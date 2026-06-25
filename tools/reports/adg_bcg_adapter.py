"""Shared executive-brief helpers for ADG reports.

The adapter keeps the presentation contract consistent across reports while
preserving JSON compatibility for one release. Markdown renders the executive
view; JSON can keep legacy aliases and richer evidence payloads.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

BCG_NORTH_STAR = (
    "Maintain SVP engineer-level repo standards: executive decisions, explicit "
    "prioritization, and technical evidence a layperson can follow."
)

LEGACY_ROW_ALIASES: dict[str, str] = {
    "business_reason": "why_it_matters",
    "technical_reason": "evidence",
    "decision": "next_step",
}


@dataclass(frozen=True)
class ExecutivePriorityRow:
    priority: int = 0
    rank: int = 0
    move: str = ""
    action: str = ""
    work: str = ""
    why_it_matters: str = ""
    business_reason: str = ""
    evidence: str = ""
    technical_reason: str = ""
    next_step: str = ""
    why_this_rank: str = ""
    decision: str = ""
    scope: str = ""
    affected_system: str = ""
    affected_layers: list[str] = field(default_factory=list)
    change_breakout: list[dict[str, Any]] = field(default_factory=list)
    decision_options: list[dict[str, Any]] = field(default_factory=list)
    done_condition: str = ""
    diagram: dict[str, Any] | None = None
    action_type: str = ""


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


def _normalize_priority_row(row: dict[str, Any] | ExecutivePriorityRow | None) -> dict[str, Any]:
    if row is None:
        row = {}
    if isinstance(row, ExecutivePriorityRow):
        data = asdict(row)
    else:
        data = dict(row)

    priority = data.get("priority")
    if priority in (None, ""):
        priority = data.get("rank", 0)

    move = (
        data.get("move")
        or data.get("work")
        or data.get("action")
        or data.get("priority_work")
        or data.get("move_title")
        or ""
    )
    why_it_matters = (
        data.get("why_it_matters")
        or data.get("business_reason")
        or data.get("business")
        or data.get("why_now")
        or ""
    )
    evidence = (
        data.get("evidence")
        or data.get("technical_reason")
        or data.get("technical")
        or data.get("testing_mv_action")
        or ""
    )
    next_step = (
        data.get("next_step")
        or data.get("decision")
        or data.get("why_this_rank")
        or data.get("why")
        or ""
    )

    normalized = {
        "priority": int(priority or 0),
        "rank": int(data.get("rank") or priority or 0),
        "move": str(move),
        "action": str(data.get("action") or move),
        "work": str(data.get("work") or move),
        "why_it_matters": str(why_it_matters),
        "business_reason": str(data.get("business_reason") or why_it_matters),
        "evidence": str(evidence),
        "technical_reason": str(data.get("technical_reason") or evidence),
        "next_step": str(next_step),
        "why_this_rank": str(data.get("why_this_rank") or next_step),
        "decision": str(data.get("decision") or next_step),
        "scope": str(data.get("scope") or ""),
        "affected_system": str(data.get("affected_system") or ""),
        "affected_layers": list(data.get("affected_layers") or []),
        "change_breakout": list(data.get("change_breakout") or []),
        "decision_options": list(data.get("decision_options") or []),
        "done_condition": str(data.get("done_condition") or ""),
        "diagram": data.get("diagram"),
        "action_type": str(data.get("action_type") or ""),
    }

    for key, alias in LEGACY_ROW_ALIASES.items():
        if not normalized.get(key):
            normalized[key] = str(data.get(key) or normalized.get(alias) or "")

    return normalized


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
    normalized_rows = [_normalize_priority_row(row) for row in list(priority_rows or [])]
    return {
        "title": title,
        "north_star": BCG_NORTH_STAR,
        "business_read": business_read,
        "technical_read": _text_list(technical_read),
        "priority_rule": priority_rule or "",
        "priority_rows": normalized_rows,
        "why_this_order": [item for item in _text_list(why_this_order)],
        "next_step": next_step or "",
        "status": status or "",
        "status_label": status_label or "Status",
        "secondary_statuses": dict(secondary_statuses or {}),
        "table_limit": table_limit,
    }



def build_report_bcg_findings(
    *,
    report_kind: str,
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
    """Build the canonical BCG findings envelope used by ADG reports.

    Reports may keep richer domain-specific fields, but this envelope is the
    mandatory management-consulting story surface: what happened, why it matters,
    evidence, priority rule, ranked next moves, and done/next step.
    """
    brief = build_bcg_brief(
        title=title,
        status=status,
        status_label=status_label,
        secondary_statuses=secondary_statuses,
        business_read=business_read,
        technical_read=technical_read,
        priority_rule=priority_rule,
        priority_rows=priority_rows,
        why_this_order=why_this_order,
        next_step=next_step,
        table_limit=table_limit,
    )
    return {
        "schema_version": "1.0",
        "report_kind": report_kind,
        "brief": brief,
        "business_read": brief["business_read"],
        "technical_read": brief["technical_read"],
        "priority_rule": brief["priority_rule"],
        "priority_rows": brief["priority_rows"],
        "why_this_order": brief["why_this_order"],
        "next_step": brief["next_step"],
        "status": brief["status"],
        "status_label": brief["status_label"],
        "north_star": brief["north_star"],
    }


def render_report_bcg_findings_md(findings: dict[str, Any]) -> str:
    """Render a BCG findings envelope built by ``build_report_bcg_findings``."""
    brief = findings.get("brief") if isinstance(findings, dict) else None
    if not isinstance(brief, dict):
        brief = build_bcg_brief(
            title=str((findings or {}).get("title") or "BCG Brief"),
            business_read=str((findings or {}).get("business_read") or "No business read emitted."),
            technical_read=(findings or {}).get("technical_read") or [],
            priority_rule=str((findings or {}).get("priority_rule") or ""),
            priority_rows=(findings or {}).get("priority_rows") or [],
            why_this_order=(findings or {}).get("why_this_order") or [],
            next_step=str((findings or {}).get("next_step") or ""),
            status=str((findings or {}).get("status") or ""),
            status_label=str((findings or {}).get("status_label") or "Status"),
        )
    return render_bcg_brief_md(brief)


def has_bcg_findings(doc: dict[str, Any] | None) -> bool:
    """Return True when a report payload carries a usable BCG findings envelope."""
    if not isinstance(doc, dict):
        return False
    findings = doc.get("bcg_findings") or doc.get("brief")
    if isinstance(findings, dict) and "brief" in findings:
        findings = findings["brief"]
    return isinstance(findings, dict) and bool(
        findings.get("business_read") and findings.get("technical_read") and findings.get("priority_rule")
    )

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
    priority_rows = [_normalize_priority_row(row) for row in list(brief.get("priority_rows") or [])]
    if priority_rows:
        a("")
        a("| Priority | Move | Why it matters | Evidence | Next step |")
        a("|---------:|------|----------------|----------|-----------|")
        limit = brief.get("table_limit")
        if not isinstance(limit, int) or limit < 0:
            limit = len(priority_rows)
        for row in priority_rows[:limit]:
            a(
                f"| {_row_value(row, 'priority', 'rank')} | "
                f"{_row_value(row, 'move', 'work', 'priority_work', 'action')} | "
                f"{_row_value(row, 'why_it_matters', 'business_reason', 'business', 'why_now')} | "
                f"{_row_value(row, 'evidence', 'technical_reason', 'technical', 'testing_mv_action')} | "
                f"{_row_value(row, 'next_step', 'decision', 'why_this_rank', 'why')} |"
            )
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
    dead_hotspots = dead_code.get("dead_code_hotspots") or []
    dead_import_hotspots = dead_imports.get("dead_import_hotspots") or []
    cleanup_hotspots = dead_hotspots or dead_import_hotspots
    unresolved_hotspots = unresolved.get("unresolved_hotspots") or []
    unresolved_lead = unresolved_hotspots[0] if unresolved_hotspots else ("none", 0)
    source = report.get("source") or {}
    adg_snapshot = str(summary.get("adg_snapshot") or source.get("adg_snapshot") or "")
    adg_snapshot_ts = str(summary.get("adg_snapshot_ts") or source.get("adg_snapshot_ts") or "")
    technical_read: list[str] = []
    if adg_snapshot:
        source_line = f"ADG source: {adg_snapshot}"
        if adg_snapshot_ts:
            source_line = f"{source_line} (snapshot {adg_snapshot_ts})"
        technical_read.append(source_line)
    technical_read.extend(
        [
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
        ]
    )
    priority_rows: list[dict[str, Any]] = []

    def _priority_row(
        *,
        priority: int,
        move: str,
        why_it_matters: str,
        evidence: str,
        next_step: str,
        scope: str = "",
        decision: str = "",
    ) -> dict[str, Any]:
        return _normalize_priority_row(
            ExecutivePriorityRow(
                priority=priority,
                rank=priority,
                move=move,
                action=move,
                work=move,
                why_it_matters=why_it_matters,
                business_reason=why_it_matters,
                evidence=evidence,
                technical_reason=evidence,
                next_step=next_step,
                why_this_rank=next_step,
                decision=decision or next_step,
                scope=scope,
                done_condition="Rerun ADG and confirm the relevant evidence stays clean.",
            )
        )

    if cleanup_hotspots:
        for module, count in cleanup_hotspots[:3]:
            is_dead_code = bool(dead_hotspots) and dead_code.get("source") != "dead_import_overlay"
            move = (
                "Deprecate then delete confirmed dead code"
                if is_dead_code
                else "Remove confirmed dead imports"
            )
            why_it_matters = (
                "This is high-confidence cleanup because the completed ADG marked it as dead-code candidate traffic."
                if is_dead_code
                else "This is high-confidence cleanup because the completed ADG resolved it as dead import traffic."
            )
            evidence = (
                f"{count} dead-code candidate edge(s) point at this module."
                if is_dead_code
                else f"{count} resolved dead-import overlay row(s) point at this file."
            )
            next_step = (
                "Deprecate now, then delete after the evidence stays clean."
                if is_dead_code
                else "Remove the imports, then rerun ADG to confirm the dead-import signal clears."
            )
            priority_rows.append(
                _priority_row(
                    priority=len(priority_rows) + 1,
                    move=move,
                    why_it_matters=why_it_matters,
                    evidence=evidence,
                    next_step=next_step,
                    scope=module,
                    decision="delete_after_deprecation" if is_dead_code else "remove_imports",
                )
            )
    else:
        priority_rows.append(
            _priority_row(
                priority=1,
                move="Hold all deletion",
                why_it_matters=(
                    "The scan found no confirmed dead code, so deleting anything now would be speculative and could break working paths."
                ),
                evidence=(
                    f"Dead-code candidates = {summary.get('total_dead_code_candidates', 0)} and dead imports = {summary.get('total_dead_imports', 0)}."
                ),
                next_step="No deletion move until a proven target appears.",
                scope="whole codebase",
                decision="defer",
            )
        )

    priority_rows.extend(
        [
            _priority_row(
                priority=len(priority_rows) + 1,
                move="Triage unresolved imports",
                why_it_matters="Unresolved imports are the biggest uncertainty and can hide real cleanup opportunities.",
                evidence=(
                    f"{summary.get('total_unresolved_imports', 0)} unresolved imports; lead hotspot {unresolved_lead[0]} ({unresolved_lead[1]})."
                ),
                next_step="Trace the top unresolved scope before deleting anything else.",
                scope=unresolved_lead[0],
                decision="investigate",
            ),
            _priority_row(
                priority=len(priority_rows) + 2,
                move="Reduce low-confidence noise",
                why_it_matters="Cleaner evidence makes later reviews faster and lowers the risk of deleting the wrong thing.",
                evidence=(
                    "First-party low-confidence ratio = "
                    f"{float(low_conf.get('first_party_low_confidence_ratio', 0) or 0):.2f}% and inferred-symbol ratio = "
                    f"{float(inferred.get('inferred_symbol_ratio', 0) or 0):.2f}%."
                ),
                next_step="Lower the noise floor, then rerun the scan.",
                scope="first-party nodes",
                decision="stabilize",
            ),
            _priority_row(
                priority=len(priority_rows) + 3,
                move="Deprecate low-value ADG signals",
                why_it_matters="Remove empty or low-value diagnostics to cut review overhead once the evidence layer is stable.",
                evidence=(
                    f"{len([r for r in cleanup_candidates if r.get('item_type') == 'mv'])} MV candidates and "
                    f"{len([r for r in cleanup_candidates if r.get('item_type') == 'artifact'])} unused artifacts surfaced by the report."
                ),
                next_step="Deprecate only after higher-confidence cleanup is complete.",
                scope="materialized views and unused artifacts",
                decision="deprecate",
            ),
        ]
    )

    executive_read = (
        "ADG found confirmed dead-code targets; remove the most certain ones first, then clean up uncertainty and noisy diagnostics."
        if cleanup_hotspots
        else "No deletions are approved in this run because ADG found 0 confirmed dead-code candidates; reduce uncertainty first, then deprecate noisy diagnostics."
    )

    deletion_status = "DELETION_CANDIDATES" if cleanup_hotspots else "NO_DELETIONS_APPROVED"
    source_status = str(report.get("status") or "").strip()

    brief = build_bcg_brief(
        title="BCG Deletion Brief",
        status=deletion_status,
        status_label="Deletion status",
        secondary_statuses={"Source report status": source_status} if source_status else None,
        business_read=executive_read,
        technical_read=technical_read,
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
