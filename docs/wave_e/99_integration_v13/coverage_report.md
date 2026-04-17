# v1.3 Coverage Report — Delta vs v1.2

All counts recounted directly from `canonical/*.yaml`.

## Global

| Metric | v1.2 | v1.3 | Δ |
|---|---:|---:|---:|
| Atoms total | 61 | 61 | 0 |
| Atoms ACTIVE | 60 | 60 | 0 |
| Atoms EXCLUDED | 1 | 1 | 0 |
| NORMATIVE | 55 | **60** | **+5** |
| WEAK_EVIDENCE | 5 | **0** | **-5** |
| Coverage score | 0.917 | **1.000** | **+0.083** |
| Bucket | GREEN | GREEN | — (but perfect) |
| Sources | 12 | 15 | +3 |

Coverage = NORMATIVE / (NORMATIVE + WEAK_EVIDENCE) across ACTIVE atoms.
F12.06 (EXCLUDED) is omitted from the denominator.

## Per-family

| Family | v1.2 coverage | v1.3 coverage | v1.2 bucket | v1.3 bucket | Change |
|---|---:|---:|---|---|---|
| F01 | 1.000 | 1.000 | GREEN | GREEN | — |
| F02 | 1.000 | 1.000 | GREEN | GREEN | — |
| F03 | 1.000 | 1.000 | GREEN | GREEN | — |
| F04 | 0.250 (1N/3W) | **1.000** (4N/0W) | RED | **GREEN** | **two-level flip** |
| F05 | 0.750 (3N/1W) | **1.000** (4N/0W) | YELLOW | **GREEN** | flip up |
| F06 | 1.000 | 1.000 | GREEN | GREEN | — |
| F07 | 0.750 (3N/1W) | **1.000** (4N/0W) | YELLOW | **GREEN** | flip up |
| F08 | 1.000 | 1.000 | GREEN | GREEN | — |
| F09 | 1.000 | 1.000 | GREEN | GREEN | — |
| F10 | 1.000 | 1.000 | GREEN | GREEN | — |
| F11 | 1.000 | 1.000 | GREEN | GREEN | — |
| F12 | 1.000 | 1.000 | GREEN | GREEN | — |

Three families flipped upward (F04 two buckets, F05 one, F07 one). Zero regressed.

## Bucket distribution

| Bucket | v1.2 | v1.3 | Δ |
|---|---:|---:|---:|
| GREEN (≥0.90) | 9 | **12** | +3 |
| YELLOW | 2 | **0** | −2 |
| RED | 1 | **0** | −1 |

## Remaining WEAK atoms (0)

All previously-weak atoms closed.

| Atom | Was | Now | Source that closed it |
|---|---|---|---|
| F04.02 | WEAK | NORMATIVE | SRC-ADR-007 (CTX-I1) |
| F04.03 | WEAK | NORMATIVE | SRC-ADR-007 (CTX-I2) |
| F04.04 | WEAK | NORMATIVE | SRC-ADR-007 (CTX-I3) + SRC-ADR-005 (supplementary) |
| F05.04 | WEAK | NORMATIVE | SRC-ADR-008 (L3-I1 step 2) |
| F07.03 | WEAK | NORMATIVE | SRC-ADR-009 (ESC-I1) + SRC-ADR-008 (L3-I3) |

## Source contributions (F3)

| Source | Atoms upgraded NORMATIVE | Families affected |
|---|---:|---|
| SRC-ADR-007 (ADR-CTX-001) | 3 (F04.02, F04.03, F04.04) | F04 |
| SRC-ADR-008 (ADR-L3-001) | 2 (F05.04, F07.03 receiving half) | F05, F07 |
| SRC-ADR-009 (ADR-ESC-001) | 1 (F07.03 emitting half) | F07 |

## Rank-floor check (new bindings only)

Every v1.3 NORMATIVE upgrade cites ≥1 ARCHITECTURAL-rank source in addition to SRC-INT-003:

| Atom | Authority binding | Lowest rank |
|---|---|---:|
| F04.02 | [SRC-INT-003, SRC-ADR-007] | 4 ✅ |
| F04.03 | [SRC-INT-003, SRC-ADR-007] | 4 ✅ |
| F04.04 | [SRC-INT-003, SRC-ADR-005, SRC-ADR-007] | 4 ✅ |
| F05.04 | [SRC-INT-003, SRC-ADR-008] | 4 ✅ |
| F07.03 | [SRC-INT-003, SRC-ADR-008, SRC-ADR-009] | 4 ✅ |

## Edge evidence (unchanged)

| Evidence class | Count |
|---|---:|
| NORMATIVE | 18 |
| WEAK_EVIDENCE | 8 |
| **Total** | **26** |

The 8 WEAK edges are unchanged from v1.2. All 8 now have **both endpoints NORMATIVE** in v1.3 (vs 5/8 in v1.2), because the 3 edges that previously had a WEAK atom endpoint (INT-F05.04-F06.01-01, INT-F07.03-F02.01-01, INT-F07.03-F05.01-01) now have their source atom upgraded.

### v1.3 weak edges — updated endpoint profile

| Edge ID | Kind | Source | Target | F4 eligibility |
|---|---|---|---|---|
| INT-F02.01-F01.05-01 | DEPENDS_ON | F02.01 NORMATIVE | F01.05 NORMATIVE | ✅ eligible |
| INT-F05.04-F06.01-01 | REQUIRES | F05.04 **now NORMATIVE** | F06.01 NORMATIVE | ✅ eligible (newly) |
| INT-F07.03-F02.01-01 | CONDITIONAL_ON | F07.03 **now NORMATIVE** | F02.01 NORMATIVE | ✅ eligible (newly) |
| INT-F07.03-F05.01-01 | REQUIRES | F07.03 **now NORMATIVE** | F05.01 NORMATIVE | ✅ eligible (newly) |
| INT-F08.04-F09.01-01 | REQUIRES | F08.04 NORMATIVE | F09.01 NORMATIVE | ✅ eligible |
| INT-F09.05-F08.04-01 | REQUIRES | F09.05 NORMATIVE | F08.04 NORMATIVE | ✅ eligible |
| INT-F12.05-F02.01-01 | DEPENDS_ON | F12.05 NORMATIVE | F02.01 NORMATIVE | ✅ eligible |
| INT-F12.08-F08.03-01 | DEPENDS_ON | F12.08 NORMATIVE | F08.03 NORMATIVE | ✅ eligible |

F3 explicitly declined edge patches; Wave F4 produces the targeted upgrade proposal.
