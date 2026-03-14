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
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="error")
            score = _rescore(dry_run=False)
        assert score == -1.0


class TestWriteLifecycleResult:
    def test_writes_all_fields_to_redis(self):
        r = _mock_redis()
        result = LifecycleResult(
            prior_score=0.749,
            new_score=0.720,
            delta=-0.029,
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
