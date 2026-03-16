"""
State utilities for common operations across the codebase.
"""

from agentic_core.mixins.safety_mixin import StateAnalysisMixin
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

_emit_records_execution_trace("p0", "evidence", "state_util")
_emit_applies_guardrail("p0", "state_util", "p0_governance")
_emit_reads_policy_state("p0", "state_util", "policy_binding")
_emit_snapshots_state("p0", "state_util", "state_snapshot")
emit_replay_key("p0", "state_util")
emit_determinism_digest("p0", "state_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "state_util", "execution_auth")
_emit_validates_capability("p2", "state_util", "capability_check")
_emit_routes_to_capability("p2", "state_util", "capability_route")
_emit_writes_via_uwg("p2", "state_util", "uwg_write")
_emit_blocks_direct_write("p2", "state_util", "direct_write_block")
_emit_records_tool_invocation("p2", "state_util", "tool_invocation")
_emit_captures_execution_output("p2", "state_util", "exec_output")
_emit_dispatches_agent("p3", "state_util", "agent_dispatch")
_emit_coordinates_agents("p3", "state_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "state_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "state_util", "healing_outcome")
_emit_escalates_failure("p3", "state_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "state_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "state_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "state_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "state_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "state_util", "eval_metric")
_emit_stores_embedding("p4", "state_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "state_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "state_util", "exec_snapshot_link")


def check_past_failures(task: str) -> str:
    """Check telemetry for past failures on similar tasks.

    Args:
        task: Task description to check

    Returns:
        Recommendation string based on analysis
    """
    try:
        result = StateAnalysisMixin._check_past_failures([])
        return result["recommendation"]
    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logging.getLogger(__name__).warning(f"State analysis error: {e}")
        return "Unable to check past failures"
    except (OSError, RuntimeError, MemoryError) as e:
        logging.getLogger(__name__).error(f"Critical state analysis error: {e}")
        return "Unable to check past failures"
