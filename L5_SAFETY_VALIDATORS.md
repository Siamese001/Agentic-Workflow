# L5 Safety Validators - Code Quality Enforcement

## Overview

Five new L5 safety validators have been added to enforce code quality and eliminate technical debt:

1. **DuplicateCodeDetectorAgent** - Detects duplicate code blocks
2. **CodeFormatterAgent** - Enforces Black + Ruff formatting
3. **UnusedCleanupAgent** - Removes unused imports and variables
4. **DependencyPruningAgent** - Removes unused Python dependencies
5. **GitHygieneAgent** - Enforces Git repository hygiene

## Validators

### 1. DuplicateCodeDetectorAgent

**Type**: Batch Validator  
**Location**: `agentic_core/L5_safety/guardrails/duplicate_code_detector_agent.py`

**Purpose**: Detects exact duplicate code blocks across the entire codebase using token-based hashing.

**Features**:
- Ignores whitespace and comments (uses normalized hashing)
- Configurable minimum block size (default: 10 lines)
- Limits detailed reporting to prevent output overflow
- Fast scanning using MD5 hashing

**Configuration**:
```python
agent.min_lines = 10      # Minimum block size to flag
agent.max_report = 20     # Limit detailed reporting
```

**Output**:
```python
{
    "duplicates_found": 15,
    "instances_eliminated_potential": 45,
    "details": [
        [("utils/file1.py", 10), ("utils/file2.py", 25)],
        ...
    ]
}
```

**Use Case**: Identify code that should be refactored into shared utilities.

### 2. CodeFormatterAgent

**Type**: Atomic Validator  
**Location**: `agentic_core/L5_safety/guardrails/code_formatter_agent.py`

**Purpose**: Enforces consistent code formatting using Black and Ruff.

**Features**:
- Runs Black formatter for consistent style
- Runs Ruff auto-fix for linting issues
- Reports when files are reformatted
- Gracefully handles missing tools

**Dependencies**:
```bash
pip install black ruff
```

**Output**:
```python
{
    "healed": True,
    "action": "formatted"
}
```

**Use Case**: Ensure all code follows project style guidelines automatically.

### 3. UnusedCleanupAgent

**Type**: Atomic Validator  
**Location**: `agentic_core/L5_safety/guardrails/unused_cleanup_agent.py`

**Purpose**: Removes unused imports and variables using autoflake.

**Features**:
- Removes all unused imports
- Removes unused variables
- In-place file modification
- Safe and conservative cleanup

**Dependencies**:
```bash
pip install autoflake
```

**Output**:
```python
{
    "healed": True,
    "action": "unused_removed"
}
```

**Use Case**: Clean up dead code and reduce file size/complexity.

### 4. DependencyPruningAgent

**Type**: Batch Validator  
**Location**: `agentic_core/L5_safety/guardrails/dependency_pruning_agent.py`

**Purpose**: Detects and removes unused Python dependencies from requirements.txt using deptry.

**Features**:
- Uses deptry for accurate AST-based analysis
- Dry-run mode by default (comments out instead of deleting)
- Regex-based package name extraction
- Safe handling of version specifiers

**Dependencies**:
```bash
pip install deptry
```

**Configuration**:
```python
agent.dry_run = True  # Default: comment out instead of delete
```

**Output**:
```python
{
    "unused_found": 5,
    "removed": 5,
    "dry_run": True
}
```

**Use Case**: Keep requirements.txt lean and reduce installation time/size.

## Integration with Canon Validator

These validators are automatically loaded by `canon_validator_agentic_v2.py` if available:

```python
# [L5 PURITY] New cleanup validators
try:
    from agentic_core.L5_safety.guardrails.duplicate_code_detector_agent import DuplicateCodeDetectorAgent
except ImportError:
    DuplicateCodeDetectorAgent = None

try:
    from agentic_core.L5_safety.guardrails.code_formatter_agent import CodeFormatterAgent
except ImportError:
    CodeFormatterAgent = None

try:
    from agentic_core.L5_safety.guardrails.unused_cleanup_agent import UnusedCleanupAgent
except ImportError:
    UnusedCleanupAgent = None
```

