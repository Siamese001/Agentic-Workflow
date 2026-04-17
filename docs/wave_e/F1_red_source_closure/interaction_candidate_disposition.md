# Wave F1 — Interaction Candidate Disposition

Evaluation of each deferred candidate from `docs/wave_e/E1d_interactions/interaction_candidates.md` (C1..C9) against F1's bounded scope.

---

## C1 — F01.06 reason code feeds L6 learning
- **Evaluation:** Would require a new F12 atom "L6 MUST catalog admission rejections."
- **Source availability:** AGENTS.md Memory Lifecycle does mandate writing significant outcomes to memory. Admission rejection could qualify as a "significant outcome" worth recording.
- **Disposition:** **DEFERRED.**
- **Why:** Arguably closable, but the additional atom would be one more L6 observation atom and the claim is narrower than F12.08 which F1 already authors. Integration of C1 as a further refinement of F12.08 is better deferred to a future wave when admission telemetry design is concrete.

## C2 — F04 context bound by L5 policy
- **Evaluation:** Would require a new F11 atom "L5 policies MUST bind context assembly surfaces."
- **Source availability:** No rule, ADR, or governing-semantics statement binds context to policy.
- **Disposition:** **DEFERRED.**
- **Why:** No real source exists. Adding a WEAK_EVIDENCE atom under F11 would degrade F11 from 1.00 GREEN.

## C3 — F07 retry budget set by L5
- **Evaluation:** Would require a new F11 atom "L5 MUST set retry budgets for L2 heal/retry."
- **Source availability:** Constitutional §14 (subprocess timeout) is the nearest precedent but does not cover retry loops.
- **Disposition:** **DEFERRED.** (See source_gap_closure_log.md §F07.02 for the full rejection rationale.)
- **Why:** Adding F11.08 as WEAK_EVIDENCE would degrade F11 from 1.00 GREEN to 0.875 YELLOW without materially strengthening F07.02. Net loss.

## C4 — F04 attribution feeds audit trail
- **Evaluation:** Would require an audit-trail atom somewhere (likely a new F08 or F10 atom).
- **Source availability:** No audit-trail design exists in the repo.
- **Disposition:** **DEFERRED.**
- **Why:** Downstream atoms don't exist yet; speculative to emit edges.

## C5 — F08 outcome observed for future learning
- **Evaluation:** Would require a new F12 atom "L6 MUST observe F08 exit outcomes for memory."
- **Source availability:** AGENTS.md Memory Lifecycle mandates writing outcomes to memory at significant points.
- **Disposition:** **CLOSED.**
- **How:** F1 authored **F12.08** + edge **INT-F12.08-F08.03-01 DEPENDS_ON**. The DEPENDS_ON edge is WEAK_EVIDENCE (inherits F08.03's weakness) but the F12.08 claim itself is NORMATIVE via memory-lifecycle sources.

## C6 — F03 route rationale feeds F04 context
- **Evaluation:** Would require a new F03 or F04 atom for route-rationale capture.
- **Source availability:** No rule mandates route-rationale persistence.
- **Disposition:** **DEFERRED.**
- **Why:** Speculative. Route attribution could be derived from the ADG / observability stack but there's no canonical design yet.

## C7 — F02.04 implies executor (no clean target)
- **Disposition:** **NO ACTION.** F02.04 is correctly self-contained. No edge necessary. E1d's analysis stands.

## C8 — F07.03 "surface to L3" vs F05.02 "L3 MUST NOT plan"
- **Disposition:** **NO ACTION.** Not a real conflict. F07.03 routes the re-plan request; L1 actually plans (F02.01). Existing `INT-F07.03-F02.01-01 CONDITIONAL_ON` edge already captures this.

## C9 — CO_REQUIRES BIDIRECTIONAL for F09.04/F11.04
- **Evaluation:** Promote the existing `INT-F09.04-F11.04-01 REQUIRES` to CO_REQUIRES BIDIRECTIONAL.
- **Disposition:** **DEFERRED.**
- **Why:** Would require patching an existing canonical edge in a Wave F sub-wave. The directed REQUIRES relationship is sufficient; promotion to CO_REQUIRES adds semantic precision but no behavioral change. Defer to a later cleanup wave.

---

## Disposition Summary

| Candidate | Disposition |
|---|---|
| C1 — admission reason → L6 | DEFERRED |
| C2 — F04 context ← L5 policy | DEFERRED (no source) |
| C3 — F07 retry budget ← L5 | DEFERRED (net-negative coverage) |
| C4 — F04 attribution → audit | DEFERRED (no downstream atom) |
| **C5** — F08 outcome → L6 | **CLOSED via F12.08** |
| C6 — F03 rationale → F04 | DEFERRED |
| C7 — F02.04 no-target | NO ACTION (E1d stands) |
| C8 — F07.03 / F05.02 non-conflict | NO ACTION (E1d stands) |
| C9 — CO_REQUIRES upgrade | DEFERRED |

**1 of 9 candidates closed in F1.** Remaining 8 await real sources or downstream atom designs.
