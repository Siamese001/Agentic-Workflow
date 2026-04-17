# Wave F2 - Source Authoring for Remaining RED Families

**Lane ID:** `F2_source_authoring`
**Scope:** Register real canonical repo documents as SourceAuthorityRecords; upgrade atoms only where those sources truly support the claim. No schema drift. No new families. No fabricated ADRs.
**Schema SSOT:** `docs/wave_e/00_schema/requirement_graph_schema.yaml`

## Headline Finding

**F2 authored zero new repo documents.** The long-"missing" ADRs for F08 exit spine, F07 healer retry, F03 L0 determinism, and F01 structured rejection **already exist** in the repo:

| Expected gap | Existing canonical source discovered in F2 |
|---|---|
| F08 Exit Spine ADR | `docs/architecture/eval_pipeline_acceptance.md` (ACCEPTED 2026-04-13, 135/135 tests passing) |
| F07 Healer Retry ADR | `docs/specs/hardening/HEALER_RETRY_HARDENING_SPEC.md` |
| F03 / F01 L0 Structure | `docs/specs/hardening/L0_DECOMPOSITION_SPEC.md` |
| F03.04 Determinism | `docs/specs/hardening/REPLAY_DETERMINISM_RULES.md` |
| Authority layering | `docs/specs/hardening/AUTHORITY_HIERARCHY_INVARIANTS.md` |

Prior waves (F1 especially) treated these as "missing ADR" blockers. They were a documentation-discovery failure, not an authoring failure.

## Deliverables

- `proposals/sources.yaml` — **6** new SourceAuthorityRecords (SRC-ADR-001 through SRC-ADR-006).
- `proposals/atoms.yaml` — **9 atom patches** (WEAK → NORMATIVE upgrades) + 1 supplementary binding (F04.04 stays WEAK).
- `proposals/edges.yaml`, `proposals/families.yaml`, `proposals/exclusions.yaml` — empty (no new entities).
- `scorecards/SCORE-F{01,03,04,07,08,09}-F2.yaml` — 6 projected post-F2 scorecards.
- `authored_source_index.md` — per-source locator resolvability check and why no new docs were authored.
- `source_authoring_log.md` — per-gap closure log with real sources cited.
- `red_family_closure_matrix.md` — atom-by-atom closure status for F04/F07/F08.
- `interaction_revisit_log.md` — re-evaluation of C1–C9 against new sources (still all deferred).

## ID Allocations Recorded

Appended to `docs/wave_e/00_schema/id_allocations.log`:
- SRC-ADR-001 through SRC-ADR-006

## 1. Number of Real Source Documents Authored

**0 new documents authored.** All 6 registered sources were pre-existing.

## 2. SourceAuthorityRecord Entries Added

**6** — SRC-ADR-001 (ADVISORY, invalid_for_normative_use) + SRC-ADR-002/003/004/005/006 (all ARCHITECTURAL rank 4).

## 3. Atoms Upgraded WEAK → NORMATIVE

**9** — F07.01, F07.02, F08.01, F08.03, F08.04, F08.05, F09.05, F01.06, F03.04.

Plus **1** supplementary binding (F04.04 stays WEAK but now cites SRC-ADR-005 for replay-determinism adjacency).

## 4. F04 Improvement

**NO.** F04 remains RED 0.25.

- No rule, ADR, or governing-semantics statement in the repo canonicalizes context attribution (F04.02), no-private-substitute (F04.03), or explicit context-assembly idempotence (F04.04).
- F2 declined to author a speculative ADR without implementation backing or HITL review.
- Blocker B3 remains.

## 5. F07 Improvement

**YES — material.** F07 moves RED 0.25 → YELLOW 0.75.

- F07.01 and F07.02 upgraded NORMATIVE via SRC-ADR-002 (HEALER_RETRY_HARDENING_SPEC defines `max_attempts=3`, strictness escalation, timeout escalation, scope lock).
- F07.03 stays WEAK because the escalation-target ADR (`healing_dispatch_routing_adr.md`) carries `invalid_for_normative_use=True`. Bound as ADVISORY supplement only.

## 6. F08 Improvement

**YES — full closure.** F08 moves RED 0.20 → GREEN 1.00.

