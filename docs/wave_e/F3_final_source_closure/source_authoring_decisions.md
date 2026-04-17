# Wave F3 — Source Authoring Decisions

Records the non-trivial decisions made while authoring the three F3 source artifacts.

## D-F3-01 — Three narrow ADRs vs one omnibus ADR

**Question:** Should F3 author a single omnibus "L3 and context" ADR or three narrow ADRs?

**Analysis:** The F3 contract says "prefer narrow, explicit docs over omnibus docs". The three concerns (context assembly, L3 charter, escalation target) have distinct authority surfaces, distinct layer owners, and distinct validation criteria. Merging them would create cross-concern coupling and make future revision harder.

**Decision:** Three narrow ADRs:
- `ADR-CTX-001` at `docs/architecture/context_assembly_adr.md` — SRC-ADR-007
- `ADR-L3-001` at `docs/architecture/l3_orchestration_charter_adr.md` — SRC-ADR-008
- `ADR-ESC-001` at `docs/architecture/unrecoverable_failure_escalation_adr.md` — SRC-ADR-009

## D-F3-02 — Revise ADR-F25-int vs author a new ADR for F07.03

**Question:** F07.03 needs a normative escalation-target source. Two options:
- (a) Revise `docs/architecture/healing_dispatch_routing_adr.md` (ADR-F25-int) to drop `invalid_for_normative_use=True`.
- (b) Author a new narrow ADR explicitly naming L3.

**Analysis of (a):** ADR-F25-int is explicitly framed as a **repo-internal** current-state architecture description, with `invalid_for_normative_use=True` deliberately set to prevent it from being used as target-state authority. Its `ESCALATED` tier routes to "HITL or deterministic abort", not to "L3 for re-planning". Revising the ADR to both drop the marker AND reframe the escalation target would contradict the original decision and would retroactively change the semantics of a released ADR. Unacceptable.

**Analysis of (b):** A new ADR can sit ABOVE the healing-tier decision (which is about *which tier heals*) and answer the higher-level question *what happens after all healing tiers fail unrecoverably*. This is a strictly different concern and does not conflict with ADR-F25-int.

**Decision:** Option (b). ADR-ESC-001 is new, narrow, and sits above ADR-F25-int in the escalation stack. ADR-F25-int retains its `invalid_for_normative_use=True` marker unchanged. SRC-ADR-001 remains ADVISORY in the canonical graph and is NOT added to F07.03's `authority_binding`.

## D-F3-03 — F04.04 supplementary binding retention

**Question:** F04.04 currently carries `[SRC-INT-003, SRC-ADR-005]`. After F3 registers SRC-ADR-007 as the direct normative support, should SRC-ADR-005 stay on the binding?

**Analysis:** Schema permits multi-source bindings. SRC-ADR-005 (replay-determinism) is adjacent context that still adds signal. Removing it would be revisionist; retaining it is additive.

**Decision:** F04.04 `authority_binding = [SRC-INT-003, SRC-ADR-005, SRC-ADR-007]`. SRC-ADR-007 is the primary normative source; SRC-ADR-005 is retained as adjacent support.

## D-F3-04 — Do not widen to B7 / interaction candidates

**Question:** Does authoring L3-I3 and ESC-I1 make any deferred interaction candidate (C1, C2, C3, C4, C6, C9) cleanly supportable?

**Analysis:**
- **C2** (F04 context bound by L5 policy): ADR-L3-001 §3.5 says L3 MUST consult the L5 policy envelope before dispatching, which binds dispatch to L5 policy — but it does NOT bind context ASSEMBLY to L5 policy. F04 is still not L5-bound.
- **C3** (F07 retry budget set by L5): ADR-L3-001 §3.3 binds retry bounds to the healer hardening spec, not to L5 dynamic policy. No change.
- **C1, C4, C6, C9:** none of the three new ADRs touches these.

**Decision:** No interaction candidate closes as a free byproduct. B7 stays deferred. F3 does not emit any edge patches.

## D-F3-05 — Do not close OOS-003 unilaterally

**Question:** ADR-CTX-001's §4 notes that OOS-003's revisit trigger is now satisfied. Should F3 mark OOS-003 as SUPERSEDED?

**Analysis:** An exclusion-state transition is a governance act independent of source authoring. The revisit trigger says "SHOULD be re-evaluated", not "MUST be auto-closed". Auto-closing an exclusion from a source-authoring wave would bypass the exclusion-review process.

**Decision:** F3 leaves OOS-003 ACTIVE and flags it for a later exclusion-review pass or integration-pass action. Proposals `exclusions.yaml` contains `exclusion_patches: []`.

## D-F3-06 — Do not patch edges

**Question:** SRC-ADR-007/008/009 could plausibly support several weak edges whose endpoints are now NORMATIVE. Should F3 patch them?

**Analysis:** F3's bounded scope explicitly excludes edge-evidence upgrades unless the new source "directly and unambiguously supports an existing weak edge as a free byproduct". Testing each weak edge against the new source text:

| Edge | New ADR support | Direct and unambiguous? |
|---|---|---|
| INT-F02.01-F01.05-01 | none | — |
| INT-F05.04-F06.01-01 | ADR-L3-001 dispatches from L3 to L2; F06 is L2 execution family. The edge REQUIRES relationship is implied but not explicit. | No |
| INT-F07.03-F02.01-01 | ADR-ESC-001 names L1 as the re-plan recipient; F02 is the L1 planning family. Plausible but edge's CONDITIONAL_ON wording needs its own citation. | No |
| INT-F07.03-F05.01-01 | ADR-L3-001 L3-I3 binds escalation to the L3 orchestration path; F05.01 is L3 orchestration family. Plausible. | No (still adjacent, not explicit on the REQUIRES claim) |
| INT-F08.04-F09.01-01 | none | — |
| INT-F09.05-F08.04-01 | none | — |
| INT-F12.05-F02.01-01 | none | — |
| INT-F12.08-F08.03-01 | none | — |

**Decision:** F3 emits no edge patches. The honest signal is that several edges are now upgrade-eligible in a later targeted edge pass, but none is a clean free byproduct. Follow-up D-v12-01 remains open.

## Summary

| Decision | Action |
|---|---|
| D-F3-01 | Three narrow ADRs at real repo paths. |
| D-F3-02 | New ADR-ESC-001; ADR-F25-int unchanged. |
| D-F3-03 | F04.04 binding kept with SRC-ADR-005 as adjacent + SRC-ADR-007 as primary. |
| D-F3-04 | B7 interaction candidates remain deferred. |
| D-F3-05 | OOS-003 left ACTIVE; revisit trigger flagged. |
| D-F3-06 | No edge patches. |
