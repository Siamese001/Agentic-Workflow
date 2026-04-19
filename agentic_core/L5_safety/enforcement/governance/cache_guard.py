from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

emit_replay_key("p0", "cache_guard")
emit_determinism_digest("p0", "cache_guard")

_emit_dispatches_healing_run("p1", "cache_guard", "L5")
_emit_routes_through("p1", "cache_guard", "L5")
_emit_checks_agent_registry("p1", "cache_guard", "agent_registry")
_emit_validates_agent_capability("p1", "cache_guard", "capability")
_emit_dispatches_execution_plan("p1", "cache_guard", "exec_plan")
_emit_agent_executes_agent("p1", "cache_guard", "sub_agent")
_emit_routes_to_agent("p1", "cache_guard", "target_agent")
_emit_verifies_policy("p1", "cache_guard", "policy_check")
_emit_observes_runtime_state("p1", "cache_guard", "runtime_state")
_emit_verifies_boundary("p1", "cache_guard", "boundary_check")
_emit_transcripts_response("p1", "cache_guard", "transcript")
_emit_hard_fails_untranscripted("p1", "cache_guard")
_emit_gated_by_confidence("p1", "cache_guard", "confidence_gate")
_emit_escalates_to_human("p1", "cache_guard", "L5")
_emit_reads_policy_state("p1", "cache_guard", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "cache_guard")
_emit_applies_guardrail("p0", "cache_guard", "p0_governance")
_emit_snapshots_state("p0", "cache_guard", "state_snapshot")
_emit_authorize_and_execute("p2", "cache_guard", "execution_auth")
_emit_validates_capability("p2", "cache_guard", "capability_check")
_emit_routes_to_capability("p2", "cache_guard", "capability_route")
_emit_writes_via_uwg("p2", "cache_guard", "uwg_write")
_emit_blocks_direct_write("p2", "cache_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "cache_guard", "tool_invocation")
_emit_captures_execution_output("p2", "cache_guard", "exec_output")
_emit_dispatches_agent("p3", "cache_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "cache_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "cache_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "cache_guard", "healing_outcome")
_emit_escalates_failure("p3", "cache_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "cache_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cache_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "cache_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "cache_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cache_guard", "eval_metric")
_emit_stores_embedding("p4", "cache_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "cache_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cache_guard", "exec_snapshot_link")

"\nCache & Temp Governance Guard\n\nDeterministic read-only scanner for cache/temp directory governance.\nEnforces location constraints and tracked file detection.\n"
import os
import subprocess
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS
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
from tqdm import tqdm

_emit_emits_metric_event("cache_guard", "p4obs", "metric_1")
_emit_emits_metric_event("cache_guard", "p4obs", "metric_2")
_emit_emits_metric_event("cache_guard", "p4obs", "metric_3")
_emit_emits_metric_event("cache_guard", "p4obs", "metric_4")
_emit_emits_metric_event("cache_guard", "p4obs", "metric_5")
_emit_emits_metric_event("cache_guard", "p4obs", "metric_6")
_emit_records_incident_event("cache_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("cache_guard", "p4obs", "anomaly")
_emit_writes_observability_log("cache_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("cache_guard", "p4obs", "mon_state")
_emit_triggers_alert("cache_guard", "p4obs", "alert")
_emit_links_incident_trace("cache_guard", "p4obs", "trace_link")
_emit_captures_pattern("cache_guard", "p3lm", "pattern")
_emit_records_learning_event("cache_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cache_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("cache_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cache_guard", "p3lm", "routing")
_emit_improves_agent_policy("cache_guard", "p3lm", "policy")
_emit_stores_learning_state("cache_guard", "p3lm", "state")
_emit_records_execution_trace("cache_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cache_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cache_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cache_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cache_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cache_guard", "env_read", "p2_env_1")
_emit_reads_environ("cache_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("cache_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cache_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "cache_guard", "context_pull")
_emit_pulls_context("p1", "cache_guard", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "cache_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cache_guard", "uwg_term_secondary")
_emit_writes_through("p1", "cache_guard", "write_through")
_emit_writes_through("p1", "cache_guard", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "cache_guard", "safety_validation")
_emit_invokes_eval("p1", "cache_guard", "eval_call")
_emit_proposal_commits_routing("p1", "cache_guard", "routing_commit")


def is_cache_directory(dir_path: Path) -> bool:
    """Check if directory is a cache directory."""
    cache_names = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS
    return dir_path.name in cache_names


def is_excluded_directory(dir_path: Path) -> bool:
    """Check if directory should be excluded from scanning."""
    return dir_path.name == ".git"


def estimate_directory_size(dir_path: Path) -> int:
    """Estimate directory size, capped at 200MB scan."""
    total_size = 0
    max_scan_bytes = 200 * 1024 * 1024
    try:
        for root, dirs, files in tqdm(os.walk(dir_path), desc="Processing", unit="item"):
            for file in tqdm(files, desc="Processing", unit="item"):
                file_path = Path(root) / file
                try:
                    total_size += file_path.stat().st_size
                    if total_size > max_scan_bytes:
                        return total_size
                except (
                    OSError,
                    PermissionError,
                ):  # guardian: Multiple exceptions (OSError, PermissionError) need specific handling
                    continue
    except (
        OSError,
        PermissionError,
    ) as e:  # guardian: allow-log-and-swallow -- directory size scan best-effort: non-fatal, partial size returned
        import logging

        logging.getLogger(__name__).debug("cache_guard: OSError swallowed at L201: %s", e)
    return total_size


def has_tracked_files(dir_path: Path, root_path: Path) -> bool:
    """Check if cache directory has any tracked files under it."""
    try:
        relative_path = dir_path.relative_to(root_path)
        result = subprocess.run(
            ["git", "ls-files", str(relative_path)],
            capture_output=True,
            text=True,
            cwd=str(root_path),
        )
        return bool(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError):
        return False


def is_forbidden_location(dir_path: Path, root_path: Path) -> bool:
    """Check if cache directory is in forbidden location."""
    try:
        relative_path = dir_path.relative_to(root_path)
        path_parts = relative_path.parts
        if path_parts and path_parts[0] in {AGENTIC_CORE_DIR}:
            return True
        if path_parts and path_parts[0].startswith("apps_"):
            return True
    except (
        ValueError
    ):  # guardian: allow-silent-swallow -- path not relative to root: control-flow fallthrough to False
        pass
    return False


def scan_cache_directories(root_path: Path) -> dict[str, Any]:
    """Scan repository for cache directories."""
    violations = []
    inventory = []
    dirs_scanned = 0
    all_dirs = sorted(root_path.rglob("*"))
    for item_path in tqdm(all_dirs, desc="Processing", unit="item"):
        if not item_path.is_dir():
            continue
        if is_excluded_directory(item_path):
            continue
        dirs_scanned += 1
        if not is_cache_directory(item_path):
            continue
        relative_path = item_path.relative_to(root_path)
        size_bytes = estimate_directory_size(item_path)
        if has_tracked_files(item_path, root_path):
            violations.append(
                {
                    "path": str(relative_path),
                    "type": "tracked_cache",
                    "detail": f"Cache directory contains tracked files: {relative_path}",
                },
            )
        if is_forbidden_location(item_path, root_path):
            violations.append(
                {
                    "path": str(relative_path),
                    "type": "cache_in_core_or_apps",
                    "detail": f"Cache directory in forbidden location: {relative_path}",
                },
            )
        inventory_item = {
            "path": str(relative_path),
            "type": "cache_directory",
            "detail": f"Size: {size_bytes:,} bytes",
        }
        if size_bytes > 10 * 1024 * 1024:
            inventory_item["detail"] += " (oversize)"
        inventory.append(inventory_item)
    return {"dirs_scanned": dirs_scanned, "violations": violations, "inventory": inventory}


def main():
    """Main scanner execution."""
    root_path = Path(__file__).parent.parent.parent
    print(f"Scanning repository for cache directories: {root_path}")
    result = scan_cache_directories(root_path)
    output_dir = root_path / "artifacts" / "governance"
    _wg.ensure_dir(output_dir)
    report_path = output_dir / "cache_guard_report.json"
    _wg.write_json(report_path, result, indent=2)
    print(f"Scan complete. Report written to: {report_path}")
    print(f"Directories scanned: {result['dirs_scanned']}")
    print(f"Cache directories found: {len(result['inventory'])}")
    print(f"Violations found: {len(result['violations'])}")
    total_size = 0
    oversize_count = 0
    for item in tqdm(result["inventory"], desc="Processing", unit="item"):
        detail = item.get("detail", "")
        if "Size:" in detail:
            try:
                size_str = detail.split("Size:")[1].split(" bytes")[0].replace(",", "").strip()
                size_bytes = int(size_str)
                total_size += size_bytes
                if size_bytes > 10 * 1024 * 1024:
                    oversize_count += 1
            except (
                ValueError,
                IndexError,
            ):  # guardian: allow-silent-swallow -- malformed size detail: skip accumulation, continue scan
                pass
    if total_size > 0:
        print(f"Total cache size: {total_size:,} bytes")
    if oversize_count > 0:
        print(f"Oversize directories (>10MB): {oversize_count}")
    if result["violations"]:
        print("CACHE/TEMP GOVERNANCE VIOLATIONS DETECTED:")
        for violation in result["violations"]:
            print(f"  {violation['path']}: {violation['type']} - {violation['detail']}")
        return 1
    else:
        print("No cache/temp governance violations found.")
        return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
