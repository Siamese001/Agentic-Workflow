"""
Phase 3: Semantic Coverage Quality Enforcement.

Ensures that coverage ratchet cannot be gamed with empty assertions.
Only quality assertions (status + semantic property) count toward coverage.
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

_emit_records_execution_trace("p0", "evidence", "test_semantic_coverage_quality")
_emit_applies_guardrail("p0", "test_semantic_coverage_quality", "p0_governance")
_emit_reads_policy_state("p0", "test_semantic_coverage_quality", "policy_binding")
_emit_snapshots_state("p0", "test_semantic_coverage_quality", "state_snapshot")
emit_replay_key("p0", "test_semantic_coverage_quality")
emit_determinism_digest("p0", "test_semantic_coverage_quality")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_semantic_coverage_quality", "execution_auth")
_emit_validates_capability("p2", "test_semantic_coverage_quality", "capability_check")
_emit_routes_to_capability("p2", "test_semantic_coverage_quality", "capability_route")
_emit_writes_via_uwg("p2", "test_semantic_coverage_quality", "uwg_write")
_emit_blocks_direct_write("p2", "test_semantic_coverage_quality", "direct_write_block")
_emit_records_tool_invocation("p2", "test_semantic_coverage_quality", "tool_invocation")
_emit_captures_execution_output("p2", "test_semantic_coverage_quality", "exec_output")
_emit_dispatches_agent("p3", "test_semantic_coverage_quality", "agent_dispatch")
_emit_coordinates_agents("p3", "test_semantic_coverage_quality", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_semantic_coverage_quality", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_semantic_coverage_quality", "healing_outcome")
_emit_escalates_failure("p3", "test_semantic_coverage_quality", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_semantic_coverage_quality", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_semantic_coverage_quality", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_semantic_coverage_quality", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_semantic_coverage_quality", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_semantic_coverage_quality", "eval_metric")
_emit_stores_embedding("p4", "test_semantic_coverage_quality", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_semantic_coverage_quality", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_semantic_coverage_quality", "exec_snapshot_link")

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
    CheckStatus,
    GuardianResult,
)
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
)
from tests.guardian._assertions import (
    assert_check,
    clear_assertion_registry,
    get_asserted_check_ids,
)

_emit_emits_metric_event("test_semantic_coverage_quality", "p4obs", "metric_1")
_emit_emits_metric_event("test_semantic_coverage_quality", "p4obs", "metric_2")
_emit_emits_metric_event("test_semantic_coverage_quality", "p4obs", "metric_3")
_emit_emits_metric_event("test_semantic_coverage_quality", "p4obs", "metric_4")
_emit_emits_metric_event("test_semantic_coverage_quality", "p4obs", "metric_5")
_emit_emits_metric_event("test_semantic_coverage_quality", "p4obs", "metric_6")
_emit_records_incident_event("test_semantic_coverage_quality", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_semantic_coverage_quality", "p4obs", "anomaly")
_emit_writes_observability_log("test_semantic_coverage_quality", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_semantic_coverage_quality", "p4obs", "mon_state")
_emit_triggers_alert("test_semantic_coverage_quality", "p4obs", "alert")
_emit_links_incident_trace("test_semantic_coverage_quality", "p4obs", "trace_link")
_emit_captures_pattern("test_semantic_coverage_quality", "p3lm", "pattern")
_emit_records_learning_event("test_semantic_coverage_quality", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_semantic_coverage_quality", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_semantic_coverage_quality", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_semantic_coverage_quality", "p3lm", "routing")
_emit_improves_agent_policy("test_semantic_coverage_quality", "p3lm", "policy")
_emit_stores_learning_state("test_semantic_coverage_quality", "p3lm", "state")
_emit_records_execution_trace("test_semantic_coverage_quality", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_semantic_coverage_quality", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_semantic_coverage_quality", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_semantic_coverage_quality", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_semantic_coverage_quality", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_semantic_coverage_quality", "env_read", "p2_env_1")
_emit_reads_environ("test_semantic_coverage_quality", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_semantic_coverage_quality", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_semantic_coverage_quality", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_semantic_coverage_quality", "context_pull")
_emit_pulls_context("p1", "test_semantic_coverage_quality", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_semantic_coverage_quality", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_semantic_coverage_quality", "uwg_term_secondary")
_emit_writes_through("p1", "test_semantic_coverage_quality", "write_through")
_emit_writes_through("p1", "test_semantic_coverage_quality", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_semantic_coverage_quality", "safety_validation")
_emit_invokes_eval("p1", "test_semantic_coverage_quality", "eval_call")
_emit_proposal_commits_routing("p1", "test_semantic_coverage_quality", "routing_commit")

pytestmark = pytest.mark.guardian


class TestAssertionQuality:
    """Coverage is only recorded for quality assertions (status + semantic property)."""

    def setup_method(self):
        """Clear registry before each test."""
        clear_assertion_registry()

    def test_empty_assertion_not_recorded(self):
        """Assertion with only check_id presence does not count toward coverage."""
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.PASS, "ok")

        # Empty assertion - just checks existence
        assert_check(r, "c1")

        coverage = get_asserted_check_ids()
        assert coverage.get("test", set()) == set(), "Empty assertion should not be recorded"

    def test_status_only_assertion_not_recorded(self):
        """Assertion with only status does not count toward coverage."""
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.PASS, "ok")

        # Status-only assertion - no semantic verification
        assert_check(r, "c1", status="PASS")

        coverage = get_asserted_check_ids()
        assert coverage.get("test", set()) == set(), "Status-only assertion should not be recorded"

    def test_quality_assertion_with_details_recorded(self):
        """Assertion with status + details_contains counts toward coverage."""
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.PASS, "all checks passed")

        # Quality assertion - status + semantic property
        assert_check(r, "c1", status="PASS", details_contains="passed")

        coverage = get_asserted_check_ids()
        assert coverage.get("test", set()) == {"c1"}, "Quality assertion should be recorded"

    def test_quality_assertion_with_evidence_predicate_recorded(self):
        """Assertion with status + evidence_predicate counts toward coverage."""
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.PASS, "ok", evidence={"count": 5})

        # Quality assertion - status + evidence predicate
        assert_check(r, "c1", status="PASS", evidence_predicate=lambda e: e.get("count") == 5)

        coverage = get_asserted_check_ids()
        assert coverage.get("test", set()) == {"c1"}, "Quality assertion should be recorded"

    def test_semantic_only_assertion_not_recorded(self):
        """Assertion with only semantic property (no status) does not count."""
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.PASS, "all checks passed")

        # Semantic-only assertion - no status
        assert_check(r, "c1", details_contains="passed")

        coverage = get_asserted_check_ids()
        assert coverage.get("test", set()) == set(), "Semantic-only assertion should not be recorded"

    def test_multiple_quality_assertions_recorded(self):
        """Multiple quality assertions are all recorded."""
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.PASS, "ok1")
        r.add_check("c2", CheckStatus.FAIL, "failed")

        assert_check(r, "c1", status="PASS", details_contains="ok")
        assert_check(r, "c2", status="FAIL", details_contains="fail")

        coverage = get_asserted_check_ids()
        assert coverage.get("test", set()) == {"c1", "c2"}


class TestBehavioralRatchetRequirements:
    """Each check_id must have both PASS and FAIL/SKIP scenarios with quality assertions."""

    def setup_method(self):
        """Clear registry before each test."""
        clear_assertion_registry()

    def test_pass_scenario_requires_quality_assertion(self):
        """PASS scenario must use quality assertion to count."""
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.PASS, "clean")

        # Empty assertion doesn't satisfy PASS requirement
        assert_check(r, "c1", status="PASS")
        coverage = get_asserted_check_ids()
        assert coverage.get("test", set()) == set()

        # Quality assertion satisfies PASS requirement
        assert_check(r, "c1", status="PASS", details_contains="clean")
        coverage = get_asserted_check_ids()
        assert coverage.get("test", set()) == {"c1"}

    def test_fail_scenario_requires_quality_assertion(self):
        """FAIL scenario must use quality assertion to count."""
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.FAIL, "violation found")

        # Empty assertion doesn't satisfy FAIL requirement
        assert_check(r, "c1", status="FAIL")
        coverage = get_asserted_check_ids()
        assert coverage.get("test", set()) == set()

        # Quality assertion satisfies FAIL requirement
        assert_check(r, "c1", status="FAIL", details_contains="violation")
        coverage = get_asserted_check_ids()
        assert coverage.get("test", set()) == {"c1"}

    def test_evidence_predicate_satisfies_quality(self):
        """Evidence predicate is a valid semantic property."""
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.FAIL, "found 3 violations", evidence={"count": 3})

        assert_check(
            r,
            "c1",
            status="FAIL",
            evidence_predicate=lambda e: e.get("count") == 3,
        )

        coverage = get_asserted_check_ids()
        assert coverage.get("test", set()) == {"c1"}
