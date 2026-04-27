---
name: notion
description: Notion workspace integration — page CRUD, database queries, comments, block manipulation — for ADRs, Author-Gate decisions, MCP registry, plan/wave/phase status, SC/AP violation backlog, anti-pattern burndown. Invoke when the user asks for plan status, phase progress, wave status, ADR registry, decision history, MCP server status, what's blocked, or any project-management state. Distinguishes Notion writeback discipline (this skill) from filesystem reads. Wraps upstream Notion MCP (https://developers.notion.com/guides/mcp/mcp) for the Windsurf architecture.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
---

# Notion Skill

Notion holds the searchable rows; disk holds the full artifact. Never duplicate narrative — link the row to the file.

**Upstream:** https://developers.notion.com/guides/mcp/mcp
**Workspace map:** see `AGENTS.md` Notion Workspace Map (auto-synced)
**Sibling skill:** `writeback-discipline` (entity/row templates, the "when to write" decision tree)

## When To Use This MCP

| User intent | Use Notion MCP? | Alternative |
|---|---|---|
| Query plan/wave/phase status | ✅ Yes | (or read Backlog Snapshot page — preferred) |
| Read ADR Registry | ✅ Yes | — |
| Append SC/AP violation row | ✅ Yes | — |
| Log Author-Gate decision | ✅ Yes | — |
| Append MCP Registry note | ✅ Yes | — |
| Read source code | ❌ No | native `read_file` |
| Persistent agent memory (cross-session recall) | ❌ No | `memory` MCP |

## Read vs Write — Two Different IDs

| Operation | Parameter | Source |
|---|---|---|
| Query rows | `data_source_id` | AGENTS.md table column 2 |
| Create row | `database_id` | AGENTS.md table column 3 |

⚠️ Using `data_source_id` for `API-post-page` returns 404. This is the most common Notion MCP failure mode.

## Tool Routing

| Goal | Tool |
|---|---|
| Query a database | `API-query-data-source` |
| Create a row | `API-post-page` (parent: `database_id`) |
| Update page properties | `API-patch-page` |
| Move a page | `API-move-page` |
| Get a page | `API-retrieve-a-page` |
| Get a page property | `API-retrieve-a-page-property` |
| Get a database schema | `API-retrieve-a-database` |
| Get a data source schema | `API-retrieve-a-data-source` |
| List database templates | `API-list-data-source-templates` |
| Append blocks to a page | `API-patch-block-children` |
| Get block children | `API-get-block-children` |
| Update a block | `API-update-a-block` |
| Delete a block | `API-delete-a-block` |
| Add a comment | `API-create-a-comment` |
| Read comments | `API-retrieve-a-comment` |
| Search by title | `API-post-search` |
| List users | `API-get-users` |
| Bot identity | `API-get-self` |

## Hard Rules

1. **Backlog Snapshot first.** For "what's the state of the backlog" / dashboard queries, fetch page `34b27693-f55c-81b4-93ba-efec5755a20e` via `API-get-block-children` (~5 KB) instead of paginating Wave/Phase Convergence (~170 KB).
2. **Stale-Source Sniff Test before status writeback.** Per `writeback-discipline` — verify plan header status against git log + filesystem evidence before writing it as truth.
3. **Required fields when posting Wave/Phase Convergence rows:** Phase Title, Phase ID, Wave ID, Sub-Wave, Dependencies, Success Criteria, Files In Scope, Parent Plan Summary, Plan File, Status, Est Tokens, Blocking Items.
4. **Auto-routing triggers fire without prompting** — see AGENTS.md "Auto-Routing Rules" (new ADR → ADR Registry; new SC/AP defect → Violation Backlog; etc.).

## Sibling Skill — `writeback-discipline`

When deciding **whether** to write to Notion vs Memory vs neither, consult `writeback-discipline/SKILL.md`. This skill (`notion/`) is the **how**; `writeback-discipline` is the **when and which database**.

## MCP Serialization

Per constitutional §25, Notion MCP calls (`API-*`) MUST be issued one per response with no sibling tool calls. Plan accordingly — batch the read up front, do non-MCP work, then a single Notion write.
