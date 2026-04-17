# v1.2 HITL Decision Ledger

F2 integration pass. Records every non-trivial decision made while merging F2 onto v1.1.

## Carried forward from v1 / v1.1

All prior HITL decisions (HITL-INT-F07-AUTH, HITL-INT-MEMORY-LIFECYCLE, etc.) remain binding in v1.2. F2 introduced no changes that reopen earlier decisions.

## New decisions in v1.2

### DEC-v12-01 — SRC-ADR-001 evidence-class discipline

**Question:** F2 proposal binds SRC-ADR-001 (healing_dispatch_routing_adr.md) to F07.03 as "ADVISORY supplement". Should v1.2 canonical `authority_binding` list SRC-ADR-001 alongside SRC-INT-003 for F07.03?

**Analysis:** The source carries `invalid_for_normative_use=True` on its frontmatter and is classified ADVISORY (rank 6). Schema `authority_classes.yaml` says ADVISORY sources cannot promote atoms to NORMATIVE. The `authority_binding` field is schema-defined as sources that support the declared `evidence_class` — not an "associated reading list".

**Decision:** F07.03 `authority_binding` stays `[SRC-INT-003]`. SRC-ADR-001 is documented as supplementary context in `docs/wave_e/F2_source_authoring/source_authoring_log.md` but does NOT appear in the canonical atom binding.

**Rationale:** Listing it would create a false signal that ADR-001 actually supports the WEAK claim. It does, but only as advisory prose, not as authority. The atom stays honest at WEAK_EVIDENCE with its original binding.

### DEC-v12-02 — F04.04 supplementary binding on SRC-ADR-005

**Question:** F2 proposal adds SRC-ADR-005 (REPLAY_DETERMINISM_RULES) to F04.04's authority_binding as "supplementary". Should v1.2 canonical carry that binding?

**Analysis:** F04.04 stays WEAK_EVIDENCE — SRC-ADR-005 is adjacent (mutation replay), not direct (context-assembly idempotence). If the binding list is reserved strictly for sources that support the claim, adding SRC-ADR-005 is noise.

**Decision:** Accept the binding. F04.04 `authority_binding = [SRC-INT-003, SRC-ADR-005]`. Both sources provide partial, acknowledged-weak support. The evidence class truthfully stays WEAK_EVIDENCE because neither source makes the direct claim.

**Rationale:** A WEAK_EVIDENCE atom may cite multiple WEAK/adjacent sources. What's forbidden is a NORMATIVE atom with only WEAK/ADVISORY support, which we don't have here.

### DEC-v12-03 — Whether to upgrade weak edges touching upgraded atoms

**Question:** Edges `INT-F08.04-F09.01-01`, `INT-F09.05-F08.04-01`, and `INT-F12.08-F08.03-01` carry `evidence_class: WEAK_EVIDENCE` with binding `[SRC-INT-003]` or `[SRC-INT-004]`. Their atom endpoints upgrade to NORMATIVE in v1.2. Should the edges also upgrade?

**Analysis:** Edge evidence is independent of atom evidence — an edge needs its own source support. SRC-ADR-003 does describe the relationships in these edges (F08.04→F09.01 via GovernedHandoffAgent→UWG, F09.05→F08.04 via approval-state check). However, F2 did NOT propose these edge patches, and the contract says "do not reopen unrelated E1/F1 decisions unless an F2 delta makes that unavoidable."

**Decision:** Edges unchanged in v1.2. Log as follow-up D-v12-01 for a future targeted edge-evidence pass.

**Rationale:** Bounded scope discipline. The edges remain schema-valid and honest at WEAK_EVIDENCE. A future wave can upgrade them using SRC-ADR-003 which is now in the canonical source registry.

### DEC-v12-04 — DRAFT vs ACTIVE discipline for patched atoms

**Question:** F2's proposal files mark all patched atoms as `status: DRAFT`. Should v1.2 demote them to DRAFT, or keep the v1.1 ACTIVE status?

**Analysis:** Per the downstream lane contract, DRAFT is for proposal artifacts; ACTIVE is canonical. v1.1 already published these atoms as ACTIVE with WEAK evidence. F2 is an evidence-upgrade patch, not a new-atom proposal.

**Decision:** All 10 patched atoms retain `status: ACTIVE` in v1.2 canonical. Only `evidence_class` and `authority_binding` were modified.

**Rationale:** Demoting to DRAFT would incorrectly suggest the atoms are under reconsideration. They are not — their claims are unchanged; only their evidence binding improved.

### DEC-v12-05 — No F04 fabrication

**Question:** Should the integration pass author a minimal context-assembly ADR to close F04's three WEAK atoms, since that would flip F04 RED → GREEN and the global coverage > 0.95?

**Analysis:** The integration pass is a merge-only role. Authoring a new source is the authoring lane's responsibility (F2 proper), and F2 explicitly declined to do so. The contract is explicit: "Do not fabricate sources or locators."

**Decision:** F04 stays RED. B3 blocker is the highest priority for any later source-authoring wave.

**Rationale:** Any other resolution would be fabrication.

## Summary

| ID | Topic | Resolution |
|---|---|---|
| DEC-v12-01 | SRC-ADR-001 handling | Not added to F07.03 canonical binding |
| DEC-v12-02 | SRC-ADR-005 on F04.04 | Accepted as supplementary; stays WEAK |
| DEC-v12-03 | Weak-evidence edge upgrades | Deferred; not in F2 scope |
| DEC-v12-04 | DRAFT/ACTIVE discipline | Kept ACTIVE |
| DEC-v12-05 | F04 fabrication | Refused; B3 remains open |

Zero decisions required escalation. All are consistent with the frozen schema, the F2 proposal, and the bounded-scope contract.
