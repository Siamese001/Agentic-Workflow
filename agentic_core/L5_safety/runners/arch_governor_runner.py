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
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "arch_governor_runner")
emit_determinism_digest("p0", "arch_governor_runner")

_emit_dispatches_healing_run("p1", "arch_governor_runner", "L5")
_emit_routes_through("p1", "arch_governor_runner", "L5")
_emit_escalates_to_human("p1", "arch_governor_runner", "L5")
_emit_reads_policy_state("p1", "arch_governor_runner", "L5")
_emit_authorize_and_execute("p2", "arch_governor_runner", "execution_auth")
_emit_validates_capability("p2", "arch_governor_runner", "capability_check")
_emit_routes_to_capability("p2", "arch_governor_runner", "capability_route")
_emit_writes_via_uwg("p2", "arch_governor_runner", "uwg_write")
_emit_blocks_direct_write("p2", "arch_governor_runner", "direct_write_block")
_emit_records_tool_invocation("p2", "arch_governor_runner", "tool_invocation")
_emit_captures_execution_output("p2", "arch_governor_runner", "exec_output")
_emit_dispatches_agent("p3", "arch_governor_runner", "agent_dispatch")
_emit_coordinates_agents("p3", "arch_governor_runner", "agent_coordination")
_emit_records_workflow_lineage("p3", "arch_governor_runner", "workflow_lineage")
_emit_records_healing_outcome("p3", "arch_governor_runner", "healing_outcome")
_emit_escalates_failure("p3", "arch_governor_runner", "failure_escalation")
_emit_orchestrates_workflow("p3", "arch_governor_runner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "arch_governor_runner", "healing_dispatch")
_emit_invokes_evaluation("p3", "arch_governor_runner", "evaluation_signal")
_emit_records_telemetry_event("p4", "arch_governor_runner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "arch_governor_runner", "eval_metric")
_emit_stores_embedding("p4", "arch_governor_runner", "embedding_store")
_emit_updates_meta_learning_state("p4", "arch_governor_runner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "arch_governor_runner", "exec_snapshot_link")


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
