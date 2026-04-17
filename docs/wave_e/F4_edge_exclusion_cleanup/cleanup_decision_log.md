# Wave F4 — Cleanup Decision Log

Every non-trivial F4 decision is recorded here.

## DEC-F4-01 — All 8 weak edges upgrade to NORMATIVE

**Question:** Which of the 8 v1.3 weak edges upgrade, and which remain WEAK?

**Analysis:** Per-edge direct-support analysis in `weak_edge_upgrade_matrix.md`. Each edge was tested against existing canonical sources using the rule "does a canonical source directly state the edge claim?" — not just "do both endpoints have normative support?". Results:

| Edge | Direct statement source | Disposition |
|---|---|---|
| INT-F02.01-F01.05-01 | F01.05 self-support + SRC-INT-001/003 + SRC-RULE-001 | UPGRADE |
| INT-F05.04-F06.01-01 | SRC-ADR-008 L3-I1 step 2 | UPGRADE |
| INT-F07.03-F02.01-01 | SRC-ADR-009 ESC-I1 + SRC-ADR-008 L3-I3 | UPGRADE |
| INT-F07.03-F05.01-01 | SRC-ADR-009 ESC-I1 + SRC-ADR-008 L3-I3 | UPGRADE |
| INT-F08.04-F09.01-01 | F08.04 self-support + SRC-ADR-003 HandoffAgent | UPGRADE |
| INT-F09.05-F08.04-01 | F09.05 self-support + SRC-ADR-003 `evaluate_sealed()` | UPGRADE |
| INT-F12.05-F02.01-01 | F12.05 self-support + SRC-INT-004 + SRC-RULE-001 §17 | UPGRADE |
| INT-F12.08-F08.03-01 | F12.08 self-support + SRC-ADR-003 + SRC-INT-004 | UPGRADE |

**Decision:** Propose 8 UPGRADE patches. 0 edges remain WEAK.

**Rationale:** Each upgrade cites a source whose text directly expresses the edge relation. None relied on endpoint-atom-normativity as the upgrade justification. If any edge had failed the direct-statement test, it would have been left WEAK; none did.

## DEC-F4-02 — OOS-003 revised to SUPERSEDED

**Question:** Retire, retain, or revise OOS-003?

**Analysis:** See `exclusion_review_log.md`. SRC-ADR-007 (ADR-CTX-001) supersedes the rationale for holding OOS-003 open — L1 is now normatively established as capable of satisfying context grounding, eliminating the case for a C0 layer. Options: (A) Retain unchanged — dishonest. (B) Retire — loses history. (C) Revise to SUPERSEDED — preserves history, matches schema enum. (D) Revise to OUT_OF_CHARTER — wrong enum.

**Decision:** Propose OOS-003 revision to reason=SUPERSEDED with SRC-ADR-007 cited in `notes` and an updated `revisit_trigger` capturing the resolution.

**Rationale:** Matches the F4 "truly supersedes" bar. Preserves historical scope_statement and related_atoms / related_families for future reviewers.

## DEC-F4-03 — No B7 interaction candidates closed as byproduct

**Question:** Do any of the 8 edge upgrades, individually or collectively, close any of the 6 deferred B7 interaction candidates?

**Analysis:** B7 candidates are *new* edges or *new* atoms that were flagged in E1d's `interaction_candidates.md` as interactions not yet first-classed. F4's edge upgrades modify only evidence_class and authority_binding on 8 already-existing edges. Revising edge evidence cannot instantiate a new interaction. No existing edge-kind patch is obviously justified by F4 evidence; all 8 patches stay within `REQUIRES / CONDITIONAL_ON / DEPENDS_ON` as already declared.

**Decision:** No B7 closures. B7 candidates remain deferred.

**Rationale:** F4 scope explicitly excludes chasing B7 candidates "except where an already-existing edge-kind patch is now obviously justified". No such case arose.

## DEC-F4-04 — No atom reopens, no new sources, no new families

**Question:** Does F4 need any atom changes, new sources, or family changes?

**Analysis:** F4 scope is edge evidence + OOS-003. No atom claim is reopened — the 60 ACTIVE NORMATIVE atoms in v1.3 remain untouched. All edge upgrades cite only v1.3 sources; no new SRC IDs are required. No family boundary is affected.

**Decision:** `proposals/families.yaml: []`, `proposals/atoms.yaml: []`, `proposals/sources.yaml: []`.

**Rationale:** Bounded-scope discipline. Writing empty proposal files explicitly documents that nothing changed in those scopes.

## DEC-F4-05 — Preserve edge_kind, direction, status, condition verbatim

**Question:** Should any edge's `edge_kind`, `direction`, `status`, or `condition` be revised as part of the evidence cleanup?

**Analysis:** The F4 scope fence is evidence cleanup only. `edge_kind` and `direction` changes are structural and would require a separate targeted wave. `status` stays ACTIVE for all 8 edges (they were ACTIVE in v1.2 and v1.3 with weak evidence; upgrading evidence does not change status). `condition` on INT-F07.03-F02.01-01 stays as "Unrecoverable L2 task failure detected." — SRC-ADR-009 §3.1 definition matches.

**Decision:** Preserve edge_kind, direction, status, and condition verbatim from v1.3.

**Rationale:** Minimal, bounded cleanup.

## DEC-F4-06 — No downgrades

**Question:** Does anything in v1.3 regress or downgrade under F4 scrutiny?

**Analysis:** Every atom, every NORMATIVE edge, and every source in v1.3 was re-validated against F4's stricter direct-statement standard. Nothing regressed.

**Decision:** No downgrades in F4.

**Rationale:** Cleanup is upgrade-only.

## Follow-ups after F4

| ID | Topic | Status |
|---|---|---|
| D-v12-01 | Weak-edge upgrade pass | **Closed by this F4 proposal** once v1.4 integration accepts edges.yaml. |
| DEC-v13-05 | OOS-003 state transition | **Closed by this F4 proposal** once v1.4 integration accepts exclusions.yaml. |
| B7 | 6 deferred interaction candidates | **Open.** Requires future wave with HITL approval. |

No silent drops. No new blockers introduced.
