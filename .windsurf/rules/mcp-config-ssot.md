---
trigger: glob
description: Apply when reading or editing the MCP server configuration file to enforce SSOT discipline, auto-sync rules, and secret handling constraints.
globs:
  - ".windsurf/mcp_config.json"
---
# MCP Config SSOT Rule

## Source of Truth

```
.windsurf/mcp_config.json           ← EDIT HERE (repo-local, version-controlled, Windsurf mcpServers format)
~/.codeium/windsurf/mcp_config.json ← auto-synced on save via hook (Windsurf reads this at startup)
```

**`.windsurf/mcp_config.json` is the ONE SSOT.** It uses the native Windsurf `mcpServers` JSON
format. There is no YAML layer, no sync script, no mirror anywhere else in the repo.

**Auto-sync:** The `post_write_mcp_config_sync.py` hook fires automatically on every save of
`.windsurf/mcp_config.json` and copies it to `~/.codeium/windsurf/mcp_config.json`.
Restart Windsurf after saving to apply the new config.

## Format

```json
{
  "mcpServers": {
    "ServerName": {
      "command": "...",
      "args": [...],
      "env": { "KEY": "value" },
      "disabled": false
    }
  }
}
```

- Use `${env:VAR_NAME}` for secrets (Windsurf resolves from its secrets store)
- Stay under the **100 tool limit** across all enabled MCP servers
- API keys as `${env:VAR_NAME}` placeholders only — never hardcoded

## Adding / Removing MCP Servers

1. Edit `.windsurf/mcp_config.json`
2. Save — hook auto-copies to `~/.codeium/windsurf/mcp_config.json`
3. Restart Windsurf
4. Update `docs/reference/MCP_Registry.md`
5. Run health check: `python ops_scripts/ci/mcp_health_check.py`

## Hard Constraints

- **NEVER** add a `config/mcp_servers.yaml` layer — archived in W5.2, do not restore
- **NEVER** add a sync script — the YAML sync infra is archived in `tools/archive/mcp_yaml_infra_w5.2/`
- **NEVER** create a second copy of MCP config anywhere in the repo
- **DO NOT** exceed 100 total tools across all MCPs — Windsurf hard limit

## Enforcement

| Layer | Mechanism |
|-------|-----------|
| Windsurf rule | This file (triggers on `.windsurf/mcp_config.json` edits) |
| T1 hook | `post_write_mcp_config_sync.py` — auto-syncs to global on every save of mcp_config.json |
| T1 hook | `post_write_audit.py` — JSON lint on every mcp_config.json write |
| T1 hook | `pre_write_gate.py` — blocks deletion of mcp_config.json (DENY) |
| Drift check | `tools/generate/integration/mcp_drift.py` — runs during ADG generation |
| Health check | `python ops_scripts/ci/mcp_health_check.py` |

## References

- Repo SSOT: `.windsurf/mcp_config.json`
- Global (Windsurf reads): `~/.codeium/windsurf/mcp_config.json`
- Registry: `docs/reference/MCP_Registry.md`
- Archive: `tools/archive/mcp_yaml_infra_w5.2/` (YAML infra + sync script — do not restore)
- ADR: `docs/architecture/adr/ADR-002-mcp-config-single-sync-script.md`
