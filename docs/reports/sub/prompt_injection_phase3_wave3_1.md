# Phase 3 Wave 3.1 - Inventory + Call-Site Map

## Executive Summary

**FINDING**: The apps_shared instructional_layer.py appears to be a legacy duplicate implementation with **NO ACTIVE RUNTIME CALL SITES**. All current usage in tests and agentic_core points to the agentic_core implementation.

## WAVE 3.1.1 — HARD GATE EVIDENCE CAPTURE

### Baseline State

```text
Commit Hash: e18826d1b54a938a62933e13d06f0ab24ec3fa8e
Git Status: Clean (no uncommitted changes)
```

### Pre-commit Validation

```text
T0: Trailing Whitespace..................................................Passed
T0: End-of-File Fixer....................................................Passed
T0: Enforce LF Line Endings..............................................Passed
T0: Check Merge Conflict Markers.........................................Passed
T1: Python Syntax Validation.............................................Passed
T2a: Ruff Lint & Auto-Fix................................................Passed
T2b: Ruff Format.........................................................Passed
T3a: Anti-Pattern Landmine Detection.....................................Passed
T3b: Report Location SSOT Check..........................................Passed
T3c: Reject Tracked Generated Artifacts..................................Passed
T3e: Pycache Purge.......................................................Passed
T3f: Module Collision Guard..............................................Passed
T3h: Evidence Contract Validator.........................................Passed
T3i: Guard pytest.ini scope changes......................................Passed
T3g: Governance Policy Validation........................................Passed
```

### Default Test Suite

```text
================================= 10 passed, 88 deselected in 0.31s ==================================
```

### Structural Audit Suite

```text
=========================== 15 failed, 47 passed, 36 deselected in 2.65s ============================
```

## WAVE 3.1.2 — CALL-SITE MAPPING

### Search Results for apps_shared instructional_layer symbols

**Pattern: `apps_shared\.utils\.instructional_layer|get_instructional_injections|get_required_injections|InstructionalPattern|InjectionLayer`**

#### ACTIVE USAGE (agentic_core implementation):
1. **tests/unit/agentic_core/test_yaml_injection_loader.py**
   - Line 8: `from agentic_core.config.core.injection_layer_config import InjectionLayer`
   - Lines 175-194: Uses `InjectionLayer` enum values
   - **Type**: Test-only, using agentic_core implementation

2. **tests/unit/agentic_core/test_instructional_injections.py**
   - Lines 7, 11-12: `from agentic_core.config.core.injection_layer_config import InjectionLayer, InstructionalPattern`
   - Lines 25, 46, 55, 65, 88, 89, 104: Uses `get_instructional_injections()` and `get_required_injections()`
   - Lines 111-154: Uses `InstructionalPattern` and `InjectionLayer` classes
   - **Type**: Test-only, using agentic_core implementation

3. **tests/unit/agentic_core/base_agents/test_instructional_injection.py**
   - Line 73: Imports `InjectionLayer` from agentic_core
   - **Type**: Test-only, using agentic_core implementation

4. **tests/agentic_core/base_agents/test_instructional_injection.py**
   - Line 73: Imports `InjectionLayer` from agentic_core
   - **Type**: Test-only, using agentic_core implementation

#### LEGACY REFERENCES (documentation/artifacts only):
5. **docs/reports/sub/prompt_governance_yaml_phase2_wave2_1.md**
   - Line 143: `from apps_shared.utils.instructional_layer import get_instructional_injections, get_required_injections`
   - **Type**: Documentation only (evidence from previous phase)

### Search Results for instructional_layer.py file references

**Pattern: `instructional_layer\.py`**

- Found only in documentation, artifact JSON files, and previous phase reports
- **No active code imports found**

### Search Results for PromptInjectionLoader symbols

**Pattern: `PromptInjectionLoader|prompt_injection_loader_config|instructional_injections`**

1. **tests/agentic_core/runtime/config/test_prompt_injection_loader_config.py**
   - Tests agentic_core.runtime.config.prompt_injection_loader_config module
   - **Type**: Test-only, using agentic_core implementation

2. **tests/unit/agentic_core/test_instructional_injections.py**
   - Uses agentic_core.runtime.config.instructional_injections functions
   - **Type**: Test-only, using agentic_core implementation

3. **tests/unit/agentic_core/context_engineering/test_phase0_contract_harness.py**
   - References agentic_core.runtime.config.prompt_injection_loader_config
   - **Type**: Test-only, using agentic_core implementation

## WAVE 3.1.3 — DETERMINISTIC CALL-SITE TABLE

| File Path | Symbol Used | Import Path | Usage Type | Implementation |
|-----------|-------------|-------------|-----------|----------------|
| tests/unit/agentic_core/test_yaml_injection_loader.py | InjectionLayer | agentic_core.config.core.injection_layer_config | Test-only | agentic_core |
| tests/unit/agentic_core/test_instructional_injections.py | get_instructional_injections, get_required_injections, InstructionalPattern, InjectionLayer | agentic_core.config.core.injection_layer_config, agentic_core.runtime.config.instructional_injections | Test-only | agentic_core |
| tests/unit/agentic_core/base_agents/test_instructional_injection.py | InjectionLayer | agentic_core.config.core.injection_layer_config | Test-only | agentic_core |
| tests/agentic_core/base_agents/test_instructional_injection.py | InjectionLayer | agentic_core.config.core.injection_layer_config | Test-only | agentic_core |
| tests/agentic_core/runtime/config/test_prompt_injection_loader_config.py | prompt_injection_loader_config | agentic_core.runtime.config.prompt_injection_loader_config | Test-only | agentic_core |
| tests/unit/agentic_core/context_engineering/test_phase0_contract_harness.py | prompt_injection_loader_config | agentic_core.runtime.config.prompt_injection_loader_config | Test-only | agentic_core |

## CRITICAL FINDINGS

### NO RUNTIME CALL SITES FOUND

- **Zero** runtime imports of `apps_shared.utils.instructional_layer`
- **Zero** production code using apps_shared implementation
- **All** active usage points to agentic_core implementation

### apps_shared DUPLICATE STATUS

- **File exists**: `apps_shared/utils/instructional_layer.py` (899 lines)
- **Functions present**: `get_instructional_injections()`, `get_required_injections()`
- **Classes present**: `InstructionalLayer`, `InstructionalPattern`
- **Usage**: NONE - completely dormant duplicate implementation

### MIGRATION READINESS

- **No migration required** - no active call sites to migrate
- **Safe to remove** - no production dependencies
- **Tests already use agentic_core** - verification already in place

## CONCLUSION

**Phase 3.1 Finding**: The apps_shared instructional_layer.py is a completely dormant duplicate implementation with no active runtime dependencies. All current usage (tests only) already points to the agentic_core SSOT implementation.

**Next Steps**: Can proceed directly to Wave 3.3 (removal) without needing Wave 3.2 (migration) since there are no call sites to migrate.