- All four WEAK atoms (F08.01, F08.03, F08.04, F08.05) upgraded NORMATIVE via SRC-ADR-003 (eval_pipeline_acceptance).
- F08.02 was already NORMATIVE.
- F2 closes what prior waves thought impossible: the exit-spine source was hiding in plain sight.

## 7. Deferred Interaction Candidates That Became Closable

**None.** C1–C9 all remain deferred. Full re-evaluation in `interaction_revisit_log.md`.

Upgrading F01.06 and F03.04 to NORMATIVE does strengthen the "source atom" end of hypothetical edges (C1, C6), but the "target atom" or downstream-atom end is still missing in every deferred candidate.

## 8. Exact Blockers Still Requiring a Later Wave

| # | Blocker | Family impact | Required action |
|---|---|---|---|
| **B1-partial** | Exit-spine ADR - RESOLVED via SRC-ADR-003 | F08 closed | ✅ done by F2 |
| **B2-partial** | Bounded-retry rule - RESOLVED via SRC-ADR-002 for F07.01/.02 | F07 partial | F07.03 needs normative escalation-target ADR (e.g., de-advisory the F25-int ADR via HITL) |
| **B3** | Context-assembly ADR | F04 RED unchanged | Author a dedicated ADR specifying attribution, no-private-substitute, idempotence. Also resolves OOS-003 revisit trigger. **Highest remaining impact.** |
| **B4** | Structured rejection reason-code standard - RESOLVED via SRC-ADR-004 | F01.06 closed | ✅ done by F2 |
| **B5** | One-route-per-step determinism rule - RESOLVED via SRC-ADR-004 | F03.04 closed | ✅ done by F2 |
| **B6** | L3 orchestration charter ADR | F05.04 stays WEAK | Author L3 charter explicitly defining dispatch role. |
| **B7** | 6 deferred interaction candidates (C1, C2, C3, C4, C6, C9) | Graph completeness | Downstream atoms / edge-kind patches required. |

**Four blockers closed; three remain** (B3 context, B6 L3 charter, F07.03 escalation ADR de-advisory).

## Projected Canonical v1.2 State

Bucket distribution:

| Bucket | v1.1 count | Projected post-F2 | Families |
|---|---:|---:|---|
| GREEN | 5 | **9** | F01, F02, F03, F06, F08, F09, F10, F11, F12 |
| YELLOW | 4 | **2** | F05, F07 |
| RED | 3 | **1** | F04 only |

Global coverage: **0.776 YELLOW → projected 0.931 GREEN** (54 NORMATIVE / 58 counted atoms; 4 WEAK remaining).

## Ready for Integration?

**YES.**

F2's output is schema-valid, bounded, and honestly constrained. Every NORMATIVE upgrade cites at least one real, resolvable, rank-4 ARCHITECTURAL source. The one ADVISORY source (SRC-ADR-001) is used only as supplementary binding on an atom that stays WEAK, respecting the `invalid_for_normative_use=True` marker.

Projected canonical v1.2 after F2 integration:
- Global coverage: 0.931 GREEN (up from 0.776 YELLOW).
- 9 green / 2 yellow / 1 red families.
- F04 remains the sole RED family, awaiting a context-assembly ADR.

## Validation Self-Check

- [x] All new SRC IDs match `^SRC-(INT|EXT|ADR|RULE|CODE|DEC)-[0-9]{3}$` (SRC-ADR-001..006).
- [x] All 6 locators resolve in-repo (verified by direct file reads in F2 session).
- [x] Every NORMATIVE upgrade cites ≥1 ARCHITECTURAL-rank source.
- [x] No atom marked ACTIVE; all proposals are DRAFT.
- [x] No new Family IDs minted.
- [x] No new atom IDs minted (F2 is patch-only).
- [x] Exclusions unchanged (OOS-003 retained).
- [x] No writes outside `docs/wave_e/F2_source_authoring/` except id_allocations.log (append-only per schema).
- [x] No canonical v1.1 files modified.
- [x] No fabricated ADRs.
- [x] ADVISORY source (SRC-ADR-001) correctly NOT used to support NORMATIVE evidence_class.
