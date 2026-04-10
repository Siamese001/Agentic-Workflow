#!/usr/bin/env python3
"""GraphDB P2/P3 Watch Gates — Non-blocking debt and trend tracking.

This module implements P2 (Warning) and P3 (Watch/Trend) gates for GraphDB CI:
    P2-1: Non-critical query coverage gaps
    P2-2: Indexing / performance debt
    P2-3: Snapshot storage / bloat debt
    P2-4: Partial graph metadata enrichment gaps
    P3-1: Experimental graph features
    P3-2: Query ergonomics debt
    P3-3: Long-term graph model opportunities

P2/P3 gates never block commits. They output warnings and trend data
for informational purposes and future prioritization.

Architecture:
    Canonical ADG SQLite → GraphDB Projection → P2/P3 Watch → Warnings/Trends

Exit codes:
    0 — Always (P2/P3 gates are non-blocking)

Reference: docs/technical/graphdb_ci_hardening.md
"""

from __future__ import annotations

import json
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
ADG_DIR = REPO_ROOT / "artifacts" / "adg"
GRAPHDB_DIR = REPO_ROOT / "tools" / "graphdb"

# P2 warning thresholds
INDEXING_DEBT_THRESHOLD = 100  # Number of missing recommended indexes
SNAPSHOT_SIZE_THRESHOLD_MB = 500  # Max recommended snapshot size in MB

# P3 tracking categories
EXPERIMENTAL_FEATURES: Set[str] = {
    "prototype_traversal",
    "optional_analytical_rollups",
    "non_production_viz",
}


@dataclass
class WatchGateResult:
    """Result from a P2/P3 watch gate check."""

    gate_id: str
    severity: str  # P2 or P3
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    debt_score: int = 0  # 0-100 scale for prioritization
    trend_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
            "debt_score": self.debt_score,
            "trend_data": self.trend_data,
        }


