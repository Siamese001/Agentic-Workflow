---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-refactoring-wave2-plan-58a2b1.md'
original_relative_path: 'apps-refactoring-wave2-plan-58a2b1.md'
source_sha256: ab5a0b24ca9db8fde57fcb32547ceb9854bcaa88286b2aef730f3fcd7349e7bd
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps Directory Refactoring Plan - Wave 2 onwards

**Generated:** 2025-04-05 18:14
**ADG Snapshot:** adg_indexed_04052026_1813.sqlite
**Scope:** Recursive analysis and refactoring of apps_* directories

## Executive Summary

Based on detailed ADG SQLite analysis of 9 apps_* directories (1,063 total files), this plan addresses:
- Root-level file violations (documentation files at app root)
- Test coverage gaps across all apps_* directories
- Structural alignment with territories.yaml definitions
- SSOT updates to reflect all changes

**Current State:**
- ✅ apps_qwen: Refactored in Wave 1 (complete)
- ⚠️ apps_lic: 187 files, root-level SVP_ENGINEERING_REVIEW.md (violation)
- ⚠️ apps_rg: 170 files, root-level SVP_ENGINEERING_REVIEW.md (violation)
- ✅ apps_eval: 58 files, proper structure, 14.6% test coverage
- ✅ apps_exec: 60 files, proper structure, 9.8% test coverage
- ✅ apps_research: 58 files, proper structure, 10.3% test coverage
- ✅ apps_rfp: 58 files, proper structure, 10.3% test coverage
- ✅ apps_shared: 291 files, proper structure, 1.6% test coverage
- ✅ apps_underwriting_ai: 69 files, proper structure, 6.8% test coverage

---

## Wave Summary Table

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| Wave 2 | 2.1-2.2 | Root-level file violations | 5,000 | docs/ territory exists | Pending | No non-__init__ files at app root |
| Wave 3 | 3.1-3.3 | Test coverage - critical apps | 15,000 | Test patterns exist | Pending | apps_qwen, apps_underwriting_ai > 20% coverage |
| Wave 4 | 4.1-4.3 | Test coverage - high-signal apps | 20,000 | Test patterns exist | Pending | apps_eval, apps_exec > 25% coverage |
| Wave 5 | 5.1-5.4 | Test coverage - remaining apps | 25,000 | Test patterns exist | Pending | All apps > 15% coverage |
| Wave 6 | 6.1-6.2 | SSOT synchronization | 10,000 | territories.yaml up-to-date | Pending | All SSOT files reflect structure |

**Total Estimated Tokens:** 75,000

---

## Wave 2: Root-Level File Violations

**Focus:** Remove documentation files from app root levels

### Phase 2.1: Move apps_lic SVP Engineering Review
- **Action:** Move `apps_lic/SVP_ENGINEERING_REVIEW.md` to `docs/apps_lic/`
- **Rationale:** Documentation belongs in docs/ territory, not app root
- **Files affected:** 1 file moved
- **Risk:** LOW - documentation only, no code changes

### Phase 2.2: Move apps_rg SVP Engineering Review
- **Action:** Move `apps_rg/SVP_ENGINEERING_REVIEW.md` to `docs/apps_rg/`
- **Rationale:** Documentation belongs in docs/ territory, not app root
- **Files affected:** 1 file moved
- **Risk:** LOW - documentation only, no code changes

**Success Criteria:**
- No non-__init__.py files at root level of any apps_* directory
- Documentation files in docs/ territory
- territories.yaml unchanged (no app structure changes)

---

## Wave 3: Test Coverage - Critical Applications

**Focus:** apps_qwen (0% coverage) and apps_underwriting_ai (6.8% coverage)

