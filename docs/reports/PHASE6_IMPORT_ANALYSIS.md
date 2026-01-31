# Phase 6 Import Analysis & Remediation Plan

## Executive Summary

Phase 6 test migration revealed systematic import issues in the `apps_rg` module due to:
1. Inconsistent filename conventions (snake_case vs PascalCase)
2. Circular dependencies between core modules
3. Missing module files referenced in imports
4. MRO (Method Resolution Order) conflicts from redundant mixin inheritance

## Current Status

### ✅ Completed Fixes
- `apps_rg/domain/__init__.py` - Fixed PromptTemplate import
- `apps_rg/domain/config/__init__.py` - Fixed SovereignConfigLoader import
- `apps_rg/shared/reasoning/__init__.py` - Fixed ReasoningToggles import
- `apps_rg/logic_nodes/__init__.py` - Fixed PascalCase imports
- `apps_rg/logic_nodes/RGFlowRouter.py` - Fixed ThematicAnalysisNode import
- `apps_rg/engines/ContentQualityAgent.py` - Fixed SkillExtractorNode import
- 13 files in `apps_rg/engines/` - Fixed agent_base imports and removed redundant SubatomicTestingMixin

### ❌ Remaining Issues

#### Issue 1: Circular Dependency Chain
**Root Cause:** `StateTransaction.py` imports from `engines/base/BaseRGEngine.py`, which triggers import of all engines through `engines/__init__.py`, which then tries to import back through `shared/core/__init__.py`.

**Chain:**
```
apps_rg/shared/core/__init__.py
  → apps_rg/shared/core/StateTransaction.py
    → apps_rg/engines/base/BaseRGEngine.py
      → apps_rg/engines/__init__.py (imports all engines)
        → apps_rg/engines/HardenedOpenAIExecutor.py
          → agentic_core/base_agents/TokenLimitError.py
            → agentic_core/base_agents/circuit_breaker.py (MISSING)
```

#### Issue 2: Missing Module - circuit_breaker
**File:** `agentic_core/base_agents/TokenLimitError.py:16`
**Import:** `from .circuit_breaker import CircuitBreakerOpenError, get_breaker`
**Actual Files:**
- `agentic_core/base_agents/CircuitBreakerState.py`
- `agentic_core/L4_state/ledger/CircuitBreaker.py`

**Resolution:** Update import to use correct module path.

## Detailed Remediation Plan

### Phase 6.6: Resolve Circular Dependency

**Strategy:** Break the circular dependency by moving mixins out of engines module.

**Option A: Move Mixins to Dedicated Module (RECOMMENDED)**
Create `apps_rg/shared/mixins.py` with MCPHardenedMixin and HealerMixin, avoiding engine imports.

**Option B: Lazy Imports**
Use lazy imports in StateTransaction.py to defer engine loading.

**Option C: Remove ImmutableStagingBuffer from core/__init__.py**
Don't export ImmutableStagingBuffer through __init__.py, require direct imports.

**Selected: Option A**

**File Diffs:**

1. **Create `apps_rg/shared/mixins.py`**
```python
"""
Shared mixins for RG agents - extracted to avoid circular dependencies.
"""
from __future__ import annotations

class MCPHardenedMixin:
    """MCP hardening mixin for RG agents."""
    def __init__(self):
        self._mcp_hardened = True

class HealerMixin:
    """Healing mixin for RG agents."""
    def __init__(self):
        self._healing_enabled = False
```

2. **Update `apps_rg/shared/core/StateTransaction.py`**
```diff
- from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin
- from apps_rg.engines.base.BaseRGEngine import MCPHardenedMixin, HealerMixin
+ from apps_rg.shared.mixins import MCPHardenedMixin, HealerMixin
```

3. **Update `apps_rg/shared/core/mixins.py`**
```diff
  from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin
- from apps_rg.engines.base.BaseRGEngine import MCPHardenedMixin, HealerMixin
+ from apps_rg.shared.mixins import MCPHardenedMixin, HealerMixin
```

4. **Update `apps_rg/engines/base/BaseRGEngine.py`**
```diff
+ from apps_rg.shared.mixins import MCPHardenedMixin, HealerMixin
+
  # Keep class definitions for backward compatibility but they now inherit from shared
- class MCPHardenedMixin:
-     ...
+ class MCPHardenedMixin(apps_rg.shared.mixins.MCPHardenedMixin):
+     """Backward compatibility wrapper."""
+     pass
```

**Test Case:**
```python
# Test circular dependency is broken
def test_no_circular_dependency():
    """Verify StateTransaction can be imported without triggering engine imports."""
    import sys

    # Clear any cached imports
    for key in list(sys.modules.keys()):
        if key.startswith('apps_rg.engines'):
            del sys.modules[key]

    # Import StateTransaction - should not trigger engine imports
    from apps_rg.shared.core.StateTransaction import ImmutableStagingBuffer

    # Verify engines were not imported
    assert 'apps_rg.engines.HardenedOpenAIExecutor' not in sys.modules
    assert 'apps_rg.engines.ContentQualityAgent' not in sys.modules
```

### Phase 6.7: Fix circuit_breaker Import

**Root Cause:** Import path mismatch - trying to import from `base_agents` but file is in `L4_state/ledger`.

**File Diff:**

**Update `agentic_core/base_agents/TokenLimitError.py`**
```diff
- from .circuit_breaker import CircuitBreakerOpenError, get_breaker
+ from agentic_core.L4_state.ledger.CircuitBreaker import CircuitBreakerOpenError, get_breaker
```

**Test Case:**
```python
def test_token_limit_error_imports():
    """Verify TokenLimitError can be imported successfully."""
    from agentic_core.base_agents.TokenLimitError import (
        HardeningMixin,
        TokenLimitError,
        CircuitBreakerOpenError
    )
    assert HardeningMixin is not None
    assert TokenLimitError is not None
    assert CircuitBreakerOpenError is not None
```

### Phase 6.8: Validation Tests

**Test Suite: `tests/e2e/ops_scripts/test_lic_rg_parity.py`**

Expected Results:
- ✅ test_configuration_parity - PASS
- ✅ test_reasoning_toggles_parity - PASS
- ✅ test_trace_registry_parity - PASS (after fixes)
- ✅ test_base_engine_parity - PASS (after fixes)
- ✅ test_orchestrator_parity - PASS (after fixes)
- ✅ test_gap_closure_validation - PASS (after fixes)

**Validation Command:**
```bash
python -m pytest tests/e2e/ops_scripts/test_lic_rg_parity.py -v --tb=short
```

## Risk Assessment

### Low Risk
- Moving mixins to shared module (no logic changes)
- Fixing import paths (mechanical changes)

### Medium Risk
- Circular dependency resolution (requires careful testing)

### Mitigation
- Run full test suite after each phase
- Keep git commits granular for easy rollback
- Verify no new import errors introduced

## Success Criteria

1. All imports resolve without ModuleNotFoundError
2. No circular dependency warnings
3. test_lic_rg_parity.py: 6/6 tests pass
4. Full e2e test suite runs without import errors
5. Zero MRO conflicts

## Timeline

- Phase 6.6: 10 minutes (circular dependency)
- Phase 6.7: 5 minutes (circuit_breaker fix)
- Phase 6.8: 5 minutes (validation)
- **Total: 20 minutes**
