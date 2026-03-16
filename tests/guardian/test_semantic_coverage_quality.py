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
from tests.guardian._assertions import (
    assert_check,
    clear_assertion_registry,
    get_asserted_check_ids,
)

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
