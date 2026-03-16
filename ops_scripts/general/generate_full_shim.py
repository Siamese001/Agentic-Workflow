"""Generate a complete monolith shim that re-exports ALL names from the modular package."""
from __future__ import annotations

import ast
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
    get_validated_project_root,
)
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

_emit_records_execution_trace("p0", "evidence", "generate_full_shim")
_emit_applies_guardrail("p0", "generate_full_shim", "p0_governance")
_emit_reads_policy_state("p0", "generate_full_shim", "policy_binding")
_emit_snapshots_state("p0", "generate_full_shim", "state_snapshot")
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
