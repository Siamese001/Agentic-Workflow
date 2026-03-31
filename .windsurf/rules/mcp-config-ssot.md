---
description: MCP config SSOT enforcement - workspace file is single source of truth
---

# MCP Config SSOT Rule

## SSOT Location

```
.windsurf/mcp_config.json
```

This is the **single source of truth** for all MCP server configuration.

## Hard Constraints

- **NEVER** edit `C:\Users\amita\.codeium\windsurf\mcp_config.json` directly
- **ALWAYS** edit `.windsurf/mcp_config.json` (workspace) first
- **AFTER every edit** to `.windsurf/mcp_config.json`, run the sync script:
  ```
  python tools/adg/sync_global_config.py
  ```
- **ALL Python MCP servers MUST have `cwd`** set to `C:\Git\Agentic-Workflow`
- **NEVER** add a server entry without `cwd` if its command is `python`

## Why

Windsurf reads MCP config from the **user-global** path (`~/.codeium/windsurf/mcp_config.json`), not from the workspace `.windsurf/mcp_config.json`. Without sync, edits to the workspace file have zero effect. Missing `cwd` causes Python servers to hang (RCA: `docs/reports/plans/RCA_dual_mcp_config_divergence.md`).

## Drift Check

To verify configs are in sync without writing:
```
python tools/adg/sync_global_config.py --check
```

Exit 0 = synced, Exit 1 = drifted.

## Reference

- Sync script: `tools/adg/sync_global_config.py`
- RCA: `docs/reports/plans/RCA_dual_mcp_config_divergence.md`
