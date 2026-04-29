"""Three-Bucket Gap Report — review all three ADG graphs together.

Runs the full 7-defect-class reconciliation across the three buckets
(static / runtime / registry) of the ADG, against the latest snapshot
under artifacts/adg/adg_indexed_*.sqlite.

Defect classes (set algebra over (src,dst,relation)):

    | static | runtime | registry | class               |
    |  ---   |  ---    |  ---     | ---                 |
    |   1    |    1    |    1     | TRIPLET_ATTESTED    | ← gold standard
    |   1    |    1    |    0     | REGISTRY_DRIFT      | ← undocumented coupling
    |   1    |    0    |    1     | DEAD_PATH           | ← untested wiring
    |   1    |    0    |    0     | UNOBSERVED_CODE     | ← orphan / never-traced
    |   0    |    1    |    1     | DYNAMIC_DISPATCH    | ← plugin / DI (good)
    |   0    |    1    |    0     | SHADOW_CHANNEL      | ⚠ SECURITY
    |   0    |    0    |    1     | CONFIG_BLOAT        | ← dead policy

Usage:
    python tools/adg/three_bucket_gap_report.py [--snapshot PATH]
                                                 [--top-n N]
                                                 [--out PATH]
                                                 [--format json|md|both]

Outputs (default):
    docs/reports/adg/THREE_BUCKET_GAP_REPORT.json
    docs/reports/adg/THREE_BUCKET_GAP_REPORT.md
"""

from __future__ import annotations

# W6 ADG consumer mode declaration — this is an inventory/reporting tool.
__adg_consumer_mode__ = "inventory"

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_DIR = REPO_ROOT / "docs" / "reports" / "adg"

DEFECT_CLASSES = [
    "TRIPLET_ATTESTED",
    "REGISTRY_DRIFT",
    "DEAD_PATH",
    "UNOBSERVED_CODE",
    "DYNAMIC_DISPATCH",
    "SHADOW_CHANNEL",
    "CONFIG_BLOAT",
]

DEFECT_DESCRIPTIONS = {
    "TRIPLET_ATTESTED": "Edge present in all three graphs — fully proven. NOT a defect.",
    "REGISTRY_DRIFT": "Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API.",
    "DEAD_PATH": "Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy.",
    "UNOBSERVED_CODE": "Static-only — orphan import, dead code, or never-traced path.",
    "DYNAMIC_DISPATCH": "No static link, but declared + verified at runtime. Plugin / DI / lazy import — usually fine.",
    "SHADOW_CHANNEL": "Runtime-only undeclared edge — monkey-patch, side-effect coupling, hidden import. SECURITY-CRITICAL.",
    "CONFIG_BLOAT": "Declared in registry but never used in code or runtime. Dead policy / config drift.",
}

DEFECT_SEVERITY = {
    # P-band assignment (P1 highest):
    "SHADOW_CHANNEL": "P1",       # security-critical
    "REGISTRY_DRIFT": "P2",       # undocumented coupling
    "DEAD_PATH": "P3",            # untested wiring
    "UNOBSERVED_CODE": "P3",      # orphan / dead code
    "CONFIG_BLOAT": "P4",         # dead policy
    "DYNAMIC_DISPATCH": "P5",     # informational — usually intentional
    "TRIPLET_ATTESTED": "—",      # not a defect
}


def _latest_snapshot() -> Path:
    snaps = sorted((REPO_ROOT / "artifacts" / "adg").glob("adg_indexed_*.sqlite"))
    if not snaps:
        print("ERROR: no ADG snapshot found at artifacts/adg/adg_indexed_*.sqlite", file=sys.stderr)
        sys.exit(2)
    return snaps[-1]


def _has_runtime_view(con: sqlite3.Connection) -> bool:
    row = con.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name='v_runtime_proof'"
    ).fetchone()
    return row is not None


