"""
apps_eval Configuration Schemas — Evaluation Lab.

Pydantic models for type-safe configuration. Aligned with apps_rg pattern.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator

_log = logging.getLogger(__name__)


class BenchmarkSuiteConfig(BaseModel):
    """Configuration for a single benchmark suite."""

    suite_id: str
    display_name: str
    target_module: str = Field(..., description="Python import path to the module under test")
    scenario_ids: list[str] = Field(default_factory=list)
    timeout_sec: int = Field(default=60, ge=1)
    required: bool = True


class ScorecardDimensionConfig(BaseModel):
    """A single scored dimension in the evaluation scorecard."""

    dimension_id: str
    display_name: str
    weight: float = Field(default=1.0, ge=0.0, le=10.0)
    threshold_pass: float = Field(default=0.70, ge=0.0, le=1.0)
    threshold_warn: float = Field(default=0.80, ge=0.0, le=1.0)


class RegressionConfig(BaseModel):
    """Configuration for regression detection."""

    baseline_dir: str = Field(default="eval_baselines")
    tolerance_delta: float = Field(
        default=0.05, ge=0.0, le=1.0, description="Max allowed score drop before REGRESSION flag"
    )
    auto_update_baseline: bool = False


class EvalOutputConfig(BaseModel):
    """Output configuration for evaluation lab."""

    output_dir: str = Field(default="eval")
    artifact_prefix: str = Field(default="eval_report")
    emit_run_summary: bool = True
    emit_scorecard_csv: bool = True
    emit_json_manifest: bool = True
    dry_run: bool = False


class EvalGateConfig(BaseModel):
    """Quality gates for evaluation runs."""

    min_overall_score: float = Field(default=0.70, ge=0.0, le=1.0)
    fail_on_regression: bool = True
    fail_on_missing_suite: bool = True
    max_timeout_violations: int = Field(default=0, ge=0)


class EvalAgentSpecs(BaseModel):
    """Root configuration for all apps_eval agent specifications."""

    version: str = "1.0.0"
    benchmark_suites: dict[str, BenchmarkSuiteConfig] = Field(
        default_factory=lambda: {
            "routing_enforcement": BenchmarkSuiteConfig(
                suite_id="routing_enforcement",
                display_name="L0 Routing Enforcement",
                target_module="agentic_core.L0_routing.enforcement",
                scenario_ids=["policy_hash_valid", "policy_hash_invalid", "missing_hash"],
            ),
            "determinism_contracts": BenchmarkSuiteConfig(
                suite_id="determinism_contracts",
                display_name="Determinism Contract Checks",
                target_module="agentic_core.L5_safety.static_checks.determinism_serialization_check",
                scenario_ids=["nondeterministic_time_call", "allowlisted_call", "clean_module"],
            ),
            "orchestration_hop": BenchmarkSuiteConfig(
                suite_id="orchestration_hop",
                display_name="Multi-Hop Orchestration",
                target_module="apps_rg.reasoning.RgResumeOrchestrator",
                scenario_ids=["single_hop", "multi_hop_pass", "multi_hop_gate_fail"],
            ),
            "output_contracts": BenchmarkSuiteConfig(
                suite_id="output_contracts",
                display_name="Output Contract Integrity",
                target_module="agentic_core.interfaces.execution_contracts",
                scenario_ids=["signed_output_valid", "tampered_signature"],
            ),
            "exec_brief_generation": BenchmarkSuiteConfig(
                suite_id="exec_brief_generation",
                display_name="Executive Brief Generation (apps_exec)",
                target_module="apps_exec.reasoning.ExecOrchestrator",
                scenario_ids=["recruiter_brief", "cto_brief", "dry_run"],
            ),
            "ml_metrics_validation": BenchmarkSuiteConfig(
                suite_id="ml_metrics_validation",
                display_name="ML Evaluation Metrics Validation",
                target_module="agentic_core.evaluation.metrics.classification",
                scenario_ids=[
                    "binary_precision_perfect",
                    "binary_recall_perfect",
                    "binary_f1_harmonic_mean",
                    "multiclass_macro_f1",
                    "multiclass_weighted_f1",
                    "confusion_matrix_invariants",
                ],
            ),
        }
    )
    scorecard_dimensions: list[ScorecardDimensionConfig] = Field(
        default_factory=lambda: [
            ScorecardDimensionConfig(
                dimension_id="correctness", display_name="Correctness", weight=3.0, threshold_pass=0.80
            ),
            ScorecardDimensionConfig(
                dimension_id="determinism",
                display_name="Determinism Compliance",
                weight=3.0,
                threshold_pass=0.90,
            ),
            ScorecardDimensionConfig(
                dimension_id="governance",
                display_name="Governance Gate Coverage",
                weight=2.5,
                threshold_pass=0.75,
            ),
            ScorecardDimensionConfig(
                dimension_id="latency", display_name="Latency SLA", weight=1.5, threshold_pass=0.70
            ),
            ScorecardDimensionConfig(
                dimension_id="output_richness",
                display_name="Output Richness",
                weight=1.0,
                threshold_pass=0.65,
            ),
            ScorecardDimensionConfig(
                dimension_id="ml_metric_correctness",
                display_name="ML Metric Correctness",
                weight=2.0,
                threshold_pass=0.90,
            ),
        ]
    )
    regression: RegressionConfig = Field(default_factory=RegressionConfig)
    output: EvalOutputConfig = Field(default_factory=EvalOutputConfig)
    gate: EvalGateConfig = Field(default_factory=EvalGateConfig)
    global_step_limit: int = Field(default=20)
    checkpoint_enabled: bool = True
    trace_persistence: bool = True

    @model_validator(mode="after")
    def validate_weights_sum(self) -> EvalAgentSpecs:
        total = sum(d.weight for d in self.scorecard_dimensions)
        if total <= 0:
            raise ValueError("Scorecard dimension weights must sum to > 0")
        return self


_SPEC_CACHE: EvalAgentSpecs | None = None


def load_eval_specs(spec_path: str | None = None) -> EvalAgentSpecs:
    """Load EvalAgentSpecs from JSON file or return defaults."""
    global _SPEC_CACHE
    if _SPEC_CACHE is not None:
        return _SPEC_CACHE

    resolved: Path | None = None
    if spec_path:
        resolved = Path(spec_path)
    else:
        default = Path(__file__).parent / "eval_agent_specs.json"
        if default.exists():
            resolved = default

    if resolved and resolved.exists():
        try:
            raw: dict[str, Any] = json.loads(resolved.read_text(encoding="utf-8"))
            _SPEC_CACHE = EvalAgentSpecs.model_validate(raw)
            return _SPEC_CACHE
        except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError) as exc:
            _log.warning("[apps_eval] Failed to load specs: %s — using defaults", exc)

    _SPEC_CACHE = EvalAgentSpecs()
    return _SPEC_CACHE
