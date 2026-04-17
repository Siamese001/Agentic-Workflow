# F1 Integration — Coverage Report (v1 → v1.1 delta)

## Global Coverage Delta

| Metric | v1 | v1.1 | Delta |
|---|---:|---:|---:|
| Atoms counted (excl. EXCLUDED) | 58 | 58 + 2 new = 60 | +2 |
| NORMATIVE with binding | 43 | 43 + 2 new + 1 patched = 45, but -1 patched-out-of-WEAK = net WEAK−1 | +2 |
| WEAK_EVIDENCE | 15 | 15 − 1 (F12.05 upgraded) = 13 | −2 net |
| UNRESOLVED | 0 | 0 | 0 |
| **Global coverage_score** | **0.741 RED** | **0.776 YELLOW** | **+0.035, bucket flip** |

Computation v1.1: `45 / (45 + 13 + 0) = 0.7759`. Reported as 0.776, not rounded up.

## Per-Family Delta

| Family | v1 Score | v1.1 Score | v1 Bucket | v1.1 Bucket | Changed? |
|---|---:|---:|---|---|:---:|
| F01 | 0.83 | 0.83 | 🟡 | 🟡 | no |
| F02 | 1.00 | 1.00 | 🟢 | 🟢 | edge-count only |
| F03 | 0.75 | 0.75 | 🟡 | 🟡 | no |
| F04 | 0.25 | 0.25 | 🔴 | 🔴 | no |
| F05 | 0.75 | 0.75 | 🟡 | 🟡 | no |
| F06 | 1.00 | 1.00 | 🟢 | 🟢 | no |
| F07 | 0.25 | 0.25 | 🔴 | 🔴 | no |
| F08 | 0.20 | 0.20 | 🔴 | 🔴 | edge-count only |
| F09 | 0.80 | 0.80 | 🟡 | 🟡 | no |
| F10 | 1.00 | 1.00 | 🟢 | 🟢 | no |
| F11 | 1.00 | 1.00 | 🟢 | 🟢 | no |
| **F12** | **0.80** | **1.00** | 🟡 | **🟢** | **YES** |

**Bucket distribution:**
- v1: 4 🟢 (F02, F06, F10, F11) / 5 🟡 (F01, F03, F05, F09, F12) / 3 🔴 (F04, F07, F08)
- v1.1: **5 🟢** (F02, F06, F10, F11, **F12**) / **4 🟡** (F01, F03, F05, F09) / 3 🔴 (F04, F07, F08)

## Edge Evidence Distribution

| Class | v1 | v1.1 | Delta |
|---|---:|---:|---:|
| NORMATIVE edges | 15 | 17 | +2 |
| WEAK_EVIDENCE edges | 8 | 9 | +1 |
| **Total ACTIVE edges** | **23** | **26** | **+3** |

## What Changed

### Material changes
- **F12 moved GREEN.** F12.05 upgraded WEAK → NORMATIVE; F12.07 + F12.08 added NORMATIVE. F12 is now the fifth green family, alongside F02, F06, F10, F11.
- **Global bucket flipped RED → YELLOW.** Score rose from 0.741 to 0.776 (honest, unrounded).
- **Three new edges** wire the memory-lifecycle consumption mechanism into F02 (target of the REQUIRES edge) and F08 (target of the DEPENDS_ON edge). The REFINES edge is internal to F12.
- **SRC-INT-004** added: `AGENTS.md#memory-lifecycle` anchor, GOVERNANCE rank 2.

### Non-material changes
- F02 and F08 scorecards show +1 edge each.
- F12 scorecard shows 8 atoms, 7 ACTIVE + 1 EXCLUDED, 7 edges.

### What did NOT change
- No family bucket transitioned except F12.
- F04, F07, F08 all remain RED with identical coverage scores. F1 correctly declined to fabricate sources.
- F01.06, F03.04, F05.04 remain WEAK. No sources available.
- Exclusions (OOS-001, OOS-002, OOS-003) unchanged.
- All non-F12 atoms unchanged.

## Projection Toward GREEN

To reach global GREEN (≥0.90, zero WEAK, zero UNRESOLVED) from v1.1's 0.776:

| Gap | Family | Wave F+ action | Effort |
|---|---|---|---|
| Exit-spine ADR | F08 | Author dedicated ADR (Blocker B1) | Medium-High |
| Bounded-retry rule | F07 | Author operational rule (Blocker B2) | Medium |
| Context-assembly ADR | F04 | Dedicated ADR covering attribution, idempotence, no-private-substitute (Blocker B3) | Medium |
| Structured reason-code | F01.06 | Trivial ADR (Blocker B4) | Low |
| One-route-per-step | F03.04 | Trivial ADR (Blocker B5) | Low |
| L3 dispatch | F05.04 | L3 orchestration charter (Blocker B6) | Medium |

Closing B1–B3 alone (3 RED families) would lift global coverage into projected green territory.

## Unresolved / Excluded

- **UNRESOLVED:** 0 (unchanged).
- **EXCLUDED:** 1 (F12.06, still referencing OOS-001).
- **DEPRECATED, SUPERSEDED:** 0.

## Coverage Summary Line

**v1.1 closes at 0.776 YELLOW (bucket flip from v1 RED) with 5 green / 4 yellow / 3 red families, 60 active + 1 excluded atom, 26 active edges, 6 sources, 3 exclusions. F12 is newly green. F04/F07/F08 remain RED.**
