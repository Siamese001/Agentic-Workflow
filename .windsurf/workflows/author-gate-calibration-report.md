---
description: Generate weekly Author-Gate calibration report — firing rate, FP rate, flip-readiness. Invokes `.windsurf/scripts/generate_calibration_report.py` and writes `docs/reports/author-gate/<YYYY-Www>.md`.
---

> **Cascade workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules.

# Author-Gate Calibration Report

Produces a weekly signal report consumed by the shadow-mode-flip decision and
the Author-Gate SVP Engineering review.

## When to invoke

- Every Monday morning for the prior week (standing cadence)
- Before flipping `enforcement: shadow` → `block` in `author_gate_triggers.yaml` (~2026-04-28)
- After any triggers.yaml tuning to confirm FP rate trajectory
- When an SVP review asks "is Author-Gate working?"

## Steps

### 1. Run the report

```bash
# Current week (Mon 00:00 UTC → Sun 23:59 UTC)
python .windsurf/scripts/generate_calibration_report.py

# Previous week
python .windsurf/scripts/generate_calibration_report.py --week-offset 1

# Print only, don't write
python .windsurf/scripts/generate_calibration_report.py --no-write
```

### 2. Read the **Flip Readiness** section first

| Recommendation | Meaning | Action |
|---|---|---|
| **GO** | FP rate < 5%, no ceiling breaches, events observed | Safe to flip `enforcement: block` |
| **HOLD** | Insufficient signal OR FP rate too high | Tune `author_gate_triggers.yaml`; re-bake |
| **INVESTIGATE** | Denial ceiling breached | Likely a bug or overaggressive trigger — stop before flip |

### 3. Inspect top triggers

If one trigger (e.g. `HITL-1.2`) accounts for >80% of fires, it's either:
- Genuinely the most valuable trigger (confirm with decision outcomes)
- Too broad (consider raising `files_changed_min` or tightening globs)

### 4. Inspect decisions

- **Override rate > 40%** → recommender is miscalibrated; review scoring rules
- **Rubber-stamps > 20%** of selections → UI too easy to click through
- **`unbound` outcomes > 50%** → `post_commit_outcome_binder` not catching commits; check git hook installation

### 5. Archive report

Report is auto-written to `docs/reports/author-gate/<YYYY-Www>.md`. Commit it:

```bash
git add docs/reports/author-gate/
git commit -m "author-gate: calibration report for <week>"
```

### 6. (Optional) Post summary to Notion HITL Decision Ledger

Create a row in the HITL Decision Ledger DB (database_id
`18bb9145-1320-4191-8b14-6c309776bcf5`) via `API-post-page`. Include:

- Title: `Calibration <YYYY-Www> — <GO|HOLD|INVESTIGATE>`
- Decision Type: `Rule Change` (if tuning) or leave unset (pure signal report)
- Notes: paste the Flip Readiness table

## Data inputs

- `.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite` — decisions + outcomes
- `artifacts/windsurf/hitl_violations.jsonl` — gate events (shadow warnings and blocks)

## Output

- `docs/reports/author-gate/<YYYY-Www>.md` — canonical report
- stdout — full markdown preview

## Flip-day playbook (2026-04-28)

1. Run: `python .windsurf/scripts/generate_calibration_report.py --week-offset 1`
2. Read Flip Readiness → if **GO**, proceed; else stop and tune
3. Edit `.windsurf/schemas/author_gate_triggers.yaml` → `enforcement: block`
4. Run: `python .windsurf/scripts/pre_author_gate.py --self-test`
5. Commit: `git commit -m "author-gate: flip to enforcement=block [hitl:bypass]"`
6. Monitor `hitl_violations.jsonl` for the next 48h; roll back the single line if false blocks spike

## Reference

- Schema: `.windsurf/schemas/author_gate_triggers.yaml` (`shadow_launch_date`, `shadow_min_days`)
- Rule: `.windsurf/rules/hitl-enforcement.md`
- Plan: `.windsurf/plans/harness-enforcement-rename-a8f21c.md` (W3 shadow mode)
