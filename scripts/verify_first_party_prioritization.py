#!/usr/bin/env python3
"""
ADG First-Party Prioritization and External Signal Control

Implements identity_origin classification and first-party-only analytics views:
- identity_origin = first_party | external | generated | unknown
- First-party-only SQL views and reporting
- Executive remediation rankings using first-party data
- External signal dilution control

DEFAULT EXECUTIVE / RISK / REMEDIATION VIEWS MUST USE: first_party_only
REQUIRE ALL COUNTS TO BE AVAILABLE IN BOTH FORMS: raw_all, first_party_only
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class FirstPartyPrioritizationError(Exception):
    """Raised when first-party prioritization verification fails."""
    pass

class ADGFirstPartyPrioritizationVerifier:
    """Verifies first-party prioritization and external signal control."""
    
    VALID_IDENTITY_ORIGINS = {"first_party", "external", "generated", "unknown"}
    
    # Identity classification rules
    IDENTITY_CLASSIFICATION_RULES = {
        "first_party": {
            "identity_kinds": {"repo_module"},
            "path_patterns": ["agentic_core/", "apps_", "tests/"],
            "exclude_patterns": ["site-packages", ".venv", "venv"]
        },
        "external": {
            "identity_kinds": {"external_module", "external_provider"},
            "path_patterns": ["site-packages", "dist-packages"],
            "common_prefixes": ["requests", "numpy", "pandas", "torch", "tensorflow"]
        },
        "generated": {
            "identity_kinds": {"generated_symbol"},
            "path_patterns": [".pyi", "_pb2.py", "protobuf"]
        },
        "unknown": {
            "identity_kinds": {"unresolved_import", "unknown_symbol"},
            "default_fallback": True
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
            raise FirstPartyPrioritizationError("No SQLite database found")
        
        return max(sqlite_files, key=lambda p: p.stat().st_mtime)
    
    def _verify_identity_origin_classification(self) -> Dict[str, Any]:
        """Verify identity_origin field exists and has valid values."""
        print("🏷️  Verifying identity_origin classification...")
        
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                
                # Check if identity_origin field exists
                cursor.execute("PRAGMA table_info(nodes)")
                columns = {row[1]: row for row in cursor.fetchall()}
                
                if "identity_origin" not in columns:
                    self.errors.append("identity_origin field missing from nodes table")
                    return {"field_exists": False, "classification_complete": False}
                
                print(f"   ✅ identity_origin field exists")
                
                # Get current identity_origin distribution
                cursor.execute("""
                    SELECT identity_origin, COUNT(*) FROM nodes 
                    WHERE identity_origin IS NOT NULL
                    GROUP BY identity_origin
                """)
                
                current_distribution = dict(cursor.fetchall())
                
                # Check for invalid values
                invalid_values = set(current_distribution.keys()) - self.VALID_IDENTITY_ORIGINS
                if invalid_values:
                    self.errors.append(f"Invalid identity_origin values: {invalid_values}")
                
                # Check for unclassified nodes
                cursor.execute("SELECT COUNT(*) FROM nodes WHERE identity_origin IS NULL")
                unclassified_count = cursor.fetchone()[0]
                
                if unclassified_count > 0:
                    self.warnings.append(f"{unclassified_count} nodes have NULL identity_origin")
                
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
            raise FirstPartyPrioritizationError(f"Identity origin classification verification failed: {e}")
    
    def _verify_first_party_vs_external_separation(self) -> Dict[str, Any]:
        """Verify proper separation between first-party and external modules."""
        print("🔍 Verifying first-party vs external separation...")
        
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                
                # Get module counts by identity_origin
                cursor.execute("""
                    SELECT identity_origin, COUNT(*) FROM nodes 
                    WHERE entity_type = 'module'
                    GROUP BY identity_origin
                """)
                
                module_distribution = dict(cursor.fetchall())
                
                # Get total module count
                cursor.execute("SELECT COUNT(*) FROM nodes WHERE entity_type = 'module'")
                total_modules = cursor.fetchone()[0]
                
                # Calculate percentages
                first_party_count = module_distribution.get("first_party", 0)
                external_count = module_distribution.get("external", 0)
                first_party_percentage = (first_party_count / max(1, total_modules)) * 100
                external_percentage = (external_count / max(1, total_modules)) * 100
                
                print(f"   📊 Total modules: {total_modules}")
                print(f"   📊 First-party: {first_party_count} ({first_party_percentage:.1f}%)")
                print(f"   📊 External: {external_count} ({external_percentage:.1f}%)")
                
                # Check for external dominance in critical areas
                if external_percentage > 80:
                    self.warnings.append(f"External modules dominate ({external_percentage:.1f}% of total)")
                
                # Analyze by layer
                cursor.execute("""
                    SELECT layer, identity_origin, COUNT(*) FROM nodes 
                    WHERE entity_type = 'module'
                    GROUP BY layer, identity_origin
                    ORDER BY layer, identity_origin
                """)
                
                layer_breakdown = {}
                for row in cursor.fetchall():
                    layer, origin, count = row
                    if layer not in layer_breakdown:
                        layer_breakdown[layer] = {}
                    layer_breakdown[layer][origin] = count
                
                print(f"   📊 Layer breakdown:")
                for layer, origins in sorted(layer_breakdown.items()):
                    total_layer = sum(origins.values())
                    fp_count = origins.get("first_party", 0)
                    fp_pct = (fp_count / max(1, total_layer)) * 100
                    print(f"      {layer}: {fp_count}/{total_layer} first-party ({fp_pct:.1f}%)")
                
                return {
                    "total_modules": total_modules,
                    "first_party_count": first_party_count,
                    "external_count": external_count,
                    "first_party_percentage": first_party_percentage,
                    "external_percentage": external_percentage,
                    "module_distribution": module_distribution,
                    "layer_breakdown": layer_breakdown
                }
                
        except Exception as e:
            raise FirstPartyPrioritizationError(f"First-party separation verification failed: {e}")
    
    def _verify_first_party_only_views(self) -> Dict[str, Any]:
        """Verify first-party-only analytics views and metrics."""
        print("👁️  Verifying first-party-only analytics views...")
        
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                
                # Define key metrics that should have first-party-only versions
                key_metrics = {
                    "node_count": "SELECT COUNT(*) FROM nodes WHERE identity_origin = 'first_party'",
                    "edge_count": "SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id = n.id WHERE n.identity_origin = 'first_party'",
                    "violation_count": """
                        SELECT COUNT(*) FROM edges e 
                        JOIN nodes n ON e.src_id = n.id 
                        WHERE n.identity_origin = 'first_party' 
                        AND e.relation_type IN ('violates', 'layer_violation', 'uwg_bypass')
                    """,
                    "trace_coverage": """
                        SELECT COUNT(DISTINCT e.src_id) FROM edges e 
                        JOIN nodes n ON e.src_id = n.id 
                        WHERE n.identity_origin = 'first_party' 
                        AND e.relation_type = 'records_execution_trace'
                    """,
                    "uwg_compliance": """
                        SELECT COUNT(DISTINCT e.src_id) FROM edges e 
                        JOIN nodes n ON e.src_id = n.id 
                        WHERE n.identity_origin = 'first_party' 
                        AND e.relation_type = 'execution_terminates_at_uwg'
                    """
                }
                
                first_party_metrics = {}
                all_metrics = {}
                
                # Calculate first-party-only metrics
                for metric_name, query in key_metrics.items():
                    try:
                        cursor.execute(query)
                        fp_count = cursor.fetchone()[0]
                        first_party_metrics[metric_name] = fp_count
                    except Exception as e:
                        self.warnings.append(f"Failed to calculate first-party {metric_name}: {e}")
                        first_party_metrics[metric_name] = None
                
                # Calculate corresponding all-node metrics for comparison
                all_queries = {
                    "node_count": "SELECT COUNT(*) FROM nodes",
                    "edge_count": "SELECT COUNT(*) FROM edges",
                    "violation_count": "SELECT COUNT(*) FROM edges WHERE relation_type IN ('violates', 'layer_violation', 'uwg_bypass')",
                    "trace_coverage": "SELECT COUNT(DISTINCT src_id) FROM edges WHERE relation_type = 'records_execution_trace'",
                    "uwg_compliance": "SELECT COUNT(DISTINCT src_id) FROM edges WHERE relation_type = 'execution_terminates_at_uwg'"
                }
                
                for metric_name, query in all_queries.items():
                    try:
                        cursor.execute(query)
                        all_count = cursor.fetchone()[0]
                        all_metrics[metric_name] = all_count
                    except Exception as e:
                        self.warnings.append(f"Failed to calculate all {metric_name}: {e}")
                        all_metrics[metric_name] = None
                
                # Calculate first-party percentages
                metric_comparison = {}
                for metric_name in key_metrics.keys():
                    fp_val = first_party_metrics.get(metric_name)
                    all_val = all_metrics.get(metric_name)
                    
                    if fp_val is not None and all_val is not None and all_val > 0:
                        fp_percentage = (fp_val / all_val) * 100
                        metric_comparison[metric_name] = {
                            "first_party": fp_val,
                            "all_nodes": all_val,
                            "first_party_percentage": fp_percentage
                        }
                    else:
                        metric_comparison[metric_name] = {
                            "first_party": fp_val,
                            "all_nodes": all_val,
                            "first_party_percentage": None
                        }
                
                print(f"   📊 First-party vs All metrics comparison:")
                for metric_name, comparison in metric_comparison.items():
                    fp_pct = comparison["first_party_percentage"]
                    if fp_pct is not None:
                        print(f"      {metric_name}: {comparison['first_party']}/{comparison['all_nodes']} ({fp_pct:.1f}%)")
                    else:
                        print(f"      {metric_name}: {comparison['first_party']}/{comparison['all_nodes']} (N/A)")
                
                return {
                    "first_party_metrics": first_party_metrics,
                    "all_metrics": all_metrics,
                    "metric_comparison": metric_comparison
                }
                
        except Exception as e:
            raise FirstPartyPrioritizationError(f"First-party views verification failed: {e}")
    
    def _verify_external_signal_dilution_control(self) -> Dict[str, Any]:
        """Verify external signals don't dominate critical analytics."""
        print("🎛️  Verifying external signal dilution control...")
        
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                
                # Check for external dominance in key relation types
                critical_relations = [
                    "calls", "writes_to", "invokes_provider", "records_execution_trace",
                    "violates", "applies_guardrail", "validated_by_safety_plane"
                ]
                
                dilution_analysis = {}
                
                for relation_type in critical_relations:
                    cursor.execute("""
                        SELECT n.identity_origin, COUNT(*) FROM edges e
                        JOIN nodes n ON e.src_id = n.id
                        WHERE e.relation_type = ?
                        GROUP BY n.identity_origin
                    """, (relation_type,))
                    
                    origin_counts = dict(cursor.fetchall())
                    total_count = sum(origin_counts.values())
                    
                    if total_count > 0:
                        external_count = origin_counts.get("external", 0)
                        external_percentage = (external_count / total_count) * 100
                        
                        dilution_analysis[relation_type] = {
                            "total_count": total_count,
                            "external_count": external_count,
                            "external_percentage": external_percentage,
                            "origin_breakdown": origin_counts
                        }
                        
                        # Flag high external dominance
                        if external_percentage > 70:
                            self.warnings.append(
                                f"High external dominance in {relation_type}: {external_percentage:.1f}%"
                            )
                
                print(f"   📊 External signal analysis:")
                for relation_type, analysis in dilution_analysis.items():
                    ext_pct = analysis["external_percentage"]
                    print(f"      {relation_type}: {analysis['external_count']}/{analysis['total_count']} external ({ext_pct:.1f}%)")
                
                # Check centrality metrics dilution
                cursor.execute("""
                    SELECT n.identity_origin, COUNT(*) as fan_out FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    GROUP BY n.identity_origin
                    ORDER BY fan_out DESC
                """)
                
                centrality_by_origin = dict(cursor.fetchall())
                total_fan_out = sum(centrality_by_origin.values())
                
                if total_fan_out > 0:
                    external_centrality = centrality_by_origin.get("external", 0)
                    external_centrality_pct = (external_centrality / total_fan_out) * 100
                    
                    print(f"   📊 Centrality by origin: {centrality_by_origin}")
                    print(f"   📊 External centrality share: {external_centrality_pct:.1f}%")
                    
                    if external_centrality_pct > 60:
                        self.warnings.append(f"External nodes dominate centrality ({external_centrality_pct:.1f}%)")
                
                return {
                    "dilution_analysis": dilution_analysis,
                    "centrality_by_origin": centrality_by_origin,
                    "external_centrality_percentage": external_centrality_pct if total_fan_out > 0 else 0
                }
                
        except Exception as e:
            raise FirstPartyPrioritizationError(f"External dilution control verification failed: {e}")
    
    def _verify_executive_readiness(self) -> Dict[str, Any]:
        """Verify readiness for executive-grade reporting."""
        print("📊 Verifying executive readiness...")
        
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                
                # Executive metrics should be first-party-focused
                executive_metrics = {
                    "critical_violations": {
                        "query": """
                            SELECT COUNT(*) FROM edges e 
                            JOIN nodes n ON e.src_id = n.id 
                            WHERE n.identity_origin = 'first_party' 
                            AND e.relation_type IN ('violates', 'layer_violation', 'uwg_bypass')
                        """,
                        "target": "< 10"
                    },
                    "trace_coverage": {
                        "query": """
                            SELECT COUNT(DISTINCT e.src_id) FROM edges e 
                            JOIN nodes n ON e.src_id = n.id 
                            WHERE n.identity_origin = 'first_party' 
                            AND e.relation_type = 'records_execution_trace'
                        """,
                        "target": "> 90%"
                    },
                    "uwg_compliance": {
                        "query": """
                            SELECT COUNT(DISTINCT e.src_id) FROM edges e 
                            JOIN nodes n ON e.src_id = n.id 
                            WHERE n.identity_origin = 'first_party' 
                            AND e.relation_type = 'execution_terminates_at_uwg'
                        """,
                        "target": "> 95%"
                    }
                }
                
                executive_readiness = {}
                readiness_issues = []
                
                # Get first-party module count for percentage calculations
                cursor.execute("SELECT COUNT(*) FROM nodes WHERE identity_origin = 'first_party' AND entity_type = 'module'")
                fp_module_count = cursor.fetchone()[0]
                
                for metric_name, config in executive_metrics.items():
                    cursor.execute(config["query"])
                    actual_value = cursor.fetchone()[0]
                    
                    target = config["target"]
                    readiness_score = "PASS"
                    
                    # Evaluate against target
                    if metric_name == "critical_violations":
                        if actual_value >= int(target.replace("<", "").replace(">", "").strip()):
                            readiness_score = "FAIL"
                            readiness_issues.append(f"Too many critical violations: {actual_value} (target: {target})")
                    elif "%" in target:
                        target_pct = int(target.replace(">", "").replace("<", "").replace("%", "").strip())
                        actual_pct = (actual_value / max(1, fp_module_count)) * 100
                        if ">" in target and actual_pct < target_pct:
                            readiness_score = "FAIL"
                            readiness_issues.append(f"Low {metric_name}: {actual_pct:.1f}% (target: {target})")
                        elif "<" in target and actual_pct > target_pct:
                            readiness_score = "FAIL"
                            readiness_issues.append(f"High {metric_name}: {actual_pct:.1f}% (target: {target})")
                    
                    executive_readiness[metric_name] = {
                        "actual_value": actual_value,
                        "target": target,
                        "readiness_score": readiness_score
                    }
                
                print(f"   📊 Executive readiness assessment:")
                for metric_name, assessment in executive_readiness.items():
                    status_icon = "✅" if assessment["readiness_score"] == "PASS" else "❌"
                    print(f"      {status_icon} {metric_name}: {assessment['actual_value']} (target: {assessment['target']})")
                
                if readiness_issues:
                    print(f"   ❌ Readiness issues: {len(readiness_issues)}")
                    for issue in readiness_issues:
                        print(f"      • {issue}")
                
                return {
                    "executive_readiness": executive_readiness,
                    "readiness_issues": readiness_issues,
                    "overall_readiness": "PASS" if not readiness_issues else "FAIL",
                    "first_party_module_count": fp_module_count
                }
                
        except Exception as e:
            raise FirstPartyPrioritizationError(f"Executive readiness verification failed: {e}")
    
    def verify(self) -> Dict[str, Any]:
        """Run complete first-party prioritization verification."""
        print("🔍 Starting ADG First-Party Prioritization Verification...")
        print(f"📁 ADG Directory: {self.adg_dir}")
        print(f"🗄️  SQLite Database: {self.sqlite_path.name}")
        
        # Verify identity origin classification
        classification = self._verify_identity_origin_classification()
        
        # Verify first-party vs external separation
        separation = self._verify_first_party_vs_external_separation()
        
        # Verify first-party-only views
        views = self._verify_first_party_only_views()
        
        # Verify external signal dilution control
        dilution = self._verify_external_signal_dilution_control()
        
        # Verify executive readiness
        executive = self._verify_executive_readiness()
        
        # Determine overall status
        critical_issues = (
            not classification.get("classification_complete", False) or
            executive.get("overall_readiness") == "FAIL"
        )
        
        # Prepare result
        result = {
            "status": "FAIL" if critical_issues else "PASS",
            "identity_classification": classification,
            "first_party_separation": separation,
            "first_party_views": views,
            "external_dilution": dilution,
            "executive_readiness": executive,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "first_party_percentage": separation.get("first_party_percentage", 0),
                "external_percentage": separation.get("external_percentage", 0),
                "classification_complete": classification.get("classification_complete", False),
                "executive_ready": executive.get("overall_readiness") == "PASS",
                "dilution_concerns": len([w for w in self.warnings if "dominat" in w.lower()])
            }
        }
        
        # Print results
        if self.errors:
            print("\n❌ FIRST-PARTY PRIORITIZATION VERIFICATION FAILED")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if critical_issues:
            print("\n❌ FIRST-PARTY PRIORITIZATION ISSUES FOUND")
        else:
            print("\n✅ FIRST-PARTY PRIORITIZATION VERIFICATION PASSED")
            print(f"📊 First-party modules: {separation.get('first_party_percentage', 0):.1f}%")
            print(f"📊 Executive ready: {executive.get('overall_readiness') == 'PASS'}")
        
        return result

def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify ADG first-party prioritization")
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
        verifier = ADGFirstPartyPrioritizationVerifier(args.adg_dir)
        result = verifier.verify()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"📄 Report saved to: {args.output}")
        
        return 0 if result["status"] == "PASS" else 1
        
    except FirstPartyPrioritizationError as e:
        print(f"❌ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
