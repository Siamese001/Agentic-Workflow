---
description: MCP config SSOT — Workspace config is source of truth, synced to global
tags: [ssot, mcp, config]
---

# MCP Config SSOT Rule

## Source of Truth Location

```
.windsurf/mcp_config.json (workspace, version-controlled)
```

The workspace config is the **SSOT**. The global config at `C:\Users\amita\.codeium\windsurf\mcp_config.json` is a **read-only deployment target** that Windsurf reads at startup.

## Hard Constraints

- **NEVER** edit the global file directly — always edit workspace first
- **AFTER** every edit to `.windsurf/mcp_config.json`, run: `python tools/adg/sync_global_config.py`
- **ALL** Python MCP servers MUST have `"cwd": "C:\\Git\\Agentic-Workflow"`
- **Drift check** (no writes): `python tools/adg/sync_global_config.py --check`

## Why Workspace-First

1. Workspace config is version-controlled and reviewable in PRs
2. CI can validate and gate changes before they reach global
3. Multiple config changes can be batched and tested
4. Rollback is possible via git history

## Validation

```
python ops_scripts/ci/validate_mcp_config.py
```

Exit 0 = global config matches workspace SSOT, Exit 1 = drift detected.

## Enforcement Layers

| Layer | Mechanism |
|-------|-----------|
| Windsurf rule | `.windsurf/rules/mcp-config-ssot.md` (this file) |
| Workflow | `.windsurf/workflows/mcp-config-sync.md` (invoke with `/mcp-config-sync`) |
| Git hook | `.git/hooks/post-commit` — auto-syncs when `mcp_config.json` is committed |
| Sync script | `tools/adg/sync_global_config.py` (validates, backs up, syncs, verifies) |

## References

- Workspace SSOT: `.windsurf/mcp_config.json`
- Global target (read-only): `C:\Users\amita\.codeium\windsurf\mcp_config.json`
- Sync script: `tools/adg/sync_global_config.py`
- RCA: `docs/reports/plans/RCA_dual_mcp_config_divergence.md`
