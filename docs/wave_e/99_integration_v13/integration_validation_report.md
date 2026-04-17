# v1.3 Integration Validation Report

F3 integration pass QA against the frozen E0 schema and the v1.3 integration contract.

All counts re-tallied directly from `canonical/*.yaml`.

## Schema validation

| Check | Result |
|---|---|
| Every Family record has all required fields | ✅ 12/12 |
| Every Family `owning_layer` is a single enum value | ✅ 12/12 |
| Every Family with status ACTIVE has ≥1 ACTIVE atom | ✅ 12/12 |
| Every Atom record has all required fields | ✅ 61/61 |
| Every Atom claim contains exactly one normative verb | ✅ 61/61 |
| Every Atom `family_id` matches Family prefix of atom id | ✅ 61/61 |
| Every NORMATIVE atom cites ≥1 authority source | ✅ 60/60 |
| Every WEAK_EVIDENCE atom cites ≥1 authority source | ✅ n/a (0 in v1.3) |
| Every EXCLUDED atom references an Exclusion record (F12.06 → OOS-001) | ✅ 1/1 |
| Every Edge has all required fields | ✅ 26/26 |
| CONDITIONAL_ON edge has `condition` | ✅ 1/1 (INT-F07.03-F02.01-01) |
| Every SourceAuthorityRecord has valid `subtype`, `authority_class`, and `locator` | ✅ 15/15 |
| Every Exclusion `reason` is from the fixed enum | ✅ 3/3 |

## ID uniqueness

| Check | Result |
|---|---|
| Family IDs unique | ✅ 12 unique |
| Atom IDs unique | ✅ 61 unique |
| Edge IDs unique | ✅ 26 unique |
| Source IDs unique | ✅ 15 unique |
| Exclusion IDs unique | ✅ 3 unique |
| No duplicate (family_id, claim) semantic atoms | ✅ 61 distinct pairs |

## Orphan reference check

| Check | Result |
|---|---|
| Every Atom `family_id` resolves to a Family | ✅ 61/61 |
| Every Edge `source_atom_id` resolves to an Atom | ✅ 26/26 |
| Every Edge `target_atom_id` resolves to an Atom | ✅ 26/26 |
| Every Atom `authority_binding` SRC id resolves to a Source | ✅ all bindings resolve |
| Every Edge `authority_binding` SRC id resolves to a Source | ✅ all bindings resolve |
| Every EXCLUDED atom references a live Exclusion | ✅ F12.06 → OOS-001 |

## Authority-binding discipline

| Check | Result |
|---|---|
| Every NORMATIVE atom cites ≥1 non-ADVISORY source | ✅ 60/60 |
| SRC-ADR-001 (only ADVISORY source) appears in any atom binding | ✅ 0 occurrences |
| Every NORMATIVE atom cites ≥1 ARCHITECTURAL-rank-or-higher source | ✅ 60/60 |
| F04.02 binding | `[SRC-INT-003, SRC-ADR-007]` ✅ |
| F04.03 binding | `[SRC-INT-003, SRC-ADR-007]` ✅ |
| F04.04 binding | `[SRC-INT-003, SRC-ADR-005, SRC-ADR-007]` ✅ |
| F05.04 binding | `[SRC-INT-003, SRC-ADR-008]` ✅ |
| F07.03 binding | `[SRC-INT-003, SRC-ADR-008, SRC-ADR-009]` ✅ |

## Source resolvability (F3-authored)

| SRC | Locator | Resolvable |
|---|---|---|
| SRC-ADR-007 | `docs/architecture/context_assembly_adr.md` | ✅ file exists |
| SRC-ADR-008 | `docs/architecture/l3_orchestration_charter_adr.md` | ✅ file exists |
| SRC-ADR-009 | `docs/architecture/unrecoverable_failure_escalation_adr.md` | ✅ file exists |

All three pre-existing sources (SRC-INT-001..004, SRC-RULE-001..002, SRC-ADR-001..006) pass their v1.2 resolvability checks unchanged.

## Placeholder-ID check

| Check | Result |
|---|---|
| No placeholder SRC IDs (e.g., SRC-TODO, SRC-XXX, SRC-000) | ✅ none found |
| No placeholder atom IDs | ✅ none found |
| No placeholder edge IDs | ✅ none found |

## Counts reconciliation

| Artifact | Count in file | Expected | Match |
|---|---:|---:|---|
| `families.yaml` entries | 12 | 12 | ✅ |
| `atoms.yaml` entries (ACTIVE+EXCLUDED) | 61 (60+1) | 61 | ✅ |
| `edges.yaml` entries | 26 | 26 | ✅ |
| `sources.yaml` entries | 15 | 15 | ✅ |
| `exclusions.yaml` entries | 3 | 3 | ✅ |
| Scorecards in `canonical/scorecards/` | 12 | 12 | ✅ |

## Coverage arithmetic

- ACTIVE NORMATIVE atoms: 60
- ACTIVE WEAK_EVIDENCE atoms: 0
- EXCLUDED atoms: 1 (F12.06, omitted from denominator)
- Coverage = 60 / (60 + 0) = **1.000** GREEN ✅
- Per-family: all 12 at 1.000 — **12 GREEN / 0 YELLOW / 0 RED** ✅

## Edge-specific validation

| Check | Result |
|---|---|
| Every edge endpoint is an atom in canonical YAML (ACTIVE or EXCLUDED) | ✅ 26/26 |
| Every edge cites ≥1 valid source in authority_binding | ✅ 26/26 |
| CONDITIONAL_ON edges carry a `condition` field | ✅ 1/1 |
| No edge has `source_atom_id == target_atom_id` | ✅ 0 self-loops |
| No duplicate (source, target, edge_kind) triples | ✅ 26 unique |

## Sidecar contamination check

| Check | Result |
|---|---|
| No proposal-only `rationale:` fields leaked into F04/F05/F07 canonical atoms | ✅ |
| Pre-existing rationales preserved on F07 family note, F12.05, F12.06, F12.07, F12.08 | ✅ (unchanged from v1.2) |
| Sources retain `notes:` and `excerpt:` per schema (permitted fields) | ✅ |

## Write boundary check

All v1.3 writes are confined to:

- `docs/wave_e/99_integration_v13/canonical/*`
- `docs/wave_e/99_integration_v13/*.md`

No writes to `docs/wave_e/00_schema/`, v1.1, v1.2, or F3 proposal files.

## Exclusion integrity

| Check | Result |
|---|---|
| OOS-001 referenced by F12.06 (EXCLUDED atom) | ✅ |
| OOS-002 referenced in related_atoms (informational) | ✅ |
| OOS-003 present, reason=NOT_YET_DECIDED, revisit_trigger intact | ✅ unchanged from v1.2 |
| No Exclusion is referenced as authority by any ACTIVE atom | ✅ 0 |

## Final verdict

**✅ ALL CHECKS PASS. Canonical v1.3 is publishable.**

All 60 ACTIVE atoms are NORMATIVE. All 12 families are GREEN. Global coverage is 1.000. No schema drift. All prior discipline (ADVISORY containment, claim verbatim, exclusion integrity) preserved.
