#!/usr/bin/env python3
"""
SSOT - Sovereign Single Source of Truth CLI

Professional-grade command-line tool for SSOT architectural governance.
Provides a unified interface for scanning, validation, and enforcement.

Usage:
    python scripts/ssot.py scan              # Scan and list all agents
    python scripts/ssot.py validate          # Run comprehensive validation
    python scripts/ssot.py enforce           # Apply automated remediation
    python scripts/ssot.py status            # Show compliance dashboard

Similar to git/npm, this tool provides a discoverable interface for
architectural governance as a first-class citizen of your workflow.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
REPO = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO))

from agentic_core.utils.core_extensions.ssot_scanner import SSOTScanner
from agentic_core.utils.core_extensions.unified_validator import UnifiedSSOTValidator

# ARCHIVED: ssot_relocator import removed # SSOTRelocator


def print_header(title: str, char: str = "=", width: int = 80) -> None:
    """Print formatted section header."""
    print()
    print(char * width)
    print(f"  {title}")
    print(char * width)
    print()


def cmd_scan(args) -> int:
    """
    Scan command: List all discovered agents and their metadata.

    Returns:
        Exit code (0 for success)
    """
    print_header("SSOT SCANNER - Agent Discovery")

    print("Scanning filesystem for agents...")
    scanner = SSOTScanner(REPO)

    # Scan agents
    agents = scanner.scan_agents()
    stats = scanner.get_compliance_stats()

    print(f"\nDiscovered {stats['total_agents']} agents")
    print()

    # Display options
    if args.summary:
        # Summary view
        print("Summary by Layer:")
        layer_counts = {}
        for agent in agents:
            layer = agent.assigned_layer
            layer_counts[layer] = layer_counts.get(layer, 0) + 1

        for layer in sorted(layer_counts.keys()):
            print(f"  {layer}: {layer_counts[layer]} agents")

    elif args.violations_only:
        # Show only violations
        violations = scanner.find_gravity_violations()

        if violations:
            print(f"Gravity Violations: {len(violations)}")
            for agent in violations:
                print(f"  • {agent.relative_path}")
                print(f"    Actual: {agent.layer}, Assigned: {agent.assigned_layer}")
        else:
            print("✅ No gravity violations found")

    else:
        # Full listing
        if args.limit:
            agents = agents[: args.limit]
            print(f"Showing first {args.limit} agents:")
        else:
            print("All agents:")

        print()
        for agent in agents:
            status = "✅" if not agent.has_gravity_violation else "⚠️"
            print(f"{status} {agent.relative_path}")
            print(f"   Class: {agent.class_name}")
            print(f"   Layer: {agent.layer} (assigned: {agent.assigned_layer})")
            if agent.base_classes:
                print(f"   Bases: {', '.join(agent.base_classes[:3])}")
            print()

    # Statistics
    print("Statistics:")
    print(f"  Total agents: {stats['total_agents']}")
    print(f"  Compliant: {stats['compliant_agents']}")
    print(f"  Violations: {stats['gravity_violations']}")
    print(f"  Compliance: {stats['compliance_percentage']:.1f}%")

    return 0


def cmd_validate(args) -> int:
    """
    Validate command: Run comprehensive SSOT validation.

    Returns:
        Exit code (0 if compliant, 1 if violations found)
    """
    print_header("SSOT VALIDATOR - Comprehensive Health Check")

    print("Running validation checks...")
    print("  • Gravity violations (physical location)")
    print("  • Import violations (upward dependencies)")
    print("  • Hierarchy violations (depth limits)")
    print("  • Drift violations (filesystem vs blueprint)")
    print()

    # Run validation
    validator = UnifiedSSOTValidator(REPO)
    report = validator.validate_all()

    # Display results
    if args.summary:
        # Brief summary
        print(f"Compliance Score: {report.compliance_score:.1f}%")
        print(f"Total Violations: {report.total_violations}")
        print(f"  • Gravity:    {len(report.gravity_violations)}")
        print(f"  • Imports:    {len(report.import_violations)}")
        print(f"  • Hierarchy:  {len(report.hierarchy_violations)}")
        print(f"  • Drift:      {len(report.drift_violations)}")
        print()

        if report.is_compliant:
            print("✅ Status: COMPLIANT")
        else:
            print("⚠️  Status: NON-COMPLIANT")

    else:
        # Full report
        print(report.to_markdown())

    # Save to file if requested
    if args.output or args.markdown:
        if args.output:
            output_path = Path(args.output)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = REPO / f"SSOT_Health_Report_{timestamp}.md"

        output_path.write_text(report.to_markdown(), encoding="utf-8")
        print(f"\n📄 Report saved: {output_path}")

    # JSON output
    if args.json:
        json_data = {
            "compliance_score": report.compliance_score,
            "total_violations": report.total_violations,
            "is_compliant": report.is_compliant,
            "scan_duration": report.scan_duration,
            "violations": {
                "gravity": len(report.gravity_violations),
                "imports": len(report.import_violations),
                "hierarchy": len(report.hierarchy_violations),
                "drift": len(report.drift_violations),
            },
        }
        print("\n" + json.dumps(json_data, indent=2))

    return 0 if report.is_compliant else 1


def cmd_enforce(args) -> int:
    """
    Enforce command: Apply automated remediation.

    Returns:
        Exit code (0 for success)
    """
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
        if not args.yes:
            response = input("Continue with enforcement? (yes/no): ").strip().lower()
            if response not in ("yes", "y"):
                print("\nEnforcement cancelled by user.")
                return 0
        print()

    # Run validation first
    print("Step 1: Running validation...")
    validator = UnifiedSSOTValidator(REPO)
    report = validator.validate_all()

    print(f"  Compliance: {report.compliance_score:.1f}%")
    print(f"  Violations: {report.total_violations}")
    print()

    if report.is_compliant:
        print("✅ System is fully compliant - no enforcement needed")
        return 0

    # Initialize enforcer
    print("Step 2: Initializing enforcer...")
    relocator = SSOTRelocator(REPO, dry_run=dry_run)
    print(f"  Log file: {relocator.log_file}")
    print()

    # Execute enforcement
    print("Step 3: Applying remediation...")

    total_operations = 0
    total_successful = 0
    total_failed = 0

    # Drift enforcement
    if (args.all or args.drift) and report.drift_violations:
        print(f"\n{'[DRY-RUN] ' if dry_run else ''}Fixing drift violations...")
        drift_report = relocator.relocate_orphans(report.drift_violations)

        print(f"  Operations: {drift_report.total_operations}")
        print(f"  Successful: {drift_report.successful}")
        print(f"  Failed: {drift_report.failed}")

        total_operations += drift_report.total_operations
        total_successful += drift_report.successful
        total_failed += drift_report.failed

    # Hierarchy enforcement
    if (args.all or args.hierarchy) and report.hierarchy_violations:
        print(f"\n{'[DRY-RUN] ' if dry_run else ''}Fixing hierarchy violations...")
        hierarchy_report = relocator.enforce_hierarchy(report.hierarchy_violations)

        print(f"  Operations: {hierarchy_report.total_operations}")
        print(f"  Successful: {hierarchy_report.successful}")
        print(f"  Failed: {hierarchy_report.failed}")

        total_operations += hierarchy_report.total_operations
        total_successful += hierarchy_report.successful
        total_failed += hierarchy_report.failed

    # Gravity enforcement
    if (args.all or args.gravity) and report.gravity_violations:
        print(f"\n{'[DRY-RUN] ' if dry_run else ''}Fixing gravity violations...")
        gravity_report = relocator.relocate_agents(report.gravity_violations)

        print(f"  Operations: {gravity_report.total_operations}")
        print(f"  Successful: {gravity_report.successful}")
        print(f"  Failed: {gravity_report.failed}")

        total_operations += gravity_report.total_operations
        total_successful += gravity_report.successful
        total_failed += gravity_report.failed

    # Import violations note
    if report.import_violations:
        print(f"\n⚠️  Import violations: {len(report.import_violations)}")
        print("   These require manual refactoring (cannot be auto-fixed)")

    # Summary
    print_header("ENFORCEMENT SUMMARY", "-", 60)

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
        print(f"   Check {relocator.log_file} for details")
        print("\n📋 Next: Run 'python scripts/ssot.py validate' to verify")

    return 0 if total_failed == 0 else 1


def cmd_status(args) -> int:
    """
    Status command: Show high-level compliance dashboard.

    Returns:
        Exit code (0 for success)
    """
    print_header("SSOT STATUS - Compliance Dashboard")

    # Run quick validation
    validator = UnifiedSSOTValidator(REPO)
    report = validator.validate_all()

    # Display dashboard
    print("Overall Health:")
    print(f"  Compliance Score: {report.compliance_score:.1f}%")
    print(f"  Status: {'✅ COMPLIANT' if report.is_compliant else '⚠️  NON-COMPLIANT'}")
    print()

    print("Violation Breakdown:")
    print(f"  Gravity:    {len(report.gravity_violations):3d} (agents in wrong layers)")
    print(f"  Imports:    {len(report.import_violations):3d} (upward dependencies)")
    print(f"  Hierarchy:  {len(report.hierarchy_violations):3d} (depth limit exceeded)")
    print(f"  Drift:      {len(report.drift_violations):3d} (unauthorized folders)")
    print(f"  {'─' * 40}")
    print(f"  Total:      {report.total_violations:3d}")
    print()

    print("System Statistics:")
    print(f"  Total agents: {report.total_agents}")
    print(f"  Files scanned: {report.total_files_scanned}")
    print(f"  Scan duration: {report.scan_duration:.2f}s")
    print()

    # Recommendations
    if not report.is_compliant:
        print("Recommended Actions:")

        if report.gravity_violations:
            print(f"  1. Fix {len(report.gravity_violations)} gravity violations:")
            print("     python scripts/ssot.py enforce --gravity --execute")

        if report.drift_violations:
            print(f"  2. Archive {len(report.drift_violations)} orphaned folders:")
            print("     python scripts/ssot.py enforce --drift --execute")

        if report.hierarchy_violations:
            print(f"  3. Flatten {len(report.hierarchy_violations)} deep folders:")
            print("     python scripts/ssot.py enforce --hierarchy --execute")

        if report.import_violations:
            print(f"  4. Refactor {len(report.import_violations)} import violations:")
            print("     (Manual refactoring required - see health report)")

        print()
        print("  Or fix all at once:")
        print("     python scripts/ssot.py enforce --execute")
    else:
        print("✅ No actions needed - system is fully compliant!")

    return 0


def main():
    """Main entry point for SSOT CLI."""
    parser = argparse.ArgumentParser(
        prog="ssot",
        description="SSOT - Sovereign Single Source of Truth CLI",
        epilog="For more information on a command, use: python scripts/ssot.py <command> --help",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan and list all discovered agents")
    scan_parser.add_argument(
        "--summary", action="store_true", help="Show summary by layer instead of full listing"
    )
    scan_parser.add_argument(
        "--violations-only", action="store_true", help="Show only agents with gravity violations"
    )
    scan_parser.add_argument("--limit", type=int, help="Limit number of agents displayed")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Run comprehensive SSOT validation")
    validate_parser.add_argument(
        "--summary", action="store_true", help="Show brief summary instead of full report"
    )
    validate_parser.add_argument(
        "--markdown", action="store_true", help="Save report as Markdown file"
    )
    validate_parser.add_argument("--json", action="store_true", help="Output report as JSON")
    validate_parser.add_argument("--output", type=str, help="Output file path for Markdown report")

    # Enforce command
    enforce_parser = subparsers.add_parser("enforce", help="Apply automated remediation")
    enforce_parser.add_argument(
        "--execute", action="store_true", help="Execute enforcement (default is dry-run)"
    )
    enforce_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    enforce_parser.add_argument(
        "--gravity", action="store_true", help="Fix gravity violations only"
    )
    enforce_parser.add_argument("--drift", action="store_true", help="Fix drift violations only")
    enforce_parser.add_argument(
        "--hierarchy", action="store_true", help="Fix hierarchy violations only"
    )
    enforce_parser.add_argument(
        "--all", action="store_true", default=True, help="Fix all violations (default)"
    )

    # Status command
    subparsers.add_parser("status", help="Show compliance dashboard")

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if args.command == "scan":
        return cmd_scan(args)
    elif args.command == "validate":
        return cmd_validate(args)
    elif args.command == "enforce":
        return cmd_enforce(args)
    elif args.command == "status":
        return cmd_status(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
