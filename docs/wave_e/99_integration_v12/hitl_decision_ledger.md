# v1.2 HITL Decision Ledger

F2 integration pass. Records every non-trivial decision made while merging F2 onto v1.1. Updated during the F2.1 reporting reconciliation pass for internal consistency only; no decision was changed.

## Carried forward from v1 / v1.1

All prior HITL decisions (HITL-INT-F07-AUTH, HITL-INT-MEMORY-LIFECYCLE, etc.) remain binding in v1.2. F2 introduced no changes that reopened earlier decisions.

## New decisions in v1.2

### DEC-v12-01 — SRC-ADR-001 evidence-class discipline

**Question:** F2 proposal binds SRC-ADR-001 (healing_dispatch_routing_adr.md) to F07.03 as "ADVISORY supplement". Should v1.2 canonical `authority_binding` list SRC-ADR-001 alongside SRC-INT-003 for F07.03?

**Analysis:** The source carries `invalid_for_normative_use=True` on its frontmatter and is classified ADVISORY (rank 6). Per schema `authority_classes.yaml`, ADVISORY sources cannot promote atoms to NORMATIVE. The `authority_binding` field is reserved for sources that actually support the declared `evidence_class` — not an "associated reading list".

**Decision:** F07.03 `authority_binding` stays `[SRC-INT-003]`. SRC-ADR-001 is documented as supplementary context in `docs/wave_e/F2_source_authoring/source_authoring_log.md` but does NOT appear in the canonical atom binding.

**Rationale:** Listing it would create a false signal that ADR-001 supports the WEAK claim. It does, but only as advisory prose, not as authority. The atom stays honest at WEAK_EVIDENCE.

### DEC-v12-02 — F04.04 supplementary binding on SRC-ADR-005

**Question:** F2 adds SRC-ADR-005 (REPLAY_DETERMINISM_RULES) to F04.04's authority_binding as "supplementary". Should v1.2 carry that binding?

**Analysis:** F04.04 stays WEAK_EVIDENCE — SRC-ADR-005 is adjacent (mutation replay), not direct (context-assembly idempotence).

**Decision:** Accept the binding. F04.04 `authority_binding = [SRC-INT-003, SRC-ADR-005]`. Both sources provide partial, acknowledged-weak support. Evidence class truthfully remains WEAK_EVIDENCE because neither source makes the direct claim.

**Rationale:** A WEAK_EVIDENCE atom may cite multiple WEAK/adjacent sources. What's forbidden is a NORMATIVE atom with only WEAK/ADVISORY support, which this is not.

### DEC-v12-03 — Whether to upgrade weak edges touching upgraded atoms

**Question:** v1.2 retains **8 WEAK_EVIDENCE edges** (recounted from canonical `edges.yaml`). Should any upgrade to NORMATIVE because their atom endpoints were upgraded?

**Analysis:** Edge evidence is independent of atom evidence — an edge needs its own source support.

Of the 8 weak edges:
- **5 have both endpoints NORMATIVE in v1.2**: `INT-F02.01-F01.05-01`, `INT-F08.04-F09.01-01`, `INT-F09.05-F08.04-01`, `INT-F12.05-F02.01-01`, `INT-F12.08-F08.03-01`. SRC-ADR-003 is registered and could plausibly support three of these (F08.04↔F09.01 via GovernedHandoffAgent→UWG and F09.05→F08.04 via approval-state check).
- **3 involve a WEAK atom endpoint** and cannot upgrade until the atom closes: `INT-F05.04-F06.01-01` (F05.04 WEAK), `INT-F07.03-F02.01-01` and `INT-F07.03-F05.01-01` (F07.03 WEAK).

F2 did NOT propose edge patches; the contract forbids reopening unrelated E1/F1 decisions unless an F2 delta makes that unavoidable.

**Decision:** All 8 weak edges unchanged in v1.2. Log as follow-up D-v12-01 for a future targeted edge-evidence pass covering at least the 5 dual-NORMATIVE-endpoint edges.

**Rationale:** Bounded-scope discipline. The edges remain schema-valid and honest at WEAK_EVIDENCE. A future wave can upgrade them using SRC-ADR-003 (and other sources) now in the canonical registry.

### DEC-v12-04 — DRAFT vs ACTIVE discipline for patched atoms

**Question:** F2's proposal files mark all patched atoms as `status: DRAFT`. Should v1.2 demote them to DRAFT, or keep v1.1 ACTIVE?

**Analysis:** DRAFT is for proposal artifacts; ACTIVE is canonical. v1.1 already published these atoms as ACTIVE with WEAK evidence. F2 is an evidence-upgrade patch, not a new-atom proposal.

**Decision:** All 10 patched atoms retain `status: ACTIVE` in v1.2 canonical. Only `evidence_class` and `authority_binding` were modified.

**Rationale:** Demoting to DRAFT would incorrectly suggest the atoms are under reconsideration.

### DEC-v12-05 — No F04 fabrication

**Question:** Should the integration pass author a minimal context-assembly ADR to close F04's three WEAK atoms, since that would flip F04 RED → GREEN?

**Analysis:** The integration pass is merge-only. The contract is explicit: "Do not fabricate sources or locators."

**Decision:** F04 stays RED. B3 blocker is the highest priority for any later source-authoring wave.

**Rationale:** Any other resolution would be fabrication.

## Follow-up items

| ID | Topic | Status |
|---|---|---|
| D-v12-01 | Targeted edge-evidence upgrade for the 5 dual-NORMATIVE-endpoint weak edges | Open; deferred to a later wave. |

## Summary

| ID | Topic | Resolution |
|---|---|---|
| DEC-v12-01 | SRC-ADR-001 handling | Not added to F07.03 canonical binding |
| DEC-v12-02 | SRC-ADR-005 on F04.04 | Accepted as supplementary; stays WEAK |
| DEC-v12-03 | Weak-evidence edge upgrades (8 edges total) | Deferred; 5 are candidates, 3 are blocked by WEAK atom endpoints |
| DEC-v12-04 | DRAFT/ACTIVE discipline | Kept ACTIVE |
| DEC-v12-05 | F04 fabrication | Refused; B3 remains open |

Zero decisions required escalation. All are consistent with the frozen schema, the F2 proposal, and the bounded-scope contract.
