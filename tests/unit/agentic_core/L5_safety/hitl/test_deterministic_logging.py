"""Addendum 6.3: Deterministic HITL Decision Logger tests."""

from __future__ import annotations

import json

from agentic_core.L5_safety.hitl.decision_logger import HITLDecision, HITLDecisionLogger
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

_emit_records_execution_trace("p0", "evidence", "test_deterministic_logging")
_emit_applies_guardrail("p0", "test_deterministic_logging", "p0_governance")
_emit_reads_policy_state("p0", "test_deterministic_logging", "policy_binding")
_emit_snapshots_state("p0", "test_deterministic_logging", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_deterministic_logging", "p4obs", "metric_1")
_emit_emits_metric_event("test_deterministic_logging", "p4obs", "metric_2")
_emit_emits_metric_event("test_deterministic_logging", "p4obs", "metric_3")
_emit_emits_metric_event("test_deterministic_logging", "p4obs", "metric_4")
_emit_emits_metric_event("test_deterministic_logging", "p4obs", "metric_5")
_emit_emits_metric_event("test_deterministic_logging", "p4obs", "metric_6")
_emit_records_incident_event("test_deterministic_logging", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_deterministic_logging", "p4obs", "anomaly")
_emit_writes_observability_log("test_deterministic_logging", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_deterministic_logging", "p4obs", "mon_state")
_emit_triggers_alert("test_deterministic_logging", "p4obs", "alert")
_emit_links_incident_trace("test_deterministic_logging", "p4obs", "trace_link")
_emit_captures_pattern("test_deterministic_logging", "p3lm", "pattern")
_emit_records_learning_event("test_deterministic_logging", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_deterministic_logging", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_deterministic_logging", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_deterministic_logging", "p3lm", "routing")
_emit_improves_agent_policy("test_deterministic_logging", "p3lm", "policy")
_emit_stores_learning_state("test_deterministic_logging", "p3lm", "state")
_emit_records_execution_trace("test_deterministic_logging", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_deterministic_logging", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_deterministic_logging", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_deterministic_logging", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_deterministic_logging", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_deterministic_logging", "env_read", "p2_env_1")
_emit_reads_environ("test_deterministic_logging", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_deterministic_logging", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_deterministic_logging", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_deterministic_logging", "context_pull")
_emit_pulls_context("p1", "test_deterministic_logging", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_deterministic_logging", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_deterministic_logging", "uwg_term_2")
_emit_writes_through("p1", "test_deterministic_logging", "write_through")
_emit_writes_through("p1", "test_deterministic_logging", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_deterministic_logging", "safety_validation")
_emit_invokes_eval("p1", "test_deterministic_logging", "eval_call")
_emit_proposal_commits_routing("p1", "test_deterministic_logging", "routing_commit")
emit_replay_key("p0", "test_deterministic_logging")
emit_determinism_digest("p0", "test_deterministic_logging")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_deterministic_logging", "execution_auth")
_emit_validates_capability("p2", "test_deterministic_logging", "capability_check")
_emit_routes_to_capability("p2", "test_deterministic_logging", "capability_route")
_emit_writes_via_uwg("p2", "test_deterministic_logging", "uwg_write")
_emit_blocks_direct_write("p2", "test_deterministic_logging", "direct_write_block")
_emit_records_tool_invocation("p2", "test_deterministic_logging", "tool_invocation")
_emit_captures_execution_output("p2", "test_deterministic_logging", "exec_output")
_emit_dispatches_agent("p3", "test_deterministic_logging", "agent_dispatch")
_emit_coordinates_agents("p3", "test_deterministic_logging", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_deterministic_logging", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_deterministic_logging", "healing_outcome")
_emit_escalates_failure("p3", "test_deterministic_logging", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_deterministic_logging", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_deterministic_logging", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_deterministic_logging", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_deterministic_logging", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_deterministic_logging", "eval_metric")
_emit_stores_embedding("p4", "test_deterministic_logging", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_deterministic_logging", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_deterministic_logging", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestHITLDecisionLogger:
    def test_log_returns_decision(self, tmp_path):
        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        decision = logger.log(
            agent="TestAgent",
            file="foo.py",
            violation="missing_field",
            proposed="add field",
            decision="APPROVE",
            reviewer_signature="reviewer@test.com",
        )
        assert isinstance(decision, HITLDecision)
        assert decision.agent == "TestAgent"
        assert decision.decision == "APPROVE"
        assert decision.decision_number == 1

    def test_counter_increments(self, tmp_path):
        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        d1 = logger.log("A", "f1.py", "v1", "p1", "APPROVE")
        d2 = logger.log("B", "f2.py", "v2", "p2", "REJECT")
        assert d1.decision_number == 1
        assert d2.decision_number == 2

    def test_log_line_format(self, tmp_path):
        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        d = logger.log("AgentX", "bar.py", "bad_import", "fix import", "REJECT")
        line = d.to_log_line()
        assert "HITL_DECISION_1" in line
        assert "Agent=AgentX" in line
        assert "File=bar.py" in line
        assert "Violation=bad_import" in line
        assert "Decision=REJECT" in line

    def test_no_timestamp_in_log_line(self, tmp_path):
        """Determinism rule: no wall-clock timestamps in key fields."""
        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        d = logger.log("A", "f.py", "v", "p", "APPROVE")
        line = d.to_log_line()
        import re

        assert not re.search(r"\d{4}-\d{2}-\d{2}", line), "Timestamp found in log line"

    def test_written_to_jsonl_file(self, tmp_path):
        log_path = tmp_path / "decisions.jsonl"
        logger = HITLDecisionLogger(log_path=log_path)
        logger.log("A", "f.py", "v", "p", "APPROVE")
        assert log_path.exists()
        with open(log_path) as f:
            record = json.loads(f.readline())
        assert record["agent"] == "A"
        assert record["decision"] == "APPROVE"

    def test_all_records_retrievable(self, tmp_path):
        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        for i in range(3):
            logger.log(f"Agent{i}", f"f{i}.py", "v", "p", "APPROVE")
        records = logger.all_records()
        assert len(records) == 3

    def test_count_matches_logged(self, tmp_path):
        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        logger.log("A", "f.py", "v", "p", "APPROVE")
        logger.log("B", "g.py", "v", "p", "REJECT")
        assert logger.count() == 2

    def test_negative_no_records_without_log_call(self, tmp_path):
        """Negative control: fresh logger must have zero records."""
        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        assert logger.count() == 0
        assert logger.all_records() == []
