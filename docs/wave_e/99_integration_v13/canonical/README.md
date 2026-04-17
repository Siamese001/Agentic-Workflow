# Canonical Requirement Graph v1.3

**Produced at wave:** F3 integration pass
**Predecessor:** `docs/wave_e/99_integration_v12/canonical/` (v1.2)
**Delta source:** `docs/wave_e/F3_final_source_closure/proposals/`
**Schema SSOT:** `docs/wave_e/00_schema/requirement_graph_schema.yaml`

## Counts

| Entity | v1.2 | v1.3 | Delta |
|---|---:|---:|---:|
| Families | 12 | 12 | 0 |
| Atoms (total) | 61 | 61 | 0 |
| Atoms (ACTIVE) | 60 | 60 | 0 |
| Atoms (EXCLUDED) | 1 | 1 | 0 |
| Atoms (NORMATIVE) | 55 | **60** | **+5** |
| Atoms (WEAK_EVIDENCE) | 5 | **0** | **-5** |
| Edges | 26 | 26 | 0 |
| Edges (NORMATIVE) | 18 | 18 | 0 |
| Edges (WEAK_EVIDENCE) | 8 | 8 | 0 |
| Sources | 12 | **15** | **+3** |
| Exclusions | 3 | 3 | 0 |

## Global Coverage

| Metric | v1.2 | v1.3 |
|---|---:|---:|
| Coverage score | 0.917 GREEN | **1.000 GREEN** |
| GREEN families | 9 | **12** |
| YELLOW families | 2 | **0** |
| RED families | 1 | **0** |

All 12 families are GREEN. All 60 ACTIVE atoms are NORMATIVE. The sole EXCLUDED atom (F12.06) is omitted from the coverage denominator per schema.

## What changed in v1.3

1. **3 new SourceAuthorityRecords** registered — SRC-ADR-007 (ADR-CTX-001 Context Assembly Grounding Invariants), SRC-ADR-008 (ADR-L3-001 L3 Orchestration Charter), SRC-ADR-009 (ADR-ESC-001 Unrecoverable Failure Escalation to L3). All three point at real, resolvable repo documents created in Wave F3.
2. **5 WEAK_EVIDENCE atoms upgraded to NORMATIVE**:
   - `F04.02` + SRC-ADR-007 (CTX-I1 attribution invariant)
   - `F04.03` + SRC-ADR-007 (CTX-I2 single-grounded-path invariant)
   - `F04.04` + SRC-ADR-007 (CTX-I3 idempotence invariant) — SRC-ADR-005 retained as supplementary
   - `F05.04` + SRC-ADR-008 (L3-I1 step 2 dispatch invariant)
   - `F07.03` + SRC-ADR-008 (L3-I3 receiving half) + SRC-ADR-009 (ESC-I1 emitting half)
3. **No new families, atoms, edges, or exclusions.**
4. **No atom claim text was modified.** F3's proposal redrafted F04.02's claim; v1.3 preserves the v1.2 claim verbatim per M-v13-02.
5. **OOS-003 unchanged.** Its revisit trigger is satisfied by SRC-ADR-007, but the exclusion state transition is deferred to a later review pass. Logged as DEC-v13-05.
6. **8 WEAK edges unchanged.** F3 proposed no edge patches. Wave F4 produces a cleanup proposal targeting these.
7. **SRC-ADR-001 discipline preserved.** Remains ADVISORY, remains `invalid_for_normative_use=True`, remains absent from every `authority_binding`.
8. **No schema drift.** All 5 patches use only schema-legal fields.

## Bucket flips (v1.2 -> v1.3)

| Family | v1.2 | v1.3 | Notes |
|---|---|---|---|
| F04 | RED 0.25 | **GREEN 1.00** | Two-bucket flip. F04.02/.03/.04 closed. |
| F05 | YELLOW 0.75 | **GREEN 1.00** | F05.04 closed. B6 blocker cleared. |
| F07 | YELLOW 0.75 | **GREEN 1.00** | F07.03 closed via ESC-I1 + L3-I3. |

Unchanged: F01, F02, F03, F06, F08, F09, F10, F11, F12 (all already GREEN in v1.2).

## Remaining blockers

| # | Blocker | Impact | Required action |
|---|---|---|---|
| **D-v12-01** | 8 weak edges still cite only foundational sources | Edge-evidence completeness; coverage score already 1.00 because scoring is atom-based | **Wave F4** (`docs/wave_e/F4_edge_exclusion_cleanup/`) produces a targeted upgrade proposal. |
| **DEC-v13-05** | OOS-003 exclusion still ACTIVE despite satisfied revisit trigger | Exclusion hygiene only; no atom blocked | Wave F4 exclusion review log proposes revision to SUPERSEDED. |
| **B7** | 6 deferred interaction candidates from E1d | Graph completeness | Out of scope for F3 and F4. Each candidate requires a separate HITL-approved wave. |

All three are tracked follow-ups; none prevents v1.3 from being publishable.

## Publishability

**YES — v1.3 is publishable.** Full QA in `../integration_validation_report.md`:

- 0 orphan family, atom, or edge references
- 0 duplicate IDs
- 0 duplicate (family_id, claim) pairs
- 0 atoms supported only by ADVISORY authority
- All 15 sources have real, resolvable locators
- Every ACTIVE NORMATIVE atom cites ≥1 ARCHITECTURAL-rank source
- Every EXCLUDED atom references a real OOS record
- No placeholder SRC IDs
- No writes outside `docs/wave_e/99_integration_v13/`

See also:
- `../coverage_report.md` — delta-oriented coverage analysis
- `../merge_conflicts_register.md` — merge decisions
- `../hitl_decision_ledger.md` — non-trivial HITL decisions
- `../integration_validation_report.md` — full QA output
