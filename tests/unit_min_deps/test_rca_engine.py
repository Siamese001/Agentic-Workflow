"""Unit tests for system_learning.engines.rca_engine."""

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "test_rca_engine", "execution_auth")
_emit_validates_capability("p2", "test_rca_engine", "capability_check")
_emit_routes_to_capability("p2", "test_rca_engine", "capability_route")
_emit_writes_via_uwg("p2", "test_rca_engine", "uwg_write")
_emit_blocks_direct_write("p2", "test_rca_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "test_rca_engine", "tool_invocation")
_emit_captures_execution_output("p2", "test_rca_engine", "exec_output")
_emit_dispatches_agent("p3", "test_rca_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "test_rca_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_rca_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_rca_engine", "healing_outcome")
_emit_escalates_failure("p3", "test_rca_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_rca_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_rca_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_rca_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_rca_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_rca_engine", "eval_metric")
_emit_stores_embedding("p4", "test_rca_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_rca_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_rca_engine", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
from system_learning.engines.rca_engine import RCAAnalysisError, analyze_failures

_emit_emits_metric_event("test_rca_engine", "p4obs", "metric_1")
_emit_emits_metric_event("test_rca_engine", "p4obs", "metric_2")
_emit_emits_metric_event("test_rca_engine", "p4obs", "metric_3")
_emit_emits_metric_event("test_rca_engine", "p4obs", "metric_4")
_emit_emits_metric_event("test_rca_engine", "p4obs", "metric_5")
_emit_emits_metric_event("test_rca_engine", "p4obs", "metric_6")
_emit_records_incident_event("test_rca_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_rca_engine", "p4obs", "anomaly")
_emit_writes_observability_log("test_rca_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_rca_engine", "p4obs", "mon_state")
_emit_triggers_alert("test_rca_engine", "p4obs", "alert")
_emit_links_incident_trace("test_rca_engine", "p4obs", "trace_link")
_emit_captures_pattern("test_rca_engine", "p3lm", "pattern")
_emit_records_learning_event("test_rca_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_rca_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_rca_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_rca_engine", "p3lm", "routing")
_emit_improves_agent_policy("test_rca_engine", "p3lm", "policy")
_emit_stores_learning_state("test_rca_engine", "p3lm", "state")
_emit_records_execution_trace("test_rca_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_rca_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_rca_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_rca_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_rca_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_rca_engine", "env_read", "p2_env_1")
_emit_reads_environ("test_rca_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_rca_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_rca_engine", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_rca_engine")
_emit_applies_guardrail("p0", "test_rca_engine", "p0_governance")
_emit_reads_policy_state("p0", "test_rca_engine", "policy_binding")
_emit_snapshots_state("p0", "test_rca_engine", "state_snapshot")
_emit_pulls_context("p1", "test_rca_engine", "context_pull")
_emit_pulls_context("p1", "test_rca_engine", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_rca_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_rca_engine", "uwg_term_secondary")
_emit_writes_through("p1", "test_rca_engine", "write_through")
_emit_writes_through("p1", "test_rca_engine", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_rca_engine", "safety_validation")
_emit_invokes_eval("p1", "test_rca_engine", "eval_call")
_emit_proposal_commits_routing("p1", "test_rca_engine", "routing_commit")
_emit_escalates_to_human("p1", "test_rca_engine", "human_escalation")
_emit_routes_through("p1", "test_rca_engine", "route_through")
_emit_checks_agent_registry("p1", "test_rca_engine", "agent_registry")
_emit_validates_agent_capability("p1", "test_rca_engine", "capability")
_emit_dispatches_execution_plan("p1", "test_rca_engine", "exec_plan")
_emit_agent_executes_agent("p1", "test_rca_engine", "sub_agent")
_emit_routes_to_agent("p1", "test_rca_engine", "target_agent")
_emit_verifies_policy("p1", "test_rca_engine", "policy_check")
_emit_observes_runtime_state("p1", "test_rca_engine", "runtime_state")
_emit_verifies_boundary("p1", "test_rca_engine", "boundary_check")
_emit_transcripts_response("p1", "test_rca_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "test_rca_engine")
_emit_gated_by_confidence("p1", "test_rca_engine", "confidence_gate")
emit_replay_key("p0", "test_rca_engine")
emit_determinism_digest("p0", "test_rca_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps


# Synthetic audit slice fixture
AUDIT_SLICE_FIXTURE = b"""
SyntaxError: invalid syntax
SyntaxError: unexpected EOF
ModuleNotFoundError: No module named 'foo'
ImportError: cannot import name 'bar'
ERROR collecting tests/test_example.py
TimeoutError: operation timed out
SyntaxError: invalid syntax
SourceMutationBlocked: cannot modify protected file
"""


class TestRCAEngine:
    def test_analyze_failures_basic(self):
        """Basic RCA analysis produces expected findings."""
        report = analyze_failures(
            snapshot_id="snap123",
            audit_slice=AUDIT_SLICE_FIXTURE,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        # Should have findings for multiple categories
        assert len(report.findings) > 0

        # Check that we have expected categories
        categories = {f.category for f in report.findings}
        assert "SYNTAX" in categories
        assert "IMPORT" in categories
        assert "TEST_DISCOVERY" in categories
        assert "TIMEOUT" in categories
        assert "POLICY_BLOCK" in categories

    def test_exact_findings_counts(self):
        """Exact findings match expected categories, signatures, and counts."""
        report = analyze_failures(
            snapshot_id="snap123",
            audit_slice=AUDIT_SLICE_FIXTURE,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        # Build a dict for easier assertion
        findings_dict = {(f.category, f.signature): f.count for f in report.findings}

        # SYNTAX: 3 occurrences
        assert findings_dict.get(("SYNTAX", "SyntaxError")) == 3

        # IMPORT: 1 ModuleNotFoundError + 1 ImportError
        assert findings_dict.get(("IMPORT", "ModuleNotFoundError")) == 1
        assert findings_dict.get(("IMPORT", "ImportError")) == 1

        # TEST_DISCOVERY: 1 occurrence
        assert findings_dict.get(("TEST_DISCOVERY", "pytest_collection_error")) == 1

        # TIMEOUT: 1 occurrence
        assert findings_dict.get(("TIMEOUT", "TimeoutError")) == 1

        # POLICY_BLOCK: 1 occurrence
        assert findings_dict.get(("POLICY_BLOCK", "SourceMutationBlocked")) == 1

    def test_determinism_same_slice_identical_report_id(self):
        """Same audit_slice produces identical report_id."""
        report1 = analyze_failures(
            snapshot_id="snap123",
            audit_slice=AUDIT_SLICE_FIXTURE,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        report2 = analyze_failures(
            snapshot_id="snap123",
            audit_slice=AUDIT_SLICE_FIXTURE,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        assert report1.report_id == report2.report_id
        assert report1.report_hash == report2.report_hash

    def test_invalid_window_rejected(self):
        """Invalid window (start >= end) raises RCAAnalysisError."""
        with pytest.raises(RCAAnalysisError, match="Invalid window"):
            analyze_failures(
                snapshot_id="snap123",
                audit_slice=AUDIT_SLICE_FIXTURE,
                window_start_utc=1700003600,
                window_end_utc=1700000000,  # end < start
            )

    def test_malformed_utf8_rejected(self):
        """Malformed UTF-8 raises RCAAnalysisError."""
        malformed_bytes = b"\xff\xfe invalid utf-8"

        with pytest.raises(RCAAnalysisError, match="Failed to decode"):
            analyze_failures(
                snapshot_id="snap123",
                audit_slice=malformed_bytes,
                window_start_utc=1700000000,
                window_end_utc=1700003600,
            )

    def test_empty_slice_produces_unknown_category(self):
        """Empty audit slice produces UNKNOWN category."""
        report = analyze_failures(
            snapshot_id="snap123",
            audit_slice=b"",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        # Should have one finding with UNKNOWN category
        assert len(report.findings) == 1
        assert report.findings[0].category == "UNKNOWN"
        assert report.findings[0].signature == "no_patterns_matched"

    def test_no_matching_patterns_produces_unknown(self):
        """Audit slice with no matching patterns produces UNKNOWN."""
        report = analyze_failures(
            snapshot_id="snap123",
            audit_slice=b"some random text\nwith no patterns\n",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        # Should have one finding with UNKNOWN category
        assert len(report.findings) == 1
        assert report.findings[0].category == "UNKNOWN"


class TestDeterminism:
    def test_analyze_failures_deterministic(self):
        """analyze_failures produces identical results across multiple calls."""
        report1 = analyze_failures(
            snapshot_id="snap123",
            audit_slice=AUDIT_SLICE_FIXTURE,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        report2 = analyze_failures(
            snapshot_id="snap123",
            audit_slice=AUDIT_SLICE_FIXTURE,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        report3 = analyze_failures(
            snapshot_id="snap123",
            audit_slice=AUDIT_SLICE_FIXTURE,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
        )

        assert report1.report_id == report2.report_id == report3.report_id
        assert report1.report_hash == report2.report_hash == report3.report_hash
