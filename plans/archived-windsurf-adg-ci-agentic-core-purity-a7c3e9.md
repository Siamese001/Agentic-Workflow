---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\adg-ci-agentic-core-purity-a7c3e9.md'
original_relative_path: 'adg-ci-agentic-core-purity-a7c3e9.md'
source_sha256: 0a275d27f1ce082a3b47424040702ce2e7d54c4db4cd39802918c81d44466c05
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-12'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
title: "ADG CI Check: agentic_core Purity + apps_* U0 Input Contract (Hardened)"
slug: adg-ci-agentic-core-purity-a7c3e9
description: |
  Hardened ADG-driven CI gate enforcing agentic_core remains a pure pipeline
  and apps_* domain packages enter only through U0 runtime_customization_package.
  Detects active leakage types with exemption classifications, enforces positive allowed-flow,
  emits structured artifacts with full provenance. Advisory mode with documented
  promotion criteria to strict.
tier: T2
status: Completed
plan_version: "2.2"
closure_status: "closed_after_w4"
follow_on_plan: "ag-purity-open-work-remediation-roadmap"
created: 2026-05-12
last_updated: 2026-05-12 (W0-W4 COMPLETE; open work moved to separate remediation roadmap)
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

- [x] New ADG CI gate `gate_agentic_core_purity.py` exists at `ops_scripts/ci/adg_gates/`
- [x] Gate ID: `AG-PURITY` (consistent throughout)
- [x] W0 schema discovery phase queries ADG SQLite tables/views/relation types
- [x] Detects active leakage types plus exemption classifications implemented through W4
- [x] Enforces positive allowed-flow: `apps_* -> U0 runtime_customization_package` ✅
- [x] Violations emit full JSON artifact with 11 required fields
- [x] Separate `violation_severity` (P1/P2/P3), `gate_mode` (advisory/strict), `ci_effect` (warn/fail)
- [x] W3 runtime package validation (11 apps scanned, 11 U0 missing, 3 thin adapters unreceipted)
- [x] W4 CI registration (`--gate AG-PURITY` works, advisory mode, exit 0)
- [x] W4 synthetic tests (9 scenarios T1-T9)
- [x] W4 baseline artifact (21 fields)
- [x] W4 promotion criteria doc (strict mode NOT activated, earliest 2026-05-26)
- [x] Registered in `run_contract_gates.py` as "AG-PURITY agentic_core purity (advisory)"
- [x] Baseline artifact: `artifacts/ci/agentic_core_purity_baseline.json` (✅ W4)
- [x] Promotion criteria documented for advisory → strict transition (✅ W4, earliest 2026-05-26)

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | P1-P2 | Schema discovery + baseline | ~2k | ADG SQLite accessible, can introspect schema | ✅ COMPLETE | Schema map emitted, baseline captured |
| W1 | P1-P3 | Gate skeleton + ADG query layer | ~4k | ADGGateBase stable, semantic edges populated | ✅ COMPLETE | Gate runs, connects to ADG, emits JSON (Commit: 899df41daa) |
| W2 | P1-P4 | Leakage detection refinement + exemptions | ~5k | Materialized views available, edge authority reliable | ✅ COMPLETE | 4 leakage types + 5 exemption types implemented (Commit: f34dbfbc87) |
| W3 | P1-P3 | Runtime package validation + receipt checks | ~3k | U0 package paths resolvable | ✅ COMPLETE | 11 apps scanned, 11 U0 missing, 3 thin adapters unreceipted (Commit: 6916c714a1) |
| W4 | P1-P3 | CI registration + synthetic tests + baseline | ~4k | `run_contract_gates.py` accepts new gate | ✅ COMPLETE | --gate AG-PURITY works, 9 tests, baseline JSON, promotion doc |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.P1 | Schema introspection | SQL queries | Discover tables, views, edge types | ~1k | ✅ COMPLETE |
| W0.P2 | Baseline capture | Artifact write | Emit schema map + initial leakage count | ~1k | ✅ COMPLETE |
| W1.P1 | Gate skeleton | 1 new file | Extend ADGGateBase, set gate_family | ~1.5k | ✅ COMPLETE (467 lines) |
| W1.P2 | ADG query layer | SQL + Python | Semantic edge queries, path resolution | ~1.5k | ✅ COMPLETE (3 detection queries) |
| W1.P3 | JSON output schema | Dataclass | Match required 11-field artifact | ~1k | ✅ COMPLETE (AGPurityViolation dataclass) |
| W2.P1 | CORE_APP_SPECIFIC_LITERAL detection | SQL + Python hybrid | File-based literal search (no nodes.body) | ~1.5k | ✅ COMPLETE (511 violations found) |
| W2.P2 | CORE_TO_APP_IMPORT detection | Edge query | agentic_core → apps_* imports | ~1k | ✅ COMPLETE (18 violations) |
| W2.P3 | CORE_TO_APP_CALL detection | Edge query | agentic_core → apps_* calls | ~1k | ✅ COMPLETE (0 violations - clean) |
| W2.P4 | APP_BYPASSES_U0 detection | Path analysis + exemptions | Apps entering core layers directly | ~1.5k | ✅ COMPLETE (426 violations, entrypoint filtered) |
| W2.P5 | Exemption classifier | Python | TEST/DOC/RECEIPT/GENERATED/MIGRATION | ~1k | ✅ COMPLETE (5 exempted) |
| W3.P1 | Runtime package existence check | File system | Verify U0 package exists per app | ~1k | ✅ COMPLETE (11 apps missing U0) |
| W3.P2 | Runtime package type validation | AST analysis | U0 package type annotations | ~1k | ✅ COMPLETE (0 untyped - no packages found) |
| W3.P3 | Thin adapter receipt check | File system | Verify TEMPORARY_THIN_ADAPTER receipts | ~1k | ✅ COMPLETE (3 unreceipted, 0 receipted) |
| W4.P1 | CI registration | run_contract_gates.py | Add AG-PURITY entry, advisory mode | ~1k | ✅ COMPLETE (3-tuple registration with --gate filter) |
| W4.P2 | Synthetic SQLite tests | 1 test file | 9 test scenarios with mock ADG | ~2k | ✅ COMPLETE (T1-T9 scenarios, 215 lines) |
| W4.P3 | Baseline artifact + promotion doc | 2 files | JSON baseline + promotion criteria | ~1k | ✅ COMPLETE (21-field JSON + 12-section MD) |

