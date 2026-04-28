# apps_eval — Evaluation Lab

Benchmarks `agentic_core` and application workloads against deterministic scenarios.
Produces weighted scorecards, regression detection, and audit-grade reports.

## Quick Start

```bash
# Run all configured suites
python -m apps_eval --all --out artifacts/eval/

# Run specific suites
python -m apps_eval --suites routing_enforcement,determinism_contracts

# Dry run — score but don't emit files
python -m apps_eval --all --dry-run

# JSON output for CI
python -m apps_eval --all --json-output

# Update baseline after a clean run
python -m apps_eval --all --update-baseline
```

## Benchmark Suites

| Suite ID                  | Target Module                          | Scenarios |
|---------------------------|----------------------------------------|-----------|
| `routing_enforcement`     | L0 routing enforcement                 | 3         |
| `determinism_contracts`   | L5 static analysis                     | 3         |
| `orchestration_hop`       | apps_rg orchestration                  | 3         |
| `output_contracts`        | agentic_core execution contracts       | 2         |
| `exec_brief_generation`   | apps_exec ExecOrchestrator             | 3         |

## Scorecard Dimensions

| Dimension           | Weight | Pass Threshold |
|---------------------|--------|----------------|
| Correctness         | 3.0    | 80%            |
| Determinism         | 3.0    | 90%            |
| Governance          | 2.5    | 75%            |
| Latency SLA         | 1.5    | 70%            |
| Output Richness     | 1.0    | 65%            |

## Regression Detection

Baseline stored at `eval_baselines/eval_baseline.json`.
Any dimension score drop > 5% (configurable) → `REGRESSION` status.
Exit code 2 on regression (distinct from exit code 1 for gate failure).

## Artifacts

All artifacts written to `eval/` by default:

- `eval_report_<trace_id[:8]>.md` — full report with scorecard + suite results + regression table
- `scorecard_<trace_id[:8]>.csv` — machine-readable scorecard
- `eval_manifest_<trace_id[:8]>.json` — lightweight manifest
- `run_summary_<trace_id[:8]>.json` — provenance + gate results

## Folder Structure

```
apps_eval/
├── config/           # EvalAgentSpecs: suites, scorecard dimensions, regression config
├── engines/          # ScenarioRunner, ScorecardEngine, RegressionDetector
├── reasoning/        # EvalOrchestrator (full pipeline)
├── scripts/          # run_eval.py CLI
├── types/            # eval_types.py
├── utils/
├── validators/       # EvalGateValidator
├── __init__.py
└── __main__.py
```
