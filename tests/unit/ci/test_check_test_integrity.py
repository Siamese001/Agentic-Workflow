"""Tests for Gate B: check_test_integrity.py AST scanner."""

from __future__ import annotations

import textwrap
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "test_check_test_integrity")
_emit_applies_guardrail("p0", "test_check_test_integrity", "p0_governance")
_emit_reads_policy_state("p0", "test_check_test_integrity", "policy_binding")
_emit_snapshots_state("p0", "test_check_test_integrity", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_check_test_integrity", "p4obs", "metric_1")
_emit_emits_metric_event("test_check_test_integrity", "p4obs", "metric_2")
_emit_emits_metric_event("test_check_test_integrity", "p4obs", "metric_3")
_emit_emits_metric_event("test_check_test_integrity", "p4obs", "metric_4")
_emit_emits_metric_event("test_check_test_integrity", "p4obs", "metric_5")
_emit_emits_metric_event("test_check_test_integrity", "p4obs", "metric_6")
_emit_records_incident_event("test_check_test_integrity", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_check_test_integrity", "p4obs", "anomaly")
_emit_writes_observability_log("test_check_test_integrity", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_check_test_integrity", "p4obs", "mon_state")
_emit_triggers_alert("test_check_test_integrity", "p4obs", "alert")
_emit_links_incident_trace("test_check_test_integrity", "p4obs", "trace_link")
_emit_captures_pattern("test_check_test_integrity", "p3lm", "pattern")
_emit_records_learning_event("test_check_test_integrity", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_check_test_integrity", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_check_test_integrity", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_check_test_integrity", "p3lm", "routing")
_emit_improves_agent_policy("test_check_test_integrity", "p3lm", "policy")
_emit_stores_learning_state("test_check_test_integrity", "p3lm", "state")
_emit_records_execution_trace("test_check_test_integrity", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_check_test_integrity", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_check_test_integrity", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_check_test_integrity", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_check_test_integrity", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_check_test_integrity", "env_read", "p2_env_1")
_emit_reads_environ("test_check_test_integrity", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_check_test_integrity", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_check_test_integrity", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_check_test_integrity", "context_pull")
_emit_pulls_context("p1", "test_check_test_integrity", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_check_test_integrity", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_check_test_integrity", "uwg_term_2")
_emit_writes_through("p1", "test_check_test_integrity", "write_through")
_emit_writes_through("p1", "test_check_test_integrity", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_check_test_integrity", "safety_validation")
_emit_invokes_eval("p1", "test_check_test_integrity", "eval_call")
_emit_proposal_commits_routing("p1", "test_check_test_integrity", "routing_commit")
emit_replay_key("p0", "test_check_test_integrity")
emit_determinism_digest("p0", "test_check_test_integrity")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_check_test_integrity", "execution_auth")
_emit_validates_capability("p2", "test_check_test_integrity", "capability_check")
_emit_routes_to_capability("p2", "test_check_test_integrity", "capability_route")
_emit_writes_via_uwg("p2", "test_check_test_integrity", "uwg_write")
_emit_blocks_direct_write("p2", "test_check_test_integrity", "direct_write_block")
_emit_records_tool_invocation("p2", "test_check_test_integrity", "tool_invocation")
_emit_captures_execution_output("p2", "test_check_test_integrity", "exec_output")
_emit_dispatches_agent("p3", "test_check_test_integrity", "agent_dispatch")
_emit_coordinates_agents("p3", "test_check_test_integrity", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_check_test_integrity", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_check_test_integrity", "healing_outcome")
_emit_escalates_failure("p3", "test_check_test_integrity", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_check_test_integrity", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_check_test_integrity", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_check_test_integrity", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_check_test_integrity", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_check_test_integrity", "eval_metric")
_emit_stores_embedding("p4", "test_check_test_integrity", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_check_test_integrity", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_check_test_integrity", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def _write_temp_test(tmp_path: Path, content: str) -> Path:
    f = tmp_path / "test_sample.py"
    f.write_text(textwrap.dedent(content), encoding="utf-8")
    return f


class TestCheckTestIntegritySilentSwallower:
    def test_no_violations_on_clean_test(self, tmp_path):
        from ops_scripts.ci.check_test_integrity import scan_file

        f = _write_temp_test(
            tmp_path,
            """
            def test_something():
                assert 1 + 1 == 2
        """,
        )
        assert scan_file(f) == []

    def test_flags_assertion_less_test(self, tmp_path):
        from ops_scripts.ci.check_test_integrity import scan_file

        f = _write_temp_test(
            tmp_path,
            """
            def test_no_asserts():
                x = 1 + 1
        """,
        )
        violations = scan_file(f)
        assert any("zero assert" in v[1] for v in violations)

    def test_flags_xfail_without_strict(self, tmp_path):
        from ops_scripts.ci.check_test_integrity import scan_file

        f = _write_temp_test(
            tmp_path,
            """
            import pytest

            @pytest.mark.xfail
            def test_xfail_no_strict():
                assert False
        """,
        )
        violations = scan_file(f)
        assert any("strict=True" in v[1] for v in violations)

    def test_xfail_with_strict_passes(self, tmp_path):
        from ops_scripts.ci.check_test_integrity import scan_file

        f = _write_temp_test(
            tmp_path,
            """
            import pytest

            @pytest.mark.xfail(strict=True, reason="linked_issue: #42")
            def test_xfail_strict():
                assert False
        """,
        )
        violations = scan_file(f)
        xfail_violations = [v for v in violations if "strict" in v[1]]
        assert xfail_violations == []


class TestCheckTestIntegrityMain:
    def test_main_returns_0_on_clean_dir(self, tmp_path):
        from ops_scripts.ci.check_test_integrity import main

        clean_test = tmp_path / "test_clean.py"
        clean_test.write_text("def test_ok():\n    assert True\n", encoding="utf-8")
        result = main([str(tmp_path)])
        assert result == 0

    def test_main_returns_1_on_violations(self, tmp_path):
        from ops_scripts.ci.check_test_integrity import main

        bad_test = tmp_path / "test_bad.py"
        bad_test.write_text("def test_noop():\n    pass\n", encoding="utf-8")
        result = main([str(tmp_path)])
        assert result == 1