## Gap Register

| ID | Gap | Risk | Resolution Wave |
|----|-----|------|-----------------|
| G1 | ADG semantic edge coverage gaps may miss dynamic calls | Medium | Addressed in W2 literal detection |
| G2 | False positives on TEST_ALLOWED/DOC_ALLOWED/RECEIPT_ALLOWED paths | Low | ✅ W2 filter via path patterns (5 exempted) |
| G3 | TEMPORARY_THIN_ADAPTER classification requires manual receipt verification | Medium | W3.P3 file existence check |
| G4 | U0 runtime_customization_package path resolution varies by app | Low | W3.P1 canonical path mapping |
| G5 | Synthetic tests may not cover all edge cases | Medium | W4.P2 9-scenario matrix |
| G6 | APP_RUNTIME_PACKAGE_MISSING not yet implemented | Medium | ✅ W3.P1 (11 apps scanned) |
| G7 | APP_RUNTIME_PACKAGE_UNTYPED not yet implemented | Low | ✅ W3.P2 (0 found) |
| G8 | TEMPORARY_THIN_ADAPTER_UNRECEIPTED not yet implemented | Medium | ✅ W3.P3 (3 found) |
| G9 | Post-W4 remediation scope moved to follow-on plan | - | See: ag-purity-open-work-remediation-roadmap |

## Definition of Done

