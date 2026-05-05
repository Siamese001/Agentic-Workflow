"""L2 E5 SEAL stage — seal reports, scorecards, manifests."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from apps_eval.engines.scenario_runner import ScenarioRunnerResult

logger = logging.getLogger(__name__)


@dataclass
class SealResult:
    ok: bool = False
    scorecard_path: Path | None = None
    all_scenarios_passed: bool = False
    degraded: bool = False
    terminal_class: str = "FAILURE"
    gate_violations: list[dict] = field(default_factory=list)


class EvalSealStage:
    """Seal evaluation artifacts and determine terminal class."""

    def __init__(self, exec_result: "ScenarioRunnerResult"):
        self.exec_result = exec_result
        self.run_dir = exec_result.run_dir
        self.trace_id = exec_result.trace_id

    def run(self) -> SealResult:
        result = SealResult()

        # Seal eval_report_<trace_id>.md
        report_path = self._seal_report()

        # Seal scorecard_<trace_id>.csv
        result.scorecard_path = self._seal_scorecard()

        # Seal eval_manifest_<trace_id>.json
        self._seal_manifest()

        # Seal run_summary_<trace_id>.json
        self._seal_run_summary()

        # Determine terminal class
        if self._all_passed():
            result.all_scenarios_passed = True
            result.terminal_class = "SUCCESS"
        elif self._degraded():
            result.degraded = True
            result.terminal_class = "DEGRADED_SUCCESS"
        else:
            result.terminal_class = "FAILURE"

        # Collect gate violations for Exit X2
        result.gate_violations = self._collect_gate_violations()

        result.ok = True
        return result

    def _seal_report(self) -> Path:
        """Seal full markdown report."""
        report_path = self.run_dir / f"eval_report_{self.trace_id}.md"
        # TODO: Implement report generation (deferred)
        report_path.write_text("# Eval Report (stub)")
        return report_path

    def _seal_scorecard(self) -> Path:
        """Seal machine-readable scorecard CSV."""
        scorecard_path = self.run_dir / f"scorecard_{self.trace_id}.csv"
        # TODO: Implement scorecard CSV generation (deferred)
        scorecard_path.write_text("scenario_id,dimension,score\n")
        return scorecard_path

    def _seal_manifest(self) -> None:
        """Seal lightweight JSON manifest."""
        manifest_path = self.run_dir / f"eval_manifest_{self.trace_id}.json"
        manifest = {
            "trace_id": self.trace_id,
            "suite_count": len(self.exec_result.suite_results),
            "scenarios_run": self.exec_result.scenarios_run,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2))

    def _seal_run_summary(self) -> None:
        """Seal provenance + gate results."""
        summary_path = self.run_dir / f"run_summary_{self.trace_id}.json"
        summary = {
            "trace_id": self.trace_id,
            "terminal_class": self._terminal_class_from_results(),
            "gate_violations": [],
        }
        summary_path.write_text(json.dumps(summary, indent=2))

    def _all_passed(self) -> bool:
        """Check if all scenarios passed thresholds."""
        return all(r.passed for r in self.exec_result.scenario_results)

    def _degraded(self) -> bool:
        """Check if run degraded (judge unavailable, partial pass)."""
        return self.exec_result.judge_degraded and any(
            r.passed for r in self.exec_result.scenario_results
        )

    def _terminal_class_from_results(self) -> str:
        if self._all_passed():
            return "SUCCESS"
        if self._degraded():
            return "DEGRADED_SUCCESS"
        return "FAILURE"

    def _collect_gate_violations(self) -> list[dict]:
        """Collect gate violations for Exit X2 aggregation."""
        violations = []
        for r in self.exec_result.scenario_results:
            if r.gate_violations:
                violations.extend(r.gate_violations)
        return violations
