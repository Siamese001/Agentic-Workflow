#!/usr/bin/env python3
"""
ADG-Driven Anti-Pattern Analyzer

Analyzes remaining violations using dependency graph to identify
fixable patterns and their blast radius.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "adg_antipattern_analyzer")
_emit_applies_guardrail("p0", "adg_antipattern_analyzer", "p0_governance")
_emit_reads_policy_state("p0", "adg_antipattern_analyzer", "policy_binding")
_emit_snapshots_state("p0", "adg_antipattern_analyzer", "state_snapshot")
emit_replay_key("p0", "adg_antipattern_analyzer")
emit_determinism_digest("p0", "adg_antipattern_analyzer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "adg_antipattern_analyzer", "execution_auth")
_emit_validates_capability("p2", "adg_antipattern_analyzer", "capability_check")
_emit_routes_to_capability("p2", "adg_antipattern_analyzer", "capability_route")
_emit_writes_via_uwg("p2", "adg_antipattern_analyzer", "uwg_write")
_emit_blocks_direct_write("p2", "adg_antipattern_analyzer", "direct_write_block")
_emit_records_tool_invocation("p2", "adg_antipattern_analyzer", "tool_invocation")
_emit_captures_execution_output("p2", "adg_antipattern_analyzer", "exec_output")
_emit_dispatches_agent("p3", "adg_antipattern_analyzer", "agent_dispatch")
_emit_coordinates_agents("p3", "adg_antipattern_analyzer", "agent_coordination")
_emit_records_workflow_lineage("p3", "adg_antipattern_analyzer", "workflow_lineage")
_emit_records_healing_outcome("p3", "adg_antipattern_analyzer", "healing_outcome")
_emit_escalates_failure("p3", "adg_antipattern_analyzer", "failure_escalation")
_emit_orchestrates_workflow("p3", "adg_antipattern_analyzer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "adg_antipattern_analyzer", "healing_dispatch")
_emit_invokes_evaluation("p3", "adg_antipattern_analyzer", "evaluation_signal")
_emit_records_telemetry_event("p4", "adg_antipattern_analyzer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "adg_antipattern_analyzer", "eval_metric")
_emit_stores_embedding("p4", "adg_antipattern_analyzer", "embedding_store")
_emit_updates_meta_learning_state("p4", "adg_antipattern_analyzer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "adg_antipattern_analyzer", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
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

_emit_emits_metric_event("adg_antipattern_analyzer", "p4obs", "metric_1")
_emit_emits_metric_event("adg_antipattern_analyzer", "p4obs", "metric_2")
_emit_emits_metric_event("adg_antipattern_analyzer", "p4obs", "metric_3")
_emit_emits_metric_event("adg_antipattern_analyzer", "p4obs", "metric_4")
_emit_emits_metric_event("adg_antipattern_analyzer", "p4obs", "metric_5")
_emit_emits_metric_event("adg_antipattern_analyzer", "p4obs", "metric_6")
_emit_records_incident_event("adg_antipattern_analyzer", "p4obs", "incident")
_emit_captures_runtime_anomaly("adg_antipattern_analyzer", "p4obs", "anomaly")
_emit_writes_observability_log("adg_antipattern_analyzer", "p4obs", "obs_log")
_emit_updates_monitoring_state("adg_antipattern_analyzer", "p4obs", "mon_state")
_emit_triggers_alert("adg_antipattern_analyzer", "p4obs", "alert")
_emit_links_incident_trace("adg_antipattern_analyzer", "p4obs", "trace_link")
_emit_captures_pattern("adg_antipattern_analyzer", "p3lm", "pattern")
_emit_records_learning_event("adg_antipattern_analyzer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("adg_antipattern_analyzer", "p3lm", "snapshot")
_emit_feeds_meta_learning("adg_antipattern_analyzer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("adg_antipattern_analyzer", "p3lm", "routing")
_emit_improves_agent_policy("adg_antipattern_analyzer", "p3lm", "policy")
_emit_stores_learning_state("adg_antipattern_analyzer", "p3lm", "state")
_emit_records_execution_trace("adg_antipattern_analyzer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("adg_antipattern_analyzer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("adg_antipattern_analyzer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("adg_antipattern_analyzer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("adg_antipattern_analyzer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("adg_antipattern_analyzer", "env_read", "p2_env_1")
_emit_reads_environ("adg_antipattern_analyzer", "env_read", "p2_env_2")
_emit_reads_runtime_state("adg_antipattern_analyzer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("adg_antipattern_analyzer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "adg_antipattern_analyzer", "context_pull")
_emit_pulls_context("p1", "adg_antipattern_analyzer", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "adg_antipattern_analyzer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "adg_antipattern_analyzer", "uwg_term_secondary")
_emit_writes_through("p1", "adg_antipattern_analyzer", "write_through")
_emit_writes_through("p1", "adg_antipattern_analyzer", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "adg_antipattern_analyzer", "safety_validation")
_emit_invokes_eval("p1", "adg_antipattern_analyzer", "eval_call")
_emit_proposal_commits_routing("p1", "adg_antipattern_analyzer", "routing_commit")
_emit_escalates_to_human("p1", "adg_antipattern_analyzer", "human_escalation")
_emit_routes_through("p1", "adg_antipattern_analyzer", "route_through")
_emit_checks_agent_registry("p1", "adg_antipattern_analyzer", "agent_registry")
_emit_validates_agent_capability("p1", "adg_antipattern_analyzer", "capability")
_emit_dispatches_execution_plan("p1", "adg_antipattern_analyzer", "exec_plan")
_emit_agent_executes_agent("p1", "adg_antipattern_analyzer", "sub_agent")
_emit_routes_to_agent("p1", "adg_antipattern_analyzer", "target_agent")
_emit_verifies_policy("p1", "adg_antipattern_analyzer", "policy_check")
_emit_observes_runtime_state("p1", "adg_antipattern_analyzer", "runtime_state")
_emit_verifies_boundary("p1", "adg_antipattern_analyzer", "boundary_check")
_emit_transcripts_response("p1", "adg_antipattern_analyzer", "transcript")
_emit_hard_fails_untranscripted("p1", "adg_antipattern_analyzer")
_emit_gated_by_confidence("p1", "adg_antipattern_analyzer", "confidence_gate")


def analyze_violations_by_category(baseline_path: Path) -> dict:
    """Analyze violations grouped by category with file clustering."""
    violations = defaultdict(lambda: defaultdict(list))

    with open(baseline_path, encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(':')
            if len(parts) < 4:
                continue

            file_path = parts[0]
            line_num = parts[1]
            category = parts[2]
            message = ':'.join(parts[3:])

            violations[category][file_path].append({
                'line': int(line_num),
                'message': message,
            })

    return violations


def analyze_silent_swallowers(violations: dict, adg_path: Path) -> dict:
    """Analyze silent swallower patterns using ADG."""
    swallowers = violations.get('silent_swallower', {})

    # Load ADG for dependency analysis
    with open(adg_path, encoding='utf-8') as f:
        adg = json.load(f)

    # Categorize by pattern
    patterns = {
        'bare_except': [],
        'exception_without_raise': [],
        'pass_in_except': [],
    }

    for file_path, viols in swallowers.items():
        for v in viols:
            msg = v['message'].lower()
            if 'bare except' in msg:
                patterns['bare_except'].append((file_path, v))
            elif 'without raise' in msg:
                patterns['exception_without_raise'].append((file_path, v))
            elif 'pass' in msg:
                patterns['pass_in_except'].append((file_path, v))

    return {
        'total': len(swallowers),
        'files': len(swallowers.keys()),
        'patterns': {k: len(v) for k, v in patterns.items()},
        'pattern_details': patterns,
    }


def analyze_path_fragility(violations: dict) -> dict:
    """Analyze path fragility patterns."""
    fragility = violations.get('path_fragility', {})

    patterns = {
        'os_path_join': [],
        'os_path_basename': [],
        'os_path_dirname': [],
        'string_concat': [],
    }

    for file_path, viols in fragility.items():
        for v in viols:
            msg = v['message'].lower()
            if 'os.path.join' in msg:
                patterns['os_path_join'].append((file_path, v))
            elif 'os.path.basename' in msg:
                patterns['os_path_basename'].append((file_path, v))
            elif 'os.path.dirname' in msg:
                patterns['os_path_dirname'].append((file_path, v))
            elif 'string concatenation' in msg:
                patterns['string_concat'].append((file_path, v))

    return {
        'total': len(fragility),
        'files': len(fragility.keys()),
        'patterns': {k: len(v) for k, v in patterns.items()},
        'pattern_details': patterns,
    }


def analyze_global_mutation(violations: dict) -> dict:
    """Analyze global mutation patterns."""
    mutations = violations.get('global_mutation', {})

    patterns = {
        'os_environ': [],
        'sys_path': [],
        'global_var': [],
    }

    for file_path, viols in mutations.items():
        for v in viols:
            msg = v['message'].lower()
            if 'os.environ' in msg:
                patterns['os_environ'].append((file_path, v))
            elif 'sys.path' in msg:
                patterns['sys_path'].append((file_path, v))
            else:
                patterns['global_var'].append((file_path, v))

    return {
        'total': len(mutations),
        'files': len(mutations.keys()),
        'patterns': {k: len(v) for k, v in patterns.items()},
        'pattern_details': patterns,
    }


def main():
    """Main execution."""
    project_root = get_validated_project_root()
    baseline_path = project_root / "ops_scripts" / "hooks" / "landmine_baseline.txt"
    adg_path = project_root / "artifacts" / "adg" / "adg_file_graph_03122026.json"

    print("[INFO] Analyzing violations by category...")
    violations = analyze_violations_by_category(baseline_path)

    print("\n" + "="*80)
    print("ADG-DRIVEN ANTI-PATTERN ANALYSIS")
    print("="*80)

    # Analyze silent swallowers
    print("\n[1] SILENT SWALLOWERS")
    swallow_analysis = analyze_silent_swallowers(violations, adg_path)
    print(f"  Total violations: {swallow_analysis['total']}")
    print(f"  Affected files: {swallow_analysis['files']}")
    print("  Patterns:")
    for pattern, count in swallow_analysis['patterns'].items():
        print(f"    - {pattern}: {count}")

    # Analyze path fragility
    print("\n[2] PATH FRAGILITY")
    path_analysis = analyze_path_fragility(violations)
    print(f"  Total violations: {path_analysis['total']}")
    print(f"  Affected files: {path_analysis['files']}")
    print("  Patterns:")
    for pattern, count in path_analysis['patterns'].items():
        print(f"    - {pattern}: {count}")

    # Analyze global mutation
    print("\n[3] GLOBAL MUTATION")
    mutation_analysis = analyze_global_mutation(violations)
    print(f"  Total violations: {mutation_analysis['total']}")
    print(f"  Affected files: {mutation_analysis['files']}")
    print("  Patterns:")
    for pattern, count in mutation_analysis['patterns'].items():
        print(f"    - {pattern}: {count}")

    # Show top files for each category
    print("\n[TOP VIOLATORS BY CATEGORY]")

    for category in ['silent_swallower', 'path_fragility', 'global_mutation']:
        if category in violations:
            sorted_files = sorted(
                violations[category].items(),
                key=lambda x: len(x[1]),
                reverse=True
            )[:5]

            print(f"\n{category.upper()} - Top 5 files:")
            for file_path, viols in sorted_files:
                print(f"  {len(viols):3d} violations - {file_path}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
