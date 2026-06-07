## §7 — Notion

Notion holds searchable rows; disk holds full artifacts. **Upstream:** https://developers.notion.com/guides/mcp/mcp

### When To Use

| Intent | Use? | Alternative |
|--------|------|-------------|
| Query plan/wave/phase status | ✅ Yes | Backlog Snapshot page (preferred) |
| Read ADR Registry | ✅ Yes | — |
| Append SC/AP violation row | ✅ Yes | — |
| Log Author-Gate decision | ✅ Yes | — |
| Read source code | ❌ No | native `read_file` |
| Persistent agent memory | ❌ No | `memory` MCP |

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
1. **Backlog Snapshot first** — for dashboard queries, fetch page `34b27693-f55c-81b4-93ba-efec5755a20e`
2. **Stale-source sniff test** — verify plan status against git + filesystem before writeback

---
