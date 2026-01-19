#!/usr/bin/env python3
"""
Sprint 2: Identify L0 → L3/L4 Violations

Analyzes the validation report to find all remaining orchestration and state violations.
"""

from pathlib import Path
import sys

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO))

from agentic_core.L5_safety.gravity.unified_validator import UnifiedSSOTValidator

def main():
    """Identify all L0 → L3 and L0 → L4 violations."""
    
    print("=" * 80)
    print("  Sprint 2: L0 → L3/L4 Violation Analysis")
    print("=" * 80)
    print()
    
    # Run validation
    validator = UnifiedSSOTValidator(REPO)
    report = validator.validate_all()
    
    # Filter for L0 → L3 and L0 → L4 violations
    l0_to_l3 = []
    l0_to_l4 = []
    
    for violation in report.import_violations:
        if violation.source_layer == "LL0" and violation.target_layer == "LL3":
            l0_to_l3.append(violation)
        elif violation.source_layer == "LL0" and violation.target_layer == "LL4":
            l0_to_l4.append(violation)
    
    print(f"L0 → L3 Violations: {len(l0_to_l3)}")
    print(f"L0 → L4 Violations: {len(l0_to_l4)}")
    print()
    
    if l0_to_l3:
        print("=" * 80)
        print("  L0 → L3 (Orchestration) Violations")
        print("=" * 80)
        print()
        
        # Group by file
        by_file = {}
        for v in l0_to_l3:
            if v.file_path not in by_file:
                by_file[v.file_path] = []
            by_file[v.file_path].append(v)
        
        for file_path, violations in sorted(by_file.items()):
            print(f"\n📄 {file_path}")
            for v in violations:
                print(f"  Line {v.line_number}: {v.import_statement[:60]}...")
    
    if l0_to_l4:
        print()
        print("=" * 80)
        print("  L0 → L4 (State) Violations")
        print("=" * 80)
        print()
        
        # Group by file
        by_file = {}
        for v in l0_to_l4:
            if v.file_path not in by_file:
                by_file[v.file_path] = []
            by_file[v.file_path].append(v)
        
        for file_path, violations in sorted(by_file.items()):
            print(f"\n📄 {file_path}")
            for v in violations:
                print(f"  Line {v.line_number}: {v.import_statement[:60]}...")
    
    print()
    print("=" * 80)
    print("  Summary")
    print("=" * 80)
    print(f"Total L0 → L3/L4 violations: {len(l0_to_l3) + len(l0_to_l4)}")
    print(f"Files affected: {len(set([v.file_path for v in l0_to_l3 + l0_to_l4]))}")
    print()
    
    return 0

if __name__ == "__main__":
    exit(main())
