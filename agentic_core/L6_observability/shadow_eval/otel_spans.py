"""OTEL span and KPI registry for L6 shadow evaluation (06.8 doctrine).

This module is the SSOT for the canonical L6 OTEL span names, the KPI board
thresholds, and the failure containment matrix.

It does NOT emit telemetry directly. The pipeline orchestrator records span
events to an injected sink so test fixtures can assert ordering and content
without depending on a live OTEL collector.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# 06.8 §"Required spans" — order is the canonical 6A → 6B → 6C → 6D pipeline.
SPAN_NAMES: tuple[str, ...] = (
    "l6.ingest.bundle_receive",
    "l6.ingest.source_collect",
    "l6.ingest.lineage_bind",
    "l6.ingest.stage_map_build",
    "l6.ingest.artifact_inventory",
    "l6.normalize.record_emit",
    "l6.ingest.gap_report_emit",
    "l6.observer.surface_isolation_check",
    "l6.observer.stage_barrier_check",
    "l6.g28.audit_completeness",
    "l6.g29.learning_firewall",
    "l6.readiness.evaluate",
    "l6.eval.outcome.start",
    "l6.eval.outcome.record_emit",
    "l6.eval.trajectory.start",
    "l6.eval.trajectory.record_emit",
    "l6.eval.governance_regression.start",
    "l6.eval.governance_regression.record_emit",
    "l6.calibration.holdout_load",
    "l6.calibration.judge_score",
    "l6.calibration.spearman_compute",
    "l6.calibration.reliability_emit",
    "l6.calibration.record_emit",
    "l6.calibration.record_seal",
    "l6.eval_record.seal",
    "l6.rca.signal_fusion",
    "l6.rca.packet_emit",
    "l6.pattern.record_emit",
    "l6.proposal.draft",
    "l6.proposal.admission_receipt",
    "l6.gauntlet.run",
    "l6.gauntlet.receipt_emit",
    "l6.approval.decide",
    "l6.promotion.packet_build",
    "l6.promotion.uwg_request_package",
    "l6.promotion.uwg_receipt_bind",
    "l6.future_run.activation_receipt",
)

SPAN_ORDER_INDEX: dict[str, int] = {name: i for i, name in enumerate(SPAN_NAMES)}

REQUIRED_SPAN_ATTRS: tuple[str, ...] = (
    "trace_id",
    "span_id",
    "status",
    "latency_ms",
)


@dataclass(slots=True)
class L6SpanRecord:
    """In-memory representation of a single L6 OTEL span event."""

    name: str
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    request_id: str | None = None
    run_id: str | None = None
    tenant_id: str | None = None
    policy_hash: str | None = None
    blueprint_hash: str | None = None
    replay_key: str | None = None
    source_trace_root: str | None = None
    runtime_exhaust_bundle_id: str | None = None
    completed_eval_record_id: str | None = None
    proposal_id: str | None = None
    promotion_packet_id: str | None = None
    uwg_receipt_id: str | None = None
    status: str = "OK"
    reason_codes: list[str] = field(default_factory=list)
    latency_ms: float = 0.0
    artifact_refs: list[str] = field(default_factory=list)


class L6SpanRecorder:
    """Test-friendly recorder that captures span events in order."""

    __slots__ = ("_records",)

    def __init__(self) -> None:
        self._records: list[L6SpanRecord] = []

    def record(self, span: L6SpanRecord) -> None:
        if span.name not in SPAN_ORDER_INDEX:
            raise ValueError(f"unknown L6 span name: {span.name}")
        self._records.append(span)

    @property
    def records(self) -> tuple[L6SpanRecord, ...]:
        return tuple(self._records)

    def names(self) -> list[str]:
        return [r.name for r in self._records]

    def assert_no_runtime_feedback_edge(self) -> None:
        """Doctrinal proof that no L6 span feeds back into a runtime stage.

        Any span name not in SPAN_ORDER_INDEX would imply a runtime stage was
        re-invoked from L6 — which is forbidden by 06.2 observer law.
        """
        for r in self._records:
            assert r.name in SPAN_ORDER_INDEX, f"unknown L6 span '{r.name}' — possible runtime feedback edge"

    def assert_pipeline_order(self) -> None:
        """Asserts spans are emitted in canonical 6A → 6B → 6C → 6D order."""
        last_idx = -1
        for r in self._records:
            idx = SPAN_ORDER_INDEX[r.name]
            assert idx >= last_idx, f"L6 span out of order: {r.name} (idx={idx}) after idx={last_idx}"
            last_idx = idx


# ---------------------------------------------------------------------------
# KPI board (06.8) — thresholds for KPI checks
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class KpiThreshold:
    name: str
    direction: str  # "<=" or ">=" or "=="
    target: float
    units: str = ""
    description: str = ""


KPI_BOARD: tuple[KpiThreshold, ...] = (
    KpiThreshold("trace_ingest_freshness_minutes", "<=", 10.0, "min", "newest ingested span age"),
    KpiThreshold("evidence_field_completeness_pct", ">=", 99.0, "%", "required normalized fields present"),
    KpiThreshold("orphan_artifact_rate_pct", "<=", 0.5, "%", "artifacts lacking trace/run linkage"),
    KpiThreshold("observer_law_violation_count", "==", 0.0, "count", "writes/live mutations from L6"),
    KpiThreshold("eval_readiness_coverage_pct", ">=", 98.0, "%", "runs evaluable within 24h"),
    KpiThreshold("outcome_eval_coverage_pct", ">=", 98.0, "%", "last-24h runs"),
    KpiThreshold("trajectory_eval_coverage_pct", ">=", 98.0, "%", "non-RET executions graded"),
    KpiThreshold("governance_eval_coverage_pct", "==", 100.0, "%", "high-risk / write / HITL paths checked"),
    KpiThreshold("judge_unknown_budget_compliance_pct", ">=", 95.0, "%", "judge unknown budget compliance"),
    KpiThreshold("judge_human_agreement_freshness_days", "<=", 7.0, "days", "latest calibration per rubric"),
    KpiThreshold("golden_set_regression_pass_rate_pct", ">=", 99.0, "%", "critical golden cases pass"),
    KpiThreshold("rca_to_proposal_lead_time_hours_p95", "<=", 24.0, "h", "incident close → proposal"),
    KpiThreshold("root_cause_localization_rate_pct", ">=", 90.0, "%", "first_bad_span/class or UNKNOWN hold"),
    KpiThreshold("proposal_evidence_completeness_pct", "==", 100.0, "%", "proposals link eval+RCA+evidence"),
    KpiThreshold("gauntlet_false_promote_rate_pct", "<=", 1.0, "%", "reverted promotions"),
    KpiThreshold("eval_freshness_on_write_pct", "==", 100.0, "%", "writes have fresh gating eval"),
    KpiThreshold("uwg_ink_path_uniqueness_violations", "==", 0.0, "count", "non-UWG writers detected"),
    KpiThreshold("rollback_reachability_pct", "==", 100.0, "%", "promotions have tested rollback"),
    KpiThreshold(
        "bus_u_activation_correctness_pct", "==", 100.0, "%", "updates activate at future run_start"
    ),
)


def evaluate_kpi(kpi_name: str, observed: float) -> bool:
    """Return True if the observed value satisfies the KPI direction/target."""
    for kpi in KPI_BOARD:
        if kpi.name == kpi_name:
            if kpi.direction == "<=":
                return observed <= kpi.target
            if kpi.direction == ">=":
                return observed >= kpi.target
            if kpi.direction == "==":
                return observed == kpi.target
            raise ValueError(f"invalid KPI direction: {kpi.direction!r}")
    raise KeyError(f"unknown KPI: {kpi_name}")


# ---------------------------------------------------------------------------
# Failure containment matrix (06.8)
# ---------------------------------------------------------------------------

FAILURE_CONTAINMENT: dict[str, str] = {
    "stale_ingest": "mark_stale_block_learning_until_refreshed",
    "orphan_evidence": "hold_request_repair_exclude_from_promotion",
    "eval_gap": "block_6c_6d",
    "forced_certainty": "calibration_failure_block_rubric_use",
    "preference_overfitting": "require_rubric_plus_sme_calibration",
    "rca_vagueness": "hold_proposal_until_actionable_or_unknown_root_cause",
    "false_promote": "rollback_mark_gauntlet_regression_open_rca",
    "shadow_writer": "freeze_sovereignty_incident_require_uwg_l4_audit",
    "stale_eval_on_write": "uwg_reject",
    "partial_bypass": "reject_unless_adr_scoped_exception_with_narrowed_blast_radius",
    "current_run_mutation": "fatal_invariant_breach",
    "rollback_missing": "reject_promotion",
    "cache_contamination": "disable_surface_purge_via_uwg_rca",
    "rubric_drift": "hold_evals_recalibrate",
    "replay_nonlocalization": "block_promotion_improve_instrumentation",
}


__all__ = [
    "SPAN_NAMES",
    "SPAN_ORDER_INDEX",
    "REQUIRED_SPAN_ATTRS",
    "L6SpanRecord",
    "L6SpanRecorder",
    "KpiThreshold",
    "KPI_BOARD",
    "evaluate_kpi",
    "FAILURE_CONTAINMENT",
]
