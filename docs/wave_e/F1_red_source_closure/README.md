# Wave F1 — Red-Family and Weak-Source Closure

**Lane ID:** `F1_red_source_closure`
**Scope:** Bounded closure of known red/weak gaps from canonical v1. No redesign. No new families. No new schema fields.
**Schema SSOT:** `docs/wave_e/00_schema/requirement_graph_schema.yaml`

## Deliverables

- `proposals/sources.yaml` — **1** new source (`SRC-INT-004` AGENTS.md Memory Lifecycle section anchor).
- `proposals/atoms.yaml` — **3** atom records: 1 patch (F12.05) + 2 new (F12.07, F12.08). All DRAFT, all NORMATIVE.
- `proposals/edges.yaml` — **3** new edges (REFINES, REQUIRES, DEPENDS_ON).
- `proposals/families.yaml`, `proposals/exclusions.yaml` — schema-valid empty lists.
- `scorecards/SCORE-F12-F1.yaml` — projected post-F1 F12 scorecard.
- `source_gap_closure_log.md` — honest per-gap closure record.
- `interaction_candidate_disposition.md` — 9 deferred candidates evaluated; 1 closed (C5), 6 deferred, 2 no-action.
- `family_delta_summary.md` — per-family projected delta.

## ID Allocations Recorded

Appended to `docs/wave_e/00_schema/id_allocations.log`:
- F12 atoms 07-08
- SRC-INT-004

## 1. Source Gaps Closed

**1 gap closed** (F12.05 future-run consumption mechanism).
**10 gaps deferred** across F04 (3), F07 (3), F08 (4), F01 (1), F03 (1), F05 (1) — minus F08.02 which was already NORMATIVE.

Full table in `source_gap_closure_log.md §Summary Counts`.

## 2. Atoms Added or Patched

| Atom | Action | evidence_class | Status |
|---|---|---|---|
| F12.05 | PATCH | WEAK_EVIDENCE → NORMATIVE | DRAFT |
| F12.07 | NEW | NORMATIVE | DRAFT |
| F12.08 | NEW | NORMATIVE | DRAFT |

**Total: 3 atoms touched.** All contributions are NORMATIVE grounded in real SRC-RULE-001 (constitutional §17) + SRC-INT-001 + new SRC-INT-004.

## 3. Edges Added

**3 new edges:**
- `INT-F12.05-F12.07-01` REFINES
- `INT-F12.07-F02.01-01` REQUIRES
- `INT-F12.08-F08.03-01` DEPENDS_ON (WEAK_EVIDENCE — inherits F08.03)

## 4. F04 / F07 / F08 Material Improvement

| Family | Before F1 | After F1 | Material improvement? |
|---|---:|---:|:---:|
| **F04** | 0.25 RED | 0.25 RED | **NO** — no real source available |
| **F07** | 0.25 RED | 0.25 RED | **NO** — candidate F11.08 rejected (net-negative) |
| **F08** | 0.20 RED | 0.20 RED | **NO** — exit-spine source cannot be fabricated |

All three RED families remain RED. F1 documented honest reasons rather than inflating coverage with fake sources.

## 5. Weak Atoms Remaining and Why

| Atom | Family | Class | Why still weak |
|---|---|---|---|
| F01.06 | F01 | WEAK | No structured-rejection-code rule exists |
| F03.04 | F03 | WEAK | One-route-per-step determinism implicit, not canonicalized |
| F04.02 | F04 | WEAK | Context attribution has no dedicated ADR/rule |
| F04.03 | F04 | WEAK | No-private-context-substitute has no dedicated source |
| F04.04 | F04 | WEAK | Idempotence claim unsourced |
| F05.04 | F05 | WEAK | L3-dispatch-to-L2 implicit from layer separation |
| F07.01 | F07 | WEAK | Bounded-heal-path has no dedicated source |
| F07.02 | F07 | WEAK | Bounded-retry has no dedicated source |
| F07.03 | F07 | WEAK | Surface-to-L3 escalation inferred only |
| F08.01 | F08 | WEAK | Evaluation-spine concept unsourced |
| F08.03 | F08 | WEAK | Outcome-recording unsourced |
| F08.04 | F08 | WEAK | Spine-signals-gate unsourced |
| F08.05 | F08 | WEAK | No-ad-hoc-exit unsourced (E1c downgrade) |
| F09.05 | F09 | WEAK | Gate rejects missing exit signal (inherits F08 weakness) |

