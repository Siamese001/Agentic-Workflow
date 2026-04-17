# Canonical Requirement Graph v1.4

**Produced at wave:** F4 integration pass
**Predecessor:** `docs/wave_e/99_integration_v13/canonical/` (v1.3)
**Delta source:** `docs/wave_e/F4_edge_exclusion_cleanup/proposals/`
**Schema SSOT:** `docs/wave_e/00_schema/requirement_graph_schema.yaml`

## Counts

| Entity | v1.3 | v1.4 | Delta |
|---|---:|---:|---:|
| Families | 12 | 12 | 0 |
| Atoms (total) | 61 | 61 | 0 |
| Atoms (ACTIVE) | 60 | 60 | 0 |
| Atoms (EXCLUDED) | 1 | 1 | 0 |
| Atoms (NORMATIVE) | 60 | 60 | 0 |
| Atoms (WEAK_EVIDENCE) | 0 | 0 | 0 |
| Edges | 26 | 26 | 0 |
| Edges (NORMATIVE) | 18 | **26** | **+8** |
| Edges (WEAK_EVIDENCE) | 8 | **0** | **-8** |
| Sources | 15 | 15 | 0 |
| Exclusions | 3 | 3 | 0 |

## Global Coverage

| Metric | v1.3 | v1.4 |
|---|---:|---:|
| Atom coverage score | 1.000 GREEN | **1.000 GREEN** |
| Edge coverage score | 0.692 (18/26) | **1.000** (26/26) |
| GREEN families | 12 | **12** |

All 60 ACTIVE atoms are NORMATIVE; all 26 edges are NORMATIVE. F12.06 (EXCLUDED) is the sole non-NORMATIVE record and is omitted from the coverage denominator per schema.

## What changed in v1.4

1. **8 edge evidence upgrades** (WEAK_EVIDENCE → NORMATIVE), per F4 `proposals/edges.yaml`:
   - `INT-F02.01-F01.05-01` → `[SRC-RULE-001, SRC-INT-001, SRC-INT-003]`
   - `INT-F05.04-F06.01-01` → `[SRC-INT-003, SRC-ADR-008]`
   - `INT-F07.03-F02.01-01` → `[SRC-INT-003, SRC-ADR-008, SRC-ADR-009]` (condition preserved)
   - `INT-F07.03-F05.01-01` → `[SRC-INT-003, SRC-ADR-008, SRC-ADR-009]`
   - `INT-F08.04-F09.01-01` → `[SRC-INT-003, SRC-ADR-003]`
   - `INT-F09.05-F08.04-01` → `[SRC-INT-003, SRC-ADR-003]`
   - `INT-F12.05-F02.01-01` → `[SRC-RULE-001, SRC-INT-001, SRC-INT-004]`
   - `INT-F12.08-F08.03-01` → `[SRC-INT-004, SRC-ADR-003]`
2. **OOS-003 revised**: `reason: NOT_YET_DECIDED → SUPERSEDED`, `decided_at_wave: E1c → F4`, `revisit_trigger` rewritten to cite SRC-ADR-007 as supersession source. `scope_statement`, `related_atoms`, `related_families` preserved verbatim.
3. **No atom patches.** F4 scope forbade reopening closed atoms. All 60 ACTIVE atoms carry forward verbatim.
4. **No new families, sources, or exclusions.** F4 authored none.
5. **OOS-001 and OOS-002 unchanged.**
6. **SRC-ADR-001 discipline preserved.** Remains ADVISORY, remains unbound.
7. **No schema drift.** All 8 edge patches use only schema-legal fields and enum values.

## Bucket flips (v1.3 → v1.4)

None at the family level — all 12 were already GREEN in v1.3. The v1.4 delta is edge-evidence only.

## Remaining blockers

| # | Blocker | Status |
|---|---|---|
| **B7** | 6 deferred interaction candidates from E1d | **Only remaining open item.** Requires new atoms or edges with explicit HITL approval. Out of scope for v1.4. |
| D-v12-01 | Weak-edge upgrade pass | **CLOSED** by this integration pass. |
| DEC-v13-05 | OOS-003 state transition | **CLOSED** by this integration pass. |

## Publishability

**YES — v1.4 is publishable.** QA in `../integration_validation_report.md`:

- 0 orphan family, atom, or edge references
- 0 duplicate IDs
- 0 duplicate `(family_id, claim)` pairs
- 0 atoms supported only by ADVISORY authority
- 0 ACTIVE atoms citing any Exclusion as authority
- 0 edges with missing authority_binding
- All 15 sources have real, resolvable locators (unchanged from v1.3)
- Every ACTIVE NORMATIVE atom and every edge cites ≥1 non-ADVISORY source
- EXCLUDED atom (F12.06) references OOS-001 via rationale
- OOS-003 `reason` is schema-valid (SUPERSEDED ∈ enum)
- No placeholder SRC IDs
- No writes outside `docs/wave_e/99_integration_v14/`

See also:
- `../coverage_report.md` — delta-oriented coverage analysis
- `../merge_conflicts_register.md` — merge decisions
- `../hitl_decision_ledger.md` — non-trivial HITL decisions
- `../integration_validation_report.md` — full QA output
