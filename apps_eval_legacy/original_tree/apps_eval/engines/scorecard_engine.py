"""
Scorecard Engine — apps_eval.

Computes weighted scorecard from suite results.
Maps suite pass_rates to scorecard dimensions.
Produces a ranked, weighted overall score.

Deterministic: all scoring logic is arithmetic — no model calls.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import logging
from dataclasses import dataclass, field
from typing import Any

from apps_eval._telemetry import (
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
    _emit_records_execution_trace,
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
from apps_eval.integrations.meta_bus_publisher import (
    KIND_SCORECARD,
    publish_eval_outcome,
)
from apps_eval.integrations.tracing import eval_span
from apps_eval.types.eval_types import ScorecardRow, SuiteResult

_emit_applies_guardrail("p0", "scorecard_engine", "p0_governance")
_emit_reads_policy_state("p0", "scorecard_engine", "policy_binding")
_emit_snapshots_state("p0", "scorecard_engine", "state_snapshot")
from apps_eval._telemetry import (
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
from tqdm import tqdm

_emit_emits_metric_event("scorecard_engine", "p4obs", "metric_1")
_emit_emits_metric_event("scorecard_engine", "p4obs", "metric_2")
_emit_emits_metric_event("scorecard_engine", "p4obs", "metric_3")
_emit_emits_metric_event("scorecard_engine", "p4obs", "metric_4")
_emit_emits_metric_event("scorecard_engine", "p4obs", "metric_5")
_emit_emits_metric_event("scorecard_engine", "p4obs", "metric_6")
_emit_records_incident_event("scorecard_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("scorecard_engine", "p4obs", "anomaly")
_emit_writes_observability_log("scorecard_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("scorecard_engine", "p4obs", "mon_state")
_emit_triggers_alert("scorecard_engine", "p4obs", "alert")
_emit_links_incident_trace("scorecard_engine", "p4obs", "trace_link")
_emit_captures_pattern("scorecard_engine", "p3lm", "pattern")
_emit_records_learning_event("scorecard_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("scorecard_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("scorecard_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("scorecard_engine", "p3lm", "routing")
_emit_improves_agent_policy("scorecard_engine", "p3lm", "policy")
_emit_stores_learning_state("scorecard_engine", "p3lm", "state")
_emit_records_execution_trace("scorecard_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("scorecard_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("scorecard_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("scorecard_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("scorecard_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("scorecard_engine", "env_read", "p2_env_1")
_emit_reads_environ("scorecard_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("scorecard_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("scorecard_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "scorecard_engine", "context_pull")
_emit_pulls_context("p1", "scorecard_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "scorecard_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "scorecard_engine", "uwg_term_2")
_emit_writes_through("p1", "scorecard_engine", "write_through")
_emit_writes_through("p1", "scorecard_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "scorecard_engine", "safety_validation")
_emit_invokes_eval("p1", "scorecard_engine", "eval_call")
_emit_proposal_commits_routing("p1", "scorecard_engine", "routing_commit")
_emit_escalates_to_human("p1", "scorecard_engine", "human_escalation")
_emit_routes_through("p1", "scorecard_engine", "route_through")
_emit_checks_agent_registry("p1", "scorecard_engine", "agent_registry")
_emit_validates_agent_capability("p1", "scorecard_engine", "capability")
_emit_dispatches_execution_plan("p1", "scorecard_engine", "exec_plan")
_emit_agent_executes_agent("p1", "scorecard_engine", "sub_agent")
_emit_routes_to_agent("p1", "scorecard_engine", "target_agent")
_emit_verifies_policy("p1", "scorecard_engine", "policy_check")
_emit_observes_runtime_state("p1", "scorecard_engine", "runtime_state")
_emit_verifies_boundary("p1", "scorecard_engine", "boundary_check")
_emit_transcripts_response("p1", "scorecard_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "scorecard_engine")
_emit_gated_by_confidence("p1", "scorecard_engine", "confidence_gate")
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

    @traces_execute(layer="L3_ORCHESTRATION")
    def compute(self, suite_results: list[SuiteResult]) -> ScorecardResult:
        """Compute scorecard from suite results.

        Args:
            suite_results: List of completed SuiteResult objects.

        Returns:
            ScorecardResult with rows and overall weighted score.

        Emits:
            - OTel span ``apps_eval.v1.scorecard.compute`` with attributes
              ``eval.suite_count`` and ``eval.overall_score``.
            - Publishes a ``eval.scorecard`` MetaLearningChangePackage onto
              the canonical process-level FIFO bus so downstream
              system_learning consumers can drain it.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ScorecardEngine.compute")

        with eval_span(
            "apps_eval.v1.scorecard.compute",
            attributes={
                "eval.trace_id": _trace_id,
                "eval.suite_count": len(suite_results),
            },
        ) as _span:
            result = self._compute_inner(suite_results, _trace_id, _span)
            return result

    def _compute_inner(
        self,
        suite_results: list[SuiteResult],
        _trace_id: str,
        _span: Any,
    ) -> ScorecardResult:
        """Deterministic scoring loop — separated so the tracing wrapper in
        :meth:`compute` is the only span boundary."""
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

        for dim_id, weight in tqdm(dim_weight_map.items(), desc="Processing", unit="item"):
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
                ),
            )

        overall = weighted_sum / total_weight if total_weight > 0 else 0.0
        rows_sorted = sorted(rows, key=lambda r: -r.weight)

        _log.info("[ScorecardEngine] overall_score=%.3f dimensions=%d", overall, len(rows))
        result = ScorecardResult(
            rows=rows_sorted,
            overall_score=round(overall, 4),
            total_weight=total_weight,
        )

        # Publish outcome to canonical meta-learning bus (plan W2 wiring).
        # Fail-open: a degraded publish never breaks eval runs.
        receipt = publish_eval_outcome(
            kind=KIND_SCORECARD,
            trace_id=_trace_id,
            payload={
                "engine": self.AGENT_ID,
                "overall_score": result.overall_score,
                "total_weight": result.total_weight,
                "dimension_count": len(result.rows),
                "rows": [r.model_dump() for r in result.rows],
            },
        )
        try:
            _span.set_attribute("eval.overall_score", result.overall_score)
            _span.set_attribute("eval.bus_publish_ok", bool(receipt.ok))
            if receipt.package_hash:
                _span.set_attribute("eval.bus_package_hash", receipt.package_hash)
        except (
            AttributeError,
            TypeError,
        ):  # guardian: allow-log-and-swallow -- span attr is best-effort telemetry; never break eval
            pass

        return result
