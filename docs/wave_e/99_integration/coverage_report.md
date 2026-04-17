# Wave E1 Integration — Coverage Report

## Global Coverage

- **Atoms counted:** 58 (ACTIVE only; 1 EXCLUDED not counted per rubric).
- **NORMATIVE with binding:** 43
- **WEAK_EVIDENCE:** 15
- **UNRESOLVED:** 0
- **Global coverage_score:** `43 / (43 + 15 + 0) = 0.741` → **RED** (threshold: ≥0.75 yellow, ≥0.90 green).

The global score is NOT rounded up. Per contract rule: "if blockers remain, coverage_score must be reported and must not be rounded up."

## Per-Family Coverage

| Family | Atoms | Norm | Weak | Score | Bucket | Note |
|---|---:|---:|---:|---:|---|---|
| F01 Request Intake | 6 | 5 | 1 | 0.83 | 🟡 YELLOW | Reason-code atom weak |
| F02 L1 Reasoning | 5 | 5 | 0 | 1.00 | 🟢 GREEN | Fully normative |
| F03 L0 Route | 4 | 3 | 1 | 0.75 | 🟡 YELLOW | One-route-per-step weak |
| F04 Context Assembly | 4 | 1 | 3 | 0.25 | 🔴 RED | Idempotence/attribution unsourced |
| F05 L3 Orchestration | 4 | 3 | 1 | 0.75 | 🟡 YELLOW | L3-dispatch weak |
| F06 L2 Task Execution | 5 | 5 | 0 | 1.00 | 🟢 GREEN | Fully normative |
| F07 L2 Heal/Retry | 4 | 1 | 3 | 0.25 | 🔴 RED | Bounded retry unsourced |
| F08 Exit Spine | 5 | 1 | 4 | 0.20 | 🔴 RED | SRC-ADR-EXIT missing |
| F09 Write Gate | 5 | 4 | 1 | 0.80 | 🟡 YELLOW | F09.05 inherits F08 weakness |
| F10 L4 State | 4 | 4 | 0 | 1.00 | 🟢 GREEN | Fully normative |
| F11 L5 Policy | 7 | 7 | 0 | 1.00 | 🟢 GREEN | Fully normative, largest family |
| F12 L6 Learning | 5 | 4 | 1 | 0.80 | 🟡 YELLOW | F12.05 future-run consumption weak |

### Bucket Distribution

- 🟢 **GREEN (4):** F02, F06, F10, F11
- 🟡 **YELLOW (5):** F01, F03, F05, F09, F12
- 🔴 **RED (3):** F04, F07, F08

## Edge Evidence Distribution

- **Edges total:** 23 (all ACTIVE)
- **NORMATIVE edges:** 15
- **WEAK_EVIDENCE edges:** 8 (all in recovery chain, exit spine path, or F04 isolation area)

## What Drives the RED Score

The three RED families share a root cause: **absence of dedicated ARCHITECTURAL-rank sources** at the level required by the schema's NORMATIVE floor.

1. **F04 Context** — no source for idempotence or attribution requirements. The E0 schema governing-semantics (SRC-INT-003) talks about L1/L0/L4/L5/L6/WG but not context grounding specifically. Needs an ADR.
2. **F07 Heal/Retry** — no source for bounded-retry or escalation semantics. Operational invariant without canonical policy.
3. **F08 Exit Spine** — concept inferred from F08's intent but not stated in any rank ≤ 4 source. Needs an ADR or rule.

## Recovery Trajectory

To reach GREEN globally (≥0.90, zero weak, zero unresolved), the following work is required:

| Gap | Action | Owner | Effort |
|---|---|---|---|
| F04 idempotence source | Author ADR or rule binding F04.04 | Wave F+ | Low |
| F04 attribution source | Author ADR or rule binding F04.02, F04.03 | Wave F+ | Low |
| F07 bounded retry source | Author operational rule with rank ≤ ARCHITECTURAL citation | Wave F | Medium |
| F08 exit spine source | Author dedicated ADR (the "SRC-ADR-EXIT" that doesn't yet exist) | Wave F+ | Medium-High |
| F12.05 consumption mechanism | Specify the L6→future-L1 consumption protocol | Wave F+ | Medium |
| F03.04 one-route-per-step | Tighten citation | Wave F | Low |
| F05.04 L3 dispatch | Tighten citation | Wave F | Low |
| F01.06 structured reason code | ADR or rule | Wave F | Low |

If all nine gaps close and no new WEAK atoms are introduced, projected global score:
- 58 NORMATIVE / (58 + 0 + 0) = **1.00** GREEN.

## Unresolved / Excluded Counts

- **UNRESOLVED:** 0 (all E1b UNRESOLVED atoms resolved by E1c patches).
- **EXCLUDED:** 1 (F12.06, references OOS-001).
- **DEPRECATED, SUPERSEDED:** 0.

## Exclusion Distribution

| OOS | Reason | Family | Note |
|---|---|---|---|
| OOS-001 | OUT_OF_CHARTER | F12, F03 | L6 → L0 current-run bias |
| OOS-002 | OUT_OF_CHARTER | F07, F12 | L6 → L2 heal/retry current-run |
| OOS-003 | NOT_YET_DECIDED | F04 | C0 as separate owning_layer (has revisit_trigger) |

## Coverage Report Summary Line

**E1 integration closes at 0.74 global (RED) with 4 green / 5 yellow / 3 red families, 58 active + 1 excluded atom, 23 active edges, and 3 first-class exclusions. Schema-valid and publishable as canonical v1.**
