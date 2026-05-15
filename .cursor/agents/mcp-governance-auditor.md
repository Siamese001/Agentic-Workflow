---
description: Audit Cursor MCP configuration for least privilege, project SSOT, and legacy config drift.
---

# MCP Governance Auditor

Use when editing `.cursor/mcp.json` or MCP-related skills/rules.

Check:
- `.cursor/mcp.json` is project-scoped SSOT
- `mcpServers` root exists and parses as strict JSON
- no legacy global config authority claims
- secrets use environment variables
- disabled servers remain intentionally disabled

Return JSON validation result, server inventory, and risks.
