"""
ADG Retrieval Wiring Accelerator

Validates that all 5 retrieval layers (L1-L5) from Agentic Retrieval Models v18
are wired across agentic_core (L0-L6) and all apps_* packages.

Waves implemented:
- W1-W2: SQLite query layer for gap detection
- W3: JSON/CSV report generation
- W4: CLI integration
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sqlite3
import sys
from dataclasses import dataclass, field
from typing import Any

# Import SSOT constants for layer and app package names
from agentic_core.L0_routing.config.ssot_tier_constants import (
    AGENTIC_CORE_LAYERS,
    APPS_PACKAGES,
)


@dataclass
class GapReport:
    """Container for all gap detection results."""

    # Global counts
    node_count: int = 0
    edge_count: int = 0
    sqlite_path: str = ""

    # Relation counts
    relation_counts: dict[str, int] = field(default_factory=dict)

    # Layer coverage (source_file match)
    layer_coverage: dict[str, dict[str, Any]] = field(default_factory=dict)

    # App coverage (source_file match)
    app_coverage: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Symbol presence in nodes
    symbol_presence: dict[str, int] = field(default_factory=dict)
    symbol_absent: list[str] = field(default_factory=list)

    # Cross-layer edges
    cross_layer_edges: dict[str, dict[str, int]] = field(default_factory=dict)

    # App-to-layer wiring detail
    app_layer_wiring: dict[str, dict[str, int]] = field(default_factory=dict)

    # Computed gaps
    gaps: list[dict[str, Any]] = field(default_factory=list)


class RetrievalAccelerator:
    """ADG retrieval wiring validation accelerator."""

    DEFAULT_SQLITE = None  # Resolved dynamically via path_resolver

    def _get_sqlite_path(self) -> str:
        """Resolve SQLite path dynamically using path_resolver."""
        from tools.adg.shared_modules.path_resolver import latest_sqlite
        path = latest_sqlite()
        if path:
            return str(path)
        raise FileNotFoundError("No ADG SQLite file found in artifacts/adg/")

    RETRIEVAL_RELATIONS = [
        "pulls_context",
        "reads_from",
        "writes_to",
        "reads_through",
        "writes_through",
        "validated_by_safety_plane",
        "calls",
        "routes_through",
        "emits_metric_event",
        "execution_terminates_at_uwg",
    ]

    RETRIEVAL_SYMBOLS = [
        "query_intent_expansion",
        "graphrag_config",
        "react_config",
        "chunk",
        "enrich",
        "ingestion",
        "document_load",
        "brief_assembly",
        "source_ingestion",
        "context",
        "orchestrat",
        "retrieval",
        "graph_rag",
        "graphrag",
        "vector",
        "faiss",
        "chroma",
        "l4d",
    ]

    def __init__(self, sqlite_path: str | None = None) -> None:
        """Initialize accelerator with optional explicit SQLite path.

        Args:
            sqlite_path: Explicit path, or None to auto-resolve latest
        """
        if sqlite_path:
            self.sqlite_path = sqlite_path
        else:
            # Resolve dynamically using path_resolver
            from tools.adg.shared_modules.path_resolver import latest_sqlite

            path = latest_sqlite()
            if not path:
                raise FileNotFoundError("No ADG SQLite file found in artifacts/adg/")
            self.sqlite_path = str(path)
        self.conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        """Establish SQLite connection."""
        if not os.path.exists(self.sqlite_path):
            raise FileNotFoundError(f"ADG SQLite not found: {self.sqlite_path}")
        self.conn = sqlite3.connect(self.sqlite_path)

    def close(self) -> None:
        """Close SQLite connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def query_graph_size(self) -> tuple[int, int]:
        """Return (node_count, edge_count)."""
        if not self.conn:
            raise RuntimeError("Not connected to SQLite")
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM nodes")
        node_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM edges")
        edge_count = cur.fetchone()[0]
        return node_count, edge_count

    def query_relation_counts(self) -> dict[str, int]:
        """Count edges per retrieval relation type."""
        if not self.conn:
            raise RuntimeError("Not connected to SQLite")
        cur = self.conn.cursor()
        counts = {}
        for rel in self.RETRIEVAL_RELATIONS:
            cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rel,))
            counts[rel] = cur.fetchone()[0]
        return counts

    def query_layer_coverage(self) -> dict[str, dict[str, Any]]:
        """Query retrieval edge counts per agentic_core layer."""
        if not self.conn:
            raise RuntimeError("Not connected to SQLite")
        cur = self.conn.cursor()
        coverage = {}
        placeholders = ",".join("?" * len(self.RETRIEVAL_RELATIONS))
        for layer in AGENTIC_CORE_LAYERS:
            pat = f"%/{layer}/%"
            cur.execute(
                f"SELECT relation_type, COUNT(*) FROM edges "
                f"WHERE source_file LIKE ? AND relation_type IN ({placeholders}) "
                f"GROUP BY relation_type",
                [pat] + self.RETRIEVAL_RELATIONS,
            )
            rows = dict(cur.fetchall())
            coverage[layer] = {"total": sum(rows.values()), "by_relation": rows}
        return coverage

    def query_app_coverage(self) -> dict[str, dict[str, Any]]:
        """Query retrieval edge counts per apps_* package."""
        if not self.conn:
            raise RuntimeError("Not connected to SQLite")
        cur = self.conn.cursor()
        coverage = {}
        placeholders = ",".join("?" * len(self.RETRIEVAL_RELATIONS))
        for app in APPS_PACKAGES:
            pat = f"%{app}/%"
            cur.execute(
                f"SELECT relation_type, COUNT(*) FROM edges "
                f"WHERE source_file LIKE ? AND relation_type IN ({placeholders}) "
                f"GROUP BY relation_type",
                [pat] + self.RETRIEVAL_RELATIONS,
            )
            rows = dict(cur.fetchall())
            coverage[app] = {"total": sum(rows.values()), "by_relation": rows}
        return coverage

    def query_symbol_presence(self) -> tuple[dict[str, int], list[str]]:
        """Query retrieval symbol presence in node resolved_path."""
        if not self.conn:
            raise RuntimeError("Not connected to SQLite")
        cur = self.conn.cursor()
        present = {}
        absent = []
        for sym in self.RETRIEVAL_SYMBOLS:
            cur.execute(
                "SELECT COUNT(*) FROM nodes WHERE resolved_path LIKE ?",
                (f"%{sym}%",),
            )
            count = cur.fetchone()[0]
            if count > 0:
                present[sym] = count
            else:
                absent.append(sym)
        return present, absent

    def query_cross_layer_edges(
        self, pairs: list[tuple[str, str]] | None = None
    ) -> dict[str, dict[str, int]]:
        """Query cross-layer retrieval edges."""
        if not self.conn:
            raise RuntimeError("Not connected to SQLite")
        if pairs is None:
            pairs = [
                ("L1_cognition", "L4_state"),
                ("L2_execution", "L4_state"),
                ("L3_orchestration", "L4_state"),
                ("L3_orchestration", "L2_execution"),
                ("L5_safety", "L3_orchestration"),
                ("L0_routing", "L1_cognition"),
                ("L6_observability", "L4_state"),
                ("apps_shared", "L2_execution"),
                ("apps_lic", "L2_execution"),
            ]
        cur = self.conn.cursor()
        results = {}
        placeholders = ",".join("?" * len(self.RETRIEVAL_RELATIONS))
        for src_pat, dst_pat in pairs:
            cur.execute(
                f"""SELECT COUNT(*) FROM edges e
                   JOIN nodes n_dst ON e.dst_id = n_dst.id
                   WHERE e.source_file LIKE ?
                     AND n_dst.resolved_path LIKE ?
                     AND e.relation_type IN ({placeholders})""",
                [f"%{src_pat}%", f"%{dst_pat}%"] + self.RETRIEVAL_RELATIONS,
            )
            fwd = cur.fetchone()[0]
            cur.execute(
                f"""SELECT COUNT(*) FROM edges e
                   JOIN nodes n_dst ON e.dst_id = n_dst.id
                   WHERE e.source_file LIKE ?
                     AND n_dst.resolved_path LIKE ?
                     AND e.relation_type IN ({placeholders})""",
                [f"%{dst_pat}%", f"%{src_pat}%"] + self.RETRIEVAL_RELATIONS,
            )
            rev = cur.fetchone()[0]
            results[f"{src_pat} <-> {dst_pat}"] = {"fwd": fwd, "rev": rev, "total": fwd + rev}
        return results

    def query_app_layer_wiring(self) -> dict[str, dict[str, int]]:
        """Query per-app wiring to L1-L5 retrieval layers."""
        if not self.conn:
            raise RuntimeError("Not connected to SQLite")
        cur = self.conn.cursor()
        wiring = {}
        layers = ["L1_cognition", "L2_execution", "L3_orchestration", "L4_state", "L5_safety"]
        for app in APPS_PACKAGES:
            app_wiring = {}
            for layer in layers:
                cur.execute(
                    """SELECT COUNT(*) FROM edges e
                       JOIN nodes n_dst ON e.dst_id = n_dst.id
                       WHERE (e.source_file LIKE ? AND n_dst.resolved_path LIKE ?)
                          OR (e.source_file LIKE ? AND n_dst.resolved_path LIKE ?)""",
                    [f"%{app}%", f"%{layer}%", f"%{layer}%", f"%{app}%"],
                )
                count = cur.fetchone()[0]
                app_wiring[layer] = count
            wiring[app] = app_wiring
        return wiring

    def compute_gaps(self, report: GapReport) -> list[dict[str, Any]]:
        """Compute gap list from report data."""
        gaps = []

        # GAP-1: apps_underwriting_ai zero retrieval wiring
        if report.app_coverage.get("apps_underwriting_ai", {}).get("total", 0) == 0:
            gaps.append({
                "id": "GAP-1",
                "severity": "CRITICAL",
                "description": "apps_underwriting_ai has zero retrieval edges",
                "impact": "Entire underwriting AI app invisible to retrieval governance",
            })

        # GAP-2: apps_lic missing L1, L3, L5
        app_lic_wiring = report.app_layer_wiring.get("apps_lic", {})
        missing = [layer for layer in ["L1_cognition", "L3_orchestration", "L5_safety"] if app_lic_wiring.get(layer, 0) == 0]
        if missing:
            gaps.append({
                "id": "GAP-2",
                "severity": "HIGH",
                "description": f"apps_lic missing wiring to: {missing}",
                "impact": "Retrieval lacks intent expansion, context assembly, guardrail",
            })

        # GAP-3: apps_eval missing L1, L3, L4
        app_eval_wiring = report.app_layer_wiring.get("apps_eval", {})
        missing = [layer for layer in ["L1_cognition", "L3_orchestration", "L4_state"] if app_eval_wiring.get(layer, 0) == 0]
        if missing:
            gaps.append({
                "id": "GAP-3",
                "severity": "HIGH",
                "description": f"apps_eval missing wiring to: {missing}",
                "impact": "Eval cannot measure retrieval quality against context",
            })

        # GAP-4: apps_exec, apps_research, apps_rfp missing L1, L3, L4, L5
        for app in ["apps_exec", "apps_research", "apps_rfp"]:
            app_wiring = report.app_layer_wiring.get(app, {})
            missing = [layer for layer in ["L1_cognition", "L3_orchestration", "L4_state", "L5_safety"] if app_wiring.get(layer, 0) == 0]
            if missing:
                gaps.append({
                    "id": f"GAP-4-{app}",
                    "severity": "MEDIUM",
                    "description": f"{app} missing wiring to: {missing}",
                    "impact": f"{app} retrieval by coincidence not architecture",
                })

        # GAP-5: apps_shared missing L1
        app_shared_wiring = report.app_layer_wiring.get("apps_shared", {})
        if app_shared_wiring.get("L1_cognition", 0) == 0:
            gaps.append({
                "id": "GAP-5",
                "severity": "MEDIUM",
                "description": "apps_shared missing L1_cognition wiring",
                "impact": "Shared strategies unaware of query intent layer",
            })

        # GAP-6: Absent symbols
        if report.symbol_absent:
            gaps.append({
                "id": "GAP-6",
                "severity": "HIGH",
                "description": f"Absent ADG symbols: {report.symbol_absent}",
                "impact": "Components invisible to ADG governance",
            })

        # GAP-7: Thin cross-layer edges
        l1_l4 = report.cross_layer_edges.get("L1_cognition <-> L4_state", {})
        l6_l4 = report.cross_layer_edges.get("L6_observability <-> L4_state", {})
        if l1_l4.get("total", 0) < 5 or l6_l4.get("total", 0) < 5:
            gaps.append({
                "id": "GAP-7",
                "severity": "LOW",
                "description": f"Thin cross-layer: L1↔L4={l1_l4.get('total', 0)}, L6↔L4={l6_l4.get('total', 0)}",
                "impact": "Critical retrieval paths not demonstrably proven",
            })

        return gaps

    def run(self) -> GapReport:
        """Execute full validation and return report."""
        self.connect()
        try:
            report = GapReport()
            report.sqlite_path = self.sqlite_path

            # Graph size
            report.node_count, report.edge_count = self.query_graph_size()

            # Relation counts
            report.relation_counts = self.query_relation_counts()

            # Layer coverage
            report.layer_coverage = self.query_layer_coverage()

            # App coverage
            report.app_coverage = self.query_app_coverage()

            # Symbol presence
            report.symbol_presence, report.symbol_absent = self.query_symbol_presence()

            # Cross-layer edges
            report.cross_layer_edges = self.query_cross_layer_edges()

            # App layer wiring
            report.app_layer_wiring = self.query_app_layer_wiring()

            # Compute gaps
            report.gaps = self.compute_gaps(report)

            return report
        finally:
            self.close()


