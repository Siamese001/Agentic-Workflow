# RCA: Test Files Misplaced in data/prompt_governance/misc/

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

**Issue**: Python test files incorrectly placed in `data/prompt_governance/misc/` directory, violating the architectural separation between code and data.

**Impact**:
- 3 misplaced test files in data directory
- Violation of code/data separation principles
- Test infrastructure cluttering production data structure
- SSOT compliance test referencing misplaced files

**Status**: **CRITICAL** - Requires immediate remediation

---

## 1. Problem Analysis

### 1.1 Current State

```
data/prompt_governance/misc/
├── __pycache__/                    # Python cache files (shouldn't exist in data/)
├── test_tests_golden_state_test_datasets.py      (618 bytes)
├── tests_modularity_test_layer_imports.py        (686 bytes)
└── tests_modularity_test_layer_imports_impl.py   (646 bytes)
```

**Total**: 3 Python test files + cache directory

### 1.2 File Analysis

| File | Type | Purpose | Reference |
|------|------|---------|-----------|
| `test_tests_golden_state_test_datasets.py` | Test file | Golden state dataset validation | `tests/guardian/test_ssot_compliance.py:348` |
| `tests_modularity_test_layer_imports.py` | Test shim | Backward compatibility for layer import tests | `tests/guardian/test_ssot_compliance.py:348` |
| `tests_modularity_test_layer_imports_impl.py` | Test implementation | Layer import test implementation | `tests/guardian/test_ssot_compliance.py:348` |

### 1.3 Root Cause Analysis

#### Primary Cause: **Test File Misplacement During Migration**

Test files were incorrectly placed in the data directory during previous refactoring efforts, likely due to:

1. **Ambiguous "misc" Classification**: `misc/` subfolder used as a catch-all for uncategorized files
2. **No Test File Validation**: No automated detection of test files in data directories
3. **Migration Oversight**: Test files moved during consolidation without proper destination validation
4. **Cache Generation**: Python cache files generated, indicating test execution attempts in data directory

#### Secondary Causes:

1. **Missing Governance**: No enforcement preventing Python files in data directories
2. **Test Infrastructure Confusion**: Test files mixed with production data artifacts
3. **Reference Pattern**: SSOT compliance test referencing misplaced files creates circular dependency

---

## 2. Architectural Violation Analysis

### 2.1 Code/Data Separation Violation

**Expected Pattern:**
```yaml
data/prompt_governance/     # Data only (YAML, MD, JSON)
├── executive/*.yaml        # Prompt templates
├── outreach/*.yaml         # Prompt templates
├── resume/*.yaml           # Prompt templates
└── prompt_injections/*.md  # Injection patterns

tests/                      # Tests only (Python files)
├── guardian/
├── unit/
└── integration/
```

**Current Violation:**
```yaml
data/prompt_governance/
├── misc/                   # Contains PYTHON TEST FILES ❌
│   ├── test_*.py          # Test files in data directory
│   └── __pycache__/       # Cache files in data directory
```

### 2.2 Blueprint Compliance Issue

According to `structure_blueprint/_constants.py`:

```yaml
data:
  purpose: "Data storage and processing artifacts."
  allowed_extensions: [".py", ".json", ".md"]  # .py allowed but should be config/data, not tests
  no_cross_layer_imports: True
```

The blueprint allows `.py` files in data directories, but these should be **configuration/data processing files**, not **test files**.

---

## 3. Fix Implementation Plan

### 3.1 Phase 1: Test File Relocation

**Target**: Move all test files to proper test directory structure

```bash
# Create appropriate test directory structure
mkdir -p tests/guardian/data_prompt_governance

# Move test files to canonical test location
mv data/prompt_governance/misc/test_tests_golden_state_test_datasets.py tests/guardian/data_prompt_governance/
mv data/prompt_governance/misc/tests_modularity_test_layer_imports.py tests/guardian/data_prompt_governance/
mv data/prompt_governance/misc/tests_modularity_test_layer_imports_impl.py tests/guardian/data_prompt_governance/

# Remove Python cache directory
rm -rf data/prompt_governance/misc/__pycache__

# Remove empty misc directory
rmdir data/prompt_governance/misc
```

### 3.2 Phase 2: Reference Updates

