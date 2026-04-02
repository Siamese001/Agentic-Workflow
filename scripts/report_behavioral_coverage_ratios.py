#!/usr/bin/env python3
"""
ADG Runtime vs Structural Balance Reporting

Reports on the balance between runtime-semantic coverage and structural analysis:
- runtime_semantic_edge_count
- structural_edge_count
- runtime_coverage_ratio
- structural_dominance_ratio
- layer_balance_report
- domain_balance_report

REQUIRE:
- balanced reporting to prevent scanner/test dominance in risk assessment
- separate views for runtime-first vs structural-first analysis
- trend analysis capabilities for coverage improvement over time
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

class RuntimeStructuralBalanceError(Exception):
    """Raised when runtime/structural balance verification fails."""
    pass

class ADGRuntimeStructuralBalanceVerifier:
    """Verifies runtime vs structural balance reporting."""

    # Runtime-semantic edge types
    RUNTIME_SEMANTIC_EDGES = {
        "records_execution_trace", "signs_execution_trace", "emits_replay_key",
        "execution_terminates_at_uwg", "validated_by_safety_plane", "validated_by_llm_gateway",
        "writes_to", "writes_through", "invokes_provider", "invokes_dynamic",
        "applies_guardrail", "verifies_policy", "stores_validation_artifact",
        "captures_execution_output", "records_tool_invocation"
    }

    # Structural edge types
    STRUCTURAL_EDGES = {
        "imports", "calls", "belongs_to_layer", "implements", "instantiates",
        "produces", "consumes", "decorated_by", "exports", "re_exports"
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
            raise RuntimeStructuralBalanceError("No SQLite database found")

        return max(sqlite_files, key=lambda p: p.stat().st_mtime)

    def _verify_runtime_semantic_edge_detection(self) -> Dict[str, Any]:
        """Verify runtime-semantic edges are properly detected."""
        print("🏃 Verifying runtime-semantic edge detection...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Count runtime-semantic edges
                runtime_counts = {}
                total_runtime = 0

                for edge_type in self.RUNTIME_SEMANTIC_EDGES:
                    cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (edge_type,))
                    count = cursor.fetchone()[0]
                    runtime_counts[edge_type] = count
                    total_runtime += count

                print(f"   📊 Runtime-semantic edges found: {total_runtime}")
                print(f"   📊 Runtime edge distribution:")
                for edge_type, count in sorted(runtime_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"      {edge_type}: {count}")

                # Get runtime edges by layer
                cursor.execute("""
                    SELECT n.layer, COUNT(*) FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE e.relation_type IN ({}) AND n.layer IS NOT NULL
                    GROUP BY n.layer
                    ORDER BY COUNT(*) DESC
                """.format(','.join(['?' for _ in self.RUNTIME_SEMANTIC_EDGES])), list(self.RUNTIME_SEMANTIC_EDGES))

                runtime_by_layer = dict(cursor.fetchall())

                print(f"   📊 Runtime edges by layer:")
                for layer, count in runtime_by_layer.items():
                    print(f"      {layer}: {count}")

                return {
                    "total_runtime_edges": total_runtime,
                    "runtime_edge_counts": runtime_counts,
                    "runtime_by_layer": runtime_by_layer
                }

        except Exception as e:
            raise RuntimeStructuralBalanceError(f"Runtime-semantic edge detection failed: {e}")

    def _verify_structural_edge_detection(self) -> Dict[str, Any]:
        """Verify structural edges are properly detected."""
        print("🏗️  Verifying structural edge detection...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Count structural edges
                structural_counts = {}
                total_structural = 0

                for edge_type in self.STRUCTURAL_EDGES:
                    cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (edge_type,))
                    count = cursor.fetchone()[0]
                    structural_counts[edge_type] = count
                    total_structural += count

                print(f"   📊 Structural edges found: {total_structural}")
                print(f"   📊 Structural edge distribution:")
                for edge_type, count in sorted(structural_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"      {edge_type}: {count}")

                # Get structural edges by layer
                cursor.execute("""
                    SELECT n.layer, COUNT(*) FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE e.relation_type IN ({}) AND n.layer IS NOT NULL
                    GROUP BY n.layer
                    ORDER BY COUNT(*) DESC
                """.format(','.join(['?' for _ in self.STRUCTURAL_EDGES])), list(self.STRUCTURAL_EDGES))

                structural_by_layer = dict(cursor.fetchall())

                print(f"   📊 Structural edges by layer:")
                for layer, count in structural_by_layer.items():
                    print(f"      {layer}: {count}")

                return {
                    "total_structural_edges": total_structural,
                    "structural_edge_counts": structural_counts,
                    "structural_by_layer": structural_by_layer
                }

        except Exception as e:
            raise RuntimeStructuralBalanceError(f"Structural edge detection failed: {e}")

    def _calculate_balance_metrics(self) -> Dict[str, Any]:
        """Calculate balance metrics between runtime and structural."""
        print("⚖️  Calculating balance metrics...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Get total edge counts
                cursor.execute("SELECT COUNT(*) FROM edges")
                total_edges = cursor.fetchone()[0]

                # Count runtime and structural edges
                runtime_placeholders = ','.join(['?' for _ in self.RUNTIME_SEMANTIC_EDGES])
                structural_placeholders = ','.join(['?' for _ in self.STRUCTURAL_EDGES])

                cursor.execute(f"SELECT COUNT(*) FROM edges WHERE relation_type IN ({runtime_placeholders})",
                             list(self.RUNTIME_SEMANTIC_EDGES))
                runtime_count = cursor.fetchone()[0]

                cursor.execute(f"SELECT COUNT(*) FROM edges WHERE relation_type IN ({structural_placeholders})",
                             list(self.STRUCTURAL_EDGES))
                structural_count = cursor.fetchone()[0]

                # Calculate ratios
                runtime_coverage_ratio = (runtime_count / max(1, total_edges)) * 100
                structural_dominance_ratio = (structural_count / max(1, total_edges)) * 100

                # Calculate balance score (ideal is around 50-50 for balanced analysis)
                balance_ratio = runtime_count / max(1, structural_count)
                balance_score = 100 - abs(50 - (balance_ratio * 100))  # Score closer to 100 is better

                print(f"   📊 Total edges: {total_edges}")
                print(f"   📊 Runtime-semantic edges: {runtime_count} ({runtime_coverage_ratio:.1f}%)")
                print(f"   📊 Structural edges: {structural_count} ({structural_dominance_ratio:.1f}%)")
                print(f"   📊 Balance ratio: {balance_ratio:.2f}")
                print(f"   📊 Balance score: {balance_score:.1f}/100")

                # Check for imbalance
                if runtime_coverage_ratio < 20:
                    self.warnings.append(f"Low runtime coverage: {runtime_coverage_ratio:.1f}%")

                if structural_dominance_ratio > 80:
                    self.warnings.append(f"High structural dominance: {structural_dominance_ratio:.1f}%")

                return {
                    "total_edges": total_edges,
                    "runtime_edges": runtime_count,
                    "structural_edges": structural_count,
                    "runtime_coverage_ratio": runtime_coverage_ratio,
                    "structural_dominance_ratio": structural_dominance_ratio,
                    "balance_ratio": balance_ratio,
                    "balance_score": balance_score
                }

        except Exception as e:
            raise RuntimeStructuralBalanceError(f"Balance metrics calculation failed: {e}")

    def _verify_layer_balance_analysis(self) -> Dict[str, Any]:
        """Verify balance analysis by architectural layer."""
        print("🏗️  Verifying layer balance analysis...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Analyze balance by layer
                layer_balance = {}

                cursor.execute("SELECT DISTINCT layer FROM nodes WHERE layer IS NOT NULL")
                layers = [row[0] for row in cursor.fetchall()]

                for layer in layers:
                    # Count runtime edges in this layer
                    runtime_placeholders = ','.join(['?' for _ in self.RUNTIME_SEMANTIC_EDGES])
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM edges e
                        JOIN nodes n ON e.src_id = n.id
                        WHERE n.layer = ? AND e.relation_type IN ({runtime_placeholders})
                    """, [layer] + list(self.RUNTIME_SEMANTIC_EDGES))

                    runtime_count = cursor.fetchone()[0]

                    # Count structural edges in this layer
                    structural_placeholders = ','.join(['?' for _ in self.STRUCTURAL_EDGES])
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM edges e
                        JOIN nodes n ON e.src_id = n.id
                        WHERE n.layer = ? AND e.relation_type IN ({structural_placeholders})
                    """, [layer] + list(self.STRUCTURAL_EDGES))

                    structural_count = cursor.fetchone()[0]

                    # Calculate layer balance
                    total_layer_edges = runtime_count + structural_count
                    runtime_percentage = (runtime_count / max(1, total_layer_edges)) * 100
                    structural_percentage = (structural_count / max(1, total_layer_edges)) * 100

                    layer_balance[layer] = {
                        "runtime_edges": runtime_count,
                        "structural_edges": structural_count,
                        "total_edges": total_layer_edges,
                        "runtime_percentage": runtime_percentage,
                        "structural_percentage": structural_percentage
                    }

                print(f"   📊 Layer balance analysis:")
                print(f"      Layer | Runtime | Structural | Total | Runtime % | Structural %")
                print(f"      -------|---------|------------|-------|-----------|-------------")

                for layer in sorted(layer_balance.keys()):
                    balance = layer_balance[layer]
                    print(f"      {layer:6} | {balance['runtime_edges']:7} | {balance['structural_edges']:10} | "
                          f"{balance['total_edges']:5} | {balance['runtime_percentage']:9.1f}% | "
                          f"{balance['structural_percentage']:11.1f}%")

                # Identify imbalanced layers
                imbalanced_layers = []
                for layer, balance in layer_balance.items():
                    if balance["runtime_percentage"] < 10 or balance["runtime_percentage"] > 90:
                        imbalanced_layers.append({
                            "layer": layer,
                            "runtime_percentage": balance["runtime_percentage"],
                            "structural_percentage": balance["structural_percentage"]
                        })

                if imbalanced_layers:
                    print(f"   ⚠️  Imbalanced layers: {len(imbalanced_layers)}")
                    for layer_info in imbalanced_layers[:5]:
                        print(f"      {layer_info['layer']}: {layer_info['runtime_percentage']:.1f}% runtime")

                return {
                    "layer_balance": layer_balance,
                    "imbalanced_layers": imbalanced_layers,
                    "total_imbalanced_layers": len(imbalanced_layers)
                }

        except Exception as e:
            raise RuntimeStructuralBalanceError(f"Layer balance analysis failed: {e}")

    def _verify_domain_balance_analysis(self) -> Dict[str, Any]:
        """Verify balance analysis by domain."""
        print("🌐 Verifying domain balance analysis...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Check if domain field exists
                cursor.execute("PRAGMA table_info(nodes)")
                columns = {row[1]: row for row in cursor.fetchall()}

                if "domain" not in columns:
                    self.warnings.append("Domain field not available for balance analysis")
                    return {"domain_available": False}

                # Analyze balance by domain
                cursor.execute("SELECT DISTINCT domain FROM nodes WHERE domain IS NOT NULL")
                domains = [row[0] for row in cursor.fetchall()]

                domain_balance = {}

                for domain in domains:
                    # Count runtime edges in this domain
                    runtime_placeholders = ','.join(['?' for _ in self.RUNTIME_SEMANTIC_EDGES])
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM edges e
                        JOIN nodes n ON e.src_id = n.id
                        WHERE n.domain = ? AND e.relation_type IN ({runtime_placeholders})
                    """, [domain] + list(self.RUNTIME_SEMANTIC_EDGES))

                    runtime_count = cursor.fetchone()[0]

                    # Count structural edges in this domain
                    structural_placeholders = ','.join(['?' for _ in self.STRUCTURAL_EDGES])
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM edges e
                        JOIN nodes n ON e.src_id = n.id
                        WHERE n.domain = ? AND e.relation_type IN ({structural_placeholders})
                    """, [domain] + list(self.STRUCTURAL_EDGES))

                    structural_count = cursor.fetchone()[0]

                    # Calculate domain balance
                    total_domain_edges = runtime_count + structural_count
                    runtime_percentage = (runtime_count / max(1, total_domain_edges)) * 100
                    structural_percentage = (structural_count / max(1, total_domain_edges)) * 100

                    domain_balance[domain] = {
                        "runtime_edges": runtime_count,
                        "structural_edges": structural_count,
                        "total_edges": total_domain_edges,
                        "runtime_percentage": runtime_percentage,
                        "structural_percentage": structural_percentage
                    }

                print(f"   📊 Domain balance analysis:")
                print(f"      Domain | Runtime | Structural | Total | Runtime % | Structural %")
                print(f"      -------|---------|------------|-------|-----------|-------------")

                for domain in sorted(domain_balance.keys()):
                    balance = domain_balance[domain]
                    print(f"      {domain:7} | {balance['runtime_edges']:7} | {balance['structural_edges']:10} | "
                          f"{balance['total_edges']:5} | {balance['runtime_percentage']:9.1f}% | "
                          f"{balance['structural_percentage']:11.1f}%")

                # Check for domain-specific issues
                runtime_domain = domain_balance.get("runtime", {})
                test_domain = domain_balance.get("test", {})
                scanner_domain = domain_balance.get("scanner", {})

                domain_issues = []

                if runtime_domain and runtime_domain.get("runtime_percentage", 0) < 70:
                    domain_issues.append("Runtime domain has low runtime edge percentage")

                if test_domain and test_domain.get("structural_percentage", 0) > 80:
                    domain_issues.append("Test domain has high structural dominance")

                if scanner_domain and scanner_domain.get("structural_percentage", 0) > 90:
                    domain_issues.append("Scanner domain has extreme structural dominance")

                if domain_issues:
                    print(f"   ⚠️  Domain issues: {len(domain_issues)}")
                    for issue in domain_issues:
                        print(f"      • {issue}")

                return {
                    "domain_available": True,
                    "domain_balance": domain_balance,
                    "domain_issues": domain_issues
                }

        except Exception as e:
            raise RuntimeStructuralBalanceError(f"Domain balance analysis failed: {e}")

    def _verify_first_party_balance_analysis(self) -> Dict[str, Any]:
        """Verify balance analysis for first-party modules only."""
        print("🎯 Verifying first-party balance analysis...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Count runtime edges for first-party modules
                runtime_placeholders = ','.join(['?' for _ in self.RUNTIME_SEMANTIC_EDGES])
                cursor.execute(f"""
                    SELECT COUNT(*) FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE n.identity_kind NOT IN ('external_module', 'external_provider')
                    AND e.relation_type IN ({runtime_placeholders})
                """, list(self.RUNTIME_SEMANTIC_EDGES))

                fp_runtime_count = cursor.fetchone()[0]

                # Count structural edges for first-party modules
                structural_placeholders = ','.join(['?' for _ in self.STRUCTURAL_EDGES])
                cursor.execute(f"""
                    SELECT COUNT(*) FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE n.identity_kind NOT IN ('external_module', 'external_provider')
                    AND e.relation_type IN ({structural_placeholders})
                """, list(self.STRUCTURAL_EDGES))

                fp_structural_count = cursor.fetchone()[0]

                # Calculate first-party balance
                total_fp_edges = fp_runtime_count + fp_structural_count
                fp_runtime_percentage = (fp_runtime_count / max(1, total_fp_edges)) * 100
                fp_structural_percentage = (fp_structural_count / max(1, total_fp_edges)) * 100

                print(f"   📊 First-party balance analysis:")
                print(f"      Runtime edges: {fp_runtime_count} ({fp_runtime_percentage:.1f}%)")
                print(f"      Structural edges: {fp_structural_count} ({fp_structural_percentage:.1f}%)")
                print(f"      Total first-party edges: {total_fp_edges}")

                # Compare with overall balance
                cursor.execute(f"SELECT COUNT(*) FROM edges WHERE relation_type IN ({runtime_placeholders})",
                             list(self.RUNTIME_SEMANTIC_EDGES))
                total_runtime = cursor.fetchone()[0]

                cursor.execute(f"SELECT COUNT(*) FROM edges WHERE relation_type IN ({structural_placeholders})",
                             list(self.STRUCTURAL_EDGES))
                total_structural = cursor.fetchone()[0]

                overall_runtime_pct = (fp_runtime_count / max(1, total_runtime)) * 100
                overall_structural_pct = (fp_structural_count / max(1, total_structural)) * 100

                print(f"   📊 First-party contribution to overall:")
                print(f"      Runtime: {overall_runtime_pct:.1f}%")
                print(f"      Structural: {overall_structural_pct:.1f}%")

                return {
                    "first_party_runtime_edges": fp_runtime_count,
                    "first_party_structural_edges": fp_structural_count,
                    "first_party_runtime_percentage": fp_runtime_percentage,
                    "first_party_structural_percentage": fp_structural_percentage,
                    "overall_runtime_contribution": overall_runtime_pct,
                    "overall_structural_contribution": overall_structural_pct
                }

        except Exception as e:
            raise RuntimeStructuralBalanceError(f"First-party balance analysis failed: {e}")

    def verify(self) -> Dict[str, Any]:
        """Run complete runtime vs structural balance verification."""
        print("🔍 Starting ADG Runtime vs Structural Balance Verification...")
        print(f"📁 ADG Directory: {self.adg_dir}")
        print(f"🗄️  SQLite Database: {self.sqlite_path.name}")

        # Verify runtime-semantic edge detection
        runtime = self._verify_runtime_semantic_edge_detection()

        # Verify structural edge detection
        structural = self._verify_structural_edge_detection()

        # Calculate balance metrics
        balance = self._calculate_balance_metrics()

        # Verify layer balance analysis
        layer_balance = self._verify_layer_balance_analysis()

        # Verify domain balance analysis
        domain_balance = self._verify_domain_balance_analysis()

        # Verify first-party balance analysis
        fp_balance = self._verify_first_party_balance_analysis()

        # Determine overall status
        critical_issues = (
            balance.get("runtime_coverage_ratio", 0) < 10 or
            balance.get("balance_score", 0) < 30
        )

        # Prepare result
        result = {
            "status": "FAIL" if critical_issues else "PASS",
            "runtime_semantic": runtime,
            "structural": structural,
            "balance_metrics": balance,
            "layer_balance": layer_balance,
            "domain_balance": domain_balance,
            "first_party_balance": fp_balance,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "total_edges": balance.get("total_edges", 0),
                "runtime_edges": balance.get("runtime_edges", 0),
                "structural_edges": balance.get("structural_edges", 0),
                "runtime_coverage_ratio": balance.get("runtime_coverage_ratio", 0),
                "structural_dominance_ratio": balance.get("structural_dominance_ratio", 0),
                "balance_score": balance.get("balance_score", 0),
                "imbalanced_layers": layer_balance.get("total_imbalanced_layers", 0),
                "first_party_runtime_percentage": fp_balance.get("first_party_runtime_percentage", 0)
            }
        }

        # Print results
        if self.errors:
            print("\n❌ RUNTIME/STRUCTURAL BALANCE VERIFICATION FAILED")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")

        if critical_issues:
            print("\n❌ RUNTIME/STRUCTURAL BALANCE ISSUES FOUND")
            print(f"   • Runtime coverage: {result['summary']['runtime_coverage_ratio']:.1f}%")
            print(f"   • Balance score: {result['summary']['balance_score']:.1f}/100")
        else:
            print("\n✅ RUNTIME/STRUCTURAL BALANCE VERIFICATION PASSED")
            print(f"📊 Runtime coverage: {result['summary']['runtime_coverage_ratio']:.1f}%")
            print(f"📊 Balance score: {result['summary']['balance_score']:.1f}/100")
            print(f"📊 First-party runtime: {result['summary']['first_party_runtime_percentage']:.1f}%")

        return result

def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Verify ADG runtime vs structural balance")
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
        verifier = ADGRuntimeStructuralBalanceVerifier(args.adg_dir)
        result = verifier.verify()

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"📄 Report saved to: {args.output}")

        return 0 if result["status"] == "PASS" else 1

    except RuntimeStructuralBalanceError as e:    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context    # guardian: RuntimeStructuralBalanceError should be handled with specific context
        print(f"❌ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())