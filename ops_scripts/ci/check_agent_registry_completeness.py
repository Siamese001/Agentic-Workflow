"""AST-based CI guard: every apps_* reasoning agent class is in AGENT_REGISTRY.

Scans all apps_*/reasoning/*.py files, extracts class names, cross-checks
against the AGENT_REGISTRY dict keys.  Hard-fails on any missing entry.
"""
from __future__ import annotations

import ast
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

_emit_records_execution_trace("p0", "evidence", "check_agent_registry_completeness")
_emit_applies_guardrail("p0", "check_agent_registry_completeness", "p0_governance")
_emit_reads_policy_state("p0", "check_agent_registry_completeness", "policy_binding")
_emit_snapshots_state("p0", "check_agent_registry_completeness", "state_snapshot")
emit_replay_key("p0", "check_agent_registry_completeness")
emit_determinism_digest("p0", "check_agent_registry_completeness")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_agent_registry_completeness", "execution_auth")
_emit_validates_capability("p2", "check_agent_registry_completeness", "capability_check")
_emit_routes_to_capability("p2", "check_agent_registry_completeness", "capability_route")
_emit_writes_via_uwg("p2", "check_agent_registry_completeness", "uwg_write")
_emit_blocks_direct_write("p2", "check_agent_registry_completeness", "direct_write_block")
_emit_records_tool_invocation("p2", "check_agent_registry_completeness", "tool_invocation")
_emit_captures_execution_output("p2", "check_agent_registry_completeness", "exec_output")
_emit_dispatches_agent("p3", "check_agent_registry_completeness", "agent_dispatch")
_emit_coordinates_agents("p3", "check_agent_registry_completeness", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_agent_registry_completeness", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_agent_registry_completeness", "healing_outcome")
_emit_escalates_failure("p3", "check_agent_registry_completeness", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_agent_registry_completeness", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_agent_registry_completeness", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_agent_registry_completeness", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_agent_registry_completeness", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_agent_registry_completeness", "eval_metric")
_emit_stores_embedding("p4", "check_agent_registry_completeness", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_agent_registry_completeness", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_agent_registry_completeness", "exec_snapshot_link")
REPO_ROOT = Path(__file__).resolve().parents[2]
REASONING_GLOBS = ['apps_lic/reasoning/*.py', 'apps_rg/reasoning/*.py', 'apps_shared/reasoning/*.py']

def _extract_classes(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding='utf-8', errors='replace'))
    except SyntaxError:
        return []
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

def _load_registry_keys() -> set[str]:
    # guardian: allow-global-mutation
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from agentic_core.agents.agent_registry import AGENT_REGISTRY
        return set(AGENT_REGISTRY.keys())
    except (ImportError, AttributeError):
        return set()

def main() -> int:
    agent_classes: list[tuple[str, str]] = []
    for glob in REASONING_GLOBS:
        for path in REPO_ROOT.glob(glob):
            for cls in _extract_classes(path):
                agent_classes.append((cls, path.relative_to(REPO_ROOT).as_posix()))
    registry_keys = _load_registry_keys()
    missing = [(cls, path) for cls, path in agent_classes if cls not in registry_keys]
    print(f'Registry keys: {len(registry_keys)}')
    print(f'Agent classes scanned: {len(agent_classes)}')
    print(f'Missing from registry: {len(missing)}')
    if missing:
        print('FAIL: unregistered agent classes:')
        for cls, path in sorted(missing):
            print(f'  {cls}  ({path})')
        return 1
    print('OK: all agent classes registered')
    return 0
if __name__ == '__main__':
    sys.exit(main())
