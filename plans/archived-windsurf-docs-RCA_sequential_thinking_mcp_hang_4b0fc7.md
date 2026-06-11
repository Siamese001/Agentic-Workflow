---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\RCA_sequential_thinking_mcp_hang_4b0fc7.md'
original_relative_path: 'RCA_sequential_thinking_mcp_hang_4b0fc7.md'
source_sha256: b93527729ea74368def98f51375606b37eeb66bfb067b53e4056a57a7c676095
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Sequential Thinking MCP Hangs on Every Call

**Status:** ✅ RESOLVED  
**Date:** 2026-03-26  
**Severity:** HIGH — tool completely non-functional despite appearing in tool list

---

## 1. Symptom

Every `mcp7_sequentialthinking` tool call shows "Step was canceled by user" — actually a Windsurf-side timeout/hang, not user cancellation. The tool appears in the available tools list but never returns a result.

## 2. Root Cause

**Windsurf reads MCP config from `C:\Users\amita\.codeium\windsurf\mcp_config.json`, NOT from `.windsurf/mcp_config.json` in the workspace.**

The workspace config (`.windsurf/mcp_config.json`) had been hardened with:
- Direct `node.exe` path (bypasses fnm/npx wrapper)
- `DISABLE_THOUGHT_LOGGING=true` (suppresses stderr chalk rendering)
- Explicit `cwd` for ESM module resolution

But Windsurf was **ignoring it entirely** and reading from the user-global config at `~/.codeium/windsurf/mcp_config.json`, which still had the old broken config:

```json
"sequential-thinking": {
  "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
  "command": "npx"
}
```

### Why `npx` Causes the Hang

Process list evidence showed **two node processes** for sequential-thinking:

| PID | Command | Role |
|-----|---------|------|
| 8540 | `npx-cli.js -y @modelcontextprotocol/server-sequential-thinking` | NPX wrapper (parent) |
| 31828 | `node_modules\...\server-sequential-thinking\dist\index.js` | Actual server (child) |

The npx wrapper creates a **double-pipe chain**: `Windsurf ↔ npx stdin/stdout ↔ child server stdin/stdout`. On Windows, this intermediary process can buffer, drop, or stall JSON-RPC messages. Combined with the missing `DISABLE_THOUGHT_LOGGING` env var (causing stderr chalk output that can interfere with stdio transport), the handshake never completes.

### Proof the Server Itself Works

A direct Python-based JSON-RPC handshake test confirmed the server is 100% functional when launched directly:

```
initialize     → ✅ valid response (protocolVersion: 2024-11-05, server: v0.2.0)
notifications  → ✅ accepted
tools/list     → ✅ returns "sequentialthinking" tool
tools/call     → ✅ returns structured result {thoughtNumber, branches, thoughtHistoryLength}
```

Full round-trip completes in under 1 second.

## 3. Fix Applied

Patched `C:\Users\amita\.codeium\windsurf\mcp_config.json` (the real config Windsurf reads):

**Before:**
```json
"sequential-thinking": {
  "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
  "command": "npx"
}
```

**After:**
```json
"sequential-thinking": {
  "command": "C:\\Users\\amita\\AppData\\Roaming\\fnm\\node-versions\\v24.13.0\\installation\\node.exe",
  "args": [
    "C:\\Users\\amita\\AppData\\Roaming\\fnm\\node-versions\\v24.13.0\\installation\\node_modules\\@modelcontextprotocol\\server-sequential-thinking\\dist\\index.js"
  ],
  "env": {
    "DISABLE_THOUGHT_LOGGING": "true"
  }
}
```

Changes:
1. **Direct `node.exe` path** — eliminates npx double-pipe
2. **Direct `dist/index.js` path** — eliminates npx package resolution
3. **`DISABLE_THOUGHT_LOGGING=true`** — prevents stderr chalk from stalling transport

## 4. Required Action

**Restart Windsurf** to pick up the new config. The old npx-spawned processes will persist until Windsurf restarts.

## 5. Lesson: Two Config Files

| File | Purpose | Who Reads It |
|------|---------|-------------|
| `.windsurf/mcp_config.json` (workspace) | Documentation/reference only | **Nobody** (Windsurf ignores it) |
| `~/.codeium/windsurf/mcp_config.json` (user-global) | Actual MCP server config | **Windsurf** |

Any future MCP config changes must be applied to `~/.codeium/windsurf/mcp_config.json`.

## 6. Diagnostic Evidence

```
# Server launches and prints banner (stderr)
Sequential Thinking MCP Server running on stdio

# Direct handshake test (Python subprocess)
SENT initialize → RECV: {"result":{"protocolVersion":"2024-11-05",...},"id":1}
SENT tools_list → RECV: {"result":{"tools":[{"name":"sequentialthinking",...}]},"id":2}
SENT tools_call → RECV: {"result":{"content":[{"type":"text","text":"{...}"}]},"id":3}

# Process list showing npx double-pipe
PID 8540:  npx-cli.js -y @modelcontextprotocol/server-sequential-thinking  (parent)
PID 31828: server-sequential-thinking\dist\index.js                         (child)
```

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

