"""
Regression tests for tools/adg/drift_lifecycle.py

All tests use mocks and stubs — no live Redis, no live MetaLearningBus,
no live filesystem writes.  38 tests total.
"""

from __future__ import annotations

import json
import time
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Module under test
# ---------------------------------------------------------------------------
import tools.adg.drift_lifecycle as lifecycle
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_authorize_and_execute("p2", "test_drift_lifecycle", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_drift_lifecycle", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_drift_lifecycle", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_drift_lifecycle", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_drift_lifecycle", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_drift_lifecycle", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_drift_lifecycle", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_drift_lifecycle", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_drift_lifecycle", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_drift_lifecycle", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_drift_lifecycle", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_drift_lifecycle", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_drift_lifecycle", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_drift_lifecycle", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_drift_lifecycle", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_drift_lifecycle", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_drift_lifecycle", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_drift_lifecycle", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_drift_lifecycle", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_drift_lifecycle", "exec_snapshot_link")
from tools.adg.drift_lifecycle import (
    HealResult,
    LifecycleResult,
    WorkItem,
    _build_work_queue,
    _heal_item,
    _heal_orphan_test,
    _heal_uncovered_module,
    _maybe_escalate,
    _read_drift_state,
    _rescore,
    _resolve_test_paths,
    _run_meta_learning_bus,
    _run_scoped_pytest,
    _shape_trace_signal,
    _write_lifecycle_result,
    run_lifecycle,
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_drift_lifecycle")
# REMOVED: _emit_applies_guardrail("p0", "test_drift_lifecycle", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_drift_lifecycle", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_drift_lifecycle", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_drift_lifecycle", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_drift_lifecycle", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_drift_lifecycle", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_drift_lifecycle", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_drift_lifecycle", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_drift_lifecycle", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_drift_lifecycle", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_drift_lifecycle", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_drift_lifecycle", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_drift_lifecycle", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_drift_lifecycle", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_drift_lifecycle", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_drift_lifecycle", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_drift_lifecycle", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_drift_lifecycle", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_drift_lifecycle", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_drift_lifecycle", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_drift_lifecycle", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_drift_lifecycle", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_drift_lifecycle", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_drift_lifecycle", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_drift_lifecycle", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_drift_lifecycle", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_drift_lifecycle", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_drift_lifecycle", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_drift_lifecycle", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_drift_lifecycle", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_drift_lifecycle", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_drift_lifecycle", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_drift_lifecycle", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_drift_lifecycle", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_drift_lifecycle", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_drift_lifecycle", "write_through")
# REMOVED: _emit_writes_through("p1", "test_drift_lifecycle", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_drift_lifecycle", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_drift_lifecycle", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_drift_lifecycle", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_drift_lifecycle", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_drift_lifecycle", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_drift_lifecycle", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_drift_lifecycle", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_drift_lifecycle", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_drift_lifecycle", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_drift_lifecycle", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_drift_lifecycle", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_drift_lifecycle", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_drift_lifecycle", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_drift_lifecycle", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_drift_lifecycle")
# REMOVED: _emit_gated_by_confidence("p1", "test_drift_lifecycle", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_drift_lifecycle")
# REMOVED: emit_determinism_digest("p0", "test_drift_lifecycle")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _mock_redis(data: dict | None = None):
    """Minimal Redis mock with get/hgetall/lrange/smembers/pipeline."""
    r = MagicMock()
    store = data or {}
    r.get.side_effect = lambda k: store.get(k)
    r.hgetall.side_effect = lambda k: store.get(k, {})
    r.lrange.side_effect = lambda k, start, end: store.get(k, [])
    r.smembers.side_effect = lambda k: store.get(k, set())
    pipe = MagicMock()
    pipe.__enter__ = lambda s: s
    pipe.__exit__ = MagicMock(return_value=False)
    pipe.execute.return_value = []
    r.pipeline.return_value = pipe
    return r


def _good_drift_state() -> dict:
    """Typical drift state dict as returned by _read_drift_state."""
    return {
        "composite": 0.749,
        "coverage": 1.0,
        "blast": 0.998,
        "orphan": 0.248,
        "violation": 0.0,
        "prod_total": 2857,
        "test_total": 3165,
        "uncovered_count": 2667,
        "orphan_count": 366,
        "blast_top": [
            {"path": "agentic_core/L5_safety/foo.py", "fan_out": 1146},
            {"path": "agentic_core/L0_routing/bar.py", "fan_out": 500},
        ],
        "uncovered": [
            "agentic_core/L5_safety/foo.py",
            "agentic_core/L0_routing/bar.py",
        ],
        "orphan_tests": ["tests/adg/orphan_test.py"],
        "violation_gaps": [],
        "timestamp": time.time(),
    }


# ---------------------------------------------------------------------------
# Stage 1: _read_drift_state
# ---------------------------------------------------------------------------


class TestReadDriftState:
    def test_raises_when_score_missing(self):
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        r = _mock_redis()
        with pytest.raises(RuntimeError, match="adg:drift:score not found"):
            _read_drift_state(r)

    def test_returns_composite_from_score_key(self):
        r = _mock_redis(
            {
                "adg:drift:score": "0.749062",
                "adg:drift:subscores": {
                    "coverage": "1.0",
                    "blast": "0.998",
                    "orphan": "0.248",
                    "violation": "0.0",
                    "prod_total": "2857",
                    "test_total": "3165",
                    "timestamp": "1000.0",
                },
                "adg:drift:blast_top": [
                    json.dumps({"path": "x.py", "fan_out": 10})
                ],
                "adg:drift:uncovered": ["x.py"],
                "adg:drift:orphan_tests": [],
                "adg:drift:violation_gaps": [],
            }
        )
        state = _read_drift_state(r)
        assert state["composite"] == pytest.approx(0.749062)
        assert state["prod_total"] == 2857
        assert state["blast_top"] == [{"path": "x.py", "fan_out": 10}]
        assert state["uncovered"] == ["x.py"]

    def test_defaults_when_subscores_empty(self):
        r = _mock_redis(
            {
                "adg:drift:score": "0.5",
                "adg:drift:subscores": {},
            }
        )
        state = _read_drift_state(r)
        assert state["coverage"] == pytest.approx(1.0)
        assert state["blast"] == pytest.approx(1.0)
        assert state["orphan"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Stage 2: _shape_trace_signal
# ---------------------------------------------------------------------------


class TestShapeTraceSignal:
    def test_alert_when_above_threshold(self):
        drift = _good_drift_state()
        drift["composite"] = 0.8
        sig = _shape_trace_signal(drift)
        assert sig["final_outcome_class"] == "DRIFT_ALERT"
        assert sig["success"] is False
        assert sig["route_selected"] == "DRIFT_RECONCILE"

    def test_nominal_when_below_threshold(self):
        drift = _good_drift_state()
        drift["composite"] = 0.3
        sig = _shape_trace_signal(drift)
        assert sig["final_outcome_class"] == "DRIFT_NOMINAL"
        assert sig["success"] is True

    def test_groundedness_is_inverted_composite(self):
        drift = _good_drift_state()
        drift["composite"] = 0.6
        sig = _shape_trace_signal(drift)
        assert sig["retrieval_groundedness_score"] == pytest.approx(0.4)

    def test_groundedness_clamps_at_zero(self):
        drift = _good_drift_state()
        drift["composite"] = 1.5
        sig = _shape_trace_signal(drift)
        assert sig["retrieval_groundedness_score"] == 0.0

    def test_no_mutation_no_guardrail_for_scoring(self):
        sig = _shape_trace_signal(_good_drift_state())
        assert sig["mutation_presence"] is False
        assert sig["guardrails_applied"] is False
        assert sig["policy_state_accessed"] is False


# ---------------------------------------------------------------------------
# Stage 3: _run_meta_learning_bus
# ---------------------------------------------------------------------------


class TestRunMetaLearningBus:
    def test_returns_zero_commits_when_bus_unavailable(self):
        with patch.dict("sys.modules", {"system_learning.engines.meta_learning_bus": None}):
            commits, affected = _run_meta_learning_bus({"route_selected": "X"}, 1000)
        assert commits == 0
        assert affected == []

    def test_returns_commit_count_and_affected(self):
        commit = MagicMock()
        commit.affected_components = ("apps_rg/foo.py",)
        bus_result = MagicMock()
        bus_result.commits = [commit]
        bus_result.proposals = []
        bus_result.rejected_proposal_ids = []

        mock_bus_instance = MagicMock()
        mock_bus_instance.process_traces.return_value = bus_result

        mock_bus_cls = MagicMock(return_value=mock_bus_instance)
        mock_config_cls = MagicMock()
        mock_sl = MagicMock()
        mock_sl.MetaLearningBus = mock_bus_cls
        mock_sl.MetaLearningBusConfig = mock_config_cls

        with patch.dict(
            "sys.modules", {"system_learning.engines.meta_learning_bus": mock_sl}
        ):
            commits, affected = _run_meta_learning_bus({"route_selected": "X"}, 1000)

        assert commits == 1
        assert "apps_rg/foo.py" in affected


# ---------------------------------------------------------------------------
# Stage 4: _build_work_queue
# ---------------------------------------------------------------------------


class TestBuildWorkQueue:
    def test_empty_drift_returns_empty(self):
        drift = _good_drift_state()
        drift["blast_top"] = []
        drift["orphan_tests"] = []
        items = _build_work_queue(drift, 0, [], 5)
        assert items == []

    def test_blast_top_fills_queue(self):
        drift = _good_drift_state()
        items = _build_work_queue(drift, 0, [], 5)
        kinds = [i.kind for i in items]
        assert "uncovered_module" in kinds

    def test_bus_affected_takes_priority(self):
        drift = _good_drift_state()
        items = _build_work_queue(drift, 1, ["bus_module.py"], 5)
        assert items[0].path == "bus_module.py"

    def test_budget_limits_items(self):
        drift = _good_drift_state()
        drift["blast_top"] = [{"path": f"mod_{i}.py", "fan_out": i} for i in range(20)]
        items = _build_work_queue(drift, 0, [], 3)
        assert len(items) <= 3

    def test_orphan_tests_appended_when_budget_remains(self):
        drift = _good_drift_state()
        drift["blast_top"] = []
        items = _build_work_queue(drift, 0, [], 5)
        kinds = {i.kind for i in items}
        assert "orphan_test" in kinds

    def test_high_risk_class_for_large_fan_out(self):
        drift = _good_drift_state()
        items = _build_work_queue(drift, 0, [], 10)
        high_risk = [i for i in items if i.fan_out > 100]
        assert all(i.risk_class == "HIGH" for i in high_risk)

    def test_no_duplicate_paths(self):
        drift = _good_drift_state()
        items = _build_work_queue(
            drift,
            1,
            ["agentic_core/L5_safety/foo.py"],  # already in blast_top
            5,
        )
        paths = [i.path for i in items]
        assert len(paths) == len(set(paths))


# ---------------------------------------------------------------------------
# Stage 5: heal helpers
# ---------------------------------------------------------------------------


class TestHealOrphanTest:
    def test_skipped_when_file_not_found(self, tmp_path):
        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            result = _heal_orphan_test("tests/adg/missing.py", dry_run=False)
        assert result.status == "skipped"
        assert "not found" in result.error

    def test_skipped_in_dry_run(self, tmp_path):
        (tmp_path / "tests" / "adg").mkdir(parents=True)
        (tmp_path / "tests" / "adg" / "orphan.py").write_text("")
        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            result = _heal_orphan_test("tests/adg/orphan.py", dry_run=True)
        assert result.status == "skipped"
        assert result.error == "dry_run"

    def test_fixes_by_moving_to_quarantine(self, tmp_path):
        (tmp_path / "tests" / "adg").mkdir(parents=True)
        src = tmp_path / "tests" / "adg" / "orphan.py"
        src.write_text("# orphan")
        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            result = _heal_orphan_test("tests/adg/orphan.py", dry_run=False)
        assert result.status == "fixed"
        assert not src.exists()
        assert (tmp_path / "tests" / "_quarantine" / "orphan.py").exists()


class TestHealUncoveredModule:
    def test_skips_when_stub_already_exists(self, tmp_path):
        stub_dir = tmp_path / "tests" / "unit" / "apps_rg" / "reasoning"
        stub_dir.mkdir(parents=True)
        (stub_dir / "test_MyAgent_adg.py").write_text("")
        r = _mock_redis()
        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            result, path = _heal_uncovered_module(
                r, "apps_rg/reasoning/MyAgent.py", dry_run=False
            )
        assert result.status == "skipped"
        assert "already exists" in result.error

    def test_generates_stub_file(self, tmp_path):
        r = _mock_redis()
        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            result, stub_path = _heal_uncovered_module(
                r, "apps_rg/reasoning/MyAgent.py", dry_run=False
            )
        assert result.status == "fixed"
        assert stub_path is not None
        generated = tmp_path / stub_path
        assert generated.exists()
        content = generated.read_text()
        assert "TestDriftCoverage_MyAgent" in content
        assert "apps_rg.reasoning.MyAgent" in content

    def test_dry_run_does_not_write(self, tmp_path):
        r = _mock_redis()
        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            result, _ = _heal_uncovered_module(
                r, "apps_rg/reasoning/MyAgent.py", dry_run=True
            )
        assert result.status == "skipped"
        assert result.error == "dry_run"
        assert not list(tmp_path.rglob("test_MyAgent_adg.py"))

    def test_stub_includes_symbols_from_adg(self, tmp_path):
        r = _mock_redis(
            {
                "adg:nodes:by_file:apps_rg/reasoning/MyAgent.py": {"42"},
                "adg:node:42": {
                    "entity_type": "symbol",
                    "adg_name": "ADG::Symbol::apps_rg.reasoning.MyAgent::MyAgent",
                    "resolved_path": "apps_rg/reasoning/MyAgent.py",
                },
            }
        )
        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            result, stub_path = _heal_uncovered_module(
                r, "apps_rg/reasoning/MyAgent.py", dry_run=False
            )
        content = (tmp_path / stub_path).read_text()
        assert "MyAgent" in content


class TestHealItem:
    def test_dispatches_orphan(self, tmp_path):
        r = _mock_redis()
        item = WorkItem(kind="orphan_test", path="tests/adg/orphan.py")
        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            result, new_path = _heal_item(r, item, dry_run=True)
        assert result.item.kind == "orphan_test"
        assert new_path is None

    def test_dispatches_uncovered(self, tmp_path):
        r = _mock_redis()
        item = WorkItem(kind="uncovered_module", path="apps_rg/reasoning/MyAgent.py")
        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            result, new_path = _heal_item(r, item, dry_run=True)
        assert result.item.kind == "uncovered_module"

    def test_antipattern_skipped(self):
        r = _mock_redis()
        item = WorkItem(kind="antipattern_module", path="agentic_core/foo.py")
        result, new_path = _heal_item(r, item, dry_run=False)
        assert result.status == "skipped"
        assert new_path is None


# ---------------------------------------------------------------------------
# Stage 6: _resolve_test_paths and _run_scoped_pytest
# ---------------------------------------------------------------------------


class TestResolveTestPaths:
    def test_returns_empty_when_no_node(self):
        r = _mock_redis()
        paths = _resolve_test_paths(r, "apps_rg/reasoning/Foo.py")
        assert paths == []

    def test_returns_covers_paths(self):
        r = _mock_redis(
            {
                "adg:nodes:by_file:apps_rg/reasoning/Foo.py": {"10"},
                "adg:node:10": {"entity_type": "module", "resolved_path": "apps_rg/reasoning/Foo.py"},
                "adg:edge:in:10:covers": {"20"},
                "adg:node:20": {"entity_type": "module", "resolved_path": "tests/unit/apps_rg/test_Foo_adg.py"},
            }
        )
        paths = _resolve_test_paths(r, "apps_rg/reasoning/Foo.py")
        assert paths == ["tests/unit/apps_rg/test_Foo_adg.py"]

    def test_skips_non_test_paths(self):
        r = _mock_redis(
            {
                "adg:nodes:by_file:apps_rg/reasoning/Foo.py": {"10"},
                "adg:node:10": {"entity_type": "module"},
                "adg:edge:in:10:covers": {"20"},
                "adg:node:20": {"entity_type": "module", "resolved_path": "apps_rg/reasoning/Foo.py"},
            }
        )
        paths = _resolve_test_paths(r, "apps_rg/reasoning/Foo.py")
        assert paths == []


class TestRunScopedPytest:
    def test_returns_zero_for_empty_paths(self):
        exit_code, passed, failed = _run_scoped_pytest([])
        assert exit_code == 0
        assert passed == 0
        assert failed == 0

    def test_returns_zero_when_paths_dont_exist(self, tmp_path):
        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            exit_code, passed, failed = _run_scoped_pytest(["tests/nonexistent.py"])
        assert exit_code == 0

    def test_forwards_pytest_exit_code(self, tmp_path):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="1 passed\n", stderr=""
            )
            # patch exists check
            with patch("pathlib.Path.exists", return_value=True):
                with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
                    exit_code, passed, failed = _run_scoped_pytest(
                        ["tests/dummy.py"]
                    )
        # At least the subprocess was called
        assert mock_run.called


# ---------------------------------------------------------------------------
# Stage 8 & 9: rescore, write_lifecycle, escalation
# ---------------------------------------------------------------------------


class TestRescore:
    def test_dry_run_returns_negative(self):
        result = _rescore(dry_run=True)
        assert result == -1.0

    def test_returns_score_from_redis_on_success(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("redis.Redis") as mock_redis_cls:
                mock_r = MagicMock()
                mock_r.get.return_value = "0.720"
                mock_redis_cls.return_value = mock_r
                score = _rescore(dry_run=False)
        assert score == pytest.approx(0.720)

    def test_returns_negative_on_subprocess_failure(self):
    """Test returns_negative_on_subprocess_failure runtime behavior."""
    # Arrange
    # TODO: Set up processing data
    raw_data = []  # Replace with actual test data

    # Act
    # TODO: Process data with returns_negative_on_subprocess_failure
    processed_result = None  # Replace with actual processing

    # Assert
    assert processed_result is not None, "Processing should produce a result"
    assert len(processed_result) >= 0, "Processed result should be measurable"
    # TODO: Add specific processing assertions
            work_items=[WorkItem(kind="uncovered_module", path="foo.py")],
            heal_results=[HealResult(item=WorkItem(kind="uncovered_module", path="foo.py"), status="fixed")],
            bus_commits=1,
            total_tests_passed=3,
            total_tests_failed=0,
            escalated=False,
            timestamp=1000.0,
        )
        _write_lifecycle_result(r, result)
        pipe = r.pipeline.return_value
        pipe.hmset.assert_called_once()
        call_args = pipe.hmset.call_args[0]
        assert call_args[0] == "adg:drift:lifecycle"
        mapping = call_args[1]
        assert mapping["delta"] == str(round(-0.029, 6))
        assert mapping["bus_commits"] == "1"


class TestMaybeEscalate:
    def test_escalates_when_delta_zero(self):
        r = _mock_redis()
        result = LifecycleResult(
            prior_score=0.749,
            new_score=0.749,
            delta=0.0,
            work_items=[],
            heal_results=[],
            bus_commits=0,
            total_tests_passed=0,
            total_tests_failed=0,
            escalated=True,
            timestamp=1000.0,
        )
        _maybe_escalate(r, result)
        r.rpush.assert_called_once()
        assert r.rpush.call_args[0][0] == "adg:drift:escalation"

    def test_no_escalation_when_improved(self):
        r = _mock_redis()
        result = LifecycleResult(
            prior_score=0.749,
            new_score=0.720,
            delta=-0.029,
            work_items=[],
            heal_results=[],
            bus_commits=0,
            total_tests_passed=0,
            total_tests_failed=0,
            escalated=False,
            timestamp=1000.0,
        )
        _maybe_escalate(r, result)
        r.rpush.assert_not_called()


# ---------------------------------------------------------------------------
# run_lifecycle integration (full dry-run with mocks)
# ---------------------------------------------------------------------------


class TestRunLifecycle:
    def _patch_redis(self, drift_state: dict):
        """Patch redis.Redis to return a mock with drift state."""
        r_mock = MagicMock()
        r_mock.get.side_effect = lambda k: (
            str(drift_state["composite"])
            if k == "adg:drift:score"
            else None
        )
        r_mock.hgetall.side_effect = lambda k: (
            {
                "coverage": str(drift_state["coverage"]),
                "blast": str(drift_state["blast"]),
                "orphan": str(drift_state["orphan"]),
                "violation": str(drift_state["violation"]),
                "prod_total": str(drift_state["prod_total"]),
                "test_total": str(drift_state["test_total"]),
                "timestamp": str(time.time()),
            }
            if k == "adg:drift:subscores"
            else {}
        )
        r_mock.lrange.side_effect = lambda k, s, e: {
            "adg:drift:blast_top": [
                json.dumps(e) for e in drift_state["blast_top"]
            ],
            "adg:drift:uncovered": drift_state["uncovered"],
            "adg:drift:orphan_tests": drift_state["orphan_tests"],
            "adg:drift:violation_gaps": drift_state["violation_gaps"],
        }.get(k, [])
        r_mock.smembers.return_value = set()
        pipe = MagicMock()
        pipe.execute.return_value = []
        r_mock.pipeline.return_value = pipe
        return r_mock

    def test_dry_run_returns_lifecycle_result(self):
        drift = _good_drift_state()
        r_mock = self._patch_redis(drift)

        with patch("redis.Redis", return_value=r_mock), \
             patch.object(lifecycle, "_run_meta_learning_bus", return_value=(0, [])), \
             patch.object(lifecycle, "_rescore", return_value=-1.0):
            result = run_lifecycle(dry_run=True)

        assert isinstance(result, LifecycleResult)
        assert result.prior_score == pytest.approx(drift["composite"])

    def test_escalation_not_triggered_in_dry_run(self):
        drift = _good_drift_state()
        r_mock = self._patch_redis(drift)

        with patch("redis.Redis", return_value=r_mock), \
             patch.object(lifecycle, "_run_meta_learning_bus", return_value=(0, [])), \
             patch.object(lifecycle, "_rescore", return_value=-1.0):
            result = run_lifecycle(dry_run=True)

        # dry_run → escalated is always False
        assert result.escalated is False
        r_mock.rpush.assert_not_called()

    def test_work_items_built_from_blast_top(self):
        drift = _good_drift_state()
        r_mock = self._patch_redis(drift)

        with patch("redis.Redis", return_value=r_mock), \
             patch.object(lifecycle, "_run_meta_learning_bus", return_value=(0, [])), \
             patch.object(lifecycle, "_rescore", return_value=-1.0):
            result = run_lifecycle(dry_run=True)

        assert len(result.work_items) > 0
        assert result.work_items[0].kind in ("uncovered_module", "orphan_test")

    def test_redis_connection_error_raises_runtime_error(self):
    """Test redis_connection_error_raises_runtime_error runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute redis_connection_error_raises_runtime_error
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
# ---------------------------------------------------------------------------


class TestHardeningLifecycle:
    def test_pytest_parser_mixed_passed_and_failed_line(self):
        """B7: '3 failed, 7 passed in 0.5s' must give passed=7 failed=3, not both=7."""
        with patch.object(lifecycle, "PROJECT_ROOT", lifecycle.PROJECT_ROOT):
            # Simulate the subprocess returning that summary
            mock_proc = MagicMock()
            mock_proc.returncode = 1
            mock_proc.stdout = "3 failed, 7 passed in 0.50s\n"
            with patch("subprocess.run", return_value=mock_proc):
                # Need abs_paths to exist — patch Path.exists
                with patch("pathlib.Path.exists", return_value=True):
                    exit_code, passed, failed = _run_scoped_pytest(["tests/dummy.py"])
        assert passed == 7
        assert failed == 3
        assert exit_code == 1

    def test_pytest_parser_only_passed(self):
        """B7: '5 passed in 0.1s' → passed=5 failed=0."""
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "5 passed in 0.10s\n"
        with patch("subprocess.run", return_value=mock_proc), \
             patch("pathlib.Path.exists", return_value=True):
            exit_code, passed, failed = _run_scoped_pytest(["tests/dummy.py"])
        assert passed == 5
        assert failed == 0

    def test_pytest_parser_only_failed(self):
        """B7: '2 failed in 0.2s' → passed=0 failed=2."""
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stdout = "2 failed in 0.20s\n"
        with patch("subprocess.run", return_value=mock_proc), \
             patch("pathlib.Path.exists", return_value=True):
            _, passed, failed = _run_scoped_pytest(["tests/dummy.py"])
        assert passed == 0
        assert failed == 2

    def test_no_collect_only_subprocess_call(self):
    """Test no_collect_only_subprocess_call runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute no_collect_only_subprocess_call
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        """B10: path in blast_top AND orphan_tests must appear only once."""
        drift = _good_drift_state()
        shared_path = "agentic_core/L5_safety/foo.py"
        drift["blast_top"] = [{"path": shared_path, "fan_out": 500}]
        drift["orphan_tests"] = [shared_path, "tests/adg/other.py"]
        items = _build_work_queue(drift, 0, [], budget=10)
        paths = [i.path for i in items]
        assert paths.count(shared_path) == 1

    def test_build_work_queue_deduplicates_orphan_against_bus(self):
        """B10: path in bus_affected AND orphan_tests must appear only once."""
        drift = _good_drift_state()
        shared_path = "agentic_core/L0_routing/bar.py"
        drift["blast_top"] = []
        drift["orphan_tests"] = [shared_path]
        items = _build_work_queue(drift, 1, [shared_path], budget=10)
        paths = [i.path for i in items]
        assert paths.count(shared_path) == 1

    def test_heal_uncovered_module_init_uses_parent_name(self, tmp_path):
        """B9: __init__.py stub filename and class name must use parent dir ('reasoning'), not '__init__'."""
        r = MagicMock()
        r.smembers.return_value = set()
        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            result, stub_path = _heal_uncovered_module(r, "apps_rg/reasoning/__init__.py", dry_run=True)
        assert stub_path is not None
        # filename uses parent dir name: test_reasoning_adg.py, not test___init___adg.py
        assert "test_reasoning_adg.py" in stub_path
        assert "test___init__" not in stub_path
        # dry_run → skipped
        assert result.status == "skipped"

    def test_heal_uncovered_module_normal_stem_unchanged(self, tmp_path):
        """B9: normal module stem is used as-is for class name."""
        r = MagicMock()
        r.smembers.return_value = set()
        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            result, stub_path = _heal_uncovered_module(r, "apps_rg/reasoning/MyAgent.py", dry_run=False)
        # stub not written yet (no existing file) — check path
        assert stub_path is not None
        assert "test_MyAgent_adg.py" in stub_path
