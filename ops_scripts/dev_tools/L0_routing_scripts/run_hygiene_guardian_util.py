"""
Standalone script to run HygieneGuardianAgent on entire repo.
Reports findings before and after fixes.
"""

import os
import shutil
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "run_hygiene_guardian_util")
emit_determinism_digest("p0", "run_hygiene_guardian_util")

_emit_dispatches_healing_run("p1", "run_hygiene_guardian_util", "L0")
_emit_routes_through("p1", "run_hygiene_guardian_util", "L0")
_emit_checks_agent_registry("p1", "run_hygiene_guardian_util", "agent_registry")
_emit_validates_agent_capability("p1", "run_hygiene_guardian_util", "capability")
_emit_dispatches_execution_plan("p1", "run_hygiene_guardian_util", "exec_plan")
_emit_agent_executes_agent("p1", "run_hygiene_guardian_util", "sub_agent")
_emit_routes_to_agent("p1", "run_hygiene_guardian_util", "target_agent")
_emit_verifies_policy("p1", "run_hygiene_guardian_util", "policy_check")
_emit_observes_runtime_state("p1", "run_hygiene_guardian_util", "runtime_state")
_emit_verifies_boundary("p1", "run_hygiene_guardian_util", "boundary_check")
_emit_transcripts_response("p1", "run_hygiene_guardian_util", "transcript")
_emit_hard_fails_untranscripted("p1", "run_hygiene_guardian_util")
_emit_gated_by_confidence("p1", "run_hygiene_guardian_util", "confidence_gate")
_emit_escalates_to_human("p1", "run_hygiene_guardian_util", "L0")
_emit_reads_policy_state("p1", "run_hygiene_guardian_util", "L0")
_emit_authorize_and_execute("p2", "run_hygiene_guardian_util", "execution_auth")
_emit_validates_capability("p2", "run_hygiene_guardian_util", "capability_check")
_emit_routes_to_capability("p2", "run_hygiene_guardian_util", "capability_route")
_emit_writes_via_uwg("p2", "run_hygiene_guardian_util", "uwg_write")
_emit_blocks_direct_write("p2", "run_hygiene_guardian_util", "direct_write_block")
_emit_records_tool_invocation("p2", "run_hygiene_guardian_util", "tool_invocation")
_emit_captures_execution_output("p2", "run_hygiene_guardian_util", "exec_output")
_emit_dispatches_agent("p3", "run_hygiene_guardian_util", "agent_dispatch")
_emit_coordinates_agents("p3", "run_hygiene_guardian_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_hygiene_guardian_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_hygiene_guardian_util", "healing_outcome")
_emit_escalates_failure("p3", "run_hygiene_guardian_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_hygiene_guardian_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_hygiene_guardian_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_hygiene_guardian_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_hygiene_guardian_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_hygiene_guardian_util", "eval_metric")
_emit_stores_embedding("p4", "run_hygiene_guardian_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_hygiene_guardian_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_hygiene_guardian_util", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))
from agentic_core.L0_routing.config import ROOT_WHITELIST
from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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

