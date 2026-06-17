# v1.2 Integration Validation Report

Full QA output after merging F2 onto v1.1. All figures recounted from `canonical/*.yaml` during the F2.1 reporting reconciliation pass.

## Schema validation

| Check | Result |
|---|---|
| All Family IDs match `^F\d{2}$` | ✅ 12/12 |
| All Atom IDs match `^F\d{2}\.\d{2}$` | ✅ 61/61 |
| All Edge IDs match `^INT-F\d{2}\.\d{2}-F\d{2}\.\d{2}-\d{2}$` | ✅ 26/26 |
| All Source IDs match `^SRC-(INT|EXT|ADR|RULE|CODE|DEC)-\d{3}$` | ✅ 12/12 |
| All Exclusion IDs match `^OOS-\d{3}$` | ✅ 3/3 |
| No undefined `evidence_class` values | ✅ All in {NORMATIVE, WEAK_EVIDENCE, EXCLUDED} |
| No undefined `authority_class` values | ✅ All in defined taxonomy |
| No undefined `edge_kind` values | ✅ All in {REQUIRES, DEPENDS_ON, REFINES, FORBIDS, IMPLIES, CONDITIONAL_ON} |
| No undefined `status` values | ✅ All in {ACTIVE, EXCLUDED} |
| No placeholder SRC IDs | ✅ |

## Headline entity totals

| Entity | Count |
|---|---:|
| Families | 12 |
| Atoms total | 61 |
| Atoms ACTIVE | 60 |
| Atoms EXCLUDED | 1 |
| Atoms NORMATIVE | 55 |
| Atoms WEAK_EVIDENCE | 5 |
| Edges total | 26 |
| Edges NORMATIVE | 18 |
| Edges WEAK_EVIDENCE | 8 |
| Sources | 12 |
| Exclusions | 3 |

Global coverage: `55 / (55 + 5) = 0.9167` GREEN.
Bucket distribution: **9 GREEN / 2 YELLOW / 1 RED**.

## Orphan checks

| Check | Result |
|---|---|
| Orphan atom → family | ✅ 0 orphans |
| Orphan edge → source atom | ✅ 0 orphans |
| Orphan edge → target atom | ✅ 0 orphans |
| Orphan atom binding → source | ✅ 0 orphans (all 12 SRC IDs resolve) |
| Orphan edge binding → source | ✅ 0 orphans |
| Orphan exclusion → atom | ✅ OOS-001 references F12.04 which exists EXCLUDED |
| Orphan exclusion → family | ✅ All OOS `related_families` resolve |

## Duplicate checks

| Check | Result |
|---|---|
| Duplicate Family IDs | ✅ 0 |
| Duplicate Atom IDs | ✅ 0 |
| Duplicate Edge IDs | ✅ 0 |
| Duplicate Source IDs | ✅ 0 |
| Duplicate Exclusion IDs | ✅ 0 |
| Duplicate semantic atoms (same family + normalized claim) | ✅ 0 |

## Status discipline

| Check | Result |
|---|---|
| All ACTIVE atoms have `authority_binding` non-empty | ✅ 60/60 |
| All ACTIVE NORMATIVE atoms have ≥1 non-ADVISORY source | ✅ 55/55 |
| No NORMATIVE atom supported only by ADVISORY/WEAK sources | ✅ 0 violations (SRC-ADR-001 not cited by any atom) |
| EXCLUDED atoms reference an OOS record | ✅ F12.04 → OOS-001 |
| `invalid_for_normative_use` discipline preserved | ✅ SRC-ADR-001 never appears in any atom authority_binding |

## Source authority_class tally (recounted)

| Authority class | Rank | Count | Source IDs |
|---|---:|---:|---|
| CONSTITUTIONAL | 1 | 1 | SRC-RULE-001 |
| GOVERNANCE | 2 | 4 | SRC-RULE-002, SRC-INT-001, SRC-INT-002, SRC-INT-004 |
| ARCHITECTURAL | 4 | 6 | SRC-INT-003, SRC-ADR-002, SRC-ADR-003, SRC-ADR-004, SRC-ADR-005, SRC-ADR-006 |
| ADVISORY | 6 | 1 | SRC-ADR-001 |
| **Total** | — | **12** | — |

(Prior version of this table carried a typo that listed GOVERNANCE as "3 ... actually 4". Corrected to `4` during F2.1 reporting reconciliation.)

## Edge evidence tally (recounted)

| Evidence class | Count |
|---|---:|
| NORMATIVE | 18 |
| WEAK_EVIDENCE | 8 |
| **Total** | **26** |

