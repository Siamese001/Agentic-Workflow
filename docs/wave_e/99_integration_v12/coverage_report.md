# v1.2 Coverage Report — Delta vs v1.1

All counts in this report were recounted directly from `canonical/*.yaml` during the F2.1 reporting reconciliation pass. Canonical graph content was not modified.

## Global

| Metric | v1.1 | v1.2 | Δ |
|---|---:|---:|---:|
| Atoms total | 61 | 61 | 0 |
| Atoms ACTIVE | 60 | 60 | 0 |
| Atoms EXCLUDED | 1 | 1 | 0 |
| NORMATIVE | 46 | 55 | **+9** |
| WEAK_EVIDENCE | 14 | 5 | **-9** |
| Coverage score | 0.767 | **0.917** | **+0.150** |
| Bucket | YELLOW | **GREEN** | flip |

Coverage = NORMATIVE / (NORMATIVE + WEAK_EVIDENCE) across ACTIVE atoms. F12.04 (EXCLUDED via OOS-001) is omitted from the denominator.

## Per-family

| Family | v1.1 coverage | v1.2 coverage | v1.1 bucket | v1.2 bucket | Change |
|---|---:|---:|---|---|---|
| F01 | 0.833 (5N/1W) | **1.000** (6N/0W) | YELLOW | GREEN | flip up |
| F02 | 1.000 | 1.000 | GREEN | GREEN | — |
| F03 | 0.750 (3N/1W) | **1.000** (4N/0W) | YELLOW | GREEN | flip up |
| F04 | 0.250 (1N/3W) | 0.250 (1N/3W) | RED | RED | unchanged |
| F05 | 0.750 (3N/1W) | 0.750 (3N/1W) | YELLOW | YELLOW | — |
| F06 | 1.000 | 1.000 | GREEN | GREEN | — |
| F07 | 0.250 (1N/3W) | **0.750** (3N/1W) | RED | YELLOW | flip up |
| F08 | 0.200 (1N/4W) | **1.000** (5N/0W) | RED | GREEN | flip up (two-level) |
| F09 | 0.800 (4N/1W) | **1.000** (5N/0W) | YELLOW | GREEN | flip up |
| F10 | 1.000 | 1.000 | GREEN | GREEN | — |
| F11 | 1.000 | 1.000 | GREEN | GREEN | — |
| F12 | 1.000 (7N/0W, 1 EXCLUDED) | 1.000 | GREEN | GREEN | — |

Five families flipped upward. Zero regressed. F04 stayed RED.

## Bucket distribution

| Bucket | v1.1 | v1.2 | Δ |
|---|---:|---:|---:|
| GREEN (≥0.90) | 5 | **9** | +4 |
| YELLOW (0.70–0.89) | 4 | **2** | −2 |
| RED (<0.70) | 3 | **1** | −2 |

## Remaining WEAK atoms (5)

| Atom | Family | Claim | Blocker |
|---|---|---|---|
| F04.02 | F04 | Context MUST carry attribution | B3 context-assembly ADR |
| F04.03 | F04 | No private unattributed substitute context | B3 context-assembly ADR |
| F04.04 | F04 | Context assembly MUST be idempotent | B3 (SRC-ADR-005 supplementary; replay determinism is adjacent, not direct) |
| F05.04 | F05 | L3 MUST dispatch each plan step to L2 | B6 L3 orchestration charter ADR |
| F07.03 | F07 | Unrecoverable failures MUST surface to L3 | Normative escalation-target ADR (SRC-ADR-001 is invalid_for_normative_use=True) |

## Source contributions (F2)

