---
trigger: glob
globs:
  - ".windsurf/mcp_config.json"
---
# MCP Config SSOT Rule

## Source of Truth

```
.windsurf/mcp_config.json  (repo-local, version-controlled)
C:\Users\amita\.codeium\windsurf\mcp_config.json  (global — Windsurf reads this at startup)
```

**The repo-local `.windsurf/mcp_config.json` is the SSOT.** Edit it directly. The global file is
a manual sync target — update it via Windsurf UI or copy the repo file when servers change.

The YAML layer (`config/mcp_servers.yaml`, `tools/adg/sync_yaml_to_global.py`) was archived in
W5.2 (see `tools/archive/mcp_yaml_infra_w5.2/`). Do not recreate it.

## Editing MCP Config

1. Edit `.windsurf/mcp_config.json` directly
2. Use `${env:VAR_NAME}` for environment variables (Windsurf native interpolation)
3. Stay under the **100 tool limit** across all enabled MCP servers
4. Run health check: `python ops_scripts/ci/mcp_health_check.py`

## Hard Constraints

- **NEVER** add a `config/mcp_servers.yaml` layer — confirmed overkill (ADR-002)
- **NEVER** use `${VAR:-default}` shell syntax — use `${env:VAR_NAME}` instead
- **DO NOT** exceed 100 total tools across all MCPs — Windsurf hard limit
- **API keys** as `${env:VAR_NAME}` placeholders only — never hardcoded

## Adding / Removing MCP Servers

Before adding a new MCP server, check `docs/reference/MCP_Registry.md` to verify:
- No existing MCP already covers this capability
- Tool count stays under 100 after addition

After removing a server, update `docs/reference/MCP_Registry.md`.

## Enforcement

| Layer | Mechanism |
|-------|-----------|
| Windsurf rule | This file (triggers on `.windsurf/mcp_config.json` edits) |
| T1 hook | `post_write_audit.py` — JSON-native lint on every mcp_config.json write |
| T1 hook | `pre_write_gate.py` — blocks deletion of mcp_config.json (DENY) |
| Health check | `python ops_scripts/ci/mcp_health_check.py` |

## References

- Repo SSOT: `.windsurf/mcp_config.json`
- Global target: `C:\Users\amita\.codeium\windsurf\mcp_config.json` (manual sync)
- Registry: `docs/reference/MCP_Registry.md`
- Health check: `ops_scripts/ci/mcp_health_check.py`
- ADR: `docs/architecture/adr/ADR-002-mcp-config-single-sync-script.md`
- Archive: `tools/archive/mcp_yaml_infra_w5.2/` (YAML infra — do not restore)
