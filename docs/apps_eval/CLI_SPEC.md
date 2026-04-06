# CLI SPEC — apps_eval: Evaluation Lab

## Entrypoints

```bash
python -m apps_eval [OPTIONS]
python apps_eval/scripts/run_eval.py [OPTIONS]
```

---

## Arguments

| Argument           | Type  | Required | Default          | Description                                            |
|--------------------|-------|----------|------------------|--------------------------------------------------------|
| `--suites`         | str   | No       | `""`             | Comma-separated suite IDs to run                       |
| `--all`            | flag  | No       | `False`          | Run all configured suites                              |
| `--out`            | path  | No       | `eval`           | Output directory for artifacts                         |
| `--baseline-dir`   | path  | No       | `eval_baselines` | Directory for regression baseline file                 |
| `--no-regression`  | flag  | No       | `False`          | Skip regression detection (treats all as NO_BASELINE)  |
| `--update-baseline`| flag  | No       | `False`          | Overwrite baseline with current results after run      |
| `--dry-run`        | flag  | No       | `False`          | Score suites; do not emit artifacts                    |
| `--trace-id`       | str   | No       | auto-generated   | Override trace ID                                      |
| `--json-output`    | flag  | No       | `False`          | Print JSON result summary to stdout                    |
| `--log-level`      | str   | No       | `INFO`           | `DEBUG`, `INFO`, `WARNING`                             |

---

## Usage Examples

```bash
# Run all suites
python -m apps_eval --all

# Run specific suites
python -m apps_eval --suites routing_enforcement,determinism_contracts

# Dry run — score without emitting
python -m apps_eval --all --dry-run

# Update baseline after a clean run
python -m apps_eval --all --update-baseline

# Skip regression detection (first run with no baseline)
python -m apps_eval --all --no-regression

# Full CI pipeline command
python -m apps_eval --all \
  --out eval/ \
  --baseline-dir eval_baselines/ \
  --json-output

# Debug a specific suite
python -m apps_eval --suites exec_brief_generation --log-level DEBUG
```

---

## JSON Output Schema (when `--json-output`)

Printed to stdout after all logging.

```json
{
  "trace_id": "string",
  "status": "complete | failed | regression | dry_run",
  "overall_score": 0.0,
  "suites_run": 0,
  "gate_violations": [],
  "regressions": 0,
  "artifacts": []
}
```

---

## Exit Codes

| Code | Condition                                           |
|------|-----------------------------------------------------|
| `0`  | `COMPLETE` or `DRY_RUN`                             |
| `1`  | `FAILED` (gate threshold, suite error, timeout)     |
| `2`  | `REGRESSION` (dimension score drop > tolerance)     |

These exit codes are stable and guaranteed for CI integration.

---

## Suite Selection Logic

| Flags provided           | Suites run                                     |
|--------------------------|------------------------------------------------|
| `--all`                  | All suites in `EvalAgentSpecs.benchmark_suites`|
| `--suites a,b`           | Only suites `a` and `b`                        |
| `--all` + `--suites a,b` | `--all` takes precedence                       |
| Neither                  | All configured suites (same as `--all`)        |

Unknown suite IDs in `--suites` → WARNING logged, skipped, run continues.

---

## Regression Workflow

```bash
# Step 1: First run — no baseline exists
python -m apps_eval --all --no-regression --out eval/

# Step 2: Establish baseline on a known-good run
python -m apps_eval --all --update-baseline --out eval/

# Step 3: CI gate — detect regressions automatically
python -m apps_eval --all --out eval/
# exit 0 → clean
# exit 2 → regression detected, investigate
```

---

## Argument Validation

- `--suites` with unknown suite ID → WARNING + skip (no crash)
- `--update-baseline` + `--dry-run` → warning; baseline NOT updated in dry-run mode
- `--baseline-dir` not existing → created automatically
- `--out` not existing → created automatically