def run_validation(sqlite_path: str | None = None) -> GapReport:
    """Convenience function to run validation."""
    accel = RetrievalAccelerator(sqlite_path)
    return accel.run()


def print_report(report: GapReport) -> None:
    """Print human-readable report to stdout."""
    print("=" * 70)
    print("ADG RETRIEVAL WIRING VALIDATION")
    print(f"SQLite: {os.path.basename(report.sqlite_path)}")
    print("=" * 70)
    print(f"\n[GRAPH] Nodes={report.node_count:,}  Edges={report.edge_count:,}")

    print("\n[RETRIEVAL RELATIONS]")
    for rel, count in sorted(report.relation_counts.items()):
        status = "OK  " if count > 0 else "MISS"
        print(f"  [{status}] {rel}: {count:,}")

    print("\n[AGENTIC_CORE LAYER COVERAGE]")
    for layer, data in sorted(report.layer_coverage.items()):
        total = data["total"]
        status = "OK  " if total > 0 else "GAP "
        print(f"  [{status}] {layer}: {total:,} edges")

    print("\n[APPS_* COVERAGE]")
    for app, data in sorted(report.app_coverage.items()):
        total = data["total"]
        status = "OK  " if total > 0 else "GAP "
        print(f"  [{status}] {app}: {total:,} edges")

    print(f"\n[SYMBOLS] Present: {len(report.symbol_presence)}, Absent: {len(report.symbol_absent)}")
    if report.symbol_absent:
        print(f"  ABSENT: {report.symbol_absent}")

    print("\n[CROSS-LAYER EDGES]")
    for pair, counts in sorted(report.cross_layer_edges.items()):
        total = counts["total"]
        status = "OK  " if total > 0 else "GAP "
        print(f"  [{status}] {pair}: fwd={counts['fwd']} rev={counts['rev']} total={total}")

    print("\n[APP ↔ LAYER WIRING]")
    for app, wiring in sorted(report.app_layer_wiring.items()):
        missing = [layer for layer, count in wiring.items() if count == 0]
        if missing:
            print(f"  [GAP ] {app}: missing {missing}")
        else:
            print(f"  [OK  ] {app}: all layers wired")

    print("\n" + "=" * 70)
    print("GAP REGISTER")
    print("=" * 70)
    if report.gaps:
        for gap in report.gaps:
            print(f"\n[{gap['id']}] {gap['severity']}")
            print(f"  {gap['description']}")
            print(f"  Impact: {gap['impact']}")
        print(f"\nTOTAL GAPS: {len(report.gaps)}")
    else:
        print("\n✅ NO GAPS FOUND")
    print("=" * 70)


