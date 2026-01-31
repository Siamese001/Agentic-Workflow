# Pre-commit Scope Analysis and Recommendations

## Current Pre-commit Configuration Scope

### TIER 1: Ruff Linting and Formatting
**Current Scope:**
- **Ruff (Lint)**: Basic Python linting with rules F,E,W,B,UP,I
  - F: Pyflakes (undefined names, unused imports)
  - E: Error (syntax errors, indentation)
  - W: Warning (style warnings)
  - B: Flake8-bugbear (common pitfalls)
  - UP: Pyupgrade (Python 3+ syntax)
  - I: isort (import sorting)
- **Ruff (Format)**: Code formatting
- **Exclusions**: archives/, .sovereign_healing_backup/

### TIER 2: Essential Checks
**Current Scope:**
1. **Constitutional Base Agent Lock**
   - Validates all *BaseAgent.py files are in agentic_core/base_agents/
   - Entry: `python scripts/validate_structure.py`
   - Files: `.*BaseAgent\.py$`

2. **Pycache Purge**
   - Removes all __pycache__ folders
   - Entry: `python ops_scripts/maintenance/purge_cache.py --quiet`

## Guardian Tests Coverage

### Current Guardian Test Suite:
1. **test_import_safety.py** (58KB)
   - Nuclear Import Sweep (global import crawl)
   - Ghost Import Detection
   - Import Waterfall Violations (core contamination)
   - Internal Gravity Leaks (unidirectional dependencies)
   - Cross-App Import Violations
   - SSOT Violations (tracked as technical debt)

2. **test_ssot_alignment.py** (28KB)
   - Naming Convention Violations (Agent/Mixin naming)
   - Path Depth Violations (>5 levels deep)
   - Orphan Directories
   - Missing Blueprint Paths
   - Sub-Atomic Granularity (monolith files >800 LOC)

3. **test_mro_integrity.py** (38KB)
   - Diamond of Death Detection
   - Redundant Mixin Check
   - Method Resolution Order validation

4. **test_ssot_compliance.py** (28KB)
   - Void Compliance (empty files/directories)
   - Sub-Atomic Granularity
   - Blueprint compliance

5. **test_manual_verification.py** (11KB)
   - Manual verification of detection capabilities
   - Creates temporary violations to verify tests work

6. **test_pascal_edge_cases.py** (3KB)
   - Pascal naming edge cases

7. **test_subatomic_compliance.py** (14KB)
   - Subatomic testing compliance

## Recommendations: What Should Move to Guardian Tests

### 🔄 **MOVE to Guardian Tests**

#### 1. **Enhanced SSOT Validation** (from validate_structure.py)
**Currently in pre-commit:**
- Base Agent Location Lock (already constitutional - keep in pre-commit)
- Basic territory validation

**Move to Guardian:**
- Comprehensive SSOT structure validation
- Forbidden directory checks
- Test file placement validation
- Logic file location validation

#### 2. **Import Safety Deep Dive**
**Currently in pre-commit:**
- Basic import linting (ruff F,E)

**Already in Guardian (good):**
- Ghost Import Detection
- Import Waterfall Violations
- Internal Gravity Leaks
- Cross-App Import Violations

#### 3. **Code Quality Metrics**
**Currently in pre-commit:**
- Basic formatting (ruff-format)

**Move to Guardian:**
- File size validation (>800 LOC monoliths)
- Path depth validation (>5 levels)
- Naming convention validation
- Documentation coverage

### ✅ **KEEP in Pre-commit**

#### 1. **Constitutional Base Agent Location Lock**
- **Reason**: Critical constitutional rule
- **Impact**: Prevents breaking the entire inheritance hierarchy
- **Speed**: Fast (<1s)
- **Scope**: Only *BaseAgent.py files

#### 2. **Basic Linting and Formatting**
- **Reason**: Developer experience, code consistency
- **Impact**: Prevents syntax errors and formatting issues
- **Speed**: Fast (<2s)
- **Scope**: Staged files only

