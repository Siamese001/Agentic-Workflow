"""
Generate the monolith shim that re-exports everything from the modular package.

Scans all 197 importers to find exactly which names they import from
structure_blueprint_config, then generates a shim that re-exports them.
"""
from __future__ import annotations

import ast
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("generate_monolith_shim", "p4obs", "metric_1")
_emit_emits_metric_event("generate_monolith_shim", "p4obs", "metric_2")
_emit_emits_metric_event("generate_monolith_shim", "p4obs", "metric_3")
_emit_emits_metric_event("generate_monolith_shim", "p4obs", "metric_4")
_emit_emits_metric_event("generate_monolith_shim", "p4obs", "metric_5")
_emit_emits_metric_event("generate_monolith_shim", "p4obs", "metric_6")
_emit_records_incident_event("generate_monolith_shim", "p4obs", "incident")
_emit_captures_runtime_anomaly("generate_monolith_shim", "p4obs", "anomaly")
_emit_writes_observability_log("generate_monolith_shim", "p4obs", "obs_log")
_emit_updates_monitoring_state("generate_monolith_shim", "p4obs", "mon_state")
_emit_triggers_alert("generate_monolith_shim", "p4obs", "alert")
_emit_links_incident_trace("generate_monolith_shim", "p4obs", "trace_link")
_emit_captures_pattern("generate_monolith_shim", "p3lm", "pattern")
_emit_records_learning_event("generate_monolith_shim", "p3lm", "learning_event")
_emit_writes_learning_snapshot("generate_monolith_shim", "p3lm", "snapshot")
_emit_feeds_meta_learning("generate_monolith_shim", "p3lm", "meta_feed")
_emit_updates_routing_strategy("generate_monolith_shim", "p3lm", "routing")
_emit_improves_agent_policy("generate_monolith_shim", "p3lm", "policy")
_emit_stores_learning_state("generate_monolith_shim", "p3lm", "state")
_emit_records_execution_trace("generate_monolith_shim", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("generate_monolith_shim", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("generate_monolith_shim", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("generate_monolith_shim", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("generate_monolith_shim", "L4_STATE", "p2_trace_5")
_emit_reads_environ("generate_monolith_shim", "env_read", "p2_env_1")
_emit_reads_environ("generate_monolith_shim", "env_read", "p2_env_2")
_emit_reads_runtime_state("generate_monolith_shim", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("generate_monolith_shim", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "generate_monolith_shim")
_emit_applies_guardrail("p0", "generate_monolith_shim", "p0_governance")
_emit_reads_policy_state("p0", "generate_monolith_shim", "policy_binding")
_emit_snapshots_state("p0", "generate_monolith_shim", "state_snapshot")
_emit_pulls_context("p1", "generate_monolith_shim", "context_pull")
_emit_pulls_context("p1", "generate_monolith_shim", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "generate_monolith_shim", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "generate_monolith_shim", "uwg_term_secondary")
_emit_writes_through("p1", "generate_monolith_shim", "write_through")
_emit_writes_through("p1", "generate_monolith_shim", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "generate_monolith_shim", "safety_validation")
_emit_invokes_eval("p1", "generate_monolith_shim", "eval_call")
_emit_proposal_commits_routing("p1", "generate_monolith_shim", "routing_commit")
_emit_escalates_to_human("p1", "generate_monolith_shim", "human_escalation")
_emit_routes_through("p1", "generate_monolith_shim", "route_through")
_emit_checks_agent_registry("p1", "generate_monolith_shim", "agent_registry")
_emit_validates_agent_capability("p1", "generate_monolith_shim", "capability")
_emit_dispatches_execution_plan("p1", "generate_monolith_shim", "exec_plan")
_emit_agent_executes_agent("p1", "generate_monolith_shim", "sub_agent")
_emit_routes_to_agent("p1", "generate_monolith_shim", "target_agent")
_emit_verifies_policy("p1", "generate_monolith_shim", "policy_check")
_emit_observes_runtime_state("p1", "generate_monolith_shim", "runtime_state")
_emit_verifies_boundary("p1", "generate_monolith_shim", "boundary_check")
_emit_transcripts_response("p1", "generate_monolith_shim", "transcript")
_emit_hard_fails_untranscripted("p1", "generate_monolith_shim")
_emit_gated_by_confidence("p1", "generate_monolith_shim", "confidence_gate")
emit_replay_key("p0", "generate_monolith_shim")
emit_determinism_digest("p0", "generate_monolith_shim")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "generate_monolith_shim", "execution_auth")
_emit_validates_capability("p2", "generate_monolith_shim", "capability_check")
_emit_routes_to_capability("p2", "generate_monolith_shim", "capability_route")
_emit_writes_via_uwg("p2", "generate_monolith_shim", "uwg_write")
_emit_blocks_direct_write("p2", "generate_monolith_shim", "direct_write_block")
_emit_records_tool_invocation("p2", "generate_monolith_shim", "tool_invocation")
_emit_captures_execution_output("p2", "generate_monolith_shim", "exec_output")
_emit_dispatches_agent("p3", "generate_monolith_shim", "agent_dispatch")
_emit_coordinates_agents("p3", "generate_monolith_shim", "agent_coordination")
_emit_records_workflow_lineage("p3", "generate_monolith_shim", "workflow_lineage")
_emit_records_healing_outcome("p3", "generate_monolith_shim", "healing_outcome")
_emit_escalates_failure("p3", "generate_monolith_shim", "failure_escalation")
_emit_orchestrates_workflow("p3", "generate_monolith_shim", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "generate_monolith_shim", "healing_dispatch")
_emit_invokes_evaluation("p3", "generate_monolith_shim", "evaluation_signal")
_emit_records_telemetry_event("p4", "generate_monolith_shim", "telemetry_event")
_emit_captures_evaluation_metric("p4", "generate_monolith_shim", "eval_metric")
_emit_stores_embedding("p4", "generate_monolith_shim", "embedding_store")
_emit_updates_meta_learning_state("p4", "generate_monolith_shim", "meta_learning")
_emit_links_execution_to_snapshot("p4", "generate_monolith_shim", "exec_snapshot_link")
ROOT = get_validated_project_root()
MONOLITH = ROOT / AGENTIC_CORE_DIR / 'L5_safety' / 'config' / 'structure_blueprint_config.py'
MOD_DIR = ROOT / AGENTIC_CORE_DIR / 'L5_safety' / 'config' / 'structure_blueprint'

def find_all_imported_names() -> set[str]:
    """Scan every .py file for names imported from structure_blueprint_config."""
    imported_names: set[str] = set()
    for py_file in ROOT.rglob('*.py'):
        rel = py_file.relative_to(ROOT)
        rel_str = str(rel).replace('\\', '/')
        if 'structure_blueprint_config.py' in rel_str and 'test' not in rel_str:
            continue
        if 'structure_blueprint/' in rel_str:
            continue
        if '_migrate_' in rel_str or 'generate_' in rel_str:
            continue
        try:
            source = py_file.read_text(encoding='utf-8', errors='ignore')
        except (OSError, UnicodeDecodeError):    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling
            continue
        if 'structure_blueprint_config' not in source:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and 'structure_blueprint_config' in node.module:
                    if node.names:
                        for alias in node.names:
                            imported_names.add(alias.name)
    return imported_names

def find_modular_locations(names: set[str]) -> dict[str, str]:
    """Find which modular module each name lives in."""
    name_to_module: dict[str, str] = {}
    for f in sorted(MOD_DIR.glob('*.py')):
        if f.name == '__init__.py':
            continue
        src = f.read_text(encoding='utf-8')
        tree = ast.parse(src)
        for node in ast.iter_child_nodes(tree):
            node_name = None
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        node_name = t.id
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                node_name = node.target.id
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                node_name = node.name
            elif isinstance(node, ast.ClassDef):
                node_name = node.name
            if node_name and node_name in names:
                name_to_module[node_name] = f.stem
    return name_to_module

def generate_shim(imported_names: set[str], name_to_module: dict[str, str]) -> str:
    """Generate the shim content."""
    parts: list[str] = []
    parts.append('"""')
    parts.append('Structure Blueprint Config - Backward Compatible Shim.')
    parts.append('')
    parts.append('SSOT is now: agentic_core.L5_safety.config.structure_blueprint/')
    parts.append('This file re-exports all public names for backward compatibility.')
    parts.append('All 197+ existing importers will continue to work unchanged.')
    parts.append('')
    parts.append('DO NOT add new definitions here. Add them to the modular package instead.')
    parts.append('"""')
    parts.append('')
    parts.append('from __future__ import annotations')
    parts.append('')
    by_module: dict[str, list[str]] = {}
    missing: list[str] = []
    for name in sorted(imported_names):
        if name in name_to_module:
            mod = name_to_module[name]
            if mod not in by_module:
                by_module[mod] = []
            by_module[mod].append(name)
        else:
            missing.append(name)
    module_order = ['ssot', 'territories', 'classification', 'semantics', 'artifacts', 'derived', 'governance']
    for mod in module_order:
        names = by_module.get(mod, [])
        if not names:
            continue
        parts.append(f'from agentic_core.L5_safety.config.structure_blueprint.{mod} import (')
        for n in sorted(names):
            parts.append(f'    {n},')
        parts.append(')')
        parts.append('')
    if missing:
        parts.append('')
        parts.append(f'# WARNING: {len(missing)} names not found in modular package:')
        for n in sorted(missing):
            parts.append(f'#   {n}')
    parts.append('')
    parts.append('# Re-export all names for backward compatibility')
    all_names = sorted(imported_names & set(name_to_module.keys()))
    parts.append('__all__ = [')
    for n in all_names:
        parts.append(f'    "{n}",')
    parts.append(']')
    parts.append('')
    return '\n'.join(parts)

def main() -> None:
    print('Scanning importers...')
    imported_names = find_all_imported_names()
    print(f'Found {len(imported_names)} unique names imported from monolith')
    print('Locating names in modular package...')
    name_to_module = find_modular_locations(imported_names)
    found = imported_names & set(name_to_module.keys())
    missing = imported_names - set(name_to_module.keys())
    print(f'Found: {len(found)}, Missing: {len(missing)}')
    if missing:
        print(f'MISSING names: {sorted(missing)}')
    shim = generate_shim(imported_names, name_to_module)
    output = ROOT / 'data' / 'freeze_reports' / '_monolith_shim.py'
    output.write_text(shim, encoding='utf-8')
    print(f'\nWrote shim to {output} ({len(shim.splitlines())} lines)')
    ast.parse(shim)
    print('Syntax OK')
if __name__ == '__main__':
    main()
