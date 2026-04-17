# F2.1 Reporting Reconciliation Report

**Pass type:** reporting-only cleanup. No graph content changed. Canonical YAML untouched.

## Canonical source-of-truth recount

Programmatic recount from `docs/wave_e/99_integration_v12/canonical/*.yaml`:

| Entity | Count |
|---|---:|
| Families | 12 |
| Atoms total | 61 |
| Atoms ACTIVE | 60 |
| Atoms EXCLUDED | 1 |
| Atoms NORMATIVE | 55 |
| Atoms WEAK_EVIDENCE | 5 |
| Edges total | 26 |
| Edges NORMATIVE | 18 |
| Edges WEAK_EVIDENCE | 8 |
| Sources | 12 |
| Exclusions | 3 |
| Global coverage | 0.9167 GREEN |
| Bucket distribution (G/Y/R) | 9 / 2 / 1 |

## Source-authority-class recount

| Class | Rank | Count | IDs |
|---|---:|---:|---|
| CONSTITUTIONAL | 1 | 1 | SRC-RULE-001 |
| GOVERNANCE | 2 | 4 | SRC-RULE-002, SRC-INT-001, SRC-INT-002, SRC-INT-004 |
| GOVERNING_SEMANTICS | 3 | 0 | — |
| ARCHITECTURAL | 4 | 6 | SRC-INT-003, SRC-ADR-002, SRC-ADR-003, SRC-ADR-004, SRC-ADR-005, SRC-ADR-006 |
| OPERATIONAL | 5 | 0 | — |
| ADVISORY | 6 | 1 | SRC-ADR-001 |
| INTERNAL_ONLY | 7 | 0 | — |
| **Total** | — | **12** | — |

## Weak-edge recount (8 total)

| Edge ID | Source evidence | Target evidence | Dual-NORMATIVE? |
|---|---|---|:---:|
| INT-F02.01-F01.05-01 | NORMATIVE | NORMATIVE | ✅ |
| INT-F05.04-F06.01-01 | WEAK_EVIDENCE | NORMATIVE | ❌ |
| INT-F07.03-F02.01-01 | WEAK_EVIDENCE | NORMATIVE | ❌ |
| INT-F07.03-F05.01-01 | WEAK_EVIDENCE | NORMATIVE | ❌ |
| INT-F08.04-F09.01-01 | NORMATIVE | NORMATIVE | ✅ |
| INT-F09.05-F08.04-01 | NORMATIVE | NORMATIVE | ✅ |
| INT-F12.05-F02.01-01 | NORMATIVE | NORMATIVE | ✅ |
| INT-F12.08-F08.03-01 | NORMATIVE | NORMATIVE | ✅ |

5 of 8 weak edges have both endpoints NORMATIVE. 3 involve a WEAK atom endpoint (F05.04 or F07.03).

## Issues found and corrected

### Issue A — Source-authority GOVERNANCE tally typo

- **Found in:** `integration_validation_report.md` source authority table.
- **Defect:** Row read "GOVERNANCE (2) | 3 (SRC-RULE-002, SRC-INT-001, SRC-INT-002, SRC-INT-004) — actually 4". The count cell contradicted its own ID list.
- **Source of truth:** 4 GOVERNANCE sources in canonical `sources.yaml`.
- **Corrected in:** `integration_validation_report.md` (count fixed to 4, contradiction removed).

### Issue B — Weak-edge count disagreement across reports

- **Found in:** `coverage_report.md`, `merge_conflicts_register.md`, `hitl_decision_ledger.md`.
- **Defect:**
  - `coverage_report.md` said "Five edges retain `evidence_class: WEAK_EVIDENCE`" in its lead sentence, then listed 8 in its bullet list.
  - `merge_conflicts_register.md` DEC-v12-03 referenced 3 specific edges as if they were the total.
  - `hitl_decision_ledger.md` DEC-v12-03 said 8 in one spot.
- **Source of truth:** 8 WEAK_EVIDENCE edges in canonical `edges.yaml`.
- **Corrected in:** all three docs now state **8** as the total and list all 8 edges where enumerated.

### Issue C — Overbroad wording "despite NORMATIVE endpoints"

- **Found in:** `coverage_report.md`, `hitl_decision_ledger.md`.
- **Defect:** Earlier wording implied all weak edges have NORMATIVE endpoints.
- **Source of truth:** Only 5 of 8 weak edges have both endpoints NORMATIVE. The other 3 involve WEAK atom endpoints (F05.04 in 1 edge, F07.03 in 2 edges).
- **Corrected in:** `coverage_report.md`, `hitl_decision_ledger.md`, `integration_validation_report.md`, `merge_conflicts_register.md` — all now state the 5/3 breakdown and explain the endpoint evidence before claiming any edge is a candidate for upgrade.

### Issue D — Headline count alignment

- **Found in:** `canonical/README.md` vs `coverage_report.md` vs `integration_validation_report.md`.
- **Defect:** Minor — `canonical/README.md` already matched canonical YAML. Wave-level `README.md` did not exist.
- **Corrected in:** Added `docs/wave_e/99_integration_v12/README.md` (wave-level index) using canonical counts. All published headline counts now align across the reporting set.

## Docs corrected

| File | Issues corrected |
|---|---|
| `docs/wave_e/99_integration_v12/README.md` | Created (wave-level index with canonical counts) |
| `docs/wave_e/99_integration_v12/coverage_report.md` | Issue B (weak-edge count to 8), Issue C (endpoint-evidence wording), Issue D (headline alignment) |
| `docs/wave_e/99_integration_v12/merge_conflicts_register.md` | Issue B (weak-edge count to 8), Issue C |
| `docs/wave_e/99_integration_v12/hitl_decision_ledger.md` | Issue B (weak-edge count to 8), Issue C (DEC-v12-03 rewritten with 5/3 breakdown) |
| `docs/wave_e/99_integration_v12/integration_validation_report.md` | Issue A (GOVERNANCE=4), Issue B, Issue C, Issue D |
| `docs/wave_e/99_integration_v12/canonical/README.md` | Not modified — already consistent with canonical YAML |

## Graph content change

**None.**

No edits to `canonical/*.yaml`. No edits to schema. No edits to proposal waves. No edits to v1.1. No new sources, atoms, edges, families, or exclusions.

## Remaining unresolved count mismatches

**None.** All headline counts, tallies, and enumerated weak-edge lists across the five existing v1.2 reporting docs (plus the new wave-level README) now match canonical YAML.

## Scope compliance

- ✅ No schema file touched.
- ✅ No canonical YAML touched.
- ✅ No proposal-wave file touched.
- ✅ No v1.1 file touched.
- ✅ Only files under `docs/wave_e/99_integration_v12/` (non-canonical subdirectory) were modified.
