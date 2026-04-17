# Wave E1 Integration — Validation Report

Every QA check required by the integration contract, with result.

---

## 1. Schema Conformance

| Check | Expected | Result |
|---|---|---|
| All Family IDs match `^F[0-9]{2}$` | 12 match | ✅ 12/12 |
| All Atom IDs match `^F[0-9]{2}\.[0-9]{2}$` | 59 match | ✅ 59/59 |
| All Edge IDs match `^INT-F[0-9]{2}\.[0-9]{2}-F[0-9]{2}\.[0-9]{2}-[0-9]{2}$` | 23 match | ✅ 23/23 |
| All SRC IDs match `^SRC-(INT\|EXT\|ADR\|RULE\|CODE\|DEC)-[0-9]{3}$` | 5 match | ✅ 5/5 |
| All OOS IDs match `^OOS-[0-9]{3}$` | 3 match | ✅ 3/3 |
| All Scorecard IDs match `^SCORE-F[0-9]{2}-(E[0-9]+[a-z]?\|INTEGRATION)$` | 12 match | ✅ 12/12 |

## 2. Orphan / Reference Integrity

| Check | Result |
|---|---|
| No orphan family references (atom.family_id resolves) | ✅ 59/59 resolve |
| No orphan atom references (edge endpoints resolve) | ✅ 46/46 (23 × 2 endpoints) resolve |
| No orphan edge endpoints | ✅ |
| No orphan authority_binding (every SRC ID resolves) | ✅ All bindings resolve to the 5 canonical sources |
| Every EXCLUDED atom references a real OOS-* record | ✅ F12.06 → OOS-001 (exists) |
| No ACTIVE edge targets an EXCLUDED or UNRESOLVED atom | ✅ F12.06 is isolated from edges |
| Every superseded/superseded_by cross-reference resolves | ✅ N/A (no supersedes chains in canonical after self-reference drops) |

## 3. Duplicate / Uniqueness

| Check | Result |
|---|---|
| No duplicate IDs across entire graph | ✅ 59+23+5+3+12 = 102 unique IDs |
| No duplicate `(family_id, claim)` atom pairs | ✅ Verified 59 distinct claims |
| No duplicate `(source, target, edge_kind)` edge triples | ✅ 23 distinct triples |

## 4. Status / Evidence Rules

| Check | Result |
|---|---|
| Every NORMATIVE atom has ≥1 authority_binding | ✅ 43/43 |
| Every WEAK_EVIDENCE atom has ≥1 authority_binding | ✅ 15/15 |
| Every EXCLUDED atom has empty authority_binding (no requirement) | ✅ F12.06 = [] |
| Every EXCLUDED atom references an OOS in rationale | ✅ F12.06 rationale: "Excluded per OOS-001." |
| No atom has status ACTIVE without authority_binding + owning_layer | ✅ 58 ACTIVE all compliant |
| No atom has evidence_class NORMATIVE with authority rank > 4 | ✅ All NORMATIVE bindings cite SRC-RULE-001 (rank 1) or SRC-INT-003 (rank 4) or rank-2 INT sources (all ≤ 4) |
| Every ACTIVE family has ≥1 ACTIVE atom | ✅ 12/12 |
| No family spans two authority_class values | ✅ Each family has single authority_class |

## 5. Placeholder SRC Cleansing

| Check | Result |
|---|---|
| No `SRC-ADR-L0..L6` references remain in canonical atoms.yaml | ✅ Zero hits |
| No `SRC-ADR-WG` references remain | ✅ Zero hits |
| No `SRC-ADR-EXIT` references remain | ✅ Zero hits |
| No `SRC-ADR-*` references remain in canonical edges.yaml | ✅ Zero hits |

## 6. Edge-Specific Rules

| Check | Result |
|---|---|
| Every CONDITIONAL_ON edge has non-empty `condition` | ✅ INT-F07.03-F02.01-01 has "Unrecoverable L2 task failure detected." |
| No BIDIRECTIONAL edge with edge_kind outside {CONFLICTS_WITH, CO_REQUIRES} | ✅ No BIDIRECTIONAL edges used |
| No CONFLICTS_WITH edge with both endpoints ACTIVE | ✅ No CONFLICTS_WITH edges used |
| No edge has source_atom_id == target_atom_id | ✅ |

## 7. Scorecard Arithmetic

| Check | Result |
|---|---|
| For each scorecard: atom_count_total == sum(atom_count_by_status) | ✅ 12/12 |
| For each scorecard: atom_count_total == sum(atom_count_by_evidence) | ✅ 12/12 |
| For each scorecard: edge_count_total == sum(edge_count_by_kind) | ✅ 12/12 |
| coverage_score in [0.0, 1.0] for every scorecard | ✅ Range observed: 0.20 to 1.00 |
| Global score NOT rounded up despite blockers present | ✅ 0.74 reported, not 0.75 |

## 8. Sidecar Isolation

| Check | Result |
|---|---|
| No sidecar markdown content copied into canonical YAML schema fields | ✅ Canonical YAMLs contain only schema-defined fields (+ `notes` where schema allows) |
| No criticality / failure-mode / test-priority fields in edges.yaml | ✅ (those live in E1d sidecars only) |

## 9. Integration Pass Scope

| Check | Result |
|---|---|
| No new Family IDs minted | ✅ F01..F12 only |
| No new Atom IDs minted | ✅ F01.01..F12.06 only, matches E1b ranges |
| No write to `docs/wave_e/00_schema/` (except existing log reservations done by sub-waves) | ✅ Integration pass did not touch 00_schema/ |
| All writes confined to `docs/wave_e/99_integration/` | ✅ |

## 10. HITL Ledger Coverage

| Check | Result |
|---|---|
| Every non-trivial merge decision logged in `hitl_decision_ledger.md` | ✅ 10 decisions (HITL-INT-001..010) |
| Every merge conflict resolved in `merge_conflicts_register.md` | ✅ 10 register entries (MC-01..10) |

## Summary

**All 10 check categories PASSED.** Canonical v1 is schema-valid, internally consistent, and ready for publication. The only remaining flag is the RED global coverage score (0.74), which reflects documented gaps in ARCHITECTURAL sources, not structural defects.
