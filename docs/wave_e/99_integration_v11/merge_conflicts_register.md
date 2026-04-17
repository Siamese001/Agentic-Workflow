# F1 Integration — Merge Conflicts Register (v1.1 delta)

Records only conflicts introduced by merging F1 into canonical v1. All v1 conflicts (MC-01..MC-10) remain applied from v1.

---

## MC-V11-01 — F12.05 patch application (WEAK_EVIDENCE → NORMATIVE)

**Conflict:** F1 proposes F12.05 with evidence_class NORMATIVE and expanded authority_binding (`[SRC-RULE-001, SRC-INT-001, SRC-INT-003, SRC-INT-004]`). Canonical v1 has F12.05 WEAK_EVIDENCE bound only to `[SRC-INT-003]`.
**Resolution:** Apply last-writer-wins per v1 precedent (HITL-INT-001). Accept F1's version. The new bindings are real and schema-valid:
- SRC-RULE-001 constitutional §17 "Memory Lifecycle mandatory" directly covers future-run consumption.
- SRC-INT-001 AGENTS.md and SRC-INT-004 (new) elaborate the session-start recall protocol.
**Evidence:** Canonical v1.1 `atoms.yaml` F12.05 has NORMATIVE + 4 bindings. Rationale field records the upgrade.

## MC-V11-02 — New atoms F12.07, F12.08 admission

**Conflict:** F1 proposes two new atoms under existing family F12. IDs 07 and 08 were reserved in `id_allocations.log` by F1 before publish.
**Resolution:** Admit both. Each atom:
- cites ≥1 rank≤ARCHITECTURAL source (SRC-RULE-001 rank 1 + SRC-INT-001 rank 2 + SRC-INT-004 rank 2);
- has resolved `owning_layer: L6`;
- has no conflicting or duplicate `(family_id, claim)` match against v1 atoms;
- has clear rationale.
Promote both DRAFT → ACTIVE per v1 promotion rules (HITL-INT-005).
**Evidence:** Canonical v1.1 atoms.yaml contains F12.07 + F12.08 as ACTIVE NORMATIVE.

## MC-V11-03 — SRC-INT-004 admission

**Conflict:** F1 proposes new source SRC-INT-004 at locator `AGENTS.md#memory-lifecycle`.
**Resolution:** Admit.
- Locator resolves in-repo (AGENTS.md exists; the Memory Lifecycle section is an actual heading).
- Subtype `INT` is schema-valid.
- authority_class `GOVERNANCE` (rank 2) is consistent with the parent doc (AGENTS.md = SRC-INT-001 = GOVERNANCE).
- ID was reserved in `id_allocations.log`.
**Evidence:** Canonical v1.1 sources.yaml contains SRC-INT-004.

## MC-V11-04 — Three new edges admission

**Conflict:** F1 proposes three edges; endpoints include two new atoms.
**Resolution:** All three admit to ACTIVE after F12.07 and F12.08 are admitted:
- `INT-F12.05-F12.07-01 REFINES` — both endpoints ACTIVE NORMATIVE. Edge NORMATIVE.
- `INT-F12.07-F02.01-01 REQUIRES` — endpoints ACTIVE NORMATIVE. Edge NORMATIVE.
- `INT-F12.08-F08.03-01 DEPENDS_ON` — F12.08 ACTIVE NORMATIVE; F08.03 ACTIVE WEAK_EVIDENCE. Edge WEAK_EVIDENCE (correctly inherits target weakness).
**Evidence:** Canonical v1.1 edges.yaml; all three appear at end of list with ACTIVE status.
**Note on uniqueness:** `INT-F12.07-F02.01-01` uses edge_kind REQUIRES while v1's existing `INT-F12.05-F02.01-01` uses DEPENDS_ON. Different source atoms + different kinds = no duplicate `(source, target, edge_kind)` triple.

## MC-V11-05 — Candidates NOT closed (deferred carry-forward)

**Conflict:** F1's `interaction_candidate_disposition.md` explicitly defers C1, C2, C3, C4, C6, C9 and takes no action on C7, C8. Integration pass must confirm nothing has silently changed for these.
**Resolution:** v1.1 carries all deferred candidates forward untouched. No edges added for deferred items. No atoms added for C2/C3 (would have required new F04/F11 atoms F1 explicitly declined to fabricate).
**Evidence:** v1.1 edges.yaml contains exactly 3 F1-authored edges; no entries for C1/C2/C3/C4/C6/C9.