def write_json_report(report: GapReport, output_path: str) -> None:
    """Write report as JSON."""
    data = {
        "metadata": {
            "sqlite_path": report.sqlite_path,
            "node_count": report.node_count,
            "edge_count": report.edge_count,
            "timestamp": None,  # Could add timestamp
        },
        "relation_counts": report.relation_counts,
        "layer_coverage": report.layer_coverage,
        "app_coverage": report.app_coverage,
        "symbol_presence": report.symbol_presence,
        "symbol_absent": report.symbol_absent,
        "cross_layer_edges": report.cross_layer_edges,
        "app_layer_wiring": report.app_layer_wiring,
        "gaps": report.gaps,
        "gap_count": len(report.gaps),
        "all_gaps_closed": len(report.gaps) == 0,
    }
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)


def write_csv_report(report: GapReport, output_path: str) -> None:
    """Write gaps as CSV."""
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["gap_id", "severity", "description", "impact"])
        for gap in report.gaps:
            writer.writerow([gap["id"], gap["severity"], gap["description"], gap["impact"]])


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ADG Retrieval Wiring Accelerator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python adg_retrieval_accelerator.py
  python adg_retrieval_accelerator.py --sqlite path/to/adg.sqlite
  python adg_retrieval_accelerator.py --json out.json --csv out.csv
""",
    )
    parser.add_argument(
        "--sqlite",
        help="Path to ADG SQLite file (default: artifacts/adg/adg_indexed_03312026_1808.sqlite)",
    )
    parser.add_argument("--json", help="Write JSON report to path")
    parser.add_argument("--csv", help="Write CSV gap report to path")
    parser.add_argument("--quiet", action="store_true", help="Suppress stdout output")
    args = parser.parse_args()

    try:
        report = run_validation(args.sqlite)

        if not args.quiet:
            print_report(report)

        if args.json:
            write_json_report(report, args.json)
            if not args.quiet:
                print(f"\nJSON report written: {args.json}")

        if args.csv:
            write_csv_report(report, args.csv)
            if not args.quiet:
                print(f"CSV report written: {args.csv}")

        return 0 if report.gaps else 0  # Return 0 even with gaps ( informational)

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except sqlite3.Error as e:
        print(f"ERROR: SQLite error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
