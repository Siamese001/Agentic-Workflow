# Wave F2 - Interaction Candidate Revisit Log

Re-evaluation of each deferred candidate (C1, C2, C3, C4, C6, C9) from `E1d_interactions/interaction_candidates.md` in light of F2's new sources. C5 was already closed in F1 via F12.08.

---

## C1 - F01.06 rejection reason -> L6 learning catalog

- **Revisit status:** NOT NEWLY SUPPORTABLE.
- **What F2 changed:** F01.06 upgraded to NORMATIVE via SRC-ADR-004. The rejection reason is now structurally attested.
- **Why still deferred:** adding an L6 atom "L6 MUST catalog admission rejections" would require a new F12.09 atom. SRC-ADR-003 and SRC-INT-004 (memory lifecycle) do support the general L6-observes-significant-events pattern, but the specific "catalog admission rejections" scope is narrower than F12.08's general outcome-recording. Redundant if F12.08 is read generously.
- **Action:** DEFERRED. Not required for F2's red-family closure.

---

## C2 - F04 context bound by L5 policy

- **Revisit status:** STILL UNSUPPORTABLE.
- **What F2 changed:** nothing relevant. F04 remains RED.
- **Why:** there is still no rule, ADR, or governing-semantics statement that binds context assembly to L5 policy. SRC-ADR-006 (AUTHORITY_HIERARCHY_INVARIANTS) does not mention context assembly at all.
- **Action:** DEFERRED. Cannot emit an F11-to-F04 edge when F04 itself has no NORMATIVE policy binding.

---

## C3 - F07 retry budget set by L5

- **Revisit status:** PARTIALLY supportable, but still declined.
- **What F2 changed:** F07.01 and F07.02 are now NORMATIVE via SRC-ADR-002. The retry budget values (max_attempts=3, strictness=[0.70, 0.85, 0.95], timeout=[30, 20, 10]) are now canonically registered.
- **Why declined:** the HEALER_RETRY spec presents these as **architectural constants** baked into the hardening specification, not **L5 policy** that L5 is authorized to mutate. SRC-ADR-001 (the F25-int ADR) says "Changing these values requires a new ADR revision" — i.e., they're owned by the architecture layer, not by L5 dynamic policy.
- **Possible minimal atom to add:** `F11.08 "L5 MUST bind retry-budget configuration to L2 heal/retry paths"` at WEAK_EVIDENCE. But this would degrade F11 from GREEN 1.00 to YELLOW 0.875 without clearly strengthening F07.
- **Action:** DEFERRED. Same rationale as F1.

---

## C4 - F04 attribution feeds audit trail

- **Revisit status:** STILL UNSUPPORTABLE.
- **Why:** F04.02 attribution remains WEAK. Even if F04.02 were NORMATIVE, the audit-trail surface (a hypothetical downstream F08 or F10 atom) doesn't exist. No canonical audit-trail spec in the repo.
- **Action:** DEFERRED.

---

## C6 - F03 route rationale -> F04 context

- **Revisit status:** STILL UNSUPPORTABLE.
- **What F2 changed:** F03.04 is now NORMATIVE (deterministic single-route-per-step). This strengthens the "route decision" end of the hypothetical edge, but the "context consumes rationale" end still has no atom.
- **Why:** no F04 atom captures "context consumes route rationale". Adding one speculatively would require a new claim with no source.
- **Action:** DEFERRED.

---

## C9 - CO_REQUIRES BIDIRECTIONAL for F09.04/F11.04

- **Revisit status:** STILL OUT OF F2 SCOPE.
- **Why:** this is an edge-kind upgrade on an existing canonical edge (`INT-F09.04-F11.04-01 REQUIRES`). F2's bounded scope is source authoring, not edge patching. Also, the existing directed REQUIRES captures the functional semantics already.
- **Action:** DEFERRED.

---

## Summary

| Candidate | F1 disposition | F2 disposition | Delta |
|---|---|---|---|
| C1 | DEFERRED | DEFERRED | no change |
| C2 | DEFERRED | DEFERRED | no change |
| C3 | DEFERRED | DEFERRED | no change |
| C4 | DEFERRED | DEFERRED | no change |
| C5 | **CLOSED (F1)** | (already closed) | — |
| C6 | DEFERRED | DEFERRED | no change |
| C7 | NO_ACTION | NO_ACTION | no change |
| C8 | NO_ACTION | NO_ACTION | no change |
| C9 | DEFERRED | DEFERRED | no change |

**Zero new candidates closed in F2.** The red-family closures raised confidence in adjacent atoms (F01.06, F03.04 became NORMATIVE) but none of those adjacencies converted a deferred candidate into a supportable one.

**Honest conclusion:** the remaining six deferred candidates need either new atoms (F04 / F11 additions) or new normative ADRs that F2 declined to fabricate. They are correctly deferred to a later wave.
