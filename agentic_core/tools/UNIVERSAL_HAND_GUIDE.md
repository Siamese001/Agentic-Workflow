# Universal Hand Consolidation Guide

## Overview

The "Universal Hand" consolidation has successfully merged all scattered file operations and utilities into a single, sandboxed tool registry with preservation enforcement and security logging.

## Architecture Changes

### Before: Utility Sprawl
- **11+ utility files** with duplicated logic
- **Unguarded file operations**: Direct writes without sandbox validation
- **No preservation checks**: Mass deletions possible
- **Fragmented tools**: `core_utils.py`, `sandbox_utils.py`, `security_utils.py`, `network_utils.py`
- No centralized security logging

### After: Consolidated Tool Registry
- **Single Source of Truth**: `agentic_core/tools/`
- **Sandboxed Operations**: All file I/O validated against excluded directories
- **Preservation Enforcement**: 90% line-count threshold prevents mass deletions
- **Security Logging**: All violations logged to AtomicBlackboard
- **Specialized Modules**: `filesystem.py`, `analysis_ops.py`, `network_ops.py`

## File Structure

```
agentic_core/tools/
├── __init__.py                      # Public API exports
├── definitions.py                   # Pydantic argument models
├── filesystem.py                    # Sandboxed file operations (ENHANCED)
├── execution.py                     # Timeout-protected subprocess
├── analysis_ops.py                  # AST, linting, code quality (NEW)
├── network_ops.py                   # API, Redis, external services (NEW)
├── registry.py                      # FunctionDeclaration generator
└── UNIVERSAL_HAND_GUIDE.md          # This file

Legacy (Thin Wrappers):
├── agentic_core/core_utils_wrapper.py
├── apps_shared/sandbox_utils_wrapper.py
└── agentic_core/core_utils.py       # Original (preserved)
```

## Key Features

### 1. Preservation Enforcement

**The Rule**: If new content is less than 90% of the original file's line count, the write is REJECTED unless `override_preservation=True` is passed by a SystemArchitect agent.

```python
from agentic_core.tools import write_file, WriteFileArgs

# This will be rejected if it deletes >10% of lines
write_file(
    WriteFileArgs(path="file.py", content=new_content),
    blackboard=context.blackboard,
    agent_id="agent_001"
)

# SystemArchitect can override
write_file(
    WriteFileArgs(path="file.py", content=new_content),
    blackboard=context.blackboard,
    agent_id="system_architect",
    override_preservation=True  # Allows mass deletion
)
```

**Example Rejection:**
```
PreservationViolationError: Preservation violation: New content (45 lines) is less than 90% 
of original (100 lines). Minimum required: 90 lines. This would delete 55.0% of the file. 
Set override_preservation=True if this is intentional (SystemArchitect only).
```

### 2. Sandbox Enforcement

**The Rule**: Any tool attempting to touch `.git`, `archives`, or `agentic_core` (from outside) must raise a `SecurityException` and log the attempt to the AtomicBlackboard.

```python
from agentic_core.tools import write_file, WriteFileArgs, SandboxViolationError

try:
    # This will be rejected
    write_file(WriteFileArgs(path=".git/config", content="malicious"))
except SandboxViolationError as e:
    print(f"Sandbox violation: {e}")
    # Logged to AtomicBlackboard automatically
```

**Excluded Directories:**
- `.git` - Version control
- `__pycache__` - Python bytecode
- `archives` - Archived code
- `data` - Data files
- `.venv`, `venv`, `env` - Virtual environments
- `node_modules` - Node dependencies
- `.pytest_cache` - Test cache
- `.idea`, `.vscode` - IDE files
- `build`, `dist`, `eggs` - Build artifacts

### 3. HealingLease Integration

All write operations require HealingLease verification:

```python
from agentic_core.tools import write_file, WriteFileArgs
from agentic_core.infra.context import context

# Acquire lease first
context.blackboard.acquire_healing_lease("agent_001", "file.py")

# Write with lease verification
write_file(
    WriteFileArgs(path="file.py", content=new_content),
    blackboard=context.blackboard,
    agent_id="agent_001"
)

# Release lease
context.blackboard.release_healing_lease("agent_001", "file.py")
```

### 4. Security Logging

All security violations logged to AtomicBlackboard:

```python
# Preservation violation logged automatically
{
    "agent_id": "agent_001",
    "event_type": "PRESERVATION_VIOLATION",
    "file_path": "apps_shared/file.py",
    "details": {
        "original_lines": 100,
        "new_lines": 45,
        "threshold": 90,
        "deletion_percentage": 55.0
    },
    "timestamp": "2025-12-19T14:45:00"
}

# Sandbox violation logged automatically
{
    "agent_id": "agent_001",
    "event_type": "SANDBOX_VIOLATION",
    "file_path": ".git/config",
    "details": {
        "violation_type": "excluded_directory",
        "excluded_dir": ".git"
    },
    "timestamp": "2025-12-19T14:45:00"
}
```

