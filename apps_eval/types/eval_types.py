"""
_emit_reads_through("l4", "eval_types", "urg_read_1")
_emit_reads_through("l4", "eval_types", "urg_read_2")
_emit_reads_through("l4", "eval_types", "urg_read_3")
_emit_reads_through("l4", "eval_types", "urg_read_4")
_emit_reads_through("l4", "eval_types", "urg_read_5")
_emit_reads_through("l4", "eval_types", "urg_read_6")
_emit_reads_through("l4", "eval_types", "urg_read_7")
_emit_reads_through("l4", "eval_types", "urg_read_8")
_emit_reads_through("l4", "eval_types", "urg_read_9")
_emit_reads_through("l4", "eval_types", "urg_read_10")
_emit_reads_through("l4", "eval_types", "urg_read_11")
_emit_reads_through("l4", "eval_types", "urg_read_12")
_emit_reads_through("l4", "eval_types", "urg_read_13")
_emit_reads_through("l4", "eval_types", "urg_read_14")
_emit_reads_through("l4", "eval_types", "urg_read_15")
_emit_reads_through("l4", "eval_types", "urg_read_16")
_emit_reads_through("l4", "eval_types", "urg_read_17")
_emit_reads_through("l4", "eval_types", "urg_read_18")
_emit_reads_through("l4", "eval_types", "urg_read_19")
_emit_reads_through("l4", "eval_types", "urg_read_20")
_emit_reads_through("l4", "eval_types", "urg_read_21")
_emit_reads_through("l4", "eval_types", "urg_read_22")
_emit_reads_through("l4", "eval_types", "urg_read_23")
_emit_reads_through("l4", "eval_types", "urg_read_24")
_emit_reads_through("l4", "eval_types", "urg_read_25")
_emit_reads_through("l4", "eval_types", "urg_read_26")
_emit_reads_through("l4", "eval_types", "urg_read_27")
_emit_reads_through("l4", "eval_types", "urg_read_28")
_emit_reads_through("l4", "eval_types", "urg_read_29")
_emit_reads_through("l4", "eval_types", "urg_read_30")
_emit_reads_through("l4", "eval_types", "urg_read_31")
_emit_reads_through("l4", "eval_types", "urg_read_32")
_emit_reads_through("l4", "eval_types", "urg_read_33")
_emit_reads_through("l4", "eval_types", "urg_read_34")
_emit_reads_through("l4", "eval_types", "urg_read_35")
_emit_reads_through("l4", "eval_types", "urg_read_36")
_emit_reads_through("l4", "eval_types", "urg_read_37")
_emit_reads_through("l4", "eval_types", "urg_read_38")
_emit_reads_through("l4", "eval_types", "urg_read_39")
_emit_reads_through("l4", "eval_types", "urg_read_40")
_emit_reads_through("l4", "eval_types", "urg_read_41")
_emit_reads_through("l4", "eval_types", "urg_read_42")
_emit_reads_through("l4", "eval_types", "urg_read_43")
_emit_reads_through("l4", "eval_types", "urg_read_44")
_emit_reads_through("l4", "eval_types", "urg_read_45")
_emit_reads_through("l4", "eval_types", "urg_read_46")
_emit_reads_through("l4", "eval_types", "urg_read_47")
_emit_reads_through("l4", "eval_types", "urg_read_48")
_emit_reads_through("l4", "eval_types", "urg_read_49")
_emit_reads_through("l4", "eval_types", "urg_read_50")
_emit_reads_through("l4", "eval_types", "urg_read_51")
_emit_reads_through("l4", "eval_types", "urg_read_52")
_emit_reads_through("l4", "eval_types", "urg_read_53")
_emit_reads_through("l4", "eval_types", "urg_read_54")
_emit_reads_through("l4", "eval_types", "urg_read_55")
_emit_reads_through("l4", "eval_types", "urg_read_56")
_emit_reads_through("l4", "eval_types", "urg_read_57")
_emit_reads_through("l4", "eval_types", "urg_read_58")
_emit_reads_through("l4", "eval_types", "urg_read_59")
_emit_reads_through("l4", "eval_types", "urg_read_60")
_emit_reads_through("l4", "eval_types", "urg_read_61")
_emit_reads_through("l4", "eval_types", "urg_read_62")
_emit_reads_through("l4", "eval_types", "urg_read_63")
_emit_reads_through("l4", "eval_types", "urg_read_64")
_emit_reads_through("l4", "eval_types", "urg_read_65")
_emit_reads_through("l4", "eval_types", "urg_read_66")
_emit_reads_through("l4", "eval_types", "urg_read_67")
_emit_reads_through("l4", "eval_types", "urg_read_68")
_emit_reads_through("l4", "eval_types", "urg_read_69")
_emit_reads_through("l4", "eval_types", "urg_read_70")
_emit_reads_through("l4", "eval_types", "urg_read_71")
_emit_reads_through("l4", "eval_types", "urg_read_72")
_emit_reads_through("l4", "eval_types", "urg_read_73")
apps_eval domain types — Evaluation Lab.

All types are frozen dataclasses or Pydantic models.
Every artifact carries provenance. No silent pass — all failures recorded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import _emit_reads_through


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