### Phase 3.1: Analyze apps_qwen Test Gaps
- **Action:** Query ADG for apps_qwen files without corresponding tests
- **Target files:** 7 Python files (config: 2, engines: 3, reasoning: 1, tools: 1)
- **Priority:** High - apps_qwen is critical infrastructure (vLLM inference)
- **Test strategy:**
  - Test config classes for validation logic
  - Test engine client wrappers with mocks
  - Test gateway orchestration with mocked dependencies
  - Test GPU monitoring with mocked psutil

### Phase 3.2: Create apps_qwen Test Suite
- **Action:** Create test files in `apps_qwen/tests/`
- **Files to create:**
  - `test_config.py` - Test AppsQwenConfig, AppsQwenModelConfig
  - `test_engines.py` - Test OptimizedVLLMClient, HardenedVLLMClient
  - `test_gateway.py` - Test AppsQwenGateway orchestration
  - `test_tools.py` - Test GPUMemoryMonitor
- **Risk:** MEDIUM - requires mocking of external dependencies (vLLM, GPU)

### Phase 3.3: Enhance apps_underwriting_ai Test Coverage
- **Action:** Add tests for core underwriting components
- **Target coverage increase:** 6.8% → 20%
- **Priority:** High - business-critical domain logic
- **Test strategy:**
  - Test parsers with sample financial documents
  - Test validators with edge cases
  - Test reasoning agents with mocked LLM calls
  - Test engines with mock data

**Success Criteria:**
- apps_qwen test coverage > 20%
- apps_underwriting_ai test coverage > 20%
- All tests pass with mocks for external dependencies

---

## Wave 4: Test Coverage - High-Signal Applications

**Focus:** apps_eval (14.6%) and apps_exec (9.8%)

### Phase 4.1: Analyze apps_eval Test Gaps
- **Action:** Query ADG for apps_eval files without tests
- **Target files:** 41 Python files, 6 tests (gap: 35 files)
- **Priority:** HIGH - evaluation is quality gate for other apps
- **High-signal files to test:**
  - `reasoning/EvalOrchestrator.py` - Core orchestration
  - `engines/evaluation_retrieval_engine.py` - Retrieval logic
  - `services/quality_assessor_service.py` - Quality assessment
  - `services/regression_detector_service.py` - Regression detection

### Phase 4.2: Create apps_eval Test Suite
- **Action:** Add test files for high-signal components
- **Files to create:**
  - `test_eval_orchestrator.py` - Test orchestration logic
  - `test_evaluation_engines.py` - Test retrieval and scoring
  - `test_quality_services.py` - Test quality assessment
  - `test_regression_detection.py` - Test regression detection
- **Risk:** MEDIUM - requires mocking of retrieval/LLM services

### Phase 4.3: Enhance apps_exec Test Coverage
- **Action:** Add tests for apps_exec high-signal components
- **Target coverage increase:** 9.8% → 25%
- **High-signal files to test:**
  - `reasoning/ExecOrchestrator.py` - Execution orchestration
  - `engines/brief_assembly_engine.py` - Brief assembly
  - `engines/ingestion_engine.py` - Document ingestion
  - `services/style_validator_service.py` - Style validation

**Success Criteria:**
- apps_eval test coverage > 25%
- apps_exec test coverage > 25%
- High-signal orchestration and engine components tested

---

## Wave 5: Test Coverage - Remaining Applications

**Focus:** apps_lic (3.3%), apps_rg (2.7%), apps_research (10.3%), apps_rfp (10.3%), apps_shared (1.6%)

### Phase 5.1: Enhance apps_lic Test Coverage
- **Action:** Add tests for critical LIC components
- **Target coverage increase:** 3.3% → 15%
- **High-signal files:** LIC validation, outreach orchestration
- **Test strategy:** Focus on validation logic and message routing

### Phase 5.2: Enhance apps_rg Test Coverage
- **Action:** Add tests for resume generation components
- **Target coverage increase:** 2.7% → 15%
- **High-signal files:** Content optimization, ATS compatibility
- **Test strategy:** Focus on generation engines with mocked LLM