## Usage

### Standalone Usage

```python
from pathlib import Path
from agentic_core.L5_safety.guardrails import (
    DuplicateCodeDetectorAgent,
    CodeFormatterAgent,
    UnusedCleanupAgent
)

# Duplicate detection
detector = DuplicateCodeDetectorAgent(Path("."), ctx)
result = await detector.execute()
print(f"Found {result['duplicates_found']} duplicate blocks")

# Format a file
formatter = CodeFormatterAgent(Path("."), ctx)
result = await formatter.execute("path/to/file.py")
if result["healed"]:
    print("File formatted")

# Clean unused code
cleaner = UnusedCleanupAgent(Path("."), ctx)
result = await cleaner.execute("path/to/file.py")
if result["healed"]:
    print("Unused code removed")
```

### Via Canon Validator

The validators are automatically integrated when running the canon validator:

```bash
python canon_validator_agentic_v2.py --target agentic_core
```

Output:
```
[+] DuplicateCodeDetectorAgent ARMED — code uniqueness enforced
[+] CodeFormatterAgent ARMED — Black + Ruff enforced
[+] UnusedCleanupAgent ARMED — removing dead imports/variables
```

## Installation

Install required dependencies:

```bash
pip install black ruff autoflake
```

Or add to `requirements.txt`:
```
black>=23.0.0
ruff>=0.1.0
autoflake>=2.0.0
```

## Benefits

### Code Quality
- **Consistency**: All code follows the same style (Black)
- **Cleanliness**: No unused imports or variables
- **DRY Principle**: Duplicate code is identified for refactoring

### Developer Experience
- **Automatic**: Formatting and cleanup happen automatically
- **Fast**: Validators run quickly using efficient algorithms
- **Safe**: Conservative cleanup that won't break code

### Maintenance
- **Reduced Debt**: Less duplicate code to maintain
- **Easier Reviews**: Consistent formatting reduces review friction
- **Smaller Codebase**: Removing unused code reduces complexity

## Limitations

### DuplicateCodeDetectorAgent
- Only detects exact duplicates (after normalization)
- May miss semantic duplicates with different implementations
- Minimum block size may miss smaller duplicates

### CodeFormatterAgent
- Requires Black and Ruff to be installed
- May conflict with custom formatting preferences
- Cannot fix all linting issues automatically

### UnusedCleanupAgent
- May miss dynamically used imports (e.g., `__import__()`)
- Conservative - may leave some unused code
- Requires autoflake to be installed

## Best Practices

1. **Run validators regularly** as part of CI/CD pipeline
2. **Review changes** before committing formatted code
3. **Configure Black** in `pyproject.toml` for project-wide settings
4. **Use with hygiene validator** for comprehensive cleanup
5. **Test after cleanup** to ensure nothing broke

## Example Workflow

```bash
# 1. Detect duplicates
python canon_validator_agentic_v2.py --target agentic_core

# 2. Review duplicate report
# Identify code to refactor into shared utilities

# 3. Format all code
black agentic_core/

# 4. Clean unused imports
autoflake --in-place --remove-all-unused-imports -r agentic_core/

# 5. Run tests
pytest

# 6. Commit changes
git add -A
git commit -m "chore: enforce code quality standards"
```

## Future Enhancements

- **Semantic duplicate detection** using AST analysis
- **Complexity metrics** (cyclomatic complexity, cognitive complexity)
- **Security scanning** for common vulnerabilities
- **Performance profiling** to identify slow code
- **Documentation coverage** checking

## Summary

The L5 safety validators provide automated code quality enforcement:
- **DuplicateCodeDetectorAgent**: Find and eliminate duplicate code
- **CodeFormatterAgent**: Enforce consistent style with Black + Ruff
- **UnusedCleanupAgent**: Remove dead imports and variables

Together with the hygiene validator, these tools help maintain a clean, consistent, and high-quality codebase.
