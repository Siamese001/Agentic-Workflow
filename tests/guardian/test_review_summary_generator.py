"""V15 P10.1 — Review Summary Generator Tests.

Validates deterministic markdown output, missing-file handling, and
approval decision logic using tmp_path fixtures with fake evidence JSON.
"""

from __future__ import annotations

import json
from pathlib import Path

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

# REMOVED: _emit_authorize_and_execute("p2", "test_review_summary_generator", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_review_summary_generator", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_review_summary_generator", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_review_summary_generator", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_review_summary_generator", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_review_summary_generator", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_review_summary_generator", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_review_summary_generator", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_review_summary_generator", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_review_summary_generator", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_review_summary_generator", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_review_summary_generator", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_review_summary_generator", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_review_summary_generator", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_review_summary_generator", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_review_summary_generator", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_review_summary_generator", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_review_summary_generator", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_review_summary_generator", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_review_summary_generator", "exec_snapshot_link")
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
from ops_scripts.review.generate_v15_review_summary import generate_summary

# REMOVED: _emit_emits_metric_event("test_review_summary_generator", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_review_summary_generator", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_review_summary_generator", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_review_summary_generator", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_review_summary_generator", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_review_summary_generator", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_review_summary_generator", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_review_summary_generator", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_review_summary_generator", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_review_summary_generator", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_review_summary_generator", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_review_summary_generator", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_review_summary_generator", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_review_summary_generator", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_review_summary_generator", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_review_summary_generator", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_review_summary_generator", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_review_summary_generator", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_review_summary_generator", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_review_summary_generator", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_review_summary_generator", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_review_summary_generator", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_review_summary_generator", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_review_summary_generator", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_review_summary_generator", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_review_summary_generator", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_review_summary_generator", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_review_summary_generator", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_review_summary_generator")
# REMOVED: _emit_applies_guardrail("p0", "test_review_summary_generator", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_review_summary_generator", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_review_summary_generator", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_review_summary_generator", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_review_summary_generator", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_review_summary_generator", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_review_summary_generator", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_review_summary_generator", "write_through")
# REMOVED: _emit_writes_through("p1", "test_review_summary_generator", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_review_summary_generator", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_review_summary_generator", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_review_summary_generator", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_review_summary_generator", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_review_summary_generator", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_review_summary_generator", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_review_summary_generator", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_review_summary_generator", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_review_summary_generator", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_review_summary_generator", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_review_summary_generator", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_review_summary_generator", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_review_summary_generator", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_review_summary_generator", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_review_summary_generator")
# REMOVED: _emit_gated_by_confidence("p1", "test_review_summary_generator", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_review_summary_generator")
# REMOVED: emit_determinism_digest("p0", "test_review_summary_generator")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ===========================================================================
# Fixtures
# ===========================================================================


def _write_evidence(tmp_path: Path, phase: str, passed: int, violations: int, gate: str = "test_gate"):
    """Write a minimal evidence JSON fixture."""
    data = {
        "phase": phase,
        "gate": gate,
        "passed": passed,
        "violations": violations,
        "total_checks": passed + violations,
        "blocking": False,
        "passed_details": [],
        "violation_details": [{"check": f"check_{i}", "detail": f"violation {i}"} for i in range(violations)],
    }
    p = tmp_path / f"v15_{phase.lower()}_evidence.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def _write_guardian(tmp_path: Path, status: str = "PASS", total: int = 88, passed: int = 88, failed: int = 0):
    """Write a minimal guardian_report.json fixture."""
    data = {
        "status": status,
        "violations": [],
        "metadata": {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "skipped_tests": 0,
            "failed_by_category": {},
        },
    }
    p = tmp_path / "guardian_report.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def _build_paths(tmp_path: Path, phases: list[str]):
    """Build evidence_files dict from tmp_path for given phases."""
    return {ph: tmp_path / f"v15_{ph.lower()}_evidence.json" for ph in phases}


# ===========================================================================
# A) Deterministic Content
# ===========================================================================


class TestDeterministicContent:
    """Validate fixed headings and key lines in generated markdown."""

    def test_all_present_all_pass(self, tmp_path):
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        """All evidence + guardian present and passing."""
        for ph in ["P3", "P4", "P5", "P6"]:
            _write_evidence(tmp_path, ph, passed=5, violations=0, gate=f"gate_{ph.lower()}")
        gp = _write_guardian(tmp_path)

        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        md, code = generate_summary(evidence_files=ev, guardian_report_paths=[gp])

        assert code == 0
        assert "# V15 Review Summary" in md
        assert "## 1. Inputs" in md
        assert "## 2. Gate Results" in md
        assert "## 3. Violation Details" in md
        assert "## 4. Guardian Report" in md
        assert "## 5. Approval Decision" in md
        assert "**Ready for human approval: YES**" in md
        assert "MISSING" not in md

    def test_headings_in_order(self, tmp_path):
        """Section headings appear in correct order."""
        for ph in ["P3", "P4", "P5", "P6"]:
            _write_evidence(tmp_path, ph, passed=3, violations=0)
        gp = _write_guardian(tmp_path)

        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])

        idx1 = md.index("## 1. Inputs")
        idx2 = md.index("## 2. Gate Results")
        idx3 = md.index("## 3. Violation Details")
        idx4 = md.index("## 4. Guardian Report")
        idx5 = md.index("## 5. Approval Decision")
        assert idx1 < idx2 < idx3 < idx4 < idx5

    def test_gate_table_rows(self, tmp_path):
        """Each phase gets a row in the gate results table."""
        for ph in ["P3", "P4", "P5", "P6"]:
            _write_evidence(tmp_path, ph, passed=4, violations=0, gate=f"gate_{ph}")
        gp = _write_guardian(tmp_path)

        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])

        for ph in ["P3", "P4", "P5", "P6"]:
            assert f"| {ph} |" in md

    def test_guardian_stats_shown(self, tmp_path):
        """Guardian report stats appear in output."""
        _write_evidence(tmp_path, "P3", passed=1, violations=0)
        gp = _write_guardian(tmp_path, total=100, passed=99, failed=1, status="FAIL")

        ev = _build_paths(tmp_path, ["P3"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])

        assert "**Total tests**: 100" in md
        assert "**Passed**: 99" in md
        assert "**Failed**: 1" in md