| ID | Criterion | Verification Method | Owner | Status |
|----|-----------|---------------------|-------|--------|
| DoD-1 | Gate detects CORE_APP_SPECIFIC_LITERAL | Verified: 511 literal violations found in W2 run | W2 | ✅ |
| DoD-2 | Gate detects CORE_TO_APP_IMPORT | Verified: 18 import violations found | W2 | ✅ |
| DoD-3 | Gate detects CORE_TO_APP_CALL | Verified: 0 call violations (clean baseline) | W2 | ✅ |
| DoD-4 | Gate detects APP_BYPASSES_U0 | Verified: 426 direct layer violations (filtered from 9,684) | W2 | ✅ |
| DoD-5 | Gate exemption classification works | Verified: 5 exemptions classified (MIGRATION, RECEIPT) | W2 | ✅ |
| DoD-6 | Gate allows apps_* → U0 flow | Entrypoint/adapter filtering implemented | W2 | ✅ |
| DoD-7 | All active leakage types classified correctly | 7 types + 5 exemptions implemented through W3 | W3 | ✅ |
| DoD-8 | Runtime package existence validation | File existence check with 11 apps scanned | W3 | ✅ |
| DoD-9 | CI integration emits artifact | `python ops_scripts/ci/run_contract_gates.py --gate AG-PURITY` exits 0 | W4 | ✅ |
| DoD-10 | Baseline artifact created | `artifacts/ci/agentic_core_purity_baseline.json` | W4 | ✅ |
| DoD-11 | Promotion criteria documented | Markdown file with advisory→strict criteria | W4 | ✅ |
| DoD-12 | Synthetic tests pass | 9 test scenarios with mock ADG | W4 | ✅ |
| DoD-13 | Gate runs standalone | `python -m ops_scripts.ci.adg_gates.gate_agentic_core_purity` exits 0 | W1-W2 | ✅ |
| DoD-14 | Completed implementation plan closed and follow-on remediation plan created separately | Plan cleanup and closure | W4 | ✅ |

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

| Leakage Type | Severity | CI Effect | Status | Description |
|--------------|----------|-----------|--------|-------------|
| `CORE_APP_SPECIFIC_LITERAL` | P1 | warn | ✅ W2 | App literal (`apps_*`) in agentic_core file body (511 found) |
| `CORE_TO_APP_IMPORT` | P1 | warn | ✅ W2 | agentic_core imports from apps_* (reverse flow) (18 found) |
| `CORE_TO_APP_CALL` | P1 | warn | ✅ W2 | agentic_core calls apps_* function (runtime leakage) (0 found) |
| `APP_BYPASSES_U0` | P1 | warn | ✅ W2 | apps_* imports L0/L1 core layer directly (211 found) |
| `APP_DIRECT_TO_CORE_LAYER` | P2 | warn | ✅ W2 | apps_* imports L2-L6 core layer directly (215 found) |
| `APP_RUNTIME_PACKAGE_MISSING` | P2 | warn | ✅ W3 | apps_* has no runtime_customization_package (11 found) |
| `APP_RUNTIME_PACKAGE_UNTYPED` | P3 | warn | ✅ W3 | U0 package exists but lacks type annotations (0 found) |
| `TEMPORARY_THIN_ADAPTER_UNRECEIPTED` | P2 | warn | ✅ W3 | Thin adapter pattern without migration receipt (3 found) |
| `TEST_ALLOWED` | exempt | pass | ✅ W2 | Tests importing both layers (allowed) |
| `DOC_ALLOWED` | exempt | pass | ✅ W2 | Documentation referencing both (allowed) |
| `RECEIPT_ALLOWED` | exempt | pass | ✅ W2 | Migration receipts with app references (allowed) |
| `GENERATED_ALLOWED` | exempt | pass | ✅ W2 | Generated artifacts with app references (allowed) |
| `MIGRATION_ALLOWED` | exempt | pass | ✅ W2 | Migration/archive files (allowed) |

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
              "nodes",                    # W0-confirmed: resolved_path, span_line
              "edges",                    # W0-confirmed: src_id, dst_id, line_no, relation_type
              "violations",               # W0-confirmed: P0/P1/P2/P3 violations
              "meta",                     # W0-confirmed: snapshot metadata
              "edge_view",                # W0-confirmed: derived edge view
              "mv_edges_governance",      # W0-confirmed: governance edge materialized view
              "v_infra_violations_summary" # W0-confirmed: infrastructure violation summary
              # Note: mv_layer_violations W0-discovered as unavailable
          ]
