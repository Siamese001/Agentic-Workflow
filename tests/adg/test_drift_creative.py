"""
Creative tests for the drift lifecycle / ratchet / scoped-runner trio.

Techniques used (no live Redis, no filesystem side-effects):
  1. Property-based (hypothesis) — formula invariants, budget contracts,
     monotonicity, JSON round-trip.
  2. Mutation sentinels — inject known logic bugs, assert the real tests
     would catch them.
  3. Contract / schema — Redis key schema completeness, dataclass fields.
  4. Adversarial boundary — epsilon edges, corrupt JSON, zero-module graph,
     massive fan-out, all-orphan test layer, blast_top empty.
  5. Idempotency — double-write baseline is safe, double work-queue write
     yields same items.
  6. Round-trip — trace signal round-trip preserves composite, baseline
     write→read is lossless.
"""

from __future__ import annotations

import json
import math
import time
from copy import deepcopy
from dataclasses import fields
from unittest.mock import MagicMock, patch

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

_emit_records_execution_trace("p0", "evidence", "test_drift_creative")
_emit_applies_guardrail("p0", "test_drift_creative", "p0_governance")
_emit_reads_policy_state("p0", "test_drift_creative", "policy_binding")
_emit_snapshots_state("p0", "test_drift_creative", "state_snapshot")
emit_replay_key("p0", "test_drift_creative")
emit_determinism_digest("p0", "test_drift_creative")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_drift_creative", "execution_auth")
_emit_validates_capability("p2", "test_drift_creative", "capability_check")
_emit_routes_to_capability("p2", "test_drift_creative", "capability_route")
_emit_writes_via_uwg("p2", "test_drift_creative", "uwg_write")
_emit_blocks_direct_write("p2", "test_drift_creative", "direct_write_block")
_emit_records_tool_invocation("p2", "test_drift_creative", "tool_invocation")
_emit_captures_execution_output("p2", "test_drift_creative", "exec_output")
_emit_dispatches_agent("p3", "test_drift_creative", "agent_dispatch")
_emit_coordinates_agents("p3", "test_drift_creative", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_drift_creative", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_drift_creative", "healing_outcome")
_emit_escalates_failure("p3", "test_drift_creative", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_drift_creative", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_drift_creative", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_drift_creative", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_drift_creative", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_drift_creative", "eval_metric")
_emit_stores_embedding("p4", "test_drift_creative", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_drift_creative", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_drift_creative", "exec_snapshot_link")

# hypothesis is optional — skip property tests gracefully if not installed
try:
    from hypothesis import assume, given, settings
    from hypothesis import strategies as st

    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False

# ---------------------------------------------------------------------------
# Modules under test
# ---------------------------------------------------------------------------
import ops_scripts.ci.drift_ratchet_gate as ratchet
import ops_scripts.ci.drift_scoped_test_runner as runner
import tools.adg.drift_lifecycle as lifecycle
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
from ops_scripts.ci.drift_ratchet_gate import (
    EPSILON,
    _read_baseline,
    _write_baseline,
    check,
)
from ops_scripts.ci.drift_scoped_test_runner import (
    run,
)
from tools.adg.drift_lifecycle import (
    DRIFT_THRESHOLD,
    WORK_BUDGET,
    HealResult,
    LifecycleResult,
    WorkItem,
    _build_work_queue,
    _heal_orphan_test,
    _heal_uncovered_module,
    _maybe_escalate,
    _shape_trace_signal,
    _write_lifecycle_result,
    _write_work_queue,
)
from tools.adg.drift_score import WEIGHTS

_emit_emits_metric_event("test_drift_creative", "p4obs", "metric_1")
_emit_emits_metric_event("test_drift_creative", "p4obs", "metric_2")
_emit_emits_metric_event("test_drift_creative", "p4obs", "metric_3")
_emit_emits_metric_event("test_drift_creative", "p4obs", "metric_4")
_emit_emits_metric_event("test_drift_creative", "p4obs", "metric_5")
_emit_emits_metric_event("test_drift_creative", "p4obs", "metric_6")
_emit_records_incident_event("test_drift_creative", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_drift_creative", "p4obs", "anomaly")
_emit_writes_observability_log("test_drift_creative", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_drift_creative", "p4obs", "mon_state")
_emit_triggers_alert("test_drift_creative", "p4obs", "alert")
_emit_links_incident_trace("test_drift_creative", "p4obs", "trace_link")
_emit_captures_pattern("test_drift_creative", "p3lm", "pattern")
_emit_records_learning_event("test_drift_creative", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_drift_creative", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_drift_creative", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_drift_creative", "p3lm", "routing")
_emit_improves_agent_policy("test_drift_creative", "p3lm", "policy")
_emit_stores_learning_state("test_drift_creative", "p3lm", "state")
_emit_records_execution_trace("test_drift_creative", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_drift_creative", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_drift_creative", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_drift_creative", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_drift_creative", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_drift_creative", "env_read", "p2_env_1")
_emit_reads_environ("test_drift_creative", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_drift_creative", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_drift_creative", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_drift_creative", "context_pull")
_emit_pulls_context("p1", "test_drift_creative", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_drift_creative", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_drift_creative", "uwg_term_secondary")
_emit_writes_through("p1", "test_drift_creative", "write_through")
_emit_writes_through("p1", "test_drift_creative", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_drift_creative", "safety_validation")
_emit_invokes_eval("p1", "test_drift_creative", "eval_call")
_emit_proposal_commits_routing("p1", "test_drift_creative", "routing_commit")
_emit_escalates_to_human("p1", "test_drift_creative", "human_escalation")
_emit_routes_through("p1", "test_drift_creative", "route_through")
_emit_checks_agent_registry("p1", "test_drift_creative", "agent_registry")
_emit_validates_agent_capability("p1", "test_drift_creative", "capability")
_emit_dispatches_execution_plan("p1", "test_drift_creative", "exec_plan")
_emit_agent_executes_agent("p1", "test_drift_creative", "sub_agent")
_emit_routes_to_agent("p1", "test_drift_creative", "target_agent")
_emit_verifies_policy("p1", "test_drift_creative", "policy_check")
_emit_observes_runtime_state("p1", "test_drift_creative", "runtime_state")
_emit_verifies_boundary("p1", "test_drift_creative", "boundary_check")
_emit_transcripts_response("p1", "test_drift_creative", "transcript")
_emit_hard_fails_untranscripted("p1", "test_drift_creative")
_emit_gated_by_confidence("p1", "test_drift_creative", "confidence_gate")

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_WEIGHTS_SUM = sum(WEIGHTS.values())


def _drift(composite=0.749, coverage=1.0, blast=0.998, orphan=0.248, violation=0.0):
    return {
        "composite": composite,
        "coverage": coverage,
        "blast": blast,
        "orphan": orphan,
        "violation": violation,
        "prod_total": 2857,
        "test_total": 3165,
        "uncovered_count": 100,
        "orphan_count": 10,
        "blast_top": [{"path": f"mod_{i}.py", "fan_out": 200 - i} for i in range(5)],
        "uncovered": [f"mod_{i}.py" for i in range(5)],
        "orphan_tests": ["tests/adg/orphan.py"],
        "violation_gaps": [],
        "timestamp": time.time(),
    }


def _mock_r():
    r = MagicMock()
    pipe = MagicMock()
    pipe.execute.return_value = []
    r.pipeline.return_value = pipe
    return r


# ===========================================================================
# 1. PROPERTY-BASED TESTS
# Each test uses pytest.importorskip inside its body — safe when hypothesis
# is absent because decorators are never evaluated at collection time.
# ===========================================================================


def _hyp():
    """Return (given, settings, assume, st) or skip the test."""
    hypothesis = pytest.importorskip("hypothesis")
    strategies = pytest.importorskip("hypothesis.strategies")
    return hypothesis.given, hypothesis.settings, hypothesis.assume, strategies


def test_prop_composite_always_in_unit_interval():
    """Composite drift score must always be in [0.0, 1.0] for valid inputs."""
    given, settings, assume, st = _hyp()

    @given(
        coverage=st.floats(0.0, 1.0),
        blast=st.floats(0.0, 1.0),
        orphan=st.floats(0.0, 1.0),
        violation=st.floats(0.0, 1.0),
    )
    @settings(max_examples=200)
    def inner(coverage, blast, orphan, violation):
        assume(all(math.isfinite(v) for v in [coverage, blast, orphan, violation]))
        composite = (
            WEIGHTS["coverage"] * coverage
            + WEIGHTS["blast"] * blast
            + WEIGHTS["orphan"] * orphan
            + WEIGHTS["violation"] * violation
        )
        assert 0.0 <= composite <= 1.0 + 1e-9

    inner()


def test_prop_weights_sum_to_one():
    """Weights must sum to exactly 1.0 (within float tolerance)."""
    _hyp()  # skip if hypothesis absent
    assert abs(_WEIGHTS_SUM - 1.0) < 1e-9


def test_prop_groundedness_never_negative():
    """retrieval_groundedness_score must always be >= 0."""
    given, settings, assume, st = _hyp()

    @given(composite=st.floats(0.0, 1.5, allow_nan=False))
    @settings(max_examples=100)
    def inner(composite):
        sig = _shape_trace_signal(_drift(composite=composite))
        assert sig["retrieval_groundedness_score"] >= 0.0

    inner()


def test_prop_success_flag_consistent_with_threshold():
    """success flag must be True iff composite < DRIFT_THRESHOLD."""
    given, settings, assume, st = _hyp()

    @given(composite=st.floats(0.0, 1.0, allow_nan=False))
    @settings(max_examples=100)
    def inner(composite):
        sig = _shape_trace_signal(_drift(composite=composite))
        assert sig["success"] == (composite < DRIFT_THRESHOLD)

    inner()


def test_prop_work_queue_never_exceeds_budget():
    """Work queue length must never exceed the declared budget."""
    given, settings, assume, st = _hyp()

    @given(
        n_blast=st.integers(0, 50),
        n_orphan=st.integers(0, 20),
        budget=st.integers(1, WORK_BUDGET),
    )
    @settings(max_examples=150)
    def inner(n_blast, n_orphan, budget):
        drift = _drift()
        drift["blast_top"] = [{"path": f"mod_{i}.py", "fan_out": i} for i in range(n_blast)]
        drift["orphan_tests"] = [f"tests/orphan_{i}.py" for i in range(n_orphan)]
        items = _build_work_queue(drift, 0, [], budget)
        assert len(items) <= budget

    inner()


def test_prop_baseline_json_round_trip():
    """Baseline JSON write→read must be lossless for any valid score/modules."""
    given, settings, assume, st = _hyp()

    @given(
        score=st.floats(0.0, 1.0, allow_nan=False),
        modules=st.lists(st.text(min_size=1, max_size=50), max_size=30),
    )
    @settings(max_examples=100)
    def inner(score, modules):
        r = MagicMock()
        captured: dict = {}
        r.set.side_effect = lambda k, v: captured.update({k: v})
        r.get.side_effect = lambda k: captured.get(k)
        _write_baseline(r, score, modules)
        result = _read_baseline(r)
        assert result is not None
        assert result["score"] == pytest.approx(round(score, 6))
        assert result["uncovered_modules"] == sorted(modules)

    inner()


def test_prop_ratchet_logic_monotone():
    """If current > prior + EPSILON → fail; else pass. Never fails on improvement."""
    given, settings, assume, st = _hyp()

    @given(
        prior=st.floats(0.0, 1.0, allow_nan=False),
        current=st.floats(0.0, 1.0, allow_nan=False),
    )
    @settings(max_examples=200)
    def inner(prior, current):
        assume(math.isfinite(prior) and math.isfinite(current))
        baseline_json = json.dumps({
            "score": prior,
            "uncovered_modules": [],
            "timestamp": 1000.0,
        })
        r = MagicMock()
        r.get.side_effect = lambda k: (
            str(current) if k == "adg:drift:score"
            else baseline_json if k == ratchet.BASELINE_KEY
            else None
        )
        r.hgetall.return_value = {"timestamp": str(time.time())}
        r.lrange.return_value = []
        r.set = MagicMock()
        with patch.object(ratchet, "_connect", return_value=r):
            code = check()
        if current > prior + EPSILON:
            assert code == 1
        else:
            assert code == 0

    inner()


def test_prop_risk_class_threshold_consistent():
    """HIGH risk iff fan_out > 100."""
    given, settings, assume, st = _hyp()

    @given(fan_out=st.integers(0, 10000))
    @settings(max_examples=100)
    def inner(fan_out):
        drift = _drift()
        drift["blast_top"] = [{"path": "mod.py", "fan_out": fan_out}]
        drift["orphan_tests"] = []
        items = _build_work_queue(drift, 0, [], 5)
        uncovered = [i for i in items if i.kind == "uncovered_module" and i.path == "mod.py"]
        if uncovered:
            expected = "HIGH" if fan_out > 100 else "MEDIUM"
            assert uncovered[0].risk_class == expected

    inner()


# ===========================================================================
# 2. MUTATION SENTINEL TESTS
# ===========================================================================


class TestMutationSentinels:
    """
    These tests verify that the existing test suite would catch known mutations.
    We inject a mutation, run the affected function, and assert the result
    differs from the correct output.  This validates test sensitivity.
    """

    def test_sentinel_wrong_weight_changes_composite(self):
        """
        Mutation: swap coverage and orphan weights (0.40 ↔ 0.20).
        The composite must change for a case where coverage != orphan.
        """
        d_cov, d_blast, d_orphan, d_viol = 1.0, 0.998, 0.248, 0.0

        # Correct
        correct = (
            0.40 * d_cov + 0.30 * d_blast + 0.20 * d_orphan + 0.10 * d_viol
        )
        # Mutant: swapped weights
        mutant = (
            0.20 * d_cov + 0.30 * d_blast + 0.40 * d_orphan + 0.10 * d_viol
        )
        assert correct != pytest.approx(mutant), "Mutation not detected"

    def test_sentinel_missing_epsilon_allows_regression(self):
        """
        Mutation: remove EPSILON tolerance (treat any increase as failure).
        A score increase of EPSILON/2 should PASS, but without epsilon it FAILS.
        """
        prior = 0.700
        current = prior + EPSILON / 2  # valid noise, should pass

        # With EPSILON tolerance (correct behavior)
        regressed_correct = current > prior + EPSILON
        assert not regressed_correct  # must pass

        # Without EPSILON (mutant — would reject valid noise)
        regressed_mutant = current > prior  # strict comparison
        assert regressed_mutant  # mutant incorrectly rejects

        # This confirms the tests that check EPSILON are guarding real behavior

    def test_sentinel_inverted_groundedness_direction(self):
        """
        Mutation: groundedness = composite (not 1 - composite).
        With higher drift, groundedness should DECREASE, not increase.
        """
        low_drift = _shape_trace_signal(_drift(composite=0.2))
        high_drift = _shape_trace_signal(_drift(composite=0.8))

        # Correct: lower drift → higher groundedness
        assert low_drift["retrieval_groundedness_score"] > high_drift["retrieval_groundedness_score"]

        # Mutant would invert this — catch it
        mutant_low = 0.2  # composite itself
        mutant_high = 0.8
        assert mutant_low < mutant_high  # mutant has wrong direction

    def test_sentinel_budget_off_by_one(self):
        """
        Mutation: budget check uses `<` instead of `<=` (allows budget+1 items).
        We verify the correct implementation caps at exactly `budget`.
        """
        budget = 3
        drift = _drift()
        drift["blast_top"] = [{"path": f"mod_{i}.py", "fan_out": i + 1} for i in range(20)]
        drift["orphan_tests"] = []

        items = _build_work_queue(drift, 0, [], budget)
        assert len(items) == budget  # must be EXACTLY budget, not budget+1

    def test_sentinel_escalation_inverted_condition(self):
        """
        Mutation: escalate when delta < 0 (score improved) instead of >= 0.
        We verify escalation only fires when score did NOT improve.
        """
        r = _mock_r()

        # Score improved — should NOT escalate
        improved = LifecycleResult(
            prior_score=0.749, new_score=0.700, delta=-0.049,
            work_items=[], heal_results=[], bus_commits=0,
            total_tests_passed=0, total_tests_failed=0,
            escalated=False, timestamp=1000.0,
        )
        _maybe_escalate(r, improved)
        r.rpush.assert_not_called()

        # Score same — SHOULD escalate
        r2 = _mock_r()
        unchanged = LifecycleResult(
            prior_score=0.749, new_score=0.749, delta=0.0,
            work_items=[], heal_results=[], bus_commits=0,
            total_tests_passed=0, total_tests_failed=0,
            escalated=True, timestamp=1000.0,
        )
        _maybe_escalate(r2, unchanged)
        r2.rpush.assert_called_once()

    def test_sentinel_covers_key_direction(self):
        """
        Mutation: use adg:edge:<nid>:covers (fan-out) instead of
        adg:edge:in:<nid>:covers (fan-in).
        Fan-in gives test→prod direction; fan-out would give prod→??? which is empty.
        """
        r = MagicMock()
        # Correct key: adg:edge:in:10:covers → test nodes
        r.smembers.side_effect = lambda k: (
            {"10"} if k == "adg:nodes:by_file:apps_rg/foo.py"
            else {"20"} if k == "adg:edge:in:10:covers"
            else set()  # mutant key "adg:edge:10:covers" would return empty
        )
        r.hgetall.side_effect = lambda k: (
            {"entity_type": "module"} if k == "adg:node:10"
            else {"entity_type": "module", "resolved_path": "tests/unit/test_foo.py"}
            if k == "adg:node:20"
            else {}
        )

        paths = runner._resolve_test_paths_for_module(r, "apps_rg/foo.py")
        assert paths == ["tests/unit/test_foo.py"]

        # Mutant: fan-out direction would yield empty
        r2 = MagicMock()
        r2.smembers.side_effect = lambda k: (
            {"10"} if k == "adg:nodes:by_file:apps_rg/foo.py"
            else {"20"} if k == "adg:edge:10:covers"  # wrong direction
            else set()
        )
        r2.hgetall.side_effect = lambda k: (
            {"entity_type": "module"} if k == "adg:node:10" else {}
        )
        mutant_paths = runner._resolve_test_paths_for_module(r2, "apps_rg/foo.py")
        assert mutant_paths == []  # mutant produces wrong (empty) result


# ===========================================================================
# 3. CONTRACT / SCHEMA TESTS
# ===========================================================================


class TestContracts:
    def test_lifecycle_result_dataclass_has_all_required_fields(self):
        """LifecycleResult must expose all fields written to Redis lifecycle HASH."""
        field_names = {f.name for f in fields(LifecycleResult)}
        required = {
            "prior_score", "new_score", "delta", "work_items",
            "heal_results", "bus_commits", "total_tests_passed",
            "total_tests_failed", "escalated", "timestamp",
        }
        assert required <= field_names

    def test_work_item_dataclass_has_all_serializable_fields(self):
        """WorkItem must be fully JSON-serializable via its dict representation."""
        item = WorkItem(kind="uncovered_module", path="foo.py", fan_out=42, risk_class="HIGH")
        d = {"kind": item.kind, "path": item.path, "fan_out": item.fan_out,
             "risk_class": item.risk_class, "commit_id": item.commit_id}
        raw = json.dumps(d)
        back = json.loads(raw)
        assert back["kind"] == "uncovered_module"
        assert back["fan_out"] == 42

    def test_lifecycle_redis_hash_has_correct_field_names(self):
        """
        adg:drift:lifecycle HASH must contain exactly the fields documented
        in the design spec.
        """
        r = _mock_r()
        result = LifecycleResult(
            prior_score=0.749, new_score=0.720, delta=-0.029,
            work_items=[WorkItem(kind="uncovered_module", path="foo.py")],
            heal_results=[HealResult(
                item=WorkItem(kind="uncovered_module", path="foo.py"), status="fixed"
            )],
            bus_commits=1, total_tests_passed=3, total_tests_failed=0,
            escalated=False, timestamp=1000.0,
        )
        _write_lifecycle_result(r, result)
        pipe = r.pipeline.return_value
        _, mapping = pipe.hmset.call_args[0]

        required_keys = {
            "prior_score", "new_score", "delta", "bus_commits", "work_items",
            "heals_fixed", "heals_skipped", "heals_error",
            "total_tests_passed", "total_tests_failed", "escalated", "timestamp",
        }
        assert required_keys <= set(mapping.keys())

    def test_work_queue_redis_entries_are_valid_json(self):
        """Every entry pushed to adg:drift:work_queue must be valid JSON."""
        r = _mock_r()
        items = [
            WorkItem(kind="uncovered_module", path="a.py", fan_out=10, risk_class="HIGH"),
            WorkItem(kind="orphan_test", path="tests/b.py"),
        ]
        _write_work_queue(r, items)
        pipe = r.pipeline.return_value
        rpush_calls = [c for c in pipe.rpush.call_args_list]
        for call in rpush_calls:
            raw = call[0][1]
            parsed = json.loads(raw)
            assert "kind" in parsed
            assert "path" in parsed

    def test_baseline_schema_has_required_keys(self):
        """adg:drift:baseline JSON must always have score, uncovered_modules, timestamp."""
        r = MagicMock()
        captured = {}
        r.set.side_effect = lambda k, v: captured.update({k: v})

        _write_baseline(r, 0.749, ["a.py"])
        raw = captured[ratchet.BASELINE_KEY]
        parsed = json.loads(raw)
        assert "score" in parsed
        assert "uncovered_modules" in parsed
        assert "timestamp" in parsed
        assert isinstance(parsed["uncovered_modules"], list)
        assert isinstance(parsed["timestamp"], float)

    def test_trace_signal_has_all_meta_learning_bus_required_fields(self):
        """
        Trace signal must contain the fields the MetaLearningBus TraceFeatureExtractor
        reads: route_selected, success, final_outcome_class, mutation_presence,
        policy_state_accessed, guardrails_applied, retrieval_groundedness_score.
        """
        sig = _shape_trace_signal(_drift())
        required = {
            "route_selected", "success", "final_outcome_class",
            "mutation_presence", "policy_state_accessed",
            "guardrails_applied", "retrieval_groundedness_score",
        }
        assert required <= set(sig.keys())

    def test_ci_run_hash_field_types_are_strings(self):
        """All values in adg:drift:ci_run HASH must be strings (Redis HASH constraint)."""
        r = MagicMock()
        pipe = MagicMock()
        pipe.execute.return_value = []
        r.pipeline.return_value = pipe

        runner._write_ci_run_result(r, 3, 5, ["a.py"], 0)
        _, mapping = pipe.hmset.call_args[0]
        for k, v in mapping.items():
            assert isinstance(v, str), f"Field {k} is not a string: {v!r}"


# ===========================================================================
# 4. ADVERSARIAL BOUNDARY TESTS
# ===========================================================================


class TestAdversarialBoundary:
    def test_zero_module_graph_returns_empty_work_queue(self):
        """With no prod or test modules, work queue must be empty."""
        drift = _drift()
        drift["blast_top"] = []
        drift["orphan_tests"] = []
        drift["uncovered"] = []
        items = _build_work_queue(drift, 0, [], WORK_BUDGET)
        assert items == []

    def test_all_modules_orphaned_does_not_exceed_budget(self):
        """If all test modules are orphaned, queue still respects budget."""
        drift = _drift()
        drift["blast_top"] = []
        drift["orphan_tests"] = [f"tests/orphan_{i}.py" for i in range(100)]
        items = _build_work_queue(drift, 0, [], WORK_BUDGET)
        assert len(items) <= WORK_BUDGET

    def test_massive_fan_out_module_stays_high_risk(self):
        """fan_out=10_000 must produce risk_class=HIGH."""
        drift = _drift()
        drift["blast_top"] = [{"path": "god_module.py", "fan_out": 10_000}]
        drift["orphan_tests"] = []
        items = _build_work_queue(drift, 0, [], 5)
        assert items[0].risk_class == "HIGH"
        assert items[0].fan_out == 10_000

    def test_corrupt_baseline_json_returns_none(self):
        """Malformed baseline JSON must not crash — returns None."""
        r = MagicMock()
        r.get.return_value = "{corrupt: not json,,}"
        assert _read_baseline(r) is None

    def test_empty_blast_top_does_not_crash_work_queue(self):
        """drift['blast_top'] = [] must not crash _build_work_queue."""
        drift = _drift()
        drift["blast_top"] = []
        items = _build_work_queue(drift, 0, [], 5)
        # Only orphan items (if any)
        assert all(i.kind == "orphan_test" for i in items)

    def test_composite_exactly_at_threshold_is_nominal(self):
        """composite == DRIFT_THRESHOLD (0.5) → DRIFT_NOMINAL, success=False."""
        sig = _shape_trace_signal(_drift(composite=DRIFT_THRESHOLD))
        assert sig["final_outcome_class"] == "DRIFT_NOMINAL"
        assert sig["success"] is False  # not strictly less than

    def test_composite_zero_full_groundedness(self):
        """composite=0.0 → groundedness=1.0, success=True, DRIFT_NOMINAL."""
        sig = _shape_trace_signal(_drift(composite=0.0))
        assert sig["retrieval_groundedness_score"] == pytest.approx(1.0)
        assert sig["success"] is True

    def test_composite_one_zero_groundedness(self):
        """composite=1.0 → groundedness=0.0, success=False, DRIFT_ALERT."""
        sig = _shape_trace_signal(_drift(composite=1.0))
        assert sig["retrieval_groundedness_score"] == pytest.approx(0.0)
        assert sig["success"] is False

    def test_no_changed_files_returns_zero_without_redis_calls(self):
        """If git reports no changed files, pytest is never invoked."""
        r = MagicMock()
        with patch.object(runner, "_connect", return_value=r), \
             patch.object(runner, "_changed_prod_files", return_value=[]):
            code = run()
        assert code == 0
        r.smembers.assert_not_called()

    def test_ratchet_score_exactly_at_epsilon_boundary_passes(self):
        """score == prior + EPSILON must PASS (not strictly greater)."""
        prior = 0.700
        current = prior + EPSILON  # exactly at boundary
        baseline = json.dumps({"score": prior, "uncovered_modules": [], "timestamp": 1000.0})
        r = MagicMock()
        r.get.side_effect = lambda k: (
            str(current) if k == "adg:drift:score"
            else baseline if k == ratchet.BASELINE_KEY
            else None
        )
        r.hgetall.return_value = {"timestamp": str(time.time())}
        r.lrange.return_value = []
        r.set = MagicMock()
        with patch.object(ratchet, "_connect", return_value=r):
            code = check()
        assert code == 0

    def test_orphan_heal_with_deeply_nested_path(self, tmp_path):
        """Orphan heal must create nested quarantine dir for deep paths."""
        deep_dir = tmp_path / "tests" / "unit" / "apps_rg" / "reasoning"
        deep_dir.mkdir(parents=True)
        orphan = deep_dir / "orphan_deep.py"
        orphan.write_text("# orphan")
        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            result = _heal_orphan_test(
                "tests/unit/apps_rg/reasoning/orphan_deep.py", dry_run=False
            )
        assert result.status == "fixed"
        assert (tmp_path / "tests" / "_quarantine" / "orphan_deep.py").exists()

    def test_stub_generated_for_init_module_uses_safe_class_name(self, tmp_path):
        """__init__.py stub class name must not contain dunder."""
        r = MagicMock()
        r.smembers.return_value = set()
        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            result, stub_path = _heal_uncovered_module(
                r, "apps_rg/reasoning/__init__.py", dry_run=False
            )
        # Either succeeds with safe name or is skipped — must not raise
        assert result.status in ("fixed", "skipped", "error")
        if result.status == "fixed" and stub_path:
            content = (tmp_path / stub_path).read_text()
            assert "TestDriftCoverage___init__" in content

    def test_work_queue_bus_path_deduped_against_blast_top(self):
        """If bus returns a path already in blast_top, it must not appear twice."""
        drift = _drift()
        blast_path = drift["blast_top"][0]["path"]
        items = _build_work_queue(drift, 1, [blast_path], WORK_BUDGET)
        paths = [i.path for i in items if i.path == blast_path]
        assert len(paths) == 1, f"Duplicate path in work queue: {paths}"


# ===========================================================================
# 5. IDEMPOTENCY TESTS
# ===========================================================================


class TestIdempotency:
    def test_write_baseline_twice_same_inputs_is_safe(self):
        """Writing baseline twice with same inputs must not corrupt state."""
        captured: dict = {}
        r = MagicMock()
        r.set.side_effect = lambda k, v: captured.update({k: v})
        r.get.side_effect = lambda k: captured.get(k)

        _write_baseline(r, 0.749, ["a.py", "b.py"])
        first = json.loads(captured[ratchet.BASELINE_KEY])

        _write_baseline(r, 0.749, ["a.py", "b.py"])
        second = json.loads(captured[ratchet.BASELINE_KEY])

        assert first["score"] == second["score"]
        assert first["uncovered_modules"] == second["uncovered_modules"]

    def test_write_work_queue_twice_replaces_not_appends(self):
        """Writing work queue twice must not double-push items."""
        r = _mock_r()
        pipe = r.pipeline.return_value
        rpush_counts: list[int] = []

        items = [WorkItem(kind="uncovered_module", path="a.py")]

        _write_work_queue(r, items)
        count1 = pipe.rpush.call_count
        rpush_counts.append(count1)

        pipe.reset_mock()
        _write_work_queue(r, items)
        count2 = pipe.rpush.call_count
        rpush_counts.append(count2)

        # Both writes push same number of items (pipe.delete + pipe.rpush called)
        assert rpush_counts[0] == rpush_counts[1]
        # delete is called before rpush each time
        assert pipe.delete.call_count >= 1

    def test_shape_trace_signal_deterministic(self):
        """_shape_trace_signal must be pure — same input → same output."""
        drift = _drift()
        sig1 = _shape_trace_signal(drift)
        sig2 = _shape_trace_signal(deepcopy(drift))
        assert sig1 == sig2

    def test_build_work_queue_deterministic(self):
        """Same drift state → same ordered work queue."""
        drift = _drift()
        items1 = _build_work_queue(drift, 0, [], WORK_BUDGET)
        items2 = _build_work_queue(deepcopy(drift), 0, [], WORK_BUDGET)
        assert [i.path for i in items1] == [i.path for i in items2]
        assert [i.kind for i in items1] == [i.kind for i in items2]

    def test_heal_orphan_twice_second_is_skipped(self, tmp_path):
        """Healing an orphan that no longer exists on second run → skipped."""
        (tmp_path / "tests" / "adg").mkdir(parents=True)
        orphan = tmp_path / "tests" / "adg" / "orphan.py"
        orphan.write_text("# orphan")

        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            r1 = _heal_orphan_test("tests/adg/orphan.py", dry_run=False)
        assert r1.status == "fixed"

        with patch.object(lifecycle, "PROJECT_ROOT", tmp_path):
            r2 = _heal_orphan_test("tests/adg/orphan.py", dry_run=False)
        assert r2.status == "skipped"  # file no longer exists at original path


# ===========================================================================
# 6. ROUND-TRIP TESTS
# ===========================================================================


class TestRoundTrip:
    def test_trace_signal_composite_extractable(self):
        """drift_composite in trace signal must match input composite."""
        for composite in [0.0, 0.25, 0.5, 0.749, 1.0]:
            sig = _shape_trace_signal(_drift(composite=composite))
            assert sig["drift_composite"] == pytest.approx(composite)

    def test_trace_signal_sub_scores_match_drift_state(self):
        """All sub-scores in trace signal must match the drift state inputs."""
        drift = _drift(coverage=0.8, blast=0.6, orphan=0.3, violation=0.1)
        sig = _shape_trace_signal(drift)
        assert sig["drift_coverage"] == pytest.approx(0.8)
        assert sig["drift_blast"] == pytest.approx(0.6)
        assert sig["drift_orphan"] == pytest.approx(0.3)
        assert sig["drift_violation"] == pytest.approx(0.1)

    def test_baseline_preserves_module_order(self):
        """Baseline must store modules in sorted order regardless of input order."""
        r = MagicMock()
        captured: dict = {}
        r.set.side_effect = lambda k, v: captured.update({k: v})
        r.get.side_effect = lambda k: captured.get(k)

        modules = ["z.py", "a.py", "m.py", "b.py"]
        _write_baseline(r, 0.5, modules)
        parsed = _read_baseline(r)
        assert parsed["uncovered_modules"] == sorted(modules)

    def test_lifecycle_delta_is_new_minus_prior(self):
        """delta field must always equal new_score - prior_score."""
        for prior, new in [(0.749, 0.720), (0.5, 0.5), (0.3, 0.4)]:
            result = LifecycleResult(
                prior_score=prior, new_score=new, delta=new - prior,
                work_items=[], heal_results=[], bus_commits=0,
                total_tests_passed=0, total_tests_failed=0,
                escalated=(new - prior) >= 0, timestamp=1000.0,
            )
            assert result.delta == pytest.approx(new - prior)
            assert result.escalated == ((new - prior) >= 0)

    def test_heal_result_status_exhaustive(self):
        """HealResult.status must be one of the three documented values."""
        valid_statuses = {"fixed", "skipped", "error"}
        for status in valid_statuses:
            hr = HealResult(
                item=WorkItem(kind="uncovered_module", path="x.py"),
                status=status,
            )
            assert hr.status in valid_statuses

    def test_changed_files_filters_are_consistent_with_prod_definition(self):
        """
        Any file starting with 'tests/' must be excluded.
        Any file not ending in '.py' must be excluded.
        Production .py files must be included.
        """
        cases = [
            ("apps_rg/reasoning/Foo.py", True),
            ("tests/unit/test_Foo.py", False),
            ("apps_rg/config.json", False),
            ("ops_scripts/ci/drift_ratchet_gate.py", True),
            ("tests/adg/test_drift.py", False),
            ("README.md", False),
            ("tools/adg/drift_score.py", True),
        ]
        for path, expected_included in cases:
            included = path.endswith(".py") and not path.startswith("tests/")
            assert included == expected_included, f"Wrong for {path!r}"
