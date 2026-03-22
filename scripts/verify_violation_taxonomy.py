#!/usr/bin/env python3
"""
ADG Violation Taxonomy Expansion

Implements precise violation taxonomy for remediation prioritization:
- exception_swallow
- bare_except
- broad_exception_without_structured_handling
- retry_without_backoff
- retry_without_bound
- retry_without_trace_link
- layer_violation
- runtime_boundary_breach
- uwg_bypass
- policy_violation
- guardrail_bypass
- trace_missing
- replay_missing
- validation_missing
- learning_loop_gap
- embedding_gap
- unresolved_import
- low_confidence_identity
- unknown_l4_identity
- dead_import
- dead_code_candidate

REQUIRE:
- every violation queryable by category/subcategory/severity/domain
- every violation type mapped to remediation class
- every report able to aggregate by first_party_only mode
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

class ViolationTaxonomyError(Exception):
    """Raised when violation taxonomy verification fails."""
    pass

class ADGViolationTaxonomyVerifier:
    """Verifies ADG violation taxonomy and classification."""
    
    # Expanded violation taxonomy
    VIOLATION_TAXONOMY = {
        "exception_handling": {
            "exception_swallow": {"severity": "high", "remediation_class": "error_handling"},
            "bare_except": {"severity": "high", "remediation_class": "error_handling"},
            "broad_exception_without_structured_handling": {"severity": "medium", "remediation_class": "error_handling"}
        },
        "retry_patterns": {
            "retry_without_backoff": {"severity": "medium", "remediation_class": "retry_handling"},
            "retry_without_bound": {"severity": "medium", "remediation_class": "retry_handling"},
            "retry_without_trace_link": {"severity": "high", "remediation_class": "retry_handling"}
        },
        "architectural": {
            "layer_violation": {"severity": "high", "remediation_class": "architecture"},
            "runtime_boundary_breach": {"severity": "high", "remediation_class": "architecture"},
            "uwg_bypass": {"severity": "critical", "remediation_class": "architecture"},
            "policy_violation": {"severity": "high", "remediation_class": "architecture"},
            "guardrail_bypass": {"severity": "critical", "remediation_class": "architecture"}
        },
        "observability": {
            "trace_missing": {"severity": "high", "remediation_class": "observability"},
            "replay_missing": {"severity": "medium", "remediation_class": "observability"},
            "validation_missing": {"severity": "medium", "remediation_class": "observability"}
        },
        "learning": {
            "learning_loop_gap": {"severity": "medium", "remediation_class": "learning"},
            "embedding_gap": {"severity": "low", "remediation_class": "learning"}
        },
        "identity": {
            "unresolved_import": {"severity": "medium", "remediation_class": "identity"},
            "low_confidence_identity": {"severity": "low", "remediation_class": "identity"},
            "unknown_l4_identity": {"severity": "high", "remediation_class": "identity"}
        },
        "code_health": {
            "dead_import": {"severity": "low", "remediation_class": "code_health"},
            "dead_code_candidate": {"severity": "low", "remediation_class": "code_health"}
        }
    }
    
    # Severity levels for prioritization
    SEVERITY_LEVELS = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    
    def __init__(self, adg_dir: Path):
        self.adg_dir = Path(adg_dir)
        self.sqlite_path = self._find_sqlite_database()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def _find_sqlite_database(self) -> Path:
        """Find the latest SQLite database."""
        sqlite_files = list(self.adg_dir.glob("adg_indexed_*.sqlite"))
        if not sqlite_files:
            raise ViolationTaxonomyError("No SQLite database found")
        
        return max(sqlite_files, key=lambda p: p.stat().st_mtime)
    
    def _verify_violation_taxonomy_coverage(self) -> Dict[str, Any]:
        """Verify all violation types in taxonomy are detected."""
        print("📋 Verifying violation taxonomy coverage...")
        
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                
                # Get all violation-related edge types in database
                cursor.execute("""
                    SELECT DISTINCT relation_type FROM edges 
                    WHERE relation_type LIKE '%violation%' 
                    OR relation_type LIKE '%violate%'
                    OR relation_type IN ('bare_except', 'exception_swallow', 'layer_violation',
                                         'uwg_bypass', 'policy_violation', 'guardrail_bypass',
                                         'trace_missing', 'replay_missing', 'validation_missing',
                                         'learning_loop_gap', 'embedding_gap', 'unresolved_import',
                                         'dead_import', 'dead_code_candidate')
                """)
                
                detected_violations = {row[0] for row in cursor.fetchall()}
                
                # Get all expected violation types from taxonomy
                expected_violations = set()
                for category, violations in self.VIOLATION_TAXONOMY.items():
                    expected_violations.update(violations.keys())
                
                print(f"   📊 Expected violation types: {len(expected_violations)}")
                print(f"   📊 Detected violation types: {len(detected_violations)}")
                
                # Find missing violations
                missing_violations = expected_violations - detected_violations
                unexpected_violations = detected_violations - expected_violations
                
                if missing_violations:
                    self.warnings.append(f"Missing violation detection: {sorted(missing_violations)}")
                
                if unexpected_violations:
                    self.warnings.append(f"Unexpected violation types: {sorted(unexpected_violations)}")
                
                # Count violations by type
                violation_counts = {}
                for violation_type in detected_violations:
                    cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (violation_type,))
                    count = cursor.fetchone()[0]
                    violation_counts[violation_type] = count
                
                print(f"   📊 Violation counts:")
                for violation_type in sorted(detected_violations):
                    count = violation_counts[violation_type]
                    if count > 0:
                        print(f"      {violation_type}: {count}")
                
                return {
                    "expected_violations": len(expected_violations),
                    "detected_violations": len(detected_violations),
                    "missing_violations": sorted(missing_violations),
                    "unexpected_violations": sorted(unexpected_violations),
                    "violation_counts": violation_counts,
                    "total_violations": sum(violation_counts.values())
                }
                
        except Exception as e:
            raise ViolationTaxonomyError(f"Violation taxonomy coverage verification failed: {e}")
    
    def _verify_violation_categorization(self) -> Dict[str, Any]:
        """Verify violations are properly categorized and mapped to remediation classes."""
        print("🏷️  Verifying violation categorization...")
        
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                
                # Analyze violations by category
                category_analysis = {}
                
                for category, violations in self.VIOLATION_TAXONOMY.items():
                    category_stats = {
                        "violation_types": list(violations.keys()),
                        "detected_count": 0,
                        "severity_distribution": defaultdict(int),
                        "remediation_class": None
                    }
                    
                    # Get remediation class (should be same for all violations in category)
                    if violations:
                        first_violation = list(violations.keys())[0]
                        category_stats["remediation_class"] = violations[first_violation]["remediation_class"]
                    
                    # Count detected violations in this category
                    for violation_type in violations:
                        cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (violation_type,))
                        count = cursor.fetchone()[0]
                        category_stats["detected_count"] += count
                        
                        if count > 0:
                            severity = violations[violation_type]["severity"]
                            category_stats["severity_distribution"][severity] += count
                    
                    category_analysis[category] = category_stats
                
                print(f"   📊 Violation analysis by category:")
                print(f"      Category | Types | Count | Remediation | Critical | High | Medium | Low")
                print(f"      ---------|-------|-------|-------------|----------|------|--------|----")
                
                for category, stats in category_analysis.items():
                    critical = stats["severity_distribution"]["critical"]
                    high = stats["severity_distribution"]["high"]
                    medium = stats["severity_distribution"]["medium"]
                    low = stats["severity_distribution"]["low"]
                    
                    print(f"      {category:9} | {len(stats['violation_types']):5} | {stats['detected_count']:5} | "
                          f"{stats['remediation_class']:11} | {critical:8} | {high:4} | {medium:6} | {low:2}")
                
                # Verify remediation class mapping
                remediation_classes = set()
                for stats in category_analysis.values():
                    if stats["remediation_class"]:
                        remediation_classes.add(stats["remediation_class"])
                
                expected_remediation_classes = {
                    "error_handling", "retry_handling", "architecture", 
                    "observability", "learning", "identity", "code_health"
                }
                
                missing_remediation = expected_remediation_classes - remediation_classes
                if missing_remediation:
                    self.warnings.append(f"Missing remediation classes: {missing_remediation}")
                
                return {
                    "category_analysis": category_analysis,
                    "remediation_classes": remediation_classes,
                    "missing_remediation_classes": missing_remediation
                }
                
        except Exception as e:
            raise ViolationTaxonomyError(f"Violation categorization verification failed: {e}")
    
    def _verify_severity_based_prioritization(self) -> Dict[str, Any]:
        """Verify violations can be prioritized by severity."""
        print("🎯 Verifying severity-based prioritization...")
        
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                
                # Calculate severity-weighted violation scores
                severity_scores = {"critical": 0, "high": 0, "medium": 0, "low": 0}
                
                for category, violations in self.VIOLATION_TAXONOMY.items():
                    for violation_type, config in violations.items():
                        severity = config["severity"]
                        weight = self.SEVERITY_LEVELS[severity]
                        
                        cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (violation_type,))
                        count = cursor.fetchone()[0]
                        
                        severity_scores[severity] += count * weight
                
                print(f"   📊 Severity-weighted violation scores:")
                total_score = sum(severity_scores.values())
                for severity in ["critical", "high", "medium", "low"]:
                    score = severity_scores[severity]
                    percentage = (score / max(1, total_score)) * 100
                    print(f"      {severity:8} | {score:6} | {percentage:5.1f}%")
                
                # Get top violations by severity
                top_critical_violations = []
                top_high_violations = []
                
                for category, violations in self.VIOLATION_TAXONOMY.items():
                    for violation_type, config in violations.items():
                        severity = config["severity"]
                        
                        cursor.execute("""
                            SELECT e.src_id, n.adg_name, n.layer, e.source_file, e.line_no
                            FROM edges e
                            JOIN nodes n ON e.src_id = n.id
                            WHERE e.relation_type = ?
                            AND n.identity_kind NOT IN ('external_module', 'external_provider')
                            LIMIT 5
                        """, (violation_type,))
                        
                        instances = cursor.fetchall()
                        if instances:
                            violation_data = {
                                "violation_type": violation_type,
                                "category": category,
                                "severity": severity,
                                "remediation_class": config["remediation_class"],
                                "instances": [
                                    {
                                        "module": instance[1],
                                        "layer": instance[2],
                                        "file": instance[3],
                                        "line": instance[4]
                                    }
                                    for instance in instances
                                ]
                            }
                            
                            if severity == "critical":
                                top_critical_violations.append(violation_data)
                            elif severity == "high":
                                top_high_violations.append(violation_data)
                
                # Sort by number of instances
                top_critical_violations.sort(key=lambda x: len(x["instances"]), reverse=True)
                top_high_violations.sort(key=lambda x: len(x["instances"]), reverse=True)
                
                print(f"   📊 Top critical violations:")
                for i, violation in enumerate(top_critical_violations[:5]):
                    print(f"      {i+1}. {violation['violation_type']} ({len(violation['instances'])} instances)")
                
                return {
                    "severity_scores": severity_scores,
                    "total_weighted_score": total_score,
                    "top_critical_violations": top_critical_violations[:5],
                    "top_high_violations": top_high_violations[:5]
                }
                
        except Exception as e:
            raise ViolationTaxonomyError(f"Severity-based prioritization verification failed: {e}")
    
    def _verify_first_party_violation_analysis(self) -> Dict[str, Any]:
        """Verify violations can be analyzed with first-party-only mode."""
        print("🎯 Verifying first-party violation analysis...")
        
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                
                # Compare all violations vs first-party-only violations
                first_party_analysis = {}
                
                for category, violations in self.VIOLATION_TAXONOMY.items():
                    category_stats = {
                        "all_violations": 0,
                        "first_party_violations": 0,
                        "first_party_percentage": 0
                    }
                    
                    for violation_type in violations:
                        # Count all violations
                        cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (violation_type,))
                        all_count = cursor.fetchone()[0]
                        
                        # Count first-party violations only
                        cursor.execute("""
                            SELECT COUNT(*) FROM edges e
                            JOIN nodes n ON e.src_id = n.id
                            WHERE e.relation_type = ? 
                            AND n.identity_kind NOT IN ('external_module', 'external_provider')
                        """, (violation_type,))
                        
                        fp_count = cursor.fetchone()[0]
                        
                        category_stats["all_violations"] += all_count
                        category_stats["first_party_violations"] += fp_count
                    
                    # Calculate percentage
                    if category_stats["all_violations"] > 0:
                        category_stats["first_party_percentage"] = (
                            category_stats["first_party_violations"] / category_stats["all_violations"]
                        ) * 100
                    
                    first_party_analysis[category] = category_stats
                
                print(f"   📊 First-party violation analysis:")
                print(f"      Category | All | FP | FP %")
                print(f"      ---------|-----|----|------")
                
                for category, stats in first_party_analysis.items():
                    all_count = stats["all_violations"]
                    fp_count = stats["first_party_violations"]
                    fp_pct = stats["first_party_percentage"]
                    
                    print(f"      {category:9} | {all_count:3} | {fp_count:2} | {fp_pct:4.1f}%")
                
                # Calculate overall first-party percentage
                total_all = sum(stats["all_violations"] for stats in first_party_analysis.values())
                total_fp = sum(stats["first_party_violations"] for stats in first_party_analysis.values())
                overall_fp_percentage = (total_fp / max(1, total_all)) * 100
                
                print(f"   📊 Overall first-party violations: {total_fp}/{total_all} ({overall_fp_percentage:.1f}%)")
                
                # Check for external dominance in violations
                if overall_fp_percentage < 50:
                    self.warnings.append(f"External violations dominate: {100-overall_fp_percentage:.1f}%")
                
                return {
                    "first_party_analysis": first_party_analysis,
                    "total_all_violations": total_all,
                    "total_first_party_violations": total_fp,
                    "overall_first_party_percentage": overall_fp_percentage
                }
                
        except Exception as e:
            raise ViolationTaxonomyError(f"First-party violation analysis verification failed: {e}")
    
    def _verify_remediation_mapping(self) -> Dict[str, Any]:
        """Verify all violations are mapped to remediation classes."""
        print("🔧 Verifying remediation mapping...")
        
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                
                # Group violations by remediation class
                remediation_analysis = {}
                
                for category, violations in self.VIOLATION_TAXONOMY.items():
                    for violation_type, config in violations.items():
                        remediation_class = config["remediation_class"]
                        severity = config["severity"]
                        
                        if remediation_class not in remediation_analysis:
                            remediation_analysis[remediation_class] = {
                                "violation_types": [],
                                "severity_distribution": defaultdict(int),
                                "total_violations": 0
                            }
                        
                        remediation_analysis[remediation_class]["violation_types"].append(violation_type)
                        
                        # Count actual violations
                        cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (violation_type,))
                        count = cursor.fetchone()[0]
                        
                        remediation_analysis[remediation_class]["severity_distribution"][severity] += count
                        remediation_analysis[remediation_class]["total_violations"] += count
                
                print(f"   📊 Remediation class analysis:")
                print(f"      Class | Types | Violations | Critical | High | Medium | Low")
                print(f"      ------|-------|------------|----------|------|--------|----")
                
                for remediation_class, analysis in sorted(remediation_analysis.items()):
                    critical = analysis["severity_distribution"]["critical"]
                    high = analysis["severity_distribution"]["high"]
                    medium = analysis["severity_distribution"]["medium"]
                    low = analysis["severity_distribution"]["low"]
                    total = analysis["total_violations"]
                    
                    print(f"      {remediation_class:6} | {len(analysis['violation_types']):5} | {total:10} | "
                          f"{critical:8} | {high:4} | {medium:6} | {low:2}")
                
                # Verify all expected remediation classes are present
                expected_classes = {
                    "error_handling", "retry_handling", "architecture", 
                    "observability", "learning", "identity", "code_health"
                }
                
                detected_classes = set(remediation_analysis.keys())
                missing_classes = expected_classes - detected_classes
                
                if missing_classes:
                    self.warnings.append(f"Missing remediation classes: {missing_classes}")
                
                return {
                    "remediation_analysis": remediation_analysis,
                    "expected_remediation_classes": expected_classes,
                    "detected_remediation_classes": detected_classes,
                    "missing_remediation_classes": missing_classes
                }
                
        except Exception as e:
            raise ViolationTaxonomyError(f"Remediation mapping verification failed: {e}")
    
    def verify(self) -> Dict[str, Any]:
        """Run complete violation taxonomy verification."""
        print("🔍 Starting ADG Violation Taxonomy Verification...")
        print(f"📁 ADG Directory: {self.adg_dir}")
        print(f"🗄️  SQLite Database: {self.sqlite_path.name}")
        
        # Verify taxonomy coverage
        coverage = self._verify_violation_taxonomy_coverage()
        
        # Verify categorization
        categorization = self._verify_violation_categorization()
        
        # Verify severity-based prioritization
        prioritization = self._verify_severity_based_prioritization()
        
        # Verify first-party analysis
        first_party = self._verify_first_party_violation_analysis()
        
        # Verify remediation mapping
        remediation = self._verify_remediation_mapping()
        
        # Determine overall status
        critical_issues = (
            coverage.get("total_violations", 0) > 1000 or
            prioritization.get("total_weighted_score", 0) > 500
        )
        
        # Prepare result
        result = {
            "status": "FAIL" if critical_issues else "PASS",
            "taxonomy_coverage": coverage,
            "violation_categorization": categorization,
            "severity_prioritization": prioritization,
            "first_party_analysis": first_party,
            "remediation_mapping": remediation,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "total_violations": coverage.get("total_violations", 0),
                "detected_violation_types": coverage.get("detected_violations", 0),
                "total_weighted_score": prioritization.get("total_weighted_score", 0),
                "first_party_percentage": first_party.get("overall_first_party_percentage", 0),
                "remediation_classes": len(remediation.get("detected_remediation_classes", []))
            }
        }
        
        # Print results
        if self.errors:
            print("\n❌ VIOLATION TAXONOMY VERIFICATION FAILED")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if critical_issues:
            print("\n❌ VIOLATION TAXONOMY ISSUES FOUND")
            print(f"   • Total violations: {result['summary']['total_violations']}")
            print(f"   • Weighted severity score: {result['summary']['total_weighted_score']}")
        else:
            print("\n✅ VIOLATION TAXONOMY VERIFICATION PASSED")
            print(f"📊 Total violations: {result['summary']['total_violations']}")
            print(f"📊 Violation types detected: {result['summary']['detected_violation_types']}")
            print(f"📊 First-party violations: {result['summary']['first_party_percentage']:.1f}%")
        
        return result

def main():
    """CLI entry point."""
    import argparse
    from collections import defaultdict
    
    parser = argparse.ArgumentParser(description="Verify ADG violation taxonomy")
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
        verifier = ADGViolationTaxonomyVerifier(args.adg_dir)
        result = verifier.verify()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"📄 Report saved to: {args.output}")
        
        return 0 if result["status"] == "PASS" else 1
        
    except ViolationTaxonomyError as e:
        print(f"❌ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
