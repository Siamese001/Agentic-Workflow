# Pascal Sovereignty Architecture - Implementation Guide

## Overview

The **Pascal Sovereignty Fixer** enforces strict file naming conventions across the Agentic-Workflow codebase based on AST (Abstract Syntax Tree) analysis. This ensures architectural clarity and maintainability through consistent naming patterns.

## Architecture Principles

### File Naming Rules

1. **Agents** → `PascalCaseAgent.py`
   - Files containing classes that inherit from `*Agent` or end with `Agent`
   - Example: `DecompositionOrchestratorAgent.py`

2. **Core Classes** → `PascalCase.py`
   - Files containing class definitions (non-agent)
   - Example: `ErrorHandler.py`, `StateManager.py`

3. **Utilities** → `snake_case.py`
   - Files with only functions and constants (no classes)
   - Example: `file_io.py`, `common_patterns.py`

## Current State Analysis

**Validation Results (as of Jan 25, 2026):**
- Total files analyzed: **1,453**
- Compliant files: **735** (50.6%)
- Agent naming violations: **45**
- Class naming violations: **566**
- Utility naming violations: **0**
- **Total violations: 611** (42.0%)

## Usage

### 1. Validation Mode (Recommended First Step)

Check current compliance without making changes:

```bash
python pascal_sovereignty_fixer.py --validate
```

**Output:**
```
[SOVEREIGNTY] INFO: Pascal File Sovereignty Validator
============================================================
Total files analyzed: 1453
Compliant files: 735
Agent naming violations: 45
Class naming violations: 566
Utility naming violations: 0
Total violations: 611
```

### 2. Dry-Run Mode (Preview Changes)

See what would be renamed without executing:

```bash
python pascal_sovereignty_fixer.py --dry-run
```

**Output Preview:**
```
[DETECT] sovereign_auditor_v3.py (CLASS) -> AuditStatus.py
  [PLAN] Rename sovereign_auditor_v3.py -> AuditStatus.py
    [REF] Would update imports in sovereign_mission_control.py

[DETECT] StateManagerAgent.py (CLASS) -> StateManager.py
  [PLAN] Rename StateManagerAgent.py -> StateManager.py
    [REF] Would update imports in StateValidatorAgent.py
```

### 3. Execute Mode (Apply Changes)

Apply all naming fixes:

```bash
python pascal_sovereignty_fixer.py
```

**⚠️ WARNING:** This will rename **611 files** and update **1,273 import references**. Ensure you have:
- Committed all current changes to git
- Run tests before and after
- Reviewed dry-run output

## Technical Implementation

### AST-Based Classification

The fixer uses Python's `ast` module to analyze file contents:

```python
def classify_file_content(path: Path) -> FileType:
    """
    - IGNORE: __init__.py, syntax errors, empty files
    - AGENT: Classes inheriting from *Agent or ending in 'Agent'
    - CLASS: Contains class definitions (non-agent)
    - UTILITY: No classes (functions/constants only)
    """
```

### Windows-Safe Renaming

Three-step rename process to handle case-insensitive filesystems:

```python
def safe_rename_windows(src: Path, dest_name: str):
    """
    Steps: src -> __temp -> dest
    Prevents collisions on Windows case-insensitive FS
    """
```

### Import Refactoring

Automatically updates all import statements:

```python
# Pattern: from module.path import old_name
# Regex: (from\s+[\w\.]+\s+import\s+)old_name\b
# Result: from module.path import NewName
```

## Testing

### Run Test Suite

```bash
python tests/test_pascal_sovereignty.py
```

**Test Coverage (26 tests, 100% pass rate):**

1. **Classification Tests (11 tests)**
   - Agent detection via inheritance
   - Agent detection via naming suffix
   - Standard class detection
   - Utility file detection
   - `__init__.py` handling
   - Syntax error handling
   - Complex inheritance patterns
   - Attribute-based inheritance

2. **Import Regex Tests (2 tests)**
   - Precision matching (avoids partial matches)
   - Word boundary enforcement

3. **Windows Rename Tests (2 tests)**
   - Three-step rename sequence
   - Collision detection

4. **Agent Suffix Tests (2 tests)**
   - Suffix enforcement
   - Already-compliant handling

5. **Compliant Name Tests (3 tests)**
   - Agent name detection
   - Class name detection
   - Utility name detection

6. **Error Handling Tests (2 tests)**
   - File read errors
   - Unicode decode errors

7. **Edge Case Tests (2 tests)**
   - Empty files
   - Comment-only files

8. **Integration Tests (2 tests)**
   - Full renaming workflow
   - Mixed compliance scenarios

## Example Transformations

### Agent Files

```
Before: decomposition_orchestrator.py
After:  DecompositionOrchestratorAgent.py
Reason: Contains class DecompositionOrchestrator(BaseAgent)
```

### Class Files

```
Before: state_manager_agent.py
After:  StateManager.py
Reason: Contains class StateManager (not inheriting from Agent)
```

### Import Updates

```python
# Before
from state_manager_agent import StateManager

# After
from StateManager import StateManager
```

## Safety Features

### 1. Collision Detection
- Checks if target file already exists
- Prevents data loss from overwrites

### 2. Dry-Run Mode
- Preview all changes before execution
- Validate impact scope

### 3. Comprehensive Logging
- All operations logged with severity levels
- Import update tracking
- Error reporting

### 4. Backup Recommendation
- Always commit to git before running
- Test suite validates logic

## Integration with SSOT

The fixer integrates with the Single Source of Truth (SSOT) structure:

```python
from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENTIC_CORE_DIR,
    APPS_RG_DIR,
    APPS_LIC_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.utils.ssot_discovery import get_python_files
```

**Target Directories:**
- `agentic_core/` - Core framework (depth-3)
- `apps_rg/` - Resume Generator app (depth-2)
- `apps_lic/` - LinkedIn Canonical app (depth-2)
- `apps_shared/` - Shared utilities (depth-2)

## Performance Metrics

**Expected Execution Time:**
- Validation: ~5 seconds (1,453 files)
- Dry-run: ~8 seconds (611 renames, 1,273 imports)
- Execution: ~15 seconds (actual file operations)

**Impact:**
- Files to rename: **611**
- Import references to update: **1,273**
- Estimated time: **15-20 seconds**

## Rollback Strategy

If issues occur after execution:

```bash
# Revert all changes
git reset --hard HEAD

# Or revert specific files
git checkout HEAD -- path/to/file.py
```

## Future Enhancements

1. **Incremental Mode**: Only fix new violations
2. **Custom Rules**: User-defined naming patterns
3. **Pre-commit Hook**: Prevent non-compliant commits
4. **IDE Integration**: Real-time validation
5. **Batch Processing**: Process in chunks for large repos

## Critical Analysis

### Strengths
- ✅ AST-based classification (accurate)
- ✅ Windows-safe renaming (three-step process)
- ✅ Comprehensive test coverage (26 tests)
- ✅ Import refactoring automation
- ✅ Dry-run mode for safety

### Limitations
- ⚠️ Utility file naming not enforced (complex heuristics needed)
- ⚠️ Requires manual review of complex inheritance patterns
- ⚠️ Import regex may miss dynamic imports
- ⚠️ No support for relative imports (yet)

### Risk Mitigation
- Always use `--dry-run` first
- Commit to git before execution
- Run full test suite after changes
- Review import updates manually

## Support

For issues or questions:
1. Check test suite: `python tests/test_pascal_sovereignty.py`
2. Run validation: `python pascal_sovereignty_fixer.py --validate`
3. Review logs for specific errors

## License

Part of the Agentic-Workflow project.
