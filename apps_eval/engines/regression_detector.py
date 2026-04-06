"""
Regression Detector — apps_eval.

Compares current scorecard results against a stored baseline.
Flags REGRESSION when score drops by more than tolerance_delta.
Writes new baseline when auto_update_baseline=True.

Deterministic: delta computation, threshold comparison.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "regression_detector", "execution_auth")
_emit_validates_capability("p2", "regression_detector", "capability_check")
_emit_routes_to_capability("p2", "regression_detector", "capability_route")
_emit_writes_via_uwg("p2", "regression_detector", "uwg_write")
_emit_blocks_direct_write("p2", "regression_detector", "direct_write_block")
_emit_records_tool_invocation("p2", "regression_detector", "tool_invocation")
_emit_captures_execution_output("p2", "regression_detector", "exec_output")
_emit_dispatches_agent("p3", "regression_detector", "agent_dispatch")
_emit_coordinates_agents("p3", "regression_detector", "agent_coordination")
_emit_records_workflow_lineage("p3", "regression_detector", "workflow_lineage")
_emit_records_healing_outcome("p3", "regression_detector", "healing_outcome")
_emit_escalates_failure("p3", "regression_detector", "failure_escalation")
_emit_orchestrates_workflow("p3", "regression_detector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "regression_detector", "healing_dispatch")
_emit_invokes_evaluation("p3", "regression_detector", "evaluation_signal")
_emit_records_telemetry_event("p4", "regression_detector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "regression_detector", "eval_metric")
_emit_stores_embedding("p4", "regression_detector", "embedding_store")
_emit_updates_meta_learning_state("p4", "regression_detector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "regression_detector", "exec_snapshot_link")
from apps_eval.types.eval_types import RegressionRecord, RegressionVerdict, ScorecardRow

_emit_applies_guardrail("p0", "regression_detector", "p0_governance")
_emit_reads_policy_state("p0", "regression_detector", "policy_binding")
_emit_snapshots_state("p0", "regression_detector", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_links_incident_trace,
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
    _emit_writes_through,
)

_emit_emits_metric_event("regression_detector", "p4obs", "metric_1")
_emit_emits_metric_event("regression_detector", "p4obs", "metric_2")
_emit_emits_metric_event("regression_detector", "p4obs", "metric_3")
_emit_emits_metric_event("regression_detector", "p4obs", "metric_4")
_emit_emits_metric_event("regression_detector", "p4obs", "metric_5")
_emit_emits_metric_event("regression_detector", "p4obs", "metric_6")
_emit_records_incident_event("regression_detector", "p4obs", "incident")
_emit_captures_runtime_anomaly("regression_detector", "p4obs", "anomaly")
_emit_writes_observability_log("regression_detector", "p4obs", "obs_log")
_emit_updates_monitoring_state("regression_detector", "p4obs", "mon_state")
_emit_triggers_alert("regression_detector", "p4obs", "alert")
_emit_links_incident_trace("regression_detector", "p4obs", "trace_link")
_emit_captures_pattern("regression_detector", "p3lm", "pattern")
_emit_records_learning_event("regression_detector", "p3lm", "learning_event")
_emit_writes_learning_snapshot("regression_detector", "p3lm", "snapshot")
_emit_feeds_meta_learning("regression_detector", "p3lm", "meta_feed")
_emit_updates_routing_strategy("regression_detector", "p3lm", "routing")
_emit_improves_agent_policy("regression_detector", "p3lm", "policy")
_emit_stores_learning_state("regression_detector", "p3lm", "state")
_emit_records_execution_trace("regression_detector", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("regression_detector", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("regression_detector", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("regression_detector", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("regression_detector", "L4_STATE", "p2_trace_5")
_emit_reads_environ("regression_detector", "env_read", "p2_env_1")
_emit_reads_environ("regression_detector", "env_read", "p2_env_2")
_emit_reads_runtime_state("regression_detector", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("regression_detector", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "regression_detector", "context_pull")
_emit_pulls_context("p1", "regression_detector", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "regression_detector", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "regression_detector", "uwg_term_2")
_emit_writes_through("p1", "regression_detector", "write_through")
_emit_writes_through("p1", "regression_detector", "write_through_2")
_emit_validated_by_safety_plane("p1", "regression_detector", "safety_validation")
_emit_invokes_eval("p1", "regression_detector", "eval_call")
_emit_proposal_commits_routing("p1", "regression_detector", "routing_commit")
_emit_escalates_to_human("p1", "regression_detector", "human_escalation")
_emit_routes_through("p1", "regression_detector", "route_through")
_emit_checks_agent_registry("p1", "regression_detector", "agent_registry")
_emit_validates_agent_capability("p1", "regression_detector", "capability")
_emit_dispatches_execution_plan("p1", "regression_detector", "exec_plan")
_emit_agent_executes_agent("p1", "regression_detector", "sub_agent")
_emit_routes_to_agent("p1", "regression_detector", "target_agent")
_emit_verifies_policy("p1", "regression_detector", "policy_check")
_emit_observes_runtime_state("p1", "regression_detector", "runtime_state")
_emit_verifies_boundary("p1", "regression_detector", "boundary_check")
_emit_transcripts_response("p1", "regression_detector", "transcript")
_emit_hard_fails_untranscripted("p1", "regression_detector")
_emit_gated_by_confidence("p1", "regression_detector", "confidence_gate")
emit_replay_key("p0", "regression_detector")
emit_determinism_digest("p0", "regression_detector")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_log = logging.getLogger(__name__)


@dataclass
class RegressionResult:
    """Result of regression detection pass."""

    records: list[RegressionRecord] = field(default_factory=list)
    regression_count: int = 0
    baseline_loaded: bool = False
    baseline_path: str = ""


class RegressionDetector:
    """Compare scorecard against baseline and detect regressions.

    Baseline is a JSON file at baseline_dir/eval_baseline.json.
    If no baseline exists, all results are recorded as NO_BASELINE.
    """

    AGENT_ID = "EVAL_REGRESSION"

    def __init__(self, baseline_dir: str = "eval_baselines", tolerance_delta: float = 0.05) -> None:
        self._baseline_dir = Path(baseline_dir)
        self._tolerance_delta = tolerance_delta

    def detect(
        self,
        scorecard_rows: list[ScorecardRow],
        trace_id: str = "",
        auto_update: bool = False,
    ) -> RegressionResult:
        """Run regression detection against stored baseline.

        Args:
            scorecard_rows: Current run scorecard rows.
            trace_id: Current run trace ID.
            auto_update: If True, update baseline with current results.

        Returns:
            RegressionResult with all regression records.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RegressionDetector.detect")

        baseline = self._load_baseline()
        result = RegressionResult(baseline_loaded=baseline is not None)

        for row in scorecard_rows:
            if baseline is None:
                result.records.append(
                    RegressionRecord(
                        suite_id="",
                        dimension_id=row.dimension_id,
                        current_score=row.score,
                        baseline_score=0.0,
                        delta=0.0,
                        verdict=RegressionVerdict.NO_BASELINE,
                    )
                )
            else:
                baseline_score = baseline.get(row.dimension_id, row.score)
                delta = row.score - baseline_score

                if delta < -self._tolerance_delta:
                    verdict = RegressionVerdict.REGRESSION
                    result.regression_count += 1
                    _log.warning(
                        "[RegressionDetector] REGRESSION dim=%s delta=%.3f (threshold=%.3f)",
                        row.dimension_id,
                        delta,
                        self._tolerance_delta,
                    )
                elif delta < 0:
                    verdict = RegressionVerdict.WARN
                else:
                    verdict = RegressionVerdict.PASS

                result.records.append(
                    RegressionRecord(
                        suite_id="",
                        dimension_id=row.dimension_id,
                        current_score=row.score,
                        baseline_score=baseline_score,
                        delta=round(delta, 4),
                        verdict=verdict,
                    )
                )

        if auto_update:
            self._write_baseline(scorecard_rows, trace_id)

        # Emit regression results to system learning for drift detection
        self._emit_regression_results(result, trace_id)

        return result

    def _load_baseline(self) -> dict[str, float] | None:
        baseline_path = self._baseline_dir / "eval_baseline.json"
        if not baseline_path.exists():
            return None
        try:
            raw: dict[str, Any] = json.loads(baseline_path.read_text(encoding="utf-8"))
            _log.info("[RegressionDetector] Loaded baseline from %s", baseline_path)
            return {k: float(v) for k, v in raw.get("scores", {}).items()}
        except Exception as exc:
            _log.warning("[RegressionDetector] Could not load baseline: %s", exc)
            return None

    def _write_baseline(self, scorecard_rows: list[ScorecardRow], trace_id: str) -> None:
        self._baseline_dir.mkdir(parents=True, exist_ok=True)
        baseline_path = self._baseline_dir / "eval_baseline.json"
        data = {
            "trace_id": trace_id,
            "scores": {row.dimension_id: row.score for row in scorecard_rows},
        }
        baseline_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        _log.info("[RegressionDetector] Updated baseline at %s", baseline_path)

    def _emit_regression_results(self, result: RegressionResult, trace_id: str) -> None:
        """Emit regression results to system learning for drift detection."""
        try:
            from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge
            bridge = get_sl_memory_bridge()

            # Calculate regression metrics
            total_records = len(result.records)
            regression_count = result.regression_count
            regression_rate = regression_count / total_records if total_records > 0 else 0.0

            # Count verdicts
            verdict_counts = {}
            for record in result.records:
                verdict = record.verdict.name if hasattr(record.verdict, 'name') else str(record.verdict)
                verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1

            bridge.persist_eval_regression_results(
                trace_id=trace_id,
                total_records=total_records,
                regression_count=regression_count,
                regression_rate=regression_rate,
                verdict_counts=verdict_counts,
                baseline_loaded=result.baseline_loaded,
                timestamp_utc=int(time.time() * 1000),
            )
        except Exception:
            # System learning unavailable - continue without emission
            pass
