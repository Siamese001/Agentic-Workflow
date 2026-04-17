# Wave E - Integration v1.4

Lane-level index for the F4 integration pass. For the canonical graph README see `canonical/README.md`.

## Canonical graph snapshot (v1.4)

| Entity | Count |
|---|---:|
| Families | 12 |
| Atoms total | 61 |
| Atoms ACTIVE | 60 |
| Atoms EXCLUDED | 1 |
| Atoms NORMATIVE | 60 |
| Atoms WEAK_EVIDENCE | 0 |
| Edges | 26 |
| Edges NORMATIVE | **26** |
| Edges WEAK_EVIDENCE | **0** |
| Sources | 15 |
| Exclusions | 3 |
| **Atom coverage** | **1.000 GREEN** |
| **Edge coverage** | **1.000** (up from 0.692 in v1.3) |
| Bucket distribution (G / Y / R) | **12 / 0 / 0** |

## Sources by authority class (unchanged from v1.3)

| Class | Rank | Count | IDs |
|---|---:|---:|---|
| CONSTITUTIONAL | 1 | 1 | SRC-RULE-001 |
| GOVERNANCE | 2 | 4 | SRC-RULE-002, SRC-INT-001, SRC-INT-002, SRC-INT-004 |
| ARCHITECTURAL | 4 | 9 | SRC-INT-003, SRC-ADR-002..009 |
| ADVISORY | 6 | 1 | SRC-ADR-001 |
| **Total** | — | **15** | — |

## Exclusions by reason (v1.4)

| Reason | Count | IDs |
|---|---:|---|
| OUT_OF_CHARTER | 2 | OOS-001, OOS-002 |
| SUPERSEDED | **1** | **OOS-003** (moved from NOT_YET_DECIDED in F4) |
| NOT_YET_DECIDED | 0 | — |

## Family buckets

| Bucket | Count | Families |
|---|---:|---|
| GREEN (≥0.90) | **12** | F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12 |
| YELLOW | 0 | — |
| RED | 0 | — |

## Artifacts in this wave directory

- `canonical/` — v1.4 canonical graph YAML + scorecards + canonical README
- `coverage_report.md` — delta vs v1.3
- `merge_conflicts_register.md` — merge decisions for F4 integration
- `hitl_decision_ledger.md` — non-trivial HITL decisions
- `integration_validation_report.md` — full QA output

## Publishability

**Canonical v1.4 is publishable.** Both the atom surface and the edge surface are fully NORMATIVE. The only open follow-up (B7 — 6 deferred interaction candidates) requires a future wave with explicit HITL approval and is out of F4's scope.
