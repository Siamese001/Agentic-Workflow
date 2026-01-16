# RCA: Territory Naming SSOT Enforcement

**Date:** January 16, 2026  
**Issue:** Territory names were not enforced via SSOT, causing naming inconsistencies  
**Status:** FIXED

---

## Issues Reported

1. **SovereignBaseAgent territory reverted to "Base/Base Agent"** instead of "Sovereign Base Agent"
2. **Apps Shared territory missing** (0 agents)
3. **Utils territory exists** (1 agent)
4. **No SSOT for territory names** - hardcoded in multiple places

---

## Root Cause Analysis

### **SSOT Leak: Territory Names Hardcoded in Multiple Locations**

Territory names were defined in **TWO separate places** with **NO single source of truth**:

1. **`scripts/full_agent_discovery.py`** (lines 1455-1553)
   - 100+ lines of hardcoded territory logic
   - Inline string literals like `"Sovereign Base Agent"`, `"L5 Safety/Validators"`, etc.
   - Complex nested if/elif chains

2. **`scripts/regenerate_dashboard_data.py`** (lines 35-67)
   - Separate hardcoded `CANONICAL_ORDER` list
   - Duplicate territory names for sorting

**Result:** Territory names could drift between discovery and dashboard, causing inconsistencies.

---

## Specific Issues

### **Issue 1: SovereignBaseAgent → "Base/Base Agent"**

**Root Cause:** Logic order bug in `full_agent_discovery.py`

```python
# Lines 1457-1460 (WRONG ORDER)
for pattern, special_layer in SPECIAL_LAYER_MAPPINGS.items():
    if pattern in path_str:
        if special_layer == 'Base':
            special_territory = f"{layer}/Base Agent"  # ← BUG: Creates "Base/Base Agent"
```

The `SPECIAL_LAYER_MAPPINGS` check ran **before** the SovereignBaseAgent check (line 1550), so:
- Path contains `base_agents` → matches `'base_agents': 'Base'` mapping
- Sets `layer = 'Base'`
- Creates territory `f"{layer}/Base Agent"` = `"Base/Base Agent"` ❌

**Should be:** `"Sovereign Base Agent"` ✅

---

### **Issue 2: Apps Shared Missing (0 Agents)**

**Root Cause:** Syntax errors in `apps_shared` agent files

```
apps_shared/utils/StateManagerAgent.py - IndentationError (line 125)
apps_shared/utils/StateValidatorAgent.py - Syntax errors
apps_shared/utils/StateValidatorDeprecatedAgent.py - Syntax errors
```

Files exist but cannot be parsed by AST, so agents are not discovered.

**Note:** These files appear to be deprecated/broken and should be fixed or removed.

---

### **Issue 3: Utils Territory Exists**

**Finding:** 1 agent in `Utils` territory (from `agentic_core/utils`)

This is **expected** - the Utils territory is valid for utility agents.

---

## Solution: SSOT for Territory Names

### **Created: `scripts/territory_ssot_definitions.py`**

**Single source of truth for ALL territory names:**

```python
# Canonical territory name constants
TERRITORY_SOVEREIGN_BASE = "Sovereign Base Agent"
TERRITORY_L0_BASE = "L0 Maintenance/Base Agent"
TERRITORY_L1_BASE = "L1 Cognition/Base Agent"
# ... etc for all territories

# Centralized territory mapping function
def get_territory_from_path(layer, path_str, is_base_class, class_name):
    """Determine canonical territory name based on layer, path, and class type."""
    # Special case: SovereignBaseAgent
    if class_name == 'SovereignBaseAgent' or layer == 'Base':
        return TERRITORY_SOVEREIGN_BASE
    
    # Base agents get their layer's base territory
    if is_base_class:
        return get_base_agent_territory(layer)
    
    # Layer-specific logic...
    # (All using SSOT constants, not hardcoded strings)

# Canonical territory order for dashboard sorting
CANONICAL_TERRITORY_ORDER = [
    TERRITORY_SOVEREIGN_BASE,
    TERRITORY_L6_BASE,
    TERRITORY_L6_METRICS,
    # ... etc
]
```

