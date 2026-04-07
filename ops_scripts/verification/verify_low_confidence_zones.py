#!/usr/bin/env python3
"""
ADG Dead Code, Dead Import, and Low-Confidence Zone Control

Tracks and reports on code health issues:
- dead_import_count
- dead_code_candidate_count
- unresolved_import_count
- low_confidence_node_count
- inferred_symbol_ratio
- low_confidence_first_party_ratio

REQUIRE VIEWS:
- by layer
- by domain
- by first_party_only
- by top hotspot file

HARD RULES:
- L4 unresolved import count should trend to zero
- first-party low-confidence identities in core governance surfaces must be aggressively reduced
- unresolved imports must never be silently ignored in executive-quality reports
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class DeadCodeZoneControlError(Exception):
    """Raised when dead code zone control verification fails."""
    pass

class ADGDeadCodeZoneControlVerifier:
    """Verifies dead code, dead imports, and low-confidence zone control."""

    def __init__(self, adg_dir: Path):
        self.adg_dir = Path(adg_dir)
        self.sqlite_path = self._find_sqlite_database()
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def _find_sqlite_database(self) -> Path:
        """Find the latest SQLite database."""
        sqlite_files = list(self.adg_dir.glob("adg_indexed_*.sqlite"))
        if not sqlite_files:
            raise DeadCodeZoneControlError("No SQLite database found")

        return max(sqlite_files, key=lambda p: p.stat().st_mtime)

    def _verify_dead_import_detection(self) -> dict[str, Any]:
        """Verify dead imports are properly detected and categorized."""
        print("🔍 Verifying dead import detection...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Count dead import edges
                cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'dead_imports'")
                total_dead_imports = cursor.fetchone()[0]

                # Get dead imports by layer
                cursor.execute("""
                    SELECT n.layer, COUNT(*) FROM edges e
                    JOIN nodes n ON e.dst_id = n.id
                    WHERE e.relation_type = 'dead_imports'
                    AND n.layer IS NOT NULL
                    GROUP BY n.layer
                    ORDER BY COUNT(*) DESC
                """)

                dead_imports_by_layer = dict(cursor.fetchall())

                # Get dead imports by domain (if domain field exists)
                dead_imports_by_domain = {}
                try:
                    cursor.execute("""
                        SELECT n.domain, COUNT(*) FROM edges e
                        JOIN nodes n ON e.dst_id = n.id
                        WHERE e.relation_type = 'dead_imports'
                        AND n.domain IS NOT NULL
                        GROUP BY n.domain
                        ORDER BY COUNT(*) DESC
                    """)

                    dead_imports_by_domain = dict(cursor.fetchall())
                except sqlite3.OperationalError:
                    self.warnings.append("Domain field not available for dead import analysis")

                # Get dead imports by confidence
                cursor.execute("""
                    SELECT n.confidence, COUNT(*) FROM edges e
                    JOIN nodes n ON e.dst_id = n.id
                    WHERE e.relation_type = 'dead_imports'
                    AND n.confidence IS NOT NULL
                    GROUP BY n.confidence
                    ORDER BY COUNT(*) DESC
                """)

                dead_imports_by_confidence = dict(cursor.fetchall())

                # Get top hotspot files for dead imports
                cursor.execute("""
                    SELECT n.adg_name, COUNT(*) as dead_count FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE e.relation_type = 'dead_imports'
                    AND n.identity_kind NOT IN ('external_module', 'external_provider')
                    GROUP BY n.id, n.adg_name
                    ORDER BY dead_count DESC
                    LIMIT 10
                """)

                dead_import_hotspots = cursor.fetchall()

                print(f"   📊 Total dead imports: {total_dead_imports}")
                print("   📊 Dead imports by layer:")
                for layer, count in list(dead_imports_by_layer.items())[:10]:
                    print(f"      {layer}: {count}")

                if dead_imports_by_domain:
                    print("   📊 Dead imports by domain:")
                    for domain, count in dead_imports_by_domain.items():
                        print(f"      {domain}: {count}")

                print("   📊 Dead imports by confidence:")
                for confidence, count in dead_imports_by_confidence.items():
                    print(f"      {confidence}: {count}")

                print("   📊 Top dead import hotspots:")
                for i, (module, count) in enumerate(dead_import_hotspots[:5]):
                    print(f"      {i+1}. {module}: {count}")

                # Check L4 dead imports (should trend to zero)
                l4_dead_imports = dead_imports_by_layer.get("L4", 0)
                if l4_dead_imports > 5:
                    self.warnings.append(f"L4 has {l4_dead_imports} dead imports (should trend to zero)")

                return {
                    "total_dead_imports": total_dead_imports,
                    "dead_imports_by_layer": dead_imports_by_layer,
                    "dead_imports_by_domain": dead_imports_by_domain,
                    "dead_imports_by_confidence": dead_imports_by_confidence,
                    "dead_import_hotspots": dead_import_hotspots,
                    "l4_dead_imports": l4_dead_imports,
                }

        except Exception as e:
            raise DeadCodeZoneControlError(f"Dead import detection verification failed: {e}")

    def _verify_dead_code_candidate_detection(self) -> dict[str, Any]:
        """Verify dead code candidates are properly detected."""
        print("💀 Verifying dead code candidate detection...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Count dead code candidate edges
                cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'dead_code_candidate'")
                total_dead_code_candidates = cursor.fetchone()[0]

                # Get dead code candidates by layer
                cursor.execute("""
                    SELECT n.layer, COUNT(*) FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE e.relation_type = 'dead_code_candidate'
                    AND n.layer IS NOT NULL
                    GROUP BY n.layer
                    ORDER BY COUNT(*) DESC
                """)

                dead_code_by_layer = dict(cursor.fetchall())

                # Get dead code candidates by entity type
                cursor.execute("""
                    SELECT n.entity_type, COUNT(*) FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE e.relation_type = 'dead_code_candidate'
                    GROUP BY n.entity_type
                    ORDER BY COUNT(*) DESC
                """)

                dead_code_by_entity_type = dict(cursor.fetchall())

                # Get dead code candidates by confidence
                cursor.execute("""
                    SELECT n.confidence, COUNT(*) FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE e.relation_type = 'dead_code_candidate'
                    AND n.confidence IS NOT NULL
                    GROUP BY n.confidence
                    ORDER BY COUNT(*) DESC
                """)

                dead_code_by_confidence = dict(cursor.fetchall())

                print(f"   📊 Total dead code candidates: {total_dead_code_candidates}")
                print("   📊 Dead code by layer:")
                for layer, count in dead_code_by_layer.items():
                    print(f"      {layer}: {count}")

                print("   📊 Dead code by entity type:")
                for entity_type, count in dead_code_by_entity_type.items():
                    print(f"      {entity_type}: {count}")

                print("   📊 Dead code by confidence:")
                for confidence, count in dead_code_by_confidence.items():
                    print(f"      {confidence}: {count}")

                return {
                    "total_dead_code_candidates": total_dead_code_candidates,
                    "dead_code_by_layer": dead_code_by_layer,
                    "dead_code_by_entity_type": dead_code_by_entity_type,
                    "dead_code_by_confidence": dead_code_by_confidence,
                }

        except Exception as e:
            raise DeadCodeZoneControlError(f"Dead code candidate detection verification failed: {e}")

    def _verify_unresolved_import_analysis(self) -> dict[str, Any]:
        """Verify unresolved imports are properly tracked."""
        print("❓ Verifying unresolved import analysis...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Count unresolved import nodes
                cursor.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind = 'unresolved_import'")
                total_unresolved_imports = cursor.fetchone()[0]

                # Get unresolved imports by layer
                cursor.execute("""
                    SELECT layer, COUNT(*) FROM nodes
                    WHERE identity_kind = 'unresolved_import'
                    AND layer IS NOT NULL
                    GROUP BY layer
                    ORDER BY COUNT(*) DESC
                """)

                unresolved_by_layer = dict(cursor.fetchall())

                # Get unresolved imports by confidence
                cursor.execute("""
                    SELECT confidence, COUNT(*) FROM nodes
                    WHERE identity_kind = 'unresolved_import'
                    AND confidence IS NOT NULL
                    GROUP BY confidence
                    ORDER BY COUNT(*) DESC
                """)

                unresolved_by_confidence = dict(cursor.fetchall())

                # Get modules with most unresolved imports
                cursor.execute("""
                    SELECT n_src.adg_name, COUNT(*) as unresolved_count FROM nodes n_unres
                    JOIN edges e ON e.dst_id = n_unres.id
                    JOIN nodes n_src ON e.src_id = n_src.id
                    WHERE n_unres.identity_kind = 'unresolved_import'
                    AND n_src.identity_kind NOT IN ('external_module', 'external_provider')
                    GROUP BY n_src.id, n_src.adg_name
                    ORDER BY unresolved_count DESC
                    LIMIT 10
                """)

                unresolved_hotspots = cursor.fetchall()

                print(f"   📊 Total unresolved imports: {total_unresolved_imports}")
                print("   📊 Unresolved imports by layer:")
                for layer, count in unresolved_by_layer.items():
                    print(f"      {layer}: {count}")

                print("   📊 Unresolved imports by confidence:")
                for confidence, count in unresolved_by_confidence.items():
                    print(f"      {confidence}: {count}")

                print("   📊 Top unresolved import hotspots:")
                for i, (module, count) in enumerate(unresolved_hotspots[:5]):
                    print(f"      {i+1}. {module}: {count}")

                # Check L4 unresolved imports (should be zero)
                l4_unresolved = unresolved_by_layer.get("L4", 0)
                if l4_unresolved > 0:
                    self.errors.append(f"L4 has {l4_unresolved} unresolved imports (should be zero)")

                return {
                    "total_unresolved_imports": total_unresolved_imports,
                    "unresolved_by_layer": unresolved_by_layer,
                    "unresolved_by_confidence": unresolved_by_confidence,
                    "unresolved_hotspots": unresolved_hotspots,
                    "l4_unresolved": l4_unresolved,
                }

        except Exception as e:
            raise DeadCodeZoneControlError(f"Unresolved import analysis verification failed: {e}")

    def _verify_low_confidence_zone_analysis(self) -> dict[str, Any]:
        """Verify low-confidence zones are identified and tracked."""
        print("🔍 Verifying low-confidence zone analysis...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Count low-confidence nodes
                cursor.execute("SELECT COUNT(*) FROM nodes WHERE confidence = 'LOW'")
                total_low_confidence = cursor.fetchone()[0]

                # Get low-confidence nodes by layer
                cursor.execute("""
                    SELECT layer, COUNT(*) FROM nodes
                    WHERE confidence = 'LOW' AND layer IS NOT NULL
                    GROUP BY layer
                    ORDER BY COUNT(*) DESC
                """)

                low_conf_by_layer = dict(cursor.fetchall())

                # Get low-confidence nodes by entity type
                cursor.execute("""
                    SELECT entity_type, COUNT(*) FROM nodes
                    WHERE confidence = 'LOW'
                    GROUP BY entity_type
                    ORDER BY COUNT(*) DESC
                """)

                low_conf_by_entity_type = dict(cursor.fetchall())

                # Get low-confidence nodes by identity kind
                cursor.execute("""
                    SELECT identity_kind, COUNT(*) FROM nodes
                    WHERE confidence = 'LOW'
                    GROUP BY identity_kind
                    ORDER BY COUNT(*) DESC
                """)

                low_conf_by_identity_kind = dict(cursor.fetchall())

                # Calculate first-party low-confidence ratio
                cursor.execute("""
                    SELECT COUNT(*) FROM nodes
                    WHERE confidence = 'LOW'
                    AND identity_kind NOT IN ('external_module', 'external_provider')
                """)

                first_party_low_conf = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(*) FROM nodes
                    WHERE identity_kind NOT IN ('external_module', 'external_provider')
                """)

                total_first_party = cursor.fetchone()[0]

                first_party_low_conf_ratio = (first_party_low_conf / max(1, total_first_party)) * 100

                # Get low-confidence hotspots
                cursor.execute("""
                    SELECT layer, COUNT(*) as low_conf_count FROM nodes
                    WHERE confidence = 'LOW' AND layer IS NOT NULL
                    GROUP BY layer
                    ORDER BY low_conf_count DESC
                    LIMIT 10
                """)

                low_conf_hotspots = cursor.fetchall()

                print(f"   📊 Total low-confidence nodes: {total_low_confidence}")
                print("   📊 Low-confidence by layer:")
                for layer, count in low_conf_by_layer.items():
                    print(f"      {layer}: {count}")

                print("   📊 Low-confidence by entity type:")
                for entity_type, count in low_conf_by_entity_type.items():
                    print(f"      {entity_type}: {count}")

                print("   📊 Low-confidence by identity kind:")
                for identity_kind, count in low_conf_by_identity_kind.items():
                    print(f"      {identity_kind}: {count}")

                print(f"   📊 First-party low-confidence ratio: {first_party_low_conf_ratio:.2f}%")

                # Check for high low-confidence ratio in governance surfaces
                governance_layers = ["L0", "L1", "L2", "L3", "L5"]
                governance_low_conf = sum(low_conf_by_layer.get(layer, 0) for layer in governance_layers)
                governance_total = sum(low_conf_by_layer.get(layer, 0) for layer in governance_layers)

                governance_low_conf_ratio = (governance_low_conf / max(1, governance_total)) * 100

                if governance_low_conf_ratio > 20:
                    self.warnings.append(f"High low-confidence ratio in governance layers: {governance_low_conf_ratio:.1f}%")

                return {
                    "total_low_confidence": total_low_confidence,
                    "low_conf_by_layer": low_conf_by_layer,
                    "low_conf_by_entity_type": low_conf_by_entity_type,
                    "low_conf_by_identity_kind": low_conf_by_identity_kind,
                    "first_party_low_confidence_ratio": first_party_low_conf_ratio,
                    "governance_low_confidence_ratio": governance_low_conf_ratio,
                    "low_conf_hotspots": low_conf_hotspots,
                }

        except Exception as e:
            raise DeadCodeZoneControlError(f"Low-confidence zone analysis verification failed: {e}")

    def _verify_inferred_symbol_analysis(self) -> dict[str, Any]:
        """Verify inferred symbol ratio is tracked."""
        print("🔮 Verifying inferred symbol analysis...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Count inferred symbols
                cursor.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind = 'inferred_symbol'")
                total_inferred = cursor.fetchone()[0]

                # Count all symbols
                cursor.execute("SELECT COUNT(*) FROM nodes WHERE entity_type = 'symbol'")
                total_symbols = cursor.fetchone()[0]

                # Calculate inferred symbol ratio
                inferred_ratio = (total_inferred / max(1, total_symbols)) * 100

                # Get inferred symbols by layer
                cursor.execute("""
                    SELECT n.layer, COUNT(*) FROM nodes n
                    WHERE n.identity_kind = 'inferred_symbol' AND n.layer IS NOT NULL
                    GROUP BY n.layer
                    ORDER BY COUNT(*) DESC
                """)

                inferred_by_layer = dict(cursor.fetchall())

                # Get inferred symbols by confidence
                cursor.execute("""
                    SELECT confidence, COUNT(*) FROM nodes
                    WHERE identity_kind = 'inferred_symbol' AND confidence IS NOT NULL
                    GROUP BY confidence
                    ORDER BY COUNT(*) DESC
                """)

                inferred_by_confidence = dict(cursor.fetchall())

                print(f"   📊 Total inferred symbols: {total_inferred}")
                print(f"   📊 Total symbols: {total_symbols}")
                print(f"   📊 Inferred symbol ratio: {inferred_ratio:.2f}%")
                print("   📊 Inferred symbols by layer:")
                for layer, count in inferred_by_layer.items():
                    print(f"      {layer}: {count}")

                print("   📊 Inferred symbols by confidence:")
                for confidence, count in inferred_by_confidence.items():
                    print(f"      {confidence}: {count}")

                # High inferred ratio may indicate analysis gaps
                if inferred_ratio > 30:
                    self.warnings.append(f"High inferred symbol ratio: {inferred_ratio:.1f}%")

                return {
                    "total_inferred_symbols": total_inferred,
                    "total_symbols": total_symbols,
                    "inferred_symbol_ratio": inferred_ratio,
                    "inferred_by_layer": inferred_by_layer,
                    "inferred_by_confidence": inferred_by_confidence,
                }

        except Exception as e:
            raise DeadCodeZoneControlError(f"Inferred symbol analysis verification failed: {e}")

    def _verify_executive_readiness(self) -> dict[str, Any]:
        """Verify executive-quality reporting capabilities."""
        print("📊 Verifying executive readiness...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Executive metrics should be available by different views
                executive_metrics = {
                    "dead_import_count": "SELECT COUNT(*) FROM edges WHERE relation_type = 'dead_imports'",
                    "dead_code_count": "SELECT COUNT(*) FROM edges WHERE relation_type = 'dead_code_candidate'",
                    "unresolved_import_count": "SELECT COUNT(*) FROM nodes WHERE identity_kind = 'unresolved_import'",
                    "low_confidence_count": "SELECT COUNT(*) FROM nodes WHERE confidence = 'LOW'",
                    "inferred_symbol_ratio": "calculated",  # Special case
                }

                # Calculate all metrics
                calculated_metrics = {}
                for metric_name, query in executive_metrics.items():
                    if query == "calculated":
                        # Special handling for inferred symbol ratio
                        cursor.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind = 'inferred_symbol'")
                        inferred = cursor.fetchone()[0]
                        cursor.execute("SELECT COUNT(*) FROM nodes WHERE entity_type = 'symbol'")
                        total_symbols = cursor.fetchone()[0]
                        ratio = (inferred / max(1, total_symbols)) * 100
                        calculated_metrics[metric_name] = ratio
                    else:
                        cursor.execute(query)
                        calculated_metrics[metric_name] = cursor.fetchone()[0]

                # Calculate first-party-only versions
                first_party_metrics = {}
                for metric_name, query in executive_metrics.items():
                    if query == "calculated":
                        continue  # Skip calculated metrics for now

                    # Add first-party filter
                    if "edges" in query:
                        fp_query = query.replace("FROM edges", "FROM edges e JOIN nodes n ON e.src_id = n.id") + " AND n.identity_kind NOT IN ('external_module', 'external_provider')"
                    elif "nodes" in query:
                        fp_query = query + " AND identity_kind NOT IN ('external_module', 'external_provider')"
                    else:
                        fp_query = query

                    try:
                        cursor.execute(fp_query)
                        first_party_metrics[metric_name] = cursor.fetchone()[0]
                    except sqlite3.OperationalError:
                        first_party_metrics[metric_name] = None

                print("   📊 Executive metrics:")
                print("      Metric | All | First-Party | FP Ratio")
                print("      -------|-----|-------------|---------")

                for metric_name in executive_metrics.keys():
                    all_val = calculated_metrics[metric_name]
                    fp_val = first_party_metrics.get(metric_name)

                    if fp_val is not None and all_val > 0:
                        fp_ratio = (fp_val / all_val) * 100
                        print(f"      {metric_name:20} | {all_val:4} | {fp_val:11} | {fp_ratio:7.1f}%")
                    else:
                        print(f"      {metric_name:20} | {all_val:4} | {'N/A':>11} | {'N/A':>7}")

                # Check for executive readiness issues
                readiness_issues = []

                if calculated_metrics.get("l4_unresolved_import", 0) > 0:
                    readiness_issues.append("L4 has unresolved imports")

                if calculated_metrics.get("first_party_low_confidence_ratio", 0) > 15:
                    readiness_issues.append("High first-party low-confidence ratio")

                if calculated_metrics.get("inferred_symbol_ratio", 0) > 25:
                    readiness_issues.append("High inferred symbol ratio")

                return {
                    "executive_metrics": calculated_metrics,
                    "first_party_metrics": first_party_metrics,
                    "readiness_issues": readiness_issues,
                    "executive_ready": len(readiness_issues) == 0,
                }

        except Exception as e:
            raise DeadCodeZoneControlError(f"Executive readiness verification failed: {e}")

    def verify(self) -> dict[str, Any]:
        """Run complete dead code and low-confidence zone verification."""
        print("🔍 Starting ADG Dead Code Zone Control Verification...")
        print(f"📁 ADG Directory: {self.adg_dir}")
        print(f"🗄️  SQLite Database: {self.sqlite_path.name}")

        # Verify dead import detection
        dead_imports = self._verify_dead_import_detection()

        # Verify dead code candidate detection
        dead_code = self._verify_dead_code_candidate_detection()

        # Verify unresolved import analysis
        unresolved = self._verify_unresolved_import_analysis()

        # Verify low-confidence zone analysis
        low_confidence = self._verify_low_confidence_zone_analysis()

        # Verify inferred symbol analysis
        inferred = self._verify_inferred_symbol_analysis()

        # Verify executive readiness
        executive = self._verify_executive_readiness()

        # Determine overall status
        critical_issues = (
            unresolved.get("l4_unresolved", 0) > 0 or
            not executive.get("executive_ready", True)
        )

        # Prepare result
        result = {
            "status": "FAIL" if critical_issues else "PASS",
            "dead_imports": dead_imports,
            "dead_code_candidates": dead_code,
            "unresolved_imports": unresolved,
            "low_confidence_zones": low_confidence,
            "inferred_symbols": inferred,
            "executive_readiness": executive,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "total_dead_imports": dead_imports.get("total_dead_imports", 0),
                "total_dead_code_candidates": dead_code.get("total_dead_code_candidates", 0),
                "total_unresolved_imports": unresolved.get("total_unresolved_imports", 0),
                "total_low_confidence": low_confidence.get("total_low_confidence", 0),
                "l4_unresolved_imports": unresolved.get("l4_unresolved", 0),
                "first_party_low_confidence_ratio": low_confidence.get("first_party_low_confidence_ratio", 0),
                "inferred_symbol_ratio": inferred.get("inferred_symbol_ratio", 0),
                "executive_ready": executive.get("executive_ready", False),
            },
        }

        # Print results
        if self.errors:
            print("\n❌ DEAD CODE ZONE CONTROL VERIFICATION FAILED")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")

        if critical_issues:
            print("\n❌ DEAD CODE ZONE CONTROL ISSUES FOUND")
            print(f"   • L4 unresolved imports: {result['summary']['l4_unresolved_imports']}")
            print(f"   • Executive ready: {result['summary']['executive_ready']}")
        else:
            print("\n✅ DEAD CODE ZONE CONTROL VERIFICATION PASSED")
            print(f"📊 Dead imports: {result['summary']['total_dead_imports']}")
            print(f"📊 Unresolved imports: {result['summary']['total_unresolved_imports']}")
            print(f"📊 Low confidence: {result['summary']['total_low_confidence']}")

        return result

def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Verify ADG dead code zone control")
    parser.add_argument(
        "--adg-dir",
        type=Path,
        default=Path("artifacts/adg"),
        help="Path to ADG artifacts directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to save verification report",
    )

    args = parser.parse_args()

    try:
        verifier = ADGDeadCodeZoneControlVerifier(args.adg_dir)
        result = verifier.verify()

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"📄 Report saved to: {args.output}")

        return 0 if result["status"] == "PASS" else 1

    except DeadCodeZoneControlError as e:    # guardian: DeadCodeZoneControlError should be handled with specific context
        print(f"❌ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