def _detect_bucket_column(con: sqlite3.Connection) -> str | None:
    """Return name of the bucket column on `edges`, or None if absent."""
    cols = [r[1] for r in con.execute("PRAGMA table_info(edges)").fetchall()]
    for cand in ("bucket", "graph_bucket", "authority_bucket"):
        if cand in cols:
            return cand
    return None


def _legacy_bucket_projection(con: sqlite3.Connection) -> dict[str, str]:
    """Map legacy `authority` values to bucket {static, runtime, registry}.

    Returns SQL CASE expression as a string keyed by 'expr'.
    """
    # See tools/adg/audit_three_bucket_counts.py mapping table.
    return {
        "expr": (
            "CASE "
            "WHEN authority IN ('verified','unresolved','dynamic','external','test_only') THEN 'static' "
            "WHEN authority IN ('runtime_observed') THEN 'runtime' "
            "WHEN authority IN ('registry') THEN 'registry' "
            "ELSE 'static' "  # default — most edges are AST-derived
            "END"
        )
    }


def _classify_query(con: sqlite3.Connection) -> str:
    """Build the master gap-class query against whichever schema is present."""
    has_runtime = _has_runtime_view(con)
    bucket_col = _detect_bucket_column(con)

    if bucket_col:
        bucket_expr = f"e.{bucket_col}"
    else:
        bucket_expr = _legacy_bucket_projection(con)["expr"]

    runtime_join = ""
    runtime_present_col = "0 AS in_runtime"
    if has_runtime:
        # v_runtime_proof exposes static_edge_id (FK to edges.id) — clean
        # 1:1 join, no name-resolution needed. Falls back to a name-based
        # join if static_edge_id is NULL/unset on a row.
        runtime_join = (
            "LEFT JOIN ("
            "  SELECT static_edge_id, 1 AS rt FROM v_runtime_proof "
            "  WHERE attesting_trace_count >= 1 AND static_edge_id IS NOT NULL"
            ") rt ON rt.static_edge_id = e.id "
        )
        runtime_present_col = "MAX(COALESCE(rt.rt,0)) AS in_runtime"

    return f"""
    WITH per_edge AS (
        SELECT
            e.src_id, e.dst_id, e.relation_type,
            MAX(CASE WHEN {bucket_expr} = 'static'   THEN 1 ELSE 0 END) AS in_static,
            MAX(CASE WHEN {bucket_expr} = 'registry' THEN 1 ELSE 0 END) AS in_registry,
            {runtime_present_col}
        FROM edges e
        {runtime_join}
        GROUP BY e.src_id, e.dst_id, e.relation_type
    )
    SELECT
        CASE
            WHEN in_static=1 AND in_runtime=1 AND in_registry=1 THEN 'TRIPLET_ATTESTED'
            WHEN in_static=1 AND in_runtime=1 AND in_registry=0 THEN 'REGISTRY_DRIFT'
            WHEN in_static=1 AND in_runtime=0 AND in_registry=1 THEN 'DEAD_PATH'
            WHEN in_static=1 AND in_runtime=0 AND in_registry=0 THEN 'UNOBSERVED_CODE'
            WHEN in_static=0 AND in_runtime=1 AND in_registry=1 THEN 'DYNAMIC_DISPATCH'
            WHEN in_static=0 AND in_runtime=1 AND in_registry=0 THEN 'SHADOW_CHANNEL'
            WHEN in_static=0 AND in_runtime=0 AND in_registry=1 THEN 'CONFIG_BLOAT'
        END AS defect_class,
        src_id, dst_id, relation_type
    FROM per_edge
    """


def _resolve_node_path(con: sqlite3.Connection, node_id: int) -> str:
    """Return resolved path / module name for a node id, fail-soft."""
    try:
        row = con.execute(
            "SELECT COALESCE(resolved_path, file_path, adg_name, '<unknown>') FROM nodes WHERE id=?",
            (node_id,),
        ).fetchone()
        return row[0] if row else f"<id={node_id}>"
    except sqlite3.Error:
        return f"<id={node_id}>"