**File**: `tests/guardian/test_ssot_compliance.py`

**Change**: Update file paths in test references

```python
# BEFORE
"data/prompt_governance/misc/test_tests_golden_state_test_datasets.py",
"data/prompt_governance/misc/tests_modularity_test_layer_imports.py",
"data/prompt_governance/misc/tests_modularity_test_layer_imports_impl.py",

# AFTER
"tests/guardian/data_prompt_governance/test_tests_golden_state_test_datasets.py",
"tests/guardian/data_prompt_governance/tests_modularity_test_layer_imports.py",
"tests/guardian/data_prompt_governance/tests_modularity_test_layer_imports_impl.py",
```

### 3.3 Phase 3: Blueprint Clarification

**File**: `agentic_core/L5_safety/config/structure_blueprint/_constants.py`

**Change**: Add explicit prohibition of test files in data directories

```python
# Add to data territory validation
"forbidden_patterns": [
    r"^test_.*\.py$",           # Test files
    r".*_test\.py$",            # Test files
    r"__pycache__/",            # Python cache directories
]
```

---

## 4. Implementation Results

### 4.1 Migration Completed ✅

**All 3 test files successfully relocated to canonical test location:**

```bash
# Migration Summary
✓ data/prompt_governance/misc/test_tests_golden_state_test_datasets.py     → tests/guardian/data_prompt_governance/
✓ data/prompt_governance/misc/tests_modularity_test_layer_imports.py       → tests/guardian/data_prompt_governance/
✓ data/prompt_governance/misc/tests_modularity_test_layer_imports_impl.py  → tests/guardian/data_prompt_governance/

# Cleanup
✓ data/prompt_governance/misc/__pycache__/ completely removed
✓ data/prompt_governance/misc/ directory completely removed
```

**Verification Results:**
- **Files migrated**: 3/3 (100%)
- **Cache cleanup**: Python cache files removed
- **Directory cleanup**: `misc/` directory removed
- **Reference updates**: Test paths updated in compliance tests

### 4.2 New Canonical Structure

```yaml
tests/guardian/data_prompt_governance/
├── test_tests_golden_state_test_datasets.py      # Golden state validation
├── tests_modularity_test_layer_imports.py        # Layer import test shim
└── tests_modularity_test_layer_imports_impl.py   # Layer import implementation

data/prompt_governance/
├── executive/          # 4 prompt files
├── outreach/           # 4 prompt files
├── resume/             # 3 prompt files
├── prompt_injections/  # 3 injection patterns
└── [other governance files...]  # No test files ✅
```

---

## 5. Verification Commands

```bash
# Verify migration success
find tests/guardian/data_prompt_governance/ -name "*.py" | wc -l  # Should be 3

# Verify old directory removed
test -d data/prompt_governance/misc && echo "FAIL: Old directory exists" || echo "PASS: Old directory removed"

# Verify no Python files in data/prompt_governance
find data/prompt_governance/ -name "*.py" | wc -l  # Should be 0

# Run updated tests
python -m pytest tests/guardian/test_ssot_compliance.py -v
```

---

## 6. Impact Assessment

**Before Fix:**
- ❌ 3 test files in data directory
- ❌ Python cache files in data directory
- ❌ Code/data separation violation
- ❌ Test infrastructure cluttering production data
- ❌ Circular reference in compliance tests

**After Fix:**
- ✅ All test files in proper test directory structure
- ✅ Zero Python files in data/prompt_governance
- ✅ Clean separation of code and data
- ✅ Proper test organization
- ✅ Updated test references

---

## 7. Future Governance

**Prevention Measures:**
1. **Test File Detection**: Automated detection of test files in data directories
2. **Cache Prevention**: Gitignore rules to prevent cache files in data directories
3. **Blueprint Enforcement**: Explicit patterns to forbid test files in data territories
4. **Migration Validation**: Post-migration validation to ensure proper file placement

**Monitoring:**
- Add SSOT compliance check for test files in data directories
- Monitor for Python cache generation in data directories
- Validate test file references during compliance scans

---

**Status**: ✅ **COMPLETE** - All misplaced test files relocated to proper test structure
**Date**: 2026-02-15
**Impact**: Restored code/data separation, cleaned up test infrastructure, improved architectural integrity

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

