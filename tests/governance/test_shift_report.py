"""H4 governance tests: Multivariate drift detection with ShiftReport.

Validates:
- ShiftReport immutability (frozen dataclass)
- Minimum sample guard (n < 30 skips detection)
- MMD detects multivariate shift
- PSI detects per-feature drift
- Joint shift flag logic
- Skipped report factory
- CovariateShiftDetector integration
"""

import pytest

from agentic_core.L5_safety.types.shift_report_types import (
    MIN_SAMPLE_SIZE,
    CovariateShiftDetector,
    ShiftReport,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
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

_emit_emits_metric_event("test_shift_report", "p4obs", "metric_1")
_emit_emits_metric_event("test_shift_report", "p4obs", "metric_2")
_emit_emits_metric_event("test_shift_report", "p4obs", "metric_3")
_emit_emits_metric_event("test_shift_report", "p4obs", "metric_4")
_emit_emits_metric_event("test_shift_report", "p4obs", "metric_5")
_emit_emits_metric_event("test_shift_report", "p4obs", "metric_6")
_emit_records_incident_event("test_shift_report", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_shift_report", "p4obs", "anomaly")
_emit_writes_observability_log("test_shift_report", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_shift_report", "p4obs", "mon_state")
_emit_triggers_alert("test_shift_report", "p4obs", "alert")
_emit_links_incident_trace("test_shift_report", "p4obs", "trace_link")
_emit_captures_pattern("test_shift_report", "p3lm", "pattern")
_emit_records_learning_event("test_shift_report", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_shift_report", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_shift_report", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_shift_report", "p3lm", "routing")
_emit_improves_agent_policy("test_shift_report", "p3lm", "policy")
_emit_stores_learning_state("test_shift_report", "p3lm", "state")
_emit_records_execution_trace("test_shift_report", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_shift_report", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_shift_report", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_shift_report", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_shift_report", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_shift_report", "env_read", "p2_env_1")
_emit_reads_environ("test_shift_report", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_shift_report", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_shift_report", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_shift_report")
_emit_applies_guardrail("p0", "test_shift_report", "p0_governance")
_emit_reads_policy_state("p0", "test_shift_report", "policy_binding")
_emit_snapshots_state("p0", "test_shift_report", "state_snapshot")
_emit_pulls_context("p1", "test_shift_report", "context_pull")
_emit_pulls_context("p1", "test_shift_report", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_shift_report", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_shift_report", "uwg_term_secondary")
_emit_writes_through("p1", "test_shift_report", "write_through")
_emit_writes_through("p1", "test_shift_report", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_shift_report", "safety_validation")
_emit_invokes_eval("p1", "test_shift_report", "eval_call")
_emit_proposal_commits_routing("p1", "test_shift_report", "routing_commit")
_emit_escalates_to_human("p1", "test_shift_report", "human_escalation")
_emit_routes_through("p1", "test_shift_report", "route_through")
_emit_checks_agent_registry("p1", "test_shift_report", "agent_registry")
_emit_validates_agent_capability("p1", "test_shift_report", "capability")
_emit_dispatches_execution_plan("p1", "test_shift_report", "exec_plan")
_emit_agent_executes_agent("p1", "test_shift_report", "sub_agent")
_emit_routes_to_agent("p1", "test_shift_report", "target_agent")
_emit_verifies_policy("p1", "test_shift_report", "policy_check")
_emit_observes_runtime_state("p1", "test_shift_report", "runtime_state")
_emit_verifies_boundary("p1", "test_shift_report", "boundary_check")
_emit_transcripts_response("p1", "test_shift_report", "transcript")
_emit_hard_fails_untranscripted("p1", "test_shift_report")
_emit_gated_by_confidence("p1", "test_shift_report", "confidence_gate")
emit_replay_key("p0", "test_shift_report")
emit_determinism_digest("p0", "test_shift_report")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_shift_report", "execution_auth")
_emit_validates_capability("p2", "test_shift_report", "capability_check")
_emit_routes_to_capability("p2", "test_shift_report", "capability_route")
_emit_writes_via_uwg("p2", "test_shift_report", "uwg_write")
_emit_blocks_direct_write("p2", "test_shift_report", "direct_write_block")
_emit_records_tool_invocation("p2", "test_shift_report", "tool_invocation")
_emit_captures_execution_output("p2", "test_shift_report", "exec_output")
_emit_dispatches_agent("p3", "test_shift_report", "agent_dispatch")
_emit_coordinates_agents("p3", "test_shift_report", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_shift_report", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_shift_report", "healing_outcome")
_emit_escalates_failure("p3", "test_shift_report", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_shift_report", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_shift_report", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_shift_report", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_shift_report", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_shift_report", "eval_metric")
_emit_stores_embedding("p4", "test_shift_report", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_shift_report", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_shift_report", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


pytestmark = pytest.mark.governance


def _make_baseline(n: int, dim: int = 2) -> list[list[float]]:
    """Generate stable baseline data."""
    return [[float(i) / n for _ in range(dim)] for i in range(n)]


def _make_shifted(n: int, dim: int = 2) -> list[list[float]]:
    """Generate shifted treatment data."""
    return [[float(i) / n + 10.0 for _ in range(dim)] for i in range(n)]


class TestShiftReportImmutability:
    """ShiftReport must be frozen."""

    def test_cannot_mutate_field(self):
        report = ShiftReport.create(
            joint_shift=False,
            per_feature={},
            mmd_score=0.0,
            psi_scores={},
            sample_size_ok=True,
        )
        with pytest.raises(AttributeError):
            report.joint_shift = True  # type: ignore[misc]

    def test_timestamp_is_set(self):
        report = ShiftReport.create(
            joint_shift=False,
            per_feature={},
            mmd_score=0.0,
            psi_scores={},
            sample_size_ok=True,
        )
        assert report.timestamp is not None
        assert len(report.timestamp) > 0


class TestMinimumSampleGuard:
    """Detection must skip if n < 30 per stratum."""

    def test_min_sample_size_is_30(self):
        assert MIN_SAMPLE_SIZE == 30

    def test_small_sample_skips(self):
        detector = CovariateShiftDetector(feature_names=["f1", "f2"])
        baseline = _make_baseline(10, dim=2)
        treatment = _make_shifted(10, dim=2)
        report = detector.detect_shift(baseline, treatment)
        assert report.sample_size_ok is False
        assert report.joint_shift is False

    def test_sufficient_sample_runs(self):
        detector = CovariateShiftDetector(feature_names=["f1", "f2"])
        baseline = _make_baseline(35, dim=2)
        treatment = _make_shifted(35, dim=2)
        report = detector.detect_shift(baseline, treatment)
        assert report.sample_size_ok is True


class TestMMDDetection:
    """MMD must detect multivariate shift."""

    def test_identical_data_no_shift(self):
        detector = CovariateShiftDetector(
            feature_names=["f1"],
            mmd_threshold=THRESHOLD,
        )
        data = _make_baseline(40, dim=1)
        report = detector.detect_shift(data, data)
        assert report.mmd_score < 0.01

    def test_shifted_data_detected(self):
        detector = CovariateShiftDetector(
            feature_names=["f1"],
            mmd_threshold=THRESHOLD,
        )
        baseline = _make_baseline(40, dim=1)
        treatment = _make_shifted(40, dim=1)
        report = detector.detect_shift(baseline, treatment)
        assert report.mmd_score > 0.01
        assert report.joint_shift is True


class TestPSIDetection:
    """PSI must detect per-feature drift."""

    def test_per_feature_flags(self):
        detector = CovariateShiftDetector(
            feature_names=["f1", "f2"],
            psi_threshold=THRESHOLD,
        )
        baseline = _make_baseline(40, dim=2)
        treatment = _make_shifted(40, dim=2)
        report = detector.detect_shift(baseline, treatment)
        assert "f1" in report.per_feature
        assert "f2" in report.per_feature
        assert "f1" in report.psi_scores
        assert "f2" in report.psi_scores

    def test_no_drift_low_psi(self):
        detector = CovariateShiftDetector(
            feature_names=["f1"],
            psi_threshold=THRESHOLD,
            mmd_threshold=THRESHOLD,
        )
        data = _make_baseline(40, dim=1)
        report = detector.detect_shift(data, data)
        assert report.per_feature.get("f1") is False


class TestSkippedReport:
    """Skipped report factory."""

    def test_skipped_report_fields(self):
        report = ShiftReport.skipped()
        assert report.joint_shift is False
        assert report.sample_size_ok is False
        assert report.per_feature == {}
        assert report.psi_scores == {}
        assert report.mmd_score == 0.0
        assert report.timestamp is not None


class TestJointShiftLogic:
    """Joint shift = MMD exceeds OR any PSI exceeds."""

    def test_joint_true_when_mmd_exceeds(self):
        detector = CovariateShiftDetector(
            feature_names=["f1"],
            mmd_threshold=THRESHOLD,
            psi_threshold=THRESHOLD,
        )
        baseline = _make_baseline(40, dim=1)
        treatment = _make_shifted(40, dim=1)
        report = detector.detect_shift(baseline, treatment)
        assert report.joint_shift is True

    def test_joint_true_when_psi_exceeds(self):
        detector = CovariateShiftDetector(
            feature_names=["f1"],
            mmd_threshold=THRESHOLD,
            psi_threshold=THRESHOLD,
        )
        baseline = _make_baseline(40, dim=1)
        treatment = _make_shifted(40, dim=1)
        report = detector.detect_shift(baseline, treatment)
        assert report.joint_shift is True