def run_report(snapshot: Path, top_n: int) -> dict[str, Any]:
    con = sqlite3.connect(str(snapshot))
    con.row_factory = sqlite3.Row

    has_runtime = _has_runtime_view(con)
    runtime_total = 0
    if has_runtime:
        try:
            runtime_total = con.execute(
                "SELECT COUNT(*) FROM v_runtime_proof WHERE attesting_trace_count >= 1"
            ).fetchone()[0]
        except sqlite3.Error:
            runtime_total = 0

    rows = list(con.execute(_classify_query(con)).fetchall())

    by_class: dict[str, list[sqlite3.Row]] = {c: [] for c in DEFECT_CLASSES}
    for r in rows:
        cls = r["defect_class"]
        if cls in by_class:
            by_class[cls].append(r)

    summary = []
    samples: dict[str, list[dict[str, Any]]] = {}
    total_edges = sum(len(v) for v in by_class.values())
    for cls in DEFECT_CLASSES:
        n = len(by_class[cls])
        pct = (100.0 * n / total_edges) if total_edges else 0.0
        summary.append(
            {
                "defect_class": cls,
                "severity": DEFECT_SEVERITY[cls],
                "edge_count": n,
                "edge_pct": round(pct, 2),
                "description": DEFECT_DESCRIPTIONS[cls],
            }
        )
        # Top-N samples (skip TRIPLET_ATTESTED — not a defect).
        if cls == "TRIPLET_ATTESTED":
            samples[cls] = []
            continue
        sample_rows = by_class[cls][:top_n]
        samples[cls] = [
            {
                "src": _resolve_node_path(con, r["src_id"]),
                "dst": _resolve_node_path(con, r["dst_id"]),
                "relation": r["relation_type"],
            }
            for r in sample_rows
        ]

    health_score = (
        round(100.0 * len(by_class["TRIPLET_ATTESTED"]) / total_edges, 2)
        if total_edges
        else 0.0
    )

    con.close()
    return {
        "report_kind": "ADG_THREE_BUCKET_GAP_REPORT",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "snapshot": snapshot.name,
        "snapshot_path": str(snapshot.relative_to(REPO_ROOT)),
        "runtime_view_present": has_runtime,
        "runtime_attested_edges": runtime_total,
        "total_edges_classified": total_edges,
        "health_score_pct_triplet_attested": health_score,
        "summary_by_class": summary,
        "samples_by_class": samples,
        "static_only_classes": [
            "REGISTRY_DRIFT",
            "CONFIG_BLOAT",
            # UNOBSERVED_CODE — answerable static-only via zero-caller MVs
            # but the version we compute here uses runtime=0 condition.
        ],
        "requires_runtime_classes": [
            "TRIPLET_ATTESTED",
            "DEAD_PATH",
            "DYNAMIC_DISPATCH",
            "SHADOW_CHANNEL",
            "UNOBSERVED_CODE",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append("# ADG Three-Bucket Gap Report")
    lines.append("")
    lines.append(f"- **Generated**: {report['generated_at']}")
    lines.append(f"- **Snapshot**: `{report['snapshot']}`")
    lines.append(f"- **Runtime view present**: {report['runtime_view_present']}")
    lines.append(f"- **Runtime-attested edges**: {report['runtime_attested_edges']:,}")
    lines.append(f"- **Total edges classified**: {report['total_edges_classified']:,}")
    lines.append(
        f"- **Health score** (triplet-attested fraction): "
        f"**{report['health_score_pct_triplet_attested']}%**"
    )
    lines.append("")
    if not report["runtime_view_present"]:
        lines.append(
            "> **Caveat**: This snapshot predates the W1 `v_runtime_proof` schema "
            "addition OR no OTel traces have been emitted yet. The runtime bucket "
            "is treated as empty, so all edges fall into static-only classes "
            "(`UNOBSERVED_CODE` / `REGISTRY_DRIFT` / `CONFIG_BLOAT`). To produce "
            "the full triplet matrix, regenerate the ADG snapshot via "
            "`python tools/generate/generate_full_adg.py` against a runtime store "
            "with attested OTel spans."
        )
        lines.append("")
    if report["runtime_attested_edges"] == 0 and report["runtime_view_present"]:
        lines.append(
            "> **Caveat**: `v_runtime_proof` exists but contains zero attested "
            "edges. The runtime bucket is empty — populate the OTel "
            "`runtime_adg_store` (e.g., run pytest with OTel exporters) and "
            "regenerate the snapshot to surface `TRIPLET_ATTESTED`, "
            "`SHADOW_CHANNEL`, and `DYNAMIC_DISPATCH` rows."
        )
        lines.append("")
    lines.append("")
    lines.append("## Defect distribution")
    lines.append("")
    lines.append("| Severity | Class | Edges | % | Description |")
    lines.append("|---|---|---:|---:|---|")
    for row in report["summary_by_class"]:
        lines.append(
            f"| {row['severity']} | **{row['defect_class']}** | "
            f"{row['edge_count']:,} | {row['edge_pct']}% | {row['description']} |"
        )
    lines.append("")
    lines.append("## Static-only vs runtime-required")
    lines.append("")
    lines.append(
        "**Static-only** (answerable without OTEL traces — pure registry-vs-static set diff): "
        + ", ".join(f"`{c}`" for c in report["static_only_classes"])
    )
    lines.append("")
    lines.append(
        "**Requires runtime traces** (need OTEL span evidence to classify correctly): "
        + ", ".join(f"`{c}`" for c in report["requires_runtime_classes"])
    )
    lines.append("")
    lines.append("## Top samples per class")
    lines.append("")
    for cls in DEFECT_CLASSES:
        if cls == "TRIPLET_ATTESTED":
            continue
        sams = report["samples_by_class"].get(cls, [])
        if not sams:
            continue
        lines.append(f"### {cls}  (severity {DEFECT_SEVERITY[cls]})")
        lines.append("")
        lines.append("| src | dst | relation |")
        lines.append("|---|---|---|")
        for s in sams:
            lines.append(f"| `{s['src']}` | `{s['dst']}` | `{s['relation']}` |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=None,
                        help="Path to ADG snapshot. Default: latest.")
    parser.add_argument("--top-n", type=int, default=10,
                        help="Top-N samples per defect class. Default: 10.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_REPORT_DIR,
                        help="Output directory.")
    parser.add_argument("--format", choices=("json", "md", "both"), default="both",
                        help="Output format. Default: both.")
    args = parser.parse_args()

    snapshot = args.snapshot or _latest_snapshot()
    print(f"[gap_report] snapshot={snapshot.name}")

    report = run_report(snapshot, top_n=args.top_n)

    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.format in ("json", "both"):
        out_json = args.out_dir / "THREE_BUCKET_GAP_REPORT.json"
        out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"[gap_report] wrote {out_json.relative_to(REPO_ROOT)}")

    if args.format in ("md", "both"):
        out_md = args.out_dir / "THREE_BUCKET_GAP_REPORT.md"
        out_md.write_text(render_markdown(report), encoding="utf-8")
        print(f"[gap_report] wrote {out_md.relative_to(REPO_ROOT)}")

    # One-line summary to stdout for CI/inline use.
    print(
        f"[gap_report] health={report['health_score_pct_triplet_attested']}% "
        f"runtime_present={report['runtime_view_present']} "
        f"total_edges={report['total_edges_classified']}"
    )
    for row in report["summary_by_class"]:
        print(
            f"[gap_report]   {row['severity']:>3}  {row['defect_class']:<20} "
            f"{row['edge_count']:>8,}  ({row['edge_pct']:>5}%)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
