"""Standalone CLI entry point for ADG Repair Orchestrator.

Usage:
    python tools/adg_repair.py --latest --dry-run
    python tools/adg_repair.py --timestamp 03122026_0512 --apply
    python tools/adg_repair.py --list-rules
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add repo root to path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.adg.repair import ADGRepairOrchestrator, RuleEngine
from tools.adg.repair.git_integration import GitIntegration
from tools.adg.report_parsers import CompositeReportParser


def find_latest_timestamp(adg_dir: Path) -> str | None:
    """Find the latest ADG timestamp from available files."""
    if not adg_dir.exists():
        return None

    # Look for closure validation reports
    pattern = "closure_validation_report_*.json"
    files = list(adg_dir.glob(pattern))

    if not files:
        return None

    # Extract timestamps and find latest
    timestamps = []
    for f in files:
        # Extract timestamp from filename
        stem = f.stem
        if "closure_validation_report_" in stem:
            ts = stem.replace("closure_validation_report_", "")
            timestamps.append(ts)

    if not timestamps:
        return None

    # Sort and return latest
    timestamps.sort()
    return timestamps[-1]


def cmd_list_rules(args: argparse.Namespace) -> int:
    """List all available repair rules."""
    engine = RuleEngine()
    rules = engine.list_rules()

    print("\nAvailable Repair Rules:")
    print("=" * 60)

    for rule in sorted(rules, key=lambda r: r.get("rule_priority", 100)):
        print(f"\n  ID: {rule['rule_id']}")
        print(f"  Name: {rule['rule_name']}")
        print(f"  Priority: {rule['rule_priority']}")
        print(f"  Description: {rule['rule_description']}")

    print(f"\n\nTotal: {len(rules)} rules")
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    """Analyze ADG reports and show deficiencies."""
    adg_dir = Path(args.adg_dir) if args.adg_dir else ROOT / "artifacts" / "adg"

    # Determine timestamp
    if args.latest:
        timestamp = find_latest_timestamp(adg_dir)
        if not timestamp:
            print("Error: Could not find latest ADG timestamp")
            return 1
        print(f"Using latest timestamp: {timestamp}")
    else:
        timestamp = args.timestamp

    if not timestamp:
        print("Error: No timestamp specified (use --timestamp or --latest)")
        return 1

    # Load and analyze reports
    print(f"\nLoading ADG reports from {adg_dir}...")
    parser = CompositeReportParser(adg_dir, timestamp)

    summary = parser.get_summary()
    print(f"\nReports available: {summary['available_reports']}/{summary['total_reports']}")

    # Extract deficiencies
    deficiencies = parser.extract_all_deficiencies()

    if not deficiencies:
        print("\n✓ No deficiencies found! ADG is in good shape.")
        return 0

    # Count by category
    counts = parser.get_deficiency_counts_by_category()

    print(f"\nDeficiencies Found: {len(deficiencies)}")
    print(f"  AUTO_FIX (can auto-fix):     {counts['auto_fix']}")
    print(f"  SUGGEST_FIX (needs review):  {counts['suggest_fix']}")
    print(f"  BLOCK_FIX (requires human):  {counts['block_fix']}")

    if args.verbose:
        print("\nDetailed Deficiencies:")
        print("=" * 60)
        for d in deficiencies[:20]:  # Show first 20
            category_str = d['category'].value if hasattr(d['category'], 'value') else str(d['category'])
            print(f"\n  [{category_str.upper()}] {d['issue_type']}")
            print(f"  File: {d['file_path']}")
            print(f"  Description: {d['description']}")
            if d.get('suggested_fix'):
                print(f"  Suggested Fix: {d['suggested_fix']}")

        if len(deficiencies) > 20:
            print(f"\n  ... and {len(deficiencies) - 20} more")

    return 0


def cmd_repair(args: argparse.Namespace) -> int:
    """Run repair orchestrator."""
    adg_dir = Path(args.adg_dir) if args.adg_dir else ROOT / "artifacts" / "adg"

    # Determine timestamp
    if args.latest:
        timestamp = find_latest_timestamp(adg_dir)
        if not timestamp:
            print("Error: Could not find latest ADG timestamp")
            return 1
        print(f"Using latest timestamp: {timestamp}")
    else:
        timestamp = args.timestamp

    if not timestamp:
        print("Error: No timestamp specified (use --timestamp or --latest)")
        return 1

    # Create git checkpoint if requested
    if args.git_checkpoint:
        git = GitIntegration(ROOT)
        checkpoint = git.create_checkpoint(f"adg-repair-{timestamp}")
        print(f"Created git checkpoint: {checkpoint}")

    # Run orchestrator
    print(f"\n{'=' * 60}")
    print("ADG Repair Orchestrator")
    print(f"{'=' * 60}")
    print(f"ADG Dir: {adg_dir}")
    print(f"Timestamp: {timestamp}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'APPLY'}")
    print(f"{'=' * 60}\n")

    orchestrator = ADGRepairOrchestrator(
        adg_dir=adg_dir,
        timestamp=timestamp,
        repo_root=ROOT,
    )

    skip_rules = args.skip_rule if args.skip_rule else []

    result = orchestrator.run(
        dry_run=args.dry_run,
        skip_rules=skip_rules,
    )

    orchestrator.print_summary()

    # Return appropriate exit code
    if result.failed_fixes > 0:
        return 2  # Some fixes failed
    if result.fixes_blocked > 0 and not args.dry_run:
        return 3  # Some fixes require human attention

    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="adg_repair",
        description="ADG Repair Orchestrator - Detect and fix ADG deficiencies",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list-rules command
    list_parser = subparsers.add_parser(
        "list-rules",
        help="List available repair rules",
    )
    list_parser.set_defaults(func=cmd_list_rules)

    # analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze ADG reports and show deficiencies",
    )
    analyze_parser.add_argument(
        "--timestamp",
        help="ADG timestamp (MMDDYYYY_HHMM format)",
    )
    analyze_parser.add_argument(
        "--latest",
        action="store_true",
        help="Use the latest available ADG timestamp",
    )
    analyze_parser.add_argument(
        "--adg-dir",
        help="ADG artifacts directory (default: artifacts/adg)",
    )
    analyze_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed deficiency information",
    )
    analyze_parser.set_defaults(func=cmd_analyze)

    # repair command
    repair_parser = subparsers.add_parser(
        "repair",
        help="Run repair orchestrator",
    )
    repair_parser.add_argument(
        "--timestamp",
        help="ADG timestamp (MMDDYYYY_HHMM format)",
    )
    repair_parser.add_argument(
        "--latest",
        action="store_true",
        help="Use the latest available ADG timestamp",
    )
    repair_parser.add_argument(
        "--adg-dir",
        help="ADG artifacts directory (default: artifacts/adg)",
    )
    repair_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes",
    )
    repair_parser.add_argument(
        "--apply",
        action="store_true",
        dest="apply_mode",
        help="Apply fixes (default is dry-run)",
    )
    repair_parser.add_argument(
        "--skip-rule",
        action="append",
        help="Skip a specific rule (can be specified multiple times)",
    )
    repair_parser.add_argument(
        "--git-checkpoint",
        action="store_true",
        help="Create a git checkpoint before applying fixes",
    )
    repair_parser.set_defaults(func=cmd_repair, dry_run=True)

    args = parser.parse_args()

    # Handle --apply flag
    if hasattr(args, "apply_mode") and args.apply_mode:
        args.dry_run = False

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
