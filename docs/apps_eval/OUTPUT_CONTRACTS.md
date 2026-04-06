# OUTPUT CONTRACTS — apps_eval: Evaluation Lab

## Overview

Every non-dry-run evaluation produces four artifacts. Every artifact is self-consistent:
the `eval_report.md` and `scorecard.csv` reflect the same data as the `eval_manifest.json`.
Exit codes are distinct: 0 (pass), 1 (gate fail), 2 (regression).

---

## Artifact 1: Evaluation Report (`eval_report_<trace_id[:8]>.md`)

**Type:** Markdown
**Location:** `{output_dir}/eval_report_{trace_id[:8]}.md`
**Emitted when:** Status is `COMPLETE` or `REGRESSION`

### Schema

```markdown
# Evaluation Lab Report

**Trace ID:** `{trace_id}`
**Status:** {status}
**Overall Score:** {overall_score:.1%}
**Gate Violations:** {count}

---

## Scorecard

| Dimension | Score | Weight | Weighted | Verdict |
|-----------|-------|--------|----------|---------|
| ...       | ...   | ...    | ...      | PASS/WARN/FAIL |

---

## Suite Results

### {Suite Display Name} (`{suite_id}`)
- **Pass Rate:** N%
- **Mean Latency:** N ms

  - `✓` `scenario_id` [PASS] score=1.00 — message
  - `✗` `scenario_id` [FAIL] score=0.00 — message

---

## Regression Analysis          ← (only if baseline exists)

| Dimension | Current | Baseline | Delta | Verdict |
|-----------|---------|----------|-------|---------|

---

## Gate Violations              ← (only if violations exist)

- [RULE_ID:SEVERITY] message
```

---

## Artifact 2: Scorecard CSV (`scorecard_<trace_id[:8]>.csv`)

**Type:** CSV
**Location:** `{output_dir}/scorecard_{trace_id[:8]}.csv`
**Emitted when:** Status is `COMPLETE` or `REGRESSION` and `emit_scorecard_csv=True`

### Column Schema

| Column          | Type   | Description                        |
|-----------------|--------|------------------------------------|
| `dimension_id`  | string | Dimension identifier               |
| `display_name`  | string | Human-readable name                |
| `score`         | float  | 4 decimal places                   |
| `weight`        | float  | 1 decimal place                    |
| `weighted_score`| float  | 4 decimal places                   |
| `verdict`       | string | `PASS`, `WARN`, or `FAIL`          |

No header variations. Always UTF-8. First row is always the header row.

---

## Artifact 3: Eval Manifest (`eval_manifest_<trace_id[:8]>.json`)

**Type:** JSON
**Location:** `{output_dir}/eval_manifest_{trace_id[:8]}.json`

### Schema

```json
{
  "trace_id": "string",
  "overall_score": 0.0,
  "suites": [
    {
      "suite_id": "string",
      "pass_rate": 0.0,
      "scenarios": 3
    }
  ]
}
```

---

## Artifact 4: Run Summary (`run_summary_<trace_id[:8]>.json`)

**Type:** JSON
**Location:** `{output_dir}/run_summary_{trace_id[:8]}.json`

### Schema

```json
{
  "trace_id": "string",
  "app": "apps_eval",
  "version": "1.0.0",
  "status": "complete | failed | regression | dry_run",
  "suites_run": 0,
  "scenarios_run": 0,
  "scenarios_passed": 0,
  "overall_score": 0.0,
  "regressions_detected": 0,
  "gate_violations": [],
  "artifacts": [],
  "dry_run": false,
  "error": "",
  "provenance": {
    "trace_id": "string",
    "suite_ids": [],
    "app": "apps_eval",
    "checkpoints": ["HOP-1-SUITES", "HOP-2-SCORECARD", "HOP-3-REGRESSION", "HOP-4-GATE", "HOP-5-EMIT"]
  }
}
```

---

## Scenario Result Contract

Every `ScenarioResult` MUST have:
- `outcome`: one of `PASS`, `FAIL`, `TIMEOUT`, `ERROR`, `SKIP` — never null, never silent
- `score`: float 0.0–1.0
- `message`: non-empty string describing the outcome
- `latency_ms`: float ≥ 0

`SKIP` is NOT a failure. It means the scenario target is unavailable in the current env.
`ERROR` means the scenario implementation threw an unexpected exception.

---

## Regression Baseline Contract

Baseline file: `{baseline_dir}/eval_baseline.json`

```json
{
  "trace_id": "string",
  "scores": {
    "correctness": 0.0,
    "determinism": 0.0,
    "governance": 0.0,
    "latency": 0.0,
    "output_richness": 0.0
  }
}
```

If baseline file does not exist: all verdicts = `NO_BASELINE`. Status is not `REGRESSION`.
If baseline file is corrupt: all verdicts = `NO_BASELINE`. A warning is logged. Run continues.

---

## Exit Code Guarantee

The exit code is always consistent with `EvalResult.status`:
| Status      | Exit Code |
|-------------|-----------|
| `complete`  | 0         |
| `dry_run`   | 0         |
| `failed`    | 1         |
| `regression`| 2         |

No other exit codes are returned. Unhandled exceptions produce exit code 1.
