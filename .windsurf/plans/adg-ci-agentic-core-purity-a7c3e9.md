---
title: "ADG CI Check: agentic_core Purity + apps_* U0 Input Contract (Hardened)"
slug: adg-ci-agentic-core-purity-a7c3e9
description: |
  Hardened ADG-driven CI gate enforcing agentic_core remains a pure pipeline
  and apps_* domain packages enter only through U0 runtime_customization_package.
  Detects 9 leakage types, enforces positive allowed-flow, emits structured
  artifacts with full provenance. Advisory mode first with documented
  promotion criteria to strict.
tier: T2
status: Not Started
created: 2026-05-12
last_updated: 2026-05-12
tags:
  - adg
  - ci-gate
  - agentic_core
  - architecture-enforcement
  - purity-check
  - u0-contract
  - leakage-detection
  - spine-ingress
---

# ADG CI Check: agentic_core Purity + apps_* U0 Input Contract

## Problem Statement

Per constitutional `agentic-core-static.md`, `agentic_core` must remain **app-agnostic**. App-specific behavior must flow through `U0 runtime_customization_package` as **inputs**, not be embedded inside core layers as **leakage**.

**Current gap**: No automated ADG-driven detection exists for:
1. `agentic_core` files containing app-specific literals (`apps_rg`, `apps_lic`, etc.)
2. Import edges from `agentic_core` → `apps_*` (reverse of allowed flow)
3. Call edges from core layers into app-specific functions
4. Apps bypassing U0 and entering core layers directly
5. Untyped or missing runtime_customization_package handoffs

**Risk**: Undetected leakage accumulates, violating the "Core owns mechanisms; apps own meaning" principle.

## Success Criteria

- [ ] New ADG CI gate `gate_agentic_core_purity.py` exists at `ops_scripts/ci/adg_gates/`
- [ ] Gate ID: `AG-PURITY` (consistent throughout)
- [ ] W0 schema discovery phase queries ADG SQLite tables/views/relation types
- [ ] Detects 9 leakage types with precise classification
- [ ] Enforces positive allowed-flow: `apps_* -> U0 runtime_customization_package` ✅
- [ ] Violations emit full JSON artifact with 11 required fields
- [ ] Separate `violation_severity` (P1/P2/P3), `gate_mode` (advisory/strict), `ci_effect` (warn/fail)
- [ ] Synthetic SQLite tests cover 9 scenarios
- [ ] Registered in `run_contract_gates.py` as "AG-PURITY agentic_core purity (advisory)"
- [ ] Baseline artifact: `artifacts/ci/agentic_core_purity_baseline.json`
- [ ] Promotion criteria documented for advisory → strict transition

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | P1-P2 | Schema discovery + baseline | ~2k | ADG SQLite accessible, can introspect schema | 🔲 TODO | Schema map emitted, baseline captured |
| W1 | P1-P3 | Gate skeleton + ADG query layer | ~4k | ADGGateBase stable, semantic edges populated | 🔲 TODO | Gate runs, connects to ADG, emits JSON |
| W2 | P1-P4 | Leakage detection heuristics (9 types) | ~5k | Materialized views available, edge authority reliable | 🔲 TODO | All 9 leakage types detected |
| W3 | P1-P3 | Positive flow enforcement + classification | ~3k | U0 package paths resolvable | 🔲 TODO | Allowed flows verified, violations classified |
| W4 | P1-P3 | CI registration + synthetic tests + baseline | ~4k | `run_contract_gates.py` accepts new gate | 🔲 TODO | CI integration complete, 9 test scenarios pass |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.P1 | Schema introspection | SQL queries | Discover tables, views, edge types | ~1k | 🔲 TODO |
| W0.P2 | Baseline capture | Artifact write | Emit schema map + initial leakage count | ~1k | 🔲 TODO |
| W1.P1 | Gate skeleton | 1 new file | Extend ADGGateBase, set gate_family | ~1.5k | 🔲 TODO |
| W1.P2 | ADG query layer | SQL + Python | Semantic edge queries, path resolution | ~1.5k | 🔲 TODO |
| W1.P3 | JSON output schema | Dataclass | Match required 11-field artifact | ~1k | 🔲 TODO |
| W2.P1 | CORE_APP_SPECIFIC_LITERAL detection | SQL + regex | String matching in node bodies | ~1.5k | 🔲 TODO |
| W2.P2 | CORE_TO_APP_IMPORT detection | Edge query | agentic_core → apps_* imports | ~1k | 🔲 TODO |
| W2.P3 | CORE_TO_APP_CALL detection | Edge query | agentic_core → apps_* calls | ~1k | 🔲 TODO |
| W2.P4 | APP_BYPASSES_U0 detection | Path analysis | Apps entering core layers directly | ~1.5k | 🔲 TODO |
| W3.P1 | Allowed-flow verification | Positive check | apps_* → U0 package validation | ~1k | 🔲 TODO |
| W3.P2 | Violation classification | Python | Map to 9 leakage types + severity | ~1k | 🔲 TODO |
| W3.P3 | Thin adapter receipt check | File system | Verify TEMPORARY_THIN_ADAPTER receipts | ~1k | 🔲 TODO |
| W4.P1 | CI registration | run_contract_gates.py | Add AG-PURITY entry, advisory mode | ~1k | 🔲 TODO |
| W4.P2 | Synthetic SQLite tests | 1 test file | 9 test scenarios with mock ADG | ~2k | 🔲 TODO |
| W4.P3 | Baseline artifact + promotion doc | 2 files | JSON baseline + promotion criteria | ~1k | 🔲 TODO |

