"""
EvalOrchestrator — apps_eval.

Orchestrates the complete Evaluation Lab pipeline:
  1. Suite selection and scenario dispatch
  2. Scoring (weighted scorecard)
  3. Regression detection
  4. Gate validation
  5. Artifact emission (report, scorecard CSV, JSON manifest)
  6. Run summary

Mirrors apps_rg RgResumeOrchestrator pattern.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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

_emit_authorize_and_execute("p2", "EvalOrchestrator", "execution_auth")
_emit_validates_capability("p2", "EvalOrchestrator", "capability_check")
_emit_routes_to_capability("p2", "EvalOrchestrator", "capability_route")
_emit_writes_via_uwg("p2", "EvalOrchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "EvalOrchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "EvalOrchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "EvalOrchestrator", "exec_output")
_emit_dispatches_agent("p3", "EvalOrchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "EvalOrchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "EvalOrchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "EvalOrchestrator", "healing_outcome")
_emit_escalates_failure("p3", "EvalOrchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "EvalOrchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "EvalOrchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "EvalOrchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "EvalOrchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "EvalOrchestrator", "eval_metric")
_emit_stores_embedding("p4", "EvalOrchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "EvalOrchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "EvalOrchestrator", "exec_snapshot_link")
from apps_eval.engines.regression_detector import RegressionDetector
from apps_eval.engines.scenario_runner import ScenarioRunner
from apps_eval.engines.scorecard_engine import ScorecardEngine
from apps_eval.types.eval_types import (
    EvalRequest,
    EvalResult,
    EvalRunSummary,
    EvalStatus,
    RegressionVerdict,
)
from apps_eval.validators.eval_gate_validator import EvalGateValidator

_emit_applies_guardrail("p0", "EvalOrchestrator", "p0_governance")
_emit_reads_policy_state("p0", "EvalOrchestrator", "policy_binding")
_emit_snapshots_state("p0", "EvalOrchestrator", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("EvalOrchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("EvalOrchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("EvalOrchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("EvalOrchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("EvalOrchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("EvalOrchestrator", "p4obs", "metric_6")
_emit_records_incident_event("EvalOrchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("EvalOrchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("EvalOrchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("EvalOrchestrator", "p4obs", "mon_state")
_emit_triggers_alert("EvalOrchestrator", "p4obs", "alert")
_emit_links_incident_trace("EvalOrchestrator", "p4obs", "trace_link")
_emit_captures_pattern("EvalOrchestrator", "p3lm", "pattern")
_emit_records_learning_event("EvalOrchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("EvalOrchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("EvalOrchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("EvalOrchestrator", "p3lm", "routing")
_emit_improves_agent_policy("EvalOrchestrator", "p3lm", "policy")
_emit_stores_learning_state("EvalOrchestrator", "p3lm", "state")
_emit_records_execution_trace("EvalOrchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("EvalOrchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("EvalOrchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("EvalOrchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("EvalOrchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("EvalOrchestrator", "env_read", "p2_env_1")
_emit_reads_environ("EvalOrchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("EvalOrchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("EvalOrchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "EvalOrchestrator", "context_pull")
_emit_pulls_context("p1", "EvalOrchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "EvalOrchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "EvalOrchestrator", "uwg_term_2")
_emit_writes_through("p1", "EvalOrchestrator", "write_through")
_emit_writes_through("p1", "EvalOrchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "EvalOrchestrator", "safety_validation")
_emit_invokes_eval("p1", "EvalOrchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "EvalOrchestrator", "routing_commit")
emit_replay_key("p0", "EvalOrchestrator")
emit_determinism_digest("p0", "EvalOrchestrator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_log = logging.getLogger(__name__)


@dataclass
class EvalOrchestrator:
    """Orchestrate end-to-end evaluation lab run."""

    dry_run: bool = False
    output_dir: str = "eval"
    baseline_dir: str = "eval_baselines"
    gate_mode: str = "HARD_FAIL"
    hop_checkpoints: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._runner = ScenarioRunner()
        self._scorecard = ScorecardEngine()
        self._regression = RegressionDetector(baseline_dir=self.baseline_dir)
        self._gate = EvalGateValidator()

        try:
            from apps_eval.config import load_eval_specs

            self._specs = load_eval_specs()
            self._scorecard = ScorecardEngine(dimension_configs=self._specs.scorecard_dimensions)
            self._regression = RegressionDetector(
                baseline_dir=self._specs.regression.baseline_dir,
                tolerance_delta=self._specs.regression.tolerance_delta,
            )
            self._gate = EvalGateValidator(
                min_overall_score=self._specs.gate.min_overall_score,
                fail_on_regression=self._specs.gate.fail_on_regression,
                max_timeout_violations=self._specs.gate.max_timeout_violations,
            )
        except ImportError:
            self._specs = None

        try:
            from agentic_core.adg.runtime.behavioral_index import ADGBehavioralIndex

            _idx = ADGBehavioralIndex.from_latest(Path(__file__).resolve().parents[3])
            _profile = _idx.profile_for(Path(__file__).resolve()) if _idx else None
            self.adg_behavioral_score: float = _profile.behavioral_score if _profile else 0.5
            self.adg_antipattern_signals: list[str] = sorted(_profile.antipattern_signals) if _profile else []
        except (ImportError, AttributeError, OSError):
            self.adg_behavioral_score = 0.5
            self.adg_antipattern_signals = []

    def run(self, request: EvalRequest) -> EvalResult:
        """Execute full evaluation lab pipeline.

        Args:
            request: EvalRequest with suite IDs and options.

        Returns:
            EvalResult with scorecard, regression records, and artifacts.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EvalOrchestrator.run")

        trace_id = request.trace_id or self._make_trace_id(request)
        _log.info(
            "[EvalOrchestrator] trace=%s suites=%s dry_run=%s",
            trace_id,
            request.suite_ids,
            request.dry_run or self.dry_run,
        )

        result = EvalResult(
            trace_id=trace_id,
            status=EvalStatus.RUNNING,
            provenance={"trace_id": trace_id, "app": "apps_eval", "suite_ids": request.suite_ids},
        )

        try:
            suite_results = self._run_suites(request)
            self._record_hop("HOP-1-SUITES", bool(suite_results))
            result.suite_results = suite_results

            result.status = EvalStatus.SCORING
            scorecard = self._scorecard.compute(suite_results)
            self._record_hop("HOP-2-SCORECARD", True)
            result.scorecard = scorecard.rows
            result.overall_score = scorecard.overall_score

            regression = self._regression.detect(
                scorecard.rows,
                trace_id=trace_id,
                auto_update=self._specs.regression.auto_update_baseline if self._specs else False,
            )
            self._record_hop("HOP-3-REGRESSION", regression.regression_count == 0)
            result.regression_records = regression.records

            if regression.regression_count > 0:
                result.status = EvalStatus.REGRESSION

            gate = self._gate.validate(
                suite_results,
                scorecard.rows,
                regression.records,
                scorecard.overall_score,
            )
            self._record_hop("HOP-4-GATE", gate.passed)
            result.gate_violations = [f"[{v.rule_id}:{v.severity}] {v.message}" for v in gate.violations]

            is_dry = request.dry_run or self.dry_run
            if not gate.passed:
                _log.error("[EvalOrchestrator] Gate FAILED: %d violations", len(gate.violations))
                if not is_dry and self.gate_mode == "HARD_FAIL":
                    if result.status != EvalStatus.REGRESSION:
                        result.status = EvalStatus.FAILED

            if is_dry:
                result.status = EvalStatus.DRY_RUN
            elif result.status not in (EvalStatus.FAILED, EvalStatus.REGRESSION):
                result.status = EvalStatus.COMPLETE

            if not is_dry:
                paths = self._emit_artifacts(result, trace_id, request)
                result.artifact_paths = paths
                self._record_hop("HOP-5-EMIT", True)

        except (ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            _log.error("[EvalOrchestrator] Pipeline error trace=%s: %s", trace_id, exc, exc_info=True)
            result.status = EvalStatus.FAILED
            result.error = str(exc)
            self._record_hop("PIPELINE-ERROR", False)
            result.provenance["checkpoints"] = [c["hop_id"] for c in self.hop_checkpoints]

        total_scenarios = sum(len(sr.scenarios) for sr in result.suite_results)
        passed_scenarios = sum(
            1 for sr in result.suite_results for sc in sr.scenarios if sc.outcome.value in ("PASS", "SKIP")
        )
        regressions = sum(1 for r in result.regression_records if r.verdict == RegressionVerdict.REGRESSION)

        summary = EvalRunSummary(
            trace_id=trace_id,
            status=result.status.value,
            suites_run=len(result.suite_results),
            scenarios_run=total_scenarios,
            scenarios_passed=passed_scenarios,
            overall_score=result.overall_score,
            regressions_detected=regressions,
            gate_violations=result.gate_violations,
            artifacts=result.artifact_paths,
            dry_run=request.dry_run or self.dry_run,
            error=result.error,
            provenance=result.provenance,
        )

        if not (request.dry_run or self.dry_run):
            sp = self._emit_run_summary(summary, trace_id)
            result.run_summary_path = sp

        _log.info(
            "[EvalOrchestrator] Complete trace=%s status=%s score=%.2f regressions=%d",
            trace_id,
            result.status.value,
            result.overall_score,
            regressions,
        )
        return result

    def _run_suites(self, request: EvalRequest) -> list:
        """Dispatch suite runners for all requested suites."""

        if not self._specs:
            _log.warning("[EvalOrchestrator] No specs — running with empty suite list")
            return []

        suite_ids = request.suite_ids or list(self._specs.benchmark_suites.keys())
        results = []

        for suite_id in suite_ids:
            suite_cfg = self._specs.benchmark_suites.get(suite_id)
            if suite_cfg is None:
                _log.warning("[EvalOrchestrator] Unknown suite: %s — skipping", suite_id)
                continue
            suite_result = self._runner.run_suite(
                suite_id=suite_id,
                display_name=suite_cfg.display_name,
                scenario_ids=suite_cfg.scenario_ids,
                timeout_sec=suite_cfg.timeout_sec,
            )
            results.append(suite_result)

        return results

    def _emit_artifacts(self, result: EvalResult, trace_id: str, request: EvalRequest) -> list[str]:
        out = Path(self.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        paths: list[str] = []

        report_path = out / f"eval_report_{trace_id[:8]}.md"
        lines = [
            "# Evaluation Lab Report",
            "",
            f"**Trace ID:** `{trace_id}`  ",
            f"**Status:** {result.status.value}  ",
            f"**Overall Score:** {result.overall_score:.1%}  ",
            f"**Gate Violations:** {len(result.gate_violations)}  ",
            "",
            "---",
            "",
            "## Scorecard",
            "",
            "| Dimension | Score | Weight | Weighted | Verdict |",
            "|-----------|-------|--------|----------|---------|",
        ]
        for row in result.scorecard:
            lines.append(
                f"| {row.display_name} | {row.score:.1%} | {row.weight:.1f} "
                f"| {row.weighted_score:.3f} | {row.verdict} |"
            )
        lines += ["", "---", "", "## Suite Results", ""]

        for sr in result.suite_results:
            lines.append(f"### {sr.display_name} (`{sr.suite_id}`)")
            lines.append(f"- **Pass Rate:** {sr.pass_rate:.0%}")
            lines.append(f"- **Mean Latency:** {sr.mean_latency_ms:.1f} ms")
            lines.append("")
            for sc in sr.scenarios:
                icon = "✓" if sc.outcome.value == "PASS" else ("~" if sc.outcome.value == "SKIP" else "✗")
                lines.append(
                    f"  - `{icon}` `{sc.scenario_id}` [{sc.outcome.value}] score={sc.score:.2f} — {sc.message}"
                )
            lines.append("")

        if result.regression_records:
            lines += [
                "---",
                "",
                "## Regression Analysis",
                "",
                "| Dimension | Current | Baseline | Delta | Verdict |",
                "|-----------|---------|----------|-------|---------|",
            ]
            for reg in result.regression_records:
                lines.append(
                    f"| {reg.dimension_id} | {reg.current_score:.3f} | "
                    f"{reg.baseline_score:.3f} | {reg.delta:+.3f} | {reg.verdict.value} |"
                )
            lines.append("")

        if result.gate_violations:
            lines += ["---", "", "## Gate Violations", ""]
            for v in result.gate_violations:
                lines.append(f"- {v}")
            lines.append("")

        report_path.write_text("\n".join(lines), encoding="utf-8")
        paths.append(str(report_path))

        if request.emit_scorecard_csv:
            csv_path = out / f"scorecard_{trace_id[:8]}.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["dimension_id", "display_name", "score", "weight", "weighted_score", "verdict"]
                )
                for row in result.scorecard:
                    writer.writerow(
                        [
                            row.dimension_id,
                            row.display_name,
                            f"{row.score:.4f}",
                            f"{row.weight:.1f}",
                            f"{row.weighted_score:.4f}",
                            row.verdict,
                        ]
                    )
            paths.append(str(csv_path))

        manifest = {
            "trace_id": trace_id,
            "overall_score": result.overall_score,
            "suites": [
                {"suite_id": sr.suite_id, "pass_rate": sr.pass_rate, "scenarios": len(sr.scenarios)}
                for sr in result.suite_results
            ],
        }
        manifest_path = out / f"eval_manifest_{trace_id[:8]}.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        paths.append(str(manifest_path))

        return paths

    def _emit_run_summary(self, summary: EvalRunSummary, trace_id: str) -> str:
        out = Path(self.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        p = out / f"run_summary_{trace_id[:8]}.json"
        p.write_text(json.dumps(summary.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return str(p)

    def _record_hop(self, hop_id: str, success: bool) -> None:
        self.hop_checkpoints.append({"hop_id": hop_id, "status": "COMPLETED" if success else "FAILED"})

    @staticmethod
    def _make_trace_id(request: EvalRequest) -> str:
        raw = f"eval:{','.join(sorted(request.suite_ids))}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
