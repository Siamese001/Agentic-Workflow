#!/usr/bin/env python3
"""
ADG Domain Segmentation and Hotspot Normalization

Implements domain tagging and weighted centrality to normalize scanner/test dominance:
- domain ∈ {runtime, test, scanner, tooling, meta, shared}
- Separate graph projections by domain
- Weighted centrality calculations
- DEFAULT DOMAIN WEIGHTS: runtime > test > shared > tooling > scanner > meta

DEFAULT TOP-RISK AND TOP-HOTSPOT REPORTS:
- must use weighted_centrality
- must exclude scanner-dominant distortion unless explicitly requested
"""

from __future__ import annotations

import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class DomainSegmentationError(Exception):
    """Raised when domain segmentation verification fails."""
    pass

class ADGDomainSegmentationVerifier:
    """Verifies ADG domain segmentation and hotspot normalization."""

    VALID_DOMAINS = {"runtime", "test", "scanner", "tooling", "meta", "shared"}

    # Domain weights for centrality calculations (higher = more important)
    DOMAIN_WEIGHTS = {
        "runtime": 1.0,
        "test": 0.8,
        "shared": 0.6,
        "tooling": 0.4,
        "scanner": 0.2,
        "meta": 0.1
    }

    # Domain classification rules
    DOMAIN_CLASSIFICATION_RULES = {
        "runtime": {
            "path_patterns": ["agentic_core/L", "apps_"],
            "layer_patterns": ["L0", "L1", "L2", "L3", "L4", "L5", "L6"],
            "exclude_patterns": ["tests/", "test_", "tools/", "scanner"]
        },
        "test": {
            "path_patterns": ["tests/", "test_"],
            "entity_patterns": ["test"],
            "layer_patterns": ["L_TEST"]
        },
        "scanner": {
            "path_patterns": ["scanner", "adg/", "verification"],
            "entity_patterns": ["scanner", "validator", "verifier"]
        },
        "tooling": {
            "path_patterns": ["tools/", "ops_scripts/", "scripts/"],
            "entity_patterns": ["tool", "script", "utility"]
        },
        "meta": {
            "path_patterns": ["meta", "config", "schema"],
            "entity_patterns": ["config", "schema", "meta"]
        },
        "shared": {
            "path_patterns": ["shared", "common", "utils"],
            "entity_patterns": ["shared", "common", "util"]
        }
    }

    def __init__(self, adg_dir: Path):
        self.adg_dir = Path(adg_dir)
        self.sqlite_path = self._find_sqlite_database()
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def _find_sqlite_database(self) -> Path:
        """Find the latest SQLite database."""
        sqlite_files = list(self.adg_dir.glob("adg_indexed_*.sqlite"))
        if not sqlite_files:
            raise DomainSegmentationError("No SQLite database found")

        return max(sqlite_files, key=lambda p: p.stat().st_mtime)

    def _verify_domain_field_classification(self) -> Dict[str, Any]:
        """Verify domain field exists and has valid classifications."""
        print("🏷️  Verifying domain field classification...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Check if domain field exists
                cursor.execute("PRAGMA table_info(nodes)")
                columns = {row[1]: row for row in cursor.fetchall()}

                if "domain" not in columns:
                    self.errors.append("domain field missing from nodes table")
                    return {"field_exists": False, "classification_complete": False}

                print(f"   ✅ domain field exists")

                # Get current domain distribution
                cursor.execute("""
                    SELECT domain, COUNT(*) FROM nodes
                    WHERE domain IS NOT NULL
                    GROUP BY domain
                """)

                current_distribution = dict(cursor.fetchall())

                # Check for invalid values
                invalid_values = set(current_distribution.keys()) - self.VALID_DOMAINS
                if invalid_values:
                    self.errors.append(f"Invalid domain values: {invalid_values}")

                # Check for unclassified nodes
                cursor.execute("SELECT COUNT(*) FROM nodes WHERE domain IS NULL")
                unclassified_count = cursor.fetchone()[0]

                if unclassified_count > 0:
                    self.warnings.append(f"{unclassified_count} nodes have NULL domain")

                print(f"   📊 Current distribution: {current_distribution}")
                print(f"   📊 Unclassified: {unclassified_count}")

                return {
                    "field_exists": True,
                    "current_distribution": current_distribution,
                    "unclassified_count": unclassified_count,
                    "invalid_values": list(invalid_values),
                    "classification_complete": len(invalid_values) == 0 and unclassified_count == 0
                }

        except Exception as e:
            raise DomainSegmentationError(f"Domain field classification verification failed: {e}")

    def _verify_domain_distribution_balance(self) -> Dict[str, Any]:
        """Verify domain distribution is balanced and not dominated by scanner/test."""
        print("⚖️  Verifying domain distribution balance...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Get domain distribution for modules only
                cursor.execute("""
                    SELECT domain, COUNT(*) FROM nodes
                    WHERE entity_type = 'module' AND domain IS NOT NULL
                    GROUP BY domain
                """)

                module_distribution = dict(cursor.fetchall())

                # Get total module count
                cursor.execute("SELECT COUNT(*) FROM nodes WHERE entity_type = 'module'")
                total_modules = cursor.fetchone()[0]

                # Calculate percentages
                domain_percentages = {}
                for domain, count in module_distribution.items():
                    percentage = (count / max(1, total_modules)) * 100
                    domain_percentages[domain] = percentage

                print(f"   📊 Module distribution by domain:")
                for domain in sorted(self.VALID_DOMAINS):
                    count = module_distribution.get(domain, 0)
                    percentage = domain_percentages.get(domain, 0)
                    weight = self.DOMAIN_WEIGHTS.get(domain, 0)
                    print(f"      {domain}: {count} ({percentage:.1f}%) [weight: {weight}]")

                # Check for scanner/test dominance
                scanner_pct = domain_percentages.get("scanner", 0)
                test_pct = domain_percentages.get("test", 0)
                combined_pct = scanner_pct + test_pct

                if combined_pct > 60:
                    self.warnings.append(f"High scanner/test dominance: {combined_pct:.1f}%")

                if scanner_pct > 40:
                    self.warnings.append(f"Scanner dominance may distort risk analysis: {scanner_pct:.1f}%")

                # Calculate weighted distribution
                weighted_total = sum(count * self.DOMAIN_WEIGHTS.get(domain, 0)
                                  for domain, count in module_distribution.items())

                return {
                    "total_modules": total_modules,
                    "module_distribution": module_distribution,
                    "domain_percentages": domain_percentages,
                    "scanner_percentage": scanner_pct,
                    "test_percentage": test_pct,
                    "combined_scanner_test_percentage": combined_pct,
                    "weighted_total": weighted_total
                }

        except Exception as e:
            raise DomainSegmentationError(f"Domain distribution balance verification failed: {e}")

    def _calculate_weighted_centrality(self) -> Dict[str, Any]:
        """Calculate weighted centrality metrics by domain."""
        print("🎯 Calculating weighted centrality metrics...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Get fan-out (out-degree) by domain
                cursor.execute("""
                    SELECT n.domain, COUNT(*) as fan_out FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE n.domain IS NOT NULL
                    GROUP BY n.domain
                """)

                fan_out_by_domain = dict(cursor.fetchall())

                # Get fan-in (in-degree) by domain
                cursor.execute("""
                    SELECT n.domain, COUNT(*) as fan_in FROM edges e
                    JOIN nodes n ON e.dst_id = n.id
                    WHERE n.domain IS NOT NULL
                    GROUP BY n.domain
                """)

                fan_in_by_domain = dict(cursor.fetchall())

                # Calculate weighted centrality
                weighted_centrality = {}
                raw_centrality = {}

                for domain in self.VALID_DOMAINS:
                    weight = self.DOMAIN_WEIGHTS.get(domain, 0)
                    fan_out = fan_out_by_domain.get(domain, 0)
                    fan_in = fan_in_by_domain.get(domain, 0)

                    # Raw centrality (simple sum)
                    raw_total = fan_out + fan_in
                    raw_centrality[domain] = raw_total

                    # Weighted centrality
                    weighted_total = raw_total * weight
                    weighted_centrality[domain] = weighted_total

                print(f"   📊 Centrality analysis:")
                print(f"      Domain | Raw | Weighted | Weight")
                print(f"      -------|------|----------|-------")
                for domain in sorted(self.VALID_DOMAINS, key=lambda d: self.DOMAIN_WEIGHTS.get(d, 0), reverse=True):
                    raw = raw_centrality.get(domain, 0)
                    weighted = weighted_centrality.get(domain, 0)
                    weight = self.DOMAIN_WEIGHTS.get(domain, 0)
                    print(f"      {domain:7} | {raw:4} | {weighted:8} | {weight:.1f}")

                # Calculate centrality ratios
                total_raw = sum(raw_centrality.values())
                total_weighted = sum(weighted_centrality.values())

                centrality_ratios = {}
                for domain in self.VALID_DOMAINS:
                    raw_pct = (raw_centrality.get(domain, 0) / max(1, total_raw)) * 100
                    weighted_pct = (weighted_centrality.get(domain, 0) / max(1, total_weighted)) * 100
                    centrality_ratios[domain] = {
                        "raw_percentage": raw_pct,
                        "weighted_percentage": weighted_pct,
                        "ratio_change": weighted_pct - raw_pct
                    }

                print(f"   📊 Centrality impact:")
                for domain in sorted(self.VALID_DOMAINS, key=lambda d: weighted_centrality.get(d, 0), reverse=True):
                    ratios = centrality_ratios[domain]
                    change = ratios["ratio_change"]
                    change_symbol = "+" if change > 0 else ""
                    print(f"      {domain}: {ratios['raw_percentage']:.1f}% → {ratios['weighted_percentage']:.1f}% ({change_symbol}{change:.1f}%)")

                return {
                    "fan_out_by_domain": fan_out_by_domain,
                    "fan_in_by_domain": fan_in_by_domain,
                    "raw_centrality": raw_centrality,
                    "weighted_centrality": weighted_centrality,
                    "centrality_ratios": centrality_ratios,
                    "total_raw_centrality": total_raw,
                    "total_weighted_centrality": total_weighted
                }

        except Exception as e:
            raise DomainSegmentationError(f"Weighted centrality calculation failed: {e}")

    def _verify_hotspot_normalization(self) -> Dict[str, Any]:
        """Verify hotspot normalization excludes scanner/test dominance."""
        print("🔥 Verifying hotspot normalization...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Get top hotspots by raw centrality
                cursor.execute("""
                    SELECT n.adg_name, n.domain, COUNT(*) as connections FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE n.domain IS NOT NULL
                    GROUP BY n.id, n.adg_name, n.domain
                    ORDER BY connections DESC
                    LIMIT 20
                """)

                raw_hotspots = []
                for row in cursor.fetchall():
                    raw_hotspots.append({
                        "module": row[0],
                        "domain": row[1],
                        "connections": row[2]
                    })

                # Get top hotspots by weighted centrality
                cursor.execute("""
                    SELECT n.adg_name, n.domain,
                           COUNT(*) * ? as weighted_connections FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE n.domain IS NOT NULL
                    GROUP BY n.id, n.adg_name, n.domain
                    ORDER BY weighted_connections DESC
                    LIMIT 20
                """, (1.0,))  # Base weight, will be adjusted per domain

                weighted_hotspots = []
                for row in cursor.fetchall():
                    domain = row[1]
                    weight = self.DOMAIN_WEIGHTS.get(domain, 0)
                    weighted_connections = row[2] * weight

                    weighted_hotspots.append({
                        "module": row[0],
                        "domain": domain,
                        "raw_connections": row[2],
                        "weighted_connections": weighted_connections
                    })

                # Sort weighted hotspots properly
                weighted_hotspots.sort(key=lambda x: x["weighted_connections"], reverse=True)

                # Analyze domain distribution in top hotspots
                raw_top_domains = defaultdict(int)
                weighted_top_domains = defaultdict(int)

                for hs in raw_hotspots[:10]:
                    raw_top_domains[hs["domain"]] += 1

                for hs in weighted_hotspots[:10]:
                    weighted_top_domains[hs["domain"]] += 1

                print(f"   📊 Top 10 hotspots - Raw vs Weighted domain distribution:")
                for domain in self.VALID_DOMAINS:
                    raw_count = raw_top_domains.get(domain, 0)
                    weighted_count = weighted_top_domains.get(domain, 0)
                    print(f"      {domain}: {raw_count} → {weighted_count}")

                # Check for scanner dominance in raw hotspots
                scanner_raw_dominance = raw_top_domains.get("scanner", 0)
                scanner_weighted_dominance = weighted_top_domains.get("scanner", 0)

                if scanner_raw_dominance > 3:
                    self.warnings.append(f"Scanner dominates raw top hotspots: {scanner_raw_dominance}/10")

                if scanner_weighted_dominance < scanner_raw_dominance:
                    reduction = scanner_raw_dominance - scanner_weighted_dominance
                    print(f"   ✅ Weighted centrality reduced scanner dominance by {reduction} positions")

                return {
                    "raw_top_hotspots": raw_hotspots[:10],
                    "weighted_top_hotspots": weighted_hotspots[:10],
                    "raw_top_domains": dict(raw_top_domains),
                    "weighted_top_domains": dict(weighted_top_domains),
                    "scanner_dominance_reduction": scanner_raw_dominance - scanner_weighted_dominance
                }

        except Exception as e:
            raise DomainSegmentationError(f"Hotspot normalization verification failed: {e}")

    def _verify_graph_projection_separation(self) -> Dict[str, Any]:
        """Verify separate graph projections can be created by domain."""
        print("📊 Verifying graph projection separation...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Calculate graph metrics for each domain
                domain_graphs = {}

                for domain in self.VALID_DOMAINS:
                    # Node count
                    cursor.execute("SELECT COUNT(*) FROM nodes WHERE domain = ?", (domain,))
                    node_count = cursor.fetchone()[0]

                    # Edge count (edges where both nodes are in this domain)
                    cursor.execute("""
                        SELECT COUNT(*) FROM edges e
                        JOIN nodes n_src ON e.src_id = n_src.id
                        JOIN nodes n_dst ON e.dst_id = n_dst.id
                        WHERE n_src.domain = ? AND n_dst.domain = ?
                    """, (domain, domain))

                    edge_count = cursor.fetchone()[0]

                    # Cross-domain edges (edges from this domain to others)
                    cursor.execute("""
                        SELECT n_dst.domain, COUNT(*) FROM edges e
                        JOIN nodes n_src ON e.src_id = n_src.id
                        JOIN nodes n_dst ON e.dst_id = n_dst.id
                        WHERE n_src.domain = ? AND n_dst.domain != ? AND n_dst.domain IS NOT NULL
                        GROUP BY n_dst.domain
                    """, (domain, domain))

                    cross_domain_edges = dict(cursor.fetchall())

                    domain_graphs[domain] = {
                        "node_count": node_count,
                        "internal_edge_count": edge_count,
                        "cross_domain_edges": cross_domain_edges,
                        "total_cross_domain_edges": sum(cross_domain_edges.values())
                    }

                print(f"   📊 Domain graph projections:")
                print(f"      Domain | Nodes | Internal Edges | Cross Edges | Isolation")
                print(f"      -------|-------|----------------|------------|----------")

                for domain in sorted(self.VALID_DOMAINS, key=lambda d: domain_graphs[d]["node_count"], reverse=True):
                    graph = domain_graphs[domain]
                    nodes = graph["node_count"]
                    internal = graph["internal_edge_count"]
                    cross = graph["total_cross_domain_edges"]

                    # Calculate isolation metric (higher = more isolated)
                    total_edges = internal + cross
                    isolation = (internal / max(1, total_edges)) * 100 if total_edges > 0 else 0

                    print(f"      {domain:7} | {nodes:5} | {internal:14} | {cross:10} | {isolation:7.1f}%")

                # Check for domain isolation
                runtime_graph = domain_graphs.get("runtime", {})
                runtime_nodes = runtime_graph.get("node_count", 0)
                runtime_cross = runtime_graph.get("total_cross_domain_edges", 0)

                if runtime_nodes > 0:
                    runtime_coupling = (runtime_cross / max(1, runtime_nodes)) * 100
                    if runtime_coupling > 200:  # More than 2 cross edges per node on average
                        self.warnings.append(f"High runtime domain coupling: {runtime_coupling:.1f}%")

                return {
                    "domain_graphs": domain_graphs,
                    "runtime_coupling_percentage": runtime_coupling if runtime_nodes > 0 else 0
                }

        except Exception as e:
            raise DomainSegmentationError(f"Graph projection separation verification failed: {e}")

    def verify(self) -> Dict[str, Any]:
        """Run complete domain segmentation verification."""
        print("🔍 Starting ADG Domain Segmentation Verification...")
        print(f"📁 ADG Directory: {self.adg_dir}")
        print(f"🗄️  SQLite Database: {self.sqlite_path.name}")

        # Verify domain field classification
        classification = self._verify_domain_field_classification()

        # Verify domain distribution balance
        distribution = self._verify_domain_distribution_balance()

        # Calculate weighted centrality
        centrality = self._calculate_weighted_centrality()

        # Verify hotspot normalization
        hotspots = self._verify_hotspot_normalization()

        # Verify graph projection separation
        projections = self._verify_graph_projection_separation()

        # Determine overall status
        critical_issues = (
            not classification.get("classification_complete", False) or
            distribution.get("combined_scanner_test_percentage", 0) > 80
        )

        # Prepare result
        result = {
            "status": "FAIL" if critical_issues else "PASS",
            "domain_classification": classification,
            "domain_distribution": distribution,
            "weighted_centrality": centrality,
            "hotspot_normalization": hotspots,
            "graph_projections": projections,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "classification_complete": classification.get("classification_complete", False),
                "scanner_percentage": distribution.get("scanner_percentage", 0),
                "test_percentage": distribution.get("test_percentage", 0),
                "combined_scanner_test_percentage": distribution.get("combined_scanner_test_percentage", 0),
                "scanner_dominance_reduction": hotspots.get("scanner_dominance_reduction", 0),
                "runtime_coupling_percentage": projections.get("runtime_coupling_percentage", 0)
            }
        }

        # Print results
        if self.errors:
            print("\n❌ DOMAIN SEGMENTATION VERIFICATION FAILED")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")

        if critical_issues:
            print("\n❌ DOMAIN SEGMENTATION ISSUES FOUND")
        else:
            print("\n✅ DOMAIN SEGMENTATION VERIFICATION PASSED")
            print(f"📊 Scanner/test dominance: {distribution.get('combined_scanner_test_percentage', 0):.1f}%")
            print(f"📊 Scanner dominance reduction: {hotspots.get('scanner_dominance_reduction', 0)} positions")

        return result

def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Verify ADG domain segmentation")
    parser.add_argument(
        "--adg-dir",
        type=Path,
        default=Path("artifacts/adg"),
        help="Path to ADG artifacts directory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to save verification report"
    )

    args = parser.parse_args()

    try:
        verifier = ADGDomainSegmentationVerifier(args.adg_dir)
        result = verifier.verify()

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"📄 Report saved to: {args.output}")

        return 0 if result["status"] == "PASS" else 1

    except DomainSegmentationError as e:
        print(f"❌ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
