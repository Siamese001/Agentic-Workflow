---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\prompt_governance_yaml_integration_plan-7fa0d2.md'
original_relative_path: 'prompt_governance_yaml_integration_plan-7fa0d2.md'
source_sha256: c656ebf37d165cdaaf5c0d1dafca92e6b82f1d741b9057528cb761d742e7fac0
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Convert Markdown Prompt Injections to Production-Grade YAML and Ensure Full Integration

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary
Convert the 30 instructional injection patterns from markdown in `data/prompt_governance\prompt_injections` to structured YAML templates in `data/prompt_governance\injections`, then implement a unified loader that serves both `agentic_core` and `apps_*` with proper test coverage.

## Current State Analysis

### ✅ Production-Grade YAML Templates (Already Exist)
- **Location**: `data/prompt_governance\injections\`
- **Structure**:
  - `misc/` - 7 monolithic YAML files (framing.yaml, safety.yaml, etc.)
  - `modular/` - 64 granular YAML files organized by layer
- **Quality**: Production-ready with structured templates, variables, success criteria
- **Problem**: **NOT INTEGRATED** - No code references these YAML files

### ❌ Markdown Templates (Currently Integrated but Not Production-Grade)
- **Location**: `data/prompt_governance\prompt_injections\`
- **Files**: 4 markdown files with 30 injection patterns
- **Problem**: Hardcoded in `agentic_core/config/core/injection_layer_config.py`
- **Gap**: No integration with `apps_*` folders

### 🚨 Critical Finding
The YAML templates are **production-ready but unused**, while markdown files are **integrated but not production-grade**.

## Implementation Plan

### Phase 1: Create Unified YAML Loader
1. **Create**: `agentic_core/config/core/yaml_injection_loader.py`
   - Load YAML templates from `data/prompt_governance\injections\`
   - Support both `misc/` and `modular/` structures
   - Provide same interface as existing `PromptInjectionLoader`

2. **Update**: `agentic_core/runtime/config/prompt_injection_loader_config.py`
   - Replace hardcoded patterns with YAML loader
   - Maintain backward compatibility
   - Add fallback to markdown if YAML missing

### Phase 2: Bridge apps_* Integration Gap
1. **Create**: `apps_shared/config/prompt_governance_config.py`
   - Import YAML loader from `agentic_core`
   - Provide apps-specific configuration
   - Handle app-specific context variables

2. **Update**: `apps_shared/utils/instructional_layer.py`
   - Replace duplicate implementations with YAML loader calls
   - Maintain existing function signatures
   - Add deprecation warnings for duplicate code

### Phase 3: Test Coverage
1. **Unit Tests**:
   - `tests/unit/agentic_core/test_yaml_injection_loader.py`
   - `tests/unit/apps_shared/test_prompt_governance_integration.py`
   - Test all 30 patterns load correctly from YAML

2. **Integration Tests**:
   - `tests/integration/test_prompt_governance_end_to_end.py`
   - Verify flow from YAML → agentic_core → apps_*
   - Test template rendering with variables

### Phase 4: Migration & Cleanup
1. **Migrate**: Update all references from markdown to YAML
2. **Deprecate**: Add warnings to markdown-based code
3. **Cleanup**: Remove duplicate implementations in `apps_shared`
4. **Documentation**: Update source references in code headers

## File Changes Required

### New Files
- `agentic_core/config/core/yaml_injection_loader.py` - Unified YAML loader
- `apps_shared/config/prompt_governance_config.py` - Apps integration layer
- `tests/unit/agentic_core/test_yaml_injection_loader.py` - Loader tests
- `tests/unit/apps_shared/test_prompt_governance_integration.py` - Apps tests
- `tests/integration/test_prompt_governance_end_to_end.py` - E2E tests

### Modified Files
- `agentic_core/runtime/config/prompt_injection_loader_config.py` - Use YAML loader
- `apps_shared/utils/instructional_layer.py` - Remove duplicates, use YAML
- `agentic_core/config/core/injection_layer_config.py` - Update source reference
- `agentic_core/mixins/instructional_injection_mixin.py` - Point to YAML source

### Key Technical Decisions
1. **YAML Structure**: Use existing `modular/` structure for granular control
2. **Backward Compatibility**: Maintain existing API during transition
3. **Variable System**: Extend YAML variable format for complex templates
4. **Caching**: Implement LRU cache for YAML-loaded templates
5. **Error Handling**: Graceful fallback to markdown if YAML fails

## Success Criteria
1. ✅ All 30 injection patterns load from YAML files
2. ✅ Both `agentic_core` and `apps_*` use same YAML source
3. ✅ Existing functionality preserved (backward compatibility)
4. ✅ Test coverage > 90% for new code paths
5. ✅ Performance impact < 5% (caching mitigates this)
6. ✅ Markdown files deprecated but still functional during transition

## Risk Mitigation
1. **Breaking Changes**: Use feature flags and gradual migration
2. **Performance**: Implement aggressive caching for YAML templates
3. **Complexity**: Keep existing API surface, change only internals
4. **Testing**: Comprehensive test suite before any deprecation

## Implementation Timeline
- **Phase 1**: 2- (YAML loader + core integration)
- **Phase 2**:  (apps_* bridge)
- **Phase 3**:  (test coverage)
- **Phase 4**: 1- (migration + cleanup)
- **Total**: 7-

This plan ensures production-grade YAML templates are fully integrated across both `agentic_core` and `apps_*` while maintaining backward compatibility and comprehensive test coverage.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

