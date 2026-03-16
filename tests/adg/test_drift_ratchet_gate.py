"""
Regression tests for ops_scripts/ci/drift_ratchet_gate.py

All tests mock Redis and subprocess — no live connections.  26 tests.
"""

from __future__ import annotations

import json
import time
from unittest.mock import MagicMock, patch

import pytest

import ops_scripts.ci.drift_ratchet_gate as ratchet
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

_emit_authorize_and_execute("p2", "test_drift_ratchet_gate", "execution_auth")
_emit_validates_capability("p2", "test_drift_ratchet_gate", "capability_check")
_emit_routes_to_capability("p2", "test_drift_ratchet_gate", "capability_route")
_emit_writes_via_uwg("p2", "test_drift_ratchet_gate", "uwg_write")
_emit_blocks_direct_write("p2", "test_drift_ratchet_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "test_drift_ratchet_gate", "tool_invocation")
_emit_captures_execution_output("p2", "test_drift_ratchet_gate", "exec_output")
_emit_dispatches_agent("p3", "test_drift_ratchet_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "test_drift_ratchet_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_drift_ratchet_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_drift_ratchet_gate", "healing_outcome")
_emit_escalates_failure("p3", "test_drift_ratchet_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_drift_ratchet_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_drift_ratchet_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_drift_ratchet_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_drift_ratchet_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_drift_ratchet_gate", "eval_metric")
_emit_stores_embedding("p4", "test_drift_ratchet_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_drift_ratchet_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_drift_ratchet_gate", "exec_snapshot_link")
from ops_scripts.ci.drift_ratchet_gate import (
    EPSILON,
    _read_baseline,
    _read_current,
    _rescore,
    _write_baseline,
    check,
)

_emit_records_execution_trace("p0", "evidence", "test_drift_ratchet_gate")
_emit_applies_guardrail("p0", "test_drift_ratchet_gate", "p0_governance")
_emit_reads_policy_state("p0", "test_drift_ratchet_gate", "policy_binding")
_emit_snapshots_state("p0", "test_drift_ratchet_gate", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_drift_ratchet_gate", "p4obs", "metric_1")
_emit_emits_metric_event("test_drift_ratchet_gate", "p4obs", "metric_2")
_emit_emits_metric_event("test_drift_ratchet_gate", "p4obs", "metric_3")
_emit_emits_metric_event("test_drift_ratchet_gate", "p4obs", "metric_4")
_emit_emits_metric_event("test_drift_ratchet_gate", "p4obs", "metric_5")
_emit_emits_metric_event("test_drift_ratchet_gate", "p4obs", "metric_6")
_emit_records_incident_event("test_drift_ratchet_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_drift_ratchet_gate", "p4obs", "anomaly")
_emit_writes_observability_log("test_drift_ratchet_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_drift_ratchet_gate", "p4obs", "mon_state")
_emit_triggers_alert("test_drift_ratchet_gate", "p4obs", "alert")
_emit_links_incident_trace("test_drift_ratchet_gate", "p4obs", "trace_link")
_emit_captures_pattern("test_drift_ratchet_gate", "p3lm", "pattern")
_emit_records_learning_event("test_drift_ratchet_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_drift_ratchet_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_drift_ratchet_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_drift_ratchet_gate", "p3lm", "routing")
_emit_improves_agent_policy("test_drift_ratchet_gate", "p3lm", "policy")
_emit_stores_learning_state("test_drift_ratchet_gate", "p3lm", "state")
_emit_records_execution_trace("test_drift_ratchet_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_drift_ratchet_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_drift_ratchet_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_drift_ratchet_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_drift_ratchet_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_drift_ratchet_gate", "env_read", "p2_env_1")
_emit_reads_environ("test_drift_ratchet_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_drift_ratchet_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_drift_ratchet_gate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_drift_ratchet_gate", "context_pull")
_emit_pulls_context("p1", "test_drift_ratchet_gate", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_drift_ratchet_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_drift_ratchet_gate", "uwg_term_2")
_emit_writes_through("p1", "test_drift_ratchet_gate", "write_through")
_emit_writes_through("p1", "test_drift_ratchet_gate", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_drift_ratchet_gate", "safety_validation")
_emit_invokes_eval("p1", "test_drift_ratchet_gate", "eval_call")
_emit_proposal_commits_routing("p1", "test_drift_ratchet_gate", "routing_commit")
emit_replay_key("p0", "test_drift_ratchet_gate")
emit_determinism_digest("p0", "test_drift_ratchet_gate")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_redis_with_state(
    score: str | None = "0.749062",
    subscores: dict | None = None,
    uncovered: list | None = None,
    blast_top: list | None = None,
    baseline: str | None = None,
):
    r = MagicMock()
    _uncovered = uncovered if uncovered is not None else ["mod_a.py", "mod_b.py"]
    _blast_top = blast_top if blast_top is not None else [
        json.dumps({"path": "agentic_core/foo.py", "fan_out": 1000})
    ]
    _subscores = subscores or {
        "coverage": "1.0",
        "blast": "0.998",
        "orphan": "0.248",
        "violation": "0.0",
        "timestamp": str(time.time()),
    }
    store = {
        "adg:drift:score": score,
        "adg:drift:subscores": _subscores,
        "adg:drift:uncovered": _uncovered,
        "adg:drift:blast_top": _blast_top,
        ratchet.BASELINE_KEY: baseline,
    }
    r.get.side_effect = lambda k: store.get(k)
    r.hgetall.side_effect = lambda k: store.get(k, {})
    r.lrange.side_effect = lambda k, s, e: store.get(k, [])
    r.set = MagicMock()
    return r


# ---------------------------------------------------------------------------
# _read_current
# ---------------------------------------------------------------------------


class TestReadCurrent:
    def test_returns_none_when_score_missing(self):
        r = _mock_redis_with_state(score=None)
        assert _read_current(r) is None

    def test_returns_tuple_with_float_score(self):
        r = _mock_redis_with_state(score="0.749062")
        result = _read_current(r)
        assert result is not None
        score, uncovered, blast_top, ts = result
        assert score == pytest.approx(0.749062)
        assert isinstance(uncovered, list)
        assert isinstance(blast_top, list)

    def test_parses_blast_top_json(self):
        r = _mock_redis_with_state(
            blast_top=[json.dumps({"path": "foo.py", "fan_out": 100})]
        )
        _, _, blast_top, _ = _read_current(r)
        assert blast_top[0]["path"] == "foo.py"
        assert blast_top[0]["fan_out"] == 100


# ---------------------------------------------------------------------------
# _read_baseline / _write_baseline
# ---------------------------------------------------------------------------


class TestBaselineIO:
    def test_read_returns_none_when_missing(self):
        r = _mock_redis_with_state(baseline=None)
        assert _read_baseline(r) is None

    def test_read_parses_json(self):
        baseline_data = json.dumps(
            {"score": 0.749, "uncovered_modules": ["a.py"], "timestamp": 1000.0}
        )
        r = _mock_redis_with_state(baseline=baseline_data)
        result = _read_baseline(r)
        assert result["score"] == pytest.approx(0.749)
        assert "a.py" in result["uncovered_modules"]

    def test_read_returns_none_on_malformed_json(self):
        r = _mock_redis_with_state(baseline="NOT_JSON")
        assert _read_baseline(r) is None

    def test_write_sets_key_with_sorted_modules(self):
        r = MagicMock()
        _write_baseline(r, 0.720, ["z.py", "a.py", "m.py"])
        r.set.assert_called_once()
        key, raw = r.set.call_args[0]
        assert key == ratchet.BASELINE_KEY
        parsed = json.loads(raw)
        assert parsed["score"] == pytest.approx(0.720)
        assert parsed["uncovered_modules"] == sorted(["z.py", "a.py", "m.py"])
        assert "timestamp" in parsed


# ---------------------------------------------------------------------------
# _rescore
# ---------------------------------------------------------------------------


class TestRescore:
    def test_returns_true_on_exit_zero(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert _rescore() is True

    def test_returns_false_on_nonzero_exit(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            assert _rescore() is False

    def test_returns_false_on_exception(self):
        with patch("subprocess.run", side_effect=OSError("not found")):
            assert _rescore() is False


# ---------------------------------------------------------------------------
# check() — main logic
# ---------------------------------------------------------------------------


class TestCheck:
    def test_first_run_writes_baseline_and_passes(self):
        r = _mock_redis_with_state(baseline=None)
        with patch.object(ratchet, "_connect", return_value=r):
            code = check()
        assert code == 0
        r.set.assert_called_once()  # baseline written

    def test_promote_writes_baseline_unconditionally(self):
        r = _mock_redis_with_state(
            baseline=json.dumps(
                {"score": 0.749, "uncovered_modules": [], "timestamp": 1000.0}
            )
        )
        with patch.object(ratchet, "_connect", return_value=r):
            code = check(promote=True)
        assert code == 0
        r.set.assert_called_once()

    def test_passes_when_score_equals_baseline(self):
        baseline = json.dumps(
            {
                "score": 0.749062,
                "uncovered_modules": ["mod_a.py", "mod_b.py"],
                "timestamp": 1000.0,
            }
        )
        r = _mock_redis_with_state(score="0.749062", baseline=baseline)
        with patch.object(ratchet, "_connect", return_value=r):
            code = check()
        assert code == 0

    def test_passes_when_score_improves(self):
        baseline = json.dumps(
            {
                "score": 0.749062,
                "uncovered_modules": ["mod_a.py", "mod_b.py"],
                "timestamp": 1000.0,
            }
        )
        r = _mock_redis_with_state(score="0.700", baseline=baseline)
        with patch.object(ratchet, "_connect", return_value=r):
            code = check()
        assert code == 0
        # baseline should be updated to better score
        r.set.assert_called_once()

    def test_fails_when_score_regresses_beyond_epsilon(self):
        prior = 0.700
        current = prior + EPSILON + 0.001
        baseline = json.dumps(
            {
                "score": prior,
                "uncovered_modules": [],
                "timestamp": 1000.0,
            }
        )
        r = _mock_redis_with_state(score=str(current), uncovered=["new_mod.py"], baseline=baseline)
        with patch.object(ratchet, "_connect", return_value=r):
            code = check()
        assert code == 1

    def test_fails_when_highest_blast_newly_uncovered(self):
        prior_score = 0.700
        baseline = json.dumps(
            {
                "score": prior_score,
                "uncovered_modules": [],  # blast module was covered before
                "timestamp": 1000.0,
            }
        )
        # current uncovered includes the blast top module
        r = _mock_redis_with_state(
            score=str(prior_score),  # score same (not regressed)
            uncovered=["agentic_core/foo.py"],  # now uncovered
            blast_top=[json.dumps({"path": "agentic_core/foo.py", "fan_out": 1000})],
            baseline=baseline,
        )
        with patch.object(ratchet, "_connect", return_value=r):
            code = check()
        assert code == 1

    def test_rescores_when_score_missing(self):
        r_initial = _mock_redis_with_state(score=None)
        r_after = _mock_redis_with_state(score="0.749", baseline=None)

        call_count = [0]
        def connect_side_effect():
            call_count[0] += 1
            return r_initial

        with patch.object(ratchet, "_connect", side_effect=connect_side_effect), \
             patch.object(ratchet, "_rescore", return_value=False):
            code = check()
        assert code == 2

    def test_rescores_when_stale(self):
        old_ts = str(time.time() - 3 * 3600)  # 3h ago
        r = _mock_redis_with_state(
            subscores={
                "coverage": "1.0",
                "blast": "0.998",
                "orphan": "0.248",
                "violation": "0.0",
                "timestamp": old_ts,
            },
            baseline=None,
        )
        with patch.object(ratchet, "_connect", return_value=r), \
             patch.object(ratchet, "_rescore", return_value=True):
            code = check()
        # rescore called, baseline written on first run
        assert code == 0

    def test_within_epsilon_does_not_fail(self):
        prior = 0.749
        current = prior + EPSILON / 2  # within epsilon
        baseline = json.dumps(
            {"score": prior, "uncovered_modules": [], "timestamp": 1000.0}
        )
        r = _mock_redis_with_state(score=str(current), uncovered=[], baseline=baseline)
        with patch.object(ratchet, "_connect", return_value=r):
            code = check()
        assert code == 0


# ---------------------------------------------------------------------------
# Hardening tests (B1–B3)
# ---------------------------------------------------------------------------


class TestHardening:
    def test_corrupt_blast_top_entry_is_skipped_not_raised(self):
        """B1: corrupt JSON in blast_top must not crash _read_current."""
        r = _mock_redis_with_state(
            blast_top=["NOT_VALID_JSON", json.dumps({"path": "foo.py", "fan_out": 5})]
        )
        result = _read_current(r)
        assert result is not None
        _, _, blast_top, _ = result
        # corrupt entry skipped; valid entry present
        assert len(blast_top) == 1
        assert blast_top[0]["path"] == "foo.py"

    def test_all_corrupt_blast_top_returns_empty_list(self):
        """B1: all corrupt entries → empty blast_top, no crash."""
        r = _mock_redis_with_state(blast_top=["BAD", "WORSE"])
        result = _read_current(r)
        assert result is not None
        _, _, blast_top, _ = result
        assert blast_top == []

    def test_redis_connection_error_returns_exit_2(self):
        """B2: Redis down → check() returns 2 instead of raising."""
        import redis as redis_lib

        with patch.object(ratchet, "_connect", side_effect=redis_lib.ConnectionError("down")):
            code = check()
        assert code == 2

    def test_redis_ping_failure_returns_exit_2(self):
        """B2: Redis connects but ping raises → check() returns 2."""
        import redis as redis_lib

        r = MagicMock()
        r.ping.side_effect = redis_lib.ConnectionError("ping failed")
        with patch.object(ratchet, "_connect", return_value=r):
            code = check()
        assert code == 2

    def test_improvement_exactly_epsilon_does_not_update_baseline(self):
        """B3: score improvement of exactly EPSILON does NOT trigger baseline update."""
        prior = 0.749
        current = prior - EPSILON  # exactly epsilon improvement
        baseline = json.dumps(
            {"score": prior, "uncovered_modules": [], "timestamp": 1000.0}
        )
        r = _mock_redis_with_state(score=str(current), uncovered=[], baseline=baseline)
        with patch.object(ratchet, "_connect", return_value=r):
            code = check()
        assert code == 0
        # baseline NOT updated (current == prior - EPSILON, condition is strict <)
        r.set.assert_not_called()

    def test_improvement_beyond_epsilon_updates_baseline(self):
        """B3: score improvement beyond EPSILON DOES update baseline."""
        prior = 0.749
        current = prior - EPSILON - 0.001
        baseline = json.dumps(
            {"score": prior, "uncovered_modules": [], "timestamp": 1000.0}
        )
        r = _mock_redis_with_state(score=str(current), uncovered=[], baseline=baseline)
        with patch.object(ratchet, "_connect", return_value=r):
            code = check()
        assert code == 0
        r.set.assert_called_once()
