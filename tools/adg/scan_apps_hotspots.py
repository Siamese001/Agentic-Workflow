"""Bulk ADG hotspot scan across all non-rg apps_* directories.

For each app, query the latest ADG SQLite snapshot to compute:
  - Top engines/agents by fan-in (consumers depending on them)
  - Top engines/agents by fan-out (modules they pull in)
  - Layer-skip violations (if any)
  - Materialized view rows: hotspot centrality, dependency cone risk,
    chokepoint bridges (when present)

Writes one report per app under docs/reports/adg/<app>_hotspots_<ts>.md.

Per Constitutional §28: this is the canonical SQLite-direct fallback,
NOT a grep substitute. We read the same nodes/edges surface the
adg_sqlite MCP exposes; the static bucket is at 100% per current
three-bucket-gap-remediation status.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-{lic,eval,exec,rfp,research,underwriting-ai}-first-principles-refactor-*.md (W0.1)
"""

from __future__ import annotations

# Tool reads ADG SQLite directly; declares its consumer mode.
__adg_consumer_mode__ = "inventory"

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.adg.hotspot_gate_linkage import (
    LinkageContext,
    load_linkage_context,
    resolve_module_linkage,
    top_module_paths_from_scan,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ADG_DIR = REPO_ROOT / "artifacts" / "adg"
REPORTS_DIR = REPO_ROOT / "docs" / "reports" / "adg"

APPS = [
    ("apps_lic", "HIGH (canary surface)"),
    ("apps_eval", "MEDIUM (cross-app judge consumer)"),
    ("apps_exec", "MEDIUM"),
    ("apps_research", "LOW"),
    ("apps_underwriting_ai", "LOW (reference impl)"),
]


def latest_snapshot() -> Path:
    import os

    override = os.environ.get("ADG_SNAPSHOT", "").strip()
    if override:
        p = Path(override)
        if not p.is_absolute():
            p = REPO_ROOT / p
        if not p.exists():
            raise SystemExit(f"ADG_SNAPSHOT not found: {p}")
        return p.resolve()
    candidates = [
        c
        for c in ADG_DIR.glob("adg_indexed_*.sqlite")
        if "99999999" not in c.name and c.stat().st_size > 50_000_000
    ]
    if not candidates:
        raise SystemExit("No ADG snapshot found at artifacts/adg/adg_indexed_*.sqlite")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _table_exists(con: sqlite3.Connection, name: str) -> bool:
    row = con.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def _q(con: sqlite3.Connection, sql: str, params: tuple = ()) -> list[tuple[Any, ...]]:
    try:
        return con.execute(sql, params).fetchall()
    except sqlite3.OperationalError as exc:
        # Surface schema mismatches without crashing the whole scan.
        return [("__error__", str(exc))]


def scan_app(con: sqlite3.Connection, app: str) -> dict[str, Any]:
    """Compute the hotspot dict for one app prefix."""
    out: dict[str, Any] = {"app": app}
    prefix = f"{app}/%"

    # 1) Node count by layer for this app
    layer_rows = _q(
        con,
        """
        SELECT layer, COUNT(*) AS n
        FROM nodes
        WHERE resolved_path LIKE ?
        GROUP BY layer
        ORDER BY n DESC
        """,
        (prefix,),
    )
    out["nodes_by_layer"] = layer_rows

    # 2) Top fan-in: how many incoming `imports` edges land on each app node
    fanin_rows = _q(
        con,
        """
        SELECT n.adg_name, n.resolved_path, COUNT(*) AS fanin
        FROM edges e
        JOIN nodes n ON n.id = e.dst_id
        WHERE n.resolved_path LIKE ?
          AND e.relation_type = 'imports'
        GROUP BY e.dst_id
        ORDER BY fanin DESC
        LIMIT 15
        """,
        (prefix,),
    )
    out["top_fanin"] = fanin_rows

    # 3) Top fan-out: outbound import count per app file
    fanout_rows = _q(
        con,
        """
        SELECT n.adg_name, n.resolved_path, COUNT(*) AS fanout
        FROM edges e
        JOIN nodes n ON n.id = e.src_id
        WHERE n.resolved_path LIKE ?
          AND e.relation_type = 'imports'
        GROUP BY e.src_id
        ORDER BY fanout DESC
        LIMIT 15
        """,
        (prefix,),
    )
    out["top_fanout"] = fanout_rows

    # 4) Engines + reasoning agents — file count signal
    eng_rows = _q(
        con,
        """
        SELECT resolved_path
        FROM nodes
        WHERE resolved_path LIKE ?
          AND (resolved_path LIKE '%/engines/%' OR resolved_path LIKE '%/reasoning/%')
        ORDER BY resolved_path
        """,
        (prefix,),
    )
    out["engines_and_agents"] = eng_rows

    # 5) Materialized view hits: hotspot centrality (if present)
    if _table_exists(con, "mv_hotspot_centrality"):
        mv_hot = _q(
            con,
            """
            SELECT *
            FROM mv_hotspot_centrality m
            JOIN nodes n ON n.id = m.node_id
            WHERE n.resolved_path LIKE ?
            LIMIT 10
            """,
            (prefix,),
        )
        out["mv_hotspot_centrality"] = mv_hot
    else:
        out["mv_hotspot_centrality"] = None

    # 6) Dependency cone risk
    if _table_exists(con, "mv_dependency_cone_risk"):
        mv_cone = _q(
            con,
            """
            SELECT *
            FROM mv_dependency_cone_risk m
            JOIN nodes n ON n.id = m.node_id
            WHERE n.resolved_path LIKE ?
            LIMIT 10
            """,
            (prefix,),
        )
        out["mv_dependency_cone_risk"] = mv_cone
    else:
        out["mv_dependency_cone_risk"] = None

    # 7) Chokepoint bridges
    if _table_exists(con, "mv_chokepoint_bridges"):
        mv_choke = _q(
            con,
            """
            SELECT *
            FROM mv_chokepoint_bridges m
            JOIN nodes n ON n.id = m.node_id
            WHERE n.resolved_path LIKE ?
            LIMIT 10
            """,
            (prefix,),
        )
        out["mv_chokepoint_bridges"] = mv_choke
    else:
        out["mv_chokepoint_bridges"] = None

    # 8) P-view hits — apps directly importing infra would be flagged
    if _table_exists(con, "v_p0_apps_direct_infra"):
        p0 = _q(
            con,
            """
            SELECT * FROM v_p0_apps_direct_infra
            WHERE source_file LIKE ?
            LIMIT 20
            """,
            (prefix,),
        )
        out["v_p0_apps_direct_infra"] = p0
    else:
        out["v_p0_apps_direct_infra"] = None

    # 9) Violations (any P0/P1 SC/AP for this app)
    if _table_exists(con, "violations"):
        viol = _q(
            con,
            """
            SELECT severity, violation_class, file_path, line_no, category
            FROM violations
            WHERE file_path LIKE ?
            ORDER BY severity, file_path
            LIMIT 30
            """,
            (prefix,),
        )
        out["violations"] = viol
    else:
        out["violations"] = None

    return out


def render_actionable_hotspots(
    scan: dict[str, Any],
    linkage_ctx: LinkageContext,
    *,
    limit: int = 5,
) -> list[str]:
    """Markdown lines for top-N modules with deterministic gate linkage."""
    lines: list[str] = []
    lines.append("## Actionable hotspots (top 5 — deterministic linkage)")
    lines.append("")
    lines.append(
        "Linkage from structured sources only (`gate_results` queue file paths, "
        "P-views, `mv_debt_concentration_hotspots`, `refactor_accelerator`). "
        "`unknown` = no gate join."
    )
    lines.append("")
    lines.append(
        "| module_path | linked_gate_ids | violation_refs | impacted_tests_sample | "
        "linkage_source | linkage_confidence |"
    )
    lines.append(
        "|-------------|-----------------|----------------|----------------------|"
        "----------------|-------------------|"
    )
    modules = top_module_paths_from_scan(scan, limit=limit)
    if not modules:
        lines.append("| _none_ | | | | unknown | missing |")
        lines.append("")
        return lines

    for mod in modules:
        link = resolve_module_linkage(mod, linkage_ctx)
        gates = ", ".join(f"`{g}`" for g in link.linked_gate_ids) if link.linked_gate_ids else "—"
        vrefs = ", ".join(link.violation_refs[:3]) if link.violation_refs else "—"
        if len(link.violation_refs) > 3:
            vrefs += f" (+{len(link.violation_refs) - 3})"
        tests = ", ".join(f"`{t}`" for t in link.impacted_tests_sample[:2]) if link.impacted_tests_sample else "—"
        lines.append(
            f"| `{link.module_path}` | {gates} | {vrefs} | {tests} | "
            f"{link.linkage_source} | {link.linkage_confidence} |"
        )
    lines.append("")
    return lines


def render_md(
    scan: dict[str, Any],
    severity: str,
    snapshot: Path,
    linkage_ctx: LinkageContext | None = None,
) -> str:
    app = scan["app"]
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: list[str] = []
    lines.append(f"# `{app}` — ADG Hotspot Report (W0.1)")
    lines.append("")
    lines.append(f"Generated: `{ts}`")
    lines.append(f"Snapshot: `{snapshot.name}`")
    lines.append(f"Severity (Phase B): **{severity}**")
    lines.append(f"ADG Provenance: backend=sqlite, snapshot={snapshot.name}")
    lines.append("")
    if linkage_ctx is not None:
        lines.extend(render_actionable_hotspots(scan, linkage_ctx))
    lines.append("## Nodes by Layer")
    lines.append("")
    lines.append("| Layer | Count |")
    lines.append("|---|---:|")
    for row in scan["nodes_by_layer"]:
        if row and row[0] != "__error__":
            lines.append(f"| {row[0]} | {row[1]} |")
    lines.append("")

    lines.append("## Top Fan-In (incoming imports — most-depended-on files)")
    lines.append("")
    lines.append("| ADG name | Resolved path | Fan-in |")
    lines.append("|---|---|---:|")
    for row in scan["top_fanin"][:15]:
        if row and row[0] != "__error__":
            lines.append(f"| `{row[0]}` | `{row[1]}` | {row[2]} |")
    lines.append("")

    lines.append("## Top Fan-Out (outgoing imports — broadest reachers)")
    lines.append("")
    lines.append("| ADG name | Resolved path | Fan-out |")
    lines.append("|---|---|---:|")
    for row in scan["top_fanout"][:15]:
        if row and row[0] != "__error__":
            lines.append(f"| `{row[0]}` | `{row[1]}` | {row[2]} |")
    lines.append("")

    lines.append("## Engines + Reasoning Agents")
    lines.append("")
    lines.append(f"Total files under `engines/` + `reasoning/`: **{len(scan['engines_and_agents'])}**")
    lines.append("")
    for r in scan["engines_and_agents"][:30]:
        if r and r[0] != "__error__":
            lines.append(f"- `{r[0]}`")
    if len(scan["engines_and_agents"]) > 30:
        lines.append(f"- ... +{len(scan['engines_and_agents']) - 30} more")
    lines.append("")

    for mv_name, key in (
        ("mv_hotspot_centrality", "mv_hotspot_centrality"),
        ("mv_dependency_cone_risk", "mv_dependency_cone_risk"),
        ("mv_chokepoint_bridges", "mv_chokepoint_bridges"),
    ):
        v = scan.get(key)
        if v is None:
            lines.append(f"## {mv_name}")
            lines.append("")
            lines.append("_view not present in this snapshot_")
            lines.append("")
            continue
        lines.append(f"## {mv_name} (top 10 within app)")
        lines.append("")
        if not v:
            lines.append("_no rows for this app_")
        else:
            lines.append(f"Rows: {len(v)}")
            for row in v[:10]:
                lines.append(f"- {row}")
        lines.append("")

    p0 = scan.get("v_p0_apps_direct_infra")
    lines.append("## v_p0_apps_direct_infra (P0 violation — apps directly importing infra)")
    lines.append("")
    if p0 is None:
        lines.append("_view not present in this snapshot_")
    elif not p0:
        lines.append("_no P0 direct-infra violations for this app — clean_")
    else:
        lines.append(f"Rows: {len(p0)}")
        for row in p0[:20]:
            lines.append(f"- {row}")
    lines.append("")

    viol = scan.get("violations")
    lines.append("## SC/AP Violations (top 30 by severity)")
    lines.append("")
    if viol is None:
        lines.append("_violations table not present in this snapshot_")
    elif not viol:
        lines.append("_no violations for this app_")
    else:
        lines.append(f"Rows: {len(viol)}")
        lines.append("")
        lines.append("| Severity | Class | File | Line | Category |")
        lines.append("|---|---|---|---:|---|")
        for row in viol[:30]:
            if row and row[0] != "__error__":
                lines.append(
                    f"| {row[0]} | {row[1]} | `{row[2]}` | {row[3] or ''} | {(row[4] or '')[:80]} |"
                )
    lines.append("")
    lines.append(
        "See [adg_action_dispatch_playbook.md](../../docs/reports/cursor/adg_action_dispatch_playbook.md) "
        "and latest `artifacts/adg/adg_action_queue_*.json` for FIX-first triage."
    )
    lines.append("")

    lines.append("## Recommendations (derived)")
    lines.append("")
    fanin_top = [r for r in scan["top_fanin"] if r and r[0] != "__error__"][:5]
    fanout_top = [r for r in scan["top_fanout"] if r and r[0] != "__error__"][:5]
    if fanin_top:
        lines.append("- **Most-depended-on files (highest blast radius if changed):**")
        for r in fanin_top:
            lines.append(f"  - `{r[1]}` (fan-in {r[2]}) — touch only with explicit Author-Gate")
    if fanout_top:
        lines.append("- **Broadest reachers (most likely to consolidate):**")
        for r in fanout_top:
            lines.append(f"  - `{r[1]}` (fan-out {r[2]})")
    lines.append("")
    lines.append("## Out of Scope (this report)")
    lines.append("")
    lines.append("- Runtime evidence (Runtime bucket gated on three-bucket completion)")
    lines.append("- Cross-app comparative analysis (see Phase B comparative audit in conversation)")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    snapshot = latest_snapshot()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"[adg_scan] snapshot = {snapshot.name}")
    con = sqlite3.connect(str(snapshot))
    linkage_ctx = load_linkage_context(sqlite_connection=con)
    try:
        for app, severity in APPS:
            print(f"[adg_scan] scanning {app} ...", end=" ", flush=True)
            scan = scan_app(con, app)
            md = render_md(scan, severity, snapshot, linkage_ctx=linkage_ctx)
            out_path = REPORTS_DIR / f"{app}_hotspots_{ts}.md"
            out_path.write_text(md, encoding="utf-8")
            n_files = len(scan["engines_and_agents"])
            n_fanin = len([r for r in scan["top_fanin"] if r and r[0] != "__error__"])
            n_viol = len(scan.get("violations") or [])
            print(f"engines+agents={n_files} top_fanin={n_fanin} violations={n_viol}")
            print(f"           -> {out_path.relative_to(REPO_ROOT)}")
    finally:
        con.close()

    print("[adg_scan] done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
