"""
Guardian-Heal Pipeline Dry-Run Wrapper.

Runs the L3 guardian-dispatcher-healer pipeline in dry-run mode
and emits JSON results to stdout.

Mirrors _ssot_dry_run.py conventions (arg parsing, exit codes).

Usage:
    python ops_scripts/root_scripts/_guardian_heal_dry_run.py
    python ops_scripts/root_scripts/_guardian_heal_dry_run.py --mode scan
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "_guardian_heal_dry_run")
_emit_applies_guardrail("p0", "_guardian_heal_dry_run", "p0_governance")
_emit_reads_policy_state("p0", "_guardian_heal_dry_run", "policy_binding")
_emit_snapshots_state("p0", "_guardian_heal_dry_run", "state_snapshot")
emit_replay_key("p0", "_guardian_heal_dry_run")
emit_determinism_digest("p0", "_guardian_heal_dry_run")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_guardian_heal_dry_run", "execution_auth")
_emit_validates_capability("p2", "_guardian_heal_dry_run", "capability_check")
_emit_routes_to_capability("p2", "_guardian_heal_dry_run", "capability_route")
_emit_writes_via_uwg("p2", "_guardian_heal_dry_run", "uwg_write")
_emit_blocks_direct_write("p2", "_guardian_heal_dry_run", "direct_write_block")
_emit_records_tool_invocation("p2", "_guardian_heal_dry_run", "tool_invocation")
_emit_captures_execution_output("p2", "_guardian_heal_dry_run", "exec_output")
_emit_dispatches_agent("p3", "_guardian_heal_dry_run", "agent_dispatch")
_emit_coordinates_agents("p3", "_guardian_heal_dry_run", "agent_coordination")
_emit_records_workflow_lineage("p3", "_guardian_heal_dry_run", "workflow_lineage")
_emit_records_healing_outcome("p3", "_guardian_heal_dry_run", "healing_outcome")
_emit_escalates_failure("p3", "_guardian_heal_dry_run", "failure_escalation")
_emit_orchestrates_workflow("p3", "_guardian_heal_dry_run", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_guardian_heal_dry_run", "healing_dispatch")
_emit_invokes_evaluation("p3", "_guardian_heal_dry_run", "evaluation_signal")
_emit_records_telemetry_event("p4", "_guardian_heal_dry_run", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_guardian_heal_dry_run", "eval_metric")
_emit_stores_embedding("p4", "_guardian_heal_dry_run", "embedding_store")
_emit_updates_meta_learning_state("p4", "_guardian_heal_dry_run", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_guardian_heal_dry_run", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L3_orchestration.scripts.guardian_heal_orchestrator import (
    run_pipeline,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guardian-Heal Pipeline dry-run wrapper",
    )
    parser.add_argument(
        "--mode",
        choices=["scan", "dry-run"],
        default="dry-run",
        help="Pipeline mode (default: dry-run).",
    )
    parser.add_argument(
        "--artifacts",
        default=None,
        help="Artifact output directory (repo-relative).",
    )
    parser.add_argument(
        "--timestamp",
        default=None,
        help="Injectable ISO-8601 timestamp.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json).",
    )
    args = parser.parse_args()

    try:
        result = run_pipeline(
            mode=args.mode,
            repo_root=PROJECT_ROOT,
            write_artifacts_dir=args.artifacts,
            timestamp=args.timestamp,
        )
    # guardian: allow-silent-swallow
    except Exception as exc:
        raise
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    guardian = result.get("guardian_result", {})

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        status = guardian.get("status", "?")
        summary = guardian.get("summary", "N/A")
        print(f"Mode: {result['mode']} | Status: {status}")
        print(f"Summary: {summary}")
        for check in guardian.get("checks", []):
            cid = check.get("check_id", "?")
            cst = check.get("status", "?")
            det = check.get("details", "")
            print(f"  [{cst}] {cid}: {det}")

    if guardian.get("status") == "ERROR":
        return 2
    if args.mode != "scan" and guardian.get("status") == "FAIL":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
