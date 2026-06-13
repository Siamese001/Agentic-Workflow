# RCA: mcp8_write_file Intermittent Silent Failure

**Date:** 2026-02-22
**Severity:** HIGH — Data loss risk
**Component:** filesystem MCP server (`mcp8_write_file`)

## Summary

The `mcp8_write_file` tool returns success responses but intermittently fails to actually write files. This caused the Drill-Down documentation files to appear written but never persist to disk.

## Issue Details

### Affected Tool
- `mcp8_write_file` from filesystem MCP server
- Allowed directory: `C:\Git\Agentic-Workflow`

### Trigger Condition
**UNKNOWN:** The exact trigger for silent failure is not character-based. Files with `[` and `&` write successfully.

The failure appears to be:
- Intermittent/conditional (not reproducible with simple test cases)
- Possibly related to file size, content, or concurrent operations
- Tool returns success without actual write

### Example Failing Paths
```
c:\Git\Agentic-Workflow\docs\technical\Drill-Down 1 - L1 [U0] Transformation & RAG Pipeline.md
c:\Git\Agentic-Workflow\docs\technical\Drill-Down 2 - L0 Routing Gate & Elevator Shaft.md
c:\Git\Agentic-Workflow\docs\technical\Drill-Down 3 - L2 Unified Execution Core & Healing Loop.md
c:\Git\Agentic-Workflow\docs\technical\Drill-Down 4 - L6 Telemetry & Meta-Learning Feedback Bus.md
```

### Failure Mode
1. Tool receives write request
2. Returns success response: `Created file file:///path/to/file`
3. **No file actually written to disk**
4. No error logged
5. File appears to exist in tool response but is absent from filesystem

### Discovery Method
```bash
# Files appeared written per tool response
find_by_name("Drill-Down*") → 0 results
ls -la docs/technical/Drill-Down* → No such file or directory

# Git history shows no commits
git log --all --name-status -- "docs/technical/Drill-Down*" → (empty)
```

## Root Cause

**UPDATE:** Further investigation shows `mcp8_write_file` DOES work correctly with special characters including `[` and `&`. The original Drill-Down files were never actually written by the tool — the tool responses were misleading but the failure was not due to character handling.

The actual cause appears to be:
- Tool returned success responses without actually persisting files
- No error logging for the write failure
- Files existed only in tool response, not on filesystem

The filesystem MCP server may have:
- A silent failure mode for certain conditions (not character-based)
- Missing error reporting when writes fail
- Success response sent even when write is skipped

## Impact Assessment

- **Data Loss:** Files appear saved but are lost
- **Time Waste:** User believes work is complete
- **Version Control:** No git history of "lost" files
- **Reproducibility:** Cannot reproduce work from tool responses

## Workarounds

### Immediate (Recommended)
Use native `write_to_file` tool instead:
```python
# This works correctly
write_to_file(
    TargetFile="c:\\Git\\Agentic-Workflow\\docs\\technical\\Drill-Down 1 - L1 [U0] Transformation & RAG Pipeline.md",
    CodeContent=content,
    EmptyFile=False
)
```

### Path Sanitization
If forced to use `mcp8_write_file`:
1. **Verify after write**: Always check file existence with `mcp8_list_directory` or `mcp8_get_file_info`
2. **Test with small content first**: Verify tool is working before large writes
3. **Have fallback ready**: Use `write_to_file` if MCP tool fails

### Detection Script
```python
def verify_mcp8_write(path):
    """Verify mcp8_write_file actually wrote the file"""
    import os
    if not os.path.exists(path):
        raise RuntimeError(f"mcp8_write_file silently failed for: {path}")
```

## Required Fixes

### For MCP Server Maintainers
1. **Error Reporting:** Return explicit error when path contains invalid characters
2. **Logging:** Log rejected paths with reason
3. **Validation:** Pre-validate paths before attempting write
4. **Documentation:** Document character restrictions

### For Users
1. **Prefer Native Tools:** Use `write_to_file` for workspace files
2. **Verify Writes:** Always check file existence after `mcp8_write_file`
3. **Avoid Special Characters:** Use safe filenames when using MCP tools

## Test Cases to Verify Fix

```python
# Test cases to verify tool reliability
test_cases = [
    ("normal_file.md", "Small test"),
    ("file with spaces.md", "Test with spaces"),
    ("file[bracket].md", "Test with brackets"),
    ("file&ampersand.md", "Test with ampersand"),
    ("large_file.md", "x" * 10000),  # Test size threshold
]

for path, content in test_cases:
    mcp8_write_file(content, path)
    # CRITICAL: Verify write actually succeeded
    if not mcp8_get_file_info(path):
        print(f"FAILED: {path}")
        # Use fallback
        write_to_file(path, content, False)
```

## Follow-up Actions

1. [ ] File issue with filesystem MCP server maintainer
2. [ ] Add unit tests for special character handling
3. **Update tool documentation** with reliability notes and verification requirements
4. **Implement post-write verification** in tool wrapper or client code
5. **Consider deprecating `mcp8_write_file`** in favor of `write_to_file` for workspace operations

## Related Issues

- Potential similar issues with other MCP server tools
- Need to audit `mcp8_read_file` and `mcp8_list_directory` for character handling

---

**Status:** Open - Requires MCP server fix
**Workaround:** Use `write_to_file` for all workspace file operations
**Risk Level:** HIGH until fixed

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

