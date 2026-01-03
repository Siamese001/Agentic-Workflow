# L2 Execution Phase 2 Migration Guide

**Date:** January 3, 2026  
**Status:** Phase 2 - Unified L2ExecutionBaseAgent  
**Target:** Migrate ~130 L2 agents from dual bases to single unified base

---

## Overview

Phase 2 unifies L2 execution agents under a single canonical base class: `L2ExecutionBaseAgent`.

### What Changed
- **Old:** Two separate base classes
  - `ExecutionCanonBaseAgent` (~50 agents) - heavyweight with Gemini
  - `SubAtomicAgent` (~80 agents) - lightweight validation
  
- **New:** One unified base class
  - `L2ExecutionBaseAgent` - single source of truth with feature flags

### Key Benefits
1. **Consistency** - All L2 agents follow same initialization pattern
2. **Flexibility** - Feature flag (`enable_gemini`) controls heavyweight vs lightweight behavior
3. **Maintainability** - Single codebase to maintain instead of two
4. **Migration Path** - Backward compatible during transition period

---

## New File Location

```
agentic_core/L2_execution/base_agents/
├── __init__.py
└── L2ExecutionBaseAgent.py  ← Single source of truth
```

---

## Migration Patterns

### Pattern A: Former CanonBaseAgent Agents (~50)

**Before:**
```python
from agentic_core.L2_execution.ToolRegistry.ExecutionCanonBaseAgent import CanonBaseAgent

class MyExecutionAgent(CanonBaseAgent):
    def __init__(self, ctx: ValidationContext, **kwargs):
        super().__init__(ctx=ctx)
    
    async def execute(self) -> Any:
        # Heavy Gemini-based execution
        pass
```

**After:**
```python
from agentic_core.L2_execution.base_agents.L2ExecutionBaseAgent import L2ExecutionBaseAgent

class MyExecutionAgent(L2ExecutionBaseAgent):
    def __init__(self, ctx: ValidationContext):
        super().__init__(ctx=ctx, enable_gemini=True)  # Explicit flag
    
    async def execute(self) -> Any:
        # Heavy Gemini-based execution
        pass
```

**Key Changes:**
- Import from `base_agents.L2ExecutionBaseAgent`
- Add `enable_gemini=True` (default, but explicit for clarity)
- Keep async `execute()` method
- Gemini client available via `self._client`

---

### Pattern B: Former SubAtomicAgent Agents (~80)

**Before:**
```python
from agentic_core.L2_execution.tool_registry.base import SubAtomicAgent

class MyValidationAgent(SubAtomicAgent):
    def __init__(self, context: ValidationContext):
        super().__init__(context)
    
    async def execute(self) -> Any:
        # Lightweight validation logic
        pass
```

**After:**
```python
from agentic_core.L2_execution.base_agents.L2ExecutionBaseAgent import L2ExecutionBaseAgent

class MyValidationAgent(L2ExecutionBaseAgent):
    def __init__(self, ctx: ValidationContext):
        super().__init__(ctx=ctx, enable_gemini=False)  # Explicit lightweight flag
    
    async def execute(self) -> Any:
        # Lightweight validation logic
        pass
```

**Key Changes:**
- Import from `base_agents.L2ExecutionBaseAgent`
- Add `enable_gemini=False` for lightweight mode
- Keep async `execute()` method
- No Gemini overhead when disabled

---

## Feature Flags Explained

### `enable_gemini=True` (Default)
- Initializes Gemini client
- Initializes subatomic engine
- Enables `check_negative_constraints()` method
- For former CanonBaseAgent agents
- ~50 agents

### `enable_gemini=False`
- Skips Gemini initialization
- Lighter memory footprint
- `check_negative_constraints()` returns (True, [])
- For former SubAtomicAgent agents
- ~80 agents

---

## Unified Features

All L2ExecutionBaseAgent instances have:

| Feature | Status | Notes |
|---------|--------|-------|
| **Async execute()** | Mandatory | All agents must implement |
| **ValidationContext** | Mandatory | Passed as `ctx` parameter |
| **HealerMixin** | Mandatory | Self-repair capabilities |
| **SubatomicTestingMixin** | Mandatory | Layer-specific testing |
| **can_run()** | Inherited | Checks for CRITICAL_FAIL signal |
| **run_with_broadcast()** | Inherited | Lifecycle wrapper |
| **get_validation_keys()** | Optional | Defaults to empty list |
| **heal_repository()** | Inherited | Operational stub for L2 |
| **check_negative_constraints()** | Gated | Only if enable_gemini=True |

---

## Backward Compatibility

During migration (Phase 2-4), old imports still work:

```python
# These still work (with deprecation warnings)
from agentic_core.L2_execution.ToolRegistry.ExecutionCanonBaseAgent import CanonBaseAgent
from agentic_core.L2_execution.tool_registry.base import SubAtomicAgent

# But they now point to L2ExecutionBaseAgent internally
# Deprecation warnings will guide developers to migrate
```

---

## Migration Checklist

For each L2 agent:

- [ ] Identify if it's former CanonBaseAgent or SubAtomicAgent
- [ ] Update import statement to `L2ExecutionBaseAgent`
- [ ] Update class inheritance to `L2ExecutionBaseAgent`
- [ ] Add appropriate `enable_gemini` flag in `__init__`
- [ ] Verify `async execute()` method exists
- [ ] Run tests to confirm behavior unchanged
- [ ] Update any references to `self._client` or `self._subatomic_engine`

---

## Verification Commands

### Check migration progress
```bash
# Count agents still using old bases
grep -r "CanonBaseAgent" agentic_core/L2_execution/ --include="*.py" | wc -l
grep -r "SubAtomicAgent" agentic_core/L2_execution/ --include="*.py" | wc -l

# Should decrease as migration progresses
```

### Verify all L2 agents use new base
```bash
python canon_validator_agentic_v2_thin.py --layer L2 --check-base
# Expected output: "All 130+ L2 agents inherit from L2ExecutionBaseAgent ✓"
```

### Run tests
```bash
pytest tests/L2_execution/ -v
# All tests should pass with new base
```

---

## Timeline

| Phase | Duration | Action |
|-------|----------|--------|
| **Phase 2** | Jan 03-10 | Create L2ExecutionBaseAgent, add deprecation warnings |
| **Phase 3** | Jan 11-24 | Migrate high-priority agents (~30) |
| **Phase 4** | Jan 25-Feb 07 | Migrate remaining agents (~100) |
| **Phase 5** | Feb 08+ | Remove old base classes |

---

## Common Issues & Solutions

### Issue: "ImportError: cannot import name 'CanonBaseAgent'"
**Solution:** Update import to `L2ExecutionBaseAgent` from `base_agents` module

### Issue: "TypeError: __init__() missing required argument 'ctx'"
**Solution:** Ensure `ctx` parameter is passed to `super().__init__()`

### Issue: "AttributeError: '_client' is None"
**Solution:** Check that `enable_gemini=True` and Gemini API key is set in `.env`

### Issue: "DeprecationWarning: ExecutionCanonBaseAgent is deprecated"
**Solution:** This is expected during migration. Update imports to remove warning.

---

## Questions?

Refer to:
- `agentic_core/L2_execution/base_agents/L2ExecutionBaseAgent.py` - Source of truth
- `reports/L2_Phase2_Migration_Guide.md` - This guide
- `canon_validator_agentic_v2_thin.py --help` - Validation tool
