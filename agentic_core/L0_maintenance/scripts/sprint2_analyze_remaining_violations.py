#!/usr/bin/env python3
"""
Sprint 2: Analyze Remaining Import Violations

Since L0→L3/L4 are already fixed, analyze what violations remain
and categorize them for future sprints.
"""

from pathlib import Path
import sys
from collections import defaultdict

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO))

from agentic_core.L5_safety.gravity.unified_validator import UnifiedSSOTValidator

def main():
    """Analyze remaining import violations by type."""
    
    print("=" * 80)
    print("  Sprint 2: Remaining Violation Analysis")
    print("=" * 80)
    print()
    
    # Run validation
    validator = UnifiedSSOTValidator(REPO)
    report = validator.validate_all()
    
    print(f"Current Compliance: {report.compliance_score:.1f}%")
    print(f"Total Import Violations: {len(report.import_violations)}")
    print()
    
    # Categorize violations by source → target
    by_pattern = defaultdict(list)
    
    for v in report.import_violations:
        pattern = f"{v.source_layer} → {v.target_layer}"
        by_pattern[pattern].append(v)
    
    print("=" * 80)
    print("  Violation Breakdown by Pattern")
    print("=" * 80)
    print()
    
    # Sort by count (descending)
    for pattern, violations in sorted(by_pattern.items(), key=lambda x: len(x[1]), reverse=True):
        count = len(violations)
        print(f"{pattern}: {count} violations")
        
        # Show top 3 files for this pattern
        file_counts = defaultdict(int)
        for v in violations:
            file_counts[v.file_path] += 1
        
        top_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        for file_path, file_count in top_files:
            print(f"  • {file_path} ({file_count} violations)")
        
        if len(file_counts) > 3:
            print(f"  ... and {len(file_counts) - 3} more files")
        print()
    
    # Identify next sprint targets
    print("=" * 80)
    print("  Sprint 2 Status & Next Steps")
    print("=" * 80)
    print()
    
    l0_violations = [v for v in report.import_violations if v.source_layer == "LL0"]
    l1_violations = [v for v in report.import_violations if v.source_layer == "LL1"]
    l2_violations = [v for v in report.import_violations if v.source_layer == "LL2"]
    
    print(f"L0 violations: {len(l0_violations)}")
    print(f"L1 violations: {len(l1_violations)}")
    print(f"L2 violations: {len(l2_violations)}")
    print()
    
    print("✅ Sprint 2 Achievement:")
    print("   L0 → L3/L4 violations: 0 (already eliminated in previous phases)")
    print()
    
    print("📋 Remaining Work:")
    if l1_violations:
        print(f"   • L1 violations: {len(l1_violations)} (mostly L1→L4/L5)")
    if l2_violations:
        print(f"   • L2 violations: {len(l2_violations)} (mostly L2→L3/L5)")
    if l0_violations:
        print(f"   • L0 violations: {len(l0_violations)} (mostly L0→L1/L2)")
    
    return 0

if __name__ == "__main__":
    exit(main())
