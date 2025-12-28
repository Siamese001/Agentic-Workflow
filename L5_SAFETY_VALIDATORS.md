# L5 Safety Validators - Code Quality Enforcement

## Overview

Six new L5 safety validators have been added to enforce code quality and eliminate technical debt:

1. **DuplicateCodeDetectorAgent** - Detects duplicate code blocks
2. **CodeFormatterAgent** - Enforces Black + Ruff formatting
3. **UnusedCleanupAgent** - Removes unused imports and variables
4. **DependencyPruningAgent** - Removes unused Python dependencies
5. **GitHygieneAgent** - Enforces Git repository hygiene
6. **TestCoverageGuardianAgent** - Enforces high test coverage

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

### 5. GitHygieneAgent

**Type**: Batch Validator  
**Location**: `agentic_core/L5_safety/guardrails/git_hygiene_agent.py`

**Purpose**: Enforces Git repository hygiene by detecting stale branches, large files, and uncommitted changes.

**Features**:
- Detects stale branches (no commits in >90 days)
- Identifies uncommitted changes
- Detects unpushed commits
- Dry-run mode by default (reports without deleting)
- Configurable stale threshold

**Configuration**:
```python
agent.dry_run = True       # Default: report only
agent.stale_days = 90      # Days before branch is stale
agent.large_file_mb = 10   # MB threshold for large files
```

**Output**:
```python
{
    "stale_branches": 5,
    "uncommitted": True,
    "unpushed": True,
    "actions_taken": 0,
    "dry_run": True
}
```

**Use Case**: Keep repository clean and prevent branch sprawl.

### 6. TestCoverageGuardianAgent

**Type**: Batch Validator  
**Location**: `agentic_core/L5_safety/verifiability/test_coverage_guardian_agent.py`

**Purpose**: Ultimate verification agent with coverage, mutation testing, and property-based testing.

**Features**:
- **Coverage Analysis**: Line + branch coverage with `--branch` flag
- **Mutation Testing**: Detects test quality via mutmut (killed vs survived mutants)
- **Property Testing**: Auto-generates Hypothesis property tests with strategy mapping
- **HTML Reports**: Interactive coverage visualization
- **Historical Tracking**: Tracks coverage, mutation score, and property tests over time
- **Sovereignty Check**: Passes only if all metrics meet thresholds

**Dependencies**:
```bash
pip install coverage pytest mutmut hypothesis
```

**Configuration**:
```python
agent.min_line_coverage = 95          # Minimum line coverage threshold
agent.min_branch_coverage = 90        # Minimum branch coverage threshold
agent.min_mutation_score = 95         # Minimum mutation score (killed/total)
agent.auto_generate = True            # Auto-generate test stubs
agent.mutation_hints = True           # Show hints for surviving mutants
agent.property_testing_enabled = True # Generate Hypothesis property tests
```

**Output**:
```python
{
    "line_coverage": 87.5,
    "branch_coverage": 82.3,
    "mutation_score": 91.2,
    "property_tests_generated": 10,
    "passed_sovereignty": False
}
```

**Reports Generated**:
- `coverage.json` - Machine-readable coverage data
- `htmlcov/index.html` - Interactive HTML coverage report
- `coverage_history.json` - Historical trends (coverage, mutation, property tests)
- `test_property_*.py` - Auto-generated Hypothesis property tests

**Property Testing**:
The agent automatically discovers functions and classes in `agentic_core`, analyzes their signatures, and generates Hypothesis property tests with appropriate strategies:
- `str` → `st.text(min_size=1)`
- `int` → `st.integers()`
- `float` → `st.floats(allow_nan=False)`
- `bool` → `st.booleans()`
- Unknown → `st.text() | st.integers()`

**Mutation Testing**:
Uses mutmut to introduce mutations (e.g., `+` → `-`, `==` → `!=`) and verifies tests catch them. Low mutation scores indicate weak tests that pass even when code is broken.

**Use Case**: Ensure ultimate test quality with coverage, mutation analysis, and property-based testing for comprehensive verification.

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
