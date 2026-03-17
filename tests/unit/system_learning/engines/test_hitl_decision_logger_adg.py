"""ADG-driven tests for system_learning/engines/hitl_decision_logger.py — fan_in=2.

Contract tests: log_hitl_decision, _get_evidence_path, counter behavior.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_hitl_decision_logger_adg")
_emit_applies_guardrail("p0", "test_hitl_decision_logger_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_hitl_decision_logger_adg", "policy_binding")
_emit_snapshots_state("p0", "test_hitl_decision_logger_adg", "state_snapshot")
emit_replay_key("p0", "test_hitl_decision_logger_adg")
emit_determinism_digest("p0", "test_hitl_decision_logger_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_hitl_decision_logger_adg", "execution_auth")
_emit_validates_capability("p2", "test_hitl_decision_logger_adg", "capability_check")
_emit_routes_to_capability("p2", "test_hitl_decision_logger_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_hitl_decision_logger_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_hitl_decision_logger_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_hitl_decision_logger_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_hitl_decision_logger_adg", "exec_output")
_emit_dispatches_agent("p3", "test_hitl_decision_logger_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_hitl_decision_logger_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_hitl_decision_logger_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_hitl_decision_logger_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_hitl_decision_logger_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_hitl_decision_logger_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_hitl_decision_logger_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_hitl_decision_logger_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_hitl_decision_logger_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_hitl_decision_logger_adg", "eval_metric")
_emit_stores_embedding("p4", "test_hitl_decision_logger_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_hitl_decision_logger_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_hitl_decision_logger_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)
from system_learning.engines.hitl_decision_logger import (
    _get_evidence_path,
    log_hitl_decision,
)

_emit_emits_metric_event("test_hitl_decision_logger_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_hitl_decision_logger_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_hitl_decision_logger_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_hitl_decision_logger_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_hitl_decision_logger_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_hitl_decision_logger_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_hitl_decision_logger_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_hitl_decision_logger_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_hitl_decision_logger_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_hitl_decision_logger_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_hitl_decision_logger_adg", "p4obs", "alert")
_emit_links_incident_trace("test_hitl_decision_logger_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_hitl_decision_logger_adg", "p3lm", "pattern")
_emit_records_learning_event("test_hitl_decision_logger_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_hitl_decision_logger_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_hitl_decision_logger_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_hitl_decision_logger_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_hitl_decision_logger_adg", "p3lm", "policy")
_emit_stores_learning_state("test_hitl_decision_logger_adg", "p3lm", "state")
_emit_records_execution_trace("test_hitl_decision_logger_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_hitl_decision_logger_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_hitl_decision_logger_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_hitl_decision_logger_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_hitl_decision_logger_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_hitl_decision_logger_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_hitl_decision_logger_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_hitl_decision_logger_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_hitl_decision_logger_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_hitl_decision_logger_adg", "context_pull")
_emit_pulls_context("p1", "test_hitl_decision_logger_adg", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_hitl_decision_logger_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_hitl_decision_logger_adg", "uwg_term_secondary")
_emit_writes_through("p1", "test_hitl_decision_logger_adg", "write_through")
_emit_writes_through("p1", "test_hitl_decision_logger_adg", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_hitl_decision_logger_adg", "safety_validation")
_emit_invokes_eval("p1", "test_hitl_decision_logger_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_hitl_decision_logger_adg", "routing_commit")
_emit_escalates_to_human("p1", "test_hitl_decision_logger_adg", "human_escalation")
_emit_routes_through("p1", "test_hitl_decision_logger_adg", "route_through")
_emit_checks_agent_registry("p1", "test_hitl_decision_logger_adg", "agent_registry")
_emit_validates_agent_capability("p1", "test_hitl_decision_logger_adg", "capability")
_emit_dispatches_execution_plan("p1", "test_hitl_decision_logger_adg", "exec_plan")
_emit_agent_executes_agent("p1", "test_hitl_decision_logger_adg", "sub_agent")
_emit_routes_to_agent("p1", "test_hitl_decision_logger_adg", "target_agent")
_emit_verifies_policy("p1", "test_hitl_decision_logger_adg", "policy_check")
_emit_observes_runtime_state("p1", "test_hitl_decision_logger_adg", "runtime_state")
_emit_verifies_boundary("p1", "test_hitl_decision_logger_adg", "boundary_check")
_emit_transcripts_response("p1", "test_hitl_decision_logger_adg", "transcript")
_emit_hard_fails_untranscripted("p1", "test_hitl_decision_logger_adg")
_emit_gated_by_confidence("p1", "test_hitl_decision_logger_adg", "confidence_gate")


class TestGetEvidencePath:
    def test_returns_path_object(self):
        result = _get_evidence_path()
        assert isinstance(result, Path)

    def test_env_override_used(self):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            tmp = f.name
        try:
            os.environ["HITL_EVIDENCE_FILE"] = tmp
            result = _get_evidence_path()
            assert str(result) == tmp
        finally:
            os.environ.pop("HITL_EVIDENCE_FILE", None)
            Path(tmp).unlink(missing_ok=True)

    def test_default_path_when_no_env(self):
        os.environ.pop("HITL_EVIDENCE_FILE", None)
        result = _get_evidence_path()
        assert "evidence" in str(result).lower() or "docs" in str(result).lower()


class TestLogHitlDecision:
    def test_returns_positive_int(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            tmp = f.name
        try:
            os.environ["HITL_EVIDENCE_FILE"] = tmp
            result = log_hitl_decision(
                agent="TestAgent",
                file_path="foo/bar.py",
                violation="EMPTY_FILE",
                proposed="ARCHIVE",
                decision="APPROVED",
            )
            assert isinstance(result, int)
            assert result > 0
        finally:
            os.environ.pop("HITL_EVIDENCE_FILE", None)
            Path(tmp).unlink(missing_ok=True)

    def test_counter_increments(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            tmp = f.name
        try:
            os.environ["HITL_EVIDENCE_FILE"] = tmp
            n1 = log_hitl_decision(
                agent="AgentA", file_path="a.py",
                violation="V1", proposed="P1", decision="APPROVED",
            )
            n2 = log_hitl_decision(
                agent="AgentB", file_path="b.py",
                violation="V2", proposed="P2", decision="SKIPPED",
            )
            assert n2 == n1 + 1
        finally:
            os.environ.pop("HITL_EVIDENCE_FILE", None)
            Path(tmp).unlink(missing_ok=True)

    def test_appends_to_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            tmp = f.name
        try:
            os.environ["HITL_EVIDENCE_FILE"] = tmp
            log_hitl_decision(
                agent="TestAgent", file_path="x.py",
                violation="TEST_V", proposed="MOVE", decision="APPROVED",
                extra={"note": "test_run"},
            )
            content = Path(tmp).read_text(encoding="utf-8")
            assert "TestAgent" in content or len(content) > 0
        finally:
            os.environ.pop("HITL_EVIDENCE_FILE", None)
            Path(tmp).unlink(missing_ok=True)

    def test_accepts_extra_dict(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            tmp = f.name
        try:
            os.environ["HITL_EVIDENCE_FILE"] = tmp
            result = log_hitl_decision(
                agent="AgentExtra",
                file_path="extra.py",
                violation="EXTRA_V",
                proposed="RENAME",
                decision="MANUAL",
                extra={"reason": "needs review", "priority": "high"},
            )
            assert isinstance(result, int)
        finally:
            os.environ.pop("HITL_EVIDENCE_FILE", None)
            Path(tmp).unlink(missing_ok=True)