## Specialized Modules

### Analysis Operations (`analysis_ops.py`)

Consolidated from `core_utils.py` and `security_utils.py`:

```python
from agentic_core.tools import (
    validate_python_syntax,
    run_ruff_check,
    run_black_format,
    analyze_ast,
    count_lines_of_code,
    detect_security_issues,
)

# Validate syntax
valid, error = validate_python_syntax("file.py")

# Run linters
returncode, stdout, stderr = run_ruff_check("file.py", fix=True)
returncode, stdout, stderr = run_black_format("file.py")

# Analyze AST
analysis = analyze_ast("file.py")
# Returns: {"functions": [...], "classes": [...], "imports": [...]}

# Count lines
counts = count_lines_of_code("file.py")
# Returns: {"total": 100, "code": 80, "comments": 10, "blank": 10}

# Detect security issues
issues = detect_security_issues("file.py")
# Returns: [{"type": "dangerous_function", "function": "eval", ...}]
```

### Network Operations (`network_ops.py`)

Consolidated from `core_utils.py` and `network_utils.py`:

```python
from agentic_core.tools import (
    string_get,
    string_set,
    incr,
    brave_search,
    execute_cost_controlled_search,
    search_records,
    search_nodes,
    get_from_langcache,
    set_to_langcache,
    get_current_time,
    convert_time,
    issues_get_detail,
    browser_navigate,
    browser_type,
    browser_click,
)

# Redis operations
string_set("key", "value")
value = string_get("key")
count = incr("counter")

# Search operations
results = brave_search("Python async", count=5)
results = execute_cost_controlled_search("Machine Learning")

# Vector search
results = search_records("keywords", index="resume-index", top_k=5)

# Knowledge graph
user_data = search_nodes("user skills")

# Cache operations
cached = get_from_langcache("cache_key")
set_to_langcache("cache_key", "value", ttl=3600)

# Time utilities
current = get_current_time("Europe/London")
converted = convert_time("America/New_York", "2025-12-19T14:00:00", "Asia/Tokyo")

# Issue tracking
issue = issues_get_detail("ISSUE-123")

# Browser automation
browser_navigate("https://example.com")
browser_type("input", "ref123", "Hello World")
browser_click("button", "ref456")
```

### Filesystem Operations (`filesystem.py`)

Enhanced with preservation enforcement:

```python
from agentic_core.tools import (
    read_file,
    write_file,
    move_file,
    list_files,
    delete_file,
    create_directory,
    validate_sandbox,
    ReadFileArgs,
    WriteFileArgs,
    MoveFileArgs,
    ListFilesArgs,
    DeleteFileArgs,
    CreateDirectoryArgs,
)

# Read file
content = read_file(ReadFileArgs(path="apps_shared/file.py"))

# Write file (with preservation check)
write_file(
    WriteFileArgs(path="apps_shared/file.py", content=new_content),
    blackboard=context.blackboard,
    agent_id="agent_001"
)

# Move file
move_file(
    MoveFileArgs(source="old.py", destination="new.py"),
    blackboard=context.blackboard,
    agent_id="agent_001"
)

# List files
files = list_files(ListFilesArgs(directory="apps_shared"))

# Delete file
delete_file(
    DeleteFileArgs(path="temp.py"),
    blackboard=context.blackboard,
    agent_id="agent_001"
)

# Create directory
create_directory(CreateDirectoryArgs(path="new_dir"))

# Validate sandbox
resolved_path = validate_sandbox("apps_shared/file.py")
```

## Migration Guide

### For New Code

Use consolidated tools directly:

```python
from agentic_core.tools import (
    write_file,
    WriteFileArgs,
    validate_python_syntax,
    analyze_ast,
    brave_search,
)
from agentic_core.infra.context import context

# Write with preservation enforcement
write_file(
    WriteFileArgs(path="file.py", content=new_content),
    blackboard=context.blackboard,
    agent_id="agent_001"
)

# Validate syntax
valid, error = validate_python_syntax("file.py")

# Analyze AST
analysis = analyze_ast("file.py")

# Search
results = brave_search("Python async")
```

### For Legacy Code

Use thin wrappers for backward compatibility:

```python
# Core utils (legacy)
from agentic_core.core_utils_wrapper import (
    validate_python_syntax,
    brave_search,
    write_file,
)

# Sandbox utils (legacy)
from apps_shared.sandbox_utils_wrapper import (
    DockerSandbox,
    execute_in_sandbox,
    write_file,
)
```

