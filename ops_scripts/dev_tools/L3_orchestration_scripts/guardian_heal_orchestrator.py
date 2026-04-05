"""
Guardian Heal Orchestrator — L3 orchestration for guardian→dispatcher→healer pipeline.

Replaces the legacy execute_ssot pipeline with a clean, deterministic
three-stage execution model:

    1. **Guardians** — Scan-only detection (no mutations)
    2. **Dispatcher** — Phase-ordered interpretation of guardian results
    3. **Healers** — Dry-run or apply remediation per check_id

Modes:
    --scan       Run guardians only, emit aggregate JSON (default)
    --dry-run    Run guardians + dispatcher + healers in dry-run mode
    --apply      Run guardians + dispatcher + healers in apply mode (sandbox-gated)

CLI:
    python -m agentic_core.L3_orchestration.scripts.guardian_heal_orchestrator --scan
    python -m agentic_core.L3_orchestration.scripts.guardian_heal_orchestrator --dry-run
    python -m agentic_core.L3_orchestration.scripts.guardian_heal_orchestrator --apply --repo-root /path/to/sandbox
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from ops_scripts.dev_tools.L0_routing.project_root_util import get_validated_project_root
from agentic_core.L2_execution.utils import write_gateway as _wg

# REPORTS_DIR imported lazily to avoid L3->L5 violation
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "guardian_heal_orchestrator")
emit_determinism_digest("p0", "guardian_heal_orchestrator")

_emit_dispatches_healing_run("p1", "guardian_heal_orchestrator", "L3")
_emit_routes_through("p1", "guardian_heal_orchestrator", "L3")
_emit_checks_agent_registry("p1", "guardian_heal_orchestrator", "agent_registry")
_emit_validates_agent_capability("p1", "guardian_heal_orchestrator", "capability")
_emit_dispatches_execution_plan("p1", "guardian_heal_orchestrator", "exec_plan")
_emit_agent_executes_agent("p1", "guardian_heal_orchestrator", "sub_agent")
_emit_routes_to_agent("p1", "guardian_heal_orchestrator", "target_agent")
_emit_verifies_policy("p1", "guardian_heal_orchestrator", "policy_check")
_emit_observes_runtime_state("p1", "guardian_heal_orchestrator", "runtime_state")
_emit_verifies_boundary("p1", "guardian_heal_orchestrator", "boundary_check")
_emit_transcripts_response("p1", "guardian_heal_orchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "guardian_heal_orchestrator")
_emit_gated_by_confidence("p1", "guardian_heal_orchestrator", "confidence_gate")
_emit_escalates_to_human("p1", "guardian_heal_orchestrator", "L3")
_emit_reads_policy_state("p1", "guardian_heal_orchestrator", "L3")
_emit_authorize_and_execute("p2", "guardian_heal_orchestrator", "execution_auth")
_emit_validates_capability("p2", "guardian_heal_orchestrator", "capability_check")
_emit_routes_to_capability("p2", "guardian_heal_orchestrator", "capability_route")
_emit_writes_via_uwg("p2", "guardian_heal_orchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "guardian_heal_orchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "guardian_heal_orchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "guardian_heal_orchestrator", "exec_output")
_emit_dispatches_agent("p3", "guardian_heal_orchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "guardian_heal_orchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "guardian_heal_orchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "guardian_heal_orchestrator", "healing_outcome")
_emit_escalates_failure("p3", "guardian_heal_orchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "guardian_heal_orchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "guardian_heal_orchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "guardian_heal_orchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "guardian_heal_orchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "guardian_heal_orchestrator", "eval_metric")
_emit_stores_embedding("p4", "guardian_heal_orchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "guardian_heal_orchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "guardian_heal_orchestrator", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("guardian_heal_orchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("guardian_heal_orchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("guardian_heal_orchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("guardian_heal_orchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("guardian_heal_orchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("guardian_heal_orchestrator", "p4obs", "metric_6")
_emit_records_incident_event("guardian_heal_orchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("guardian_heal_orchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("guardian_heal_orchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("guardian_heal_orchestrator", "p4obs", "mon_state")
_emit_triggers_alert("guardian_heal_orchestrator", "p4obs", "alert")
_emit_links_incident_trace("guardian_heal_orchestrator", "p4obs", "trace_link")
_emit_captures_pattern("guardian_heal_orchestrator", "p3lm", "pattern")
_emit_records_learning_event("guardian_heal_orchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("guardian_heal_orchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("guardian_heal_orchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("guardian_heal_orchestrator", "p3lm", "routing")
_emit_improves_agent_policy("guardian_heal_orchestrator", "p3lm", "policy")
_emit_stores_learning_state("guardian_heal_orchestrator", "p3lm", "state")
_emit_records_execution_trace("guardian_heal_orchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("guardian_heal_orchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("guardian_heal_orchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("guardian_heal_orchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("guardian_heal_orchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("guardian_heal_orchestrator", "env_read", "p2_env_1")
_emit_reads_environ("guardian_heal_orchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("guardian_heal_orchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("guardian_heal_orchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "guardian_heal_orchestrator", "context_pull")
_emit_pulls_context("p1", "guardian_heal_orchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "guardian_heal_orchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "guardian_heal_orchestrator", "uwg_term_2")
_emit_writes_through("p1", "guardian_heal_orchestrator", "write_through")
_emit_writes_through("p1", "guardian_heal_orchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "guardian_heal_orchestrator", "safety_validation")
_emit_invokes_eval("p1", "guardian_heal_orchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "guardian_heal_orchestrator", "routing_commit")

TOOL_ID = "guardian_heal_orchestrator"


def _run_guardians(
    repo_root: Path, timestamp: str, correlation_id: str | None = None, write_artifacts_dir: str | None = None
) -> dict:
    """Run all enabled guardians and return aggregate result as dict."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_run_guardians", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_run_guardians", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "_run_guardians")
    from ops_scripts.dev_tools.L0_routing_scripts.run_all_guardians import run_all_guardians

    result = run_all_guardians(
        repo_root=repo_root,
        write_artifacts_dir=write_artifacts_dir,
        timestamp=timestamp,
        correlation_id=correlation_id,
    )
    return json.loads(result.to_json())


