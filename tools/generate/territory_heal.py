"""
Simplified entry point for territory-level healing.

This replaces the complex execute_ssot_entrypoint.py with a straightforward
tool that can heal any territory without bypasses or complex workarounds.
"""

import argparse
import logging
import re
import sys
from pathlib import Path

from tqdm import tqdm


def _discover_repo_root(start: Path) -> Path:
    """Best-effort repository root discovery for direct script and package execution."""
    for candidate in (start, *start.parents):
        if (candidate / "agentic_core").exists() or (candidate / ".git").exists():
            return candidate
        if candidate.name == "tools" and (candidate / "generate").exists():
            return candidate.parent
    return start.parent


REPO_ROOT = _discover_repo_root(Path(__file__).resolve().parent)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.L3_orchestration.reasoning.territory_healing.territory_healer_adapters import (
    create_adapter_coordinator,
)


_TERRITORY_RE = re.compile(r"^[A-Za-z0-9_.\-/]+$")


def _resolve_project_root(project_root_arg: str) -> Path:
    """Resolve and validate the project root supplied via CLI."""
    project_root = Path(project_root_arg).expanduser().resolve()
    if not project_root.exists():
        raise FileNotFoundError(f"Project root does not exist: {project_root}")
    if not project_root.is_dir():
        raise NotADirectoryError(f"Project root is not a directory: {project_root}")
    return project_root


def _validate_territory_name(territory: str) -> str:
    """Reject unsafe territory names before they reach lower layers."""
    if not territory:
        raise ValueError("Territory name cannot be empty")
    if not _TERRITORY_RE.fullmatch(territory):
        raise ValueError(f"Unsafe territory name: {territory}")
    normalized = territory.strip()
    if normalized.startswith("/") or normalized.startswith("\\"):
        raise ValueError(f"Absolute territory paths are not allowed: {territory}")
    if ".." in Path(normalized).parts:
        raise ValueError(f"Parent traversal is not allowed in territory name: {territory}")
    return normalized


def setup_logging(verbose: bool = False) -> None:
    """Setup basic logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def main() -> None:
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
        """,
    )

    parser.add_argument(
        "--territory",
        type=str,
        help="Specific territory to heal (e.g., tests, agentic_core, apps_eval)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Heal all detected territories",
    )
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Scan for violations without healing (dry-run)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--project-root",
        type=str,
        default=str(REPO_ROOT),
        help=f"Project root directory (default: {REPO_ROOT})",
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
    try:
        project_root = _resolve_project_root(args.project_root)
    except (FileNotFoundError, NotADirectoryError, OSError, ValueError) as e:
        logger.error(f"Invalid --project-root: {e}")
        sys.exit(1)

    logger.info(f"Initializing coordinator for project: {project_root}")

    try:
        coordinator = create_adapter_coordinator(project_root)
    except (ImportError, AttributeError, OSError, ValueError) as e:
        logger.exception(f"Failed to create coordinator: {e}")
        sys.exit(1)

    # Determine territories to process
    if args.all:
        auto_detected = coordinator._auto_detect_territories()
        try:
            territories = sorted({_validate_territory_name(t) for t in auto_detected})
        except ValueError as e:
            logger.error(f"Unsafe auto-detected territory: {e}")
            sys.exit(1)
        logger.info(f"Auto-detected territories: {territories}")
    else:
        try:
            territories = [_validate_territory_name(args.territory)]
        except ValueError as e:
            logger.error(str(e))
            sys.exit(1)

    # Process territories
    exit_code = 0
    for territory in tqdm(territories, desc="[ADG] Healing territories", unit="territory"):
        try:
            if args.scan_only:
                report = coordinator.validate_territory(territory)
                logger.info(
                    f"\n=== SCAN RESULTS FOR {territory} ===\n"
                    f"  Violations found: {report.total_violations_found}\n"
                    f"  Agents scanned: {len(report.scan_results)}",
                )
            else:
                report = coordinator.heal_territory(territory, verbose=args.verbose)
                logger.info(
                    f"\n=== HEALING RESULTS FOR {territory} ===\n"
                    f"  Violations found: {report.total_violations_found}\n"
                    f"  Violations fixed: {report.total_violations_fixed}\n"
                    f"  Agents executed: {len(report.agents_executed)}\n"
                    f"  Success: {report.success}",
                )

                if report.errors:
                    logger.warning(f"  Errors: {len(report.errors)}")
                    for error in report.errors[:5]:  # Show first 5 errors
                        logger.warning(f"    - {error}")

                if not report.success:
                    exit_code = 1

        except (AttributeError, OSError, RuntimeError, ValueError) as e:
            logger.exception(f"Failed to process territory {territory}: {e}")
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
