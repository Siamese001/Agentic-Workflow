"""
ops_scripts/dev_tools/l0_scripts/maintenance_generate_hooks_util.py
-----------------------------------------------------------------
DEPRECATED: Redirects to the unified 'generate_hooks.py' script.
This file is retained as a stub to prevent breaking existing automation
that calls this specific path.
"""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "maintenance_generate_hooks_util")
_emit_applies_guardrail("p0", "maintenance_generate_hooks_util", "p0_governance")
_emit_reads_policy_state("p0", "maintenance_generate_hooks_util", "policy_binding")
_emit_snapshots_state("p0", "maintenance_generate_hooks_util", "state_snapshot")
emit_replay_key("p0", "maintenance_generate_hooks_util")
emit_determinism_digest("p0", "maintenance_generate_hooks_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "maintenance_generate_hooks_util", "execution_auth")
_emit_validates_capability("p2", "maintenance_generate_hooks_util", "capability_check")
_emit_routes_to_capability("p2", "maintenance_generate_hooks_util", "capability_route")
_emit_writes_via_uwg("p2", "maintenance_generate_hooks_util", "uwg_write")
_emit_blocks_direct_write("p2", "maintenance_generate_hooks_util", "direct_write_block")
_emit_records_tool_invocation("p2", "maintenance_generate_hooks_util", "tool_invocation")
_emit_captures_execution_output("p2", "maintenance_generate_hooks_util", "exec_output")
_emit_dispatches_agent("p3", "maintenance_generate_hooks_util", "agent_dispatch")
_emit_coordinates_agents("p3", "maintenance_generate_hooks_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "maintenance_generate_hooks_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "maintenance_generate_hooks_util", "healing_outcome")
_emit_escalates_failure("p3", "maintenance_generate_hooks_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "maintenance_generate_hooks_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "maintenance_generate_hooks_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "maintenance_generate_hooks_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "maintenance_generate_hooks_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "maintenance_generate_hooks_util", "eval_metric")
_emit_stores_embedding("p4", "maintenance_generate_hooks_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "maintenance_generate_hooks_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "maintenance_generate_hooks_util", "exec_snapshot_link")
project_root = Path(__file__).resolve().parent.parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from agentic_core.L0_routing.scripts.generate_hooks import generate_sovereign_list, sync_pre_commit

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Sync pre-commit config with SSOT (Redirect)')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--list', action='store_true', help='List current sovereign roots')
    args = parser.parse_args()
    print('[*] maintenance_generate_hooks_util.py is DEPRECATED. Redirecting to generate_hooks.py...')
    if args.list:
        generate_sovereign_list()
    else:
        success = sync_pre_commit(dry_run=args.dry_run)
        sys.exit(0 if success else 1)