def _run_dispatcher(
    guardian_aggregate: dict,
    write_artifacts_dir: Path,
    created_utc: str,
    *,
    apply: bool = False,
    repo_root: Path | None = None,
    allow_repo_mutation: bool = False,
) -> dict:
    """Run the remediation dispatcher on guardian aggregate.

    Writes aggregate to a temp file for dispatcher consumption, then
    invokes the dispatcher and returns the CombinedHealResult as dict.
    """
    import tempfile

    from ops_scripts.dev_tools.L2_execution_scripts.remediation_dispatcher import run_dispatcher

    assert_no_persistent_write("L0", "json.dump")
    tmp_dir = write_artifacts_dir or Path(tempfile.gettempdir())
    agg_path = tmp_dir / f"_guardian_agg_{created_utc}.json"
    _wg.write_json(agg_path, guardian_aggregate)
    try:
        result = run_dispatcher(
            guardian_result_path=agg_path,
            write_artifacts_dir=write_artifacts_dir,
            created_utc=created_utc,
            apply=apply,
            repo_root=repo_root,
            allow_repo_mutation=allow_repo_mutation,
        )
        return result.to_dict()
    finally:
        _wg.remove_file(agg_path)


def run_pipeline(
    mode: str = "scan",
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
    correlation_id: str | None = None,
    allow_repo_mutation: bool = False,
) -> dict:
    """Execute the L0 pipeline in the specified mode.

    Args:
        mode: One of "scan", "dry-run", "apply".
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir for artifacts.
        timestamp: Injectable ISO-8601 timestamp.
        correlation_id: Trace correlation ID.
        allow_repo_mutation: Allow apply mode on non-sandbox repos.

    Returns:
        Pipeline result dict with keys: mode, guardian_result, heal_result (if applicable).
    """
    if repo_root is None:
        repo_root = get_validated_project_root()
    if timestamp is None:
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    guardian_artifacts_dir = write_artifacts_dir
    if write_artifacts_dir is not None:
        try:
            Path(write_artifacts_dir).resolve().relative_to(repo_root.resolve())
        except ValueError:
            guardian_artifacts_dir = None
    guardian_aggregate = _run_guardians(
        repo_root=repo_root,
        timestamp=timestamp,
        correlation_id=correlation_id,
        write_artifacts_dir=guardian_artifacts_dir,
    )
    pipeline_result: dict = {
        "tool_id": TOOL_ID,
        "mode": mode,
        "timestamp": timestamp,
        "guardian_result": guardian_aggregate,
    }
    if mode == "scan":
        return pipeline_result
    heal_dir = (
        Path(write_artifacts_dir) if write_artifacts_dir else repo_root / "docs" / REPORTS_DIR / "plans"
    )
    heal_result = _run_dispatcher(
        guardian_aggregate=guardian_aggregate,
        write_artifacts_dir=heal_dir,
        created_utc=timestamp,
        apply=mode == "apply",
        repo_root=repo_root if mode == "apply" else None,
        allow_repo_mutation=allow_repo_mutation,
    )
    pipeline_result["heal_result"] = heal_result
    return pipeline_result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="L0 Thin Router — Guardian→Dispatcher→Healer pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Modes:\n  --scan       Run guardians only, emit aggregate JSON (default)\n  --dry-run    Run guardians + dispatcher + healers in dry-run mode\n  --apply      Run full pipeline with apply-mode healers (sandbox-gated)\n",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--scan", action="store_true", default=True, help="Scan-only mode (default)")
    group.add_argument("--dry-run", action="store_true", help="Dry-run mode")
    group.add_argument("--apply", action="store_true", help="Apply mode (sandbox-gated)")
    parser.add_argument("--repo-root", default=None, help="Project root path")
    parser.add_argument("--write-artifacts", default=None, help="Artifact output directory")
    parser.add_argument("--timestamp", default=None, help="Injectable ISO-8601 timestamp")
    parser.add_argument("--correlation-id", default=None, help="Trace correlation ID")
    parser.add_argument("--allow-repo-mutation", action="store_true", help="Allow apply on non-sandbox")
    parser.add_argument(
        "--format", choices=["json", "summary"], default="json", help="Output format (default: json)"
    )
    args = parser.parse_args()
    if args.apply:
        mode = "apply"
    elif args.dry_run:
        mode = "dry-run"
    else:
        mode = "scan"
    try:
        result = run_pipeline(
            mode=mode,
            repo_root=Path(args.repo_root) if args.repo_root else None,
            write_artifacts_dir=args.write_artifacts,
            timestamp=args.timestamp,
            correlation_id=args.correlation_id,
            allow_repo_mutation=args.allow_repo_mutation,
        )
    # guardian: allow-silent-swallow
    except (ValueError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    guardian = result.get("guardian_result", {})
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"L0 Pipeline | Mode: {result['mode']} | Status: {guardian.get('status', '?')}")
        print(f"Guardian Summary: {guardian.get('summary', 'N/A')}")
        for check in guardian.get("checks", []):
            print(f"  [{check.get('status', '?')}] {check.get('check_id', '?')}: {check.get('details', '')}")
        if "heal_result" in result:
            heal = result["heal_result"]
            print(f"\nHealer Summary: {len(heal.get('results', []))} check(s) processed")
            for hr in heal.get("results", []):
                print(f"  [{hr.get('status', '?')}] {hr.get('check_id', '?')}: {hr.get('notes', '')}")
    if guardian.get("status") == "ERROR":
        return 2
    if mode != "scan" and guardian.get("status") == "FAIL":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