## Gap Register

| ID | Gap | Risk | Resolution Wave |
|----|-----|------|-----------------|
| G1 | ADG semantic edge coverage gaps may miss dynamic calls | Medium | Post-W2 baseline review |
| G2 | False positives on TEST_ALLOWED/DOC_ALLOWED/RECEIPT_ALLOWED paths | Low | W2 filter via path patterns |
| G3 | TEMPORARY_THIN_ADAPTER classification requires manual receipt verification | Medium | W3.P3 file existence check |
| G4 | U0 runtime_customization_package path resolution varies by app | Low | W3.P1 canonical path mapping |
| G5 | Synthetic tests may not cover all edge cases | Medium | W4.P2 9-scenario matrix |

## Definition of Done

| ID | Criterion | Verification Method | Owner |
|----|-----------|---------------------|-------|
| DoD-1 | Gate detects CORE_APP_SPECIFIC_LITERAL | Synthetic test: core contains `apps_rg` literal | W2 |
| DoD-2 | Gate detects CORE_TO_APP_IMPORT | Synthetic test: agentic_core imports apps_lic | W2 |
| DoD-3 | Gate detects CORE_TO_APP_CALL | Synthetic test: agentic_core calls apps_qna function | W2 |
| DoD-4 | Gate detects APP_BYPASSES_U0 | Synthetic test: apps_rg imports L2 directly | W2 |
| DoD-5 | Gate allows apps_* → U0 flow | Synthetic test: apps_rg → runtime_customization_package passes | W3 |
| DoD-6 | All 9 leakage types classified correctly | Unit test matrix | W3 |
| DoD-7 | CI integration emits artifact | `python ops_scripts/ci/run_contract_gates.py --gate AG-PURITY` exits 0 | W4 |
| DoD-8 | Baseline artifact created | `artifacts/ci/agentic_core_purity_baseline.json` exists | W4 |
| DoD-9 | Promotion criteria documented | Markdown file with advisory→strict criteria | W4 |

## Verification-vs-Deferral

| Item | Verify (this plan) | Defer (future plan) |
|------|-------------------|---------------------|
| 9 leakage type detection | ✅ W2 | |
| Positive allowed-flow enforcement | ✅ W3 | |
| Full 11-field JSON artifact | ✅ W1-W3 | |
| Synthetic test suite (9 scenarios) | ✅ W4.P2 | |
| CI advisory registration | ✅ W4.P1 | |
| Baseline artifact + promotion criteria | ✅ W4.P3 | |
| Auto-fix / migration suggestions | | Future (requires Author-Gate) |
| Historical trend analysis | | P3 gate enhancement wave |
| Strict mode enforcement | | Post-promotion (criteria defined in W4.P3) |

