# Wave E1 + F1 — Canonical Requirement Graph v1.1

**Status:** Published canonical output of the F1 integration pass on top of v1.
**Schema SSOT:** `docs/wave_e/00_schema/requirement_graph_schema.yaml`

## Contents

- `families.yaml` — 12 ACTIVE Family records (unchanged from v1).
- `atoms.yaml` — 61 atoms (60 ACTIVE + 1 EXCLUDED). **Delta:** F12.05 patched, F12.07/F12.08 added.
- `edges.yaml` — 26 ACTIVE edges (23 from v1 + 3 from F1).
- `sources.yaml` — 6 SourceAuthorityRecords (5 from v1 + SRC-INT-004).
- `exclusions.yaml` — 3 Exclusion records (unchanged from v1).
- `scorecards/SCORE-F<NN>-INTEGRATION.yaml` — 12 per-family scorecards.

## Headline Counts (v1.1)

| Entity | v1 | v1.1 | Delta |
|---|---:|---:|---:|
| Family | 12 | 12 | 0 |
| Atom (ACTIVE) | 58 | 60 | +2 |
| Atom (EXCLUDED) | 1 | 1 | 0 |
| Edge (ACTIVE) | 23 | 26 | +3 |
| SourceAuthorityRecord | 5 | 6 | +1 |
| Exclusion | 3 | 3 | 0 |

## Coverage

- Global coverage: **0.776 YELLOW** (45 NORMATIVE / 58 counted after v1.1).

Precise: `45 / (45 + 13 + 0) = 0.7759`. Not rounded up.

- v1 global: 0.741 RED.
- **v1.1 bucket flip:** RED → YELLOW.

Detailed delta analysis in `../coverage_report.md`.

## Merge Summary

Three v1.1-specific decisions logged in `../hitl_decision_ledger.md` (HITL-INT-V11-001..003). Merge conflicts in `../merge_conflicts_register.md` (MC-V11-01..04).

## Validation

`../integration_validation_report.md` records the F1 integration QA pass.

## Publishable?

**YES — canonical v1.1 is publishable** with YELLOW global coverage and F04/F07/F08 still RED. The bucket flip is the material v1.1 outcome.
