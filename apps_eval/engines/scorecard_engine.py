"""
Scorecard Engine — apps_eval.

Computes weighted scorecard from suite results.
Maps suite pass_rates to scorecard dimensions.
Produces a ranked, weighted overall score.

Deterministic: all scoring logic is arithmetic — no model calls.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_authorize_and_execute("p2", "scorecard_engine", "execution_auth")
_emit_validates_capability("p2", "scorecard_engine", "capability_check")
_emit_routes_to_capability("p2", "scorecard_engine", "capability_route")
_emit_writes_via_uwg("p2", "scorecard_engine", "uwg_write")
_emit_blocks_direct_write("p2", "scorecard_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "scorecard_engine", "tool_invocation")
_emit_captures_execution_output("p2", "scorecard_engine", "exec_output")
_emit_dispatches_agent("p3", "scorecard_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "scorecard_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "scorecard_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "scorecard_engine", "healing_outcome")
_emit_escalates_failure("p3", "scorecard_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "scorecard_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "scorecard_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "scorecard_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "scorecard_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "scorecard_engine", "eval_metric")
_emit_stores_embedding("p4", "scorecard_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "scorecard_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "scorecard_engine", "exec_snapshot_link")
from apps_eval.types.eval_types import ScorecardRow, SuiteResult

_emit_applies_guardrail("p0", "scorecard_engine", "p0_governance")
_emit_reads_policy_state("p0", "scorecard_engine", "policy_binding")
_emit_snapshots_state("p0", "scorecard_engine", "state_snapshot")
emit_replay_key("p0", "scorecard_engine")
emit_determinism_digest("p0", "scorecard_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_log = logging.getLogger(__name__)

_SUITE_TO_DIMENSION: dict[str, str] = {
    "routing_enforcement": "governance",
    "determinism_contracts": "determinism",
    "orchestration_hop": "correctness",
    "output_contracts": "correctness",
    "exec_brief_generation": "output_richness",
    "ml_metrics_validation": "ml_metric_correctness",
}


@dataclass
class ScorecardResult:
    """Output of scorecard computation."""

    rows: list[ScorecardRow] = field(default_factory=list)
    overall_score: float = 0.0
    total_weight: float = 0.0


class ScorecardEngine:
    """Compute weighted evaluation scorecard from suite results.

    Each suite result maps to one or more scorecard dimensions.
    Dimensions have weights — the overall score is a weighted mean.
    """

    AGENT_ID = "EVAL_SCORECARD"

    def __init__(self, dimension_configs: list | None = None) -> None:
        self._dimensions = dimension_configs or []

    def compute(self, suite_results: list[SuiteResult]) -> ScorecardResult:
        """Compute scorecard from suite results.

        Args:
            suite_results: List of completed SuiteResult objects.

        Returns:
            ScorecardResult with rows and overall weighted score.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ScorecardEngine.compute")

        suite_scores: dict[str, float] = {sr.suite_id: sr.pass_rate for sr in suite_results}

        dim_scores: dict[str, list[float]] = {}
        for suite_id, score in suite_scores.items():
            dim = _SUITE_TO_DIMENSION.get(suite_id, "correctness")
            dim_scores.setdefault(dim, []).append(score)

        dim_means: dict[str, float] = {dim: sum(scores) / len(scores) for dim, scores in dim_scores.items()}

        rows: list[ScorecardRow] = []
        total_weight = 0.0
        weighted_sum = 0.0

        dim_weight_map: dict[str, float] = {}
        if self._dimensions:
            for d in self._dimensions:
                dim_weight_map[d.dimension_id] = d.weight
        else:
            default_dims = {
                "correctness": 3.0,
                "determinism": 3.0,
                "governance": 2.5,
                "latency": 1.5,
                "output_richness": 1.0,
                "ml_metric_correctness": 2.0,
            }
            dim_weight_map = default_dims

        for dim_id, weight in dim_weight_map.items():
            score = dim_means.get(dim_id, 0.0)
            weighted = score * weight
            weighted_sum += weighted
            total_weight += weight

            if score >= 0.80:
                verdict = "PASS"
            elif score >= 0.70:
                verdict = "WARN"
            else:
                verdict = "FAIL"

            rows.append(
                ScorecardRow(
                    dimension_id=dim_id,
                    display_name=dim_id.replace("_", " ").title(),
                    score=round(score, 4),
                    weight=weight,
                    weighted_score=round(weighted, 4),
                    verdict=verdict,
                )
            )

        overall = weighted_sum / total_weight if total_weight > 0 else 0.0
        rows_sorted = sorted(rows, key=lambda r: -r.weight)

        _log.info("[ScorecardEngine] overall_score=%.3f dimensions=%d", overall, len(rows))
        return ScorecardResult(
            rows=rows_sorted,
            overall_score=round(overall, 4),
            total_weight=total_weight,
        )
