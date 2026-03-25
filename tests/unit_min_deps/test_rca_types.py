"""Unit tests for system_learning.types.rca_types."""

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

# REMOVED: _emit_authorize_and_execute("p2", "test_rca_types", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_rca_types", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_rca_types", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_rca_types", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_rca_types", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_rca_types", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_rca_types", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_rca_types", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_rca_types", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_rca_types", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_rca_types", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_rca_types", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_rca_types", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_rca_types", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_rca_types", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_rca_types", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_rca_types", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_rca_types", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_rca_types", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_rca_types", "exec_snapshot_link")
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
from system_learning.types.rca_types import (
    RCAFinding,
    canonical_bytes,
    compute_report_hash,
    create_rca_report,
)

# REMOVED: _emit_emits_metric_event("test_rca_types", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_rca_types", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_rca_types", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_rca_types", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_rca_types", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_rca_types", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_rca_types", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_rca_types", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_rca_types", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_rca_types", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_rca_types", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_rca_types", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_rca_types", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_rca_types", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_rca_types", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_rca_types", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_rca_types", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_rca_types", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_rca_types", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_rca_types", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_rca_types", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_rca_types", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_rca_types", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_rca_types", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_rca_types", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_rca_types", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_rca_types", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_rca_types", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_rca_types")
# REMOVED: _emit_applies_guardrail("p0", "test_rca_types", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_rca_types", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_rca_types", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_rca_types", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_rca_types", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_rca_types", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_rca_types", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_rca_types", "write_through")
# REMOVED: _emit_writes_through("p1", "test_rca_types", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_rca_types", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_rca_types", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_rca_types", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_rca_types", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_rca_types", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_rca_types", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_rca_types", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_rca_types", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_rca_types", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_rca_types", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_rca_types", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_rca_types", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_rca_types", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_rca_types", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_rca_types")
# REMOVED: _emit_gated_by_confidence("p1", "test_rca_types", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_rca_types")
# REMOVED: emit_determinism_digest("p0", "test_rca_types")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


class TestRCATypes:
    def test_deterministic_hash_stability(self):
        """Same inputs produce identical report_hash across two constructions."""
        findings = (
            RCAFinding(
                category="SYNTAX",
                signature="SyntaxError",
                count=5,
                evidence_hash="abc123",
            ),
            RCAFinding(
                category="IMPORT",
                signature="ModuleNotFoundError",
                count=2,
                evidence_hash="def456",
            ),
        )

        report1 = create_rca_report(
            snapshot_id="snap123",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings,
        )

        report2 = create_rca_report(
            snapshot_id="snap123",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings,
        )

        assert report1.report_hash == report2.report_hash
        assert report1.report_id == report2.report_id
        assert report1.report_id == report1.report_hash

    def test_findings_ordering_canonical(self):
        """Findings are sorted deterministically by (category, signature)."""
        # Create findings in non-canonical order
        findings = (
            RCAFinding(
                category="SYNTAX",
                signature="SyntaxError",
                count=5,
                evidence_hash="abc123",
            ),
            RCAFinding(
                category="IMPORT",
                signature="ModuleNotFoundError",
                count=2,
                evidence_hash="def456",
            ),
        )

        report = create_rca_report(
            snapshot_id="snap123",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings,
        )

        # Canonical bytes should sort findings
        canonical = canonical_bytes(report)

        # IMPORT should come before SYNTAX alphabetically
        assert b"IMPORT" in canonical
        assert b"SYNTAX" in canonical
        assert canonical.index(b"IMPORT") < canonical.index(b"SYNTAX")

    def test_changing_evidence_changes_hash(self):
        """Changing one byte in evidence changes report_hash."""
        findings1 = (
            RCAFinding(
                category="SYNTAX",
                signature="SyntaxError",
                count=5,
                evidence_hash="abc123",
            ),
        )

        findings2 = (
            RCAFinding(
                category="SYNTAX",
                signature="SyntaxError",
                count=5,
                evidence_hash="abc124",  # Changed last byte
            ),
        )

        report1 = create_rca_report(
            snapshot_id="snap123",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings1,
        )

        report2 = create_rca_report(
            snapshot_id="snap123",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings2,
        )

        assert report1.report_hash != report2.report_hash

    def test_report_id_equals_report_hash(self):
        """report_id is always equal to report_hash."""
        findings = (
            RCAFinding(
                category="TIMEOUT",
                signature="TimeoutError",
                count=1,
                evidence_hash="xyz789",
            ),
        )

        report = create_rca_report(
            snapshot_id="snap456",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings,
        )

        assert report.report_id == report.report_hash


class TestDeterminism:
    def test_canonical_bytes_deterministic(self):
        """canonical_bytes produces identical output for same report."""
        findings = (
            RCAFinding(
                category="SYNTAX",
                signature="SyntaxError",
                count=5,
                evidence_hash="abc123",
            ),
            RCAFinding(
                category="IMPORT",
                signature="ModuleNotFoundError",
                count=2,
                evidence_hash="def456",
            ),
        )

        report = create_rca_report(
            snapshot_id="snap123",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings,
        )

        canonical1 = canonical_bytes(report)
        canonical2 = canonical_bytes(report)
        canonical3 = canonical_bytes(report)

        assert canonical1 == canonical2 == canonical3

    def test_compute_report_hash_deterministic(self):
        """compute_report_hash produces identical output for same report."""
        findings = (
            RCAFinding(
                category="SYNTAX",
                signature="SyntaxError",
                count=5,
                evidence_hash="abc123",
            ),
        )

        report = create_rca_report(
            snapshot_id="snap123",
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            findings=findings,
        )

        hash1 = compute_report_hash(report)
        hash2 = compute_report_hash(report)
        hash3 = compute_report_hash(report)

        assert hash1 == hash2 == hash3
