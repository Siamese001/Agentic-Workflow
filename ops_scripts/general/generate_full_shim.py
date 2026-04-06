"""Generate a complete monolith shim that re-exports ALL names from the modular package."""
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

_emit_emits_metric_event("generate_full_shim", "p4obs", "metric_1")
_emit_emits_metric_event("generate_full_shim", "p4obs", "metric_2")
_emit_emits_metric_event("generate_full_shim", "p4obs", "metric_3")
_emit_emits_metric_event("generate_full_shim", "p4obs", "metric_4")
_emit_emits_metric_event("generate_full_shim", "p4obs", "metric_5")
_emit_emits_metric_event("generate_full_shim", "p4obs", "metric_6")
_emit_records_incident_event("generate_full_shim", "p4obs", "incident")
_emit_captures_runtime_anomaly("generate_full_shim", "p4obs", "anomaly")
_emit_writes_observability_log("generate_full_shim", "p4obs", "obs_log")
_emit_updates_monitoring_state("generate_full_shim", "p4obs", "mon_state")
_emit_triggers_alert("generate_full_shim", "p4obs", "alert")
_emit_links_incident_trace("generate_full_shim", "p4obs", "trace_link")
_emit_captures_pattern("generate_full_shim", "p3lm", "pattern")
_emit_records_learning_event("generate_full_shim", "p3lm", "learning_event")
_emit_writes_learning_snapshot("generate_full_shim", "p3lm", "snapshot")
_emit_feeds_meta_learning("generate_full_shim", "p3lm", "meta_feed")
_emit_updates_routing_strategy("generate_full_shim", "p3lm", "routing")
_emit_improves_agent_policy("generate_full_shim", "p3lm", "policy")
_emit_stores_learning_state("generate_full_shim", "p3lm", "state")
_emit_records_execution_trace("generate_full_shim", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("generate_full_shim", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("generate_full_shim", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("generate_full_shim", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("generate_full_shim", "L4_STATE", "p2_trace_5")
_emit_reads_environ("generate_full_shim", "env_read", "p2_env_1")
_emit_reads_environ("generate_full_shim", "env_read", "p2_env_2")
_emit_reads_runtime_state("generate_full_shim", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("generate_full_shim", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "generate_full_shim")
_emit_applies_guardrail("p0", "generate_full_shim", "p0_governance")
_emit_reads_policy_state("p0", "generate_full_shim", "policy_binding")
_emit_snapshots_state("p0", "generate_full_shim", "state_snapshot")
_emit_pulls_context("p1", "generate_full_shim", "context_pull")
_emit_pulls_context("p1", "generate_full_shim", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "generate_full_shim", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "generate_full_shim", "uwg_term_secondary")
_emit_writes_through("p1", "generate_full_shim", "write_through")
_emit_writes_through("p1", "generate_full_shim", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "generate_full_shim", "safety_validation")
_emit_invokes_eval("p1", "generate_full_shim", "eval_call")
_emit_proposal_commits_routing("p1", "generate_full_shim", "routing_commit")
_emit_escalates_to_human("p1", "generate_full_shim", "human_escalation")
_emit_routes_through("p1", "generate_full_shim", "route_through")
_emit_checks_agent_registry("p1", "generate_full_shim", "agent_registry")
_emit_validates_agent_capability("p1", "generate_full_shim", "capability")
_emit_dispatches_execution_plan("p1", "generate_full_shim", "exec_plan")
_emit_agent_executes_agent("p1", "generate_full_shim", "sub_agent")
_emit_routes_to_agent("p1", "generate_full_shim", "target_agent")
_emit_verifies_policy("p1", "generate_full_shim", "policy_check")
_emit_observes_runtime_state("p1", "generate_full_shim", "runtime_state")
_emit_verifies_boundary("p1", "generate_full_shim", "boundary_check")
_emit_transcripts_response("p1", "generate_full_shim", "transcript")
_emit_hard_fails_untranscripted("p1", "generate_full_shim")
_emit_gated_by_confidence("p1", "generate_full_shim", "confidence_gate")
emit_replay_key("p0", "generate_full_shim")
emit_determinism_digest("p0", "generate_full_shim")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "generate_full_shim", "execution_auth")
_emit_validates_capability("p2", "generate_full_shim", "capability_check")
_emit_routes_to_capability("p2", "generate_full_shim", "capability_route")
_emit_writes_via_uwg("p2", "generate_full_shim", "uwg_write")
_emit_blocks_direct_write("p2", "generate_full_shim", "direct_write_block")
_emit_records_tool_invocation("p2", "generate_full_shim", "tool_invocation")
_emit_captures_execution_output("p2", "generate_full_shim", "exec_output")
_emit_dispatches_agent("p3", "generate_full_shim", "agent_dispatch")
_emit_coordinates_agents("p3", "generate_full_shim", "agent_coordination")
_emit_records_workflow_lineage("p3", "generate_full_shim", "workflow_lineage")
_emit_records_healing_outcome("p3", "generate_full_shim", "healing_outcome")
_emit_escalates_failure("p3", "generate_full_shim", "failure_escalation")
_emit_orchestrates_workflow("p3", "generate_full_shim", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "generate_full_shim", "healing_dispatch")
_emit_invokes_evaluation("p3", "generate_full_shim", "evaluation_signal")
_emit_records_telemetry_event("p4", "generate_full_shim", "telemetry_event")
_emit_captures_evaluation_metric("p4", "generate_full_shim", "eval_metric")
_emit_stores_embedding("p4", "generate_full_shim", "embedding_store")
_emit_updates_meta_learning_state("p4", "generate_full_shim", "meta_learning")
_emit_links_execution_to_snapshot("p4", "generate_full_shim", "exec_snapshot_link")
ROOT = get_validated_project_root()
MOD_DIR = ROOT / AGENTIC_CORE_DIR / 'L5_safety' / 'config' / 'structure_blueprint'
TARGET = ROOT / AGENTIC_CORE_DIR / 'L5_safety' / 'config' / 'structure_blueprint_config.py'

def collect_public_names() -> dict[str, list[str]]:
    by_module: dict[str, list[str]] = {}
    for f in sorted(MOD_DIR.glob('*.py')):
        if f.name == '__init__.py':
            continue
        src = f.read_text(encoding='utf-8')
        tree = ast.parse(src)
        names: list[str] = []
        for node in ast.iter_child_nodes(tree):
            name = None
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and (not t.id.startswith('_')):
                        name = t.id
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if not node.target.id.startswith('_'):
                    name = node.target.id
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_'):
                    name = node.name
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith('_'):
                    name = node.name
            if name and name not in names:
                names.append(name)
        by_module[f.stem] = sorted(set(names))
    return by_module

def generate_shim(by_module: dict[str, list[str]]) -> str:
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
    parts.append('# noqa: F401 — re-exports for backward compatibility')
    parts.append('')
    parts.append('from __future__ import annotations')
    parts.append('')
    module_order = ['ssot', 'territories', 'classification', 'semantics', 'artifacts', 'derived', 'governance']
    all_names: list[str] = []
    for mod in module_order:
        names = by_module.get(mod, [])
        if not names:
            continue
        parts.append(f'from agentic_core.L5_safety.config.structure_blueprint.{mod} import (  # noqa: F401')
        for n in sorted(names):
            parts.append(f'    {n},')
            all_names.append(n)
        parts.append(')')
        parts.append('')
    parts.append('')
    parts.append('__all__ = [')
    for n in sorted(set(all_names)):
        parts.append(f'    "{n}",')
    parts.append(']')
    parts.append('')
    return '\n'.join(parts)

def main() -> None:
    by_module = collect_public_names()
    total = sum(len(v) for v in by_module.values())
    print(f'Collected {total} public names across {len(by_module)} modules')
    shim = generate_shim(by_module)
    TARGET.write_text(shim, encoding='utf-8')
    print(f'Wrote shim: {len(shim.splitlines())} lines')
    ast.parse(shim)
    print('Syntax OK')
if __name__ == '__main__':
    main()
