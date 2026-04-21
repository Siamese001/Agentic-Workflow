# Author-Gate Calibration Reports

Weekly calibration reports for the Author-Gate harness enforcement subsystem.

## Cadence

- **Frequency:** weekly, Monday morning for the prior week
- **Generator:** `python .windsurf/scripts/generate_calibration_report.py`
- **Slash command:** `/author-gate-calibration-report`
- **Output:** `docs/reports/author-gate/<YYYY-Www>.md` (one per ISO week)

## Running ad-hoc

```bash
# Current week
python .windsurf/scripts/generate_calibration_report.py

# Previous week (common for Monday reports)
python .windsurf/scripts/generate_calibration_report.py --week-offset 1

# Print without writing
python .windsurf/scripts/generate_calibration_report.py --no-write
```

## What each report tells you

| Section | Signal |
|---|---|
| **Flip Readiness** | GO / HOLD / INVESTIGATE recommendation for flipping `enforcement: shadow` → `block` |
| **Gate Firing** | Total events, daily rate, unique fingerprints, events by severity, top triggers |
| **Decisions** | Surfaced decisions count, override rate, rubber-stamp rate, outcome distribution |
| **Criterion table** | FP rate vs 5% target, consecutive denials vs 3 cap, total denials vs 20 cap |

## Key milestones

| Date | Event |
|---|---|
| **2026-04-21** | Shadow mode launched; first report W17 |
| **2026-04-28** | Target flip date (shadow → block), if Flip Readiness = GO |
| **Weekly thereafter** | Standing Monday cadence |

## Flip-day playbook

See `.windsurf/workflows/author-gate-calibration-report.md` § "Flip-day playbook (2026-04-28)".

Short version:
1. Run the report for `--week-offset 1` (the bake week)
2. Read Flip Readiness → if **GO**, proceed
3. Edit `.windsurf/schemas/author_gate_triggers.yaml` → `enforcement: block`
4. Commit, monitor `artifacts/windsurf/hitl_violations.jsonl` for 48h
5. Rollback is a single-line revert if false blocks spike

## Data inputs (for debugging)

- `.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite` — decisions + outcomes (tamper-evident via hash-chain since 2026-04-21)
- `artifacts/windsurf/hitl_violations.jsonl` — gate events (shadow warnings and real blocks)
- `artifacts/windsurf/author_gate_misses.jsonl` — retroactive miss detector (responses that should have surfaced an Author-Gate packet but didn't)

## Retention

Reports are committed to git; this directory is the canonical record. No rotation needed (markdown files are small and compress well).

## Historical reports

One row per ISO week. Sort lexicographically — `2026-W17.md` precedes `2026-W18.md`.
