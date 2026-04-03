"""
Simplified entry point for territory-level healing.

This replaces the complex execute_ssot_entrypoint.py with a straightforward
tool that can heal any territory without bypasses or complex workarounds.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path if needed
REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent.resolve()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.L0_routing.orchestration.territory_healing_coordinator import (
    TerritoryHealingCoordinator,
    create_default_coordinator,
)


def setup_logging(verbose: bool = False) -> None:
    """Setup basic logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )


def main():
    """Main entry point for territory healing."""
    parser = argparse.ArgumentParser(
        description="Simplified territory-level healing orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan territory for violations (dry-run)
  python -m agentic_core.L0_routing.orchestration.territory_heal --territory tests --scan-only

  # Heal a specific territory
  python -m agentic_core.L0_routing.orchestration.territory_heal --territory tests

  # Heal all territories
  python -m agentic_core.L0_routing.orchestration.territory_heal --all

  # Verbose output
  python -m agentic_core.L0_routing.orchestration.territory_heal --territory tests --verbose
        """
    )

    parser.add_argument(
        "--territory",
        type=str,
        help="Specific territory to heal (e.g., tests, agentic_core, apps_eval)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Heal all detected territories"
    )
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Scan for violations without healing (dry-run)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--project-root",
        type=str,
        default=str(REPO_ROOT),
        help=f"Project root directory (default: {REPO_ROOT})"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger("territory_heal")

    # Validate arguments
    if not args.territory and not args.all:
        logger.error("Must specify --territory or --all")
        sys.exit(1)

    # Create coordinator with all agents
    project_root = Path(args.project_root)
    logger.info(f"Initializing coordinator for project: {project_root}")

    try:
        coordinator = create_default_coordinator(project_root)
    except Exception as e:
        logger.exception(f"Failed to create coordinator: {e}")
        sys.exit(1)

    # Determine territories to process
    if args.all:
        territories = coordinator._auto_detect_territories()
        logger.info(f"Auto-detected territories: {territories}")
    else:
        territories = [args.territory]

    # Process territories
    exit_code = 0
    for territory in territories:
        try:
            if args.scan_only:
                report = coordinator.validate_territory(territory)
                logger.info(
                    f"\n=== SCAN RESULTS FOR {territory} ===\n"
                    f"  Violations found: {report.total_violations_found}\n"
                    f"  Agents scanned: {len(report.scan_results)}"
                )
            else:
                report = coordinator.heal_territory(territory, verbose=args.verbose)
                logger.info(
                    f"\n=== HEALING RESULTS FOR {territory} ===\n"
                    f"  Violations found: {report.total_violations_found}\n"
                    f"  Violations fixed: {report.total_violations_fixed}\n"
                    f"  Agents executed: {len(report.agents_executed)}\n"
                    f"  Success: {report.success}"
                )

                if report.errors:
                    logger.warning(f"  Errors: {len(report.errors)}")
                    for error in report.errors[:5]:  # Show first 5 errors
                        logger.warning(f"    - {error}")

                if not report.success:
                    exit_code = 1

        except Exception as e:
            logger.exception(f"Failed to process territory {territory}: {e}")
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
