# v1.3 HITL Decision Ledger

F3 integration pass. Records every non-trivial decision made while merging F3 onto v1.2.

## Carried forward from v1 / v1.1 / v1.2

All prior HITL decisions (HITL-INT-F07-AUTH, HITL-INT-V11-001 memory lifecycle, DEC-v12-01 through DEC-v12-05) remain binding in v1.3. F3 introduced no changes that reopened earlier decisions.

## New decisions in v1.3

### DEC-v13-01 — F04.02 claim text: preserve v1.2 verbatim

**Question:** F3's proposal restates F04.02 with different wording while declaring "claim verbatim." Should v1.3 accept the rewording?

**Analysis:** Scope is source-closure, not claim authoring. F3 produced no rationale for the reword, and SRC-ADR-007's CTX-I1 supports the v1.2 claim identically well.

**Decision:** Preserve v1.2 claim verbatim. Apply only `evidence_class` and `authority_binding` updates.

**Rationale:** Honest merge discipline + honor F3's own stated intent.

### DEC-v13-02 — F04.04 supplementary binding retained

**Question:** F3 proposes F04.04 binding `[SRC-INT-003, SRC-ADR-005, SRC-ADR-007]`. SRC-ADR-005 was DEC-v12-02's acknowledged-adjacent supplementary. Should v1.3 drop SRC-ADR-005 now that a direct source exists?

**Analysis:** SRC-ADR-005 remains factually adjacent (replay determinism). Keeping it causes no harm and signals the full support surface. The direct normative claim is carried by SRC-ADR-007.

**Decision:** Keep all three bindings.

**Rationale:** Additive history preserved; no honesty cost.

### DEC-v13-03 — SRC-ADR-001 stays unbound

**Question:** F3's escalation_authority_decision.md confirms SRC-ADR-001 remains `invalid_for_normative_use=True`. Confirm v1.3 keeps it out of F07.03's binding.

**Analysis:** SRC-ADR-009 (new ADR-ESC-001) provides the normative escalation target. SRC-ADR-001 continues to describe healing-tier semantics as advisory prose only.

**Decision:** SRC-ADR-001 is unbound in v1.3. F07.03 binding is `[SRC-INT-003, SRC-ADR-008, SRC-ADR-009]`.

**Rationale:** Constitutional ADVISORY discipline preserved.

### DEC-v13-04 — No edge patches in v1.3

**Question:** F3 proposes zero edge patches, although SRC-ADR-003/007/008/009 could now plausibly support at least 6 of the 8 weak edges. Should the v1.3 integration pass apply edge upgrades as a free byproduct?

**Analysis:** The integration pass's mandate is "merge only F3 deltas" (rule 3) and "do not upgrade any weak edge unless F3 explicitly proposed that edge patch" (rule 7). F3's `edge_patches: []` is explicit; the integration pass cannot substitute its own judgment.

**Decision:** v1.3 carries all 26 edges from v1.2 unchanged. Wave F4 (`docs/wave_e/F4_edge_exclusion_cleanup/`) is the correct lane for the targeted edge-evidence upgrade.

**Rationale:** Bounded-scope discipline.

### DEC-v13-05 — OOS-003 carried forward unchanged

**Question:** OOS-003's revisit trigger ("Future wave surfaces a concrete operational constraint that L1 cannot satisfy for context grounding") is now satisfied by SRC-ADR-007. The ADR confirms L1 *can* satisfy context grounding, so the original rationale to add a C0 layer is moot. Should v1.3 retire OOS-003?

**Analysis:** The integration-pass rule (rule 8) is explicit: "Do not retire or change OOS-003 unless F3 explicitly proposed an exclusion change in proposals/exclusions.yaml. Otherwise carry it forward and log that the revisit trigger is satisfied but canonical exclusion is unchanged." F3's `exclusion_patches: []` is explicit.

**Decision:** OOS-003 carries forward in v1.3 exactly as written in v1.2. This ledger records that its revisit trigger is satisfied. Wave F4's `exclusion_review_log.md` proposes a state transition (SUPERSEDED) for a later integration pass to accept.

**Rationale:** Scope fence honored. No honesty cost — the revisit-satisfied fact is now documented here and in v1.3 canonical exclusions.yaml header comment.

### DEC-v13-06 — DRAFT → ACTIVE promotion not applicable

**Question:** Do any atoms need DRAFT → ACTIVE promotion in v1.3?

**Analysis:** All 5 patched atoms were already ACTIVE in v1.2 with WEAK_EVIDENCE. F3's patches changed only `evidence_class` and `authority_binding`. No new atoms were introduced by F3.

**Decision:** No DRAFT → ACTIVE promotions in v1.3.

**Rationale:** Status stays ACTIVE where it already was; per DEC-v12-04, proposal-file DRAFT convention does not demote canonical state.

### DEC-v13-07 — No B7 interaction candidates closed

**Question:** Do the three new F3 sources (SRC-ADR-007/008/009) close any of the 6 deferred B7 interaction candidates from E1d?

**Analysis:** B7 candidates require either new atoms or new edges. F3 introduced neither. The sources describe invariants supporting existing atom claims but do not by themselves motivate new first-class edges or atoms. F3's `interaction_candidate_disposition.md` does not reopen any B7 candidate.

**Decision:** B7 candidates remain deferred.

**Rationale:** B7 is explicitly out of F3's scope. A later wave targeting interaction closure is required.

## Follow-up items

| ID | Topic | Status |
|---|---|---|
| D-v12-01 | Targeted edge-evidence upgrade for the 8 WEAK edges | **Open — addressed by Wave F4.** |
| DEC-v13-05 | OOS-003 state-transition proposal | **Open — addressed by Wave F4 exclusion review.** |
| B7 | 6 deferred interaction candidates | **Open — requires future wave with explicit HITL approval.** |

No follow-ups have been silently dropped.
