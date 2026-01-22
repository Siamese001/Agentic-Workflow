#!/usr/bin/env python3
"""
[PHASE 10] Sovereign Convergence Terminal - Execution Driver.

This script triggers the final purge and baseline lockdown.
It should be run only after a full git commit to allow rollback.

Usage:
    python scripts/maintenance/execute_convergence.py

Exit Codes:
    0 - Convergence successful, repository is architecture-pure
    1 - Convergence failed, unresolved violations remain
    2 - Error during execution
"""

import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
Logger = logging.getLogger("ConvergenceDriver")


def run_terminal_convergence() -> int:
    """Execute the terminal sovereign convergence."""
    try:
        project_root = Path(__file__).resolve().parent.parent.parent
        sys.path.insert(0, str(project_root))

            ArchitectureGovernorAgent,
        )

        Logger.info(f"Targeting Repository: {project_root}")
        Logger.info("=" * 60)
        Logger.info("PHASE 10: SOVEREIGN CONVERGENCE TERMINAL")
        Logger.info("=" * 60)

        # Initialize the Governor with full healing authority
        agent = ArchitectureGovernorAgent(
            project_root=project_root,
            auto_approve=True,
            healing_enabled=True,
        )

        # Execute Terminal Convergence
        result = agent.execute_sovereign_convergence()

        # Extract results
        purge_status = result.get("purge_status", {})
        lockdown_status = result.get("lockdown_status", (False, {}))
        final_purity = result.get("final_purity", False)

        # Report purge statistics
        raw_purge = purge_status.get("_raw_result", purge_status)
        violations_found = raw_purge.get("violations_found", 0)
        violations_fixed = raw_purge.get("violations_fixed", 0)

        Logger.info("=" * 60)
        Logger.info("CONVERGENCE REPORT")
        Logger.info("=" * 60)
        Logger.info(f"Violations Found: {violations_found}")
        Logger.info(f"Violations Fixed: {violations_fixed}")
        Logger.info(f"Final Purity: {final_purity}")

        if final_purity:
            Logger.info("=" * 60)
            Logger.info("[OK] CONVERGENCE SUCCESS: Repository is now 100% Architecture-Pure.")
            Logger.info("The Golden Baseline has been established.")
            Logger.info("=" * 60)
            return 0
        else:
            # Extract remaining violations
            is_pure, lockdown_details = lockdown_status
            raw_lockdown = lockdown_details.get("_raw_result", lockdown_details)
            remaining = raw_lockdown.get("violations_found", 0)

            Logger.error("=" * 60)
            Logger.error("[FAIL] CONVERGENCE INCOMPLETE: Unresolved violations remain.")
            Logger.error(f"Remaining Violations: {remaining}")
            Logger.error("Run again or investigate manually.")
            Logger.error("=" * 60)
            return 1

    except ImportError as e:
        Logger.error(f"[ERROR] Import Error: {e}")
        Logger.error("Ensure agentic_core is properly installed.")
        return 2
    except Exception as e:
        Logger.error(f"[ERROR] Execution Error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(run_terminal_convergence())