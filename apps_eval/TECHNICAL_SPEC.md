# TECHNICAL SPEC — apps_eval: Evaluation Lab

## Module Map

```
apps_eval/
├── config/
│   └── agent_spec_config.py     # EvalAgentSpecs, load_eval_specs(), weight validator
├── engines/
│   ├── scenario_runner.py       # ScenarioRunner: dispatch + execution + result
│   ├── scorecard_engine.py      # ScorecardEngine: weighted scoring from suite results
│   └── regression_detector.py  # RegressionDetector: baseline compare + write
├── reasoning/
│   └── EvalOrchestrator.py      # EvalOrchestrator: 5-hop pipeline
├── scripts/
│   └── run_eval.py              # CLI entrypoint
├── types/
│   └── eval_types.py            # EvalStatus, ScenarioResult, SuiteResult, ScorecardRow, ...
├── validators/
│   └── eval_gate_validator.py   # EvalGateValidator
└── __main__.py
```

---

## Key Classes and Contracts

### `EvalAgentSpecs` (Pydantic BaseModel)
- `benchmark_suites: dict[str, BenchmarkSuiteConfig]` — keyed by suite_id
- `scorecard_dimensions: list[ScorecardDimensionConfig]` — weights validated to sum > 0
- `regression: RegressionConfig` — tolerance_delta, baseline_dir, auto_update
- `gate: EvalGateConfig` — min_overall_score, fail_on_regression, max_timeout_violations

**Weight validator** (`@model_validator(mode="after")`): raises `ValidationError` if total weight ≤ 0.

### `ScenarioRunner`
Stateless class. `run_suite(suite_id, display_name, scenario_ids, timeout_sec) → SuiteResult`

**Scenario dispatch:**
- `_SCENARIO_DEFINITIONS: dict[str, dict]` — static registry of all known scenarios
- `_SCENARIO_FN_MAP: dict[str, Callable]` — maps scenario_id → implementation function
- Each impl function returns `tuple[ScenarioOutcome, float, str]`: `(outcome, score, message)`
- Unknown scenario → `ScenarioOutcome.ERROR` (never silently skipped)

**Scenario implementations** cover:
- `agentic_core.L0_routing.enforcement.policy_hash_enforcer` (3 scenarios)
- `agentic_core.L5_safety.static_checks.determinism_serialization_check` (3 scenarios)
- `apps_exec.reasoning.ExecOrchestrator` (3 scenarios)
- `apps_rg.reasoning.RgResumeOrchestrator` (3 scenarios)
- `agentic_core.interfaces.execution_contracts` (2 scenarios)

All use `try/except ImportError` → `ScenarioOutcome.SKIP` if module unavailable in eval env.

### `ScorecardEngine`
Stateless class. `compute(suite_results: list[SuiteResult]) → ScorecardResult`

**Dimension mapping:**
```python
_SUITE_TO_DIMENSION: dict[str, str] = {
    "routing_enforcement": "governance",
    "determinism_contracts": "determinism",
    "orchestration_hop": "correctness",
    "output_contracts": "correctness",
    "exec_brief_generation": "output_richness",
}
```
Suites mapping to the same dimension are averaged.
Overall score = `sum(score_d * weight_d) / sum(weight_d)`.

### `RegressionDetector`
- Baseline path: `{baseline_dir}/eval_baseline.json`
- Baseline schema: `{"trace_id": str, "scores": {dimension_id: float}}`
- Delta = `current_score - baseline_score`
- `delta < -tolerance_delta` → `RegressionVerdict.REGRESSION`
- `delta < 0` → `RegressionVerdict.WARN`
- `auto_update=True` → overwrites baseline after detection

### `EvalOrchestrator` (dataclass)
```python
@dataclass
class EvalOrchestrator:
    dry_run: bool = False
    output_dir: str = "artifacts/eval"
    baseline_dir: str = "eval_baselines"
    gate_mode: str = "HARD_FAIL"
    hop_checkpoints: list[dict] = field(default_factory=list)

    def run(self, request: EvalRequest) → EvalResult: ...
```
**Hops:**
1. `HOP-1-SUITES` → Run all requested suites via `ScenarioRunner`
2. `HOP-2-SCORECARD` → `ScorecardEngine.compute(suite_results)`
3. `HOP-3-REGRESSION` → `RegressionDetector.detect(scorecard_rows, trace_id, auto_update)`
4. `HOP-4-GATE` → `EvalGateValidator.validate(...)`
5. `HOP-5-EMIT` → Write `eval_report.md`, `scorecard.csv`, `eval_manifest.json`, `run_summary.json`

---

## Data Flow

```
EvalRequest(suite_ids, dry_run, compare_baseline, emit_scorecard_csv)
    │
    ▼
ScenarioRunner × N suites → list[SuiteResult(scenarios, pass_rate, mean_latency_ms)]
    │
    ▼
ScorecardEngine → ScorecardResult(rows: list[ScorecardRow], overall_score, total_weight)
    │
    ▼
RegressionDetector → RegressionResult(records, regression_count, baseline_loaded)
    │
    ▼
EvalGateValidator → EvalGateResult(passed, violations, overall_score)
    │
    ▼  (if passed or LOG_ONLY)
Artifact Emission → [eval_report_*.md, scorecard_*.csv, eval_manifest_*.json, run_summary_*.json]
    │
    ▼
EvalResult(trace_id, status, suite_results, scorecard, regression_records,
           overall_score, gate_violations, artifact_paths, run_summary_path)
```

---

## Provenance Contract

```python
provenance = {
    "trace_id": str,          # SHA256[:16] of sorted suite IDs
    "suite_ids": list[str],
    "app": "apps_eval",
    "checkpoints": list[str]  # HOP IDs completed
}
```

---

## Exit Code Contract

| `EvalResult.status`  | Exit Code | Description              |
|----------------------|-----------|--------------------------|
| `COMPLETE`           | 0         | All gates passed         |
| `DRY_RUN`            | 0         | Dry run completed        |
| `FAILED`             | 1         | Gate threshold violation |
| `REGRESSION`         | 2         | Regression detected      |

---

## Dependency Surface

| Dependency    | Reason                              |
|---------------|-------------------------------------|
| `pydantic`    | Config schemas + weight validator   |
| `csv`         | Scorecard CSV emission              |
| `json`        | Manifest + run summary              |
| `hashlib`     | Trace ID                            |
| `time`        | Scenario latency measurement        |
| `pathlib`     | File operations                     |
| `tempfile`    | Nondeterminism test (temp files)    |

External dependencies tested via `ImportError → SKIP` pattern. No hard agentic_core dependency.

---

## Extension Points

| Point                | How to extend                                                |
|----------------------|--------------------------------------------------------------|
| New benchmark suite  | Add `BenchmarkSuiteConfig` to `EvalAgentSpecs.benchmark_suites` |
| New scenario         | Add to `_SCENARIO_DEFINITIONS` + `_SCENARIO_FN_MAP`          |
| New dimension        | Add `ScorecardDimensionConfig` + map suite to dimension      |
| New output format    | Add emitter method to `EvalOrchestrator._emit_artifacts`     |