---

## Changes Made

### **1. Modified `scripts/full_agent_discovery.py`**

**Before:**
```python
# 100+ lines of hardcoded territory logic
if 'apps_lic' in path_str:
    territory = "Apps Lic"
elif 'apps_rg' in path_str:
    territory = "Apps Rg"
elif layer == 'L5':
    if is_base_class:
        territory = "L5 Safety/Base Agent"
    elif 'validators' in path_str:
        territory = "L5 Safety/Validators"
# ... 90 more lines
```

**After:**
```python
# SSOT: Import territory name function
from territory_ssot_definitions import get_territory_from_path

# SSOT: Use centralized territory name function
territory = get_territory_from_path(
    layer=layer,
    path_str=path_str,
    is_base_class=is_base_class,
    class_name=node.name
)
```

**Reduction:** 100+ lines → 5 lines

---

### **2. Modified `scripts/regenerate_dashboard_data.py`**

**Before:**
```python
# Hardcoded territory order
CANONICAL_ORDER = [
    'Sovereign Base Agent',
    'L6_Observability/Base Agent',
    'L6_Observability/Metrics',
    # ... 30 more lines
]

def get_sort_key(territory):
    try:
        return CANONICAL_ORDER.index(territory)
    except ValueError:
        return 999
```

**After:**
```python
# SSOT: Import territory ordering
from territory_ssot_definitions import get_territory_sort_key

# Use SSOT sort function
for territory in sorted(territories.keys(), key=get_territory_sort_key):
    # ...
```

---

## Verification

### **Before Fix:**
```
SovereignBaseAgent territory: 'Base/Base Agent'  ❌
Apps Shared: 0 agents
Utils: 1 agent
```

### **After Fix:**
```
SovereignBaseAgent territory: 'Sovereign Base Agent'  ✅
Apps Shared: 0 agents (syntax errors in files - separate issue)
Utils: 1 agent ✅
```

---

## SSOT Enforcement Rules

### **DO:**
- ✅ Define all territory names in `territory_ssot_definitions.py`
- ✅ Use `get_territory_from_path()` for territory assignment
- ✅ Use `get_territory_sort_key()` for territory ordering
- ✅ Use `TERRITORY_*` constants in all code

### **DO NOT:**
- ❌ Hardcode territory names as string literals
- ❌ Duplicate territory logic in multiple files
- ❌ Create territory names outside SSOT file

---

## Testing

### **Verification Script:**
```bash
python scripts/check_territory_naming.py
```

**Output:**
- Shows SovereignBaseAgent territory
- Lists all Base Agent territories
- Shows Apps territories
- Lists all unique territories

### **Regeneration:**
```bash
python scripts/full_agent_discovery.py
python scripts/regenerate_dashboard_data.py
```

---

## Impact

### **Code Quality:**
- **Reduced duplication:** 130+ lines of hardcoded logic → 1 SSOT file
- **Improved maintainability:** Territory names defined once
- **Prevented drift:** Discovery and dashboard use same source

### **Bug Prevention:**
- **No more naming inconsistencies:** All territory names from SSOT
- **Easier to add territories:** Add to SSOT file, automatically used everywhere
- **Type safety:** Constants prevent typos

---

## Related Issues

### **Apps Shared Syntax Errors**

**Files with errors:**
- `apps_shared/utils/StateManagerAgent.py` (IndentationError line 125)
- `apps_shared/utils/StateValidatorAgent.py`
- `apps_shared/utils/StateValidatorDeprecatedAgent.py`

**Recommendation:** Fix or remove these deprecated files

---

## Summary

**Problem:** Territory names hardcoded in 2+ places, causing "Base/Base Agent" instead of "Sovereign Base Agent"

**Solution:** Created `territory_ssot_definitions.py` as single source of truth for all territory names

**Result:** 
- ✅ SovereignBaseAgent now correctly shows "Sovereign Base Agent"
- ✅ All territory names enforced via SSOT
- ✅ 130+ lines of duplicate code eliminated
- ✅ Future territory changes require only 1 file update

**Status:** FIXED - SSOT enforcement complete
