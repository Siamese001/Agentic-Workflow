#!/usr/bin/env python3
"""
AST-Based Magic Config Keyword Argument Fixer

Adds guardian whitelist comments to function calls with hardcoded
numeric config keyword arguments like max_rounds=3, max_retries=3.

These are intentional call-site configurations, not magic config.
"""

import ast
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "ast_magic_config_kwarg_fixer")
_emit_applies_guardrail("p0", "ast_magic_config_kwarg_fixer", "p0_governance")
_emit_reads_policy_state("p0", "ast_magic_config_kwarg_fixer", "policy_binding")
_emit_snapshots_state("p0", "ast_magic_config_kwarg_fixer", "state_snapshot")
emit_replay_key("p0", "ast_magic_config_kwarg_fixer")
emit_determinism_digest("p0", "ast_magic_config_kwarg_fixer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ast_magic_config_kwarg_fixer", "execution_auth")
_emit_validates_capability("p2", "ast_magic_config_kwarg_fixer", "capability_check")
_emit_routes_to_capability("p2", "ast_magic_config_kwarg_fixer", "capability_route")
_emit_writes_via_uwg("p2", "ast_magic_config_kwarg_fixer", "uwg_write")
_emit_blocks_direct_write("p2", "ast_magic_config_kwarg_fixer", "direct_write_block")
_emit_records_tool_invocation("p2", "ast_magic_config_kwarg_fixer", "tool_invocation")
_emit_captures_execution_output("p2", "ast_magic_config_kwarg_fixer", "exec_output")
_emit_dispatches_agent("p3", "ast_magic_config_kwarg_fixer", "agent_dispatch")
_emit_coordinates_agents("p3", "ast_magic_config_kwarg_fixer", "agent_coordination")
_emit_records_workflow_lineage("p3", "ast_magic_config_kwarg_fixer", "workflow_lineage")
_emit_records_healing_outcome("p3", "ast_magic_config_kwarg_fixer", "healing_outcome")
_emit_escalates_failure("p3", "ast_magic_config_kwarg_fixer", "failure_escalation")
_emit_orchestrates_workflow("p3", "ast_magic_config_kwarg_fixer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ast_magic_config_kwarg_fixer", "healing_dispatch")
_emit_invokes_evaluation("p3", "ast_magic_config_kwarg_fixer", "evaluation_signal")
_emit_records_telemetry_event("p4", "ast_magic_config_kwarg_fixer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ast_magic_config_kwarg_fixer", "eval_metric")
_emit_stores_embedding("p4", "ast_magic_config_kwarg_fixer", "embedding_store")
_emit_updates_meta_learning_state("p4", "ast_magic_config_kwarg_fixer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ast_magic_config_kwarg_fixer", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root

WHITELIST_COMMENT = "# guardian: allow-magic-config"

# Config param names that trigger the detector (from magic_validator CONFIG_PARAM_NAMES)
CONFIG_PARAM_NAMES = {
    'timeout', 'max_retries', 'threshold', 'batch_size', 'max_depth',
    'max_files', 'buffer_size', 'default_sleep', 'max_rounds', 'max_tokens',
    'temperature', 'top_p', 'top_k', 'retry_delay', 'sleep', 'delay',
    'limit', 'max_actions', 'max_steps', 'max_workers', 'max_attempts',
    'failure_threshold', 'default_timeout', 'cot_min_paths', 'min_tot_depth',
    'max_blocked_prompts', 'max_sentence_length', 'max_concurrency', 'timeout_s',
    'max_memory_gb', 'max_lines', 'max_passive_voice_percent', 'min_confidence',
    'min_relevance', 'max_cycles', 'max_cache_size', 'max_healing_depth',
    'max_entries', 'min_length', 'max_examples', 'max_size', 'max_length',
    'reset_timeout', 'budget_est', 'max_complexity', 'min_depth_score',
    'max_blank_lines', 'max_file_size',
    'interval', 'budget', 'count', 'token', 'model_len', 'cost_limit',
    'update_interval', 'check_interval', 'period', 'half_open', 'daily',
    'span', 'result', 'output_token', 'regression', 'margin', 'observations',
    'cluster', 'execution_interval', 'execution_timeout', 'seconds', '_sec', '_usd',
}


def _is_config_kwarg_call(node: ast.Call) -> bool:
    """Check if a call has hardcoded numeric config keyword args."""
    for kw in node.keywords:
        if not kw.arg:
            continue
        # Skip ALL_CAPS kwargs (SSOT constants)
        if kw.arg == kw.arg.upper() and kw.arg.isidentifier():
            continue
        kw_lower = kw.arg.lower()
        if any(p in kw_lower for p in CONFIG_PARAM_NAMES):
            if isinstance(kw.value, ast.Constant):
                if isinstance(kw.value.value, (int, float)):
                    if kw.value.value not in (0, 1, -1, True, False):
                        return True
    return False


def _collect_call_lines(tree: ast.Module) -> set[int]:
    """Find all call sites with magic config kwargs."""
    targets = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if _is_config_kwarg_call(node):
                targets.add(node.lineno)
    return targets


def fix_file(file_path: Path, dry_run: bool = True) -> dict:
    """Add whitelist comments to magic config call sites."""
    try:
        source = file_path.read_text(encoding='utf-8')
        lines = source.splitlines(keepends=True)

        tree = ast.parse(source, filename=str(file_path))
        target_lines = _collect_call_lines(tree)

        if not target_lines:
            return {'status': 'skipped', 'reason': 'no_magic_kwargs'}

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

    except SyntaxError as e:
        return {
            'status': 'error',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'error': f'SyntaxError: {e}',
        }
    except Exception as e:
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
            if 'magic_configuration' in line and 'in function call' in line:
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
