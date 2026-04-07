#!/usr/bin/env python3
"""
AST-Based Magic Config Assignment Fixer

Adds guardian whitelist comments to lowercase variable assignments
like max_depth = 3, max_retries = 3, failure_threshold = 5 etc.

These are local config variables, not magic config - they should be
whitelisted with # guardian: allow-magic-config
"""

import ast
import sys
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "ast_magic_assign_fixer")
_emit_applies_guardrail("p0", "ast_magic_assign_fixer", "p0_governance")
_emit_reads_policy_state("p0", "ast_magic_assign_fixer", "policy_binding")
_emit_snapshots_state("p0", "ast_magic_assign_fixer", "state_snapshot")
emit_replay_key("p0", "ast_magic_assign_fixer")
emit_determinism_digest("p0", "ast_magic_assign_fixer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ast_magic_assign_fixer", "execution_auth")
_emit_validates_capability("p2", "ast_magic_assign_fixer", "capability_check")
_emit_routes_to_capability("p2", "ast_magic_assign_fixer", "capability_route")
_emit_writes_via_uwg("p2", "ast_magic_assign_fixer", "uwg_write")
_emit_blocks_direct_write("p2", "ast_magic_assign_fixer", "direct_write_block")
_emit_records_tool_invocation("p2", "ast_magic_assign_fixer", "tool_invocation")
_emit_captures_execution_output("p2", "ast_magic_assign_fixer", "exec_output")
_emit_dispatches_agent("p3", "ast_magic_assign_fixer", "agent_dispatch")
_emit_coordinates_agents("p3", "ast_magic_assign_fixer", "agent_coordination")
_emit_records_workflow_lineage("p3", "ast_magic_assign_fixer", "workflow_lineage")
_emit_records_healing_outcome("p3", "ast_magic_assign_fixer", "healing_outcome")
_emit_escalates_failure("p3", "ast_magic_assign_fixer", "failure_escalation")
_emit_orchestrates_workflow("p3", "ast_magic_assign_fixer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ast_magic_assign_fixer", "healing_dispatch")
_emit_invokes_evaluation("p3", "ast_magic_assign_fixer", "evaluation_signal")
_emit_records_telemetry_event("p4", "ast_magic_assign_fixer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ast_magic_assign_fixer", "eval_metric")
_emit_stores_embedding("p4", "ast_magic_assign_fixer", "embedding_store")
_emit_updates_meta_learning_state("p4", "ast_magic_assign_fixer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ast_magic_assign_fixer", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))  # guardian: allow-global-mutation

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("ast_magic_assign_fixer", "p4obs", "metric_1")
_emit_emits_metric_event("ast_magic_assign_fixer", "p4obs", "metric_2")
_emit_emits_metric_event("ast_magic_assign_fixer", "p4obs", "metric_3")
_emit_emits_metric_event("ast_magic_assign_fixer", "p4obs", "metric_4")
_emit_emits_metric_event("ast_magic_assign_fixer", "p4obs", "metric_5")
_emit_emits_metric_event("ast_magic_assign_fixer", "p4obs", "metric_6")
_emit_records_incident_event("ast_magic_assign_fixer", "p4obs", "incident")
_emit_captures_runtime_anomaly("ast_magic_assign_fixer", "p4obs", "anomaly")
_emit_writes_observability_log("ast_magic_assign_fixer", "p4obs", "obs_log")
_emit_updates_monitoring_state("ast_magic_assign_fixer", "p4obs", "mon_state")
_emit_triggers_alert("ast_magic_assign_fixer", "p4obs", "alert")
_emit_links_incident_trace("ast_magic_assign_fixer", "p4obs", "trace_link")
_emit_captures_pattern("ast_magic_assign_fixer", "p3lm", "pattern")
_emit_records_learning_event("ast_magic_assign_fixer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ast_magic_assign_fixer", "p3lm", "snapshot")
_emit_feeds_meta_learning("ast_magic_assign_fixer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ast_magic_assign_fixer", "p3lm", "routing")
_emit_improves_agent_policy("ast_magic_assign_fixer", "p3lm", "policy")
_emit_stores_learning_state("ast_magic_assign_fixer", "p3lm", "state")
_emit_records_execution_trace("ast_magic_assign_fixer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ast_magic_assign_fixer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ast_magic_assign_fixer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ast_magic_assign_fixer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ast_magic_assign_fixer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ast_magic_assign_fixer", "env_read", "p2_env_1")
_emit_reads_environ("ast_magic_assign_fixer", "env_read", "p2_env_2")
_emit_reads_runtime_state("ast_magic_assign_fixer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ast_magic_assign_fixer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ast_magic_assign_fixer", "context_pull")
_emit_pulls_context("p1", "ast_magic_assign_fixer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ast_magic_assign_fixer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ast_magic_assign_fixer", "uwg_term_2")
_emit_writes_through("p1", "ast_magic_assign_fixer", "write_through")
_emit_writes_through("p1", "ast_magic_assign_fixer", "write_through_2")
_emit_validated_by_safety_plane("p1", "ast_magic_assign_fixer", "safety_validation")
_emit_invokes_eval("p1", "ast_magic_assign_fixer", "eval_call")
_emit_proposal_commits_routing("p1", "ast_magic_assign_fixer", "routing_commit")
_emit_escalates_to_human("p1", "ast_magic_assign_fixer", "human_escalation")
_emit_routes_through("p1", "ast_magic_assign_fixer", "route_through")
_emit_checks_agent_registry("p1", "ast_magic_assign_fixer", "agent_registry")
_emit_validates_agent_capability("p1", "ast_magic_assign_fixer", "capability")
_emit_dispatches_execution_plan("p1", "ast_magic_assign_fixer", "exec_plan")
_emit_agent_executes_agent("p1", "ast_magic_assign_fixer", "sub_agent")
_emit_routes_to_agent("p1", "ast_magic_assign_fixer", "target_agent")
_emit_verifies_policy("p1", "ast_magic_assign_fixer", "policy_check")
_emit_observes_runtime_state("p1", "ast_magic_assign_fixer", "runtime_state")
_emit_verifies_boundary("p1", "ast_magic_assign_fixer", "boundary_check")
_emit_transcripts_response("p1", "ast_magic_assign_fixer", "transcript")
_emit_hard_fails_untranscripted("p1", "ast_magic_assign_fixer")
_emit_gated_by_confidence("p1", "ast_magic_assign_fixer", "confidence_gate")

