"""Shared executive-brief helpers for ADG reports.

The adapter keeps the presentation contract consistent across reports while
preserving JSON compatibility for one release. Markdown renders the executive
view; JSON can keep legacy aliases and richer evidence payloads.
"""

from __future__ import annotations

import datetime as _dt
import json
import shutil
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from tools.reports.gate_signal_catalog import (
    display_verdict,
    display_verdict_sub,
    format_gate_signal,
    recommended_next_step,
)

BCG_NORTH_STAR = (
    "Maintain SVP engineer-level repo standards: executive decisions, explicit "
    "prioritization, and technical evidence a layperson can follow."
)

LEGACY_ROW_ALIASES: dict[str, str] = {
    "business_reason": "why_it_matters",
    "technical_reason": "evidence",
    "decision": "next_step",
}

BCG_GATE_ADAPTER_SCHEMA_VERSION = "1.0"
BCG_GATE_ADAPTER_POLICY_VERSION = "2026-06-28.high_signal_burndown_v1"

# These signals are useful to monitor, but they are not a burn-down queue unless
# a future plan gives them an owner, target, and explicit retirement condition.
KPI_OR_WATCHLIST_GATE_IDS: frozenset[str] = frozenset(
    {
        "S4_unused_imports_ratchet",
        "Q2_cyclomatic_complexity_ratchet",
        "M1_module_loc_ratchet",
        "D1_layer_doc_binding",
        "D2_role_duplication_warn",
        "K1_churn_complexity_kpi",
        "E3_trace_theater_kpi",
        "H3_ap_velocity_kpi",
    }
)

KPI_OR_WATCHLIST_TOKENS: tuple[str, ...] = (
    "_kpi",
    "cyclomatic",
    "unused_imports",
    "module_loc",
    "layer_doc_binding",
    "role_duplication",
)


def is_unreleased_p0_tracked_gate(gate: dict[str, Any]) -> bool:
    """Return True when a P0 row is visible debt, not released P0 work.

    The downstream P0 lane burns ``FIX`` and action-queue ``P0_WAVE`` rows.
    P0 ``TRACK`` gates are still important evidence, but treating ratchet
    floors or warning inventory as immediate P0 work re-opens a green run for
    broad backlog that has not been promoted by the released queue.
    """
    return str(gate.get("band") or "") == "P0" and display_verdict(gate) == "TRACK"

SECTION_ORDER: tuple[str, ...] = ("fix_now", "burn_down", "kpi_watchlist", "clear")

SECTION_LABELS: dict[str, str] = {
    "fix_now": "Fix now",
    "burn_down": "Burn down / owned backlog",
    "kpi_watchlist": "KPI / watchlist",
    "clear": "Clear",
}

