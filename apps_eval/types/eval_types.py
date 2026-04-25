"""
apps_eval domain types — Evaluation Lab.

All types are Pydantic models with strict validation.
Every artifact carries provenance. No silent pass — all failures recorded.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, validator

EvalStatus = Literal["pending", "running", "scoring", "complete", "failed", "regression", "dry_run"]

ScenarioOutcome = Literal["PASS", "FAIL", "TIMEOUT", "ERROR", "SKIP"]

RegressionVerdict = Literal["NO_BASELINE", "PASS", "WARN", "REGRESSION"]


class ScenarioResult(BaseModel):
    """Result of a single scenario execution."""

    scenario_id: str = Field(..., description="Unique scenario identifier")
    suite_id: str = Field(..., description="Parent suite identifier")
    outcome: ScenarioOutcome = Field(..., description="Test outcome")
    score: float = Field(..., ge=0, le=1, description="Score 0.0-1.0")
    latency_ms: float = Field(0.0, ge=0, description="Execution time in ms")
    message: str = Field("", description="Status message")
    evidence: str = Field("", description="Evidence reference")
    deterministic: bool = Field(True, description="Whether result is deterministic")

    @validator("score")
    def validate_score_range(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("score must be between 0.0 and 1.0")
        return v


class SuiteResult(BaseModel):
    """Result of a complete benchmark suite."""

    suite_id: str = Field(..., description="Unique suite identifier")
    display_name: str = Field(..., description="Human-readable name")
    scenarios: list[ScenarioResult] = Field(default_factory=list, description="Scenario results")
    pass_rate: float = Field(0.0, ge=0, le=1, description="Pass rate 0.0-1.0")
    mean_latency_ms: float = Field(0.0, ge=0, description="Mean latency")
    error: str = Field("", description="Error message if failed")

    @property
    def passed(self) -> bool:
        return self.pass_rate >= 0.70 and not self.error

    @validator("pass_rate")
    def validate_pass_rate(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("pass_rate must be between 0.0 and 1.0")
        return v


class ScorecardRow(BaseModel):
    """One row of the evaluation scorecard."""

    dimension_id: str = Field(..., description="Dimension identifier")
    display_name: str = Field(..., description="Human-readable name")
    score: float = Field(..., ge=0, le=1, description="Score 0.0-1.0")
    weight: float = Field(..., gt=0, description="Weight multiplier")
    weighted_score: float = Field(..., description="Score × weight")
    verdict: str = Field(..., description="PASS/FAIL/WARN")
    # Optional taxonomy hints — added 2026-04-25 (G9). When populated, drive
    # taxonomy-aware regression tolerance per apps_eval/config/eval_policies.yaml.
    suite_id: str = Field("", description="Originating suite (used to derive taxonomy class)")
    taxonomy_class: str = Field("", description="capability | regression (empty = derive from suite_id)")


class RegressionRecord(BaseModel):
    """Regression comparison record."""

    suite_id: str = Field(..., description="Suite identifier")
    dimension_id: str = Field(..., description="Dimension identifier")
    current_score: float = Field(..., ge=0, le=1, description="Current score")
    baseline_score: float = Field(..., ge=0, le=1, description="Baseline score")
    delta: float = Field(..., description="Score difference")
    verdict: RegressionVerdict = Field(..., description="Regression verdict")


class EvalConfig(BaseModel):
    """Evaluation configuration parameters."""

    min_pass_rate: float = Field(0.7, ge=0, le=1, description="Minimum pass rate threshold")
    max_latency_ms: float = Field(30000, gt=0, description="Maximum allowed latency")
    regression_threshold: float = Field(0.05, ge=0, description="Regression detection threshold")
    require_deterministic: bool = Field(True, description="Require deterministic results")


class EvalRequest(BaseModel):
    """Input contract for a single evaluation lab run."""

    suite_ids: list[str] = Field(default_factory=list, description="Suites to run")
    dry_run: bool = Field(False, description="Dry run mode")
    trace_id: str = Field("", description="Trace identifier")
    compare_baseline: bool = Field(True, description="Compare against baseline")
    emit_scorecard_csv: bool = Field(True, description="Emit CSV scorecard")
    config: EvalConfig = Field(default_factory=EvalConfig, description="Eval configuration")


class EvalResult(BaseModel):
    """Output contract for a single evaluation lab run."""

    trace_id: str = Field("", description="Trace identifier")
    status: EvalStatus = Field("pending", description="Run status")
    suite_results: list[SuiteResult] = Field(default_factory=list, description="Suite results")
    scorecard: list[ScorecardRow] = Field(default_factory=list, description="Scorecard rows")
    regression_records: list[RegressionRecord] = Field(default_factory=list, description="Regression records")
    overall_score: float = Field(0.0, ge=0, le=1, description="Overall score")
    gate_violations: list[str] = Field(default_factory=list, description="Gate violations")
    artifact_paths: list[str] = Field(default_factory=list, description="Output artifact paths")
    provenance: dict = Field(default_factory=dict, description="Provenance metadata")
    run_summary_path: str = Field("", description="Summary output path")
    error: str = Field("", description="Error message")

    @property
    def passed_gate(self) -> bool:
        return len(self.gate_violations) == 0 and self.status in ("complete", "dry_run")


class EvalRunSummary(BaseModel):
    """Top-level run summary artifact."""

    trace_id: str = Field("", description="Trace identifier")
    app: str = Field("apps_eval", description="Application name")
    version: str = Field("1.0.0", description="Version")
    status: str = Field("pending", description="Run status")
    suites_run: int = Field(0, ge=0, description="Number of suites run")
    scenarios_run: int = Field(0, ge=0, description="Number of scenarios run")
    scenarios_passed: int = Field(0, ge=0, description="Number of scenarios passed")
    overall_score: float = Field(0.0, ge=0, le=1, description="Overall score")
    regressions_detected: int = Field(0, ge=0, description="Number of regressions")
    gate_violations: list[str] = Field(default_factory=list, description="Gate violations")
    artifacts: list[str] = Field(default_factory=list, description="Generated artifacts")
    dry_run: bool = Field(False, description="Dry run mode")
    error: str = Field("", description="Error message")
    provenance: dict = Field(default_factory=dict, description="Provenance metadata")

    def to_dict(self) -> dict:
        return self.dict()

    class Config:
        json_schema_extra = {
            "example": {
                "trace_id": "EVAL-2024-001",
                "app": "apps_eval",
                "version": "1.0.0",
                "status": "complete",
                "suites_run": 5,
                "scenarios_run": 25,
                "scenarios_passed": 23,
                "overall_score": 0.92,
            },
        }