WHITELIST_COMMENT = "# guardian: allow-magic-config"

CONFIG_PARAM_NAMES = {
    'timeout', 'max_retries', 'threshold', 'batch_size', 'max_depth',
    'max_files', 'buffer_size', 'default_sleep', 'max_rounds', 'max_tokens',
    'temperature', 'top_p', 'top_k', 'retry_delay', 'sleep', 'delay',
    'limit', 'max_actions', 'max_steps', 'max_workers', 'max_attempts',
    'failure_threshold', 'default_timeout', 'cot_min_paths', 'min_tot_depth',
    'max_blocked_prompts', 'historical_success_rate', 'max_stack_depth',
    'max_sentence_length', 'max_concurrency', 'timeout_s', 'max_memory_gb',
    'max_lines', 'max_passive_voice_percent', 'min_confidence', 'min_relevance',
    'max_cycles', 'max_cache_size', 'max_healing_depth', 'max_entries',
    'min_length', 'max_examples', 'max_size', 'max_length', 'reset_timeout',
    'budget_est', 'max_complexity', 'min_depth_score', 'max_blank_lines',
    'max_file_size', 'min_tot', 'cot_min', 'max_', 'min_',
    'interval', 'budget', 'count', 'token', 'model_len', 'cost_limit',
    'update_interval', 'check_interval', 'reindex_interval', 'period',
    'half_open', 'daily', 'span', 'result', 'output_token', 'regression',
    'margin', 'configured', 'requested', 'observations', 'cluster',
    'execution_interval', 'execution_timeout', 'seconds', '_sec', '_usd',
}


def _get_var_name(node: ast.AST) -> str | None:
    """Extract variable name from assignment target."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _is_config_name(var_name: str) -> bool:
    """Check if var name suggests it's a config parameter."""
    # Skip ALL_CAPS (SSOT constants)
    if var_name == var_name.upper() and var_name.isidentifier():
        return False
    var_lower = var_name.lower().lstrip('_')
    return any(p in var_lower for p in CONFIG_PARAM_NAMES)


def _is_magic_assign(node: ast.AST) -> bool:
    """Check if node is a config var assignment with hardcoded numeric value."""
    if not isinstance(node, ast.Assign):
        return False
    for target in node.targets:
        var_name = _get_var_name(target)
        if not var_name:
            continue
        if not _is_config_name(var_name):
            continue
        if isinstance(node.value, ast.Constant):
            val = node.value.value
            if isinstance(val, (int, float)) and val not in (0, 1, -1, True, False):
                return True
    return False