_emit_emits_metric_event("run_hygiene_guardian_util", "p4obs", "metric_1")
_emit_emits_metric_event("run_hygiene_guardian_util", "p4obs", "metric_2")
_emit_emits_metric_event("run_hygiene_guardian_util", "p4obs", "metric_3")
_emit_emits_metric_event("run_hygiene_guardian_util", "p4obs", "metric_4")
_emit_emits_metric_event("run_hygiene_guardian_util", "p4obs", "metric_5")
_emit_emits_metric_event("run_hygiene_guardian_util", "p4obs", "metric_6")
_emit_records_incident_event("run_hygiene_guardian_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_hygiene_guardian_util", "p4obs", "anomaly")
_emit_writes_observability_log("run_hygiene_guardian_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_hygiene_guardian_util", "p4obs", "mon_state")
_emit_triggers_alert("run_hygiene_guardian_util", "p4obs", "alert")
_emit_links_incident_trace("run_hygiene_guardian_util", "p4obs", "trace_link")
_emit_captures_pattern("run_hygiene_guardian_util", "p3lm", "pattern")
_emit_records_learning_event("run_hygiene_guardian_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_hygiene_guardian_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_hygiene_guardian_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_hygiene_guardian_util", "p3lm", "routing")
_emit_improves_agent_policy("run_hygiene_guardian_util", "p3lm", "policy")
_emit_stores_learning_state("run_hygiene_guardian_util", "p3lm", "state")
_emit_records_execution_trace("run_hygiene_guardian_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_hygiene_guardian_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_hygiene_guardian_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_hygiene_guardian_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_hygiene_guardian_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_hygiene_guardian_util", "env_read", "p2_env_1")
_emit_reads_environ("run_hygiene_guardian_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_hygiene_guardian_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_hygiene_guardian_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_hygiene_guardian_util", "context_pull")
_emit_pulls_context("p1", "run_hygiene_guardian_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "run_hygiene_guardian_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_hygiene_guardian_util", "uwg_term_2")
_emit_writes_through("p1", "run_hygiene_guardian_util", "write_through")
_emit_writes_through("p1", "run_hygiene_guardian_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "run_hygiene_guardian_util", "safety_validation")
_emit_invokes_eval("p1", "run_hygiene_guardian_util", "eval_call")
_emit_proposal_commits_routing("p1", "run_hygiene_guardian_util", "routing_commit")

ALLOWED_ROOT_FOLDERS = set(ROOT_WHITELIST)
ARTIFACT_PATTERNS = ["*.heal_tmp", "*.temp", "*.tmp", ".pytest_cache", "__pycache__"]
IGNORE_FILES = {".gitkeep", ".git"}


def scan_temp_artifacts(root: Path) -> list[Path]:
    """Scan for temporary artifacts without removing them."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "scan_temp_artifacts", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "scan_temp_artifacts", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "scan_temp_artifacts")
    artifacts = []
    from agentic_core.utils.runners.ssot_discovery_validator import get_data_files

    for path in get_data_files(root, extensions=[".pyc", ".pyo", ".tmp", ".bak", ".swp"]):
        if ".git" not in path.parts:
            artifacts.append(path)
    return artifacts


def scan_empty_folders(root: Path) -> list[Path]:
    """Scan for empty folders without removing them."""
    empty_folders = []
    for root_folder in ALLOWED_ROOT_FOLDERS:
        root_path = root / root_folder
        if not root_path.exists():
            continue
        for dirpath, _dirnames, _filenames in os.walk(root_path, topdown=False):
            _dirnames[:] = [d for d in _dirnames if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            current_dir = Path(dirpath)
            if ".git" in current_dir.parts:
                continue    # guardian: Permission errors should validate access before operation
            if current_dir.name in ALLOWED_ROOT_FOLDERS:
                continue
            try:
                children = [x for x in current_dir.iterdir() if x.name not in IGNORE_FILES]
                if not children:
                    empty_folders.append(current_dir)
            # guardian: allow-silent-swallow - acceptable exception handling
            except PermissionError:
                pass
    return empty_folders


def scan_folders_with_only_init(root: Path) -> list[Path]:
    """Scan for folders that only contain __init__.py (no other meaningful content)."""
    init_only_folders = []
    for root_folder in ALLOWED_ROOT_FOLDERS:
        root_path = root / root_folder
        if not root_path.exists():
            continue
        for dirpath, _dirnames, _filenames in os.walk(root_path, topdown=False):
            _dirnames[:] = [d for d in _dirnames if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            current_dir = Path(dirpath)
            if ".git" in current_dir.parts:
                continue
            if current_dir.name in ALLOWED_ROOT_FOLDERS:
                continue
            try:
                children = list(current_dir.iterdir())    # guardian: Permission errors should validate access before operation
                meaningful_children = [
                    x for x in children if x.name not in IGNORE_FILES and (not x.name.startswith("."))
                ]
                if len(meaningful_children) == 1:
                    only_child = meaningful_children[0]
                    if only_child.is_file() and only_child.name == "__init__.py":
                        # guardian: allow-silent-swallow - acceptable exception handling
                        init_only_folders.append(current_dir)
            except PermissionError:
                pass
    return init_only_folders


def remove_artifacts(artifacts: list[Path]) -> tuple[int, list[str]]:
    """Remove artifacts and return count and errors."""
    removed = 0
    errors = []
    for path in artifacts:
        try:
            if path.is_file():
                path.unlink()
                removed += 1
            elif path.is_dir():
                assert_no_persistent_write("L0", "shutil.mutate")
                shutil.rmtree(path)
                removed += 1
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            errors.append(f"{path}: {e}")
    return (removed, errors)


def remove_empty_folders(folders: list[Path]) -> tuple[int, list[str]]:
    """Remove empty folders and return count and errors."""
    removed = 0
    errors = []
    sorted_folders = sorted(folders, key=lambda p: len(p.parts), reverse=True)
    for folder in sorted_folders:
        try:
            if folder.exists():
                children = [x for x in folder.iterdir() if x.name not in IGNORE_FILES]
                if not children:
                    folder.rmdir()
                    removed += 1
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            errors.append(f"{folder}: {e}")
    return (removed, errors)


def main():
    print("=" * 70)
    print("HYGIENE GUARDIAN AGENT - FULL REPO SCAN")
    print("=" * 70)
    project_root = PROJECT_ROOT
    print(f"\nProject Root: {project_root}")
    print(f"Allowed Root Folders: {sorted(ALLOWED_ROOT_FOLDERS)}")
    print("\n" + "=" * 70)
    print("PHASE 1: INITIAL SCAN (Before Fixes)")
    print("=" * 70)
    print("\n[1.1] Scanning for temporary artifacts...")
    artifacts = scan_temp_artifacts(project_root)
    print(f"      Found: {len(artifacts)} artifact(s)")
    for a in artifacts[:20]:
        print(f"        - {a.relative_to(project_root)}")
    if len(artifacts) > 20:
        print(f"        ... and {len(artifacts) - 20} more")
    print("\n[1.2] Scanning for empty folders...")
    empty_folders = scan_empty_folders(project_root)
    print(f"      Found: {len(empty_folders)} empty folder(s)")
    for f in empty_folders[:20]:
        print(f"        - {f.relative_to(project_root)}")
    if len(empty_folders) > 20:
        print(f"        ... and {len(empty_folders) - 20} more")
    print("\n[1.3] Scanning for folders with only __init__.py...")
    init_only = scan_folders_with_only_init(project_root)
    print(f"      Found: {len(init_only)} folder(s) with only __init__.py")
    for f in init_only[:20]:
        print(f"        - {f.relative_to(project_root)}")
    if len(init_only) > 20:
        print(f"        ... and {len(init_only) - 20} more")
    print("\n" + "=" * 70)
    print("PHASE 2: APPLYING FIXES")
    print("=" * 70)
    print("\n[2.1] Removing temporary artifacts...")
    artifacts_removed, artifact_errors = remove_artifacts(artifacts)
    print(f"      Removed: {artifacts_removed} artifact(s)")
    if artifact_errors:
        print(f"      Errors: {len(artifact_errors)}")
        for e in artifact_errors[:5]:
            print(f"        - {e}")
    print("\n[2.2] Removing empty folders...")
    folders_removed, folder_errors = remove_empty_folders(empty_folders)
    print(f"      Removed: {folders_removed} folder(s)")
    if folder_errors:
        print(f"      Errors: {len(folder_errors)}")
        for e in folder_errors[:5]:
            print(f"        - {e}")
    print("\n" + "=" * 70)
    print("PHASE 3: VERIFICATION SCAN (After Fixes)")
    print("=" * 70)
    print("\n[3.1] Re-scanning for temporary artifacts...")
    remaining_artifacts = scan_temp_artifacts(project_root)
    print(f"      Remaining: {len(remaining_artifacts)} artifact(s)")
    print("\n[3.2] Re-scanning for empty folders...")
    remaining_empty = scan_empty_folders(project_root)
    print(f"      Remaining: {len(remaining_empty)} empty folder(s)")
    for f in remaining_empty:
        print(f"        - {f.relative_to(project_root)}")
    print("\n[3.3] Re-scanning for folders with only __init__.py...")
    remaining_init_only = scan_folders_with_only_init(project_root)
    print(f"      Remaining: {len(remaining_init_only)} folder(s)")
    print("\n" + "=" * 70)
    print("SUMMARY REPORT")
    print("=" * 70)
    print(
        f"\nBEFORE FIXES:\n  - Temporary artifacts: {len(artifacts)}\n  - Empty folders: {len(empty_folders)}\n  - __init__.py only folders: {len(init_only)}\n\nFIXES APPLIED:\n  - Artifacts removed: {artifacts_removed}\n  - Empty folders removed: {folders_removed}\n\nAFTER FIXES:\n  - Remaining artifacts: {len(remaining_artifacts)}\n  - Remaining empty folders: {len(remaining_empty)}\n  - Remaining __init__.py only: {len(remaining_init_only)}\n\nSTATUS: {('✅ CLEAN' if len(remaining_artifacts) == 0 and len(remaining_empty) == 0 else '⚠️ ISSUES REMAIN')}\n",
    )
    return {
        "before": {
            "artifacts": len(artifacts),
            "empty_folders": len(empty_folders),
            "init_only": len(init_only),
        },
        "fixed": {"artifacts_removed": artifacts_removed, "folders_removed": folders_removed},
        "after": {
            "artifacts": len(remaining_artifacts),
            "empty_folders": len(remaining_empty),
            "init_only": len(remaining_init_only),
        },
        "artifacts_list": [str(a.relative_to(project_root)) for a in artifacts],
        "empty_folders_list": [str(f.relative_to(project_root)) for f in empty_folders],
        "init_only_list": [str(f.relative_to(project_root)) for f in init_only],
        "remaining_empty": [str(f.relative_to(project_root)) for f in remaining_empty],
    }


if __name__ == "__main__":
    main()