### Phase 5.3: Enhance apps_research & apps_rfp Test Coverage
- **Action:** Add tests for research and RFP components
- **Target coverage increase:** 10.3% → 15% each
- **High-signal files:** Source discovery, synthesis engines
- **Test strategy:** Focus on retrieval and synthesis logic

### Phase 5.4: Enhance apps_shared Test Coverage
- **Action:** Add tests for shared utilities and adapters
- **Target coverage increase:** 1.6% → 15%
- **High-signal files:** Spine adapters, configuration services
- **Test strategy:** Focus on shared infrastructure components

**Success Criteria:**
- All apps_* directories have > 15% test coverage
- Shared infrastructure components tested
- Test patterns established for future development

---

## Wave 6: SSOT Synchronization

**Focus:** Update SSOT files to reflect all structural changes

### Phase 6.1: Update territories.yaml
- **Action:** Verify all apps_* definitions match actual structure
- **Current state:** apps_qwen and apps_underwriting_ai already added
- **Verification steps:**
  - Confirm subfolder counts match actual directories
  - Verify purpose descriptions align with actual usage
  - Check for missing subfolders (e.g., apps_shared has data_adapters, enforcement, mixins, prompts, spine)

### Phase 6.2: Update _constants.py and structure_blueprint_config.py
- **Action:** Ensure SSOT constants reflect apps_* structure
- **Files to update:**
  - `agentic_core/L5_safety/config/structure_blueprint/_constants.py`
  - Any other SSOT configuration files
- **Verification:** Run territory validation to ensure no violations

**Success Criteria:**
- territories.yaml matches actual apps_* structure
- No territory violations detected
- SSOT constants synchronized

---

## Risk Assessment

| Wave | Risk Level | Mitigation |
|------|------------|------------|
| Wave 2 | LOW | Documentation-only moves, no code changes |
| Wave 3 | MEDIUM | External dependency mocking required |
| Wave 4 | MEDIUM | External dependency mocking required |
| Wave 5 | LOW-MEDIUM | Follow patterns from Waves 3-4 |
| Wave 6 | LOW | SSOT verification only |

**Overall Risk:** MEDIUM - Test creation requires careful mocking of external services

---

## Dependencies

- Wave 2: No dependencies (can run independently)
- Wave 3: Depends on Wave 2 completion (clean structure)
- Wave 4: Depends on Wave 3 completion (test patterns established)
- Wave 5: Depends on Wave 4 completion (test patterns established)
- Wave 6: Depends on Waves 2-5 completion (final structure known)

---

## Evidence Requirements

Per constitutional §3.1, each wave will produce an evidence file:
- `.windsurf/plans/wave2-root-violations-<6hex>-evidence.md`
- `.windsurf/plans/wave3-critical-tests-<6hex>-evidence.md`
- `.windsurf/plans/wave4-highsignal-tests-<6hex>-evidence.md`
- `.windsurf/plans/wave5-remaining-tests-<6hex>-evidence.md`
- `.windsurf/plans/wave6-ssot-sync-<6hex>-evidence.md`

Each evidence file must include:
- EXECUTION_SUMMARY
- FACT_CLASSIFICATION (all 6 categories)
- ARTIFACTS
- UNRESOLVED

---

## Token Budget Status

| Wave | Budget | Status |
|------|--------|--------|
| Wave 2 | 5,000 | 🟢 GREEN |
| Wave 3 | 15,000 | 🟢 GREEN |
| Wave 4 | 20,000 | 🟢 GREEN |
| Wave 5 | 25,000 | 🟢 GREEN |
| Wave 6 | 10,000 | 🟢 GREEN |
| **Total** | **75,000** | 🟢 GREEN |

---

## Next Steps

**Awaiting user approval to proceed with:**
1. Wave 2: Root-level file violations (apps_lic, apps_rg)
2. Subsequent waves upon completion of prior waves

**Question for user:**
Should I proceed with Wave 2 (moving SVP_ENGINEERING_REVIEW.md files to docs/)?
