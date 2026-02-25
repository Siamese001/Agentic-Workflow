# Pre-commit to Guardian Migration - Validation Matrix

## Original Pre-commit Scope (What Was Moved)

### 1. Ruff Linting Rules (Reduced from F,E,W,B,UP,I to F,E only)
**MOVED TO GUARDIAN:**
- W: Warning (style warnings) → test_code_quality_metrics.py
- B: Flake8-bugbear (common pitfalls) → test_code_quality_metrics.py
- UP: Pyupgrade (Python 3+ syntax) → test_code_quality_metrics.py
- I: isort (import sorting) → test_code_quality_metrics.py

**KEPT IN PRE-COMMIT:**
- F: Pyflakes (undefined names, unused imports) → Essential
- E: Error (syntax errors, indentation) → Essential

### 2. SSOT Structure Validation (Moved from validate_structure.py)
**MOVED TO GUARDIAN:**
- Territory validation → test_comprehensive_structure.py::test_comprehensive_file_placement
- Subfolder structure validation → test_comprehensive_structure.py::test_comprehensive_file_placement
- Forbidden pattern validation → test_comprehensive_structure.py::test_forbidden_directory_usage
- Test file placement validation → test_comprehensive_structure.py::test_test_file_placement
- Package structure completeness → test_comprehensive_structure.py::test_package_structure_completeness

**KEPT IN PRE-COMMIT:**
- Base Agent Location Lock (constitutional) → validate_structure.py --constitutional-only

### 3. Advanced Import Patterns (New Addition)
**MOVED TO GUARDIAN:**
- Circular import detection → test_import_safety.py::test_advanced_import_patterns
- Dynamic import best practices → test_import_safety.py::test_advanced_import_patterns
- Relative import usage → test_import_safety.py::test_advanced_import_patterns
- Import alias conventions → test_import_safety.py::test_advanced_import_patterns

### 4. Code Quality Metrics (New Addition)
**MOVED TO GUARDIAN:**
- File size validation (monolith detection) → test_code_quality_metrics.py::test_file_size_validation
- Cyclomatic complexity analysis → test_code_quality_metrics.py::test_cyclomatic_complexity
- Documentation coverage → test_code_quality_metrics.py::test_documentation_coverage
- Import organization and best practices → test_code_quality_metrics.py::test_import_organization

## Validation Tests

### Test 1: Comprehensive File Placement
```bash
pytest tests/guardian/test_comprehensive_structure.py::TestComprehensiveSSOTStructure::test_comprehensive_file_placement -v
```
**Expected:** Validates all Python files are in valid SSOT territories

### Test 2: Package Structure Completeness
```bash
pytest tests/guardian/test_comprehensive_structure.py::TestComprehensiveSSOTStructure::test_package_structure_completeness -v
```
**Expected:** Checks all packages have proper __init__.py files

### Test 3: Forbidden Directory Usage
```bash
pytest tests/guardian/test_comprehensive_structure.py::TestComprehensiveSSOTStructure::test_forbidden_directory_usage -v
```
**Expected:** Ensures no files in forbidden directories

### Test 4: Test File Placement
```bash
pytest tests/guardian/test_comprehensive_structure.py::TestComprehensiveSSOTStructure::test_test_file_placement -v
```
**Expected:** Validates test files are in tests/ hierarchy

### Test 5: File Size Validation
```bash
pytest tests/guardian/test_code_quality_metrics.py::TestCodeQualityMetrics::test_file_size_validation -v
```
**Expected:** Detects monolith files (>800 LOC, >50KB)

### Test 6: Cyclomatic Complexity
```bash
pytest tests/guardian/test_code_quality_metrics.py::TestCodeQualityMetrics::test_cyclomatic_complexity -v
```
**Expected:** Analyzes function complexity (>15 threshold)

### Test 7: Documentation Coverage
```bash
pytest tests/guardian/test_code_quality_metrics.py::TestCodeQualityMetrics::test_documentation_coverage -v
```
**Expected:** Checks module/class/function documentation

### Test 8: Import Organization
```bash
pytest tests/guardian/test_code_quality_metrics.py::TestCodeQualityMetrics::test_import_organization -v
```
**Expected:** Validates import organization and best practices

### Test 9: Advanced Import Patterns
```bash
pytest tests/guardian/test_import_safety.py::TestImportSafety::test_advanced_import_patterns -v
```
**Expected:** Circular imports, dynamic imports, relative imports, aliases

## RCA: Why Files Aren't Committed

### Issue: 4 Modified Files in Windsurf
1. scripts/validate_structure.py - Modified by ruff-format (line endings, formatting)
2. tests/guardian/test_code_quality_metrics.py - Modified by ruff-format
3. tests/guardian/test_comprehensive_structure.py - Modified by ruff-format
4. tests/guardian/test_import_safety.py - Modified by ruff-format

### Root Cause:
- Pre-commit hooks run ruff-format which modifies files
- Modified files are not automatically staged for commit
- User must manually add and commit formatting changes

### Solution:
1. Stage the formatting changes: `git add -A`
2. Commit with: `git commit -m "Apply ruff-formatting"`
3. Or use: `git commit -a` to include all modified files

## Current Status
- ✅ All scope successfully moved from pre-commit to Guardian tests
- ✅ Pre-commit simplified to essential checks only
- ❌ Formatting changes not yet committed (need manual staging)
- ⏳ Guardian tests need 100% validation run