class GraphDBP2P3Watch:
    """P2/P3 watch gates for GraphDB projections."""

    def __init__(self, sqlite_path: Optional[Path] = None):
        """Initialize P2/P3 watch gates.

        Args:
            sqlite_path: Path to ADG SQLite file (auto-detected if None)
        """
        self.sqlite_path = sqlite_path or self._find_latest_adg_sqlite()
        self.results: List[WatchGateResult] = []

        if not self.sqlite_path or not self.sqlite_path.exists():
            raise FileNotFoundError(f"ADG SQLite not found. Run: python tools/generate/generate_full_adg.py")

    def _find_latest_adg_sqlite(self) -> Optional[Path]:
        """Find the most recent ADG SQLite file."""
        if not ADG_DIR.exists():
            return None
        sqlite_files = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"), reverse=True)
        return sqlite_files[0] if sqlite_files else None

    def _get_sqlite_stats(self) -> Tuple[int, int, Dict[str, int], Dict[str, int]]:
        """Get entity/relation counts from canonical ADG SQLite."""
        with sqlite3.connect(str(self.sqlite_path)) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM entities")
            entity_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM relations")
            relation_count = cursor.fetchone()[0]

            cursor.execute("SELECT type, COUNT(*) FROM entities GROUP BY type")
            entity_type_counts = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.execute("SELECT type, COUNT(*) FROM relations GROUP BY type")
            relation_type_counts = {row[0]: row[1] for row in cursor.fetchall()}

            return entity_count, relation_count, entity_type_counts, relation_type_counts

    def check_p2_1_query_coverage_gaps(self) -> WatchGateResult:
        """P2-1: Non-critical query coverage gaps watch.

        Tracks optional subgraph extraction and lower-priority query gaps.
        """
        gate_id = "P2-1"

        try:
            # Identify unprojected node/edge types (non-critical)
            _, _, entity_types, relation_types = self._get_sqlite_stats()

            # Types that would be nice to have but aren't required
            optional_node_types = {
                "validator_node",
                "healer_agent",
                "embedding_store",
                "chunk_pipeline",
                "retrieval_endpoint",
            }
            optional_edge_types = {
                "pulls_context",
                "retrieves_via",
                "generates_prompt",
            }

            missing_optional_nodes = optional_node_types - set(entity_types.keys())
            missing_optional_edges = optional_edge_types - set(relation_types.keys())

            # Calculate debt score based on coverage gaps
            total_optional = len(optional_node_types) + len(optional_edge_types)
            missing_count = len(missing_optional_nodes) + len(missing_optional_edges)
            debt_score = int((missing_count / total_optional) * 50) if total_optional > 0 else 0

            coverage_data = {
                "optional_node_types_available": sorted(optional_node_types & set(entity_types.keys())),
                "optional_node_types_missing": sorted(missing_optional_nodes),
                "optional_edge_types_available": sorted(optional_edge_types & set(relation_types.keys())),
                "optional_edge_types_missing": sorted(missing_optional_edges),
                "total_optional": total_optional,
                "missing_count": missing_count,
            }

            return WatchGateResult(
                gate_id=gate_id,
                severity="P2",
                message=f"Query coverage gaps: {missing_count}/{total_optional} optional types missing",
                details=coverage_data,
                debt_score=debt_score,
                trend_data={"missing_optional_types": missing_count},
            )

        except (sqlite3.Error, RuntimeError, OSError) as e:
            return WatchGateResult(
                gate_id=gate_id,
                severity="P2",
                message=f"P2-1 check error: {e}",
                details={"error": str(e)},
                debt_score=0,
            )

    def check_p2_2_indexing_debt(self) -> WatchGateResult:
        """P2-2: Indexing / performance debt watch.

        Tracks missing recommended indexes and avoidable full scans.
        """
        gate_id = "P2-2"

        try:
            # Check existing indexes on ADG SQLite
            with sqlite3.connect(str(self.sqlite_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
                existing_indexes = {row[0] for row in cursor.fetchall()}

            # Recommended indexes for optimal GraphDB queries
            recommended_indexes = {
                "idx_entities_type",
                "idx_relations_type",
                "idx_relations_from_id",
                "idx_relations_to_id",
                "idx_entities_name",
            }

            missing_indexes = recommended_indexes - existing_indexes

            # Calculate debt score
            debt_score = int((len(missing_indexes) / len(recommended_indexes)) * 100)

            # Flag high debt
            warning_level = "low"
            if debt_score > 50:
                warning_level = "high"
            elif debt_score > 25:
                warning_level = "medium"

            indexing_data = {
                "existing_indexes": sorted(existing_indexes),
                "recommended_indexes": sorted(recommended_indexes),
                "missing_indexes": sorted(missing_indexes),
                "coverage_percent": 100 - debt_score,
                "warning_level": warning_level,
            }

            return WatchGateResult(
                gate_id=gate_id,
                severity="P2",
                message=f"Indexing debt: {len(missing_indexes)}/{len(recommended_indexes)} indexes missing ({warning_level})",
                details=indexing_data,
                debt_score=debt_score,
                trend_data={"missing_index_count": len(missing_indexes)},
            )

        except (sqlite3.Error, RuntimeError, OSError) as e:
            return WatchGateResult(
                gate_id=gate_id,
                severity="P2",
                message=f"P2-2 check error: {e}",
                details={"error": str(e)},
                debt_score=0,
            )

    def check_p2_3_snapshot_bloat(self) -> WatchGateResult:
        """P2-3: Snapshot storage / bloat debt watch.

        Tracks redundant snapshot duplication and oversized artifacts.
        """
        gate_id = "P2-3"

        try:
            # Calculate total size of ADG artifacts
            total_size_bytes = 0
            artifact_count = 0

            for artifact_file in ADG_DIR.glob("adg_*"):
                if artifact_file.is_file():
                    total_size_bytes += artifact_file.stat().st_size
                    artifact_count += 1

            total_size_mb = total_size_bytes / (1024 * 1024)

            # Count snapshots
            snapshot_files = list(ADG_DIR.glob("adg_snapshot_*.json"))
            sqlite_files = list(ADG_DIR.glob("adg_indexed_*.sqlite"))

            # Calculate debt score based on size
            debt_score = min(100, int((total_size_mb / SNAPSHOT_SIZE_THRESHOLD_MB) * 50))

            # Flag old snapshots for cleanup consideration
            old_snapshots = []
            if len(snapshot_files) > 5:
                old_snapshots = [f.name for f in sorted(snapshot_files)[:-5]]

            storage_data = {
                "total_size_mb": round(total_size_mb, 2),
                "artifact_count": artifact_count,
                "snapshot_count": len(snapshot_files),
                "sqlite_count": len(sqlite_files),
                "old_snapshots_for_cleanup": old_snapshots,
                "threshold_mb": SNAPSHOT_SIZE_THRESHOLD_MB,
            }

            return WatchGateResult(
                gate_id=gate_id,
                severity="P2",
                message=f"Snapshot storage: {total_size_mb:.1f}MB across {artifact_count} artifacts",
                details=storage_data,
                debt_score=debt_score,
                trend_data={"total_size_mb": round(total_size_mb, 2)},
            )

        except (OSError, RuntimeError) as e:
            return WatchGateResult(
                gate_id=gate_id,
                severity="P2",
                message=f"P2-3 check error: {e}",
                details={"error": str(e)},
                debt_score=0,
            )

    def check_p2_4_metadata_enrichment(self) -> WatchGateResult:
        """P2-4: Partial graph metadata enrichment gaps watch.

        Tracks missing optional provenance and neighborhood metadata.
        """
        gate_id = "P2-4"

        try:
            # Check metadata completeness
            with sqlite3.connect(str(self.sqlite_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM metadata")
                metadata = {row[0]: row[1] for row in cursor.fetchall()}

            # Optional enrichment fields
            optional_fields = {
                "provenance_chain",
                "neighborhood_stats",
                "path_criticality",
                "enrichment_timestamp",
                "source_scanner_version",
            }

            present_optional = optional_fields & set(metadata.keys())
            missing_optional = optional_fields - set(metadata.keys())

            # Calculate debt score
            total_optional = len(optional_fields)
            debt_score = int((len(missing_optional) / total_optional) * 100)

            enrichment_data = {
                "present_optional_fields": sorted(present_optional),
                "missing_optional_fields": sorted(missing_optional),
                "required_fields_present": sorted(set(metadata.keys()) - optional_fields),
                "enrichment_coverage": f"{len(present_optional)}/{total_optional}",
            }

            return WatchGateResult(
                gate_id=gate_id,
                severity="P2",
                message=f"Metadata enrichment: {len(present_optional)}/{total_optional} optional fields present",
                details=enrichment_data,
                debt_score=debt_score,
                trend_data={"missing_enrichment_fields": len(missing_optional)},
            )

        except (sqlite3.Error, RuntimeError, OSError) as e:
            return WatchGateResult(
                gate_id=gate_id,
                severity="P2",
                message=f"P2-4 check error: {e}",
                details={"error": str(e)},
                debt_score=0,
            )

    def check_p3_1_experimental_features(self) -> WatchGateResult:
        """P3-1: Experimental graph features watch.

        Tracks prototype traversal helpers and non-production surfaces.
        """
        gate_id = "P3-1"

        try:
            # Scan graphdb directory for experimental markers
            experimental_markers = []

            for py_file in GRAPHDB_DIR.glob("*.py"):
                content = py_file.read_text()

                # Look for experimental markers
                if "# EXPERIMENTAL" in content:
                    experimental_markers.append(f"{py_file.name}: EXPERIMENTAL marker")
                if "# PROTOTYPE" in content:
                    experimental_markers.append(f"{py_file.name}: PROTOTYPE marker")
                if "_experimental_" in py_file.name:
                    experimental_markers.append(f"{py_file.name}: experimental in filename")

            # Check queries directory for experimental queries
            queries_dir = GRAPHDB_DIR / "queries"
            if queries_dir.exists():
                for query_file in queries_dir.glob("*.py"):
                    content = query_file.read_text()
                    if "# EXPERIMENTAL" in content or "# PROTOTYPE" in content:
                        experimental_markers.append(f"queries/{query_file.name}: experimental query")

            feature_data = {
                "experimental_markers_found": experimental_markers,
                "experimental_categories": sorted(EXPERIMENTAL_FEATURES),
                "files_checked": len(list(GRAPHDB_DIR.glob("*.py"))),
            }

            return WatchGateResult(
                gate_id=gate_id,
                severity="P3",
                message=f"Experimental features: {len(experimental_markers)} markers found",
                details=feature_data,
                debt_score=min(100, len(experimental_markers) * 10),
                trend_data={"experimental_marker_count": len(experimental_markers)},
            )

        except (OSError, RuntimeError) as e:
            return WatchGateResult(
                gate_id=gate_id,
                severity="P3",
                message=f"P3-1 check error: {e}",
                details={"error": str(e)},
                debt_score=0,
            )

    def check_p3_2_query_ergonomics(self) -> WatchGateResult:
        """P3-2: Query ergonomics debt watch.

        Tracks awkward analyst query paths and weak naming conventions.
        """
        gate_id = "P3-2"

        try:
            # Analyze query helper naming conventions
            queries_dir = GRAPHDB_DIR / "queries"
            naming_issues = []

            if queries_dir.exists():
                for py_file in queries_dir.glob("*.py"):
                    # Check for non-uniform naming
                    if not py_file.name.startswith("query_") and py_file.name != "__init__.py":
                        naming_issues.append(f"{py_file.name}: doesn't start with 'query_'")

            # Check for overly long query names (ergonomics issue)
            for py_file in GRAPHDB_DIR.glob("*.py"):
                if len(py_file.stem) > 50:
                    naming_issues.append(f"{py_file.name}: name >50 chars (ergonomics)")

            ergonomics_data = {
                "naming_convention_issues": naming_issues,
                "queries_checked": len(list(queries_dir.glob("*.py"))) if queries_dir.exists() else 0,
                "recommended_patterns": ["query_<domain>_<action>.py", "<50 chars"],
            }

            debt_score = min(100, len(naming_issues) * 5)

            return WatchGateResult(
                gate_id=gate_id,
                severity="P3",
                message=f"Query ergonomics: {len(naming_issues)} naming issues found",
                details=ergonomics_data,
                debt_score=debt_score,
                trend_data={"naming_issue_count": len(naming_issues)},
            )

        except (OSError, RuntimeError) as e:
            return WatchGateResult(
                gate_id=gate_id,
                severity="P3",
                message=f"P3-2 check error: {e}",
                details={"error": str(e)},
                debt_score=0,
            )

    def check_p3_3_long_term_opportunities(self) -> WatchGateResult:
        """P3-3: Long-term graph model opportunities watch.

        Tracks richer path semantics and advanced neighborhood surfaces.
        """
        gate_id = "P3-3"

        try:
            # Identify opportunities based on current graph structure
            entity_count, relation_count, entity_types, relation_types = self._get_sqlite_stats()

            opportunities = []

            # Opportunity: rich path semantics if we have many multi-hop paths
            if relation_count > entity_count * 2:
                opportunities.append(
                    "rich_path_semantics: high edge-to-node ratio suggests path analysis potential"
                )

            # Opportunity: centrality analysis if we have connectivity data
            if "imports" in relation_types or "calls" in relation_types:
                opportunities.append("centrality_analysis: import/call data supports centrality metrics")

            # Opportunity: community detection if we have layer data
            if "layer" in entity_types:
                opportunities.append("community_detection: layer structure supports community analysis")

            # Opportunity: temporal analysis if we have timestamp data
            with sqlite3.connect(str(self.sqlite_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM entities WHERE properties LIKE '%timestamp%'")
                timestamp_count = cursor.fetchone()[0]
                if timestamp_count > 0:
                    opportunities.append("temporal_analysis: timestamp data supports time-series analysis")

            opportunity_data = {
                "identified_opportunities": opportunities,
                "opportunity_count": len(opportunities),
                "graph_density_indicator": relation_count / max(entity_count, 1),
            }

            return WatchGateResult(
                gate_id=gate_id,
                severity="P3",
                message=f"Long-term opportunities: {len(opportunities)} potential enhancements identified",
                details=opportunity_data,
                debt_score=0,  # Opportunities aren't debt
                trend_data={"opportunity_count": len(opportunities)},
            )

        except (sqlite3.Error, RuntimeError, OSError) as e:
            return WatchGateResult(
                gate_id=gate_id,
                severity="P3",
                message=f"P3-3 check error: {e}",
                details={"error": str(e)},
                debt_score=0,
            )

    def run_all_p2p3_watches(self) -> List[WatchGateResult]:
        """Run all P2/P3 watch gates and return results."""
        self.results = [
            self.check_p2_1_query_coverage_gaps(),
            self.check_p2_2_indexing_debt(),
            self.check_p2_3_snapshot_bloat(),
            self.check_p2_4_metadata_enrichment(),
            self.check_p3_1_experimental_features(),
            self.check_p3_2_query_ergonomics(),
            self.check_p3_3_long_term_opportunities(),
        ]
        return self.results

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all watch gate results."""
        if not self.results:
            return {"status": "NO_RESULTS", "total": 0}

        p2_count = sum(1 for r in self.results if r.severity == "P2")
        p3_count = sum(1 for r in self.results if r.severity == "P3")
        total_debt = sum(r.debt_score for r in self.results if r.severity == "P2")

        return {
            "status": "WATCH",
            "total": len(self.results),
            "p2_warnings": p2_count,
            "p3_watches": p3_count,
            "total_debt_score": total_debt,
            "watches": [r.to_dict() for r in self.results],
        }


def main() -> int:
    """Main entry point for GraphDB P2/P3 watch gates."""
    print("[GRAPHDB-P2/P3] Running P2/P3 watch gates...")
    print()

    if not ADG_DIR.exists():
        print(f"[GRAPHDB-P2/P3] ERROR: ADG directory not found: {ADG_DIR}", file=sys.stderr)
        return 2

    try:
        watch = GraphDBP2P3Watch()
    except FileNotFoundError as e:
        print(f"[GRAPHDB-P2/P3] ERROR: {e}", file=sys.stderr)
        return 2

    results = watch.run_all_p2p3_watches()

    print("=== P2/P3 WATCH RESULTS ===")
    print()

    # Group by severity
    p2_results = [r for r in results if r.severity == "P2"]
    p3_results = [r for r in results if r.severity == "P3"]

    if p2_results:
        print("--- P2 Warnings (Debt) ---")
        for result in p2_results:
            debt_indicator = "🔴" if result.debt_score > 50 else "🟡" if result.debt_score > 25 else "🟢"
            print(f"[{debt_indicator} P2] {result.gate_id}: {result.message}")
            print(f"      Debt score: {result.debt_score}/100")
        print()

    if p3_results:
        print("--- P3 Watch (Trends) ---")
        for result in p3_results:
            print(f"[👁 P3] {result.gate_id}: {result.message}")
        print()

    summary = watch.get_summary()
    print("=== SUMMARY ===")
    print(f"Total watches:  {summary['total']}")
    print(f"P2 warnings:    {summary['p2_warnings']}")
    print(f"P3 watches:     {summary['p3_watches']}")
    print(f"Total debt:     {summary['total_debt_score']}/700")
    print()

    print("[GRAPHDB-P2/P3] Non-blocking watch complete. Review debt scores for prioritization.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
