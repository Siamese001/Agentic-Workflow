---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\RCA_dual_mcp_config_divergence.md'
original_relative_path: 'RCA_dual_mcp_config_divergence.md'
source_sha256: 892dd05a4cb734ff9b0dac0ee02eccf82b4bae96d54d8ad13a936a01095a3ba9
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-31'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Dual mcp_config.json Divergence

**Date:** 2026-03-31  
**Severity:** P1 — caused persistent MCP server hangs  
**Status:** RESOLVED  

---

## 1. The Two Files

| Label | Path | Role |
|-------|------|------|
| **Workspace** | `C:\Git\Agentic-Workflow\.windsurf\mcp_config.json` | Version-controlled, edited by Cascade and user |
| **Global** | `C:\Users\amita\.codeium\windsurf\mcp_config.json` | **Actually read by Windsurf at startup** |

### Key Fact

**Windsurf ignores the workspace file.** It reads MCP server definitions exclusively from the user-global path. The workspace file serves only as documentation / version-controlled reference. Any edit to `.windsurf/mcp_config.json` has **zero effect** on running MCP servers until manually copied to the global path.

---

## 2. Root Cause

The two files diverged over time through three mechanisms:

### 2a. Independent Editing
- Cascade edits the **workspace** file (the only one inside the repo it can access).
- The Windsurf IDE Settings UI edits the **global** file directly.
- Neither tool notifies or syncs the other.

### 2b. Copy-Paste Drift
- Manual `Copy-Item` or file copy was used to sync workspace → global.
- But each copy was a **point-in-time snapshot** — subsequent edits to either file created new divergence.

### 2c. JSON Key Ordering
- The workspace file preserves insertion order from manual editing (e.g., `sequential-thinking` first).
- The global file was alphabetically sorted by Windsurf's Settings UI (e.g., `GitKraken` first).
- This caused **different tool prefix mappings** (`mcp0_`, `mcp1_`, etc.) even when the same servers were present.

---

## 3. Divergences Found (at time of investigation)

### 3a. Missing `cwd` in Global Config (5 servers)

| Server | Workspace `cwd` | Global `cwd` |
|--------|-----------------|--------------|
| `enhanced_http` | `C:\Git\Agentic-Workflow` | **(missing)** |
| `pytest` | `C:\Git\Agentic-Workflow` | **(missing)** |
| `sequential-thinking` | `...node_modules\server-sequential-thinking` | **(missing)** |
| `terminal` | `C:\Git\Agentic-Workflow` | **(missing)** |
| `vector_db` | `C:\Git\Agentic-Workflow` | **(missing)** |

**Impact:** Without `cwd`, the IDE spawns Python MCP servers from an arbitrary working directory. This caused the `adg_redis` server to hang (fixed separately by adding `cwd` to it).

### 3b. Server Ordering Mismatch

```
Workspace: sequential-thinking, filesystem, adg_redis, memory, GitKraken, brave-search, ...
Global:    GitKraken, adg_redis, brave-search, deepwiki, enhanced_http, ...
```

**Impact:** Tool prefix mapping (`mcp0_`, `mcp1_`, etc.) differs between what Cascade expects and what the IDE actually provides. This causes tool call failures when the prefix doesn't match the intended server.

### 3c. Stale Entries in Global
- The global config previously contained a `minimal-test` server left over from diagnostic debugging. This was removed during the fix.

---

## 4. Impact

| Symptom | Root Cause |
|---------|-----------|
| `adg_redis` MCP hangs indefinitely | Missing `cwd` → Python spawned in wrong directory |
| Tool prefix confusion (`mcp1_` not found) | Different server ordering in global vs workspace |
| Config changes "not taking effect" | Editing workspace file that Windsurf ignores |
| Silent failures on other Python servers | Missing `cwd` for `pytest`, `terminal`, `enhanced_http`, `vector_db` |

---

## 5. Resolution

### Immediate Fix (2026-03-31)
1. Ran `sync_global_config.py` to overwrite global with workspace (SSOT)
2. All 12 servers now match: 0 field mismatches, 0 missing `cwd` entries
3. Added `socket_connect_timeout=5` and `socket_timeout=5` to `adg_mcp_server.py` as safety net

### Structural Prevention

#### Option A: Workspace-as-SSOT with Sync Script (RECOMMENDED)
- Treat `.windsurf/mcp_config.json` as the **single source of truth**
- Run `python tools/adg/sync_global_config.py` after any config change
- Add to pre-commit or Windsurf workflow

#### Option B: Symlink
```powershell
# Replace global file with symlink to workspace file
Remove-Item "C:\Users\amita\.codeium\windsurf\mcp_config.json"
New-Item -ItemType SymbolicLink `
  -Path "C:\Users\amita\.codeium\windsurf\mcp_config.json" `
  -Target "C:\Git\Agentic-Workflow\.windsurf\mcp_config.json"
```
**Risk:** If Windsurf's Settings UI rewrites the file (not in-place), the symlink breaks.

#### Option C: Single File (no workspace copy)
- Stop maintaining `.windsurf/mcp_config.json` entirely
- Always edit the global file directly
- **Downside:** Config not version-controlled, not reviewable in PR

---

## 6. Invariants to Enforce

1. **SSOT:** `.windsurf\mcp_config.json` is the canonical config; global is a deployment copy
2. **All Python servers MUST have `cwd`** — never rely on IDE default working directory
3. **After any config edit:** run `python tools/adg/sync_global_config.py`
4. **Never edit the global file directly** — always edit workspace first, then sync
5. **Server ordering matters** — keep consistent to avoid tool prefix drift

---

## 7. Files Modified

| File | Change |
|------|--------|
| `C:\Users\amita\.codeium\windsurf\mcp_config.json` | Full sync from workspace SSOT |
| `tools/adg/adg_mcp_server.py` | Added socket timeouts + stderr logging |
| `tools/adg/sync_global_config.py` | Created — canonical sync script |
