# RCA: Filesystem MCP Bypassing Write Gate

**Issue**: Filesystem MCP (`mcp5_write_file`, `mcp5_edit_file`) writing files without invoking `pre_write_code` constitutional gates
**Date**: 2026-04-08
**Severity**: HIGH — Governance bypass
**Status**: ✅ RESOLVED — Fix implemented and verified (55/55 tests pass)

## Root Cause

Two facts combine to create the bypass:

1. **`pre_write_code` only fires for Cascade native write tools** (`write_to_file`, `edit`, `multi_edit`). It does not fire when an MCP server writes a file directly.

2. **`pre_mcp_gate.py` had a deliberate fail-open for all non-ADG servers**: line 124 returned `0` immediately for any server other than `adg_sqlite` — including `filesystem`. The infrastructure to intercept MCP calls already existed (`pre_mcp_tool_use` hook → `pre_mcp_gate.py`), but it was not checking filesystem write tools.

```python
# BEFORE — line 124 in pre_mcp_gate.py
if server_name != ADG_SERVER_NAME:
    return 0   # ← filesystem MCP hit this, unconditionally allowed
```

**Secondary constraint discovered**: Windsurf does not pass tool arguments (`path`, `content`) to `pre_mcp_tool_use` hooks. Content-level validation at the MCP gate is therefore impossible — the gate can only act on server name and tool name.

## Evidence

Recent `.py` files written on 2026-04-08 via filesystem MCP without gate interception:
- `tests/unit/ops_scripts/hooks/windsurf/test_hooks_deep_edge_cases.py` (11:44 AM)
- `tests/unit/ops_scripts/hooks/windsurf/test_enforcement_gaps.py` (11:33 AM)
- `tests/unit/ops_scripts/hooks/windsurf/test_post_cascade_cleanup.py` (11:25 AM)
- `tests/unit/ops_scripts/hooks/windsurf/test_post_mcp_audit.py` (11:25 AM)

## Fix Implemented

**File**: `ops_scripts/hooks/windsurf/pre_mcp_gate.py`

Added `FILESYSTEM_SERVER_NAME`, `FILESYSTEM_WRITE_TOOLS`, and `check_filesystem_write_gate()`. Wired into `main()` before the ADG early-return:

```python
FILESYSTEM_SERVER_NAME = "filesystem"
FILESYSTEM_WRITE_TOOLS = {
    "write_file",  # mcp5_write_file — full overwrite
    "edit_file",   # mcp5_edit_file  — line-based edits
}

def check_filesystem_write_gate(tool_name: str) -> int:
    if tool_name in FILESYSTEM_WRITE_TOOLS:
        return _exit_block(
            f"filesystem MCP tool '{tool_name}' is blocked — "
            "use Cascade's native write_to_file / edit / multi_edit tools instead."
        )
    return 0
```

**Routing in `main()`**:
```python
if server_name == FILESYSTEM_SERVER_NAME:
    return check_filesystem_write_gate(tool_name)
```

**Effect**:
- `mcp5_write_file` → **BLOCKED** (exit 2)
- `mcp5_edit_file` → **BLOCKED** (exit 2)
- All read tools (`read_text_file`, `list_directory`, etc.) → **allowed** (exit 0)
- ADG gate logic unchanged

Cascade is redirected to native write tools which fire `pre_write_code` → `pre_write_gate.py` → constitutional anti-pattern and syntax checks.

## Verification

Tests: `tests/unit/ops_scripts/hooks/windsurf/test_pre_mcp_gate.py`
- 13 new tests in `TestCheckFilesystemWriteGate`
- 4 new integration tests in `TestMain`
- 1 stale test updated (`test_filesystem_mcp_allowed` → `test_filesystem_mcp_no_tool_allowed`)
- **Result: 55/55 passed**

## Lessons Learned

1. **Pre-existing hook infrastructure was sufficient** — the fix was 20 lines in one file, not new infrastructure.
2. **MCP tool args are not available in `pre_mcp_tool_use`** — gate logic must be name-based, not content-based; content validation must happen in native write tools.
3. **Fail-open defaults for non-ADG MCPs** should be reviewed whenever a new write-capable MCP is added.

## Related

- `ops_scripts/hooks/windsurf/pre_mcp_gate.py` — fix location
- `ops_scripts/hooks/windsurf/pre_write_gate.py` — constitutional content gate (fires on native writes)
- `.windsurf/hooks.json` — hook wiring