```

**W0 Schema Discovery Note**:
- Use `edges.src_id` / `edges.dst_id` joined to `nodes.id`
- Use `edges.line_no` for source line references
- Use `nodes.span_line` for span line references (not nodes.line_start)
- Use `n_dst.resolved_path` for target path (not edges.target_file)
- Do NOT use `nodes.body` (field unavailable)

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

Documented in `docs/adr/gate-promotion/AG-PURITY-advisory-to-strict.md`:

**Canonical Promotion Standard**:
1. **Stability Window**: 14 days of advisory operation
2. **False Positive Rate**: Below 5% (verified via manual audit sampling)
3. **P1 Violation Threshold**: Active P1 violations below 100 (currently 740)
4. **Owner Assignment**: All violation areas have assigned engineering owners
5. **Approval**: VP Engineering sign-off on strict mode activation

**Strict Mode Activation**:
- Environment variable: `AG_PURITY_FAIL_CLOSED=1`
- Default: advisory mode (exit 0, warn only)
- Strict mode: non-zero exit on new violations

**Explicit Statement**: ⛔ **Strict mode remains OFF.** Earliest activation: 2026-05-26.

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

## Implementation Results

### W0 Schema Discovery (COMPLETED)

**Receipt**: `artifacts/ci/ag_purity_w0_schema_discovery_receipt.md`

**Key Findings**:
| Field | Planned | W0 Reality | W1/W2 Adaptation |
|-------|---------|------------|------------------|
| `nodes.body` | Available for regex | ❌ MISSING | File-based literal detection |
| `edges.target_file` | Direct field | ❌ MISSING | JOIN via `edges.dst_id -> nodes.id` |
| `nodes.line_start` | Direct field | ❌ MISSING | Uses `nodes.span_line` |
| `edges.line_no` | Source line | ✅ AVAILABLE | Used for source line |

### W1 Gate Skeleton (COMPLETED)

**Commit**: `899df41daa`
**File**: `ops_scripts/ci/adg_gates/gate_agentic_core_purity.py` (467 lines)

**Deliverables**:
- Extends `ADGGateBase` from `gate_base.py`
- Canonical metadata: `gate_id=AG-PURITY`, `gate_family=agentic_core_purity`, `gate_mode=advisory`
- 3 detection queries: CORE_TO_APP_IMPORT, CORE_TO_APP_CALL, APP_TO_CORE_DIRECT
- 11-field `AGPurityViolation` dataclass
- JSON artifact emission to `artifacts/ci_gates/`
- Advisory mode (exit 0)

**W1 Baseline Results**:
| Leakage Type | Count |
|--------------|-------|
| CORE_TO_APP_IMPORT | 18 |
| CORE_TO_APP_CALL | 0 |
| APP_BYPASSES_U0 | ~4,000 |
| APP_DIRECT_TO_CORE_LAYER | ~5,684 |
| **TOTAL** | **9,702** |

### W2 Leakage Refinement (COMPLETED)

**Commit**: `f34dbfbc87`
**Receipt**: `artifacts/ci/ag_purity_w2_leakage_refinement_receipt.md`

**Deliverables**:
- CORE_APP_SPECIFIC_LITERAL detection (file-based SQL+Python hybrid)
- Exemption classifier: TEST_ALLOWED, DOC_ALLOWED, RECEIPT_ALLOWED, GENERATED_ALLOWED, MIGRATION_ALLOWED
- APP_TO_CORE_DIRECT refinement: entrypoint/adapter filtering, internal layer detection
- W2 summary fields: active_violation_count, exempted_count, by_exemption_type, top_*_paths

**W2 Baseline Results**:
| Metric | W1 | W2 | Delta |
|--------|-----|-----|-------|
| **Active Violations** | 9,702 | 955 | **-90.2%** |
| **Exempted** | 0 | 5 | New |
| **Total** | 9,702 | 960 | -90.1% |

**By Leakage Type (W2)**:
| Type | Count |
|------|-------|
| CORE_APP_SPECIFIC_LITERAL | 511 |
| APP_BYPASSES_U0 | 211 |
| APP_DIRECT_TO_CORE_LAYER | 215 |
| CORE_TO_APP_IMPORT | 18 |
| CORE_TO_APP_CALL | 0 |

**By Exemption Type (W2)**:
| Type | Count |
|------|-------|
| MIGRATION_ALLOWED | 3 |
| RECEIPT_ALLOWED | 2 |

**Top Violation Sources**:
| Source Path | Count |
|-------------|-------|
| `apps_shared/proof/scenario_base.py` | 29 |
| `apps_shared/spine_emission/adapter.py` | 20 |
| `apps_shared/integrations/governed_app_runner.py` | 13 |
| `apps_qna/c0_adapter.py` | 12 |
| `apps_lic/coordination/hitl_escalation.py` | 11 |

### W3 Runtime Package Validation (COMPLETED)

**Commit**: `6916c714a1`  
**Receipt**: `artifacts/ci/ag_purity_w3_runtime_package_receipt.md`

**Deliverables**:
- APP_RUNTIME_PACKAGE_MISSING detection (filesystem scan)
- APP_RUNTIME_PACKAGE_UNTYPED detection (type annotation patterns)
- TEMPORARY_THIN_ADAPTER_UNREceiptED detection (marker + receipt validation)
- W3 summary fields: w3_package_checks_applied, runtime_package_*_count, thin_adapter_*_count, apps_scanned

**W3 Baseline Results**:
| Metric | W2 | W3 | Delta |
|--------|-----|-----|-------|
| **Active Violations** | 955 | 969 | +14 (new W3 findings) |
| **Total** | 960 | 974 | +14 |

**By Leakage Type (W3)**:
| Type | Count |
|------|-------|
| CORE_APP_SPECIFIC_LITERAL | 511 |
| APP_BYPASSES_U0 | 211 |
| APP_DIRECT_TO_CORE_LAYER | 215 |
| CORE_TO_APP_IMPORT | 18 |
| CORE_TO_APP_CALL | 0 |
| **APP_RUNTIME_PACKAGE_MISSING** | **11** |
| **TEMPORARY_THIN_ADAPTER_UNRECEIPTED** | **3** |

**Apps Scanned (all missing U0)**:
```
apps_architect, apps_eval, apps_exec, apps_lic, apps_qna,
apps_repo_brief, apps_research, apps_rfp, apps_rg, apps_shared,
apps_underwriting_ai
```

### W4 CI Registration, Tests, Baseline, Promotion Criteria (COMPLETED)

**Commit**: `b8f365d7a9`  
**Receipt**: `artifacts/ci/ag_purity_w4_ci_registration_tests_baseline_receipt.md`

**Deliverables**:
- CI registration in `run_contract_gates.py` (3-tuple with gate_id)
- `--gate AG-PURITY` argument support with argparse
- Synthetic test suite (T1-T9, 215 lines)
- Baseline artifact JSON (21 fields)
- Promotion criteria doc (12 sections, strict mode NOT activated)

**W4 Results**:
| Metric | Status |
|--------|--------|
| CI Registration | ✅ AG-PURITY in assurance_gates |
| --gate filter | ✅ argparse with gate_id matching |
| Synthetic Tests | ✅ 9 scenarios (T1-T9) |
| Baseline JSON | ✅ 21 fields, all violations captured |
| Promotion Doc | ✅ Strict mode earliest 2026-05-26 |

**Baseline JSON Fields**:
```json
{
  "gate_id": "AG-PURITY",
  "gate_version": "W4-ci-registration",
  "active_violation_count": 969,
  "exempted_count": 5,
  "counts_by_leakage_type": { 7 types },
  "apps_scanned": 11,
  "mode": "advisory",
  "ci_effect": "warn"
}
```

**Test Scenarios (T1-T9)**:
| Test | Scenario |
|------|----------|
| T1 | core → apps import (CORE_TO_APP_IMPORT / P1) |
| T2 | core → apps call (CORE_TO_APP_CALL / P1) |
| T3 | core literal apps_* (CORE_APP_SPECIFIC_LITERAL / P1) |
| T4 | apps → U0 approved entry (pass) |
| T5 | apps bypass U0 → L2 (APP_BYPASSES_U0 / P1) |
| T6 | untyped runtime package (APP_RUNTIME_PACKAGE_UNTYPED / P3) |
| T7 | thin adapter with receipt (allowed) |
| T8 | thin adapter without receipt (TEMPORARY_THIN_ADAPTER_UNRECEIPTED / P2) |
| T9 | test/doc exemptions (exempt, not active) |

**Explicit Statement**: ⛔ **Strict mode is NOT activated in W4.**  
**Earliest strict mode date**: 2026-05-26 (requires 14-day stability window, <5% FP rate, <100 P1 violations, VP Eng approval).

---

## Appendix: Detection SQL Templates

### CORE_APP_SPECIFIC_LITERAL
**Note**: Uses path discovery via SQL + Python file read (nodes.body unavailable).

```sql
-- Step 1: Discover candidate files via path pattern
SELECT n.resolved_path, n.span_line
FROM nodes n
WHERE n.resolved_path LIKE 'agentic_core/%'
  AND n.resolved_path NOT LIKE '%/tests/%'
  AND n.resolved_path NOT LIKE '%/docs/%'
  AND n.resolved_path NOT LIKE '%/receipts/%'
