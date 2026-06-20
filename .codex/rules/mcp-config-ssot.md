# MCP Config SSOT — stub

> On-demand when editing MCP config (plan `always-on-rule-surface-cut-c7f3a1`); enforcement unchanged. `.mcp.json` (native `mcpServers` format) is the repo-local MCP SSOT — strict JSON, `${env:VAR}` for secrets, stable server IDs; after edits run `python -m json.tool .mcp.json` + `sync_mcp_config.py`. Detail: [`mcp-integration`](../skills/mcp-integration/SKILL.md) skill, `.codex/mcp-notes.md`. Enforced: `check_mcp_sync_integrity.py`, `check_mcp_config_schema.py`, `check_mcp_config_sovereignty.py`.
