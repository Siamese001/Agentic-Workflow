# RCA: Dual MCP Config Problem — ADG Redis

**Date:** 2025-04-03  
**Component:** ADG Redis MCP Server  
**Severity:** High (operational drag, silent failures)

---

## Problem Statement

Two MCP configuration files exist for ADG Redis:
1. **Workspace:** `.windsurf/mcp_config.json` (in repo, version controlled)
2. **Global:** `C:\Users\amita\.codeium\windsurf\mcp_config.json` (user-global, IDE-controlled)

**Windsurf ONLY reads the global config.** The workspace file is ignored, causing drift and runtime failures when they are not manually synced.

---

## Root Cause

### 1. Windsurf Architecture Decision
Windsurf (the IDE) is designed to read MCP server configurations from a **single user-global location**:
- Path: `C:\Users\amita\.codeium\windsurf\mcp_config.json`
- Purpose: Centralized MCP registry across all workspaces
- Rationale: Consistent server availability, no per-project server sprawl

### 2. Workspace Config Is Documentation-Only
The `.windsurf/mcp_config.json` in the repository serves **zero runtime purpose**:
- Windsurf does NOT look at workspace-level MCP configs
- It exists only as "documentation" or "reference" for developers
- Changes here have NO effect until manually copied to global config

### 3. The `cwd` Problem (Historical Incident)
On 2025-03-31, ADG Redis MCP hung because:
- Global config lacked `"cwd": "C:\\Git\\Agentic-Workflow"` for `adg_redis` server
- Without `cwd`, Python process spawned from arbitrary directory
- Relative imports and file resolution failed
- Server hung waiting for file access

**Fix required manual sync** from workspace config (which had correct `cwd`) to global config.

---

## Why Two Configs Exist

| Config | Purpose | Who Updates | Windsurf Reads? |
|--------|---------|-------------|-----------------|
| Global | Runtime server registry | User manually | ✅ YES |
| Workspace | Documentation/reference | Git commits | ❌ NO |

### Historical Reasoning
- Workspace config was created to version-control "desired" MCP setup
- Intention was: "checkout repo → have correct MCP config"
- Reality: Windsurf ignores it, making it a **liability** not an asset

---

## Impact

### Operational Drag
- Every MCP config change requires **manual 2-step sync**:
  1. Edit workspace config (version control)
  2. Copy to global config (test runtime)
- Forgetting step 2 → runtime behavior unchanged → silent confusion

### Silent Failure Modes
1. **Missing `cwd`**: Server hangs or fails to find files
2. **Stale `env`**: Wrong environment variables → wrong behavior
3. **Missing server entry**: Server appears registered but Windsurf can't find it

### Maintenance Burden
- Global config drifts from workspace config over time
- No automated sync mechanism
- No validation that configs match

---

## Solutions Evaluated

### Option A: Single-Source Global Config (Recommended)
**Approach:** Delete workspace config, maintain global only. Document global location.

Pros:
- Eliminates drift entirely
- Source of truth is runtime reality
- No manual sync required

Cons:
- Global config not version-controlled
- Team members must manually share changes

### Option B: Automated Sync Script
**Approach:** Add pre-commit hook or CI gate that syncs workspace → global.

Pros:
- Workspace remains version-controlled
- Automated consistency

Cons:
- Requires tooling to modify files outside repo
- Complex on Windows (global path is user-specific)

### Option C: Windsurf Feature Request
**Approach:** Request Windsurf support workspace-level MCP configs.

Pros:
- Solves at source
- Natural developer expectation

Cons:
- External dependency
- Timeline unknown

---

## Immediate Actions

### 1. Document Global Config Location
Add to `docs/project/MCP_CONFIGURATION.md`:
```
⚠️ CRITICAL: Windsurf reads MCP config from:
    C:\Users\amita\.codeium\windsurf\mcp_config.json

The .windsurf/mcp_config.json in this repo is DOCUMENTATION ONLY.
Changes there have NO EFFECT until manually copied to global config.
```

### 2. Add Sync Workflow
Create `.windsurf/workflows/mcp-config-sync.md`:
```yaml
---
description: Sync MCP config from workspace to global
---
1. Edit .windsurf/mcp_config.json (for version control)
2. Copy entire contents to C:\Users\amita\.codeium\windsurf\mcp_config.json
3. Restart Windsurf or reload window
4. Verify: MCP tools appear in command palette
```

### 3. Validation Script
Create `ops_scripts/ci/validate_mcp_config.py`:
- Compares workspace config vs global config
- Fails CI if drift detected
- Forces explicit sync decisions

---

## Conclusion

The dual-config problem exists because **Windsurf's architecture** (global-only MCP config) conflicts with **developer intuition** (repo-level config). The workspace config is a liability that creates silent drift.

**Recommendation:** Treat workspace config as documentation only. Maintain global config as source of truth. Automate validation to catch drift.

**Status:** Documented, pending decision on Option A vs Option B.

---

## References

- Memory: `824c07f8-0620-44e0-a0b4-94a6af2340a7` — Global config path
- Memory: `bcfbbf60-3476-4536-b27d-80ce3f4854bd` — Historical `cwd` hang incident
- Workspace config: `.windsurf/mcp_config.json`
- Global config: `C:\Users\amita\.codeium\windsurf\mcp_config.json`