```

```python
# Step 2: File-based literal detection
# Read file content, search for apps_* literal patterns
# Not SQL over nodes.body (field unavailable per W0)
```

### CORE_TO_APP_IMPORT / CORE_TO_APP_CALL
```sql
SELECT src.resolved_path as source_file,
       e.line_no as source_line,
       n_dst.resolved_path as target_file,
       e.relation_type
FROM edges e
JOIN nodes src ON e.src_id = src.id
JOIN nodes n_dst ON e.dst_id = n_dst.id
WHERE e.relation_type IN ('imports', 'resolves_callsite')
  AND src.resolved_path LIKE 'agentic_core/%'
  AND n_dst.resolved_path LIKE 'apps_%/%'
  AND src.resolved_path NOT LIKE '%/tests/%'
```

### APP_BYPASSES_U0
```sql
SELECT DISTINCT src.resolved_path as app_path,
       n_dst.resolved_path as core_path,
       e.relation_type
FROM edges e
JOIN nodes src ON e.src_id = src.id
JOIN nodes n_dst ON e.dst_id = n_dst.id
WHERE src.resolved_path LIKE 'apps_%/%'
  AND n_dst.resolved_path LIKE 'agentic_core/%'
  AND n_dst.resolved_path NOT LIKE '%/runtime/customization_package%'
  AND n_dst.resolved_path NOT LIKE '%/runtime/entry%'
  AND e.relation_type = 'imports'
