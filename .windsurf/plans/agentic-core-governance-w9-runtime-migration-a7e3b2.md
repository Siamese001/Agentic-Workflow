---
description: Migrate remaining runtime policy leakage from agentic_core to app-owned profiles
tags: [governance, remediation, runtime, migration, w9]
---

# W9: Migrate Remaining Runtime Policy Leakage

**Plan ID:** agentic-core-governance-w9-runtime-migration-a7e3b2  
**Parent Plan:** agentic-core-governance-w8-scanner-taxonomy-alignment-e5f2b1  
**Created:** 2026-05-12  
**Status:** Not Started  
**Priority:** HIGH

---

## Context

W8 successfully reconciled 208 blocking scanner findings (154 UNKNOWN + 54 RUNTIME) against the W7 Phase 0 classification. The taxonomy engine is installed and functioning correctly:

- UNKNOWN = 0 ✅ (all reclassified)
- STATIC_REGISTRY = 165 (properly classified, non-blocking)
- OFFLINE_TOOLING = 24 (properly classified, non-blocking)
- FALSE_POSITIVE = 11 (properly classified, non-blocking)
- RUNTIME_POLICY_LEAKAGE = 55 (**requires W9 migration**)

**Blocker for parent remediation:** The 55 remaining RUNTIME_POLICY_LEAKAGE findings prevent strict mode from exiting 0. W9 must migrate these to enable W8 parent remediation to finally close.

---

## Problem Statement

55 true runtime policy leakage violations remain in `agentic_core` runtime paths. These are app-specific code branches that influence governed runtime decisions (routing, policy enforcement, validation).

**W7 Phase 0 established:** Only RUNTIME_POLICY_LEAKAGE must be eliminated. All other categories (~295 non-runtime) are approved per W7.

**Current State:**
- Strict mode exits 2 (correctly blocking on runtime leakage)
- 11 files in runtime paths contain hardcoded app references
- Pattern: `app_id="apps_rg"`, `if app_id == "apps_lic"`, app-specific paths

---

## Goal

Move app-specific runtime behavior out of `agentic_core` into app-owned runtime profiles/packages, or prove specific files are TEMPORARY_THIN_ADAPTER with valid receipts.

**Final State Required:**
- RUNTIME_POLICY_LEAKAGE = 0
- UNKNOWN = 0 (maintained from W8)
- `core_leakage_scan.py --strict` exits 0
- `run_contract_gates.py` exits 0
- No app-specific runtime branching remains in agentic_core

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W9 | P0 | Runtime leakage audit | ~400 | W8 classification complete | 🔲 TODO | Each of 12 files audited with disposition |
| W9 | P1 | TEMPORARY_THIN_ADAPTER verification | ~200 | P0 audit complete | 🔲 TODO | Valid receipts or migration path |
| W9 | P2 | Generic resolver design | ~300 | P1 verification complete | 🔲 TODO | Profile-driven architecture spec |
| W9 | P3 | Migration execution | ~800 | P2 design approved | 🔲 TODO | Runtime leakage = 0 |
| W9 | P4 | Verification & handoff | ~200 | P3 migration complete | 🔲 TODO | Strict mode passes |

**Total: ~1900 tokens across 5 phases**

---

## Out Of Scope

