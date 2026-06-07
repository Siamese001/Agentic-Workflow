
# MCP Config SSOT Rule

## Source of truth

```text
.mcp.json                 ← EDIT HERE, project-scoped MCP config
OS environment variables         ← secrets and credentials only
.claude/skills/**/SKILL.md       ← MCP usage procedures
.claude/rules/mcp-serialization.md  ← remote MCP serialization invariant (batching / ordering)
.claude/rules/*.mdc              ← governance invariants
.claude/hooks/**                 ← deterministic Claude Code hook checks
```

`.mcp.json` is the repo-local MCP source of truth. It uses the native `mcpServers` JSON format. There is no second editor-specific global authority in this project folder.

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

Rules:

- File must be strict JSON.
- Use `${env:VAR_NAME}` placeholders for secrets.
- Keep server IDs stable unless a migration receipt explains the rename.
- Do not rely on live `mcp0_`, `mcp1_`, or similar tool prefixes as stable identifiers.
- Run `python -m json.tool .mcp.json` after edits.
- Run `python .claude/governance/scripts/check_cursor_native_config.py --strict` before claiming completion.
- CI gates: `check_mcp_sync_integrity.py`, `check_agents_mcp_coverage.py`, `check_mcp_config_schema.py --profile all`, `check_cursor_config_schema.py`, `check_mcp_editor_parity.py`, `check_mcp_config_sovereignty.py` (Rule #0).
- After editing `.mcp.json`, run `python .claude/governance/scripts/sync_mcp_config.py` (refreshes AGENTS.md + global Cursor copy).
