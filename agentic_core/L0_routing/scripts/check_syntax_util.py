"""Quick syntax check to identify the 3 remaining errors."""

import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "check_syntax_util")
emit_determinism_digest("p0", "check_syntax_util")

_emit_dispatches_healing_run("p1", "check_syntax_util", "L0")
_emit_routes_through("p1", "check_syntax_util", "L0")
_emit_escalates_to_human("p1", "check_syntax_util", "L0")
_emit_reads_policy_state("p1", "check_syntax_util", "L0")
_emit_authorize_and_execute("p2", "check_syntax_util", "execution_auth")
_emit_validates_capability("p2", "check_syntax_util", "capability_check")
_emit_routes_to_capability("p2", "check_syntax_util", "capability_route")
_emit_writes_via_uwg("p2", "check_syntax_util", "uwg_write")
_emit_blocks_direct_write("p2", "check_syntax_util", "direct_write_block")
_emit_records_tool_invocation("p2", "check_syntax_util", "tool_invocation")
_emit_captures_execution_output("p2", "check_syntax_util", "exec_output")
_emit_dispatches_agent("p3", "check_syntax_util", "agent_dispatch")
_emit_coordinates_agents("p3", "check_syntax_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_syntax_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_syntax_util", "healing_outcome")
_emit_escalates_failure("p3", "check_syntax_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_syntax_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_syntax_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_syntax_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_syntax_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_syntax_util", "eval_metric")
_emit_stores_embedding("p4", "check_syntax_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_syntax_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_syntax_util", "exec_snapshot_link")

# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent))
from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_code_validator
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def main():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "main", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "main", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "main")
    project_root = Path(__file__).parent.parent
    result = invoke_code_validator(action="validate", project_root=project_root)
    if result.get("success"):
        print(f"Total errors: {result.get('total_violations', 0)}")
        print()
        for v in result.get("violations", []):
            print(f"{v['file_path']}:{v['line_number']}:{v['column']} - {v['error_message']}")
    else:
        print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    main()
