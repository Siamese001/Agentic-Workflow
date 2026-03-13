# TEST STRATEGY — apps_eval: Evaluation Lab

## Philosophy

The eval lab tests its own components with the same rigor it applies to other apps.
Scenario execution uses real implementations where available; `SKIP` is acceptable
when a target module is unavailable — but `ERROR` always indicates a bug.
Regression tests are deterministic: a fixed baseline + known score drop → `REGRESSION`.

---

## Test Layers

### Layer 1: Unit Tests (`tests/unit/apps_eval/test_eval_pipeline.py`)

| Test Class                  | Coverage Target                                               |
|-----------------------------|---------------------------------------------------------------|
| `TestEvalAgentSpecs`        | Config loading, weight sum > 0 validator, required suites     |
| `TestScenarioRunner`        | Known scenario, unknown scenario ERROR, pass rate computation |
| `TestScorecardEngine`       | Perfect score, zero score, verdicts, empty suites             |
| `TestRegressionDetector`    | No baseline, regression detected, within tolerance, auto-update |
| `TestEvalGateValidator`     | Clean pass, score below threshold, regression blocks          |
| `TestEvalOrchestrator`      | Dry-run, scorecard non-empty, artifacts written, trace prop   |
| `TestEvalRunSummary`        | `to_dict()` completeness                                      |

### Layer 2: Self-Eval (apps_eval evaluates itself)

```bash
# apps_eval runs its own exec_brief_generation suite
python -m apps_eval --suites exec_brief_generation --dry-run
# Validates that the eval lab can evaluate apps_exec without errors
```

### Layer 3: Scenario Coverage Matrix

Every scenario in `_SCENARIO_DEFINITIONS` must have:
1. A test asserting it returns a valid `ScenarioOutcome` (not raises)
2. A test asserting `latency_ms >= 0`
3. A test asserting `message` is non-empty

### Layer 4: Regression Detection Tests

```python
def test_regression_detected_when_drop_exceeds_tolerance(tmp_path):
    # Write baseline with score=0.90
    # Run with current score=0.80
    # Assert verdict == REGRESSION, regression_count == 1
```

These tests use `tmp_path` and do NOT depend on any pre-existing baseline files.

### Layer 5: Acceptance Tests

| Scenario                                    | Expected Outcome                        |
|---------------------------------------------|-----------------------------------------|
| `--all --dry-run`                           | Status `DRY_RUN`, scorecard rows > 0   |
| Drop of 10% in one dimension                | Status `REGRESSION`, exit 2            |
| Unknown suite in `--suites`                 | Warning logged, suite skipped, no crash |
| `scorecard.csv` with all dimensions         | Header row present, correct columns    |
| `eval_report.md` after run                  | Contains Scorecard + Suite Results     |

---

## Run Commands

```bash
pytest tests/unit/apps_eval/ -v
pytest tests/unit/apps_eval/ --cov=apps_eval --cov-report=term-missing

# Specific regression test
pytest tests/unit/apps_eval/test_eval_pipeline.py::TestRegressionDetector -v
```

---

## Coverage Targets

| Module                                  | Target Coverage |
|-----------------------------------------|-----------------|
| `config/agent_spec_config.py`           | 90%             |
| `engines/scenario_runner.py`            | 80%             |
| `engines/scorecard_engine.py`           | 90%             |
| `engines/regression_detector.py`        | 90%             |
| `validators/eval_gate_validator.py`     | 90%             |
| `reasoning/EvalOrchestrator.py`         | 80%             |

---

## Exit Code Tests

Must have explicit tests for:
- `main()` returns `0` on clean run
- `main()` returns `2` when regression detected
- `main()` returns `1` on gate threshold failure

These must use mock/stub to avoid real file I/O in unit scope.

---

## Forbidden Test Patterns

- No test that accepts any `ScenarioOutcome` as valid — must check for specific outcomes.
- No floating-point `==` comparison without tolerance (use `abs(a - b) < 0.001`).
- No test that depends on ordering of `scorecard.rows` without explicit sort.
- No baseline files checked into the repository (use `tmp_path` exclusively).