| Source | Atoms upgraded NORMATIVE | Families affected |
|---|---:|---|
| SRC-ADR-002 (HEALER_RETRY) | 2 | F07 |
| SRC-ADR-003 (eval_pipeline_acceptance) | 5 | F08, F09 |
| SRC-ADR-004 (L0_DECOMPOSITION) | 2 | F01, F03 |
| SRC-ADR-005 (REPLAY_DETERMINISM) | 0 (supplementary on F04.04) | F04 |
| SRC-ADR-006 (AUTHORITY_HIERARCHY) | 0 (archive only) | — |
| SRC-ADR-001 (healing_dispatch_routing_adr) | 0 (ADVISORY, invalid_for_normative_use) | — |

## Rank-floor check

Every NORMATIVE upgrade cites ≥1 ARCHITECTURAL-rank source in addition to SRC-INT-003:

| Atom | Authority binding | Lowest rank |
|---|---|---:|
| F01.06 | [SRC-INT-003, SRC-ADR-004] | 4 ✅ |
| F03.04 | [SRC-INT-003, SRC-ADR-004] | 4 ✅ |
| F07.01 | [SRC-INT-003, SRC-ADR-002] | 4 ✅ |
| F07.02 | [SRC-INT-003, SRC-ADR-002] | 4 ✅ |
| F08.01 | [SRC-INT-003, SRC-ADR-003] | 4 ✅ |
| F08.03 | [SRC-INT-003, SRC-ADR-003] | 4 ✅ |
| F08.04 | [SRC-INT-003, SRC-ADR-003] | 4 ✅ |
| F08.05 | [SRC-INT-003, SRC-ADR-003] | 4 ✅ |
| F09.05 | [SRC-INT-003, SRC-ADR-003] | 4 ✅ |

## Edge evidence (26 total)

| Evidence class | Count |
|---|---:|
| NORMATIVE | 18 |
| WEAK_EVIDENCE | 8 |
| **Total** | **26** |

### Weak edges (8) — full enumeration with endpoint evidence

| Edge ID | Kind | Source atom | Source evidence | Target atom | Target evidence |
|---|---|---|---|---|---|
| INT-F02.01-F01.05-01 | DEPENDS_ON | F02.01 | NORMATIVE | F01.05 | NORMATIVE |
| INT-F05.04-F06.01-01 | REQUIRES | F05.04 | **WEAK_EVIDENCE** | F06.01 | NORMATIVE |
| INT-F07.03-F02.01-01 | CONDITIONAL_ON | F07.03 | **WEAK_EVIDENCE** | F02.01 | NORMATIVE |
| INT-F07.03-F05.01-01 | REQUIRES | F07.03 | **WEAK_EVIDENCE** | F05.01 | NORMATIVE |
| INT-F08.04-F09.01-01 | REQUIRES | F08.04 | NORMATIVE | F09.01 | NORMATIVE |
| INT-F09.05-F08.04-01 | REQUIRES | F09.05 | NORMATIVE | F08.04 | NORMATIVE |
| INT-F12.05-F02.01-01 | DEPENDS_ON | F12.05 | NORMATIVE | F02.01 | NORMATIVE |
| INT-F12.08-F08.03-01 | DEPENDS_ON | F12.08 | NORMATIVE | F08.03 | NORMATIVE |

### Breakdown by endpoint profile

- **5 of 8** weak edges have **both endpoints NORMATIVE**: F02.01→F01.05, F08.04→F09.01, F09.05→F08.04, F12.05→F02.01, F12.08→F08.03. These are the strongest candidates for a future edge-evidence upgrade pass (SRC-ADR-003 in the registry already supports three of them).
- **3 of 8** weak edges have **at least one WEAK atom endpoint**: F05.04→F06.01 (F05.04 WEAK), F07.03→F02.01 (F07.03 WEAK), F07.03→F05.01 (F07.03 WEAK). Edge upgrades for these three are blocked until the corresponding atom closes (B6 for F05.04, normative escalation-target ADR for F07.03).

F2 proposed no edge patches; v1.2 inherits all 26 edges from v1.1 unchanged. Follow-up logged as D-v12-01 in `hitl_decision_ledger.md`.
