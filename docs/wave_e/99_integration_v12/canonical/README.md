# Canonical Requirement Graph v1.2

**Produced at wave:** F2 integration pass
**Predecessor:** `docs/wave_e/99_integration_v11/canonical/` (v1.1)
**Delta source:** `docs/wave_e/F2_source_authoring/proposals/`
**Schema SSOT:** `docs/wave_e/00_schema/requirement_graph_schema.yaml`

## Counts

| Entity | v1.1 | v1.2 | Delta |
|---|---:|---:|---:|
| Families | 12 | 12 | 0 |
| Atoms (total) | 61 | 61 | 0 |
| Atoms (ACTIVE) | 60 | 60 | 0 |
| Atoms (EXCLUDED) | 1 | 1 | 0 |
| Atoms (NORMATIVE) | 46 | **55** | **+9** |
| Atoms (WEAK_EVIDENCE) | 14 | **5** | **-9** |
| Edges | 26 | 26 | 0 |
| Sources | 6 | **12** | **+6** |
| Exclusions | 3 | 3 | 0 |

## Global Coverage

| Metric | v1.1 | v1.2 |
|---|---:|---:|
| Coverage score | 0.767 YELLOW | **0.917 GREEN** |
| GREEN families | 5 | **9** |
| YELLOW families | 4 | **2** |
| RED families | 3 | **1** |

## What changed in v1.2

1. **6 new SourceAuthorityRecords** registered (SRC-ADR-001 through SRC-ADR-006). All point at pre-existing canonical repo documents that prior waves missed.
2. **9 WEAK_EVIDENCE atoms upgraded to NORMATIVE** via the new ARCHITECTURAL-rank sources: F01.06, F03.04, F07.01, F07.02, F08.01, F08.03, F08.04, F08.05, F09.05.
3. **1 supplementary binding** added to F04.04 (SRC-ADR-005) — evidence class remains WEAK_EVIDENCE because the source is adjacent, not direct.
4. **No new families, atoms, edges, or exclusions.**
5. **No fabricated documents.**
6. **No schema drift.**

## Bucket flips

| Family | v1.1 → v1.2 | Notes |
|---|---|---|
| F01 | YELLOW 0.83 → GREEN 1.00 | F01.06 closed |
| F03 | YELLOW 0.75 → GREEN 1.00 | F03.04 closed |
| F07 | RED 0.25 → YELLOW 0.75 | F07.01/.02 closed; F07.03 blocked by advisory-only source |
| F08 | RED 0.20 → GREEN 1.00 | Two-level flip; eval_pipeline_acceptance was the long-missing exit-spine source |
| F09 | YELLOW 0.80 → GREEN 1.00 | F09.05 closed |

Unchanged: F02, F06, F10, F11, F12 (all GREEN); F05 (YELLOW); **F04 (RED, sole remaining)**.

## Remaining blockers

| # | Blocker | Family impact | Required action |
|---|---|---|---|
| **B3** | Context-assembly ADR | **F04 RED** | Author ADR defining attribution (F04.02), no-private-substitute (F04.03), context-assembly idempotence (F04.04). Also releases OOS-003 revisit trigger. **Highest remaining impact.** |
| **F07.03** | Normative escalation-target ADR | F07 stays YELLOW | SRC-ADR-001 already describes ESCALATED-tier routing; promote via HITL review to drop `invalid_for_normative_use=True` marker. |
| **B6** | L3 orchestration charter ADR | F05 stays YELLOW (F05.04 WEAK) | Author L3 charter explicitly defining dispatch role. |
| **B7** | 6 deferred interaction candidates | Graph completeness | Each requires new atoms or edge-kind patches; none closable by F2's source additions. |

## Publishability

**YES — v1.2 is publishable.** Full QA pass in `integration_validation_report.md`:
- 0 orphan references
- 0 duplicate IDs
- 0 binding errors
- 0 advisory-only NORMATIVE atoms
- All 12 sources have real resolvable locators
- Coverage arithmetic verified

See also:
- `../coverage_report.md` — delta-oriented coverage analysis
- `../merge_conflicts_register.md` — merge decisions
- `../hitl_decision_ledger.md` — non-trivial HITL decisions
- `../integration_validation_report.md` — full QA output
