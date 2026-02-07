#!/usr/bin/env python3
"""
SSOT Folder Structure Check - CLI Entry Point

Phase 5.2 Upgrade: Fully headless, non-interactive CI verification.

This script is designed to be run by:
- Pre-commit hooks
- GitHub Actions CI pipelines
- Manual CLI verification

Returns:
    0: If structure is compliant.
    1: If drift/violations are detected.

Usage:
    python -m agentic_core.L5_safety.validators.ssot_folder_check
    python scripts/ssot_folder_check_util.py
"""

import argparse
import sys
from pathlib import Path

from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import (
    FilesystemSSOTReconcilerAgent,
)


def main() -> int:
    """
    Synchronous entry point for CI pipelines.

    No asyncio required - uses run_ci_verification_sync() for headless operation.
    """
    parser = argparse.ArgumentParser(
        description="SSOT Folder Structure Verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic check
    python -m agentic_core.L5_safety.validators.ssot_folder_check

    # Verbose output
    python -m agentic_core.L5_safety.validators.ssot_folder_check --verbose

    # Check specific path
    python -m agentic_core.L5_safety.validators.ssot_folder_check --path /path/to/project
        """,
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(".").resolve(),
        help="Project root path (default: current directory)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed violation information",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (for CI integration)",
    )

    args = parser.parse_args()
    project_root = args.path.resolve()

    print(f"[SCAN] SSOT Folder Verification: {project_root}")
    print("=" * 60)

    agent = FilesystemSSOTReconcilerAgent(project_root)
    is_compliant, results = agent.run_ci_verification_sync()

    if args.json:
        import json

        print(json.dumps(results, indent=2))
    else:
        print("\n[RESULTS]:")
        print(f"   Roots checked: {', '.join(results.get('roots_checked', []))}")
        print(f"   Hierarchy violations: {results.get('hierarchy_violations', 0)}")
        print(f"   Location violations: {results.get('location_violations', 0)}")
        print(f"   Total violations: {results.get('total_violations', 0)}")

    print("=" * 60)

    if is_compliant:
        print("[OK] SSOT Structure Verified. No violations.")
        return 0
    else:
        print("[FAIL] SSOT Violations Detected.")
        print("   Run 'python -m agentic_core.L5_safety.validators.HierarchyAgent --heal' to fix.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
