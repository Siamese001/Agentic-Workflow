# Windows Path Handling Best Practices

This guide documents Windows path handling standards for the Agentic Workflow codebase, based on the lessons learned from the `DiscoveryError:c:.Git.Agentic-Workflow` bug.

---

## The Problem

Windows uses backslash (`\`) as the path separator, while Unix systems use forward slash (`/`). This difference can cause bugs when:

- Using string `.replace()` operations on paths incorrectly
- Mixing string manipulation with `pathlib.Path` operations
- Displaying paths in error messages without proper normalization

### The Bug

The error `DiscoveryError:c:.Git.Agentic-Workflow` occurred when Windows paths containing backslashes (`C:\Git\Agentic-Workflow`) were incorrectly normalized by replacing backslashes with dots instead of forward slashes, resulting in `c:.Git.Agentic-Workflow`.

**Incorrect (Bug):**
```python
path = r'C:\Git\Agentic-Workflow'
mangled = path.replace('\\', '.')  # Result: 'C:.Git.Agentic-Workflow' ❌
```

**Correct:**
```python
path = r'C:\Git\Agentic-Workflow'
normalized = path.replace('\\', '/')  # Result: 'C:/Git/Agentic-Workflow' ✅
```

---

## The Solution

### Always Use `pathlib.Path`

**Rule #1: Never use `.replace()` on path strings for normalization**

❌ **Incorrect:**
```python
# String manipulation - fragile and error-prone
path_str = str(some_path).replace("\\", "/")
```

✅ **Correct:**
```python
from pathlib import Path

# Use pathlib.Path for all path operations
path = Path(some_path)
normalized = path.as_posix()  # Always returns forward-slash format
```

### Path Operations Reference

| Operation | String Method (❌) | pathlib Method (✅) |
|-----------|-------------------|---------------------|
| Normalize separators | `.replace("\\", "/")` | `.as_posix()` |
| Get absolute path | `os.path.abspath()` | `.resolve()` |
| Join paths | `os.path.join()` | `/` operator |
| Relative path | `os.path.relpath()` | `.relative_to()` |
| Check exists | `os.path.exists()` | `.exists()` |
| Get filename | `os.path.basename()` | `.name` |
| Get parent dir | `os.path.dirname()` | `.parent` |
| Get extension | `os.path.splitext()` | `.suffix` |

---

## Code Examples

### Example 1: Normalizing Agent Paths

```python
from pathlib import Path

def get_canonical_path(agent_path: str | Path) -> str:
    """Return forward-slash normalized path string."""
    return Path(agent_path).as_posix()

# Usage
windows_path = r'C:\Git\Agentic-Workflow\agentic_core\L0_routing'
canonical = get_canonical_path(windows_path)
# Result: 'C:/Git/Agentic-Workflow/agentic_core/L0_routing'
```

### Example 2: Validating Paths Within Project

```python
from pathlib import Path

def validate_path_within_project(path: Path, project_root: Path) -> bool:
    """Validate that a path is within the project root."""
    try:
        path = Path(path).resolve()
        project_root = Path(project_root).resolve()
        path.relative_to(project_root)
        return True
    except ValueError:
        return False

# Usage
project_root = Path(r'C:\Git\Agentic-Workflow')
test_path = project_root / 'agentic_core' / 'L0_routing'
assert validate_path_within_project(test_path, project_root)  # ✅ Passes
```

### Example 3: Converting Module Names (Intentional Dot Replacement)

```python
from pathlib import Path

def path_to_module(path: Path, project_root: Path) -> str:
    """Convert a file path to a Python module name.
    
    This is one of the few cases where .replace('\\', '.') is correct,
    because we're creating a module name, not a path.
    """
    rel_path = path.relative_to(project_root)
    # Convert path separators to dots for module notation
    module = str(rel_path).replace("\\", ".").replace("/", ".")
    # Remove .py extension
    module = module.replace(".py", "")
    return module

# Usage
file_path = Path(r'C:\Git\Agentic-Workflow\agentic_core\L0_routing\utils.py')
module = path_to_module(file_path, Path(r'C:\Git\Agentic-Workflow'))
# Result: 'agentic_core.L0_routing.utils' ✅
```

---

## Testing Guidelines

### Cross-Platform Test Compatibility

Tests must work on both Windows and Unix without platform-specific skips:

```python
import pytest
from pathlib import Path
from unittest.mock import patch

# ✅ Correct: Use mocking for platform-specific behavior
def test_windows_path_normalization():
    """Test Windows path normalization without requiring Windows."""
    # Use string that simulates Windows path
    windows_path = "C:\\Git\\Agentic-Workflow"
    normalized = windows_path.replace("\\", "/")
    assert normalized == "C:/Git/Agentic-Workflow"

# ✅ Correct: Use pathlib which handles cross-platform
def test_pathlib_as_posix():
    """Test pathlib.as_posix() returns forward-slash format."""
    path = Path("C:/Git/Agentic-Workflow")  # Works on all platforms
    posix_path = path.as_posix()
    assert "/" in posix_path
    assert "\\" not in posix_path
```

### Test the RCA Bug Pattern

```python
def test_no_backslash_to_dot_mangling():
    """Ensure the specific RCA bug doesn't occur."""
    test_path = "C:\\Git\\Agentic-Workflow"
    
    # Correct normalization (what our code should do)
    correct = test_path.replace("\\", "/")
    
    # Incorrect mangling (the bug pattern)
    buggy = test_path.replace("\\", ".")
    
    # Verify we don't produce buggy output
    assert "c:.Git" not in correct.lower()
    assert correct == "C:/Git/Agentic-Workflow"
    assert buggy == "C:.Git.Agentic-Workflow"  # This is the bug!
```

---

## Common Pitfalls

### Pitfall 1: Using `chr(92)` Instead of `'\\'`

While both work, `chr(92)` is less readable:

```python
# Works but less readable
path.replace(chr(92), "/")

# Better - explicit backslash
path.replace("\\", "/")
```

### Pitfall 2: Double Escaping in Regex

When using regex with backslashes, remember Python string escaping:

```python
import re

# ❌ Wrong: Regex sees single backslash
pattern = r'C:\Git'  # This matches 'C:Git' (\G is invalid escape)

# ✅ Correct: Raw string for regex
pattern = r'C:\\Git'  # Regex sees C:\Git
```

### Pitfall 3: UNC Path Handling

UNC paths (`\\server\share`) need special handling:

```python
# UNC path normalization
unc_path = r'\\server\share\folder'
normalized = unc_path.replace("\\", "/")
# Result: '//server/share/folder'
```

---

## Error Messages

### Include Both Original and Normalized Paths

When raising errors with paths, include both for debugging:

```python
from pathlib import Path

def validate_and_process(path: str | Path) -> Path:
    """Validate and process a path."""
    original = str(path)
    path_obj = Path(path)
    
    try:
        resolved = path_obj.resolve()
        if not resolved.exists():
            raise FileNotFoundError(
                f"Path not found: {original} "
                f"(resolved: {resolved.as_posix()})"
            )
        return resolved
    except Exception as e:
        raise ValueError(
            f"Path validation failed for {original}: {e}"
        ) from e
```

---

## Summary of Rules

1. **Never use `.replace()` on path strings for normalization** - use `pathlib.Path`
2. **Always import `pathlib.Path`** at the top of files handling paths
3. **Use `.as_posix()`** for forward-slash normalized string representation
4. **Use `.resolve()`** for absolute path resolution
5. **Use `.relative_to()`** for getting relative paths
6. **Test with Windows paths** in unit tests to catch platform-specific bugs
7. **Include both original and normalized paths** in error messages for debugging

---

## References

- **RCA Document:** `docs/reports/rca_discovery_error_path_normalization.md`
- **Audit Results:** `artifacts/path_replace_audit.json`
- **Test Coverage:**
  - `tests/unit/agentic_core/L0_routing/utils/test_path_util.py`
  - `tests/integration/agentic_core/L0_routing/test_windows_path_integration.py`
- **Python Documentation:** [pathlib - Object-oriented filesystem paths](https://docs.python.org/3/library/pathlib.html)