### Replacing Old Imports

**Before:**
```python
# Old fragmented imports
from agentic_core.core_utils import validate_python_syntax, brave_search
from apps_shared.sandbox_utils import execute_in_sandbox
from apps_shared.security_utils import detect_security_issues
```

**After:**
```python
# New unified import
from agentic_core.tools import (
    validate_python_syntax,
    brave_search,
    detect_security_issues,
)

# Docker sandbox still available
from apps_shared.sandbox_utils import DockerSandbox, execute_in_sandbox
```

## Agent Integration

### Update Agents to Use ToolRegistry

**Before:**
```python
# Agent directly imports utils
from agentic_core.core_utils import validate_python_syntax

class MyAgent:
    def run(self):
        valid, error = validate_python_syntax("file.py")
```

**After:**
```python
# Agent uses ToolRegistry
from agentic_core.tools import create_tool_registry

class MyAgent:
    def __init__(self):
        self.tools = create_tool_registry()
    
    def run(self):
        # Call via registry
        result = self.tools.execute_tool(
            "validate_python_syntax",
            {"file_path": "file.py"}
        )
```

## Benefits

1. **Mass Deletion Prevention**: 90% preservation threshold prevents accidental data loss
2. **Sandbox Enforcement**: Critical directories protected from modification
3. **Security Logging**: All violations logged to AtomicBlackboard
4. **HealingLease Integration**: Write operations require lease verification
5. **Utility Consolidation**: All tools in one location
6. **Type Safety**: Pydantic models prevent validation errors
7. **Backward Compatible**: Thin wrappers maintain legacy API
8. **Specialized Modules**: Clear separation of concerns

## Files Replaced

### Obsolete Utility Files (USE WRAPPERS)
- ⚠️ `agentic_core/core_utils.py` → Use `agentic_core/tools/analysis_ops.py` + `network_ops.py`
- ⚠️ `apps_shared/sandbox_utils.py` → Use `agentic_core/tools/filesystem.py` (Docker preserved)
- ⚠️ `apps_shared/security_utils.py` → Use `agentic_core/tools/analysis_ops.py`
- ⚠️ `apps_shared/network_utils.py` → Use `agentic_core/tools/network_ops.py`
- ⚠️ `scripts/runtime/shared/utils.py` → Use `agentic_core/tools/*`

## Testing

### Unit Tests
```python
import pytest
from agentic_core.tools import (
    write_file,
    WriteFileArgs,
    PreservationViolationError,
    SandboxViolationError,
)

def test_preservation_enforcement():
    """Test that preservation check rejects mass deletions."""
    # Create file with 100 lines
    original = "\n".join([f"line {i}" for i in range(100)])
    write_file(WriteFileArgs(path="test.py", content=original))
    
    # Try to write 45 lines (55% deletion)
    new_content = "\n".join([f"line {i}" for i in range(45)])
    
    with pytest.raises(PreservationViolationError):
        write_file(WriteFileArgs(path="test.py", content=new_content))

def test_sandbox_enforcement():
    """Test that sandbox rejects excluded directories."""
    with pytest.raises(SandboxViolationError):
        write_file(WriteFileArgs(path=".git/config", content="malicious"))
```

### Integration Tests
```bash
# Test consolidated tools
pytest tests/test_universal_hand.py

# Test backward compatibility wrappers
pytest tests/test_legacy_utils.py

# Test preservation enforcement
pytest tests/test_preservation.py
```

## Migration Checklist

- [x] Create specialized tool modules (analysis_ops.py, network_ops.py)
- [x] Implement @validate_sandbox decorator with security logging
- [x] Add line-count preservation check to write_file (90% threshold)
- [x] Update ToolRegistry to include all consolidated tools
- [x] Create thin wrappers for legacy utils files
- [ ] Update all agents to use ToolRegistry instead of direct imports
- [ ] Run full test suite
- [ ] Update documentation

## Next Steps

1. **Update Agent Imports**: Replace direct util imports with ToolRegistry calls
2. **Test Preservation**: Verify 90% threshold prevents mass deletions
3. **Test Sandbox**: Verify excluded directories are protected
4. **Monitor Logs**: Check AtomicBlackboard for security events
5. **Performance Testing**: Benchmark new vs old tools

## Support

For questions or issues with the consolidation:
- Review this guide
- Check `agentic_core/tools/filesystem.py` for preservation logic
- Check `agentic_core/tools/analysis_ops.py` for analysis tools
- Check `agentic_core/tools/network_ops.py` for network tools
- Consult wrapper files for backward compatibility patterns

---

**Last Updated**: December 19, 2025  
**Status**: Phase 4 Complete - Universal Hand Consolidated  
**Next Phase**: Update agent imports and run integration tests
