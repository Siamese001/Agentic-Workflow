---
description: MCP config SSOT — Global config is the ONLY source of truth
---

# MCP Config SSOT Rule (Updated)

## Source of Truth Location

```
C:\Users\amita\.codeium\windsurf\mcp_config.json
```

This is the **ONLY** location Windsurf reads. The workspace `.windsurf/mcp_config.json` is **DEPRECATED**.

## Hard Constraints

- **ALWAYS** edit `C:\Users\amita\.codeium\windsurf\mcp_config.json` directly
- **NEVER** rely on `.windsurf\mcp_config.json` — it is ignored by Windsurf
- **ALL** Python MCP servers MUST have `cwd` set to `C:\Git\Agentic-Workflow`

## Why The Change

The dual-config approach failed because:
1. CI cannot sync configs to user's home directory
2. Workspace config became a decoy that created drift
3. Manual sync was never reliably executed

**RCA:** `docs/reports/RCA_dual_mcp_config_adg_redis.md`

## Validation

```
python ops_scripts/ci/validate_mcp_config.py
```

Exit 0 = global config is valid, Exit 1 = issues found.

## References

- Deprecated workspace config: `.windsurf/mcp_config.json`
- Global config (edit this): `C:\Users\amita\.codeium\windsurf\mcp_config.json`
- RCA: `docs/reports/RCA_dual_mcp_config_adg_redis.md`
