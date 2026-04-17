# v1.3 Merge Conflicts Register

F3 integration pass. Base: canonical v1.2. Delta: F3 source-authoring proposals.

## Conflict inventory

**Non-trivial conflicts: 1** (F04.02 claim-text drift in F3 proposal). All others are routine merge decisions.

## Non-trivial conflict

### M-v13-02 — F04.02 claim-text drift in F3 proposal

**Observed:** `docs/wave_e/F3_final_source_closure/proposals/atoms.yaml` restates F04.02 as *"Context delivered to reasoning, orchestration, and task execution MUST carry resolvable source attribution."* — while the v1.2 canonical claim reads *"Assembled context MUST carry attribution that traces each element to its source."* F3's own atoms.yaml header comment declares "Each patch preserves the claim verbatim."

**Analysis:** F3's stated scope is source-closure: "only evidence_class and authority_binding change". Claim text is outside that scope. The two claims are semantically close, but a canonical atom's claim text is normatively load-bearing — changing it is a content change and requires its own HITL justification. F3 produced none. The F3 scorecards (SCORE-F04-F3) and `final_weak_atom_closure_matrix.md` reason about CTX-I1 attribution coverage, which SRC-ADR-007 supports for the v1.2 claim just as well as for the F3 reworded claim.

**Decision:** **v1.3 preserves the v1.2 F04.02 claim verbatim.** Only `evidence_class` (WEAK_EVIDENCE → NORMATIVE) and `authority_binding` (+SRC-ADR-007) are applied. F04.03 and F04.04 claims were unchanged in F3's proposal and are carried forward verbatim.

**Rationale:** Honor F3's explicit stated intent ("claim verbatim"). Avoid silent content drift. If a future wave deems the rewording genuinely normative, it can propose the claim change as its own tracked delta.

## Minor merge decisions (trivial)

| # | Decision | Resolution |
|---|---|---|
| M-v13-01 | Where to append F3 sources in `sources.yaml` | Appended after SRC-ADR-006 under `# === F3 additions ===`. No ordering conflict. |
| M-v13-03 | Whether to carry v1.2's SRC-ADR-005 supplementary binding on F04.04 | **Yes.** F04.04 binding becomes `[SRC-INT-003, SRC-ADR-005, SRC-ADR-007]`. SRC-ADR-007 is the direct normative source; SRC-ADR-005 is retained as acknowledged-adjacent (replay-determinism) support per DEC-v12-02. Additive, not replacement. |
| M-v13-04 | Whether F3's proposal-only sidecar `rationale:` leaks into canonical atoms | **Rejected.** Canonical atoms retain only schema-defined fields. F3 rationales stay in `F3_final_source_closure/proposals/atoms.yaml` and `source_authoring_decisions.md`. (Exception: pre-existing rationales on F12.05, F12.06, F12.07, F12.08 from prior v1.1 integration remain — not introduced by F3.) |
| M-v13-05 | DRAFT → ACTIVE promotion discipline | All 5 patched atoms were already ACTIVE in v1.2 with WEAK_EVIDENCE; v1.3 preserves ACTIVE. No DRAFT→ACTIVE transition occurred because no new atom was introduced. |
| M-v13-06 | Edges carried forward unchanged | **Accepted.** F3 proposed no edge patches (`edge_patches: []`). All 26 v1.2 edges pass through unchanged, including the 8 WEAK_EVIDENCE edges. Edge cleanup is Wave F4's responsibility. |
| M-v13-07 | Exclusions carried forward unchanged | **Accepted.** F3 proposed no exclusion patches. OOS-003 carries forward with its NOT_YET_DECIDED reason unchanged even though its revisit trigger is now satisfied; the state transition is logged as DEC-v13-05 and addressed in Wave F4. |
| M-v13-08 | SRC-ADR-001 remains unbound | **Preserved.** F3 explicitly refused to add SRC-ADR-001 to F07.03's binding because it remains `invalid_for_normative_use=True`. F07.03 uses the new SRC-ADR-008 + SRC-ADR-009 pair instead. Constitutional ADVISORY discipline held. |

## Sources considered and NOT integrated

None in F3. All three F3-authored ADRs (SRC-ADR-007/008/009) pass locator resolvability checks and are integrated.

## ADVISORY discipline

SRC-ADR-001 remains the only ADVISORY-class source in v1.3. It is present in `sources.yaml` and bound to no atom. Validation confirms 0 atoms cite SRC-ADR-001 in `authority_binding` in v1.3.

## Edge evidence unchanged

v1.3 has **26 edges total**: **18 NORMATIVE** + **8 WEAK_EVIDENCE**, identical to v1.2. F3 proposed no edge patches.

Endpoint profile changed: of the 8 weak edges, **8 now have both endpoints NORMATIVE** (up from 5/8 in v1.2), because the 3 edges that previously had a WEAK atom endpoint (F05.04, F07.03-sourced) now have their source atom upgraded.

This makes all 8 weak edges cleanly eligible for Wave F4's targeted edge-evidence upgrade pass.

## Outcome

v1.3 is a clean additive merge. One non-trivial conflict (M-v13-02 claim-text drift) resolved by honoring F3's own stated intent. All other merge actions were routine.
