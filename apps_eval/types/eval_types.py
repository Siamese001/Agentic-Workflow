"""
apps_eval domain types — Evaluation Lab.

All types are frozen dataclasses or Pydantic models.
Every artifact carries provenance. No silent pass — all failures recorded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EvalStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SCORING = "scoring"
    COMPLETE = "complete"
    FAILED = "failed"
    REGRESSION = "regression"
    DRY_RUN = "dry_run"


class ScenarioOutcome(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"
    SKIP = "SKIP"


class RegressionVerdict(str, Enum):
    NO_BASELINE = "NO_BASELINE"
    PASS = "PASS"
    WARN = "WARN"
    REGRESSION = "REGRESSION"


@dataclass(frozen=True)
class ScenarioResult:
    """Result of a single scenario execution."""

    scenario_id: str
    suite_id: str
    outcome: ScenarioOutcome
    score: float
    latency_ms: float = 0.0
    message: str = ""
    evidence: str = ""
    deterministic: bool = True


@dataclass(frozen=True)
class SuiteResult:
    """Result of a complete benchmark suite."""

    suite_id: str
    display_name: str
    scenarios: tuple[ScenarioResult, ...] = field(default_factory=tuple)
    pass_rate: float = 0.0
    mean_latency_ms: float = 0.0
    error: str = ""

    @property
    def passed(self) -> bool:
        return self.pass_rate >= 0.70 and not self.error


@dataclass(frozen=True)
class ScorecardRow:
    """One row of the evaluation scorecard."""

    dimension_id: str
    display_name: str
    score: float
    weight: float
    weighted_score: float
    verdict: str


@dataclass(frozen=True)
class RegressionRecord:
    """Regression comparison record."""

    suite_id: str
    dimension_id: str
    current_score: float
    baseline_score: float
    delta: float
    verdict: RegressionVerdict


@dataclass
class EvalRequest:
    """Input contract for a single evaluation lab run."""

    suite_ids: list[str] = field(default_factory=list)
    dry_run: bool = False
    trace_id: str = ""
    compare_baseline: bool = True
    emit_scorecard_csv: bool = True
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalResult:
    """Output contract for a single evaluation lab run."""

    trace_id: str
    status: EvalStatus
    suite_results: list[SuiteResult] = field(default_factory=list)
    scorecard: list[ScorecardRow] = field(default_factory=list)
    regression_records: list[RegressionRecord] = field(default_factory=list)
    overall_score: float = 0.0
    gate_violations: list[str] = field(default_factory=list)
    artifact_paths: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    run_summary_path: str = ""
    error: str = ""

    @property
    def passed_gate(self) -> bool:
        return len(self.gate_violations) == 0 and self.status in (EvalStatus.COMPLETE, EvalStatus.DRY_RUN)


@dataclass
class EvalRunSummary:
    """Top-level run summary artifact."""

    trace_id: str
    app: str = "apps_eval"
    version: str = "1.0.0"
    status: str = "pending"
    suites_run: int = 0
    scenarios_run: int = 0
    scenarios_passed: int = 0
    overall_score: float = 0.0
    regressions_detected: int = 0
    gate_violations: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    dry_run: bool = False
    error: str = ""
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "app": self.app,
            "version": self.version,
            "status": self.status,
            "suites_run": self.suites_run,
            "scenarios_run": self.scenarios_run,
            "scenarios_passed": self.scenarios_passed,
            "overall_score": self.overall_score,
            "regressions_detected": self.regressions_detected,
            "gate_violations": self.gate_violations,
            "artifacts": self.artifacts,
            "dry_run": self.dry_run,
            "error": self.error,
            "provenance": self.provenance,
        }
