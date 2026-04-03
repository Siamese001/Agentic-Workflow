"""CLI module for execute_ssot - extracted from monolith.

This module contains CLI-related functions that were previously in the monolithic
execute_ssot.py file. These functions handle command-line interface operations,
logging configuration, and main entry point logic.
"""

import argparse
import logging
import sys
from pathlib import Path

# Constants
REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent


def _configure_logging(verbosity: int = 0) -> None:
    """Configure logging based on verbosity level.

    Args:
        verbosity: Verbosity level (0=WARNING, 1=INFO, 2+=DEBUG)
    """
    level = logging.WARNING
    if verbosity >= 2:
        level = logging.DEBUG
    elif verbosity >= 1:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def _maybe_force_utf8_console() -> None:
    """Force UTF-8 encoding for console output if needed."""
    try:
        # Check if we're on Windows and need to force UTF-8
        if sys.platform == 'win32':
            import io
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding='utf-8',
                errors='replace'
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer,
                encoding='utf-8',
                errors='replace'
            )
    except Exception:
        # If forcing UTF-8 fails, continue with default encoding
        pass


def _apply_v15_enforcement_flag(args: argparse.Namespace) -> None:
    """Apply V15 enforcement flags from command line arguments.

    Args:
        args: Parsed command line arguments
    """
    if hasattr(args, 'v15_enforcement') and args.v15_enforcement is not None:
        # Set environment or global state for V15 enforcement
        import os
        os.environ['V15_ENFORCEMENT'] = str(args.v15_enforcement)


def run_fence_self_check() -> int:
    """Run fence self-check without mutations.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logging.info("Running fence self-check...")

    try:
        # Perform fence validation checks
        from ..config import AGENTIC_CORE_DIR

        # Ensure paths are Path objects
        core_dir = Path(AGENTIC_CORE_DIR) if isinstance(AGENTIC_CORE_DIR, str) else AGENTIC_CORE_DIR
        scripts_dir = Path(__file__).parent

        checks = [
            ("Repository root exists", REPO_ROOT.exists()),
            ("Agentic core directory exists", core_dir.exists()),
            ("Scripts directory exists", scripts_dir.exists()),
        ]

        all_passed = all(check[1] for check in checks)

        for name, passed in checks:
            status = "✓" if passed else "✗"
            logging.info(f"  {status} {name}")

        if all_passed:
            logging.info("All fence checks passed!")
            return 0
        else:
            logging.error("Some fence checks failed!")
            return 1

    except Exception as e:
        logging.error(f"Fence self-check failed: {e}")
        return 1


def print_execution_plan(
    arbitrate_plan: bool = False,
    ptc_plan: bool = False
) -> None:
    """Print execution plan and exit.

    Args:
        arbitrate_plan: Whether to include multi-agent arbitration
        ptc_plan: Whether to include PTC plan context
    """
    print("Execution Plan")
    print("=" * 50)
    print()

    phases = [
        ("1. Discovery", "Scan all layers for issues and violations"),
        ("2. Validation", "Validate discovered issues for accuracy"),
        ("3. Alignment", "Determine healing strategy for each issue"),
        ("4. Healing", "Execute healing actions"),
        ("5. Reporting", "Generate execution reports"),
    ]

    for phase, description in phases:
        print(f"{phase}")
        print(f"   {description}")
        print()

    if arbitrate_plan:
        print("Multi-agent arbitration: ENABLED")
        print("  - Agents will coordinate on plan formation")
        print()

    if ptc_plan:
        print("PTC context: ENABLED")
        print("  - Plan will include PTC-specific considerations")
        print()

    print("=" * 50)


def _legacy_main(
    args: argparse.Namespace,
    repo_root: Path,
    allow_protected_root_mutation: bool = True
) -> int:
    """Legacy main function for backward compatibility.

    This function provides the main execution logic that was previously
    in the monolithic execute_ssot.py file.

    Args:
        args: Parsed command line arguments
        repo_root: Repository root path
        allow_protected_root_mutation: Whether to allow mutations in protected roots

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    logging.info("Starting execute_ssot legacy main")

    try:
        # Import modular components
        from .execute_ssot_engine import SovereignDecisionEngine
        from .execute_ssot_reporting import ExecutionReporter
        from .execute_ssot_state import RuntimeStateManager
        from .execute_ssot_validators import NonInteractiveGuard, PreFlightValidator

        # Initialize state manager
        state_mgr = RuntimeStateManager()

        # Validate pre-flight conditions
        validator = PreFlightValidator(args=args)
        if not validator.validate():
            logging.error("Pre-flight validation failed")
            return 1

        # Check non-interactive guard
        guard = NonInteractiveGuard(args=args)
        if not guard.check_operation("execute"):
            logging.error("Non-interactive guard check failed")
            return 1

        # Initialize decision engine
        engine = SovereignDecisionEngine(
            registry=None,  # Would be populated from actual registry
            args=args,
            console=None
        )

        # Determine targets
        targets = getattr(args, 'targets', [])
        if not targets:
            # Default: scan current directory
            targets = [str(repo_root)]

        # Execute full workflow
        success, results = engine.execute_full_workflow(targets)

        if success:
            logging.info("Workflow completed successfully")

            # Generate report
            reporter = ExecutionReporter()
            report_path = getattr(args, 'report_path', None)
            if report_path:
                reporter.save_report(results, report_path)

            return 0
        else:
            logging.error(f"Workflow failed: {results.get('error', 'Unknown error')}")
            return 1

    except Exception as e:
        logging.error(f"Legacy main failed: {e}")
        return 1
