# Wave E1 — Canonical Requirement Graph v1

**Status:** Published canonical output of the Wave E1 integration pass.
**Schema SSOT:** `docs/wave_e/00_schema/requirement_graph_schema.yaml`

## Contents

- `families.yaml` — 12 ACTIVE Family records.
- `atoms.yaml` — 59 atoms (58 ACTIVE + 1 EXCLUDED).
- `edges.yaml` — 23 ACTIVE InteractionEdge records.
- `sources.yaml` — 5 SourceAuthorityRecords.
- `exclusions.yaml` — 3 Exclusion records (OOS-001, OOS-002, OOS-003).
- `scorecards/SCORE-F<NN>-INTEGRATION.yaml` — 12 per-family coverage scorecards.

## Headline Counts

| Entity | Count | Active | Draft | Unresolved | Excluded | Deprecated |
|---|---:|---:|---:|---:|---:|---:|
| Family | 12 | 12 | 0 | 0 | 0 | 0 |
| RequirementAtom | 59 | 58 | 0 | 0 | 1 | 0 |
| InteractionEdge | 23 | 23 | 0 | 0 | — | 0 |
| SourceAuthorityRecord | 5 | n/a | n/a | n/a | n/a | n/a |
| Exclusion | 3 | n/a | n/a | n/a | n/a | n/a |

## Coverage

- Global coverage: **0.74** (43 NORMATIVE with binding / 58 counted atoms — RED per the ≥0.75 yellow floor).
- Green families: **4** (F02, F06, F10, F11).
- Yellow families: **5** (F01, F03, F05, F09, F12).
- Red families: **3** (F04, F07, F08).

Detailed report in `../coverage_report.md`.

## Merge Summary

See `../merge_conflicts_register.md` and `../hitl_decision_ledger.md` for the non-trivial decisions applied during integration.

## Validation

`../integration_validation_report.md` records the QA pass. All hard-fail checks succeeded; no orphan references, no duplicate IDs, no placeholder SRC IDs in canonical YAML.

## Publishable?

**YES — canonical v1 is publishable** with RED global coverage and known gaps. The graph is schema-valid and internally consistent. The RED score is an honest reflection of missing ARCHITECTURAL-rank sources (exit spine, context idempotence, bounded retry) that Wave F+ is chartered to resolve.
