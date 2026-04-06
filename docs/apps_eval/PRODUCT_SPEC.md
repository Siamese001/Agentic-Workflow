# PRODUCT SPEC — apps_eval: Evaluation Lab

## Product Intent

`apps_eval` is a benchmarking and evaluation harness for `agentic_core` and application workloads.
It executes deterministic scenarios against platform components, computes a weighted scorecard,
detects regressions against a stored baseline, and produces audit-grade reports.

The app demonstrates engineering rigor — the ability to define measurable acceptance criteria,
track quality over time, and surface regressions before they reach production. It is the
repo's "quality dashboard" made concrete.

---

## Primary Users

| User Persona         | Goal                                                              | Success Signal                                         |
|----------------------|-------------------------------------------------------------------|--------------------------------------------------------|
| **Platform Engineer**| Verify platform contracts hold after a refactoring               | All suites green, no regressions, clean scorecard      |
| **Tech Lead**        | Establish and protect quality baselines                           | Baseline stored, regressions flagged automatically     |
| **CTO / Reviewer**   | See evidence of engineering discipline and quality governance     | Scorecard with weighted dimensions and trend data      |
| **CI Pipeline**      | Gate PRs on evaluation scores                                     | Exit code 0 = pass, 1 = fail, 2 = regression           |

---

## Core User Stories

1. **As a platform engineer,** I want to run all benchmark suites and see a pass/fail result
   so I know if my changes broke any contracts.
2. **As a tech lead,** I want regression detection that compares against a stored baseline
   so I can track quality trends over time.
3. **As a CTO reviewing the repo,** I want to see a weighted scorecard with labelled dimensions
   so I can assess where the platform is strong and where it needs work.
4. **As a CI pipeline,** I want distinct exit codes for "fail", "regression", and "pass"
   so I can gate deployments appropriately.

---

## Benchmark Suites

| Suite ID                  | What It Tests                                              |
|---------------------------|------------------------------------------------------------|
| `routing_enforcement`     | L0 policy hash validation: valid/invalid/missing hash      |
| `determinism_contracts`   | Static nondeterminism detection: time/random/uuid calls    |
| `orchestration_hop`       | Multi-hop pipeline: single/multi/gate-fail scenarios       |
| `output_contracts`        | Output contract signing and tamper detection               |
| `exec_brief_generation`   | apps_exec dry-run: recruiter, CTO, board personas          |

---

## Scorecard Dimensions

| Dimension           | Suites Mapped                             | Weight |
|---------------------|-------------------------------------------|--------|
| Correctness         | orchestration_hop, output_contracts       | 3.0    |
| Determinism         | determinism_contracts                     | 3.0    |
| Governance          | routing_enforcement                       | 2.5    |
| Latency SLA         | cross-suite latency measurements          | 1.5    |
| Output Richness     | exec_brief_generation                     | 1.0    |

---

## Inputs

| Input              | Type       | Required | Description                                     |
|--------------------|------------|----------|-------------------------------------------------|
| `--suites`         | List[str]  | No       | Comma-separated suite IDs                       |
| `--all`            | Flag       | No       | Run all configured suites                       |
| `--out`            | Path       | No       | Output directory (default: `eval/`)             |
| `--baseline-dir`   | Path       | No       | Baseline directory (default: `eval_baselines/`) |
| `--update-baseline`| Flag       | No       | Update baseline after this run                  |
| `--no-regression`  | Flag       | No       | Skip regression detection                       |
| `--dry-run`        | Flag       | No       | Score but do not emit artifacts                 |

---

## Outputs

| Artifact                                    | Format | Description                                       |
|---------------------------------------------|--------|---------------------------------------------------|
| `eval_report_<trace_id[:8]>.md`             | Markdown | Full report: scorecard + suites + regression table |
| `scorecard_<trace_id[:8]>.csv`              | CSV    | Machine-readable scorecard                        |
| `eval_manifest_<trace_id[:8]>.json`         | JSON   | Suite pass rates + lightweight manifest           |
| `run_summary_<trace_id[:8]>.json`           | JSON   | Provenance, overall score, gate violations        |

---

## Exit Codes

| Code | Meaning                              |
|------|--------------------------------------|
| 0    | All gates passed, no regressions     |
| 1    | Gate failure (score below threshold) |
| 2    | Regression detected                  |

---

## Deterministic vs. Model-Driven Boundary

| Stage              | Deterministic? | Notes                                              |
|--------------------|----------------|----------------------------------------------------|
| Scenario execution | Yes            | Fixed inputs, expected outcomes, no LLM calls      |
| Scorecard compute  | Yes            | Weighted arithmetic — pure functions               |
| Regression detect  | Yes            | Delta comparison against stored JSON baseline      |
| Gate validation    | Yes            | Threshold comparisons                              |
| Artifact emission  | Yes            | File writes + CSV/JSON serialization               |

---

## Quality Gates

| Gate ID                         | Threshold                | Action on Fail |
|---------------------------------|--------------------------|----------------|
| `EVAL_SCORE_BELOW_THRESHOLD`    | overall_score ≥ 0.70     | BLOCK          |
| `EVAL_REGRESSION_DETECTED`      | No regression            | BLOCK          |
| `EVAL_SUITE_ERROR`              | No suite errors          | BLOCK          |
| `EVAL_TIMEOUT_VIOLATIONS`       | ≤ 0 timeout violations   | BLOCK          |

---

## Testable Acceptance Criteria

1. `--all --dry-run` returns `DRY_RUN` status with scorecard rows and `artifact_paths == []`.
2. `scorecard.csv` contains `dimension_id`, `score`, `weight`, `weighted_score`, `verdict` columns.
3. Drop of > 5% in any dimension vs. baseline produces `REGRESSION` status and exit code 2.
4. Unknown `--suites` value logs a warning and skips — does not crash.
5. `eval_report.md` contains a Scorecard table, Suite Results section, and Regression Analysis section.