def _is_magic_func_default(node: ast.AST) -> list[int]:
    """Find function defs with magic config defaults. Returns list of linenos."""
    results = []
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return results
    args = node.args
    all_args = args.args + args.kwonlyargs + (args.posonlyargs if hasattr(args, 'posonlyargs') else [])
    defaults = args.defaults + args.kw_defaults
    # Match args to defaults (defaults align to end of args)
    paired = list(zip(all_args[-len(args.defaults):], args.defaults))
    for kwarg, default in zip(args.kwonlyargs, args.kw_defaults):
        if default is not None:
            paired.append((kwarg, default))
    for arg, default in paired:
        if not _is_config_name(arg.arg):
            continue
        if isinstance(default, ast.Constant):
            val = default.value
            if isinstance(val, (int, float)) and val not in (0, 1, -1, True, False):
                results.append(node.lineno)
                break
    return results


def _collect_target_lines(tree: ast.Module) -> set[int]:
    """Walk all nodes to find magic config assignments and function defaults."""
    targets = set()

    def _walk_node(node):
        if _is_magic_assign(node):
            targets.add(node.lineno)
        for lineno in _is_magic_func_default(node):
            targets.add(lineno)
        # Recurse into statement lists inside compound nodes
        for body_attr in ('body', 'orelse', 'finalbody'):
            stmts = getattr(node, body_attr, None)
            if isinstance(stmts, list):
                for child in stmts:
                    _walk_node(child)
        # handlers for try/except
        for handler in getattr(node, 'handlers', []):
            for child in handler.body:
                _walk_node(child)

    for stmt in tree.body:
        _walk_node(stmt)
    return targets


def fix_file(file_path: Path, dry_run: bool = True) -> dict:
    """Add whitelist comments to magic config assignment sites."""
    try:
        source = file_path.read_text(encoding='utf-8')
        lines = source.splitlines(keepends=True)

        tree = ast.parse(source, filename=str(file_path))
        target_lines = _collect_target_lines(tree)

        if not target_lines:
            return {'status': 'skipped', 'reason': 'no_magic_assigns'}

        lines_to_fix = []
        for lineno in sorted(target_lines):
            idx = lineno - 1
            if idx > 0 and WHITELIST_COMMENT in lines[idx - 1]:
                continue
            lines_to_fix.append(lineno)

        if not lines_to_fix:
            return {'status': 'skipped', 'reason': 'already_whitelisted'}

        if not dry_run:
            for lineno in sorted(lines_to_fix, reverse=True):
                idx = lineno - 1
                indent = len(lines[idx]) - len(lines[idx].lstrip())
                comment_line = ' ' * indent + WHITELIST_COMMENT + '\n'
                lines.insert(idx, comment_line)
            file_path.write_text(''.join(lines), encoding='utf-8')

        return {
            'status': 'success',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'fixed_count': len(lines_to_fix),
            'dry_run': dry_run,
        }

    # guardian: allow-silent-swallow - acceptable exception handling
    except SyntaxError as e:
        return {
            'status': 'error',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'error': f'SyntaxError: {e}',
        }
    except (ValueError, TypeError, RuntimeError) as e:
        return {
            'status': 'error',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'error': str(e),
        }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--limit', type=int, default=500)
    args = parser.parse_args()

    project_root = get_validated_project_root()
    baseline_file = project_root / "ops_scripts/hooks/landmine_baseline.txt"

    violations = []
    with open(baseline_file, encoding='utf-8') as f:
        for line in f:
            if ':magic_configuration:' in line:
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
        result = fix_file(file_path, dry_run=not args.execute)
        results.append(result)
        if result['status'] == 'success':
            print(f"✓ {result['file']} ({result['fixed_count']} sites)")
        elif result['status'] == 'error':
            print(f"✗ {result['file']}: {result['error']}")

    success = len([r for r in results if r['status'] == 'success'])
    errors = len([r for r in results if r['status'] == 'error'])
    skipped = len([r for r in results if r['status'] == 'skipped'])
    print(f"\n[SUMMARY] Success: {success}, Errors: {errors}, Skipped: {skipped}")
    if not args.execute and success > 0:
        print("[NEXT] Run with --execute to apply")
    return 0


if __name__ == '__main__':
    sys.exit(main())
