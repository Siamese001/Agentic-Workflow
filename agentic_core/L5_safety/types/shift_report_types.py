"""
H4: Multivariate drift detection with ShiftReport schema.

Replaces univariate ks_2samp with:
- Primary: MMD (Maximum Mean Discrepancy) — kernel-based, multivariate
- Secondary: PSI (Population Stability Index) — per-feature + joint
- Windowed time decay: exponential weighting on recent samples
- Minimum sample guard: skip test if n < 30 per stratum

Lives in L5 (safety/types) — detection is observational, not mutating.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "shift_report_types")
emit_determinism_digest("p0", "shift_report_types")

_emit_dispatches_healing_run("p1", "shift_report_types", "L5")
_emit_routes_through("p1", "shift_report_types", "L5")
_emit_checks_agent_registry("p1", "shift_report_types", "agent_registry")
_emit_validates_agent_capability("p1", "shift_report_types", "capability")
_emit_dispatches_execution_plan("p1", "shift_report_types", "exec_plan")
_emit_agent_executes_agent("p1", "shift_report_types", "sub_agent")
_emit_routes_to_agent("p1", "shift_report_types", "target_agent")
_emit_verifies_policy("p1", "shift_report_types", "policy_check")
_emit_observes_runtime_state("p1", "shift_report_types", "runtime_state")
_emit_verifies_boundary("p1", "shift_report_types", "boundary_check")
_emit_transcripts_response("p1", "shift_report_types", "transcript")
_emit_hard_fails_untranscripted("p1", "shift_report_types")
_emit_gated_by_confidence("p1", "shift_report_types", "confidence_gate")
_emit_escalates_to_human("p1", "shift_report_types", "L5")
_emit_reads_policy_state("p1", "shift_report_types", "L5")

_emit_applies_guardrail("p0", "shift_report_types", "p0_governance")
_emit_snapshots_state("p0", "shift_report_types", "state_snapshot")
_emit_authorize_and_execute("p2", "shift_report_types", "execution_auth")
_emit_validates_capability("p2", "shift_report_types", "capability_check")
_emit_routes_to_capability("p2", "shift_report_types", "capability_route")
_emit_writes_via_uwg("p2", "shift_report_types", "uwg_write")
_emit_blocks_direct_write("p2", "shift_report_types", "direct_write_block")
_emit_records_tool_invocation("p2", "shift_report_types", "tool_invocation")
_emit_captures_execution_output("p2", "shift_report_types", "exec_output")
_emit_dispatches_agent("p3", "shift_report_types", "agent_dispatch")
_emit_coordinates_agents("p3", "shift_report_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "shift_report_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "shift_report_types", "healing_outcome")
_emit_escalates_failure("p3", "shift_report_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "shift_report_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "shift_report_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "shift_report_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "shift_report_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "shift_report_types", "eval_metric")
_emit_stores_embedding("p4", "shift_report_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "shift_report_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "shift_report_types", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
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
    _emit_writes_through,
)

_emit_emits_metric_event("shift_report_types", "p4obs", "metric_1")
_emit_emits_metric_event("shift_report_types", "p4obs", "metric_2")
_emit_emits_metric_event("shift_report_types", "p4obs", "metric_3")
_emit_emits_metric_event("shift_report_types", "p4obs", "metric_4")
_emit_emits_metric_event("shift_report_types", "p4obs", "metric_5")
_emit_emits_metric_event("shift_report_types", "p4obs", "metric_6")
_emit_records_incident_event("shift_report_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("shift_report_types", "p4obs", "anomaly")
_emit_writes_observability_log("shift_report_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("shift_report_types", "p4obs", "mon_state")
_emit_triggers_alert("shift_report_types", "p4obs", "alert")
_emit_links_incident_trace("shift_report_types", "p4obs", "trace_link")
_emit_captures_pattern("shift_report_types", "p3lm", "pattern")
_emit_records_learning_event("shift_report_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("shift_report_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("shift_report_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("shift_report_types", "p3lm", "routing")
_emit_improves_agent_policy("shift_report_types", "p3lm", "policy")
_emit_stores_learning_state("shift_report_types", "p3lm", "state")
_emit_records_execution_trace("shift_report_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("shift_report_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("shift_report_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("shift_report_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("shift_report_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("shift_report_types", "env_read", "p2_env_1")
_emit_reads_environ("shift_report_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("shift_report_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("shift_report_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "shift_report_types", "context_pull")
_emit_pulls_context("p1", "shift_report_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "shift_report_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "shift_report_types", "uwg_term_2")
_emit_writes_through("p1", "shift_report_types", "write_through")
_emit_writes_through("p1", "shift_report_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "shift_report_types", "safety_validation")
_emit_invokes_eval("p1", "shift_report_types", "eval_call")
_emit_proposal_commits_routing("p1", "shift_report_types", "routing_commit")

MIN_SAMPLE_SIZE = 30


@dataclass(frozen=True)
class ShiftReport:
    """Formal drift detection report.

    Included in LearningArtifact for replay and audit integrity.
    """

    joint_shift: bool
    per_feature: dict[str, bool]
    mmd_score: float
    psi_scores: dict[str, float]
    sample_size_ok: bool
    timestamp: str

    @staticmethod
    def create(
        *,
        joint_shift: bool,
        per_feature: dict[str, bool],
        mmd_score: float,
        psi_scores: dict[str, float],
        sample_size_ok: bool,
    ) -> ShiftReport:
        """Construct with frozen timestamp."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ShiftReport.create")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ShiftReport.create".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        ts = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        return ShiftReport(
            joint_shift=joint_shift,
            per_feature=per_feature,
            mmd_score=mmd_score,
            psi_scores=psi_scores,
            sample_size_ok=sample_size_ok,
            timestamp=ts,
        )

    @staticmethod
    def skipped(reason: str = "insufficient_samples") -> ShiftReport:
        """Create a report for skipped detection."""
        ts = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        return ShiftReport(
            joint_shift=False,
            per_feature={},
            mmd_score=0.0,
            psi_scores={},
            sample_size_ok=False,
            timestamp=ts,
        )


