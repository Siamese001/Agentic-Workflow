"""Debug AST visitor for mixed list in AnnAssign."""
import ast
import sys

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

_emit_records_execution_trace("p0", "evidence", "_debug_visitor")
_emit_applies_guardrail("p0", "_debug_visitor", "p0_governance")
_emit_reads_policy_state("p0", "_debug_visitor", "policy_binding")
_emit_snapshots_state("p0", "_debug_visitor", "state_snapshot")
emit_replay_key("p0", "_debug_visitor")
emit_determinism_digest("p0", "_debug_visitor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_debug_visitor", "execution_auth")
_emit_validates_capability("p2", "_debug_visitor", "capability_check")
_emit_routes_to_capability("p2", "_debug_visitor", "capability_route")
_emit_writes_via_uwg("p2", "_debug_visitor", "uwg_write")
_emit_blocks_direct_write("p2", "_debug_visitor", "direct_write_block")
_emit_records_tool_invocation("p2", "_debug_visitor", "tool_invocation")
_emit_captures_execution_output("p2", "_debug_visitor", "exec_output")
_emit_dispatches_agent("p3", "_debug_visitor", "agent_dispatch")
_emit_coordinates_agents("p3", "_debug_visitor", "agent_coordination")
_emit_records_workflow_lineage("p3", "_debug_visitor", "workflow_lineage")
_emit_records_healing_outcome("p3", "_debug_visitor", "healing_outcome")
_emit_escalates_failure("p3", "_debug_visitor", "failure_escalation")
_emit_orchestrates_workflow("p3", "_debug_visitor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_debug_visitor", "healing_dispatch")
_emit_invokes_evaluation("p3", "_debug_visitor", "evaluation_signal")
_emit_records_telemetry_event("p4", "_debug_visitor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_debug_visitor", "eval_metric")
_emit_stores_embedding("p4", "_debug_visitor", "embedding_store")
_emit_updates_meta_learning_state("p4", "_debug_visitor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_debug_visitor", "exec_snapshot_link")
# guardian: allow-global-mutation
sys.path.insert(0, '.')
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
from ops_scripts.ci._fix_hardcoded_ssot_literals import _collect_safe_positions

content = Path('agentic_core/L0_routing/utils/scorched_earth_merge_util.py').read_text(encoding='utf-8')
safe_positions = _collect_safe_positions(content)
print(f'Safe positions: {len(safe_positions)}')
for pos in sorted(safe_positions):
    if pos[0] == 23:
        print(f'  Line 23, col {pos[1]} is safe')
tree = ast.parse(content)
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and node.value == AGENTIC_CORE_DIR:
        print(f'"agentic_core" at line {node.lineno}, col {node.col_offset}')
        print(f'  Is safe: {(node.lineno, node.col_offset) in safe_positions}')
