"""Tests for UniversalWriteGateway hard-blocking behavior.

Phase 3: UWG Runtime Blocking — L2 [UWG], Guarantee #6.
Verifies that write_file/append_file/delete_file/rename_file raise ToolNotAllowedError
on blocked paths/extensions (live mode) and return SimulationResult in replay_mode.
"""

from __future__ import annotations

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_uwg_hard_block")
# REMOVED: _emit_applies_guardrail("p0", "test_uwg_hard_block", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_uwg_hard_block", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_uwg_hard_block", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_uwg_hard_block")
# REMOVED: emit_determinism_digest("p0", "test_uwg_hard_block")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_uwg_hard_block", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_uwg_hard_block", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_uwg_hard_block", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_uwg_hard_block", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_uwg_hard_block", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_uwg_hard_block", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_uwg_hard_block", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_uwg_hard_block", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_uwg_hard_block", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_uwg_hard_block", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_uwg_hard_block", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_uwg_hard_block", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_uwg_hard_block", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_uwg_hard_block", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_uwg_hard_block", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_uwg_hard_block", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_uwg_hard_block", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_uwg_hard_block", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_uwg_hard_block", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_uwg_hard_block", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.UniversalWriteGateway import (
    MutationRecord,
    SimulationResult,
    ToolNotAllowedError,
    UniversalWriteGateway,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_uwg_hard_block", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_uwg_hard_block", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_uwg_hard_block", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_uwg_hard_block", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_uwg_hard_block", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_uwg_hard_block", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_uwg_hard_block", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_uwg_hard_block", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_uwg_hard_block", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_uwg_hard_block", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_uwg_hard_block", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_uwg_hard_block", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_uwg_hard_block", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_uwg_hard_block", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_uwg_hard_block", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_uwg_hard_block", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_uwg_hard_block", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_uwg_hard_block", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_uwg_hard_block", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_uwg_hard_block", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_uwg_hard_block", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_uwg_hard_block", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_uwg_hard_block", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_uwg_hard_block", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_uwg_hard_block", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_uwg_hard_block", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_uwg_hard_block", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_uwg_hard_block", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_uwg_hard_block", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_uwg_hard_block", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_uwg_hard_block", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_uwg_hard_block", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_uwg_hard_block", "write_through")
# REMOVED: _emit_writes_through("p1", "test_uwg_hard_block", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_uwg_hard_block", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_uwg_hard_block", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_uwg_hard_block", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_uwg_hard_block", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_uwg_hard_block", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_uwg_hard_block", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_uwg_hard_block", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_uwg_hard_block", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_uwg_hard_block", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_uwg_hard_block", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_uwg_hard_block", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_uwg_hard_block", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_uwg_hard_block", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_uwg_hard_block", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_uwg_hard_block")
# REMOVED: _emit_gated_by_confidence("p1", "test_uwg_hard_block", "confidence_gate")


class TestWriteFileHardBlock:
    def test_blocked_extension_raises(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            gw.write_file("some/path/module.py", b"print('hello')")

    def test_blocked_js_extension_raises(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            gw.write_file("src/app.js", b"console.log('hi')")

    def test_blocked_path_not_in_allowed_set_raises(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            gw.write_file("secret/config.json", b"{}")

    def test_allowed_path_succeeds(self):
        gw = UniversalWriteGateway(replay_mode=False)
        result = gw.write_file("artifacts/output.json", b'{"key": "value"}')
        assert isinstance(result, MutationRecord)
        assert result.permitted is True
        assert result.operation == "write"

    def test_replay_mode_returns_simulation_result(self):
        gw = UniversalWriteGateway(replay_mode=True)
        result = gw.write_file("some/path/module.py", b"print('hello')")
        assert isinstance(result, SimulationResult)
        assert result.replay_mode is True
        assert result.operation == "write"

    def test_blocked_write_recorded_in_ledger(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError):
            gw.write_file("src/evil.py", b"pass")
        ledger = gw.get_mutation_ledger()
        assert len(ledger) == 1
        assert ledger[0].permitted is False
        assert ledger[0].operation == "write"


class TestAppendFileHardBlock:
    def test_blocked_extension_raises(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            gw.append_file("core/engine.py", b"# extra")

    def test_allowed_path_succeeds(self):
        gw = UniversalWriteGateway(replay_mode=False)
        result = gw.append_file("logs/run.log", b"line\n")
        assert isinstance(result, MutationRecord)
        assert result.permitted is True

    def test_replay_mode_returns_simulation_result(self):
        gw = UniversalWriteGateway(replay_mode=True)
        result = gw.append_file("core/engine.py", b"# extra")
        assert isinstance(result, SimulationResult)
        assert result.operation == "append"


class TestDeleteFileHardBlock:
    def test_blocked_path_raises(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            gw.delete_file("ops_scripts/ci/scanner.py")

    def test_allowed_path_succeeds(self):
        gw = UniversalWriteGateway(replay_mode=False)
        result = gw.delete_file("artifacts/old_report.json")
        assert isinstance(result, MutationRecord)
        assert result.permitted is True
        assert result.operation == "delete"

    def test_replay_mode_returns_simulation_result(self):
        gw = UniversalWriteGateway(replay_mode=True)
        result = gw.delete_file("ops_scripts/ci/scanner.py")
        assert isinstance(result, SimulationResult)
        assert result.operation == "delete"


class TestRenameFileHardBlock:
    def test_blocked_src_raises(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            gw.rename_file("src/bad.py", "artifacts/moved.py")

    def test_blocked_dst_raises(self):
        gw = UniversalWriteGateway(replay_mode=False)
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            gw.rename_file("artifacts/ok.json", "src/bad.py")

    def test_replay_mode_returns_simulation_result(self):
        gw = UniversalWriteGateway(replay_mode=True)
        result = gw.rename_file("src/bad.py", "artifacts/moved.json")
        assert isinstance(result, SimulationResult)
        assert result.operation == "rename"
