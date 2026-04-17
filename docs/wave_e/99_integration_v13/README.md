# Wave E - Integration v1.3

Lane-level index for the F3 integration pass. For the canonical graph README see `canonical/README.md`.

## Canonical graph snapshot (v1.3)

| Entity | Count |
|---|---:|
| Families | 12 |
| Atoms total | 61 |
| Atoms ACTIVE | 60 |
| Atoms EXCLUDED | 1 |
| Atoms NORMATIVE | 60 |
| Atoms WEAK_EVIDENCE | 0 |
| Edges | 26 |
| Edges NORMATIVE | 18 |
| Edges WEAK_EVIDENCE | 8 |
| Sources | 15 |
| Exclusions | 3 |
| **Global coverage** | **1.000 GREEN** |
| Bucket distribution (G / Y / R) | **12 / 0 / 0** |

Coverage = NORMATIVE / (NORMATIVE + WEAK_EVIDENCE) across ACTIVE atoms. EXCLUDED atoms are omitted from the denominator.

## Sources by authority class

| Class | Rank | Count | IDs |
|---|---:|---:|---|
| CONSTITUTIONAL | 1 | 1 | SRC-RULE-001 |
| GOVERNANCE | 2 | 4 | SRC-RULE-002, SRC-INT-001, SRC-INT-002, SRC-INT-004 |
| ARCHITECTURAL | 4 | 9 | SRC-INT-003, SRC-ADR-002, SRC-ADR-003, SRC-ADR-004, SRC-ADR-005, SRC-ADR-006, SRC-ADR-007, SRC-ADR-008, SRC-ADR-009 |
| ADVISORY | 6 | 1 | SRC-ADR-001 |
| **Total** | — | **15** | — |

## Family buckets

| Bucket | Count | Families |
|---|---:|---|
| GREEN (≥0.90) | **12** | F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12 |
| YELLOW (0.70–0.89) | 0 | — |
| RED (<0.70) | 0 | — |

## Artifacts in this wave directory

- `canonical/` — v1.3 canonical graph YAML + scorecards + canonical README
- `coverage_report.md` — delta vs v1.2
- `merge_conflicts_register.md` — merge decisions for F3 integration
- `hitl_decision_ledger.md` — non-trivial HITL decisions
- `integration_validation_report.md` — full QA output

## Publishability

**Canonical v1.3 is publishable.** All five previously-weak atoms closed; all 12 families GREEN. Remaining follow-ups (D-v12-01 weak-edge upgrades, OOS-003 revision, B7 interaction candidates) do not block publication; they are addressed in Wave F4 (`../F4_edge_exclusion_cleanup/`) and later waves.
