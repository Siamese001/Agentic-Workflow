#!/usr/bin/env python3
"""
SSOT Enforcer - Automated Violation Remediation

Uses UnifiedSSOTValidator to detect violations and SSOTRelocator to fix them.

Remediates:
1. Drift violations (orphaned folders → archives)
2. Hierarchy violations (excessive depth → flattening)
3. Gravity violations (wrong layer → correct layer)

Safety:
- Requires --execute flag to apply changes
- Logs all operations to enforcement_history.log
- Provides detailed dry-run preview

Usage:
    python scripts/enforce_ssot.py                    # Dry-run (preview only)
    python scripts/enforce_ssot.py --execute          # Execute enforcement
    python scripts/enforce_ssot.py --drift-only       # Fix drift violations only
    python scripts/enforce_ssot.py --hierarchy-only   # Fix hierarchy violations only
"""

from __future__ import annotations
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
REPO = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO))

from agentic_core.utils.core_extensions.unified_validator import UnifiedSSOTValidator
from agentic_core.L0_maintenance.mixins.ssot_relocator import SSOTRelocator


def print_header(title: str, char: str = "=") -> None:
    """Print formatted section header."""
    print()
    print(char * 80)
    print(f"  {title}")
    print(char * 80)
    print()


def print_enforcement_report(report: any, title: str) -> None:
    """Print enforcement report summary."""
    print(f"\n{title}:")
    print(f"  Total operations: {report.total_operations}")
    print(f"  Successful: {report.successful}")
    print(f"  Failed: {report.failed}")
    print(f"  Skipped: {report.skipped}")
    print(f"  Success rate: {report.success_rate:.1f}%")
    
    if report.failed > 0:
        print(f"\n  Failed operations:")
        for result in report.results:
            if not result.success and result.action != 'SKIPPED':
                print(f"    • {result.source}: {result.error}")


def main():
    """Run SSOT enforcement."""
    parser = argparse.ArgumentParser(
        description="SSOT Enforcer - Automated violation remediation"
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute enforcement (default is dry-run)'
    )
    parser.add_argument(
        '--drift-only',
        action='store_true',
        help='Fix drift violations only'
    )
    parser.add_argument(
        '--hierarchy-only',
        action='store_true',
        help='Fix hierarchy violations only'
    )
    parser.add_argument(
        '--gravity-only',
        action='store_true',
        help='Fix gravity violations only'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        default=True,
        help='Fix all violations (default)'
    )
    
    args = parser.parse_args()
    
    # Determine mode
    dry_run = not args.execute
    mode_str = "DRY-RUN (Preview Only)" if dry_run else "LIVE EXECUTION"
    
    print_header(f"SSOT ENFORCER - {mode_str}")
    
    if dry_run:
        print("⚠️  Running in DRY-RUN mode")
        print("   No changes will be made to the filesystem")
        print("   Use --execute flag to apply changes")
        print()
    else:
        print("🔥 LIVE EXECUTION MODE")
        print("   Changes will be applied to the filesystem")
        print("   All operations will be logged")
        print()
        
        # Confirmation prompt
        response = input("Continue with enforcement? (yes/no): ").strip().lower()
        if response not in ('yes', 'y'):
            print("\nEnforcement cancelled by user.")
            sys.exit(0)
        print()
    
    # Step 1: Run validation
    print_header("STEP 1: VALIDATION", "-")
    print("Running comprehensive SSOT validation...")
    
    validator = UnifiedSSOTValidator(REPO)
    report = validator.validate_all()
    
    print(f"\nValidation complete:")
    print(f"  Compliance Score: {report.compliance_score:.1f}%")
    print(f"  Total Violations: {report.total_violations}")
    print(f"    • Gravity:    {len(report.gravity_violations)}")
    print(f"    • Imports:    {len(report.import_violations)}")
    print(f"    • Hierarchy:  {len(report.hierarchy_violations)}")
    print(f"    • Drift:      {len(report.drift_violations)}")
    
    if report.is_compliant:
        print("\n✅ System is fully compliant - no enforcement needed")
        sys.exit(0)
    
    # Step 2: Initialize relocator
    print_header("STEP 2: ENFORCEMENT PREPARATION", "-")
    print(f"Initializing SSOTRelocator (dry_run={dry_run})...")
    
    relocator = SSOTRelocator(REPO, dry_run=dry_run)
    print(f"Enforcement log: {relocator.log_file}")
    
    # Step 3: Execute enforcement
    print_header("STEP 3: ENFORCEMENT EXECUTION", "-")
    
    total_operations = 0
    total_successful = 0
    total_failed = 0
    
    # Drift enforcement
    if (args.all or args.drift_only) and report.drift_violations:
        print(f"\n{'[DRY-RUN] ' if dry_run else ''}Enforcing drift violations...")
        print(f"Target: {len(report.drift_violations)} orphaned folders")
        
        drift_report = relocator.relocate_orphans(report.drift_violations)
        print_enforcement_report(drift_report, "Drift Enforcement Results")
        
        total_operations += drift_report.total_operations
        total_successful += drift_report.successful
        total_failed += drift_report.failed
    
    # Hierarchy enforcement
    if (args.all or args.hierarchy_only) and report.hierarchy_violations:
        print(f"\n{'[DRY-RUN] ' if dry_run else ''}Enforcing hierarchy violations...")
        print(f"Target: {len(report.hierarchy_violations)} folders exceeding depth limits")
        
        hierarchy_report = relocator.enforce_hierarchy(report.hierarchy_violations)
        print_enforcement_report(hierarchy_report, "Hierarchy Enforcement Results")
        
        total_operations += hierarchy_report.total_operations
        total_successful += hierarchy_report.successful
        total_failed += hierarchy_report.failed
    
    # Gravity enforcement
    if (args.all or args.gravity_only) and report.gravity_violations:
        print(f"\n{'[DRY-RUN] ' if dry_run else ''}Enforcing gravity violations...")
        print(f"Target: {len(report.gravity_violations)} agents in wrong layers")
        
        gravity_report = relocator.relocate_agents(report.gravity_violations)
        print_enforcement_report(gravity_report, "Gravity Enforcement Results")
        
        total_operations += gravity_report.total_operations
        total_successful += gravity_report.successful
        total_failed += gravity_report.failed
    
    # Import violations (informational only - requires manual refactoring)
    if report.import_violations:
        print(f"\n⚠️  Import violations detected: {len(report.import_violations)}")
        print("   These require manual refactoring (cannot be auto-fixed)")
        print("   See SSOT_Health_Report for details")
    
    # Step 4: Summary
    print_header("ENFORCEMENT SUMMARY")
    
    print(f"Mode: {mode_str}")
    print(f"Total operations: {total_operations}")
    print(f"Successful: {total_successful}")
    print(f"Failed: {total_failed}")
    
    if total_operations > 0:
        success_rate = (total_successful / total_operations) * 100
        print(f"Success rate: {success_rate:.1f}%")
    
    print()
    
    if dry_run:
        print("⚠️  DRY-RUN complete - no changes were made")
        print("   Run with --execute to apply changes")
    else:
        print("✅ Enforcement complete")
        print(f"   {total_successful}/{total_operations} operations successful")
        print(f"   Check {relocator.log_file} for details")
        
        # Suggest re-validation
        print("\n📋 Next steps:")
        print("   1. Run: python scripts/validate_ssot.py")
        print("   2. Verify compliance score improvement")
        print("   3. Address any remaining violations")
    
    print()
    
    # Exit code
    sys.exit(0 if total_failed == 0 else 1)


if __name__ == "__main__":
    main()