**13 WEAK_EVIDENCE atoms remain** (down from 15 after F12.05 patch and the deleted F12.05-WEAK entry).

## 6. Exact Blockers Requiring Later Waves

| # | Blocker | Family impact | Recommended action | Owner |
|---|---|---|---|---|
| **B1** | **Exit Spine ADR missing** | F08 stays at 0.20 RED; blocks F09.05 upgrade | Author an ADR for the runtime exit evaluation spine with explicit invariants (single path, record outcome, signal gate, no ad-hoc exits). Requires HITL approval to attain ARCHITECTURAL rank. | Wave F2 or a targeted governance wave |
| B2 | Bounded-retry rule | F07 stays at 0.25 RED | Author an operational rule or governance ADR for bounded L2 retry (attempt count, duration, backoff). | Wave F2 |
| B3 | Context assembly design doc | F04 stays at 0.25 RED | Author an ADR specifying context attribution, idempotence, and no-private-substitute. Also resolves OOS-003 revisit trigger. | Wave F2 or F3 |
| B4 | Structured rejection reason-code standard | F01.06 stays WEAK | Short ADR enumerating rejection codes. Low effort. | Wave F2 (trivial) |
| B5 | One-route-per-step determinism rule | F03.04 stays WEAK | Short ADR on L0 route selection determinism. | Wave F2 (trivial) |
| B6 | L3 dispatch specification | F05.04 stays WEAK | L3 orchestration charter ADR. | Wave F2 |
| B7 | 6 deferred interaction candidates (C1, C2, C3, C4, C6, C9) | Graph edge coverage incomplete | Most require downstream atom designs not yet in scope. | Wave F3+ |

## Ready for Integration?

**YES** — for a canonical v1.1 patch. F1's output is schema-valid, bounded, and honestly constrained.

**Projected canonical v1.1 state:**
- Global coverage: 0.776 **YELLOW** (was 0.741 RED in v1 — bucket flips RED → YELLOW).
- F12: 1.00 GREEN.
- F04 / F07 / F08: unchanged RED.
- Green families: 5 (F02, F06, F10, F11, **F12**).
- Yellow families: 4 (F01, F03, F05, F09).
- Red families: 3 (F04, F07, F08) — unchanged.

## Validation Self-Check

- [x] All new atom IDs match `^F[0-9]{2}\.[0-9]{2}$` (F12.07, F12.08).
- [x] F12.05 patched (same ID; last-writer-wins per E1c/integration precedent).
- [x] All 3 new edges match `^INT-F[0-9]{2}\.[0-9]{2}-F[0-9]{2}\.[0-9]{2}-[0-9]{2}$`.
- [x] No edge has source_atom_id == target_atom_id.
- [x] SRC-INT-004 matches `^SRC-(INT|EXT|ADR|RULE|CODE|DEC)-[0-9]{3}$`.
- [x] SRC-INT-004 locator (`AGENTS.md#memory-lifecycle`) resolves in-repo.
- [x] All NORMATIVE atoms cite rank ≤ ARCHITECTURAL sources.
- [x] No atom or edge has status ACTIVE.
- [x] No new Family IDs minted.
- [x] No writes outside `docs/wave_e/F1_red_source_closure/` except id_allocations.log (explicit append-only log defined by the schema).
- [x] No canonical v1 files modified.
- [x] No exclusion records changed (OOS-003 intact).
