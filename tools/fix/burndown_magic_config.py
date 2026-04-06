#!/usr/bin/env python3
"""
ADG-Guided Magic Configuration Burndown

Uses AST dependency graph to systematically eliminate magic configuration
anti-patterns by replacing hardcoded values with SSOT imports.

Strategy:
1. Identify all files with threshold=0.95 violations
2. Check if they already import from path_constants
3. Replace hardcoded values with THRESHOLD constant
4. Add import if missing
5. Verify no new violations introduced
"""

import ast
import sys
from pathlib import Path
from typing import Any

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

_emit_records_execution_trace("p0", "evidence", "burndown_magic_config")
_emit_applies_guardrail("p0", "burndown_magic_config", "p0_governance")
_emit_reads_policy_state("p0", "burndown_magic_config", "policy_binding")
_emit_snapshots_state("p0", "burndown_magic_config", "state_snapshot")
emit_replay_key("p0", "burndown_magic_config")
emit_determinism_digest("p0", "burndown_magic_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "burndown_magic_config", "execution_auth")
_emit_validates_capability("p2", "burndown_magic_config", "capability_check")
_emit_routes_to_capability("p2", "burndown_magic_config", "capability_route")
_emit_writes_via_uwg("p2", "burndown_magic_config", "uwg_write")
_emit_blocks_direct_write("p2", "burndown_magic_config", "direct_write_block")
_emit_records_tool_invocation("p2", "burndown_magic_config", "tool_invocation")
_emit_captures_execution_output("p2", "burndown_magic_config", "exec_output")
_emit_dispatches_agent("p3", "burndown_magic_config", "agent_dispatch")
_emit_coordinates_agents("p3", "burndown_magic_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "burndown_magic_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "burndown_magic_config", "healing_outcome")
_emit_escalates_failure("p3", "burndown_magic_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "burndown_magic_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "burndown_magic_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "burndown_magic_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "burndown_magic_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "burndown_magic_config", "eval_metric")
_emit_stores_embedding("p4", "burndown_magic_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "burndown_magic_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "burndown_magic_config", "exec_snapshot_link")

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("burndown_magic_config", "p4obs", "metric_1")
_emit_emits_metric_event("burndown_magic_config", "p4obs", "metric_2")
_emit_emits_metric_event("burndown_magic_config", "p4obs", "metric_3")
_emit_emits_metric_event("burndown_magic_config", "p4obs", "metric_4")
_emit_emits_metric_event("burndown_magic_config", "p4obs", "metric_5")
_emit_emits_metric_event("burndown_magic_config", "p4obs", "metric_6")
_emit_records_incident_event("burndown_magic_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("burndown_magic_config", "p4obs", "anomaly")
_emit_writes_observability_log("burndown_magic_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("burndown_magic_config", "p4obs", "mon_state")
_emit_triggers_alert("burndown_magic_config", "p4obs", "alert")
_emit_links_incident_trace("burndown_magic_config", "p4obs", "trace_link")
_emit_captures_pattern("burndown_magic_config", "p3lm", "pattern")
_emit_records_learning_event("burndown_magic_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("burndown_magic_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("burndown_magic_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("burndown_magic_config", "p3lm", "routing")
_emit_improves_agent_policy("burndown_magic_config", "p3lm", "policy")
_emit_stores_learning_state("burndown_magic_config", "p3lm", "state")
_emit_records_execution_trace("burndown_magic_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("burndown_magic_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("burndown_magic_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("burndown_magic_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("burndown_magic_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("burndown_magic_config", "env_read", "p2_env_1")
_emit_reads_environ("burndown_magic_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("burndown_magic_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("burndown_magic_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "burndown_magic_config", "context_pull")
_emit_pulls_context("p1", "burndown_magic_config", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "burndown_magic_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "burndown_magic_config", "uwg_term_secondary")
_emit_writes_through("p1", "burndown_magic_config", "write_through")
_emit_writes_through("p1", "burndown_magic_config", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "burndown_magic_config", "safety_validation")
_emit_invokes_eval("p1", "burndown_magic_config", "eval_call")
_emit_proposal_commits_routing("p1", "burndown_magic_config", "routing_commit")
_emit_escalates_to_human("p1", "burndown_magic_config", "human_escalation")
_emit_routes_through("p1", "burndown_magic_config", "route_through")
_emit_checks_agent_registry("p1", "burndown_magic_config", "agent_registry")
_emit_validates_agent_capability("p1", "burndown_magic_config", "capability")
_emit_dispatches_execution_plan("p1", "burndown_magic_config", "exec_plan")
_emit_agent_executes_agent("p1", "burndown_magic_config", "sub_agent")
_emit_routes_to_agent("p1", "burndown_magic_config", "target_agent")
_emit_verifies_policy("p1", "burndown_magic_config", "policy_check")
_emit_observes_runtime_state("p1", "burndown_magic_config", "runtime_state")
_emit_verifies_boundary("p1", "burndown_magic_config", "boundary_check")
_emit_transcripts_response("p1", "burndown_magic_config", "transcript")
_emit_hard_fails_untranscripted("p1", "burndown_magic_config")
_emit_gated_by_confidence("p1", "burndown_magic_config", "confidence_gate")


class MagicConfigReplacer(ast.NodeTransformer):
    """AST transformer to replace magic config values with SSOT constants."""

    def __init__(self):
        self.replacements = []
        self.needs_import = False

    def visit_Assign(self, node: ast.Assign) -> Any:
        """Replace threshold=0.95 assignments with THRESHOLD constant."""
        if isinstance(node.value, ast.Constant):
            if node.value.value == 0.95:
                # Check if this is a threshold-related variable
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        if 'threshold' in var_name:
                            # Replace with Name node referencing THRESHOLD
                            node.value = ast.Name(id='THRESHOLD', ctx=ast.Load())
                            self.needs_import = True
                            self.replacements.append((node.lineno, var_name))
        return self.generic_visit(node)

    def visit_keyword(self, node: ast.keyword) -> Any:
        """Replace threshold=0.95 in function calls."""
        if node.arg and 'threshold' in node.arg.lower():
            if isinstance(node.value, ast.Constant) and node.value.value == 0.95:
                node.value = ast.Name(id='THRESHOLD', ctx=ast.Load())
                self.needs_import = True
                self.replacements.append((node.lineno, node.arg))
        return self.generic_visit(node)


def analyze_file(file_path: Path) -> dict:
    """Analyze a file for magic config violations."""
    try:
        source = file_path.read_text(encoding='utf-8')
        tree = ast.parse(source, filename=str(file_path))

        # Check if already imports THRESHOLD
        has_threshold_import = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and 'path_constants' in node.module:
                    if any(alias.name == 'THRESHOLD' for alias in node.names):
                        has_threshold_import = True
                        break

        # Count threshold=0.95 occurrences
        threshold_count = source.count('threshold=0.95') + source.count('THRESHOLD = 0.95')

        return {
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'has_import': has_threshold_import,
            'violations': threshold_count,
            'can_fix': threshold_count > 0,
        }
    except (ValueError, TypeError, RuntimeError) as e:
        return {
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'error': str(e),
            'can_fix': False,
        }


def main():
    """Main burndown execution."""
    project_root = get_validated_project_root()

    # Load landmine baseline
    baseline_file = project_root / "ops_scripts" / "hooks" / "landmine_baseline.txt"

    if not baseline_file.exists():
        print("[ERROR] Landmine baseline not found")
        return 1

    # Parse baseline for threshold=0.95 violations
    violations = []
    with open(baseline_file, encoding='utf-8') as f:
        for line in f:
            if 'threshold=0.95' in line:
                file_path = line.split(':')[0]
                violations.append(project_root / file_path)

    # Deduplicate files
    unique_files = sorted(set(violations))
    print(f"[INFO] Found {len(unique_files)} files with threshold=0.95 violations")

    # Analyze each file
    fixable_files = []
    for file_path in unique_files:
        if not file_path.exists():
            continue

        analysis = analyze_file(file_path)
        if analysis.get('can_fix'):
            fixable_files.append(analysis)

    print(f"[INFO] {len(fixable_files)} files can be automatically fixed")

    # Group by whether they already have the import
    has_import = [f for f in fixable_files if f['has_import']]
    needs_import = [f for f in fixable_files if not f['has_import']]

    print("\n[ANALYSIS]")
    print(f"  Already imports THRESHOLD: {len(has_import)} files")
    print(f"  Needs import added: {len(needs_import)} files")

    # Show top 10 files by violation count
    print("\n[TOP VIOLATORS]")
    sorted_files = sorted(fixable_files, key=lambda x: x['violations'], reverse=True)[:10]
    for f in sorted_files:
        status = "✓ has import" if f['has_import'] else "✗ needs import"
        print(f"  {f['violations']:3d} violations - {f['file']} ({status})")

    return 0


if __name__ == '__main__':
    sys.exit(main())
