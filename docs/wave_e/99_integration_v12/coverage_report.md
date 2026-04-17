# v1.2 Coverage Report — Delta vs v1.1

## Global

| Metric | v1.1 | v1.2 | Δ |
|---|---:|---:|---:|
| Atoms total | 61 | 61 | 0 |
| Atoms ACTIVE | 60 | 60 | 0 |
| Atoms EXCLUDED | 1 | 1 | 0 |
| NORMATIVE | 46 | 55 | **+9** |
| WEAK_EVIDENCE | 14 | 5 | **-9** |
| Coverage score | 0.767 | **0.917** | **+0.150** |
| Bucket | YELLOW | **GREEN** | **flip** |

Coverage = NORMATIVE / (NORMATIVE + WEAK_EVIDENCE) across all ACTIVE atoms. Excludes the one EXCLUDED atom (F12.04 via OOS-001).

## Per-family

| Family | v1.1 coverage | v1.2 coverage | v1.1 bucket | v1.2 bucket | Change |
|---|---:|---:|---|---|---|
| F01 | 0.833 (5N/1W) | **1.000** (6N/0W) | YELLOW | GREEN | **flip up** |
| F02 | 1.000 | 1.000 | GREEN | GREEN | — |
| F03 | 0.750 (3N/1W) | **1.000** (4N/0W) | YELLOW | GREEN | **flip up** |
| F04 | 0.250 (1N/3W) | 0.250 (1N/3W) | RED | RED | **unchanged** |
| F05 | 0.750 (3N/1W) | 0.750 (3N/1W) | YELLOW | YELLOW | — |
| F06 | 1.000 | 1.000 | GREEN | GREEN | — |
| F07 | 0.250 (1N/3W) | **0.750** (3N/1W) | RED | YELLOW | **flip up** |
| F08 | 0.200 (1N/4W) | **1.000** (5N/0W) | RED | GREEN | **flip up (two-level)** |
| F09 | 0.800 (4N/1W) | **1.000** (5N/0W) | YELLOW | GREEN | **flip up** |
| F10 | 1.000 | 1.000 | GREEN | GREEN | — |
| F11 | 1.000 | 1.000 | GREEN | GREEN | — |
| F12 | 1.000 | 1.000 | GREEN | GREEN | — |

Five families flipped upward. Zero families regressed. F04 alone stayed RED.

## Bucket distribution

| Bucket | v1.1 count | v1.2 count | Δ |
|---|---:|---:|---:|
| GREEN (≥0.90) | 5 | **9** | +4 |
| YELLOW (0.70–0.89) | 4 | **2** | -2 |
| RED (<0.70) | 3 | **1** | -2 |

## Remaining WEAK atoms (5)

| Atom | Family | Claim | Blocker |
|---|---|---|---|
| F04.02 | F04 | Context MUST carry attribution | B3 context-assembly ADR |
| F04.03 | F04 | No private unattributed substitute context | B3 context-assembly ADR |
| F04.04 | F04 | Context assembly MUST be idempotent | B3 context-assembly ADR (SRC-ADR-005 is adjacent, not direct) |
| F05.04 | F05 | L3 MUST dispatch each plan step to L2 | B6 L3 orchestration charter ADR |
| F07.03 | F07 | Unrecoverable failures MUST surface to L3 | Normative escalation-target ADR (SRC-ADR-001 exists but is invalid_for_normative_use=True) |

## Source contributions

| Source | Atoms upgraded | Families affected |
|---|---:|---|
| SRC-ADR-002 (HEALER_RETRY) | 2 | F07 |
| SRC-ADR-003 (eval_pipeline_acceptance) | 5 | F08, F09 |
| SRC-ADR-004 (L0_DECOMPOSITION) | 2 | F01, F03 |
| SRC-ADR-005 (REPLAY_DETERMINISM) | 0 (supplementary only) | F04 |
| SRC-ADR-006 (AUTHORITY_HIERARCHY) | 0 (archive only) | — |
| SRC-ADR-001 (healing_dispatch_routing_adr) | 0 (ADVISORY-only) | — |

SRC-ADR-003 is the single highest-value addition: four F08 atoms and one F09 atom upgraded from a single source registration.

## Rank-floor check

Every NORMATIVE upgrade cites at least one ≤ARCHITECTURAL-rank source in addition to SRC-INT-003:

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

All 9 upgrades pass.

## Interaction edge evidence (unchanged)

Five edges retain `evidence_class: WEAK_EVIDENCE` in v1.2 despite their endpoints upgrading to NORMATIVE atoms. F2 proposed no edge patches so v1.2 inherits them:

- `INT-F02.01-F01.05-01` (DEPENDS_ON)
- `INT-F05.04-F06.01-01` (REQUIRES)
- `INT-F07.03-F02.01-01` (CONDITIONAL_ON)
- `INT-F07.03-F05.01-01` (REQUIRES)
- `INT-F08.04-F09.01-01` (REQUIRES)
- `INT-F09.05-F08.04-01` (REQUIRES)
- `INT-F12.05-F02.01-01` (DEPENDS_ON)
- `INT-F12.08-F08.03-01` (DEPENDS_ON)

Logged as follow-up D-v12-01 in HITL ledger — candidate for a later targeted edge-evidence pass, not in F2's scope.
