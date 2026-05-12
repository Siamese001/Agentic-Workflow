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

### P0/P1 Audit Target Files (12 total)

| File | Path | Line Count | Pattern | Runtime Layer |
|------|------|------------|---------|---------------|
| apps_rg_dispatch.py | runtime/entry/ | ~487 | app_id="apps_rg" | U0 Entry |
| apps_research_dispatch.py | runtime/entry/ | ~420 | app_id="apps_research" | U0 Entry |
| apps_lic_u0_adapter.py | runtime/u0/ | ~350 | app_id checks | U0 Adapter |
| apps_rg_u0_adapter.py | runtime/u0/ | ~340 | app_id checks | U0 Adapter |
| u0_apps_research_binding_v2.py | runtime/entry/ | ~280 | delegation check | U0 Entry |
| apps_rg_learning_adapter.py | runtime/l6/ | ~220 | L6 writeback | L6 |
| writeback_proposer.py | runtime/l6/ | ~190 | L6 app literals | L6 |
| code_symbol_catalog.py | runtime/prove_requirements/ | ~260 | code catalog | Utility |
| payload_synthesizer.py | runtime/u0/ | ~310 | app-specific paths | U0 |
| integrated_r4_resume_gen.py | runtime/entrypoints/ | ~450 | pipeline entrypoint | Entrypoint |
| integrated_r4_research_then_draft.py | runtime/entrypoints/ | ~480 | pipeline entrypoint | Entrypoint |
| cross_app_research_substrate_ingest.py | C0_context/ | ~180 | app branching | C0 Context |

**Total Lines:** ~3,967 lines across 12 files

**Note:** `code_symbol_catalog.py` disposition pending P0 analysis - must prove governed runtime policy leakage vs runtime/prove tooling metadata before inclusion in migration scope.

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