- Fixing STATIC_REGISTRY, OFFLINE_TOOLING, FALSE_POSITIVE findings (approved per W7)
- Changes to ADG adapters, analysis tools, or schema enums (proven non-runtime in W8)
- New governance scanner features (W8 engine is complete)
- Documentation-only changes without migration

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P0 | Runtime leakage audit | Per-file analysis | PP-0: Determine disposition for each target file | ~400 | 🔲 TODO |
| P1.1 | Dispatch files audit | runtime/entry/apps_*_dispatch.py | PP-1: 11 dispatch files to audit | ~200 | 🔲 TODO |
| P1.2 | Adapter files audit | runtime/u0/*_adapter.py | PP-2: U0 adapters with app checks | ~100 | 🔲 TODO |
| P1.3 | L6 files audit | runtime/l6/*_learning_adapter.py | PP-3: L6 writeback with app literals | ~100 | 🔲 TODO |
| P2.1 | Receipt validation | artifacts/governance/migration_receipts/ | PP-4: Check for existing thin-adapter receipts | ~100 | 🔲 TODO |
| P2.2 | TEMPORARY_THIN_ADAPTER classification | Per-file classification | PP-5: Document migration deadline or migrate | ~100 | 🔲 TODO |
| P3.1 | Generic resolver design | App profile registry + runtime resolver | PP-6: Design generic app resolution | ~200 | 🔲 TODO |
| P3.2 | Profile-driven config spec | Runtime profile schema | PP-7: Define app-owned runtime profile format | ~100 | 🔲 TODO |
| P4.1 | Dispatch migration | Move app dispatch to app-owned packages | PP-8: Migrate 11 dispatch files | ~400 | 🔲 TODO |
| P4.2 | U0 adapter migration | Move U0 adapters to app profiles | PP-9: Migrate U0 app checks | ~200 | 🔲 TODO |
| P4.3 | L6 migration | Move L6 writeback to generic mechanism | PP-10: Migrate L6 app literals | ~200 | 🔲 TODO |
| P5.1 | Scan verification | Full strict scan | PP-11: Verify RUNTIME = 0 | ~100 | 🔲 TODO |
| P5.2 | CI verification | run_contract_gates.py | PP-12: Verify CI passes | ~50 | 🔲 TODO |
| P5.3 | W8 parent handoff | Close parent remediation | PP-13: Enable W8 to finally close | ~50 | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Files In Scope

### P0/P1 Audit Target## Source Scanner Output (Ground Truth)

**Source:** `artifacts/governance/scans/core_leakage_scan_1778562716.json`  
**Timestamp:** 1778562716  
**Total RUNTIME_POLICY_LEAKAGE Findings:** 55

| # | File Path | Findings | Patterns |
|---|-----------|----------|----------|
| 1 | `agentic_core/C0_context/cross_app_research_substrate_ingest.py` | 1 | hardcoded_app_names |
| 2 | `agentic_core/runtime/entry/apps_research_dispatch.py` | 10 | hardcoded_app_names |
| 3 | `agentic_core/runtime/entry/apps_rg_dispatch.py` | 11 | hardcoded_app_names, app_id_branching |
| 4 | `agentic_core/runtime/entry/u0_apps_research_binding_v2.py` | 9 | hardcoded_app_names, app_id_branching |
| 5 | `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` | 2 | hardcoded_app_names |
| 6 | `agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py` | 1 | hardcoded_app_names |
| 7 | `agentic_core/runtime/l6/apps_rg_learning_adapter.py` | 1 | hardcoded_app_names |
| 8 | `agentic_core/runtime/l6/writeback_proposer.py` | 2 | hardcoded_app_names |
| 9 | `agentic_core/runtime/prove_requirements/code_symbol_catalog.py` | 7 | hardcoded_app_names |
| 10 | `agentic_core/runtime/u0/apps_lic_u0_adapter.py` | 7 | hardcoded_app_names, app_specific_cache_policies |
| 11 | `agentic_core/runtime/u0/apps_rg_u0_adapter.py` | 2 | hardcoded_app_names |
| 12 | `agentic_core/runtime/u0/payload_synthesizer.py` | 2 | hardcoded_app_names |
| **TOTAL** | | **55** | |

---

## Scope Reconciliation: W9 Plan vs Scanner Reality

### Original W9 Plan Target Files (12 claimed)

The W9 plan initially listed these 12 target files:
1. `apps_rg_dispatch.py` ✓
2. `apps_research_dispatch.py` ✓
3. `apps_lic_u0_adapter.py` ✓
4. `apps_rg_u0_adapter.py` ✓
5. `u0_apps_research_binding_v2.py` ✓
6. `apps_rg_learning_adapter.py` ✓
7. `writeback_proposer.py` ✓
8. `code_symbol_catalog.py` ✓
9. `payload_synthesizer.py` ✓
10. `integrated_r4_resume_gen.py` → **RENAMED** to `integrated_r4_deterministic_pipeline_run.py`
11. `integrated_r4_research_then_draft.py` → **RENAMED** to `integrated_r4_lic_pipeline_run.py`
12. `cross_app_research_substrate_ingest.py` ✓

### Scanner Verification

**Result:** 12 files confirmed, 55 findings confirmed

| Reconciliation Item | Status |
|-------------------|--------|
| File count match | ✅ 12 files in scanner = 12 files in plan |
| Finding count match | ✅ 55 total findings |
| File name drift | ⚠️ 2 pipeline files renamed (shown above) |
| Missing from initial audit | ⚠️ `cross_app_research_substrate_ingest.py` (1 finding) was missed |
| Missing from initial audit | ⚠️ `apps_research_dispatch.py` (10 findings) was missed |

### Arithmetic Correction

| Count | Value | Note |
|-------|-------|------|
| Total RUNTIME findings | 55 | From scanner (verified) |
| FALSE_RUNTIME (tooling) | 7 | `code_symbol_catalog.py` |
| **Remaining blocking findings** | **48** | 55 - 7 = 48 (not 37 as previously miscalculated) |
| Files requiring disposition | 12 | All 12 files have exactly one disposition |

---

## Final Disposition Table

| # | File Path | Findings | Disposition | Rationale |
|---|-----------|----------|-------------|-----------|
| 1 | `agentic_core/C0_context/cross_app_research_substrate_ingest.py` | 1 | **MIGRATE_TO_PROFILE** | C0 ingest with app_id filtering - runtime policy behavior |
| 2 | `agentic_core/runtime/entry/apps_research_dispatch.py` | 10 | **MIGRATE_TO_PROFILE** | Full dispatch orchestration for apps_research |
| 3 | `agentic_core/runtime/entry/apps_rg_dispatch.py` | 11 | **MIGRATE_TO_PROFILE** | Full runtime orchestration with dispatch, bridge install |
| 4 | `agentic_core/runtime/entry/u0_apps_research_binding_v2.py` | 9 | **MIGRATE_TO_PROFILE** | App-specific delegation, validation, research-only orchestration |
| 5 | `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` | 2 | **MIGRATE_TO_PROFILE** | Pipeline runner with app-specific namespace defaults |
| 6 | `agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py` | 1 | **MIGRATE_TO_PROFILE** | Pipeline runner with hardcoded APP_NAME |
| 7 | `agentic_core/runtime/l6/apps_rg_learning_adapter.py` | 1 | **MIGRATE_TO_PROFILE** | L6 writeback with hardcoded app_id |
| 8 | `agentic_core/runtime/l6/writeback_proposer.py` | 2 | **MIGRATE_TO_PROFILE** | L6 writeback orchestration |
| 9 | `agentic_core/runtime/prove_requirements/code_symbol_catalog.py` | 7 | **FALSE_RUNTIME_CLASSIFICATION** | Static analysis tooling, not runtime behavior |
| 10 | `agentic_core/runtime/u0/apps_lic_u0_adapter.py` | 7 | **MIGRATE_TO_PROFILE** | U0 validation with app_id checks |
| 11 | `agentic_core/runtime/u0/apps_rg_u0_adapter.py` | 2 | **MIGRATE_TO_PROFILE** | U0 adapter with app_id assignment |
| 12 | `agentic_core/runtime/u0/payload_synthesizer.py` | 2 | **MIGRATE_TO_PROFILE** | Payload with app-specific defaults |
| **TOTALS** | **12 files** | **55 findings** | | |

### Post-Disposition Summary

| Category | Files | Findings | Action Required |
|----------|-------|----------|-----------------|
| **MIGRATE_TO_PROFILE** | 11 | 48 | Migrate to profile-driven architecture |
| **FALSE_RUNTIME_CLASSIFICATION** | 1 | 7 | Reclassify to OFFLINE_TOOLING_REFERENCE |
| **TEMPORARY_THIN_ADAPTER** | 0 | 0 | None qualify (all have runtime behavior) |
| **TOTAL** | 12 | 55 | |

**Blocking findings after reclassification:** 48  
**Non-blocking (tooling):** 7  
**Strict scan will pass when:** 48 → 0 via profile migration

---

## Gap Register

| ID | Gap | Risk | Mitigation |
|----|-----|------|------------|
| G1 | Migration complexity for dispatch files | High | Phase P3 generic resolver reduces per-file work |
| G2 | Runtime stability during migration | High | TEMPORARY_THIN_ADAPTER receipts allow incremental |
| G3 | App profile registry not yet defined | Medium | P3.2 defines schema; W9 is design + migrate |
| G4 | Testing coverage for generic resolver | Medium | Maintain existing tests; add profile resolver tests |
| G5 | L6 writeback coordination | Medium | Coordinate with L6 observability team |

---

## Definition of Done

| DoD | Criterion | Verification |
|-----|-----------|--------------|
| DoD-1 | **RUNTIME_POLICY_LEAKAGE = 0** | `python tools/governance/core_leakage_scan.py --strict` shows RUNTIME: 0 |
| DoD-2 | **UNKNOWN = 0 maintained** | Scan shows UNKNOWN: 0 (regression guard) |
| DoD-3 | **Strict scan exits 0** | `echo $?` returns 0 after strict scan |
| DoD-4 | **CI gates pass** | `python ops_scripts/ci/run_contract_gates.py` exits 0 |
| DoD-5 | **No app-specific runtime branching** | Manual audit: no `if app_id == "apps_..."` in runtime paths |
| DoD-6 | **W8 parent can close** | W8 plan updated with "BLOCKED BY W9: RESOLVED" |
| DoD-7 | **Receipt for TEMPORARY_THIN_ADAPTER** | Any remaining thin adapters have receipts with deadlines |
| DoD-8 | **Documentation complete** | AGENTS.md references W9 migration |

---

## Verification vs Deferral

| Phase | Verifiable Now? | If Deferred, Risk |
|-------|-----------------|-------------------|
| P1 File Audit | Yes | Medium - needed for scope clarity |
| P2 Receipt Check | Yes | Low - can check existing receipts |
| P3 Generic Design | Partial | High - blocks P4 migration |
| P4 Migration | No (requires P3) | N/A - sequential dependency |
| P5 Verification | No (requires P4) | N/A - sequential dependency |

**Deferred:** None yet. P1-P2 can proceed immediately.

---

## Acceptance Criteria

W9 is accepted when:
1. `python tools/governance/core_leakage_scan.py --strict` exits 0
2. Scan output shows `[SUMMARY] Blocking: 0 (RUNTIME_POLICY_LEAKAGE: 0, UNKNOWN: 0)`
3. `python ops_scripts/ci/run_contract_gates.py` exits 0
4. All 12 files either:
   - Migrated to app-owned runtime profiles, OR
   - Classified as valid TEMPORARY_THIN_ADAPTER (see strict criteria below), OR
   - Proven FALSE_RUNTIME_CLASSIFICATION and reclassified
5. Every remaining runtime app literal is either gone or covered by valid unexpired TEMPORARY_THIN_ADAPTER receipt
6. W8 parent plan updated to "BLOCKED BY W9: RESOLVED" **only after strict mode exits 0**

---

## TEMPORARY_THIN_ADAPTER Strict Criteria

Runtime files may ONLY receive TEMPORARY_THIN_ADAPTER classification if ALL of the following are true:

| Criterion | Verification |
|-----------|--------------|
| Pure boundary shim | No policy branching, no business logic |
| No runtime routing decisions | Does not route requests based on app identity |
| No durable writes | Does not write to L6 or external stores |
| No orchestration | Does not coordinate multi-step processes |
| No validation | Does not enforce domain constraints |
| Valid 12-field receipt | Exists at `artifacts/governance/migration_receipts/<file>.receipt.json` |
| Migration deadline | Receipt contains explicit `migration_deadline` timestamp |
| Unexpired | Current date < `migration_deadline` |
| Scanner treatment | Strict scanner treats as non-blocking ONLY when receipt valid and unexpired |

**Files with runtime routing, validation, writeback, C0 ingest, or app-specific pipeline behavior MUST migrate to app-owned profile/package. They cannot receive TEMPORARY_THIN_ADAPTER receipts.**

---

## P0 Runtime Leakage Audit Template

For each of the 12 target files, P0 must produce:

| Field | Value |
|-------|-------|
| File | path/to/file.py |
| Finding Count | N findings |
| Runtime Layer | U0/U1/L2/L3/L4/L5/L6/Entrypoint/C0 |
| Exact Leakage Pattern | e.g., `app_id="apps_rg"`, `if app_id == "apps_lic"` |
| Branches on App Identity? | YES/NO |
| Routes? | YES/NO |
| Validates? | YES/NO |
| Writes Back? | YES/NO |
| Ingests? | YES/NO |
| Orchestrates? | YES/NO |
| **Disposition** | MIGRATE_TO_PROFILE / MOVE_TO_APP_PACKAGE / TEMPORARY_THIN_ADAPTER_WITH_RECEIPT / FALSE_RUNTIME_CLASSIFICATION |

**P0 is mandatory. No implementation (P1-P5) begins until P0 is complete.**

---

## Related

- W8 Plan: `.windsurf/plans/agentic-core-governance-w8-scanner-taxonomy-alignment-e5f2b1.md`
- W7 Phase 0: `artifacts/governance/w7_phase0_classification.md`
- W8 P5 Receipt: `artifacts/governance/w8_p5_receipt.md`
- Rule: `.windsurf/rules/agentic-core-static.md` (TEMPORARY_THIN_ADAPTER)
- W8 Status: PARTIAL / CLASSIFICATION COMPLETE / REMEDIATION BLOCKED BY W9

---

## W9 Parent Handoff

When W9 completes:
1. W8 plan status flips to **COMPLETED**
2. W8 parent remediation can finally close
3. Full governance scanner taxonomy is operational
4. CI strict mode passes
5. Zero blocking findings in agentic_core

**Parent remediation closure requires:**
- W9 strict mode exit 0
- W8 DoD-6 verification
- Final W8 receipt
