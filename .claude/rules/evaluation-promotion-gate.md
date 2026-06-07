
<!-- Converted from `.claude/rules/evaluation-promotion-gate.md`. Original Cursor trigger: `model_decision`. -->

# Evaluation Promotion Gate — Regression-Pass Required

## The Invariant

> ⛔ **No prompt / policy / rubric / config change reaches L4 via UWG in §6D
> without passing the regression suite at the pass-rate threshold declared in
> `config/judges/rubrics.yaml → eval_taxonomy.regression.min_pass_rate_target`
> (default `0.98`).**

This rule formalizes v33 §6D "gated review" and closes gap **G7** in plan
`exit-eval-spine-gap-ce683b.md`. Anthropic's capability-vs-regression split
treats regression pass rate near 1.00 as fleet-protecting; anything below the
threshold is a defect.

## What triggers this gate

Any §6D promotion candidate that would change:

- a system / tool / agent **prompt**,
- an L5 **policy** (safety, routing, HITL thresholds),
- a judge **rubric** (`config/judges/*.yaml`),
- a **config** that observably affects agent behavior
  (`*_policies.yaml`, agent specs, routing toggles).

## Required artifacts (before commit)

1. **Regression run evidence** — a run of the regression suite against the
   candidate change, with overall pass rate ≥ threshold. Evidence lives under
   `docs/reports/eval/<date>-<change-slug>.md` and includes:
   - total scenarios
   - pass count, warn count, fail count
   - pass rate
   - per-dimension score deltas vs baseline
   - regression_detector.py verdict
2. **Baseline comparison** — explicit reference to the baseline snapshot used.
3. **No safety-band regressions** — zero new `safety.policy_violation == true`
   outcomes relative to baseline, regardless of pass rate.

## What the gate blocks

- UWG MutationRecord submission (via §6D promote path) when evidence is missing
  or threshold not met.
- Capability→regression graduation when the capability suite has not sustained
  the capability `min_pass_rate_target` for N consecutive runs.

## Bypass

`EVAL_PROMOTION_GATE_BYPASS=1` in the environment — logs a bypass row to
`artifacts/cursor/eval_promotion_bypass.jsonl` and permits a one-off commit.
Reserved for: emergency rollback, acknowledged experimental rollouts, operator
override under SVP engineering authority.

## Enforcement layers

- **This rule (advisory)** — shapes §6D decisions.
- **Deterministic CI gate** (follow-up execution plan) — blocks merges of
  prompt/rubric/policy file changes without a matching regression-run artifact.
- **UWG authority** — ultimate stop-gap; rejects commits that do not cite a
  passing regression run.

## References

- v33 §6D — `docs/reference/_notes/agentic_process_mapping_v34.md`
- Taxonomy — `config/judges/rubrics.yaml → eval_taxonomy`
- Plan — `.cursor/plans/exit-eval-spine-gap-ce683b.md` §W5.1
- Anthropic — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
