# Wave E1c — Authority Binding, Scope, and Exclusions

**Lane ID:** `E1c_authority_scope`
**Scope:** Materialize SourceAuthorityRecords for E1b's placeholder SRC IDs; author additional Exclusions; resolve layer/authority scope decisions; patch atoms only where IDs are stable and the change is defensible.

## Deliverables

- `proposals/sources.yaml` — **5** SourceAuthorityRecords.
- `proposals/exclusions.yaml` — **2** new OOS records (OOS-002, OOS-003). (E1b authored OOS-001.)
- `proposals/atoms.yaml` — **3** patched atoms (F04.01, F04.04, F08.05) superseding E1b versions.
- `proposals/families.yaml`, `proposals/edges.yaml` — schema-valid empty lists.
- `scorecards/SCORE-F<NN>-E1c.yaml` — 12 scorecards (post-E1c state).
- `evidence_binding_notes.md` — placeholder-to-real SRC mapping, per-family evidence policy, rank-floor check, ADVISORY/WEAK distinction.
- `scope_decision_log.md` — stable-ID decision records (DEC-E1c-*).

## 1. Source Count by Subtype and Authority Class

| Subtype | Count |
|---|---:|
| RULE | 2 (SRC-RULE-001, SRC-RULE-002) |
| INT | 3 (SRC-INT-001, SRC-INT-002, SRC-INT-003) |
| EXT | 0 |
| ADR | 0 (placeholders collapsed to INT per DEC-E1c-PLACEHOLDER-MAPPING) |
| CODE | 0 |
| DEC | 0 |
| **TOTAL** | **5** |

| authority_class | Rank | Count |
|---|---:|---:|
| CONSTITUTIONAL | 1 | 1 (SRC-RULE-001) |
| GOVERNANCE | 2 | 3 (SRC-RULE-002, SRC-INT-001, SRC-INT-002) |
| ARCHITECTURAL | 4 | 1 (SRC-INT-003) |
| EXTERNAL_STANDARD, OPERATIONAL, ADVISORY, INTERNAL_ONLY | — | 0 |

All five sources clear the NORMATIVE rank floor (rank ≤ 4).

## 2. Exclusion Count by Reason

| Reason | Count | IDs |
|---|---:|---|
| OUT_OF_CHARTER | 2 | OOS-001 (E1b), OOS-002 (E1c) |
| NOT_YET_DECIDED | 1 | OOS-003 (E1c) |
| DEFERRED, SUPERSEDED, UNSAFE, DUPLICATE | — | 0 |
| **TOTAL (across lanes)** | **3** | — |
| **E1c-authored only** | **2** | OOS-002, OOS-003 |

## 3. Families with Defendable NORMATIVE Evidence Policy

**Strong (8 of 12):** F02, F03, F06, F09, F10, F11, F12 (all cite SRC-RULE-001 + SRC-INT-003 for governing-semantics claims) and F05 (cites SRC-INT-003 layer charter + SRC-RULE-001 for cross-family prohibitions).

**Partial (2 of 12):**
- **F01** — NORMATIVE via SRC-INT-001 + SRC-INT-003; owning_layer L0 confirmed but not anchored in a hard rule (inherits from intake-as-boundary convention).
- **F04** — 1 NORMATIVE (F04.01 post-patch) + 3 WEAK_EVIDENCE; layer resolved but idempotence claim unsourced.

**Weak (2 of 12):**
- **F07** — 1 NORMATIVE (F07.04 via Write Gate monopoly) + 3 WEAK_EVIDENCE (bounded retry, surface-to-L3). Needs dedicated ARCHITECTURAL source or family authority_class revision.
- **F08** — 1 NORMATIVE (F08.02) + 4 WEAK_EVIDENCE. Exit spine is unsourced beyond inference.

## 4. Families Blocked on Missing Atom IDs

**None.** E1b published stable atom IDs F01.01..F12.06 (59 atoms) and reserved ranges in `id_allocations.log`. E1c's Pass B proceeded against those stable IDs; 3 targeted patches published.

## 5. Ready for Integration?

**NO — intentionally, and waiting on E1d.** E1c's output completes the authority/scope surface; integration pass still needs E1d's InteractionEdge records.

**Blockers carried forward to integration pass:**

| # | Blocker | Action |
|---|---|---|
| B1 | E1b atoms cite placeholder SRC IDs (SRC-ADR-L0..L6, SRC-ADR-WG, SRC-ADR-EXIT) that don't match the schema regex. | Integration pass MUST apply the mapping table in `evidence_binding_notes.md §1` to all 56 E1b atoms not re-published by E1c. |
| B2 | SRC-ADR-EXIT has no real source. F08 coverage is 0.2. | A future wave MUST author an exit-spine ADR or rule. Not blocking for this run's integration. |
| B3 | F07 family authority_class is OPERATIONAL (rank 5) but F07.04 cites rank-1. | Recommend E1a revise F07.authority_class to ARCHITECTURAL (DEC-E1c-F07-AUTH-CLASS). Integration pass emits WARNING otherwise. |
| B4 | No interaction edges published yet. | Expected — E1d is the edge-drafting lane. |
| B5 | OOS-001 and OOS-002 cover related but distinct scopes (L0 vs. L2 current-run L6 influence). | Integration pass confirms no semantic overlap. |

## 6. Cross-Lane Notes

- **To E1d:** All SRC and OOS IDs E1d may need to cite are now minted. Use `SRC-RULE-001`, `SRC-INT-001/002/003`, `OOS-001/002/003` directly; do not use placeholder mnemonics.
- **To E1a:** Recommended revision to F07 authority_class (ARCHITECTURAL). Not blocking.
- **To integration pass:** Three E1c atoms (F04.01, F04.04, F08.05) supersede E1b versions. Apply last-writer-wins. Apply placeholder-to-real SRC mapping to all other E1b atoms.

## 7. Validation Self-Check

- [x] All 5 SourceAuthorityRecords match `^SRC-(INT|EXT|ADR|RULE|CODE|DEC)-[0-9]{3}$`.
- [x] Every SRC has required fields (id, subtype, title, locator, authority_class, retrieved_at_wave).
- [x] SRC-INT-* locators are resolvable (files exist in repo).
- [x] SRC-RULE-* locators are resolvable.
- [x] OOS-002 and OOS-003 match `^OOS-[0-9]{3}$`.
- [x] OOS reasons are from the fixed enum.
- [x] OOS-003 has `revisit_trigger` (NOT_YET_DECIDED reason).
- [x] E1c's 3 patched atoms match atom schema and have valid `supersedes` set to their own IDs (last-writer-wins pattern).
- [x] No new Family IDs minted.
- [x] No ACTIVE status used.
