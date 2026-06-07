"""P0 remediation wave planning on top of the canonical ADG SQLite snapshot.

This module intentionally stays read-only. It builds a prioritized wave plan from
P0-class defects already present in the canonical ADG artifact so the same logic
can be used by:
- generate_full_adg post-scan hardening
- the ADG SQLite MCP service
- standalone repair/debug workflows
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import json
import sqlite3
from pathlib import Path
from typing import Any
from urllib.parse import quote

from tools.adg.core.guardian_filter import is_layer_violation_exempted

# Repo root — canonical reference for resolving source_file relative paths.
_REPO_ROOT = Path(__file__).resolve().parents[3]

_MAX_PLAN_LIMIT = 1000
_PROTECTED_LAYERS = frozenset({"L0", "L2", "L3", "L5"})
_PROTECTED_PATH_PREFIXES = (
    "agentic_core/L0_",
    "agentic_core/L2_",
    "agentic_core/L3_",
    "agentic_core/L5_",
)


def _readonly_uri(path: Path) -> str:
    return f"file:{quote(str(path.resolve()))}?mode=ro"


def _normalize_limit(limit: int) -> int:
    if limit <= 0:
        return 100
    return min(limit, _MAX_PLAN_LIMIT)


def _line_no(value: Any) -> int:
    try:
        line_no = int(value)
    except (TypeError, ValueError):
        return 0
    return max(line_no, 0)


def _is_protected_surface(source_file: str, from_layer: str, to_layer: str) -> bool:
    if from_layer in _PROTECTED_LAYERS or to_layer in _PROTECTED_LAYERS:
        return True
    return any(source_file.startswith(prefix) for prefix in _PROTECTED_PATH_PREFIXES)


def _priority_weight(issue_type: str, protected_surface: bool) -> int:
    if issue_type == "dynamic_exec":
        return 1000
    if issue_type == "circular_import":
        return 850
    if protected_surface:
        return 600
    return 250


def _row_to_issue(row: sqlite3.Row, issue_type: str) -> dict[str, Any]:
    source_file = row["source_file"] or ""
    from_layer = row["from_layer"] or ""
    to_layer = row["to_layer"] or ""
    protected_surface = _is_protected_surface(source_file, from_layer, to_layer)
    direct_fan_in = int(row["direct_fan_in"] or 0)
    issue = {
        "issue_type": issue_type,
        "source_file": source_file,
        "line_no": _line_no(row["line_no"]),
        "from_name": row["from_name"] or "",
        "to_name": row["to_name"] or "",
        "from_layer": from_layer,
        "to_layer": to_layer,
        "direct_fan_in": direct_fan_in,
        "protected_surface": protected_surface,
    }
    issue["priority_score"] = _priority_weight(issue_type, protected_surface) + direct_fan_in
    return issue


def _aggregate_top_files(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_file: dict[str, dict[str, Any]] = {}
    for issue in issues:
        source_file = issue["source_file"] or "ADG_METADATA"
        current = by_file.setdefault(
            source_file,
            {
                "source_file": source_file,
                "issue_count": 0,
                "direct_fan_in_max": 0,
                "protected_surface": False,
                "kinds": set(),
                "priority_score": 0,
            },
        )
        current["issue_count"] += 1
        current["direct_fan_in_max"] = max(current["direct_fan_in_max"], issue["direct_fan_in"])
        current["protected_surface"] = current["protected_surface"] or issue["protected_surface"]
        current["kinds"].add(issue["issue_type"])
        current["priority_score"] += int(issue["priority_score"])

    top_files: list[dict[str, Any]] = []
    for item in by_file.values():
        top_files.append(
            {
                "source_file": item["source_file"],
                "issue_count": item["issue_count"],
                "direct_fan_in_max": item["direct_fan_in_max"],
                "protected_surface": item["protected_surface"],
                "issue_kinds": sorted(item["kinds"]),
                "priority_score": item["priority_score"],
            }
        )

    top_files.sort(
        key=lambda item: (
            -int(item["priority_score"]),
            -int(item["issue_count"]),
            item["source_file"],
        )
    )
    return top_files[:15]


def _wave(
    wave_id: str,
    title: str,
    goal: str,
    exit_criteria: str,
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    ordered = sorted(
        issues,
        key=lambda item: (-int(item["priority_score"]), item["source_file"], int(item["line_no"])),
    )
    return {
        "wave_id": wave_id,
        "title": title,
        "goal": goal,
        "exit_criteria": exit_criteria,
        "item_count": len(ordered),
        "items": ordered,
    }


def build_p0_remediation_wave_plan(sqlite_path: Path, limit: int = 100) -> dict[str, Any]:
    """Build a prioritized P0 remediation plan from the canonical ADG SQLite file."""
    sqlite_path = Path(sqlite_path).resolve()
    if not sqlite_path.exists():
        raise FileNotFoundError(f"ADG SQLite not found: {sqlite_path}")

    safe_limit = _normalize_limit(limit)
    conn = sqlite3.connect(_readonly_uri(sqlite_path), timeout=5, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    try:
        query = """
            WITH node_fan_in AS (
                SELECT dst_id, COUNT(DISTINCT src_id) AS direct_fan_in
                FROM edges
                GROUP BY dst_id
            )
            SELECT
                COALESCE(e.source_file, '') AS source_file,
                COALESCE(e.line_no, 0) AS line_no,
                COALESCE(src.adg_name, '') AS from_name,
                COALESCE(dst.adg_name, '') AS to_name,
                COALESCE(src.layer, '') AS from_layer,
                COALESCE(dst.layer, '') AS to_layer,
                COALESCE(fi.direct_fan_in, 0) AS direct_fan_in
            FROM edges e
            JOIN nodes src ON e.src_id = src.id
            LEFT JOIN nodes dst ON e.dst_id = dst.id
            LEFT JOIN node_fan_in fi ON fi.dst_id = e.src_id
            WHERE e.relation_type = ?
            ORDER BY COALESCE(fi.direct_fan_in, 0) DESC, COALESCE(e.source_file, ''), COALESCE(e.line_no, 0)
            LIMIT ?
        """

        # Apply guardian-exemption filter (SSOT: tools/adg/core/guardian_filter.py).
        # Rows with `# guardian: allow-layer-violation` on the violation line or
        # the line above are legitimate exemptions and must NOT be reported as P0.
        layer_violations = [
            _row_to_issue(row, "layer_violation")
            for row in conn.execute(query, ("violates", safe_limit))
            if not is_layer_violation_exempted(
                row["source_file"],
                row["line_no"],
                repo_root=_REPO_ROOT,
            )
        ]
        circular_imports = [
            _row_to_issue(row, "circular_import") for row in conn.execute(query, ("in_cycle", safe_limit))
        ]
        dynamic_exec = [
            _row_to_issue(row, "dynamic_exec") for row in conn.execute(query, ("dynamic_exec", safe_limit))
        ]
    finally:
        conn.close()

    protected_violations = [issue for issue in layer_violations if issue["protected_surface"]]
    remaining_violations = [issue for issue in layer_violations if not issue["protected_surface"]]

    waves = [
        _wave(
            "wave_0_stop_the_line",
            "Stop-the-line structural blockers",
            "Eliminate dynamic execution and import-cycle defects that make the ADG provably incomplete or structurally unstable.",
            "Zero dynamic_exec edges and zero in_cycle edges remain.",
            circular_imports + dynamic_exec,
        ),
        _wave(
            "wave_1_protected_planes",
            "Protected-plane boundary fixes",
            "Resolve layer violations touching protected planes first so routing, execution, orchestration, and safety are stabilized before broader cleanup.",
            "Zero layer-violation edges remain for L0, L2, L3, and L5 surfaces.",
            protected_violations,
        ),
        _wave(
            "wave_2_remaining_boundary_cleanup",
            "Remaining boundary cleanup",
            "Burn down the rest of the P0 layer-violation inventory after the protected surfaces are clean.",
            "Zero remaining layer-violation edges remain in the canonical snapshot.",
            remaining_violations,
        ),
    ]

    all_issues = circular_imports + dynamic_exec + layer_violations
    summary = {
        "total_p0_issues": len(all_issues),
        "layer_violations": len(layer_violations),
        "circular_imports": len(circular_imports),
        "dynamic_exec": len(dynamic_exec),
        "protected_layer_violations": len(protected_violations),
        "remaining_layer_violations": len(remaining_violations),
    }

    return {
        "schema_version": "1.0",
        "generated_via": "adg_mcp_sqlite",
        "sqlite_path": str(sqlite_path),
        "sqlite_name": sqlite_path.name,
        "plan_required": bool(all_issues),
        "summary": summary,
        "waves": waves,
        "top_files": _aggregate_top_files(all_issues),
    }


def render_p0_remediation_wave_plan(plan: dict[str, Any], ts: str) -> str:
    """Render a markdown wave plan artifact for human triage."""
    summary = plan.get("summary", {})
    lines = [
        f"# ADG P0 Remediation Wave Plan {ts}",
        "",
        f"Source: `{plan.get('sqlite_name', '')}`",
        f"Generated via: `{plan.get('generated_via', 'adg_mcp_sqlite')}`",
        "",
        "## Summary",
        "",
        f"- Total P0 issues: **{summary.get('total_p0_issues', 0)}**",
        f"- Layer violations: **{summary.get('layer_violations', 0)}**",
        f"- Circular imports: **{summary.get('circular_imports', 0)}**",
        f"- Dynamic execution: **{summary.get('dynamic_exec', 0)}**",
        f"- Protected-layer violations: **{summary.get('protected_layer_violations', 0)}**",
        "",
    ]

    if not plan.get("plan_required", False):
        lines.extend(
            [
                "Status: clean. No P0 remediation wave is required for this snapshot.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## Top files by remediation priority",
                "",
                "| Priority | File | Issues | Max fan-in | Kinds |",
                "|---:|---|---:|---:|---|",
            ]
        )
        for index, item in enumerate(plan.get("top_files", []), start=1):
            kinds = ", ".join(item.get("issue_kinds", [])) or "n/a"
            lines.append(
                f"| {index} | `{item.get('source_file', '')}` | {item.get('issue_count', 0)} | {item.get('direct_fan_in_max', 0)} | {kinds} |"
            )
        lines.append("")

        for wave in plan.get("waves", []):
            lines.extend(
                [
                    f"## {wave.get('title', '')}",
                    "",
                    f"- Wave ID: `{wave.get('wave_id', '')}`",
                    f"- Goal: {wave.get('goal', '')}",
                    f"- Exit criteria: {wave.get('exit_criteria', '')}",
                    f"- Items: **{wave.get('item_count', 0)}**",
                    "",
                ]
            )
            items = wave.get("items", [])
            if not items:
                lines.append("No items in this wave.")
                lines.append("")
                continue

            lines.extend(
                [
                    "| File | Line | Type | Fan-in | From -> To |",
                    "|---|---:|---|---:|---|",
                ]
            )
            for item in items[:15]:
                arrow = f"{item.get('from_name', '')} -> {item.get('to_name', '')}".strip()
                lines.append(
                    f"| `{item.get('source_file', '')}` | {item.get('line_no', 0)} | {item.get('issue_type', '')} | {item.get('direct_fan_in', 0)} | {arrow} |"
                )
            if len(items) > 15:
                lines.append(f"| _..._ |  |  |  | {len(items) - 15} more item(s) in JSON artifact |")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def serialize_p0_remediation_wave_plan(plan: dict[str, Any]) -> str:
    """Serialize plan to stable JSON for artifact emission and MCP payload tests."""
    return json.dumps(plan, indent=2, sort_keys=True)
