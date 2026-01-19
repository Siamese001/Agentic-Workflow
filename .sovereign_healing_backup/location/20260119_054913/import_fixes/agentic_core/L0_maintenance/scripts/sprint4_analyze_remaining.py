#!/usr/bin/env python3
"""
Sprint 4: Analyze Remaining 42 Import Violations

Categorize remaining violations to plan final refactoring phases.
"""

from pathlib import Path
import sys
from collections import defaultdict

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO))

from agentic_core.utils.core_extensions.unified_validator import UnifiedSSOTValidator

def main():
    """Analyze remaining import violations."""
    
    print("=" * 80)
    print("  Sprint 4: Remaining Violation Analysis (After Phase 1)")
    print("=" * 80)
    print()
    
    validator = UnifiedSSOTValidator(REPO)
    report = validator.validate_all()
    
    print(f"Current Compliance: {report.compliance_score:.1f}%")
    print(f"Total Import Violations: {len(report.import_violations)}")
    print()
    
    # Categorize by pattern
    by_pattern = defaultdict(list)
    
    for v in report.import_violations:
        pattern = f"{v.source_layer} → {v.target_layer}"
        by_pattern[pattern].append(v)
    
    print("=" * 80)
    print("  Violation Breakdown by Pattern")
    print("=" * 80)
    print()
    
    for pattern, violations in sorted(by_pattern.items(), key=lambda x: len(x[1]), reverse=True):
        count = len(violations)
        print(f"{pattern}: {count} violations")
        
        # Show files for this pattern
        file_counts = defaultdict(int)
        for v in violations:
            file_counts[v.file_path] += 1
        
        for file_path, file_count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {file_path} ({file_count})")
        print()
    
    print("=" * 80)
    print("  Sprint 4 Remaining Phases")
    print("=" * 80)
    print()
    
    l2_violations = [v for v in report.import_violations if v.source_layer == "LL2"]
    l1_violations = [v for v in report.import_violations if v.source_layer == "LL1"]
    l3_violations = [v for v in report.import_violations if v.source_layer == "LL3"]
    l4_violations = [v for v in report.import_violations if v.source_layer == "LL4"]
    
    print(f"L1 violations: {len(l1_violations)}")
    print(f"L2 violations: {len(l2_violations)}")
    print(f"L3 violations: {len(l3_violations)}")
    print(f"L4 violations: {len(l4_violations)}")
    print()
    
    print("Phase 2 Target: L2 violations (execution layer)")
    print("Phase 3 Target: L1 violations (cognition layer)")
    print("Phase 4 Target: Remaining L3/L4 + structural cleanup")
    
    return 0

if __name__ == "__main__":
    exit(main())