# ===========================================================================
# B) Violation Details
# ===========================================================================


class TestViolationDetails:
    """Violations from evidence must appear in section 3."""

    def test_violations_listed(self, tmp_path):
        """Violations appear with phase and check name."""
        _write_evidence(tmp_path, "P5", passed=4, violations=2, gate="authority")
        _write_evidence(tmp_path, "P3", passed=6, violations=0)
        gp = _write_guardian(tmp_path)

        ev = _build_paths(tmp_path, ["P3", "P5"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])

        assert "**P5** / `check_0`" in md
        assert "**P5** / `check_1`" in md

    def test_no_violations_message(self, tmp_path):
        """When no violations, explicit message shown."""
        _write_evidence(tmp_path, "P3", passed=5, violations=0)
        gp = _write_guardian(tmp_path)

        ev = _build_paths(tmp_path, ["P3"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])

        assert "No violations recorded." in md


# ===========================================================================
# C) Missing File Handling
# ===========================================================================


class TestMissingFileHandling:
    """Partial and total missing input scenarios."""

    def test_partial_missing_still_succeeds(self, tmp_path):
        """Some evidence missing: exit 0, MISSING shown in table."""
        _write_evidence(tmp_path, "P3", passed=5, violations=0)
        gp = _write_guardian(tmp_path)

        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        md, code = generate_summary(evidence_files=ev, guardian_report_paths=[gp])

        assert code == 0
        assert "**Missing**: P4, P5, P6" in md
        assert "| P4 | — | — | — | — | MISSING |" in md

    def test_guardian_missing_still_succeeds(self, tmp_path):
        """Guardian report missing: exit 0, noted in output."""
        _write_evidence(tmp_path, "P3", passed=5, violations=0)

        ev = _build_paths(tmp_path, ["P3"])
        md, code = generate_summary(
            evidence_files=ev,
            guardian_report_paths=[tmp_path / "nonexistent.json"],
        )

        assert code == 0
        assert "**Guardian report**: missing" in md
        assert "Guardian report not available." in md

    def test_all_missing_exits_nonzero(self, tmp_path):
        """ALL inputs missing: exit 1."""
        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        _, code = generate_summary(
            evidence_files=ev,
            guardian_report_paths=[tmp_path / "nonexistent.json"],
        )
        assert code == 1


# ===========================================================================
# D) Approval Decision Logic
# ===========================================================================


class TestApprovalDecision:
    """YES iff all gates pass AND guardian PASS; otherwise NO."""

    def test_all_pass_guardian_pass_yes(self, tmp_path):
        for ph in ["P3", "P4", "P5", "P6"]:
            _write_evidence(tmp_path, ph, passed=5, violations=0)
        gp = _write_guardian(tmp_path, status="PASS")

        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])
        assert "**Ready for human approval: YES**" in md

    def test_gate_violation_means_no(self, tmp_path):
        _write_evidence(tmp_path, "P3", passed=5, violations=0)
        _write_evidence(tmp_path, "P5", passed=4, violations=1)
        gp = _write_guardian(tmp_path, status="PASS")

        ev = _build_paths(tmp_path, ["P3", "P5"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])
        assert "**Ready for human approval: NO**" in md
        assert "gate failures" in md

    def test_guardian_fail_means_no(self, tmp_path):
        for ph in ["P3", "P4", "P5", "P6"]:
            _write_evidence(tmp_path, ph, passed=5, violations=0)
        gp = _write_guardian(tmp_path, status="FAIL", failed=2)

        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])
        assert "**Ready for human approval: NO**" in md
        assert "guardian report not PASS" in md

    def test_missing_evidence_means_no(self, tmp_path):
        _write_evidence(tmp_path, "P3", passed=5, violations=0)
        gp = _write_guardian(tmp_path, status="PASS")

        ev = _build_paths(tmp_path, ["P3", "P4"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])
        assert "**Ready for human approval: NO**" in md

    def test_guardian_missing_means_no(self, tmp_path):
        for ph in ["P3", "P4", "P5", "P6"]:
            _write_evidence(tmp_path, ph, passed=5, violations=0)

        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        md, _ = generate_summary(
            evidence_files=ev,
            guardian_report_paths=[tmp_path / "nonexistent.json"],
        )
        assert "**Ready for human approval: NO**" in md


# ===========================================================================
# E) Determinism
# ===========================================================================


class TestDeterminism:
    """Same inputs must produce identical output."""

    def test_repeated_calls_identical(self, tmp_path):
    """Test repeated_calls_identical runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute repeated_calls_identical
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