SECTION_DESCRIPTIONS: dict[str, str] = {
    "fix_now": "Current blockers, regressions, or missing seeds. These are the only rows that should stop green ADG.",
    "burn_down": "Accepted debt that is still plausible burn-down work after FIX rows clear.",
    "kpi_watchlist": "Trend and hygiene signals. Report separately; do not treat as burn-down work without an owner and target.",
    "clear": "Zero-action rows.",
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


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _gate_id(gate: dict[str, Any]) -> str:
    return str(gate.get("gate_id") or gate.get("gate_family") or gate.get("name") or "").strip()


def _gate_rows(gate: dict[str, Any]) -> int:
    try:
        return int(gate.get("violation_count") or gate.get("violations_count") or 0)
    except (TypeError, ValueError):
        return 0


def is_kpi_or_watchlist_gate(gate: dict[str, Any]) -> bool:
    """Return True for report-only health/KPI signals.

    These gates may still matter, but they are not automatically burn-down work.
    Keeping the classification here prevents every report from inventing its own
    definition of "not actionable unless planned."
    """
    if is_unreleased_p0_tracked_gate(gate):
        return True
    gate_id = _gate_id(gate)
    lowered = gate_id.lower()
    if gate_id in KPI_OR_WATCHLIST_GATE_IDS:
        return True
    if any(token in lowered for token in KPI_OR_WATCHLIST_TOKENS):
        return True
    return str(gate.get("band") or "") == "P3" and str(gate.get("enforcement") or "") == "warn"


def _section_for_gate(gate: dict[str, Any]) -> str:
    verdict = display_verdict(gate)
    if verdict == "FIX":
        return "fix_now"
    if verdict == "CLEAR":
        return "clear"
    if is_kpi_or_watchlist_gate(gate):
        return "kpi_watchlist"
    return "burn_down"


def _materiality_for_gate(gate: dict[str, Any], section: str) -> str:
    gate_id = _gate_id(gate)
    lowered = gate_id.lower()
    if gate_id == "13_core_imports_apps" or "core_imports_apps" in lowered:
        return "core_app_boundary"
    if "provider" in lowered or gate_id in {"4_capability_egress", "C2_l5_bypass_pview"}:
        return "provider_model_path"
    if "embedding" in lowered or "retrieval" in lowered:
        return "retrieval_accuracy"
    if gate_id == "10_infra_wiring" or "apps_direct_infra" in lowered:
        return "runtime_infra_boundary"
    if section == "kpi_watchlist":
        return "governance_hygiene"
    return "architecture_backlog"


def normalize_bcg_gate_row(gate: dict[str, Any]) -> dict[str, Any]:
    """Normalize one dispatcher gate row for BCG/high-signal report consumers."""
    gate_id = _gate_id(gate)
    section = _section_for_gate(gate)
    verdict = display_verdict(gate)
    sub = display_verdict_sub(gate)
    rows = _gate_rows(gate)
    materiality = _materiality_for_gate(gate, section)
    baseline = gate.get("baseline_count")
    delta = None
    if baseline not in (None, ""):
        try:
            delta = rows - int(baseline)
        except (TypeError, ValueError):
            delta = None
    return {
        "gate_id": gate_id,
        "gate_class": str(gate.get("gate_class") or ""),
        "band": str(gate.get("band") or ""),
        "enforcement": str(gate.get("enforcement") or ""),
        "classification": str(gate.get("classification") or ""),
        "status": str(gate.get("status") or ""),
        "verdict": verdict,
        "sub": sub,
        "section": section,
        "section_label": SECTION_LABELS[section],
        "materiality": materiality,
        "rows": rows,
        "baseline_count": baseline,
        "delta_vs_baseline": delta,
        "is_kpi_or_watchlist": section == "kpi_watchlist",
        "is_burndown_work": section in {"fix_now", "burn_down"},
        "reported_for_priority_queue": section in {"fix_now", "burn_down"},
        "signal": format_gate_signal(gate),
        "next_step": recommended_next_step(gate),
        "raw_gate": gate,
    }


def _sort_adapter_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    section_rank = {name: idx for idx, name in enumerate(SECTION_ORDER)}

    def _within_section_key(row: dict[str, Any]) -> tuple[int, int, int, int, str]:
        section = str(row.get("section") or "")
        band_rank = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(str(row.get("band") or "").upper(), 9)
        enforcement_rank = 0 if str(row.get("enforcement") or "").lower() == "block" else 1
        materiality_rank = {
            "runtime_infra_boundary": 0,
            "core_app_boundary": 1,
            "provider_model_path": 2,
            "retrieval_accuracy": 3,
            "architecture_backlog": 4,
            "governance_hygiene": 5,
        }.get(str(row.get("materiality") or ""), 9)
        if section == "fix_now":
            return (band_rank, enforcement_rank, materiality_rank, -int(row.get("delta_vs_baseline") or 0), str(row.get("gate_id") or ""))
        return (band_rank, materiality_rank, -int(row.get("rows") or 0), 0, str(row.get("gate_id") or ""))

    return sorted(
        rows,
        key=lambda row: (
            section_rank.get(str(row.get("section") or ""), 99),
            _within_section_key(row),
        ),
    )


def build_bcg_gate_adapter(
    gates_doc: dict[str, Any] | None,
    burndown: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the normalized BCG adapter for a full ADG gate run.

    The adapter is intentionally machine-readable. Human reports should render
    FIX and burn-down rows as work, and KPI/watchlist rows as a separate trend
    section rather than smuggling them into the action queue.
    """
    source = gates_doc or {}
    gates = [g for g in list(source.get("gates") or []) if isinstance(g, dict)]
    rows = _sort_adapter_rows([normalize_bcg_gate_row(g) for g in gates])
    sections: dict[str, dict[str, Any]] = {}
    for section in SECTION_ORDER:
        section_rows = [row for row in rows if row.get("section") == section]
        sections[section] = {
            "label": SECTION_LABELS[section],
            "description": SECTION_DESCRIPTIONS[section],
            "gate_count": len(section_rows),
            "row_count": sum(int(row.get("rows") or 0) for row in section_rows),
            "rows": section_rows,
        }

    # Backward-compatible alias: these are work-visible rows, not one blended
    # priority list. Consumers should prefer ``sections`` for MECE ownership.
    priority_rows = sections["fix_now"]["rows"] + sections["burn_down"]["rows"]
    report_only_rows = sections["kpi_watchlist"]["rows"]
    summary = {
        "total_gates": len(rows),
        "fix_now_gates": sections["fix_now"]["gate_count"],
        "burn_down_gates": sections["burn_down"]["gate_count"],
        "kpi_watchlist_gates": sections["kpi_watchlist"]["gate_count"],
        "clear_gates": sections["clear"]["gate_count"],
        "fix_now_rows": sections["fix_now"]["row_count"],
        "burn_down_rows": sections["burn_down"]["row_count"],
        "kpi_watchlist_rows": sections["kpi_watchlist"]["row_count"],
        "work_section_gate_count": len(priority_rows),
        "work_section_row_count": sum(int(row.get("rows") or 0) for row in priority_rows),
        "priority_queue_gate_count": len(priority_rows),
        "priority_queue_row_count": sum(int(row.get("rows") or 0) for row in priority_rows),
        "report_only_gate_count": len(report_only_rows),
        "report_only_row_count": sum(int(row.get("rows") or 0) for row in report_only_rows),
    }
    return {
        "schema_version": BCG_GATE_ADAPTER_SCHEMA_VERSION,
        "artifact_kind": "adg_bcg_gate_adapter",
        "policy_version": BCG_GATE_ADAPTER_POLICY_VERSION,
        "generated_at_utc": _now(),
        "source": {
            "timestamp": source.get("timestamp"),
            "snapshot": source.get("snapshot"),
            "snapshot_path": source.get("snapshot_path"),
            "overall_exit_code": source.get("overall_exit_code"),
            "burndown_schema_version": (burndown or {}).get("schema_version"),
        },
        "policy": {
            "priority_rule": "FIX first; burn down accepted debt only when it is owned; keep KPI/watchlist rows in a separate report-only section.",
            "kpi_watchlist_rule": "KPI/watchlist rows are not burn-down work unless a future plan gives them an owner, target, and retirement condition.",
            "section_order": list(SECTION_ORDER),
        },
        "summary": summary,
        "sections": sections,
        "priority_rows": priority_rows,
        "report_only_rows": report_only_rows,
    }


def render_bcg_gate_adapter_md(adapter: dict[str, Any]) -> str:
    """Render the BCG gate adapter as compact markdown."""
    lines: list[str] = []
    a = lines.append
    summary = adapter.get("summary") or {}
    a("# ADG BCG Gate Adapter")
    a("")
    a(f"- **Generated:** {_md(adapter.get('generated_at_utc'))}")
    a(f"- **Policy:** `{_md(adapter.get('policy_version'))}`")
    a(f"- **Source timestamp:** {_md((adapter.get('source') or {}).get('timestamp') or 'n/a')}")
    a(
        "- **Work sections:** "
        f"{_fmt_int(summary.get('work_section_gate_count', summary.get('priority_queue_gate_count')))} gate(s) / "
        f"{_fmt_int(summary.get('work_section_row_count', summary.get('priority_queue_row_count')))} row(s)"
    )
    a(
        "- **KPI/watchlist:** "
        f"{_fmt_int(summary.get('report_only_gate_count'))} gate(s) / "
        f"{_fmt_int(summary.get('report_only_row_count'))} row(s)"
    )
    a("")
    a("This adapter is MECE: FIX, burn-down, KPI/watchlist, and clear rows have one ownership section each. FIX rows can block green; burn-down rows are after-green work; KPI/watchlist rows stay visible without becoming automatic cleanup work.")
    for section in SECTION_ORDER:
        sec = (adapter.get("sections") or {}).get(section) or {}
        rows = list(sec.get("rows") or [])
        a("")
        a(f"## {sec.get('label') or SECTION_LABELS[section]}")
        a("")
        a(str(sec.get("description") or SECTION_DESCRIPTIONS[section]))
        a("")
        if not rows:
            a("_No rows._")
            continue
        a("| Gate | Materiality | Band | Enforcement | Verdict | Sub | Rows | Next step |")
        a("|------|-------------|:----:|-------------|:-------:|:---:|-----:|-----------|")
        for row in rows[:12]:
            a(
                f"| `{_md(row.get('gate_id'))}` | "
                f"{_md(row.get('materiality'))} | "
                f"{_md(row.get('band'))} | "
                f"{_md(row.get('enforcement'))} | "
                f"{_md(row.get('verdict'))} | "
                f"{_md(row.get('sub'))} | "
                f"{_fmt_int(row.get('rows'))} | "
                f"{_md(row.get('next_step'))} |"
            )
    return "\n".join(lines) + "\n"


def _read_json(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"value": data}


def _write_json(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True, default=str), encoding="utf-8")


def emit_bcg_gate_adapter(
    *,
    adg_artifacts_dir: Path,
    ts: str,
    gate_results_path: Path | None = None,
    burndown_path: Path | None = None,
    docs_dir: Path | None = None,
    print_inline: bool = False,
    fail_closed: bool = False,
) -> tuple[int, Path | None]:
    """Emit the first BCG artifact for a generated ADG run."""
    try:
        gates_doc = _read_json(gate_results_path)
        if gates_doc is None:
            raise FileNotFoundError(f"gate results missing: {gate_results_path}")
        burndown = _read_json(burndown_path) or {}
        adapter = build_bcg_gate_adapter(gates_doc, burndown)
        md = render_bcg_gate_adapter_md(adapter)
        base = adg_artifacts_dir / f"adg_bcg_adapter_{ts}"
        json_path = base.with_suffix(".json")
        md_path = base.with_suffix(".md")
        _write_json(json_path, adapter)
        md_path.write_text(md, encoding="utf-8")
        docs_target = docs_dir or Path("docs/reports/adg")
        for suffix, src in (("json", json_path), ("md", md_path)):
            latest = adg_artifacts_dir / f"adg_bcg_adapter_latest.{suffix}"
            docs_latest = docs_target / f"adg_bcg_adapter_latest.{suffix}"
            latest.parent.mkdir(parents=True, exist_ok=True)
            docs_latest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, latest)
            shutil.copyfile(src, docs_latest)
        if print_inline:
            sys.stdout.write("\n" + md)
        print(f"[adg_bcg_adapter] ADAPTER={json_path}", file=sys.stderr)
        return 0, json_path
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"[adg_bcg_adapter] ADAPTER_ERROR={exc}", file=sys.stderr)
        return (2 if fail_closed else 0), None


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
    decision_gates: list[dict[str, Any]] | None = None,
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
    normalized_decision_gates = [_normalize_priority_row(row) for row in list(decision_gates or [])]
    normalized_rows = [_normalize_priority_row(row) for row in list(priority_rows or [])]
    return {
        "title": title,
        "north_star": BCG_NORTH_STAR,
        "business_read": business_read,
        "technical_read": _text_list(technical_read),
        "decision_gates": normalized_decision_gates,
        "priority_rule": priority_rule or "",
        "priority_rows": normalized_rows,
        "why_this_order": list(_text_list(why_this_order)),
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
    decision_gates: list[dict[str, Any]] | None = None,
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
        decision_gates=decision_gates,
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
        "decision_gates": brief["decision_gates"],
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
            decision_gates=(findings or {}).get("decision_gates") or [],
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
    business_read = str(brief.get("business_read") or "").strip()
    if business_read:
        a(f"- **Business read:** {_md(business_read)}")
    status = str(brief.get("status") or "").strip()
    if status:
        status_label = str(brief.get("status_label") or "Status").strip() or "Status"
        a(f"- **{_md(status_label)}:** {_md(status)}")
    for label, value in (brief.get("secondary_statuses") or {}).items():
        if value not in (None, ""):
            a(f"- **{_md(label)}:** {_md(value)}")
    technical_read = _text_list(brief.get("technical_read"))
    if technical_read:
        a("- **Technical evidence:**")
        for item in technical_read:
            a(f"  - {_md(item)}")
    priority_rule = str(brief.get("priority_rule") or "").strip()
    if priority_rule:
        a(f"- **Priority rule:** {_md(priority_rule)}")
    decision_gates = [_normalize_priority_row(row) for row in list(brief.get("decision_gates") or [])]
    if decision_gates:
        a("")
        a("Decision gate:")
        a("")
        a("| Gate | Why it matters | Evidence | Required before ranking |")
        a("|------|----------------|----------|-------------------------|")
        for row in decision_gates:
            a(
                f"| {_row_value(row, 'move', 'work', 'priority_work', 'action')} | "
                f"{_row_value(row, 'why_it_matters', 'business_reason', 'business', 'why_now')} | "
                f"{_row_value(row, 'evidence', 'technical_reason', 'technical', 'testing_mv_action')} | "
                f"{_row_value(row, 'next_step', 'decision', 'why_this_rank', 'why')} |"
            )
    priority_rows = [_normalize_priority_row(row) for row in list(brief.get("priority_rows") or [])]
    if priority_rows:
        a("")
        a("Fix now:")
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
