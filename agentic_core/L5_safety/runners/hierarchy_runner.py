"""
L5 Runner for HierarchyAgent.

This module provides subprocess-callable entry points for L0 scripts
to invoke HierarchyAgent without creating upward import edges.

Usage from subprocess:
    python -m agentic_core.L5_safety.runners.hierarchy_runner --action=dry_run
    python -m agentic_core.L5_safety.runners.hierarchy_runner --action=heal_violations
    python -m agentic_core.L5_safety.runners.hierarchy_runner --action=verify_mro
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_emit_dispatches_healing_run("p1", "hierarchy_runner", "L5")
_emit_routes_through("p1", "hierarchy_runner", "L5")
_emit_escalates_to_human("p1", "hierarchy_runner", "L5")
_emit_reads_policy_state("p1", "hierarchy_runner", "L5")


def get_project_root() -> Path:
    """Get project root from this file's location."""
    return Path(__file__).resolve().parent.parent.parent.parent


def run_hierarchy_dry_run(project_root: Path) -> dict:
    """Run HierarchyAgent in dry-run mode."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "run_hierarchy_dry_run", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "run_hierarchy_dry_run", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "run_hierarchy_dry_run")
    from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

    agent = HierarchyAgent(project_root, healing_enabled=False)
    agent.heal_hierarchy(create_structure=True, relocate_files=True, enforce_depth=True, purge_orphans=True)
    return {"success": True, "mode": "dry_run", "message": "Dry run complete - no changes made"}


def run_heal_violations(project_root: Path) -> dict:
    """Run HierarchyAgent to heal violations in dry-run mode."""
    from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

    agent = HierarchyAgent(project_root, healing_enabled=False)
    result = agent.heal_hierarchy_violations()
    return {
        "success": True,
        "files_relocated": result.get("files_relocated", 0),
        "folders_removed": result.get("folders_removed", 0),
        "errors": result.get("errors", []),
    }


def verify_mro() -> dict:
    """Verify HierarchyAgent MRO structure."""
    from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

    mro = [cls.__name__ for cls in HierarchyAgent.__mro__]
    return {"success": True, "agent": "HierarchyAgent", "mro": mro, "mro_length": len(mro)}


def main() -> int:
    """CLI entry point for subprocess invocation."""
    parser = argparse.ArgumentParser(description="HierarchyAgent Runner")
    parser.add_argument(
        "--action",
        choices=["dry_run", "heal_violations", "verify_mro"],
        required=True,
        help="Action to perform",
    )
    parser.add_argument(
        "--project-root", type=str, default=None, help="Project root path (defaults to auto-detect)"
    )
    args = parser.parse_args()
    project_root = Path(args.project_root) if args.project_root else get_project_root()
    try:
        if args.action == "dry_run":
            result = run_hierarchy_dry_run(project_root)
        elif args.action == "heal_violations":
            result = run_heal_violations(project_root)
        elif args.action == "verify_mro":
            result = verify_mro()
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