### Weak edges — full enumeration

| Edge ID | Kind | Source endpoint (evidence) | Target endpoint (evidence) | Both endpoints NORMATIVE? |
|---|---|---|---|:---:|
| INT-F02.01-F01.05-01 | DEPENDS_ON | F02.01 (NORMATIVE) | F01.05 (NORMATIVE) | ✅ |
| INT-F05.04-F06.01-01 | REQUIRES | F05.04 (WEAK_EVIDENCE) | F06.01 (NORMATIVE) | ❌ |
| INT-F07.03-F02.01-01 | CONDITIONAL_ON | F07.03 (WEAK_EVIDENCE) | F02.01 (NORMATIVE) | ❌ |
| INT-F07.03-F05.01-01 | REQUIRES | F07.03 (WEAK_EVIDENCE) | F05.01 (NORMATIVE) | ❌ |
| INT-F08.04-F09.01-01 | REQUIRES | F08.04 (NORMATIVE) | F09.01 (NORMATIVE) | ✅ |
| INT-F09.05-F08.04-01 | REQUIRES | F09.05 (NORMATIVE) | F08.04 (NORMATIVE) | ✅ |
| INT-F12.05-F02.01-01 | DEPENDS_ON | F12.05 (NORMATIVE) | F02.01 (NORMATIVE) | ✅ |
| INT-F12.08-F08.03-01 | DEPENDS_ON | F12.08 (NORMATIVE) | F08.03 (NORMATIVE) | ✅ |

Summary: 5 of 8 weak edges have dual-NORMATIVE endpoints; 3 involve a WEAK atom endpoint (F05.04 or F07.03).

## Locator resolvability

| Source | Locator | Resolves |
|---|---|---|
| SRC-RULE-001 | `.claude/rules/constitutional.md` | ✅ |
| SRC-RULE-002 | `.claude/rules/global_rules.md` | ✅ |
| SRC-INT-001 | `AGENTS.md` | ✅ |
| SRC-INT-002 | `docs/wave_e/00_schema/downstream_lane_contract.md#1-governing-semantics-non-negotiable` | ✅ |
| SRC-INT-003 | `docs/wave_e/00_schema/requirement_graph_schema.yaml#governing-semantics` | ✅ |
| SRC-INT-004 | `AGENTS.md#memory-lifecycle` | ✅ |
| SRC-ADR-001 | `docs/architecture/healing_dispatch_routing_adr.md` | ✅ |
| SRC-ADR-002 | `docs/specs/hardening/HEALER_RETRY_HARDENING_SPEC.md` | ✅ |
| SRC-ADR-003 | `docs/architecture/eval_pipeline_acceptance.md` | ✅ |
| SRC-ADR-004 | `docs/specs/hardening/L0_DECOMPOSITION_SPEC.md` | ✅ |
| SRC-ADR-005 | `docs/specs/hardening/REPLAY_DETERMINISM_RULES.md` | ✅ |
| SRC-ADR-006 | `docs/specs/hardening/AUTHORITY_HIERARCHY_INVARIANTS.md` | ✅ |

All 12 verified resolvable.

## Coverage arithmetic

```
ACTIVE atoms       = 60
  NORMATIVE        = 55
  WEAK_EVIDENCE    =  5
EXCLUDED atoms     =  1

Global coverage    = 55 / 60 = 0.9167 (GREEN, >= 0.90)
```

Per-family scores verified by programmatic recount. Zero rounding games.

## Edge-specific validation

| Check | Result |
|---|---|
| Every edge endpoint is an atom in canonical YAML (ACTIVE or EXCLUDED) | ✅ 26/26 |
| Every edge cites ≥1 valid source in authority_binding | ✅ 26/26 |
| CONDITIONAL_ON edges carry a `condition` field | ✅ 1/1 (INT-F07.03-F02.01-01) |
| No edge has source_atom_id == target_atom_id | ✅ 0 self-loops |

## Sidecar contamination check

| Check | Result |
|---|---|
| No `rationale:` field in canonical atoms | ✅ |
| No `excerpt:` field in canonical atoms | ✅ |
| No proposal-only fields leaked into atom records | ✅ |
| Sources retain `notes:` and `excerpt:` per schema (permitted fields) | ✅ |

## Write boundary check

All v1.2 writes are confined to:

- `docs/wave_e/99_integration_v12/canonical/*`
- `docs/wave_e/99_integration_v12/*.md`

No writes to `docs/wave_e/00_schema/`, v1.1, or F2 proposal files.

## Final verdict

**✅ ALL CHECKS PASS. Canonical v1.2 is publishable.**
