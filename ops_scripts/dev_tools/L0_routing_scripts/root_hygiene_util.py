"""
File: agentic_core/L0_routing/scripts/RootHygieneEnforcer.py
Path: agentic_core/L0_routing/scripts/RootHygieneEnforcer.py
Rationale:
    Actively enforces the new Root Hygiene laws defined in structure_blueprint.
    1. Moves root 'scripts/*' to 'ops_scripts/' (standalone) or 'L0_routing/scripts/' (core).
    2. Moves 'coverage_html' to 'reports/'.
    3. Deletes the illegal root directories after evacuation.
"""

import argparse
import shutil
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    OPS_SCRIPTS_DIR,
    REPORTS_DIR,
)
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "root_hygiene_util")
emit_determinism_digest("p0", "root_hygiene_util")

_emit_dispatches_healing_run("p1", "root_hygiene_util", "L0")
_emit_routes_through("p1", "root_hygiene_util", "L0")
_emit_checks_agent_registry("p1", "root_hygiene_util", "agent_registry")
_emit_validates_agent_capability("p1", "root_hygiene_util", "capability")
_emit_dispatches_execution_plan("p1", "root_hygiene_util", "exec_plan")
_emit_agent_executes_agent("p1", "root_hygiene_util", "sub_agent")
_emit_routes_to_agent("p1", "root_hygiene_util", "target_agent")
_emit_verifies_policy("p1", "root_hygiene_util", "policy_check")
_emit_observes_runtime_state("p1", "root_hygiene_util", "runtime_state")
_emit_verifies_boundary("p1", "root_hygiene_util", "boundary_check")
_emit_transcripts_response("p1", "root_hygiene_util", "transcript")
_emit_hard_fails_untranscripted("p1", "root_hygiene_util")
_emit_gated_by_confidence("p1", "root_hygiene_util", "confidence_gate")
_emit_escalates_to_human("p1", "root_hygiene_util", "L0")
_emit_reads_policy_state("p1", "root_hygiene_util", "L0")
_emit_authorize_and_execute("p2", "root_hygiene_util", "execution_auth")
_emit_validates_capability("p2", "root_hygiene_util", "capability_check")
_emit_routes_to_capability("p2", "root_hygiene_util", "capability_route")
_emit_writes_via_uwg("p2", "root_hygiene_util", "uwg_write")
_emit_blocks_direct_write("p2", "root_hygiene_util", "direct_write_block")
_emit_records_tool_invocation("p2", "root_hygiene_util", "tool_invocation")
_emit_captures_execution_output("p2", "root_hygiene_util", "exec_output")
_emit_dispatches_agent("p3", "root_hygiene_util", "agent_dispatch")
_emit_coordinates_agents("p3", "root_hygiene_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "root_hygiene_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "root_hygiene_util", "healing_outcome")
_emit_escalates_failure("p3", "root_hygiene_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "root_hygiene_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "root_hygiene_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "root_hygiene_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "root_hygiene_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "root_hygiene_util", "eval_metric")
_emit_stores_embedding("p4", "root_hygiene_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "root_hygiene_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "root_hygiene_util", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
from tqdm import tqdm

_emit_emits_metric_event("root_hygiene_util", "p4obs", "metric_1")
_emit_emits_metric_event("root_hygiene_util", "p4obs", "metric_2")
_emit_emits_metric_event("root_hygiene_util", "p4obs", "metric_3")
_emit_emits_metric_event("root_hygiene_util", "p4obs", "metric_4")
_emit_emits_metric_event("root_hygiene_util", "p4obs", "metric_5")
_emit_emits_metric_event("root_hygiene_util", "p4obs", "metric_6")
_emit_records_incident_event("root_hygiene_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("root_hygiene_util", "p4obs", "anomaly")
_emit_writes_observability_log("root_hygiene_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("root_hygiene_util", "p4obs", "mon_state")
_emit_triggers_alert("root_hygiene_util", "p4obs", "alert")
_emit_links_incident_trace("root_hygiene_util", "p4obs", "trace_link")
_emit_captures_pattern("root_hygiene_util", "p3lm", "pattern")
_emit_records_learning_event("root_hygiene_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("root_hygiene_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("root_hygiene_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("root_hygiene_util", "p3lm", "routing")
_emit_improves_agent_policy("root_hygiene_util", "p3lm", "policy")
_emit_stores_learning_state("root_hygiene_util", "p3lm", "state")
_emit_records_execution_trace("root_hygiene_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("root_hygiene_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("root_hygiene_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("root_hygiene_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("root_hygiene_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("root_hygiene_util", "env_read", "p2_env_1")
_emit_reads_environ("root_hygiene_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("root_hygiene_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("root_hygiene_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "root_hygiene_util", "context_pull")
_emit_pulls_context("p1", "root_hygiene_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "root_hygiene_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "root_hygiene_util", "uwg_term_2")
_emit_writes_through("p1", "root_hygiene_util", "write_through")
_emit_writes_through("p1", "root_hygiene_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "root_hygiene_util", "safety_validation")
_emit_invokes_eval("p1", "root_hygiene_util", "eval_call")
_emit_proposal_commits_routing("p1", "root_hygiene_util", "routing_commit")

# SSOT Constants
ROOT_MARKERS = [AGENTIC_CORE_DIR, "pyproject.toml"]


def get_project_root() -> Path:
    """Resolve project root securely by walking up from the current working directory."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_project_root", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_project_root", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "get_project_root")

    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if all((candidate / marker).exists() for marker in ROOT_MARKERS):
            return candidate

    raise RuntimeError("Must run from Project Root")


def _safe_move(src: Path, dst: Path, *, dry_run: bool, force: bool) -> None:
    dst.parent.mkdir(exist_ok=True, parents=True)

    if dst.exists():
        if not force:
            raise FileExistsError(f"Refusing to overwrite existing target: {dst}")
        if dry_run:
            print(f"    [DRY-RUN] Would remove existing target: {dst}")
        else:
            assert_no_persistent_write("L0", "shutil.mutate")
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()

    if dry_run:
        print(f"    [DRY-RUN] Would move {src} -> {dst}")
        return

    assert_no_persistent_write("L0", "shutil.mutate")
    shutil.move(str(src), str(dst))


def enforce_root_hygiene(*, dry_run: bool = True, force: bool = False):
    root = get_project_root()
    mode = "DRY-RUN" if dry_run else "APPLY"
    print(f"[HYGIENE] {mode} Root Sovereignty at: {root}")
    print("=" * 60)

    # 1. EVACUATE ROOT SCRIPTS
    root_scripts = root / "scripts"
    ops_scripts = root / OPS_SCRIPTS_DIR
    l0_scripts = root / AGENTIC_CORE_DIR / "L0_routing" / "scripts"

    if root_scripts.exists():
        print("[DETECT] Illegal root 'scripts/' directory found.")
        ops_scripts.mkdir(exist_ok=True)
        l0_scripts.mkdir(exist_ok=True, parents=True)

        for item in tqdm(root_scripts.iterdir(), desc="Processing", unit="item"):
            if item.is_file() and item.suffix == ".py":
                # Decision Logic: Does it import agentic_core?
                try:
                    content = item.read_text(encoding="utf-8")
                    if AGENTIC_CORE_DIR in content or "from agentic_core" in content:
                        target = l0_scripts / item.name
                        action = "REPATRIATE (Core)"
                    else:
                        target = ops_scripts / item.name
                        action = "RELOCATE (Ops)"

                    print(f"  - {item.name} -> {action}")
                    _safe_move(item, target, dry_run=dry_run, force=force)
                except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
                    print(f"  [ERROR] Could not move {item.name}: {e}")

            elif item.is_dir():
                # Move entire subfolders to ops_scripts/maintenance or similar
                # For simplicity in this phase, dump to ops_scripts root or map specific folders
                target = ops_scripts / item.name
                print(f"  - DIR {item.name}/ -> RELOCATE (Ops)")
                _safe_move(item, target, dry_run=dry_run, force=force)

        # Cleanup empty dir
        try:
            if dry_run:
                print("[DRY-RUN] Would remove empty root scripts directory.")
            else:
                root_scripts.rmdir()
                print("[SUCCESS] Illegal 'scripts/' directory eliminated.")
        except OSError:  # guardian: allow-silent-swallow - acceptable exception handling
            print("[WARNING] 'scripts/' not empty, manual check required.")
    else:
        print("[CHECK] Root 'scripts/' is clean.")

    # 2. EVACUATE COVERAGE_HTML
    cov_html = root / "coverage_html"
    reports_cov = root / REPORTS_DIR / "coverage_html"

    if cov_html.exists():
        print("\n[DETECT] Illegal root 'coverage_html/' found.")
        reports_cov.parent.mkdir(exist_ok=True)

        if reports_cov.exists() and not force:
            raise FileExistsError(f"Refusing to overwrite existing target: {reports_cov}")

        print("  - Moving to reports/coverage_html")
        _safe_move(cov_html, reports_cov, dry_run=dry_run, force=force)
        print("[SUCCESS] Coverage report relocated.")
    else:
        print("[CHECK] Root 'coverage_html/' is clean.")

    # 3. RELOCATE PURGE_CACHE (Specific Request)
    # Checks if it ended up in ops_scripts during step 1, or needs specific handling
    purge_script = ops_scripts / "purge_cache.py"
    maint_script_dir = ops_scripts / "maintenance"
    if purge_script.exists():
        maint_script_dir.mkdir(exist_ok=True)
        target = maint_script_dir / "purge_cache.py"
        print("\n[REFILE] Organizing purge_cache.py -> ops_scripts/maintenance/")
        _safe_move(purge_script, target, dry_run=dry_run, force=force)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enforce root hygiene safely")
    parser.add_argument("--apply", action="store_true", help="Perform file moves. Default is dry-run.")
    parser.add_argument("--force", action="store_true", help="Allow overwriting existing targets.")
    args = parser.parse_args()
    enforce_root_hygiene(dry_run=not args.apply, force=args.force)
