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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from apps_eval.types.eval_types import RegressionRecord, RegressionVerdict, ScorecardRow
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

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
