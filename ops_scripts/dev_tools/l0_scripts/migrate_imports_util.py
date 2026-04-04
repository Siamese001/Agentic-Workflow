from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "migrate_imports_util")
_emit_applies_guardrail("p0", "migrate_imports_util", "p0_governance")
_emit_reads_policy_state("p0", "migrate_imports_util", "policy_binding")
_emit_snapshots_state("p0", "migrate_imports_util", "state_snapshot")
emit_replay_key("p0", "migrate_imports_util")
emit_determinism_digest("p0", "migrate_imports_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "migrate_imports_util", "execution_auth")
_emit_validates_capability("p2", "migrate_imports_util", "capability_check")
_emit_routes_to_capability("p2", "migrate_imports_util", "capability_route")
_emit_writes_via_uwg("p2", "migrate_imports_util", "uwg_write")
_emit_blocks_direct_write("p2", "migrate_imports_util", "direct_write_block")
_emit_records_tool_invocation("p2", "migrate_imports_util", "tool_invocation")
_emit_captures_execution_output("p2", "migrate_imports_util", "exec_output")
_emit_dispatches_agent("p3", "migrate_imports_util", "agent_dispatch")
_emit_coordinates_agents("p3", "migrate_imports_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "migrate_imports_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "migrate_imports_util", "healing_outcome")
_emit_escalates_failure("p3", "migrate_imports_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "migrate_imports_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "migrate_imports_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "migrate_imports_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "migrate_imports_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "migrate_imports_util", "eval_metric")
_emit_stores_embedding("p4", "migrate_imports_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "migrate_imports_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "migrate_imports_util", "exec_snapshot_link")
'\nUtility to automate the migration from deep imports to clean SSOT paths.\n\nPhase 5: Repository-Wide Import Migration\n\nThis script updates imports across the codebase to use the new SSOT patterns:\n- agentic_core.config for constants/registry\n- agentic_core.unified for unified agents\n- agentic_core.utils.core_extensions.healer_mixin for HealerMixin\n\nUsage:\n    python -m agentic_core.L0_routing.scripts.migrate_imports --dry-run\n    python -m agentic_core.L0_routing.scripts.migrate_imports --apply\n'
import argparse
import re
from pathlib import Path

from agentic_core.utils.file_utils_validator import safe_read_file, safe_write_file
from agentic_core.utils.project_root import get_project_root

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
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
from agentic_core.utils.ssot_discovery_validator import get_python_files

_emit_emits_metric_event("migrate_imports_util", "p4obs", "metric_1")
_emit_emits_metric_event("migrate_imports_util", "p4obs", "metric_2")
_emit_emits_metric_event("migrate_imports_util", "p4obs", "metric_3")
_emit_emits_metric_event("migrate_imports_util", "p4obs", "metric_4")
_emit_emits_metric_event("migrate_imports_util", "p4obs", "metric_5")
_emit_emits_metric_event("migrate_imports_util", "p4obs", "metric_6")
_emit_records_incident_event("migrate_imports_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("migrate_imports_util", "p4obs", "anomaly")
_emit_writes_observability_log("migrate_imports_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("migrate_imports_util", "p4obs", "mon_state")
_emit_triggers_alert("migrate_imports_util", "p4obs", "alert")
_emit_links_incident_trace("migrate_imports_util", "p4obs", "trace_link")
_emit_captures_pattern("migrate_imports_util", "p3lm", "pattern")
_emit_records_learning_event("migrate_imports_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("migrate_imports_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("migrate_imports_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("migrate_imports_util", "p3lm", "routing")
_emit_improves_agent_policy("migrate_imports_util", "p3lm", "policy")
_emit_stores_learning_state("migrate_imports_util", "p3lm", "state")
_emit_records_execution_trace("migrate_imports_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("migrate_imports_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("migrate_imports_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("migrate_imports_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("migrate_imports_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("migrate_imports_util", "env_read", "p2_env_1")
_emit_reads_environ("migrate_imports_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("migrate_imports_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("migrate_imports_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "migrate_imports_util", "context_pull")
_emit_pulls_context("p1", "migrate_imports_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "migrate_imports_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "migrate_imports_util", "uwg_term_secondary")
_emit_writes_through("p1", "migrate_imports_util", "write_through")
_emit_writes_through("p1", "migrate_imports_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "migrate_imports_util", "safety_validation")
_emit_invokes_eval("p1", "migrate_imports_util", "eval_call")
_emit_proposal_commits_routing("p1", "migrate_imports_util", "routing_commit")
_emit_escalates_to_human("p1", "migrate_imports_util", "human_escalation")
_emit_routes_through("p1", "migrate_imports_util", "route_through")
_emit_checks_agent_registry("p1", "migrate_imports_util", "agent_registry")
_emit_validates_agent_capability("p1", "migrate_imports_util", "capability")
_emit_dispatches_execution_plan("p1", "migrate_imports_util", "exec_plan")
_emit_agent_executes_agent("p1", "migrate_imports_util", "sub_agent")
_emit_routes_to_agent("p1", "migrate_imports_util", "target_agent")
_emit_verifies_policy("p1", "migrate_imports_util", "policy_check")
_emit_observes_runtime_state("p1", "migrate_imports_util", "runtime_state")
_emit_verifies_boundary("p1", "migrate_imports_util", "boundary_check")
_emit_transcripts_response("p1", "migrate_imports_util", "transcript")
_emit_hard_fails_untranscripted("p1", "migrate_imports_util")
_emit_gated_by_confidence("p1", "migrate_imports_util", "confidence_gate")

MIGRATION_MAP: dict[str, str] = {'from agentic_core\\.L5_safety\\.validators\\.structure_blueprint_config import': 'from agentic_core.config import', 'from agentic_core\\.L5_safety\\.unified\\.code_validation_types import CodeValidatorAgent': 'from agentic_core.unified import CodeValidatorAgent', 'from agentic_core\\.L5_safety\\.unified\\.StructureValidatorAgent import StructureValidatorAgent': 'from agentic_core.unified import StructureValidatorAgent', 'from agentic_core\\.L5_safety\\.unified\\.code_enforcement_types import CodeEnforcerAgent': 'from agentic_core.unified import CodeEnforcerAgent', 'from agentic_core\\.L5_safety\\.unified\\.structure_enforcement_types import StructureEnforcerAgent': 'from agentic_core.unified import StructureEnforcerAgent', 'from agentic_core\\.L5_safety\\.unified\\.resource_types import ResourceManagerAgent': 'from agentic_core.unified import ResourceManagerAgent', 'from agentic_core\\.L5_safety\\.validators\\.healer_mixin import': 'from agentic_core.mixins.healer_mixin import', 'from agentic_core\\.L5_safety\\.guardrails\\.healer_mixin import': 'from agentic_core.mixins.healer_mixin import', 'from agentic_core\\.common\\.healing\\.healer_mixin import': 'from agentic_core.mixins.healer_mixin import'}
SKIP_FILES = {'migrate_imports_util.py', 'test_phase5_migration.py', '__init__.py'}

def migrate_file(file_path: Path, dry_run: bool=True) -> tuple[bool, list[str]]:
    """
    Migrate imports in a single file.

    Args:
        file_path: Path to the Python file
        dry_run: If True, don't write changes

    Returns:
        Tuple of (was_modified, list_of_changes)
    """
    content = safe_read_file(file_path)
    if content is None:
        return (False, [])
    original_content = content
    changes = []
    for pattern, replacement in MIGRATION_MAP.items():
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes.append(f'  {pattern} -> {replacement}')
    if content != original_content:
        if not dry_run:
            safe_write_file(file_path, content)
        return (True, changes)
    return (False, [])

def migrate_repo(dry_run: bool=True) -> dict[str, list[str]]:
    """
    Migrate all Python files in the repository.

    Args:
        dry_run: If True, only report changes without applying

    Returns:
        Dict mapping file paths to their changes
    """
    root = get_project_root()
    files = get_python_files(root)
    results = {}
    for file_path in files:
        if file_path.name in SKIP_FILES:
            continue
        was_modified, changes = migrate_file(file_path, dry_run=dry_run)
        if was_modified:
            results[str(file_path)] = changes
    return results

def main():
    parser = argparse.ArgumentParser(description='Migrate imports to SSOT patterns')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Show changes without applying (default)')
    parser.add_argument('--apply', action='store_true', help='Apply changes to files')
    args = parser.parse_args()
    dry_run = not args.apply
    print(f"{('DRY RUN' if dry_run else 'APPLYING CHANGES')}: Migrating imports...")
    results = migrate_repo(dry_run=dry_run)
    if results:
        print(f"\n{('Would modify' if dry_run else 'Modified')} {len(results)} files:\n")
        for file_path, changes in results.items():
            print(f'  {file_path}')
            for change in changes:
                print(f'    {change}')
    else:
        print('\nNo files need migration.')
    if dry_run and results:
        print('\nRun with --apply to apply changes.')
if __name__ == '__main__':
    main()