## Violation Types (9 Categories)

Per `agentic-core-static.md` §72-73:

| Leakage Type | Severity | CI Effect | Description |
|--------------|----------|-----------|-------------|
| `CORE_APP_SPECIFIC_LITERAL` | P1 | warn | App literal (`apps_*`) in agentic_core file body |
| `CORE_TO_APP_IMPORT` | P1 | warn | agentic_core imports from apps_* (reverse flow) |
| `CORE_TO_APP_CALL` | P1 | warn | agentic_core calls apps_* function (runtime leakage) |
| `APP_BYPASSES_U0` | P1 | warn | apps_* imports core layer directly, not via U0 |
| `APP_DIRECT_TO_CORE_LAYER` | P2 | warn | apps_* imports non-U0 core layer (L1-L6) |
| `APP_RUNTIME_PACKAGE_MISSING` | P2 | warn | apps_* has no runtime_customization_package |
| `APP_RUNTIME_PACKAGE_UNTYPED` | P3 | warn | U0 package exists but lacks type annotations |
| `TEMPORARY_THIN_ADAPTER_UNRECEIPTED` | P2 | warn | Thin adapter pattern without migration receipt |
| `TEST_ALLOWED` | exempt | pass | Tests importing both layers (allowed) |
| `DOC_ALLOWED` | exempt | pass | Documentation referencing both (allowed) |
| `RECEIPT_ALLOWED` | exempt | pass | Migration receipts with app references (allowed) |

## JSON Artifact Schema (11 Required Fields)

```json
{
  "source_path": "agentic_core/L3_orchestration/exit_eval/v6/pipeline.py",
  "target_path": "apps_rg/config/domain_contract/route_profile.yaml",
  "source_line": 245,
  "target_line": 12,
  "relation_type": "imports",
  "leakage_type": "CORE_TO_APP_IMPORT",
  "severity": "P1",
  "ci_effect": "warn",
  "classification_reason": "agentic_core imports apps_* config directly, bypassing U0 abstraction",
  "suggested_action": "Move to apps_rg U0 runtime_customization_package or add TEMPORARY_THIN_ADAPTER receipt",
  "evidence_refs": ["adg_edge_id:12345", "node_body_hash:abc123"]
}
```

## Allowed Flow Enforcement (Positive Check)

```
✅ ALLOWED:  apps_* -> U0 runtime_customization_package -> core layers
❌ BLOCKED: apps_* -> core layers (L0-L6) directly
❌ BLOCKED: agentic_core -> apps_* (any direction)
```

Apps must enter the spine **only** through:
1. `apps_*/runtime/entry/runtime_customization_package.py` (canonical U0 path)
2. Approved thin adapter with `TEMPORARY_THIN_ADAPTER` receipt at `artifacts/governance/migration_receipts/`

## Synthetic Test Scenarios (9 Tests)

| Test ID | Scenario | Expected Leakage Type | Expected Severity |
|---------|----------|----------------------|-------------------|
| T1 | core imports apps_rg | `CORE_TO_APP_IMPORT` | P1 |
| T2 | core calls apps_lic | `CORE_TO_APP_CALL` | P1 |
| T3 | core executable literal apps_rg | `CORE_APP_SPECIFIC_LITERAL` | P1 |
| T4 | apps_rg enters U0 package path | (none - allowed) | pass |
| T5 | apps_rg bypasses U0, imports L2 | `APP_BYPASSES_U0` | P1 |
| T6 | untyped runtime package handoff | `APP_RUNTIME_PACKAGE_UNTYPED` | P3 |
| T7 | TEMPORARY_THIN_ADAPTER with receipt | (none - allowed) | pass |
| T8 | TEMPORARY_THIN_ADAPTER without receipt | `TEMPORARY_THIN_ADAPTER_UNRECEIPTED` | P2 |
| T9 | docs/tests/receipts exemptions | (none - exempt) | pass |

## Implementation Path

