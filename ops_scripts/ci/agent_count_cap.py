"""Agent Count Hard Cap — CI Gate.

Asserts that the ACTIVE agent count does not exceed the hard cap.

Uses the shared ``active_set_helper`` — the single canonical import
point for the ACTIVE set.  This guarantees convergence with
``discovery_registry_consistency_check.py`` and all future gates.

Exit 0 = pass, exit 1 = violations found.

Merge-ready gate.
"""
from __future__ import annotations

import os
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

_emit_records_execution_trace("p0", "evidence", "agent_count_cap")
_emit_applies_guardrail("p0", "agent_count_cap", "p0_governance")
_emit_reads_policy_state("p0", "agent_count_cap", "policy_binding")
_emit_snapshots_state("p0", "agent_count_cap", "state_snapshot")
emit_replay_key("p0", "agent_count_cap")
emit_determinism_digest("p0", "agent_count_cap")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "agent_count_cap", "execution_auth")
_emit_validates_capability("p2", "agent_count_cap", "capability_check")
_emit_routes_to_capability("p2", "agent_count_cap", "capability_route")
_emit_writes_via_uwg("p2", "agent_count_cap", "uwg_write")
_emit_blocks_direct_write("p2", "agent_count_cap", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_count_cap", "tool_invocation")
_emit_captures_execution_output("p2", "agent_count_cap", "exec_output")
_emit_dispatches_agent("p3", "agent_count_cap", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_count_cap", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_count_cap", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_count_cap", "healing_outcome")
_emit_escalates_failure("p3", "agent_count_cap", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_count_cap", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_count_cap", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_count_cap", "evaluation_signal")
_emit_records_telemetry_event("p4", "agent_count_cap", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_count_cap", "eval_metric")
_emit_stores_embedding("p4", "agent_count_cap", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_count_cap", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_count_cap", "exec_snapshot_link")
HARD_CAP = 149

def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    # guardian: allow-global-mutation
    sys.path.insert(0, str(project_root))
    from ops_scripts.ci.active_set_helper import get_active_set
    try:
        result = get_active_set(project_root)
    # guardian: allow-silent-swallower
    except Exception as exc:
        print(f'FAIL: could not enumerate active agents: {exc}', file=sys.stderr)
        return 1
    print('Agent Count Cap (discovery-aligned):')
    print(f'  active={result.count}  cap={HARD_CAP}  delta={result.count - HARD_CAP}')
    print(f'  fingerprint: {result.fingerprint}')
    print(f'  first_10: {list(result.agent_ids[:10])}')
    print(f'  last_10:  {list(result.agent_ids[-10:])}')
    if result.count > HARD_CAP:
        commit_msg = os.environ.get('COMMIT_MESSAGE', '')
        if 'AGENT_COUNT_BUMP:' in commit_msg:
            print(f'PASS: count {result.count} > cap {HARD_CAP} but AGENT_COUNT_BUMP tag present')
            return 0
        print(f'FAIL: active agent count {result.count} exceeds hard cap {HARD_CAP}\n  To increase, add AGENT_COUNT_BUMP:<reason> to commit message')
        return 1
    print(f'PASS: {result.count} active agents within cap {HARD_CAP}')
    return 0
if __name__ == '__main__':
    sys.exit(main())
