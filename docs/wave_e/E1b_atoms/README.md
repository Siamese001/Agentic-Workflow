# Wave E1b — Requirement Atom Decomposition

**Lane ID:** `E1b_atoms`
**Scope:** Decompose F01..F12 into single-claim RequirementAtom records. No new Family IDs. No source registry work. No interaction edges.
**Schema SSOT:** `docs/wave_e/00_schema/requirement_graph_schema.yaml`

## Deliverables

- `proposals/atoms.yaml` — **59** DRAFT RequirementAtom records across F01..F12.
- `proposals/exclusions.yaml` — **1** OOS record (`OOS-001`) referenced by the single `EXCLUDED` atom (F12.06).
- `proposals/families.yaml`, `proposals/edges.yaml`, `proposals/sources.yaml` — schema-valid empty lists (not E1b scope).
- `scorecards/SCORE-F<NN>-E1b.yaml` — 12 scorecards (one per family).
- `compound_to_atomic_splits.md` — per-family bundling-to-atom map.
- `high_risk_atoms.md` — HIGH/MEDIUM/LOW risk flags at the atom level.

## ID Allocations Recorded

Appended to `docs/wave_e/00_schema/id_allocations.log`:
- Atom ranges for F01..F12 (all contiguous, starting at `01`).
- `OOS-001` reservation.

## Total Atom Count

**59** atoms, all `status: DRAFT` (+ 1 `EXCLUDED`).

## Counts by Family

| Family | Atoms | NORMATIVE | WEAK_EVIDENCE | UNRESOLVED | EXCLUDED | coverage_score |
|---|---:|---:|---:|---:|---:|---:|
| F01 Request Intake | 6 | 5 | 1 | 0 | 0 | 0.83 |
| F02 L1 Reasoning   | 5 | 5 | 0 | 0 | 0 | 1.00 |
| F03 L0 Route       | 4 | 3 | 1 | 0 | 0 | 0.75 |
| F04 Context        | 4 | 0 | 2 | 2 | 0 | 0.00 |
| F05 L3 Orchestration | 4 | 3 | 1 | 0 | 0 | 0.75 |
| F06 L2 Execution   | 5 | 5 | 0 | 0 | 0 | 1.00 |
| F07 L2 Heal/Retry  | 4 | 1 | 3 | 0 | 0 | 0.25 |
| F08 Exit Spine     | 5 | 2 | 3 | 0 | 0 | 0.40 |
| F09 Write Gate     | 5 | 4 | 1 | 0 | 0 | 0.80 |
| F10 L4 State       | 4 | 4 | 0 | 0 | 0 | 1.00 |
| F11 L5 Policy      | 7 | 7 | 0 | 0 | 0 | 1.00 |
| F12 L6 Learning    | 6 | 4 | 1 | 0 | 1 | 0.80 |
| **TOTAL**          | **59** | **43** | **13** | **2** | **1** | — |

## Top Families by Atom Count

1. **F11 L5 Policy** — 7 atoms (fan-out family; binds 4 other families)
2. **F01 Request Intake** — 6 atoms (bundled intake + envelope check)
3. **F12 L6 Learning** — 6 atoms (observe + no-influence + future-feed + 1 EXCLUDED)
4. F02, F06, F08, F09 — 5 atoms each
5. F03, F04, F05, F07, F10 — 4 atoms each

## Top Atoms Still Too Broad

E1b applied the one-claim rule aggressively. The atoms most likely to be split further (by E1d or integration pass) are:

- **F09.04 and F09.05** — two "gate rejects on missing signal" atoms. Could consolidate into one "gate rejects on missing admission signal" atom with edges to F08 and F11, or stay as-is. Marked LOW; decision is at integration.
- **F11.02..F11.05** — four "L5 binds X" atoms. Sound as atoms, but E1d will author the corresponding edges; integration may consolidate if redundant.
- **F12.02** — "L6 observations MUST NOT influence current-run decisions". Arguably two claims (route decisions + state mutations), but split into F12.02 + F12.03 already; no further split needed.

No atom contains more than one normative verb. No atom bundles two independent normative claims on inspection.

## Blockers Preventing Integration Readiness

| # | Blocker | Owner | Scope |
|---|---|---|---|
| B1 | All `SRC-*` IDs in `authority_binding` are placeholders. E1c MUST materialize them in `docs/wave_e/E1c_authority_scope/proposals/sources.yaml`. | E1c | 43 NORMATIVE + 13 WEAK_EVIDENCE atoms reference SRC-* IDs. Without materialization, integration-pass validation ("all cross-references resolve") FAILS. |
| B2 | F04 owning_layer is provisional `L1`; 2 atoms marked UNRESOLVED. | E1c | Blocks F04 reaching any coverage_score > 0. |
| B3 | F01 / F08 / F09 provisional `owning_layer` (carryover from E1a). | E1c | Does not block start; integration would accept provisional layers with a WARNING. |
| B4 | CONSTITUTIONAL authority_class on F02, F03, F09, F10, F11, F12 requires rank-1 source cite. | E1c | Downgrade to GOVERNANCE if no rank-1 source. |
| B5 | No interaction edges published. Many NORMATIVE claims imply required edges (F01→F11, F09→F11, F09→F08, F06→F09, etc.). | E1d | Expected; E1d is the edge-drafting lane. Integration cannot validate cross-family implications until E1d publishes. |
| B6 | `OOS-001` authored by E1b. If E1c independently authors an equivalent exclusion, integration pass must de-duplicate. | Integration | Minor; noted in `high_risk_atoms.md`. |

## proposed_new_family

None. All 59 atoms fit within F01..F12. E1b identified no concern that required a new family.

## Validation Self-Check (against schema rules)

- [x] Every atom ID matches regex `^F[0-9]{2}\.[0-9]{2}$`.
- [x] Every atom's `family_id` equals its ID prefix.
- [x] Every `claim` contains exactly one normative verb (MUST / MUST NOT / FORBIDDEN / SHALL variants).
- [x] Every `NORMATIVE` and `WEAK_EVIDENCE` atom has `authority_binding` length ≥ 1.
- [x] Every `EXCLUDED` atom references an OOS id in `rationale` (F12.06 -> OOS-001).
- [x] Every `UNRESOLVED` atom has status `UNRESOLVED`.
- [x] No atom has status `ACTIVE` (contract compliance).
- [x] No duplicate atom IDs.
- [x] No duplicate `(family_id, claim)` pairs.

## Ready for Integration?

**NO — intentionally.** E1b's output is an input to E1c (source materialization) and E1d (edges). Integration pass requires both E1c and E1d output. E1b is READY for E1c and E1d to proceed; all atom IDs they need are now minted and published.

## Cross-Lane Notes

- **To E1c:** The `SRC-*` placeholder list is documented at the top of `proposals/atoms.yaml`. Materialize all of them; any unmaterialized placeholder at integration time FAILS validation.
- **To E1d:** You have 59 atom IDs to build edges against. Expected edge targets:
  - F06.05 → F09 atoms (write gate)
  - F01.03 → F11 atoms (policy precondition)
  - F09.* → F11 atoms + F08 atoms
  - F08 → F09 + F11
  - F12.02/F12.03 → F03, F09, F11 (the negative edges encoding "L6 MUST NOT influence")
  - F02/F05/F06 → F01/F03 (dispatch chain)
