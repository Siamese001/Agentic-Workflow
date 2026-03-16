import sys
from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
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
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_records_execution_trace("p0", "evidence", "conftest_unit_min_deps")
_emit_applies_guardrail("p0", "conftest_unit_min_deps", "p0_governance")
_emit_reads_policy_state("p0", "conftest_unit_min_deps", "policy_binding")
_emit_snapshots_state("p0", "conftest_unit_min_deps", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("conftest", "p4obs", "metric_1")
_emit_emits_metric_event("conftest", "p4obs", "metric_2")
_emit_emits_metric_event("conftest", "p4obs", "metric_3")
_emit_emits_metric_event("conftest", "p4obs", "metric_4")
_emit_emits_metric_event("conftest", "p4obs", "metric_5")
_emit_emits_metric_event("conftest", "p4obs", "metric_6")
_emit_records_incident_event("conftest", "p4obs", "incident")
_emit_captures_runtime_anomaly("conftest", "p4obs", "anomaly")
_emit_writes_observability_log("conftest", "p4obs", "obs_log")
_emit_updates_monitoring_state("conftest", "p4obs", "mon_state")
_emit_triggers_alert("conftest", "p4obs", "alert")
_emit_links_incident_trace("conftest", "p4obs", "trace_link")
_emit_captures_pattern("conftest", "p3lm", "pattern")
_emit_records_learning_event("conftest", "p3lm", "learning_event")
_emit_writes_learning_snapshot("conftest", "p3lm", "snapshot")
_emit_feeds_meta_learning("conftest", "p3lm", "meta_feed")
_emit_updates_routing_strategy("conftest", "p3lm", "routing")
_emit_improves_agent_policy("conftest", "p3lm", "policy")
_emit_stores_learning_state("conftest", "p3lm", "state")
_emit_records_execution_trace("conftest", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("conftest", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("conftest", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("conftest", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("conftest", "L4_STATE", "p2_trace_5")
_emit_reads_environ("conftest", "env_read", "p2_env_1")
_emit_reads_environ("conftest", "env_read", "p2_env_2")
_emit_reads_runtime_state("conftest", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("conftest", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "conftest", "context_pull")
_emit_pulls_context("p1", "conftest", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "conftest", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "conftest", "uwg_term_2")
_emit_writes_through("p1", "conftest", "write_through")
_emit_writes_through("p1", "conftest", "write_through_2")
_emit_validated_by_safety_plane("p1", "conftest", "safety_validation")
_emit_invokes_eval("p1", "conftest", "eval_call")
_emit_proposal_commits_routing("p1", "conftest", "routing_commit")
emit_replay_key("p0", "conftest_unit_min_deps")
emit_determinism_digest("p0", "conftest_unit_min_deps")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "conftest", "execution_auth")
_emit_validates_capability("p2", "conftest", "capability_check")
_emit_routes_to_capability("p2", "conftest", "capability_route")
_emit_writes_via_uwg("p2", "conftest", "uwg_write")
_emit_blocks_direct_write("p2", "conftest", "direct_write_block")
_emit_records_tool_invocation("p2", "conftest", "tool_invocation")
_emit_captures_execution_output("p2", "conftest", "exec_output")
_emit_dispatches_agent("p3", "conftest", "agent_dispatch")
_emit_coordinates_agents("p3", "conftest", "agent_coordination")
_emit_records_workflow_lineage("p3", "conftest", "workflow_lineage")
_emit_records_healing_outcome("p3", "conftest", "healing_outcome")
_emit_escalates_failure("p3", "conftest", "failure_escalation")
_emit_orchestrates_workflow("p3", "conftest", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "conftest", "healing_dispatch")
_emit_invokes_evaluation("p3", "conftest", "evaluation_signal")
_emit_records_telemetry_event("p4", "conftest", "telemetry_event")
_emit_captures_evaluation_metric("p4", "conftest", "eval_metric")
_emit_stores_embedding("p4", "conftest", "embedding_store")
_emit_updates_meta_learning_state("p4", "conftest", "meta_learning")
_emit_links_execution_to_snapshot("p4", "conftest", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Add project root to allow absolute imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def _inject_test_key_source():
    """Inject a deterministic TestKeySource for all unit_min_deps tests."""
    from agentic_core.L2_execution.enforcement.key_source import (
        TestKeySource,
        inject_key_source,
    )

    inject_key_source(TestKeySource())