```

### APP_RUNTIME_PACKAGE_MISSING (Post-processing)
```python
# For each apps_* package, verify filesystem:
# apps_*/runtime/entry/runtime_customization_package.py exists
# OR apps_*/runtime_customization_package.py exists
# Type annotation check via AST (not SQL)
```

---

## Closure Note

**W0-W4 Implementation Complete**

This plan successfully delivered the AG-PURITY advisory CI gate through W4:

- **W0**: Schema discovery confirmed available ADG tables/views
- **W1**: Gate skeleton with ADGGateBase extension
- **W2**: Leakage detection refinement with 4 types + 5 exemptions
- **W3**: Runtime package validation + thin adapter receipt checks
- **W4**: CI registration, synthetic tests, baseline artifact, promotion criteria

**Explicit Statements**:
- ⛔ **Strict mode is NOT activated** — remains advisory
- ⛔ **No production remediation occurred** — only detection/baseline
- ⛔ **No auto-fix or migration** — requires separate Author-Gate approval

**Remaining Work**:
Remediation, strict mode readiness, and violation reduction work belongs in a new follow-on plan: **ag-purity-open-work-remediation-roadmap**.

---

Plan Version: 2.2 (W0-W4 COMPLETE — CLOSED)
Last Updated: 2026-05-12 16:45 UTC-4
Commits: 899df41daa (W1), f34dbfbc87 (W2), 6916c714a1 (W3), b8f365d7a9 (W4)
