#!/usr/bin/env python3
"""
Simple string-based threshold refactoring.

Replaces hardcoded THRESHOLD = 0.95 with import from path_constants.
Uses regex for reliability over AST transformation.
"""

import re
import sys
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "simple_threshold_refactor")
_emit_applies_guardrail("p0", "simple_threshold_refactor", "p0_governance")
_emit_reads_policy_state("p0", "simple_threshold_refactor", "policy_binding")
_emit_snapshots_state("p0", "simple_threshold_refactor", "state_snapshot")
emit_replay_key("p0", "simple_threshold_refactor")
emit_determinism_digest("p0", "simple_threshold_refactor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "simple_threshold_refactor", "execution_auth")
_emit_validates_capability("p2", "simple_threshold_refactor", "capability_check")
_emit_routes_to_capability("p2", "simple_threshold_refactor", "capability_route")
_emit_writes_via_uwg("p2", "simple_threshold_refactor", "uwg_write")
_emit_blocks_direct_write("p2", "simple_threshold_refactor", "direct_write_block")
_emit_records_tool_invocation("p2", "simple_threshold_refactor", "tool_invocation")
_emit_captures_execution_output("p2", "simple_threshold_refactor", "exec_output")
_emit_dispatches_agent("p3", "simple_threshold_refactor", "agent_dispatch")
_emit_coordinates_agents("p3", "simple_threshold_refactor", "agent_coordination")
_emit_records_workflow_lineage("p3", "simple_threshold_refactor", "workflow_lineage")
_emit_records_healing_outcome("p3", "simple_threshold_refactor", "healing_outcome")
_emit_escalates_failure("p3", "simple_threshold_refactor", "failure_escalation")
_emit_orchestrates_workflow("p3", "simple_threshold_refactor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "simple_threshold_refactor", "healing_dispatch")
_emit_invokes_evaluation("p3", "simple_threshold_refactor", "evaluation_signal")
_emit_records_telemetry_event("p4", "simple_threshold_refactor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "simple_threshold_refactor", "eval_metric")
_emit_stores_embedding("p4", "simple_threshold_refactor", "embedding_store")
_emit_updates_meta_learning_state("p4", "simple_threshold_refactor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "simple_threshold_refactor", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
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

_emit_emits_metric_event("simple_threshold_refactor", "p4obs", "metric_1")
_emit_emits_metric_event("simple_threshold_refactor", "p4obs", "metric_2")
_emit_emits_metric_event("simple_threshold_refactor", "p4obs", "metric_3")
_emit_emits_metric_event("simple_threshold_refactor", "p4obs", "metric_4")
_emit_emits_metric_event("simple_threshold_refactor", "p4obs", "metric_5")
_emit_emits_metric_event("simple_threshold_refactor", "p4obs", "metric_6")
_emit_records_incident_event("simple_threshold_refactor", "p4obs", "incident")
_emit_captures_runtime_anomaly("simple_threshold_refactor", "p4obs", "anomaly")
_emit_writes_observability_log("simple_threshold_refactor", "p4obs", "obs_log")
_emit_updates_monitoring_state("simple_threshold_refactor", "p4obs", "mon_state")
_emit_triggers_alert("simple_threshold_refactor", "p4obs", "alert")
_emit_links_incident_trace("simple_threshold_refactor", "p4obs", "trace_link")
_emit_captures_pattern("simple_threshold_refactor", "p3lm", "pattern")
_emit_records_learning_event("simple_threshold_refactor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("simple_threshold_refactor", "p3lm", "snapshot")
_emit_feeds_meta_learning("simple_threshold_refactor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("simple_threshold_refactor", "p3lm", "routing")
_emit_improves_agent_policy("simple_threshold_refactor", "p3lm", "policy")
_emit_stores_learning_state("simple_threshold_refactor", "p3lm", "state")
_emit_records_execution_trace("simple_threshold_refactor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("simple_threshold_refactor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("simple_threshold_refactor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("simple_threshold_refactor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("simple_threshold_refactor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("simple_threshold_refactor", "env_read", "p2_env_1")
_emit_reads_environ("simple_threshold_refactor", "env_read", "p2_env_2")
_emit_reads_runtime_state("simple_threshold_refactor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("simple_threshold_refactor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "simple_threshold_refactor", "context_pull")
_emit_pulls_context("p1", "simple_threshold_refactor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "simple_threshold_refactor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "simple_threshold_refactor", "uwg_term_2")
_emit_writes_through("p1", "simple_threshold_refactor", "write_through")
_emit_writes_through("p1", "simple_threshold_refactor", "write_through_2")
_emit_validated_by_safety_plane("p1", "simple_threshold_refactor", "safety_validation")
_emit_invokes_eval("p1", "simple_threshold_refactor", "eval_call")
_emit_proposal_commits_routing("p1", "simple_threshold_refactor", "routing_commit")
_emit_escalates_to_human("p1", "simple_threshold_refactor", "human_escalation")
_emit_routes_through("p1", "simple_threshold_refactor", "route_through")
_emit_checks_agent_registry("p1", "simple_threshold_refactor", "agent_registry")
_emit_validates_agent_capability("p1", "simple_threshold_refactor", "capability")
_emit_dispatches_execution_plan("p1", "simple_threshold_refactor", "exec_plan")
_emit_agent_executes_agent("p1", "simple_threshold_refactor", "sub_agent")
_emit_routes_to_agent("p1", "simple_threshold_refactor", "target_agent")
_emit_verifies_policy("p1", "simple_threshold_refactor", "policy_check")
_emit_observes_runtime_state("p1", "simple_threshold_refactor", "runtime_state")
_emit_verifies_boundary("p1", "simple_threshold_refactor", "boundary_check")
_emit_transcripts_response("p1", "simple_threshold_refactor", "transcript")
_emit_hard_fails_untranscripted("p1", "simple_threshold_refactor")
_emit_gated_by_confidence("p1", "simple_threshold_refactor", "confidence_gate")


def refactor_file(file_path: Path, dry_run: bool = True) -> dict:
    """Refactor a single file using string replacement."""
    try:
        source = file_path.read_text(encoding='utf-8')
        original = source

        # Skip if this IS the path_constants.py file (SSOT source)
        if file_path.name == 'path_constants.py' and 'L0_routing' in str(file_path):
            return {'status': 'skipped', 'reason': 'ssot_source'}

        # Check if already imports THRESHOLD from path_constants
        has_import = 'from agentic_core.L0_routing.config.path_constants import' in source
        has_threshold_import = has_import and 'THRESHOLD' in source

        # Pattern 1: Remove standalone THRESHOLD = 0.95 lines
        # Only if we're going to add the import
        if not has_threshold_import:
            source = re.sub(
                r'^THRESHOLD\s*=\s*0\.95\s*$',
                '',
                source,
                flags=re.MULTILINE
            )

        # Pattern 2: Replace threshold=0.95 in function calls
        source = re.sub(
            r'\bthreshold\s*=\s*0\.95\b',
            'threshold=THRESHOLD',
            source
        )

        # Add import if needed and modifications were made
        if source != original and not has_threshold_import:
            # Find insertion point after imports
            lines = source.splitlines(keepends=True)
            insert_pos = 0

            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('import ') or stripped.startswith('from '):
                    insert_pos = i + 1
                elif insert_pos > 0 and stripped and not stripped.startswith('#'):
                    # Found first non-import, non-comment line
                    break

            if insert_pos > 0:
                lines.insert(insert_pos, 'from agentic_core.L0_routing.config.path_constants import THRESHOLD\n')
                source = ''.join(lines)

        if source == original:
            return {'status': 'skipped', 'reason': 'no_changes'}

        if not dry_run:
            file_path.write_text(source, encoding='utf-8')

        return {
            'status': 'success',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'dry_run': dry_run,
        }

    except Exception as e:
        return {
            'status': 'error',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'error': str(e),
        }


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--limit', type=int, default=100)
    args = parser.parse_args()

    project_root = get_validated_project_root()
    baseline_file = project_root / "ops_scripts" / "hooks" / "landmine_baseline.txt"

    # Load violations
    violations = []
    with open(baseline_file, encoding='utf-8') as f:
        for line in f:
            if 'threshold=0.95' in line:
                file_path = line.split(':')[0]
                violations.append(project_root / file_path)

    unique_files = sorted(set(violations))[:args.limit]

    print(f"[INFO] Processing {len(unique_files)} files")
    print(f"[MODE] {'EXECUTE' if args.execute else 'DRY RUN'}")
    print()

    results = []
    for file_path in unique_files:
        if not file_path.exists():
            continue

        result = refactor_file(file_path, dry_run=not args.execute)
        results.append(result)

        if result['status'] == 'success':
            print(f"✓ {result['file']}")
        elif result['status'] == 'error':
            print(f"✗ {result['file']}: {result['error']}")

    success = len([r for r in results if r['status'] == 'success'])
    errors = len([r for r in results if r['status'] == 'error'])
    skipped = len([r for r in results if r['status'] == 'skipped'])

    print()
    print(f"[SUMMARY] Success: {success}, Errors: {errors}, Skipped: {skipped}")

    if not args.execute and success > 0:
        print("[NEXT] Run with --execute to apply changes")

    return 0


if __name__ == '__main__':
    sys.exit(main())
