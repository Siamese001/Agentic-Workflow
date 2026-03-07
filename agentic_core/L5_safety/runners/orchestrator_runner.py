"""
L5 Runner for Orchestrator Agent Summoning.

This module provides subprocess-callable entry points for L0 scripts
to invoke orchestrator missions without creating upward import edges.

Usage from subprocess:
    python -m agentic_core.L5_safety.runners.orchestrator_runner \
        --action=mission --targets=L0,L1 --execute
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get project root from this file's location."""
    return Path(__file__).resolve().parent.parent.parent.parent


def run_orchestrator_mission(
    project_root: Path,
    targets: list[str],
    execute: bool = False,
) -> dict:
    """Run orchestrator mission with agent roster."""
    try:
        from agentic_core.L3_orchestration.ConsolidatedOrchestratorAgent import (
            get_consolidated_orchestrator,
        )

        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )
        from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import (
            GravityLeakRepairAgent,
        )
        from agentic_core.L5_safety.reasoning.HierarchyAgent import HierarchyAgent
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

        orchestrator = get_consolidated_orchestrator(project_root)

        # Assemble Roster for L3
        active_roster = [
            ("LocationAgent", LocationHealerAgent(project_root)),
            ("HierarchyAgent", HierarchyAgent(project_root)),
            ("ArchitectureGovernorAgent", ArchitectureGovernorAgent(project_root)),
            ("GravityLeakRepairAgent", GravityLeakRepairAgent(project_root)),
        ]

        mission_context = {
            "dry_run": not execute,
            "execute": execute,
            "domains": targets,
            "scan_mode": "leveraged",
        }

        # Execute via L3
        mission_results = orchestrator.run_mission(active_roster, mission_context)
        return {
            "success": True,
            "results": mission_results,
        }

    except ImportError as e:
        return {"success": False, "error": f"Import error: {e}", "fallback": True}
    # guardian: allow-silent-swallow
    except Exception as e:
        return {"success": False, "error": str(e), "fallback": True}


def main() -> int:
    """CLI entry point for subprocess invocation."""
    parser = argparse.ArgumentParser(description="Orchestrator Runner")
    parser.add_argument(
        "--action",
        choices=["mission"],
        required=True,
        help="Action to perform",
    )
    parser.add_argument(
        "--project-root",
        type=str,
        default=None,
        help="Project root path (defaults to auto-detect)",
    )
    parser.add_argument(
        "--targets",
        type=str,
        required=True,
        help="Comma-separated target territories",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help="Execute mode (vs dry-run)",
    )

    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else get_project_root()
    targets = args.targets.split(",") if args.targets else []

    try:
        if args.action == "mission":
            result = run_orchestrator_mission(project_root, targets, args.execute)
        else:
            result = {"success": False, "error": f"Unknown action: {args.action}"}

        print(json.dumps(result, default=str))
        return 0 if result.get("success") else 1

    # guardian: allow-silent-swallow
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
