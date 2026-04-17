# Wave E - Integration v1.2

Lane-level index for the F2 integration pass. For the canonical graph README see `canonical/README.md`.

## Canonical graph snapshot (v1.2)

All figures recounted directly from `canonical/*.yaml` during the F2.1 reporting reconciliation pass.

| Entity | Count |
|---|---:|
| Families | 12 |
| Atoms total | 61 |
| Atoms ACTIVE | 60 |
| Atoms EXCLUDED | 1 |
| Atoms NORMATIVE | 55 |
| Atoms WEAK_EVIDENCE | 5 |
| Edges | 26 |
| Edges NORMATIVE | 18 |
| Edges WEAK_EVIDENCE | 8 |
| Sources | 12 |
| Exclusions | 3 |
| **Global coverage** | **0.9167 GREEN** |
| Bucket distribution (G / Y / R) | **9 / 2 / 1** |

Coverage = NORMATIVE / (NORMATIVE + WEAK_EVIDENCE) atoms. EXCLUDED atoms are excluded from the denominator.

## Sources by authority class

| Class | Rank | Count | IDs |
|---|---:|---:|---|
| CONSTITUTIONAL | 1 | 1 | SRC-RULE-001 |
| GOVERNANCE | 2 | 4 | SRC-RULE-002, SRC-INT-001, SRC-INT-002, SRC-INT-004 |
| ARCHITECTURAL | 4 | 6 | SRC-INT-003, SRC-ADR-002, SRC-ADR-003, SRC-ADR-004, SRC-ADR-005, SRC-ADR-006 |
| ADVISORY | 6 | 1 | SRC-ADR-001 |
| **Total** | — | **12** | — |

## Family buckets

| Bucket | Count | Families |
|---|---:|---|
| GREEN (≥0.90) | 9 | F01, F02, F03, F06, F08, F09, F10, F11, F12 |
| YELLOW (0.70–0.89) | 2 | F05, F07 |
| RED (<0.70) | 1 | F04 |

## Artifacts in this wave directory

- `canonical/` — v1.2 canonical graph YAML + scorecards + canonical README
- `coverage_report.md` — delta vs v1.1
- `merge_conflicts_register.md` — merge decisions
- `hitl_decision_ledger.md` — non-trivial decisions
- `integration_validation_report.md` — QA output
- `reporting_reconciliation_report.md` — F2.1 report-only reconciliation log

## Publishability

Canonical v1.2 is publishable. All reporting docs in this directory are now internally consistent with `canonical/*.yaml` per `reporting_reconciliation_report.md`.
