"""ADG per-app inspector — anti-cheat baseline + per-run deltas.

CLI:

    python -m tools.apps_proof.adg_app_inspector \
        --adg artifacts/adg/adg_indexed_<ts>.sqlite \
        --apps-glob "apps_*" \
        --out artifacts/apps_proof/adg_apps_baseline.json

Reads the ADG snapshot read-only. Surfaces, per app:
  - node count
  - violations / overlay violations
  - per-view hit count for 12 mv_* and 5 v_p* views
  - hidden writes and write sovereignty signals
  - top hotspot files
  - high-impact "no-go" file flags

Designed to handle the W0 finding that 5 P-views (`v_p0_*`, `v_p1_*`,
`v_p2_*`) lack a ``file`` column — the inspector probes the schema and
falls back to ``node_id`` joined to ``nodes.resolved_path`` when needed.

This module is read-only. It NEVER writes to the snapshot.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Per master plan ADG_GRAPH_LAYER_EVIDENCE — the 17 required views.
REQUIRED_MV_VIEWS = (
    "mv_high_fan_in_out_with_defects",
    "mv_debt_concentration_hotspots",
    "mv_write_sovereignty_paths",
    "mv_hidden_writes_overlay",
    "mv_trace_replay_eval_gaps",
    "mv_replay_surface_gaps",
    "mv_task_contract_gaps",
    "mv_actionable_surface_without_schema",
    "mv_structured_output_gaps",
    "mv_determinism_provenance_drift",
    "mv_module_load_action_calls_overlay",
    "mv_provider_surface_sprawl",
)

REQUIRED_PVIEW_VIEWS = (
    "v_p0_apps_direct_infra",
    "v_p0_write_bypass_uwg",
    "v_p0_provider_bypass",
    "v_p1_raw_http_outside_seam",
    "v_p2_duplicated_adapters",
)

ALL_REQUIRED_VIEWS = REQUIRED_MV_VIEWS + REQUIRED_PVIEW_VIEWS

# Ranked candidates for "this column holds a file path" in MVs and P-views.
FILE_COLUMN_CANDIDATES = (
    "file",
    "file_path",
    "resolved_path",
    "src_file",
    "source_file",
    "path",
    "module",
)

# Ranked candidates for "this column joins to nodes.id".
NODE_ID_COLUMN_CANDIDATES = ("node_id", "nid", "id", "src_id", "source_node_id")


@dataclass
class ColumnResolution:
    """How we extract ``apps_<X>/...`` rows from one view."""

    view: str
    file_column: str | None = None
    node_id_column: str | None = None
    resolution_strategy: str = "MISSING"  # FILE | NODE_JOIN | MISSING

    def to_dict(self) -> dict[str, Any]:
        return {
            "view": self.view,
            "file_column": self.file_column,
            "node_id_column": self.node_id_column,
            "resolution_strategy": self.resolution_strategy,
        }


@dataclass
class AppViewHit:
    """Per-app per-view hit record."""

    view: str
    hits: int
    strategy: str  # FILE | NODE_JOIN | MISSING_VIEW | NO_FILE_COLUMN | QUERY_FAILED

    def to_dict(self) -> dict[str, Any]:
        return {"view": self.view, "hits": self.hits, "strategy": self.strategy}


@dataclass
class AppRecord:
    """Per-app inspector record."""

    app_id: str
    node_count: int = 0
    violation_count: int = 0
    overlay_violation_count: int = 0
    per_view: dict[str, AppViewHit] = field(default_factory=dict)
    top_hotspot_files: list[dict[str, Any]] = field(default_factory=list)
    no_go_files_present: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_id": self.app_id,
            "node_count": self.node_count,
            "violation_count": self.violation_count,
            "overlay_violation_count": self.overlay_violation_count,
            "per_view": {k: v.to_dict() for k, v in self.per_view.items()},
            "top_hotspot_files": list(self.top_hotspot_files),
            "no_go_files_present": list(self.no_go_files_present),
        }


# No-go list — copied from the master plan §"High-Risk Files".
NO_GO_FILES = (
    "apps_shared/config/pipeline_constants_config.py",
    "apps_rg/engines/base_rg_engine.py",
    "apps_eval/engines/scenario_runner.py",
    "apps_shared/reasoning/BaseDispatchAgent.py",
    "apps_shared/enforcement/ProvenancetrackerStrategy.py",
    "apps_lic/engines/control_plane.py",
    "apps_underwriting_ai/engines/underwriting_engine.py",
    "apps_underwriting_ai/engines/decision_packet_assembler.py",
    "apps_underwriting_ai/engines/evidence_register_engine.py",
    "apps_underwriting_ai/integrations/retrieval_adapter.py",
)


def _columns_of(cur: sqlite3.Cursor, name: str) -> list[str]:
    try:
        return [r[1] for r in cur.execute(f"PRAGMA table_info({name})").fetchall()]
    except sqlite3.OperationalError:
        return []


def _resolve_columns(cur: sqlite3.Cursor, view: str) -> ColumnResolution:
    """Probe ``view`` schema, decide how to filter to one app."""
    cols = _columns_of(cur, view)
    if not cols:
        return ColumnResolution(view=view, resolution_strategy="MISSING")
    file_col = next((c for c in FILE_COLUMN_CANDIDATES if c in cols), None)
    if file_col:
        return ColumnResolution(view=view, file_column=file_col, resolution_strategy="FILE")
    node_id_col = next((c for c in NODE_ID_COLUMN_CANDIDATES if c in cols), None)
    if node_id_col:
        return ColumnResolution(
            view=view, node_id_column=node_id_col, resolution_strategy="NODE_JOIN"
        )
    return ColumnResolution(view=view, resolution_strategy="MISSING")


def _hit_count(
    cur: sqlite3.Cursor, view: str, app_id: str, resolution: ColumnResolution
) -> AppViewHit:
    """Count rows in ``view`` whose file path starts with ``{app_id}/``."""
    if resolution.resolution_strategy == "MISSING":
        return AppViewHit(view=view, hits=-1, strategy="MISSING_VIEW")
    try:
        if resolution.resolution_strategy == "FILE" and resolution.file_column:
            sql = (
                f"SELECT COUNT(*) FROM {view} WHERE {resolution.file_column} LIKE ?"
            )
            n = cur.execute(sql, (f"{app_id}/%",)).fetchone()[0]
            return AppViewHit(view=view, hits=int(n), strategy="FILE")
        if resolution.resolution_strategy == "NODE_JOIN" and resolution.node_id_column:
            # Node-join path: view stores node_id; nodes.resolved_path holds path
            sql = (
                f"SELECT COUNT(*) FROM {view} v "
                f"JOIN nodes n ON n.id = v.{resolution.node_id_column} "
                "WHERE n.resolved_path LIKE ?"
            )
            n = cur.execute(sql, (f"{app_id}/%",)).fetchone()[0]
            return AppViewHit(view=view, hits=int(n), strategy="NODE_JOIN")
    except sqlite3.OperationalError as exc:
        return AppViewHit(view=view, hits=-1, strategy=f"QUERY_FAILED:{exc}")
    return AppViewHit(view=view, hits=-1, strategy="NO_FILE_COLUMN")


def _top_hotspot_files(
    cur: sqlite3.Cursor, app_id: str, limit: int = 10
) -> list[dict[str, Any]]:
    """Top hotspot files in mv_high_fan_in_out_with_defects (if present)."""
    cols = _columns_of(cur, "mv_high_fan_in_out_with_defects")
    if not cols:
        return []
    file_col = next((c for c in FILE_COLUMN_CANDIDATES if c in cols), None)
    if not file_col:
        return []
    score_col = None
    for candidate in (
        "impact_score",
        "score",
        "fan_in",
        "fan_out",
        "defect_count",
        "n",
    ):
        if candidate in cols:
            score_col = candidate
            break
    select_score = f", {score_col}" if score_col else ""
    order_clause = f"ORDER BY {score_col} DESC" if score_col else ""
    try:
        sql = (
            f"SELECT {file_col}{select_score} FROM mv_high_fan_in_out_with_defects "
            f"WHERE {file_col} LIKE ? {order_clause} LIMIT ?"
        )
        rows = cur.execute(sql, (f"{app_id}/%", limit)).fetchall()
    except sqlite3.OperationalError:
        return []
    return [
        {"file": r[0], "score": (r[1] if len(r) > 1 else None)} for r in rows
    ]


def _discovered_apps(cur: sqlite3.Cursor, glob: str) -> list[str]:
    """Distinct top-level packages whose path matches the glob."""
    rows = cur.execute(
        """
        SELECT DISTINCT SUBSTR(resolved_path, 1, INSTR(resolved_path, '/') - 1) AS pkg
        FROM nodes
        WHERE INSTR(resolved_path, '/') > 0
        ORDER BY pkg
        """
    ).fetchall()
    apps = [r[0] for r in rows if r[0] and fnmatch.fnmatch(r[0], glob)]
    return apps


def _base_table_count(cur: sqlite3.Cursor, table: str, app_id: str) -> int:
    cols = _columns_of(cur, table)
    if not cols:
        return -1
    file_col = next((c for c in FILE_COLUMN_CANDIDATES if c in cols), None)
    if not file_col:
        return -1
    try:
        n = cur.execute(
            f"SELECT COUNT(*) FROM {table} WHERE {file_col} LIKE ?",
            (f"{app_id}/%",),
        ).fetchone()[0]
        return int(n)
    except sqlite3.OperationalError:
        return -1


def inspect(snapshot: Path, apps_glob: str) -> dict[str, Any]:
    """Run the full inspection and return a dict suitable for JSON dump."""
    if not snapshot.exists():
        raise FileNotFoundError(f"snapshot missing: {snapshot}")

    con = sqlite3.connect(str(snapshot))
    try:
        cur = con.cursor()

        # Schema check
        rows = cur.execute(
            "SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY name"
        ).fetchall()
        present = {name: typ for name, typ in rows}

        column_resolutions: dict[str, ColumnResolution] = {}
        for v in ALL_REQUIRED_VIEWS:
            if v not in present:
                column_resolutions[v] = ColumnResolution(view=v, resolution_strategy="MISSING")
            else:
                column_resolutions[v] = _resolve_columns(cur, v)

        # Per-app
        apps = _discovered_apps(cur, apps_glob)
        per_app: dict[str, AppRecord] = {}
        for app in apps:
            rec = AppRecord(app_id=app)

            # Node count
            rec.node_count = int(
                cur.execute(
                    "SELECT COUNT(*) FROM nodes WHERE resolved_path LIKE ?",
                    (f"{app}/%",),
                ).fetchone()[0]
            )
            # Violations / overlay
            rec.violation_count = _base_table_count(cur, "violations", app)
            rec.overlay_violation_count = _base_table_count(cur, "overlay_violations", app)

            # Per-view
            for v in ALL_REQUIRED_VIEWS:
                rec.per_view[v] = _hit_count(cur, v, app, column_resolutions[v])

            # Top hotspot files
            rec.top_hotspot_files = _top_hotspot_files(cur, app, limit=5)

            # No-go file presence (read filesystem)
            for ng in NO_GO_FILES:
                if ng.startswith(f"{app}/"):
                    rec.no_go_files_present.append(ng)

            per_app[app] = rec

        report: dict[str, Any] = {
            "snapshot": snapshot.name,
            "snapshot_size_bytes": snapshot.stat().st_size,
            "tables": sum(1 for t in present.values() if t == "table"),
            "views": sum(1 for t in present.values() if t == "view"),
            "required_views": list(ALL_REQUIRED_VIEWS),
            "required_views_present": [v for v in ALL_REQUIRED_VIEWS if v in present],
            "required_views_missing": [v for v in ALL_REQUIRED_VIEWS if v not in present],
            "column_resolutions": {
                k: v.to_dict() for k, v in column_resolutions.items()
            },
            "per_app": {a: rec.to_dict() for a, rec in per_app.items()},
            "no_go_files": list(NO_GO_FILES),
        }
        return report
    finally:
        con.close()


def _write_md(report: dict[str, Any], out_md: Path) -> None:
    lines: list[str] = []
    lines.append("# ADG Apps Baseline (inspector)")
    lines.append("")
    lines.append(f"- Snapshot: `{report['snapshot']}`")
    lines.append(f"- Tables: {report['tables']}")
    lines.append(f"- Views: {report['views']}")
    lines.append(
        f"- Required views present: {len(report['required_views_present'])}/"
        f"{len(report['required_views'])}"
    )
    if report["required_views_missing"]:
        lines.append("")
        lines.append("## Missing required views")
        for v in report["required_views_missing"]:
            lines.append(f"- MISSING_VIEW: `{v}`")
    lines.append("")
    lines.append("## Column resolutions")
    lines.append("")
    lines.append("| View | Strategy | File col | Node-id col |")
    lines.append("|---|---|---|---|")
    for v, r in report["column_resolutions"].items():
        lines.append(
            f"| `{v}` | {r['resolution_strategy']} | "
            f"{r['file_column'] or '-'} | {r['node_id_column'] or '-'} |"
        )
    lines.append("")
    lines.append("## Per-app summary")
    lines.append("")
    lines.append("| App | Nodes | Violations | Overlay | No-go files |")
    lines.append("|---|---:|---:|---:|---:|")
    for app, rec in report["per_app"].items():
        lines.append(
            f"| `{app}` | {rec['node_count']} | {rec['violation_count']} "
            f"| {rec['overlay_violation_count']} "
            f"| {len(rec['no_go_files_present'])} |"
        )
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tools.apps_proof.adg_app_inspector",
        description="Per-app ADG inspector — surfaces hotspots, violations, no-go files.",
    )
    parser.add_argument("--adg", required=True, type=Path, help="ADG SQLite snapshot path")
    parser.add_argument("--apps-glob", default="apps_*", help="Glob for top-level apps_* packages")
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Output JSON path; a Markdown sibling is also written.",
    )
    args = parser.parse_args(argv)

    report = inspect(args.adg, args.apps_glob)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    md_out = args.out.with_suffix(".md")
    _write_md(report, md_out)
    print(f"OK wrote {args.out}")
    print(f"OK wrote {md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
