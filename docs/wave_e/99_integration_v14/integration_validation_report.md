# v1.4 Integration Validation Report

F4 integration pass QA against the frozen E0 schema and the v1.4 integration contract.

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
| Every WEAK_EVIDENCE atom cites ≥1 authority source | ✅ n/a (0 WEAK) |
| Every EXCLUDED atom references an Exclusion record (F12.06 → OOS-001) | ✅ 1/1 |
| Every Edge has all required fields | ✅ 26/26 |
| CONDITIONAL_ON edge has `condition` | ✅ 1/1 (INT-F07.03-F02.01-01) |
| Every SourceAuthorityRecord has valid `subtype`, `authority_class`, and `locator` | ✅ 15/15 |
| Every Exclusion `reason` is from the fixed enum | ✅ 3/3 (OOS-003 now SUPERSEDED — valid) |

## ID uniqueness

| Check | Result |
|---|---|
| Family IDs unique | ✅ 12 unique |
| Atom IDs unique | ✅ 61 unique |
| Edge IDs unique | ✅ 26 unique |
| Source IDs unique | ✅ 15 unique |
| Exclusion IDs unique | ✅ 3 unique |
| No duplicate (family_id, claim) semantic atoms | ✅ 61 distinct pairs |
| No duplicate (source, target, edge_kind) edge triples | ✅ 26 unique |

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
| Every NORMATIVE edge cites ≥1 valid source | ✅ 26/26 |
| SRC-ADR-001 (only ADVISORY source) appears in any atom or edge binding | ✅ 0 occurrences |
| Every NORMATIVE atom cites ≥1 ARCHITECTURAL-rank-or-higher source | ✅ 60/60 |
| No ACTIVE atom cites any Exclusion as authority | ✅ 0 violations |

## Edge upgrade validation (F4 delta)

| Edge | v1.4 evidence | Direct-support source(s) | Verified |
|---|---|---|---|
| INT-F02.01-F01.05-01 | NORMATIVE | F01.05 claim + SRC-RULE-001 + SRC-INT-001 + SRC-INT-003 | ✅ |
| INT-F05.04-F06.01-01 | NORMATIVE | SRC-ADR-008 L3-I1 step 2 | ✅ |
| INT-F07.03-F02.01-01 | NORMATIVE | SRC-ADR-008 L3-I3 + SRC-ADR-009 ESC-I1 | ✅ |
| INT-F07.03-F05.01-01 | NORMATIVE | SRC-ADR-008 L3-I3 + SRC-ADR-009 ESC-I1 | ✅ |
| INT-F08.04-F09.01-01 | NORMATIVE | F08.04 claim + SRC-ADR-003 GovernedHandoffAgent | ✅ |
| INT-F09.05-F08.04-01 | NORMATIVE | F09.05 claim + SRC-ADR-003 evaluate_sealed() | ✅ |
| INT-F12.05-F02.01-01 | NORMATIVE | F12.05 claim + SRC-RULE-001 §17 + SRC-INT-004 | ✅ |
| INT-F12.08-F08.03-01 | NORMATIVE | F12.08 claim + SRC-ADR-003 + SRC-INT-004 | ✅ |

## Exclusion revision validation

| Check | Result |
|---|---|
| OOS-003 `reason` value after revision | `SUPERSEDED` (valid enum member) ✅ |
| Schema-required fields all present | ✅ id, title, scope_statement, reason, decided_at_wave, decided_by, related_atoms, related_families |
| `scope_statement` preserved verbatim from v1.3 | ✅ |
| `related_atoms` / `related_families` preserved | ✅ |
| Supersession source cited in `notes` | ✅ (SRC-ADR-007) |
| No ACTIVE atom cites OOS-003 in `authority_binding` | ✅ 0 occurrences |
| OOS-001 unchanged | ✅ |
| OOS-002 unchanged | ✅ |

## Source resolvability (unchanged from v1.3)

All 15 sources retain their v1.3 locators and `authority_class` values. The three F3-authored locators (`docs/architecture/context_assembly_adr.md`, `l3_orchestration_charter_adr.md`, `unrecoverable_failure_escalation_adr.md`) remain resolvable on disk.

## Placeholder-ID check

| Check | Result |
|---|---|
| No placeholder SRC IDs | ✅ none found |
| No placeholder atom IDs | ✅ none found |
| No placeholder edge IDs | ✅ none found |
| No placeholder OOS IDs | ✅ none found |

## Counts reconciliation

| Artifact | Count in file | Expected | Match |
|---|---:|---:|---|
| `families.yaml` entries | 12 | 12 | ✅ |
| `atoms.yaml` entries (ACTIVE+EXCLUDED) | 61 (60+1) | 61 | ✅ |
| `edges.yaml` entries | 26 | 26 | ✅ |
| NORMATIVE edges | 26 | 26 | ✅ |
| WEAK_EVIDENCE edges | 0 | 0 | ✅ |
| `sources.yaml` entries | 15 | 15 | ✅ |
| `exclusions.yaml` entries | 3 | 3 | ✅ |
| Scorecards in `canonical/scorecards/` | 12 | 12 | ✅ |

## Coverage arithmetic

- ACTIVE NORMATIVE atoms: 60
- ACTIVE WEAK_EVIDENCE atoms: 0
- EXCLUDED atoms: 1 (F12.06, omitted from denominator)
- **Atom coverage = 60 / 60 = 1.000 GREEN** ✅
- NORMATIVE edges: 26
- WEAK_EVIDENCE edges: 0
- **Edge coverage = 26 / 26 = 1.000** ✅
- Per-family atom coverage: all 12 at 1.000 — **12 GREEN / 0 YELLOW / 0 RED** ✅

## Sidecar contamination check

| Check | Result |
|---|---|
| F4 proposal-only `rationale:` fields leaked into canonical `edges.yaml` | ✅ rejected (M-v14-05) |
| Pre-existing atom rationales preserved (F07 family note, F12.05/.06/.07/.08) | ✅ unchanged from v1.3 |
| `notes:` on OOS-003 added per F4 proposal (schema-permitted) | ✅ |

## Write boundary check

All v1.4 writes are confined to:

- `docs/wave_e/99_integration_v14/canonical/*`
- `docs/wave_e/99_integration_v14/*.md`

No writes to `docs/wave_e/00_schema/`, v1.1–v1.3, F3 / F4 proposal files, or anywhere else.

## Over-eagerness guard (rules 4–5)

Confirmed for each edge upgrade: the cited sources directly state the edge claim, not merely support endpoint atoms. No endpoint-only upgrades. See `merge_conflicts_register.md` §"Over-eagerness check" and `hitl_decision_ledger.md` DEC-v14-01.

## Fabrication guard (rule 8)

No new atoms, families, sources, or interactions were introduced by the integration pass. All content originates in F4 proposals or v1.3 canonical.

## Final verdict

**✅ ALL CHECKS PASS. Canonical v1.4 is publishable.**

All 60 ACTIVE atoms are NORMATIVE. All 26 edges are NORMATIVE. OOS-003 revision is schema-valid and reason-justified. No schema drift. All prior discipline preserved (ADVISORY containment, claim verbatim, exclusion integrity, no-downgrades).
