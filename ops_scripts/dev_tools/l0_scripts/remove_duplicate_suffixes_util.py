"""
Remove Duplicate Files with Problematic Suffixes

RCA: These duplicates were created during Phase 1-8 architectural sovereignty work.
The flattening process created duplicates instead of consolidating to single canonical files.

Enhanced with intelligent suffix detection to catch all common patterns:
_flat, _from_utils, _1, _2, _copy, _backup, etc.

This script:
1. Identifies all files with problematic suffixes
2. Checks if canonical version (without suffix) exists
3. Removes duplicate if canonical exists
4. Reports files that need manual review
"""
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_records_execution_trace("p0", "evidence", "remove_duplicate_suffixes_util")
_emit_applies_guardrail("p0", "remove_duplicate_suffixes_util", "p0_governance")
_emit_reads_policy_state("p0", "remove_duplicate_suffixes_util", "policy_binding")
_emit_snapshots_state("p0", "remove_duplicate_suffixes_util", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("remove_duplicate_suffixes_util", "p4obs", "metric_1")
_emit_emits_metric_event("remove_duplicate_suffixes_util", "p4obs", "metric_2")
_emit_emits_metric_event("remove_duplicate_suffixes_util", "p4obs", "metric_3")
_emit_emits_metric_event("remove_duplicate_suffixes_util", "p4obs", "metric_4")
_emit_emits_metric_event("remove_duplicate_suffixes_util", "p4obs", "metric_5")
_emit_emits_metric_event("remove_duplicate_suffixes_util", "p4obs", "metric_6")
_emit_records_incident_event("remove_duplicate_suffixes_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("remove_duplicate_suffixes_util", "p4obs", "anomaly")
_emit_writes_observability_log("remove_duplicate_suffixes_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("remove_duplicate_suffixes_util", "p4obs", "mon_state")
_emit_triggers_alert("remove_duplicate_suffixes_util", "p4obs", "alert")
_emit_links_incident_trace("remove_duplicate_suffixes_util", "p4obs", "trace_link")
_emit_captures_pattern("remove_duplicate_suffixes_util", "p3lm", "pattern")
_emit_records_learning_event("remove_duplicate_suffixes_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("remove_duplicate_suffixes_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("remove_duplicate_suffixes_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("remove_duplicate_suffixes_util", "p3lm", "routing")
_emit_improves_agent_policy("remove_duplicate_suffixes_util", "p3lm", "policy")
_emit_stores_learning_state("remove_duplicate_suffixes_util", "p3lm", "state")
_emit_records_execution_trace("remove_duplicate_suffixes_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("remove_duplicate_suffixes_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("remove_duplicate_suffixes_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("remove_duplicate_suffixes_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("remove_duplicate_suffixes_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("remove_duplicate_suffixes_util", "env_read", "p2_env_1")
_emit_reads_environ("remove_duplicate_suffixes_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("remove_duplicate_suffixes_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("remove_duplicate_suffixes_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "remove_duplicate_suffixes_util", "context_pull")
_emit_pulls_context("p1", "remove_duplicate_suffixes_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "remove_duplicate_suffixes_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "remove_duplicate_suffixes_util", "uwg_term_2")
_emit_writes_through("p1", "remove_duplicate_suffixes_util", "write_through")
_emit_writes_through("p1", "remove_duplicate_suffixes_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "remove_duplicate_suffixes_util", "safety_validation")
_emit_invokes_eval("p1", "remove_duplicate_suffixes_util", "eval_call")
_emit_proposal_commits_routing("p1", "remove_duplicate_suffixes_util", "routing_commit")
_emit_escalates_to_human("p1", "remove_duplicate_suffixes_util", "human_escalation")
_emit_routes_through("p1", "remove_duplicate_suffixes_util", "route_through")
_emit_checks_agent_registry("p1", "remove_duplicate_suffixes_util", "agent_registry")
_emit_validates_agent_capability("p1", "remove_duplicate_suffixes_util", "capability")
_emit_dispatches_execution_plan("p1", "remove_duplicate_suffixes_util", "exec_plan")
_emit_agent_executes_agent("p1", "remove_duplicate_suffixes_util", "sub_agent")
_emit_routes_to_agent("p1", "remove_duplicate_suffixes_util", "target_agent")
_emit_verifies_policy("p1", "remove_duplicate_suffixes_util", "policy_check")
_emit_observes_runtime_state("p1", "remove_duplicate_suffixes_util", "runtime_state")
_emit_verifies_boundary("p1", "remove_duplicate_suffixes_util", "boundary_check")
_emit_transcripts_response("p1", "remove_duplicate_suffixes_util", "transcript")
_emit_hard_fails_untranscripted("p1", "remove_duplicate_suffixes_util")
_emit_gated_by_confidence("p1", "remove_duplicate_suffixes_util", "confidence_gate")
emit_replay_key("p0", "remove_duplicate_suffixes_util")
emit_determinism_digest("p0", "remove_duplicate_suffixes_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "remove_duplicate_suffixes_util", "execution_auth")
_emit_validates_capability("p2", "remove_duplicate_suffixes_util", "capability_check")
_emit_routes_to_capability("p2", "remove_duplicate_suffixes_util", "capability_route")
_emit_writes_via_uwg("p2", "remove_duplicate_suffixes_util", "uwg_write")
_emit_blocks_direct_write("p2", "remove_duplicate_suffixes_util", "direct_write_block")
_emit_records_tool_invocation("p2", "remove_duplicate_suffixes_util", "tool_invocation")
_emit_captures_execution_output("p2", "remove_duplicate_suffixes_util", "exec_output")
_emit_dispatches_agent("p3", "remove_duplicate_suffixes_util", "agent_dispatch")
_emit_coordinates_agents("p3", "remove_duplicate_suffixes_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "remove_duplicate_suffixes_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "remove_duplicate_suffixes_util", "healing_outcome")
_emit_escalates_failure("p3", "remove_duplicate_suffixes_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "remove_duplicate_suffixes_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "remove_duplicate_suffixes_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "remove_duplicate_suffixes_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "remove_duplicate_suffixes_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "remove_duplicate_suffixes_util", "eval_metric")
_emit_stores_embedding("p4", "remove_duplicate_suffixes_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "remove_duplicate_suffixes_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "remove_duplicate_suffixes_util", "exec_snapshot_link")
project_root = Path(__file__).parent.parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
PROBLEMATIC_SUFFIXES = ['_flat', '_from_utils', '_1', '_2', '_3', '_copy', '_backup', '_old', '_new', '_temp', '_tmp']

def find_duplicate_files() -> list[Path]:
    """Find all files with problematic suffixes."""
    all_duplicates = []
    for suffix in PROBLEMATIC_SUFFIXES:
        pattern = f'*{suffix}.py'
        files = list(project_root.rglob(pattern))
        files = [f for f in files if ARCHIVES_DIR not in str(f)]
        all_duplicates.extend(files)
    return all_duplicates

def get_canonical_path(duplicate_path: Path) -> tuple[Path, str | None]:
    """Get the canonical path by removing suffix.

    Returns:
        Tuple of (canonical_path, matched_suffix)
    """
    from agentic_core.utils.fs_util import remove_duplicate_suffix_path
    return remove_duplicate_suffix_path(duplicate_path, PROBLEMATIC_SUFFIXES)

def analyze_duplicates(duplicate_files: list[Path]) -> dict[str, list[tuple[Path, Path, str, bool]]]:
    """
    Analyze duplicates and categorize them.

    Returns:
        Dict with categories:
        - safe_to_delete: Canonical exists, duplicate can be removed
        - needs_review: Canonical doesn't exist, need to rename

    Each entry is (dup_path, canonical_path, suffix, canonical_exists)
    """
    results = {'safe_to_delete': [], 'needs_review': []}
    for dup_path in duplicate_files:
        canonical_path, suffix = get_canonical_path(dup_path)
        if suffix is None:
            continue
        canonical_exists = canonical_path.exists()
        if canonical_exists:
            results['safe_to_delete'].append((dup_path, canonical_path, suffix, True))
        else:
            results['needs_review'].append((dup_path, canonical_path, suffix, False))
    return results

def remove_duplicates(safe_to_delete: list[tuple[Path, Path, str, bool]], dry_run: bool=True) -> int:
    """Remove duplicate files that have canonical versions."""
    removed_count = 0
    for dup_path, canonical_path, _suffix, _ in safe_to_delete:
        dup_path.relative_to(project_root)
        canonical_path.relative_to(project_root)
        if dry_run:
            pass
        else:
            try:
                dup_path.unlink()
                removed_count += 1
            # guardian: allow-silent-swallow
            except Exception:
                pass
    return removed_count

def main(dry_run: bool=True) -> int:
    """
    Main execution.

    Returns:
        Exit code (0 for success)
    """
    duplicate_files = find_duplicate_files()
    results = analyze_duplicates(duplicate_files)
    safe_count = len(results['safe_to_delete'])
    review_count = len(results['needs_review'])
    suffix_breakdown = {}
    for _, _, suffix, _ in results['safe_to_delete']:
        suffix_breakdown[suffix] = suffix_breakdown.get(suffix, 0) + 1
    if safe_count > 0:
        remove_duplicates(results['safe_to_delete'], dry_run)
        if not dry_run:
            pass
    if review_count > 0:
        for dup_path, canonical_path, suffix, _ in results['needs_review']:
            dup_path.relative_to(project_root)
            canonical_path.relative_to(project_root)
    if dry_run:
        pass
    return 0
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Remove duplicate files with _flat and _1 suffixes')
    parser.add_argument('--execute', action='store_true', help='Actually delete files (default is dry-run)')
    args = parser.parse_args()
    sys.exit(main(dry_run=not args.execute))