#### 3. **Pycache Purge**
- **Reason**: Repository hygiene
- **Impact**: Prevents cache issues
- **Speed**: Fast (<1s)
- **Scope**: Entire repo

### 📋 **Proposed New Pre-commit Configuration**

```yaml
# .pre-commit-config.yaml
# MINIMAL: Only essential fast checks
# Comprehensive validation moved to Guardian tests/CI

repos:
  # =========================================================================
  # TIER 1: Essential Linting and Formatting (Staged Files Only)
  # =========================================================================
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.13
    hooks:
      - id: ruff
        name: Ruff (Lint)
        args: [--fix, --select, "F,E"]  # Only critical errors
        exclude: ^(archives/.*|\.sovereign_healing_backup/.*)
      - id: ruff-format
        name: Ruff (Format)
        exclude: ^(archives/.*|\.sovereign_healing_backup/.*)

  # =========================================================================
  # TIER 2: Constitutional Rules Only
  # =========================================================================
  - repo: local
    hooks:
      # [CONSTITUTIONAL] Base Agent Location Lock - CANNOT be disabled
      - id: check-base-agent-location
        name: Constitutional Base Agent Lock
        entry: python scripts/validate_structure.py --constitutional-only
        language: python
        files: .*BaseAgent\.py$
        
      - id: purge-cache
        name: Pycache Purge
        entry: python ops_scripts/maintenance/purge_cache.py --quiet
        language: python
        pass_filenames: false
        always_run: true
```

### 📋 **Proposed Guardian Test Enhancements**

#### 1. **New: test_comprehensive_structure.py**
```python
def test_comprehensive_ssot_structure():
    """Comprehensive SSOT structure validation"""
    # Validate all files are in approved locations
    # Check for forbidden directory usage
    # Validate test file placement
    # Check logic file locations
    # Validate package structure completeness
```

#### 2. **Enhance: test_import_safety.py**
```python
def test_advanced_import_patterns():
    """Advanced import pattern validation"""
    # Circular import detection
    # Dynamic import validation
    # Relative import best practices
    # Import grouping and sorting
```

#### 3. **New: test_code_quality_metrics.py**
```python
def test_code_quality_metrics():
    """Code quality and maintainability metrics"""
    # File size validation
    # Cyclomatic complexity
    # Documentation coverage
    # Test coverage metrics
```

## Implementation Plan

### Phase 1: Simplify Pre-commit (Immediate)
1. Update `.pre-commit-config.yaml` to minimal configuration
2. Modify `validate_structure.py` to accept `--constitutional-only` flag
3. Test pre-commit hook speed (<5 seconds)

### Phase 2: Enhance Guardian Tests (Next Sprint)
1. Create `test_comprehensive_structure.py`
2. Create `test_code_quality_metrics.py`
3. Enhance existing tests with moved validations
4. Add to CI/CD pipeline

### Phase 3: CI/CD Integration (Following Sprint)
1. Ensure Guardian tests run on every PR
2. Add failure notifications for Guardian test failures
3. Create dashboards for technical debt tracking
4. Automated remediation suggestions

## Benefits of This Approach

### ✅ **Pre-commit Benefits**
- **Speed**: <5 seconds execution
- **Reliability**: No circular dependencies
- **Developer Experience**: Fast feedback on critical issues
- **Focus**: Only constitutional and formatting rules

### ✅ **Guardian Tests Benefits**
- **Comprehensive**: Full architectural validation
- **Context**: Can access entire codebase
- **Flexibility**: Complex validation logic
- **Reporting**: Detailed violation reports and technical debt tracking

### ✅ **Overall Benefits**
- **Clear Separation**: Fast local checks vs comprehensive validation
- **Scalability**: Guardian tests can grow without slowing development
- **CI/CD Ready**: Comprehensive validation in pipeline
- **Technical Debt Tracking**: Systematic approach to managing violations

## Conclusion

Move comprehensive validation from pre-commit to Guardian tests while keeping only essential fast checks in pre-commit. This provides the best balance of developer experience and architectural integrity.

---
Report Generated: 2026-01-31 05:07:00
Next Review: After Phase 1 implementation
