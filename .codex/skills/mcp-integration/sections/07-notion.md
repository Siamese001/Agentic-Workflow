## §7 — Notion

Notion holds searchable rows; disk holds full artifacts. **Upstream:** https://developers.notion.com/guides/mcp/mcp

### When To Use

The `notion` MCP is **manual page/DB read+write only** — the Notion plan-status / wave / registration
enforcement was removed (`notion-wave-enforcement-removal`). Plans, ADRs, rules, and SC/AP defects are
**filesystem SSOT**, never mirrored to Notion.

| Intent | Use? | Alternative |
|--------|------|-------------|
| Read/query an existing Notion page or DB the user points you at | ✅ Yes | — |
| Append a Notion row by explicit user request (optional manual backlog, §24) | ✅ Yes | — |
| Plan / wave / phase status | ❌ No | disk plan file (`plans/<slug>.md`) — no Notion |
| Read source code | ❌ No | native `read_file` |
| Persistent agent memory | ❌ No | file memory (`memory/`) |

### Read vs Write — Two Different IDs

| Operation | Parameter | Source |
|-----------|-----------|--------|
| Query rows | `data_source_id` | AGENTS.md table column 2 |
| Create row | `database_id` | AGENTS.md table column 3 |

⚠️ Using `data_source_id` for `API-post-page` returns 404.

### Tool Routing

| Goal | Tool |
|------|------|
| Query database | `API-query-data-source` |
| Create row | `API-post-page` (parent: `database_id`) |
| Update properties | `API-patch-page` |
| Move page | `API-move-page` |
| Get page | `API-retrieve-a-page` |
| Get database schema | `API-retrieve-a-database` |
| List templates | `API-list-data-source-templates` |
| Append blocks | `API-patch-block-children` |
| Search by title | `API-post-search` |
| List users | `API-get-users` |

### Hard Rules
1. **Filesystem is SSOT** — never mirror plans, ADRs, rules, or status into Notion; there is no
   enforced Notion writeback. Notion rows are an optional manual durable backlog only (§24).
2. **Read vs write IDs** — `data_source_id` to query, `database_id` to create (see above).

---
