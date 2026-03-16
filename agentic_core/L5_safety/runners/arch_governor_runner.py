"""
L5 Runner for ArchitectureGovernorAgent.

This module provides subprocess-callable entry points for L0 scripts
to invoke ArchitectureGovernorAgent without creating upward import edges.

Usage from subprocess:
    python -m agentic_core.L5_safety.runners.arch_governor_runner --action=verify
    python -m agentic_core.L5_safety.runners.arch_governor_runner --action=capture_baseline
    python -m agentic_core.L5_safety.runners.arch_governor_runner --action=audit --targets=L0,L1
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "arch_governor_runner")
emit_determinism_digest("p0", "arch_governor_runner")

_emit_dispatches_healing_run("p1", "arch_governor_runner", "L5")
_emit_routes_through("p1", "arch_governor_runner", "L5")
_emit_escalates_to_human("p1", "arch_governor_runner", "L5")
_emit_reads_policy_state("p1", "arch_governor_runner", "L5")


def get_project_root() -> Path:
    """Get project root from this file's location."""
    return Path(__file__).resolve().parent.parent.parent.parent


def run_ci_verification(project_root: Path, auto_approve: bool = True) -> dict:
    """Run CI verification and return results as dict."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "run_ci_verification", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "run_ci_verification", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "run_ci_verification")
    from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

    agent = ArchitectureGovernorAgent(project_root=project_root, auto_approve=auto_approve)
    is_compliant, results = agent.run_ci_verification_sync()
    return {
        "success": is_compliant,
        "violations_found": results.get("violations_found", 0),
        "roots_scanned": results.get("roots_scanned", []),
        "raw_result": results,
    }


def capture_golden_baseline(project_root: Path) -> dict:
    """Capture golden baseline and return manifest path."""
    from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

    governor = ArchitectureGovernorAgent(project_root=project_root)
    manifest = governor.capture_golden_baseline()
    return {"success": True, "manifest_path": str(manifest) if manifest else None}


def run_audit(project_root: Path, targets: list[str] | None = None) -> dict:
    """Run audit with optional target territories."""
    from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

    governor = ArchitectureGovernorAgent(project_root=project_root, ci_mode=True)
    audit_results = governor.run_audit(target_territories=targets)
    return {"success": True, "audit_results": audit_results}


def main() -> int:
    """CLI entry point for subprocess invocation."""
    parser = argparse.ArgumentParser(description="ArchitectureGovernorAgent Runner")
    parser.add_argument(
        "--action", choices=["verify", "capture_baseline", "audit"], required=True, help="Action to perform"
    )
    parser.add_argument(
        "--project-root", type=str, default=None, help="Project root path (defaults to auto-detect)"
    )
    parser.add_argument(
        "--targets", type=str, default=None, help="Comma-separated target territories for audit"
    )
    parser.add_argument(
        "--auto-approve", action="store_true", default=True, help="Auto-approve mode (default: True)"
    )
    args = parser.parse_args()
    project_root = Path(args.project_root) if args.project_root else get_project_root()
    try:
        if args.action == "verify":
            result = run_ci_verification(project_root, args.auto_approve)
        elif args.action == "capture_baseline":
            result = capture_golden_baseline(project_root)
        elif args.action == "audit":
            targets = args.targets.split(",") if args.targets else None
            result = run_audit(project_root, targets)
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
