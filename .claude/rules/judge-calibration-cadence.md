
<!-- Converted from `.claude/rules/judge-calibration-cadence.md`. Original Cursor trigger: `model_decision`. -->

# Judge Calibration Cadence

## The Invariant

> ⛔ **Every LLM-based judge (runtime trace-grader per ADR-036, consensus/
> reference/pairwise judges per `config/judges/rubrics.yaml`) MUST be
> recalibrated against human expert labels on a bounded cadence. Judges whose
> last calibration is stale OR whose `unknown_fraction` exceeds its
> `unknown_budget` SHALL NOT drive a §5 disposition or a §6D promotion.**

This rule closes gap **G8** in plan `exit-eval-spine-gap-ce683b.md`. Anthropic
explicitly calls for periodic human calibration of model-based graders.

## Calibration cadence

| Surface | Default cadence | Min sample size |
|---|---|---|
| Runtime trace-grader (ADR-036) | **weekly** | 30 human-labeled runs |
| Dataset rubric judges (rubrics.yaml) | **biweekly** | 50 human-labeled scenarios per dim |
| Pairwise / reference judges | **monthly** | 30 pairs |

Cadence is a **minimum frequency**, not a cap.

## Calibration ledger SSOT

- Path: `data/judge_calibration/<judge_id>/<YYYY-Www>.json`
- Required fields:
  - `judge_id`, `rubric_version`, `model`, `window_start`, `window_end`
  - `sample_size`, `human_agreement_rate`, `per_dim_agreement`
  - `unknown_fraction_observed`
  - `operator` (human calibrator id)
  - `calibration_snapshot` (opaque sha that flows into
    `ExitDecision.judge_calibration_snapshot`)

## Watchdog conditions (automatic disqualification)

A judge is **disqualified** from driving §5 or §6D when any of:

1. `days_since_last_calibration > cadence_days × 1.5`.
2. `unknown_fraction_observed > unknown_budget` (per-dim) in the last window.
3. `human_agreement_rate < 0.7` in the last calibration window.
4. `rubric_version` changed since last calibration.

When disqualified, the consensus aggregator MUST treat that judge's scores as
`Unknown`. If enough judges are disqualified that `require_min_judges` cannot
be satisfied, disposition is forced to `escalate_hitl` with
`hitl_class = LOW_CONFIDENCE`.

## Writeback contract

After every calibration run, operator writes the ledger row AND updates the
judge's `calibration_snapshot` metadata. Subsequent ExitDecisions carry the new
snapshot id. The snapshot id is the audit-bind between a produced score and the
calibration state that produced it.

## Bypass

`JUDGE_CALIBRATION_CADENCE_BYPASS=1` — logs a bypass row to
`artifacts/cursor/judge_calibration_bypass.jsonl`. Reserved for scripted
batch runs or acknowledged experimental windows.

## Enforcement layers

- **This rule (advisory)** — shapes judge-usage decisions at §5 and §6B.
- **Watchdog job** (follow-up execution plan) — scheduled process that reads
  the ledger, flags stale judges, emits a Notion row in the SVP Engineering
  Reviews DB for each disqualification.
- **CI gate** (follow-up) — fails when `rubric_version` advances without a new
  calibration ledger row.

## References

- Anthropic — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Rubric SSOT — `config/judges/rubrics.yaml`, `config/judges/trace_rubric.yaml`
- Plan — `.claude/plans/exit-eval-spine-gap-ce683b.md` §W5.2
- ADR-032 — LLM judge hardening
