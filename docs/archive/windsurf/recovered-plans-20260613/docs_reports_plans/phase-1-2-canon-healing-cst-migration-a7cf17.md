# Phase 1.2: Canon Healing CST Migration Plan

This plan migrates the CodeHealerAgent's canon healing capabilities from legacy string-based operations to zero-loss CST-based transformations, following the successful pattern established for import healing in Phase 1.1b.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State Analysis

The current `heal_canon()` method in `code_healer_agent.py` uses legacy string manipulation for:
- Adding `__future__` imports
- Fixing bare `except:` clauses

However, the CST transformers already exist but need hardening:
- `SurgicalDocstringInserter` exists but has implementation issues
- `SurgicalBareExceptFixer` exists but needs integration
- Factory functions are ready but need proper violation mapping

## Implementation Steps

### Step 1: Fix SurgicalDocstringInserter Implementation

**File**: `agentic_core/L5_safety/validators/cst_transformers.py`

**Issues to Fix**:
- The current implementation incorrectly creates `cst.Module` instead of updating the body
- Indentation handling is missing for proper docstring insertion
- Need to handle classes/functions with no body (just `pass`)
- Need to differentiate between class and function docstrings

**Required Changes**:
```python
def leave_ClassDef(self, original_node, updated_node):
    # Fix: Use cst.IndentedBlock for proper body structure
    # Fix: Handle existing docstrings correctly
    # Fix: Preserve indentation and formatting
```

### Step 2: Implement Missing Future Import Transformer

**File**: `agentic_core/L5_safety/validators/cst_transformers.py`

**New Transformer**: `SurgicalFutureImportInserter`

**Logic**:
- Check if file already has `__future__` imports in first 10 lines
- Insert at top of file if missing
- Preserve existing imports and comments
- Handle shebang lines and module docstrings

### Step 3: Refactor heal_canon Method

**File**: `agentic_core/L5_safety/policy_engine/code_healer_agent.py`

**Current Issues**:
- Uses string-based line manipulation
- No surgical context creation
- No CST transformer dispatch

**Required Refactor**:
```python
def heal_canon(self, file_path: Path) -> list[HealingAction]:
    # 1. Parse file and detect canon violations
    # 2. Create SurgicalContext objects for each violation
    # 3. Use self.heal_surgical_cst() for zero-loss healing
    # 4. Map results back to HealingAction objects
```

### Step 4: Create Canon Violation Detection

**File**: `agentic_core/L5_safety/policy_engine/code_healer_agent.py`

**Detection Logic**:
- Parse AST to find classes/functions without docstrings
- Check for missing `__future__` imports
- Identify bare `except:` clauses
- Create ViolationConstraint objects with proper coordinates

### Step 5: Comprehensive Testing

**New File**: `tests/unit/agentic_core/L5_safety/test_code_healer_canon_cst.py`

**Test Scenarios**:
1. **Docstring Insertion**:
   ```python
   class MyClass:
       # This comment must stay
       def method(self):
           pass
   ```
   - Assert: Docstring added at top
   - Assert: Comment preserved
   - Assert: Method preserved

2. **Future Import Insertion**:
   ```python
   #!/usr/bin/env python3
   """Module docstring"""

   import os
   ```
   - Assert: Future import added after docstring
   - Assert: Shebang preserved
   - Assert: Module docstring preserved

3. **Bare Except Fixing**:
   ```python
   try:
       risky_operation()
   except:
       pass
   ```
   - Assert: `except:` → `except Exception:`
   - Assert: Indentation preserved

## Technical Implementation Details

### Violation Mapping Strategy
```python
# Map canon violations to transformers
VIOLATION_TO_TRANSFORMER = {
    "missing_docstring": create_docstring_inserter,
    "missing_future_import": create_future_import_inserter,
    "bare_except": create_bare_except_fixer,
}
```

### Surgical Context Creation
```python
# For missing docstring
coordinate = ASTCoordinate(
    line=node.lineno,
    column=node.col_offset,
    node_id=f"class_{name}",
    node_type="ClassDef",
)

violation = ViolationConstraint(
    constraint_type="missing_docstring",
    fix_type="insert",
    message=f"Class {name} missing docstring",
)
```

### CST Transformer Patterns
- **Insertion**: Use `cst.SimpleStatementLine` with `cst.Expr` and `cst.SimpleString`
- **Preservation**: Always check for existing elements before insertion
- **Indentation**: Use `cst.IndentedBlock` for proper body structure

## Success Criteria

1. **Zero-Loss Healing**: All comments, formatting, and structure preserved
2. **Correct Insertion**: Docstrings added at proper locations with correct indentation
3. **Comprehensive Coverage**: All canon violation types handled
4. **Test Coverage**: All scenarios tested with preservation assertions
5. **Integration**: Seamless integration with existing CodeHealerAgent workflow

## Risk Mitigation

- **CST Complexity**: Use existing working patterns from import healing
- **Indentation Issues**: Test with various indentation styles
- **Edge Cases**: Handle empty bodies, nested structures, existing docstrings
- **Performance**: CST parsing is fast, but validate on large files

## Deliverables

1. Updated `cst_transformers.py` with hardened transformers
2. Refactored `heal_canon()` method using CST approach
3. Comprehensive test suite for canon healing
4. Integration verification with existing workflow

This plan ensures zero-loss canon healing while maintaining the established patterns from Phase 1.1b.

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

