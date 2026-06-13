# apps_eval — Evaluation Lab

The harness that benchmarks `agentic_core` and the rest of the apps tier against deterministic scenarios. Produces weighted scorecards, regression detection, holdout vs dev separation, and audit-grade reports — the substrate behind the platform's "AI that behaves like software" claim.

## Design Patterns at Work

- **AppSpecificEvaluator + v6 Exit Pipeline** — every grounded app's output is graded against a per-app rubric (`apps_<x>/config/domain_contract/eval_rubrics.yaml`) before commit. Bands: `pass` / `deny` / `escalate` / `unknown` / `unbound` / `error`.
- **Holdout-vs-Dev Discipline** — `fixtures/dev/` is iteratively touched; `fixtures/holdout/` is release-gate-only. Once a developer reads holdout, its value collapses. Enforced by directory contract + future `check_holdout_isolation.py`.
- **Eval-Harness Outcome Ledger** — append-only SQLite ledger (ADR-050 family) records every grader decision with score band, hitl_policy, dim counts, and tracked metrics. Drives weekly Wilson-CI reports and judge-agreement tracking.
- **App-Domain Harness Parity Gate (AEH1)** — 9-check advisory CI gate (`ops_scripts/ci/check_app_domain_harness_parity.py`) surfacing missing rubrics, dead thresholds, fail-open LLM judges, unimplemented judges, and HITL-policy gaps across all 8 apps.
- **Score-Dimension Taxonomy** — every dim is classified `capability` / `regression` / `tracked_metric`. Tracked metrics (e.g. `context_recall`, `context_precision`, `answer_relevancy`) ride at weight=0.0 until producers wire.

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

# Update the regression baseline after a clean run
python -m apps_eval --all --update-baseline

# Run the harness-parity gate
python ops_scripts/ci/check_app_domain_harness_parity.py
APP_DOMAIN_HARNESS_PARITY_FAIL_CLOSED=1 python ops_scripts/ci/check_app_domain_harness_parity.py
```

## Benchmark Suites

| Suite ID                  | Target Module                          | Scenarios |
|---------------------------|----------------------------------------|-----------|
| `routing_enforcement`     | L0 routing enforcement                 | 3         |
| `determinism_contracts`   | L5 static analysis                     | 3         |
| `orchestration_hop`       | rg_orchestrator_facade (apps_rg eval)  | 3         |
| `output_contracts`        | agentic_core execution contracts       | 2         |

## Scorecard Dimensions

| Dimension       | Weight | Pass Threshold |
|-----------------|--------|----------------|
| Correctness     | 3.0    | 80%            |
| Determinism     | 3.0    | 90%            |
| Governance      | 2.5    | 75%            |
| Latency SLA     | 1.5    | 70%            |
| Output Richness | 1.0    | 65%            |

## Grader Types

| `grader_type`        | Use case                                                                 |
|----------------------|--------------------------------------------------------------------------|
| `exact_match`        | String / numeric equality                                                |
| `substring`          | Required substring with hard / soft variants for HITL routing             |
| `llm_as_judge`       | Per-dim rubric grading by a registered judge module                       |
| `tool_calls`         | Trajectory match: strict / unordered / subset / superset                  |
| `state_check`        | Dotted-path assertions vs `output.state_diff`                             |
| `transcript`         | Reads `output.transcript_metrics[dim_id]`                                 |
| `trajectory_match`   | End-to-end trajectory match modes                                         |

## Regression Detection

Baseline stored at `eval_baselines/eval_baseline.json`. Any dimension score drop > 5% (configurable) → `REGRESSION` status. Exit code `2` on regression (distinct from exit code `1` for gate failure).

## Artifacts

All artifacts written to `artifacts/eval/` by default:

- `eval_report_<trace_id[:8]>.md` — full report with scorecard, suite results, regression table
- `scorecard_<trace_id[:8]>.csv` — machine-readable scorecard
- `eval_manifest_<trace_id[:8]>.json` — lightweight manifest
- `run_summary_<trace_id[:8]>.json` — provenance + gate results

## HITL Policy Bands

`AppSpecificEvalResult.hitl_policy` is consumed by the Exit pipeline's `_app_hitl_routing` to decide allow / escalate:

| Policy            | Trigger                                                                       |
|-------------------|-------------------------------------------------------------------------------|
| `none`            | No escalation                                                                  |
| `required_on_low` | Soft-substring fails escalate; hard-substring fails go to deny                  |
| `required_always` | Any non-guardrail bound fail escalates                                         |

## Folder Structure

```
apps_eval/
├── config/                      # EvalAgentSpecs: suites, scorecard, regression config, rubrics
├── engines/                     # ScenarioRunner, ScorecardEngine, RegressionDetector, judges/
├── reasoning/                   # EvalOrchestrator (full pipeline)
├── scripts/                     # run_eval.py CLI
├── types/                       # eval_types.py
├── validators/                  # EvalGateValidator
├── fixtures/                    # dev/ and holdout/ (release-gate only)
├── __init__.py
└── __main__.py
```

## Companion Docs

- `RUNBOOK.md` — on-call decision tree
- `SLO.md` — performance budgets
- `SVP_ENGINEERING_REVIEW.md` — architectural review
- `Apps_eval_AGENTIC_SPINE.md` — spine alignment
