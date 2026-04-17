# v1.4 HITL Decision Ledger

F4 integration pass. Records every non-trivial decision made while merging F4 onto v1.3.

## Carried forward

All prior HITL decisions from v1 / v1.1 / v1.2 / v1.3 remain binding. Specifically:

- HITL-INT-F07-AUTH (F07 authority_class CONSTITUTIONAL)
- HITL-INT-V11-001 (F12.05 memory-lifecycle upgrade)
- DEC-v12-01 through DEC-v12-05
- DEC-v13-01 (F04.02 claim verbatim)
- DEC-v13-02 (F04.04 supplementary binding retained)
- DEC-v13-03 (SRC-ADR-001 unbound)
- DEC-v13-04 (F3 no edge patches — closed in this pass)
- DEC-v13-05 (OOS-003 revisit-trigger satisfied — closed in this pass)
- DEC-v13-06 (no DRAFT→ACTIVE)
- DEC-v13-07 (no B7 closure)

F4 introduced no changes that reopened any earlier decision.

## New decisions in v1.4

### DEC-v14-01 — Accept all 8 edge evidence upgrades

**Question:** F4 proposes 8 WEAK → NORMATIVE edge patches. Should the integration pass accept each?

**Analysis:** Per integration rules 4–5, each edge's F4 rationale was re-validated independently against the sources it cites. The direct-support test was re-run on every edge (see `merge_conflicts_register.md` §"Over-eagerness check" and F4's `weak_edge_upgrade_matrix.md`). In every case the cited source(s) directly state the edge claim, not merely support the endpoint atoms.

Conservative re-check on borderline cases:
- INT-F02.01-F01.05-01 — F01.05's normative claim *is* the DEPENDS_ON relation. Direct.
- INT-F05.04-F06.01-01 — SRC-ADR-008 L3-I1 step 2 is verbatim "L3 MUST dispatch each plan step to L2". Direct.
- INT-F07.03-F02.01-01 / -F05.01-01 — SRC-ADR-009 ESC-I1 names L3 as target; SRC-ADR-008 L3-I3 emits re-plan to L1. Together they are the full L2→L3→L1 contract. Direct.
- INT-F08.04-F09.01-01 / INT-F09.05-F08.04-01 — both edges are restatements of the source-atom claim itself plus SRC-ADR-003's GovernedHandoffAgent / evaluate_sealed() binding. Direct.
- INT-F12.05-F02.01-01 — F12.05's claim literally names L1 consumption; SRC-INT-004 memory lifecycle + SRC-RULE-001 §17 are normative. Direct.
- INT-F12.08-F08.03-01 — F12.08's claim literally names the F08 spine outcome; SRC-ADR-003 + SRC-INT-004 cover the recording and write-back. Direct.

**Decision:** Accept all 8 edge patches.

**Rationale:** Bar met: each edge has a direct-statement source. No endpoint-only upgrades.

### DEC-v14-02 — Accept OOS-003 SUPERSEDED transition

**Question:** F4 proposes revising OOS-003 from `reason: NOT_YET_DECIDED` to `reason: SUPERSEDED`, citing SRC-ADR-007 as supersession source. Accept?

**Analysis:** Three independent checks:

1. **Schema validity.** `SUPERSEDED` is a member of the `Exclusion.reason` enum. The revised record retains all required fields. No schema drift.
2. **Supersession rationale.** OOS-003's original revisit trigger was "future wave surfaces a concrete operational constraint that L1 cannot satisfy for context grounding." SRC-ADR-007 (ADR-CTX-001) declares three invariants that L1 *can* and *must* satisfy, with real implementation grounding in `agentic_core/L1_cognition/reasoning/context_assembler.py`. The rationale for holding OOS-003 open has been resolved in the negative direction — no C0 layer is needed. This is a genuine supersession, not a deferral or re-framing.
3. **Safety.** Per the cross-enum rule "An Exclusion MUST NOT be referenced by any ACTIVE atom as authority", 0 ACTIVE atoms cite OOS-003 in `authority_binding`. F12.06 (EXCLUDED) references OOS-001 only, not OOS-003. The revision has no downstream impact.

**Decision:** Accept the revision.

**Rationale:** All three checks pass. `exclusion_review_log.md` contains the full supersession analysis. The revision preserves history by keeping `scope_statement` and related_atoms intact.

### DEC-v14-03 — No atom, family, or source changes accepted

**Question:** F4's `atoms.yaml`, `families.yaml`, and `sources.yaml` proposal files are explicitly empty. Confirm v1.4 introduces no such changes.

**Analysis:** The integration rule 8 forbids fabrication. F4 produced no atom, family, or source deltas, and the pass must not introduce any of its own.

**Decision:** v1.4 carries forward all 12 families, 61 atoms, and 15 sources from v1.3 verbatim.

**Rationale:** Bounded-scope discipline.

### DEC-v14-04 — No B7 closure as byproduct

**Question:** Do the 8 edge upgrades close any of the 6 deferred B7 interaction candidates?

**Analysis:** B7 candidates require new edges or new atoms. F4's edge patches modify only `evidence_class` and `authority_binding` on existing edges — none introduces a new edge or promotes a candidate-interaction to first-class. F4's own `cleanup_decision_log.md` DEC-F4-03 reached the same conclusion.

**Decision:** B7 candidates remain deferred.

**Rationale:** F4 scope excludes B7. Future wave with explicit HITL approval is required.

### DEC-v14-05 — Scorecard recomputation

**Question:** Do any per-family scorecards need new counts?

**Analysis:** Per-family atom evidence distribution did not change from v1.3 (all 12 families were already at N=all, W=0). Edge counts are tracked globally, not inside per-family scorecards in this lineage. The only per-scorecard change is `produced_at_wave: v1.3 → v1.4`.

**Decision:** Update `produced_at_wave` on all 12 scorecards. No other fields touched.

**Rationale:** Honest reporting: the wave changed; nothing else per-family did.

## Follow-ups after F4

| ID | Topic | Status |
|---|---|---|
| D-v12-01 | Weak-edge upgrade pass | **CLOSED** by this integration pass. |
| DEC-v13-05 | OOS-003 state transition | **CLOSED** by this integration pass. |
| B7 | 6 deferred interaction candidates | **Open.** Requires future wave with explicit HITL approval. |

No silent drops. No new blockers introduced.
