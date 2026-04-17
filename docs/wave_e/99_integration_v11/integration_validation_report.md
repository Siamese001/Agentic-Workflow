# F1 Integration — Validation Report (v1.1)

Validation of the v1.1 canonical graph after merging F1 onto v1.

---

## 1. Schema Conformance

| Check | Expected | Result |
|---|---|---|
| Family IDs match `^F[0-9]{2}$` | 12 | ✅ 12/12 |
| Atom IDs match `^F[0-9]{2}\.[0-9]{2}$` | 61 | ✅ 61/61 (inc. F12.07, F12.08) |
| Edge IDs match `^INT-F[0-9]{2}\.[0-9]{2}-F[0-9]{2}\.[0-9]{2}-[0-9]{2}$` | 26 | ✅ 26/26 |
| SRC IDs match regex | 6 | ✅ 6/6 (inc. SRC-INT-004) |
| OOS IDs match regex | 3 | ✅ |
| Scorecard IDs match regex | 12 | ✅ |

## 2. Orphan / Reference Integrity

| Check | Result |
|---|---|
| Every atom.family_id resolves | ✅ 61/61 |
| Every edge endpoint resolves | ✅ 52/52 (26 × 2) |
| Every authority_binding SRC resolves | ✅ All bindings reference the 6 canonical sources |
| F12.06 EXCLUDED references real OOS | ✅ OOS-001 |
| No ACTIVE edge targets EXCLUDED or UNRESOLVED atom | ✅ F12.06 still isolated |

## 3. Duplicate / Uniqueness

| Check | Result |
|---|---|
| No duplicate IDs across graph | ✅ 12+61+26+6+3+12 = 120 unique IDs |
| No duplicate `(family_id, claim)` pairs | ✅ 61 distinct claims |
| No duplicate `(source, target, edge_kind)` triples | ✅ 26 distinct; `INT-F12.07-F02.01-01 REQUIRES` is distinct from `INT-F12.05-F02.01-01 DEPENDS_ON` because edge_kind differs |

## 4. Status / Evidence Rules

| Check | Result |
|---|---|
| Every NORMATIVE atom has ≥1 binding | ✅ 45/45 |
| Every WEAK_EVIDENCE atom has ≥1 binding | ✅ 13/13 |
| Every EXCLUDED atom has empty binding | ✅ F12.06 = [] |
| No ACTIVE atom without binding + owning_layer | ✅ 60/60 |
| No NORMATIVE atom cites rank > 4 | ✅ Highest rank used is 4 (ARCHITECTURAL via SRC-INT-003) |
| Every ACTIVE family has ≥1 ACTIVE atom | ✅ 12/12 |

## 5. Placeholder SRC Cleansing

| Check | Result |
|---|---|
| No `SRC-ADR-L*` references | ✅ Zero |
| No `SRC-ADR-WG` references | ✅ Zero |
| No `SRC-ADR-EXIT` references | ✅ Zero |

## 6. Edge-Specific Rules

| Check | Result |
|---|---|
| CONDITIONAL_ON edge has non-empty `condition` | ✅ INT-F07.03-F02.01-01 condition present |
| No BIDIRECTIONAL edges outside {CONFLICTS_WITH, CO_REQUIRES} | ✅ Zero BIDIRECTIONAL |
| No self-loop edges | ✅ |
| New F1 edges endpoints all resolve | ✅ F12.05/.07/.08 and F02.01/F08.03 all ACTIVE |

## 7. Scorecard Arithmetic

| Check | Result |
|---|---|
| atom_count_total == sum(atom_count_by_status) | ✅ 12/12 |
| atom_count_total == sum(atom_count_by_evidence) | ✅ 12/12 |
| edge_count_total == sum(edge_count_by_kind) | ✅ 12/12 |
| coverage_score in [0.0, 1.0] | ✅ Range 0.20–1.00 |
| Global score NOT rounded up | ✅ 0.776 (actual 0.77586...) |

## 8. F1 Delta Validation

| Expected F1 outcome | Observed in v1.1 |
|---|---|
| F12.05 patch WEAK → NORMATIVE | ✅ |
| F12.07 added as ACTIVE NORMATIVE | ✅ |
| F12.08 added as ACTIVE NORMATIVE | ✅ |
| 3 new F1 edges merged cleanly | ✅ INT-F12.05-F12.07-01, INT-F12.07-F02.01-01, INT-F12.08-F08.03-01 |
| F04 remains RED (0.25) | ✅ No fake closure |
| F07 remains RED (0.25) | ✅ No fake closure |
| F08 remains RED (0.20) | ✅ No fake closure |
| Deferred C1/C2/C3/C4/C6/C9 stay deferred | ✅ No edges or atoms added for them |
| No new family IDs minted | ✅ |
| No new schema fields/enums/ID formats | ✅ |

## 9. Sidecar Isolation

| Check | Result |
|---|---|
| No sidecar markdown in canonical YAML fields | ✅ Only `rationale`/`notes` (schema-defined) appear |
| No criticality/failure-mode/test-priority fields | ✅ |

## 10. Write-Scope Enforcement

| Check | Result |
|---|---|
| All writes confined to `docs/wave_e/99_integration_v11/` | ✅ 16 files, all under v1.1 dir |
| No writes to `docs/wave_e/00_schema/` | ✅ |
| No writes to `docs/wave_e/99_integration/` (v1) | ✅ |
| No writes to `docs/wave_e/F1_red_source_closure/` | ✅ |

## Summary

**All 10 check categories PASSED.** Canonical v1.1 is schema-valid, internally consistent, and ready for publication. Three RED families persist as documented blockers for Wave F+.
