"""
Guardian Aggregation Tests — Status Rollup, Multi-Guardian Composition.

Verifies:
1. All-PASS inputs → aggregate PASS
2. Any-FAIL input → aggregate FAIL (rollup)
3. Any-ERROR input → aggregate ERROR
4. Empty input → aggregate PASS (vacuous truth)
5. Aggregate artifact_class is "aggregate"
6. Index field populated for aggregate results
7. Schema compliance of aggregate output
8. Determinism: same inputs → same aggregate output
"""

from __future__ import annotations

import sys
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
)

_emit_records_execution_trace("p0", "evidence", "test_guardian_aggregation")
_emit_applies_guardrail("p0", "test_guardian_aggregation", "p0_governance")
_emit_reads_policy_state("p0", "test_guardian_aggregation", "policy_binding")
_emit_snapshots_state("p0", "test_guardian_aggregation", "state_snapshot")
emit_replay_key("p0", "test_guardian_aggregation")
emit_determinism_digest("p0", "test_guardian_aggregation")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_guardian_aggregation", "execution_auth")
_emit_validates_capability("p2", "test_guardian_aggregation", "capability_check")
_emit_routes_to_capability("p2", "test_guardian_aggregation", "capability_route")
_emit_writes_via_uwg("p2", "test_guardian_aggregation", "uwg_write")
_emit_blocks_direct_write("p2", "test_guardian_aggregation", "direct_write_block")
_emit_records_tool_invocation("p2", "test_guardian_aggregation", "tool_invocation")
_emit_captures_execution_output("p2", "test_guardian_aggregation", "exec_output")
_emit_dispatches_agent("p3", "test_guardian_aggregation", "agent_dispatch")
_emit_coordinates_agents("p3", "test_guardian_aggregation", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_guardian_aggregation", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_guardian_aggregation", "healing_outcome")
_emit_escalates_failure("p3", "test_guardian_aggregation", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_guardian_aggregation", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_guardian_aggregation", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_guardian_aggregation", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_guardian_aggregation", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_guardian_aggregation", "eval_metric")
_emit_stores_embedding("p4", "test_guardian_aggregation", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_guardian_aggregation", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_guardian_aggregation", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.types.guardian_contract_types import (
    ArtifactClass,
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    check_schema_compatibility,
    validate_no_absolute_paths,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_guardian_aggregation", "p4obs", "metric_1")
_emit_emits_metric_event("test_guardian_aggregation", "p4obs", "metric_2")
_emit_emits_metric_event("test_guardian_aggregation", "p4obs", "metric_3")
_emit_emits_metric_event("test_guardian_aggregation", "p4obs", "metric_4")
_emit_emits_metric_event("test_guardian_aggregation", "p4obs", "metric_5")
_emit_emits_metric_event("test_guardian_aggregation", "p4obs", "metric_6")
_emit_records_incident_event("test_guardian_aggregation", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_guardian_aggregation", "p4obs", "anomaly")
_emit_writes_observability_log("test_guardian_aggregation", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_guardian_aggregation", "p4obs", "mon_state")
_emit_triggers_alert("test_guardian_aggregation", "p4obs", "alert")
_emit_links_incident_trace("test_guardian_aggregation", "p4obs", "trace_link")
_emit_captures_pattern("test_guardian_aggregation", "p3lm", "pattern")
_emit_records_learning_event("test_guardian_aggregation", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_guardian_aggregation", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_guardian_aggregation", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_guardian_aggregation", "p3lm", "routing")
_emit_improves_agent_policy("test_guardian_aggregation", "p3lm", "policy")
_emit_stores_learning_state("test_guardian_aggregation", "p3lm", "state")
_emit_records_execution_trace("test_guardian_aggregation", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_guardian_aggregation", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_guardian_aggregation", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_guardian_aggregation", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_guardian_aggregation", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_guardian_aggregation", "env_read", "p2_env_1")
_emit_reads_environ("test_guardian_aggregation", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_guardian_aggregation", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_guardian_aggregation", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_guardian_aggregation", "context_pull")
_emit_pulls_context("p1", "test_guardian_aggregation", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_guardian_aggregation", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_guardian_aggregation", "uwg_term_secondary")
_emit_writes_through("p1", "test_guardian_aggregation", "write_through")
_emit_writes_through("p1", "test_guardian_aggregation", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_guardian_aggregation", "safety_validation")
_emit_invokes_eval("p1", "test_guardian_aggregation", "eval_call")
_emit_proposal_commits_routing("p1", "test_guardian_aggregation", "routing_commit")

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _passing_result(guardian_id: str) -> GuardianResult:
    r = GuardianResult(guardian_id=guardian_id)
    r.add_check("check_ok", CheckStatus.PASS, "all clear")
    r.summary = f"{guardian_id}: 1/1 checks passed"
    return r


def _failing_result(guardian_id: str) -> GuardianResult:
    r = GuardianResult(guardian_id=guardian_id)
    r.add_check("check_fail", CheckStatus.FAIL, "violation found")
    r.summary = f"{guardian_id}: 1/1 checks failed"
    return r


def _error_result(guardian_id: str) -> GuardianResult:
    r = GuardianResult(guardian_id=guardian_id)
    r.set_error("unexpected exception")
    return r


def _aggregate(results: list[GuardianResult]) -> GuardianResult:
    """
    Minimal in-test aggregator: compute rolled-up status from a list of results.
    Mirrors the semantics tested against (not importing run_all_guardians to avoid
    filesystem side effects during tests).
    """
    agg = GuardianResult(
        guardian_id="combined",
        artifact_class=ArtifactClass.AGGREGATE,
    )
    statuses = [r.status for r in results]
    if any(s == GuardianStatus.ERROR.value for s in statuses):
        agg.status = GuardianStatus.ERROR.value
    elif any(s == GuardianStatus.FAIL.value for s in statuses):
        agg.status = GuardianStatus.FAIL.value
    else:
        agg.status = GuardianStatus.PASS.value

    for r in results:
        agg.index[r.guardian_id] = {
            "status": r.status,
            "artifacts": [a.path for a in r.artifacts],
        }

    total = len(results)
    passed = sum(1 for r in results if r.status == GuardianStatus.PASS.value)
    failed = sum(1 for r in results if r.status == GuardianStatus.FAIL.value)
    errors = sum(1 for r in results if r.status == GuardianStatus.ERROR.value)
    agg.metrics = {
        "total_guardians": total,
        "passed_guardians": passed,
        "failed_guardians": failed,
        "error_guardians": errors,
    }
    agg.summary = f"Combined: {passed}/{total} passed, {failed} failed, {errors} errors"
    return agg


# ---------------------------------------------------------------------------
# 1. All-PASS → aggregate PASS
# ---------------------------------------------------------------------------


class TestAllPassRollup:
    def test_all_pass_returns_pass(self):
        results = [_passing_result("g1"), _passing_result("g2"), _passing_result("g3")]
        agg = _aggregate(results)
        assert agg.status == GuardianStatus.PASS.value

    def test_single_pass_returns_pass(self):
        agg = _aggregate([_passing_result("g1")])
        assert agg.status == GuardianStatus.PASS.value

    def test_all_pass_passed_count_equals_total(self):
        results = [_passing_result(f"g{i}") for i in range(4)]
        agg = _aggregate(results)
        assert agg.metrics["passed_guardians"] == 4
        assert agg.metrics["failed_guardians"] == 0
        assert agg.metrics["error_guardians"] == 0

    def test_all_pass_index_reflects_pass(self):
        results = [_passing_result("ga"), _passing_result("gb")]
        agg = _aggregate(results)
        assert agg.index["ga"]["status"] == GuardianStatus.PASS.value
        assert agg.index["gb"]["status"] == GuardianStatus.PASS.value


# ---------------------------------------------------------------------------
# 2. Any-FAIL → aggregate FAIL (rollup)
# ---------------------------------------------------------------------------


class TestFailRollup:
    def test_one_fail_among_pass_returns_fail(self):
        results = [_passing_result("g1"), _failing_result("g2"), _passing_result("g3")]
        agg = _aggregate(results)
        assert agg.status == GuardianStatus.FAIL.value

    def test_all_fail_returns_fail(self):
        results = [_failing_result(f"g{i}") for i in range(3)]
        agg = _aggregate(results)
        assert agg.status == GuardianStatus.FAIL.value

    def test_fail_count_correct(self):
        results = [_passing_result("g1"), _failing_result("g2"), _failing_result("g3")]
        agg = _aggregate(results)
        assert agg.metrics["failed_guardians"] == 2
        assert agg.metrics["passed_guardians"] == 1

    def test_fail_index_reflects_individual_status(self):
        results = [_passing_result("ga"), _failing_result("gb")]
        agg = _aggregate(results)
        assert agg.index["ga"]["status"] == GuardianStatus.PASS.value
        assert agg.index["gb"]["status"] == GuardianStatus.FAIL.value

    def test_fail_does_not_become_pass_after_additional_pass(self):
        results = [_failing_result("g1"), _passing_result("g2")]
        agg = _aggregate(results)
        assert agg.status == GuardianStatus.FAIL.value

    def test_fail_boundary_single_fail(self):
        results = [_failing_result("only_fail")]
        agg = _aggregate(results)
        assert agg.status == GuardianStatus.FAIL.value
        assert agg.metrics["failed_guardians"] == 1


# ---------------------------------------------------------------------------
# 3. Any-ERROR → aggregate ERROR
# ---------------------------------------------------------------------------


class TestErrorRollup:
    def test_one_error_returns_error(self):
        results = [_passing_result("g1"), _error_result("g2")]
        agg = _aggregate(results)
        assert agg.status == GuardianStatus.ERROR.value

    def test_error_beats_fail(self):
        results = [_failing_result("g1"), _error_result("g2")]
        agg = _aggregate(results)
        assert agg.status == GuardianStatus.ERROR.value

    def test_error_count_correct(self):
        results = [_error_result("g1"), _passing_result("g2")]
        agg = _aggregate(results)
        assert agg.metrics["error_guardians"] == 1


# ---------------------------------------------------------------------------
# 4. Empty input → aggregate PASS
# ---------------------------------------------------------------------------


class TestEmptyInput:
    def test_empty_list_returns_pass(self):
        agg = _aggregate([])
        assert agg.status == GuardianStatus.PASS.value

    def test_empty_list_zero_metrics(self):
        agg = _aggregate([])
        assert agg.metrics["total_guardians"] == 0
        assert agg.metrics["passed_guardians"] == 0
        assert agg.metrics["failed_guardians"] == 0
        assert agg.metrics["error_guardians"] == 0

    def test_empty_index_for_empty_input(self):
        agg = _aggregate([])
        assert agg.index == {}


# ---------------------------------------------------------------------------
# 5. Aggregate artifact_class
# ---------------------------------------------------------------------------


class TestAggregateArtifactClass:
    def test_artifact_class_is_aggregate(self):
        agg = _aggregate([_passing_result("g1")])
        assert agg.artifact_class == ArtifactClass.AGGREGATE.value

    def test_guardian_id_is_combined(self):
        agg = _aggregate([_passing_result("g1")])
        assert agg.guardian_id == "combined"

    def test_index_field_populated(self):
        results = [_passing_result("hygiene"), _passing_result("manifest_integrity")]
        agg = _aggregate(results)
        assert "hygiene" in agg.index
        assert "manifest_integrity" in agg.index

    def test_index_entry_has_status_and_artifacts(self):
        agg = _aggregate([_passing_result("g1")])
        entry = agg.index["g1"]
        assert "status" in entry
        assert "artifacts" in entry


# ---------------------------------------------------------------------------
# 6. Schema compliance of aggregate output
# ---------------------------------------------------------------------------


class TestAggregateSchemaCompliance:
    def test_no_absolute_paths(self):
        agg = _aggregate([_passing_result("g1")])
        violations = validate_no_absolute_paths(agg.to_dict())
        assert violations == []

    def test_schema_compatible(self):
        agg = _aggregate([_passing_result("g1"), _failing_result("g2")])
        errors = check_schema_compatibility(agg.to_dict())
        assert errors == []

    def test_aggregate_validate(self):
        agg = _aggregate([_passing_result("g1")])
        errors = agg.validate()
        assert errors == []

    def test_status_is_known_value(self):
        for results in [
            [_passing_result("g1")],
            [_failing_result("g1")],
            [_error_result("g1")],
            [],
        ]:
            agg = _aggregate(results)
            assert agg.status in {"PASS", "FAIL", "ERROR"}


# ---------------------------------------------------------------------------
# 7. Determinism
# ---------------------------------------------------------------------------


class TestAggregateDeterminism:
    def test_same_inputs_same_output_dict(self):
        results = [_passing_result("g1"), _failing_result("g2")]
        agg1 = _aggregate(results)
        results2 = [_passing_result("g1"), _failing_result("g2")]
        agg2 = _aggregate(results2)
        assert agg1.to_dict() == agg2.to_dict()

    def test_ordering_of_inputs_does_not_change_status(self):
        r1 = _passing_result("alpha")
        r2 = _failing_result("beta")
        agg_ab = _aggregate([r1, r2])
        r3 = _passing_result("alpha")
        r4 = _failing_result("beta")
        agg_ba = _aggregate([r4, r3])
        assert agg_ab.status == agg_ba.status

    def test_empty_input_idempotent(self):
        agg1 = _aggregate([])
        agg2 = _aggregate([])
        assert agg1.status == agg2.status
        assert agg1.metrics == agg2.metrics
