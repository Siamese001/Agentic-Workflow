---
trigger: glob
description: Apply when reading or editing the MCP server configuration file to enforce SSOT discipline, strict JSON validity, sync rules, and secret handling constraints.
globs:
  - ".windsurf/mcp_config.json"
---

> See `.windsurf/RULES_INDEX.md#always-on-discipline` for shared retrieval / enforcement guidance.

# MCP Config SSOT Rule

## Source of Truth

```text
.windsurf/mcp_config.json           ← EDIT HERE (repo-local, version-controlled, strict JSON)
~/.codeium/windsurf/mcp_config.json ← what Windsurf actually reads at startup; prefer symlink
AGENTS.md                           ← auto-regenerated autogen blocks at repo root
config/notion_databases.yaml        ← SSOT for Notion DB IDs + routing triggers
```

**`.windsurf/mcp_config.json` is the one repo-local SSOT.** It uses the native Windsurf `mcpServers` JSON format. There is no YAML layer, no second repo-local mirror, and no hidden MCP registry file inside `.windsurf/`.

### Preferred: zero-drift via symlink

Contributors should run `tools/setup/setup_symlinks.ps1` (Windows) or `tools/setup/setup_symlinks.sh` (POSIX) once per machine. This symlinks `~/.codeium/windsurf/mcp_config.json` → `.windsurf/mcp_config.json`, making drift structurally impossible. The post-write hook detects the symlink and becomes a no-op.

### Fallback: copy-based sync

Without the symlink the post-write hook (`.windsurf/scripts/post_write_mcp_config_sync.py`) copies on every save. This is still correct — just not zero-drift between save and sync.

## Format

```json
{
  "mcpServers": {
    "ServerName": {
      "command": "...",
      "args": ["..."],
      "env": {
        "KEY": "${env:VAR_NAME}"
      },
      "disabled": false
    }
  }
}
```

- The file must be valid **strict JSON**. No trailing commas.
- Use `${env:VAR_NAME}` placeholders for secrets. Never hardcode tokens.
- Keep the **server IDs** stable. They are the authoritative names used for AGENTS sync and team whitelists.
- Live tool prefixes like `mcp0_`, `mcp1_`, and `mcp2_` are **not stable**. Resolve them from the current tool list.

## Sync Contract

Saving `.windsurf/mcp_config.json` triggers `.windsurf/scripts/post_write_mcp_config_sync.py`, which:

1. Validates strict JSON structure
2. Backs up and overwrites `~/.codeium/windsurf/mcp_config.json`
3. Refreshes the repo-root `AGENTS.md` MCP Quick Reference section
4. Optionally upserts the Notion MCP Registry when `NOTION_TOKEN` is available

Manual repair path:

```bash
python .windsurf/scripts/sync_mcp_config.py
```

## Adding / Removing MCP Servers

1. Edit `.windsurf/mcp_config.json`
2. Save and let the post-write sync run
3. Restart Windsurf
4. Confirm the AGENTS Quick Reference section was refreshed
5. Run your normal MCP health check flow

## Hard Constraints

- **NEVER** reintroduce a YAML MCP layer
- **NEVER** keep a second repo-local MCP config mirror
- **NEVER** hardcode secrets into `command`, `args`, `env`, `url`, `serverUrl`, or `headers`
- **DO NOT** exceed 100 enabled tools across all MCPs

## Enforcement

| Layer | Mechanism |
|---|---|
| Windsurf rule | This file (fires on `.windsurf/mcp_config.json` edits) |
| T1 hook | `post_write_mcp_config_sync.py` — validates, syncs global config, refreshes AGENTS.md |
| T1 hook | `post_write_audit.py` — JSON-native lint on every MCP config write |
| T1 hook | `pre_write_gate.py` — blocks deletion of `mcp_config.json` |
| Manual repair | `sync_mcp_config.py` — one-shot repair for global config + AGENTS quick reference |

## References

- Repo SSOT: `.windsurf/mcp_config.json`
- Global runtime mirror: `~/.codeium/windsurf/mcp_config.json`
- Repo guidance surface: `AGENTS.md`
