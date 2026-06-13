# RCA: timeout_decorator.py Misplacement Fix

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Root Cause Analysis

The `timeout_decorator.py` file was incorrectly placed in `agentic_core/base_agents/` directory, violating the structure blueprint in multiple ways:

1. **Classification Violation**: The file contains utility functionality (a decorator) but was placed in a directory reserved for agent base classes
2. **Location Violation**: `base_agents/` is specifically for base agent classes, not utility decorators
3. **Missing Routing Rules**: No structure blueprint rules existed for `*_decorator.py` files

## Issues Identified

- **File**: `agentic_core/base_agents/timeout_decorator.py` ❌
- **Correct Location**: Should be in utils subfolder according to classification
- **Missing Blueprint Entry**: No routing rule for decorator files

## Fix Implementation

### 1. Updated Structure Blueprint Configuration

**File**: `agentic_core/L5_safety/config/structure_blueprint/_constants.py`

- Added routing rule: `"*_decorator.py": "utils"` to L0_routing layer
- Added `utils` subfolder to L0_routing extra_subfolders

**File**: `agentic_core/L5_safety/config/structure_blueprint/classification.py`

- Added pattern: `r"_decorator\.py$": "UTILITY"` to CLASSIFICATION_SUFFIX_PATTERNS
- Added mapping: `"_decorator.py": "utils"` to SUFFIX_TO_FOLDER
- Added compound suffix conflict: `(r"_agent_decorator$", "AGENT", "UTILITY", "timeout_agent_decorator.py")`

### 2. File Relocation

- **Moved**: `agentic_core/base_agents/timeout_decorator.py` → `agentic_core/L0_routing/utils/timeout_decorator.py`
- **Updated** file docstring to reflect new canonical location
- **Updated** `agentic_core/L0_routing/utils/__init__.py` to export timeout
- **Updated** shim file `agentic_core/L0_routing/utils/timeout_decorator_util.py` to import from new location

### 3. Import Updates

Updated 63 files across the codebase to use the new import path:

- **Old**: `from agentic_core.base_agents.timeout_decorator import timeout`
- **New**: `from agentic_core.L0_routing.utils.timeout_decorator import timeout`

### 4. Test Updates

**File**: `tests/unit_min_deps/test_decorator_shim_contract.py`

- Updated test class documentation to reflect new canonical location
- Updated import references in test methods
- Updated comments to reference new location

## Verification

✅ **Import Test**: Canonical location imports work correctly
✅ **Shim Test**: Backward compatibility shim works correctly
✅ **Structure Compliance**: File now follows structure blueprint rules
✅ **Classification**: Decorator files now properly classified as UTILITY

## Files Changed

1. `agentic_core/L5_safety/config/structure_blueprint/_constants.py` - Added routing rules
2. `agentic_core/L5_safety/config/structure_blueprint/classification.py` - Added classification patterns
3. `agentic_core/L0_routing/utils/timeout_decorator.py` - Moved and updated
4. `agentic_core/L0_routing/utils/timeout_decorator_util.py` - Updated shim
5. `agentic_core/L0_routing/utils/__init__.py` - Added export
6. `tests/unit_min_deps/test_decorator_shim_contract.py` - Updated tests
7. 63 source files - Updated import paths

## Impact

- **Zero Breaking Changes**: Backward compatibility maintained via shim
- **Structure Compliance**: File now follows architectural rules
- **Future-Proof**: Decorator files now have proper classification and routing
- **Maintainability**: Clear separation between agent base classes and utilities

## Canonical Import Path

```python
# New canonical location (use this for new code)
from agentic_core.L0_routing.utils.timeout_decorator import timeout

# Legacy shim (still works for backward compatibility)
from agentic_core.L0_routing.utils.timeout_decorator_util import timeout
```

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

