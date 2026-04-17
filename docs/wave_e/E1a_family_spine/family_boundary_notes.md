# Wave E1a — Family Boundary Notes

**Scope:** Record the boundary decisions where two or more layers could plausibly own a family, and the provisional owning_layer chosen for DRAFT. E1c is responsible for confirming or overturning these during authority-scope review.

Every provisional choice below satisfies the schema validation rule "owning_layer MUST be exactly one value" without concealing the underlying ambiguity.

---

## F01 — Request Intake and Envelope Check

**Candidate layers:** L0 (boundary) vs. L5 (policy).
**Provisional choice:** L0.
**Why L0 is safest:** Intake is structurally the inbound boundary; rejecting a malformed request is a boundary action, not a policy authoring action. L5 binds F01 by edge: F01 REQUIRES F11 (policy preconditions must be satisfied).
**What would flip this:** If E1c determines that envelope checks are themselves policy-authored and policy-maintained (not just policy-consumed), F01 could move to L5. In that case F01 becomes a policy-enforcement surface rather than a boundary surface.
**Recommended E1b treatment:** Draft atoms for F01 citing L5 policy sources via authority_binding rather than co-ownership.

## F04 — Context Assembly and Grounding

**Candidate layers:** L1 vs. L3.
**Provisional choice:** L1.
**Why L1 is safest:** Context grounding is the input surface of reasoning. The context set determines what L1 can decompose. Placing the family with its principal consumer (L1) avoids treating context assembly as orchestration.
**What would flip this:** If grounding is implemented as an orchestrated pre-step rather than a reasoning-phase assembly, F04 could move to L3. The current governing semantics do not specify.
**Schema-drift note:** The seed title referred to this family as "C0". `C0` is NOT a value in the `owning_layer` enum, which accepts only L0..L6. The title has been normalized accordingly. See family_risk_flags.md for the associated risk flag.

## F08 — Runtime Exit Control and Evaluation Spine

**Candidate layers:** L5 (policy) vs. L3 (orchestration).
**Provisional choice:** L5.
**Why L5 is safest:** Exit control decides whether a result is acceptable, which is a policy judgment. The evaluation spine applies that policy; L3 cooperates by invocation but does not author the exit rules.
**What would flip this:** If the evaluation spine is a strictly orchestrator-owned runtime loop with policy only contributing predicates, F08 could move to L3.
**Recommended E1d treatment:** Emit explicit edges F08 REQUIRES F11 (policy binds exit) and F08 REQUIRES F09 (exit signals feed the write gate).

## F09 — Universal Write Gate

**Candidate layers:** L4 (durable state) vs. L5 (policy).
**Provisional choice:** L4.
**Why L4 is safest:** The gate is the sole write path INTO L4 durable state and is structurally co-located with the state it protects. L5 authors the policies the gate enforces but does not own the gate itself.
**What would flip this:** If the gate is architected as a policy-layer component that merely calls into L4, F09 could move to L5. The "sole durable write path" semantic argues against that interpretation.
**Recommended E1d treatment:** Edge F09 REQUIRES F11 (gate consults policy) and F10 REQUIRES F09 (state mutations go through the gate).

---

## Boundaries That Were NOT Ambiguous

For completeness, the following owning_layer assignments were not boundary-ambiguous and did not require a decision note:

- F02 (L1), F03 (L0), F05 (L3), F06 (L2), F07 (L2), F10 (L4), F11 (L5), F12 (L6) — each family's intent aligns to exactly one layer that both authors and enforces the normative claim.

## E1c Handoff

E1c authority-scope review should confirm or refine the four provisional choices above (F01, F04, F08, F09). Where E1c overturns a provisional choice, E1c MUST record the overturn in its own lane notes and notify the integration pass so the merged canonical record reflects the confirmed layer.