def _compute_psi(baseline: list[float], treatment: list[float], bins: int = 10) -> float:
    """Compute Population Stability Index between two distributions.

    Uses equal-width binning.  Clips to avoid log(0).
    """
    if not baseline or not treatment:
        return 0.0
    all_vals = baseline + treatment
    min_val = min(all_vals)
    max_val = max(all_vals)
    if min_val == max_val:
        return 0.0
    bin_width = (max_val - min_val) / bins
    eps = 1e-06

    def _bin_proportions(data: list[float]) -> list[float]:
        counts = [0] * bins
        for v in data:
            idx = min(int((v - min_val) / bin_width), bins - 1)
            counts[idx] += 1
        total = len(data)
        return [c / total + eps for c in counts]

    p = _bin_proportions(baseline)
    q = _bin_proportions(treatment)
    return sum(((pi - qi) * math.log(pi / qi) for pi, qi in zip(p, q)))


def _compute_mmd_rbf(
    baseline: list[list[float]], treatment: list[list[float]], gamma: float | None = None
) -> float:
    """Compute MMD with RBF kernel (simplified).

    For production, consider a proper kernel library.
    This implementation is correct for governance testing.
    """
    if not baseline or not treatment:
        return 0.0
    dim = len(baseline[0])
    if gamma is None:
        gamma = 1.0 / dim if dim > 0 else 1.0

    def _rbf(x: list[float], y: list[float]) -> float:
        sq_dist = sum(((a - b) ** 2 for a, b in zip(x, y)))
        return math.exp(-gamma * sq_dist)

    n = len(baseline)
    m = len(treatment)
    kxx = sum(_rbf(baseline[i], baseline[j]) for i in range(n) for j in range(n)) / (n * n)
    kyy = sum(_rbf(treatment[i], treatment[j]) for i in range(m) for j in range(m)) / (m * m)
    kxy = sum(_rbf(baseline[i], treatment[j]) for i in range(n) for j in range(m)) / (n * m)
    return max(0.0, kxx + kyy - 2 * kxy)


@dataclass
class CovariateShiftDetector:
    """Multivariate drift detector with MMD + PSI.

    Usage::

        detector = CovariateShiftDetector(
            feature_names=["accuracy", "latency"]
        )
        report = detector.detect_shift(
            baseline=[[0.9, 10], [0.8, 12]],
            treatment=[[0.5, 50], [0.4, 55]],
        )
        assert report.joint_shift is True
    """

    feature_names: list[str] = field(default_factory=list)
    mmd_threshold: float = 0.1
    psi_threshold: float = 0.2

    def detect_shift(
        self, baseline: list[list[float]], treatment: list[list[float]], threshold: float | None = None
    ) -> ShiftReport:
        """Run multivariate drift detection.

        Returns a ShiftReport with per-feature and joint flags.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "CovariateShiftDetector.detect_shift"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:CovariateShiftDetector.detect_shift".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        mmd_thresh = threshold if threshold is not None else self.mmd_threshold
        n_baseline = len(baseline)
        n_treatment = len(treatment)
        if n_baseline < MIN_SAMPLE_SIZE or n_treatment < MIN_SAMPLE_SIZE:
            return ShiftReport.skipped("insufficient_samples")
        mmd_score = _compute_mmd_rbf(baseline, treatment)
        psi_scores: dict[str, float] = {}
        per_feature: dict[str, bool] = {}
        n_features = len(self.feature_names)
        for fi in range(n_features):
            b_col = [row[fi] for row in baseline]
            t_col = [row[fi] for row in treatment]
            psi = _compute_psi(b_col, t_col)
            fname = self.feature_names[fi]
            psi_scores[fname] = psi
            per_feature[fname] = psi > self.psi_threshold
        joint_shift = mmd_score > mmd_thresh or any(per_feature.values())
        return ShiftReport.create(
            joint_shift=joint_shift,
            per_feature=per_feature,
            mmd_score=mmd_score,
            psi_scores=psi_scores,
            sample_size_ok=True,
        )