```
ops_scripts/ci/adg_gates/gate_agentic_core_purity.py
  └── extends ADGGateBase (from gate_base.py)
      └── gate_family = "AG-PURITY"
      └── severity = "P1"
      └── gate_mode = "advisory"  # W4.P1
      └── ci_effect = "warn"      # W4.P1
      └── source_views = [
              "nodes",
              "edges",
              "mv_layer_violations",
              "mv_entrypoint_kind_summary"
          ]
```

## CI Registration

```python
# ops_scripts/ci/run_contract_gates.py
assurance_gates = [
    # ... existing gates ...
    {
        "id": "AG-PURITY",
        "name": "agentic_core purity (advisory)",
        "module": "ops_scripts.ci.adg_gates.gate_agentic_core_purity",
        "mode": "advisory",
        "fail_closed_env": "AG_PURITY_FAIL_CLOSED",
        "bypass_env": "AG_PURITY_BYPASS",
    },
]
```

## Promotion Criteria (Advisory → Strict)

Document in `docs/adr/gate-promotion/AG-PURITY-advisory-to-strict.md`:

1. **Stability**: 30 days continuous operation without false positive > 2%
2. **Coverage**: All 9 leakage types detected in at least one production run
3. **Baseline**: Initial leakage inventory complete with owner assignments
4. **Remediation**: >50% of P1 violations addressed or scheduled
5. **Approval**: SVP Engineering sign-off on strict mode activation

Strict mode activates via `AG_PURITY_STRICT=1` or gate mode change in config.

## References

- Rule: `.windsurf/rules/agentic-core-static.md` §71-73 (triage categories)
- Rule: `.windsurf/rules/adg-canonical-invariants.md` §4, §6
- Pattern: `ops_scripts/ci/adg_gates/gate_base.py` — ADGGateBase
- Pattern: `ops_scripts/ci/adg_gates/gate_p0_capability_egress.py` — egress detection
- Pattern: `ops_scripts/ci/check_agentic_core_static_boundary.py` — boundary gate
- SSOT: `artifacts/governance/migration_receipts/` — thin adapter receipts

## Non-Goals (Explicit)

- ❌ Auto-migration of detected leakage (Author-Gate required per policy)
- ❌ Fixing existing leakage (baseline only; remediation is follow-up work)
- ❌ Strict mode activation (requires promotion criteria + SVP approval)
- ❌ Auto-generation of migration receipts (human approval required)

## Appendix: Detection SQL Templates

### CORE_APP_SPECIFIC_LITERAL
```sql
SELECT n.resolved_path, n.line_start, n.body
FROM nodes n
WHERE n.resolved_path LIKE 'agentic_core/%'
  AND n.body REGEXP 'apps_[a-z_]+'
  AND n.resolved_path NOT LIKE '%/tests/%'
  AND n.resolved_path NOT LIKE '%/docs/%'
  AND n.resolved_path NOT LIKE '%/receipts/%'
```

### CORE_TO_APP_IMPORT / CORE_TO_APP_CALL
```sql
SELECT e.source_file, e.source_line, e.target_file, e.relation_type
FROM edges e
JOIN nodes src ON e.source_id = src.id
JOIN nodes tgt ON e.target_id = tgt.id
WHERE e.relation_type IN ('imports', 'calls')
  AND src.resolved_path LIKE 'agentic_core/%'
  AND tgt.resolved_path LIKE 'apps_%/%'
  AND src.resolved_path NOT LIKE '%/tests/%'
```

### APP_BYPASSES_U0
```sql
SELECT DISTINCT src.resolved_path as app_path,
       tgt.resolved_path as core_path,
       e.relation_type
FROM edges e
JOIN nodes src ON e.source_id = src.id
JOIN nodes tgt ON e.target_id = tgt.id
WHERE src.resolved_path LIKE 'apps_%/%'
  AND tgt.resolved_path LIKE 'agentic_core/%'
  AND tgt.resolved_path NOT LIKE '%/runtime/customization_package%'
  AND e.relation_type = 'imports'
```

### APP_RUNTIME_PACKAGE_MISSING (Post-processing)
```python
# For each apps_* package, verify:
# apps_*/runtime/entry/runtime_customization_package.py exists
# OR apps_*/runtime_customization_package.py exists
```

---

Plan Version: 2.0 (Hardened)
Last Updated: 2026-05-12
