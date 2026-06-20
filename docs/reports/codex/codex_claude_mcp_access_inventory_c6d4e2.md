# Codex Claude MCP Access Inventory

Generated: 2026-06-11  
Plan: `codex-claude-mcp-access-parity-c6d4e2` W1  
Scope: inventory Claude `.mcp.json` servers against Codex process visibility and callable tool surfaces.

## Sources

| Source | Role |
|---|---|
| `.mcp.json` | Claude Code live MCP server SSOT |
| `.codex/mcp-notes.md` | Bootstrap env and dormant/re-add policy |
| `scripts/governance/audit_codex_mcp_transports.py --json` | Process, env, command, and script-readiness evidence |
| `tool_search` results | Codex-callable tool discovery evidence |
| Direct Codex tool calls | Proof for exposed-but-failing and plugin-callable surfaces |

## Summary

| Category | Count | Servers |
|---|---:|---|
| Live in `.mcp.json` | 8 | `GitKraken`, `adg_sqlite`, `deepwiki`, `memory`, `vector_db`, `notion`, `context7`, `playwright` |
| Raw MCP callable and healthy in Codex | 0 | _None in this W1 snapshot_ |
| Raw MCP namespace exposed but blocked | 1 | `adg_sqlite` |
| Callable through Codex plugin/substitute | 2 | `notion`, `playwright` |
| Process-visible but not callable | 3 | `memory`, `vector_db`, `context7` |
| Not exposed or not process-visible | 2 | `GitKraken`, `deepwiki` |

## Matrix

| Server ID | Configured in `.mcp.json` | Process Visible | Codex Callable Surface | Current Gap | W1 Classification |
|---|---|---|---|---|---|
| `GitKraken` | Yes | No | None found | Claude GitKraken MCP is configured, but no Codex `git_status`/`git_add_or_commit`/PR tool surface is exposed. | `NOT_EXPOSED` |
| `adg_sqlite` | Yes | No | Raw namespace present: `mcp__adg_sqlite` | Tool namespace exists, but `adg_health` returns `Transport closed`; no backing process is visible. | `EXPOSED_BLOCKED` |
| `deepwiki` | Yes | Remote URL | None found | No Codex `read_wiki_structure`, `read_wiki_contents`, or `ask_question` surface. | `NOT_EXPOSED` |
| `memory` | Yes | Yes, single process | None found | Memory process exists, but no `mem_recall_session_start`/writeback tools are callable. | `PROCESS_ONLY` |
| `vector_db` | Yes | Yes, single process | None found | Vector process exists, but no semantic-search tools are callable. | `PROCESS_ONLY` |
| `notion` | Yes | Yes, single launch tree | Codex Notion plugin | Callable through plugin; API shape differs from Claude raw Notion MCP. | `PLUGIN_CALLABLE` |
| `context7` | Yes | Yes, single launch tree | None found | Context7 process exists, but raw `resolve-library-id`/`get-library-docs` tools are not callable. | `PROCESS_ONLY` |
| `playwright` | Yes | Yes, single launch tree | `node_repl` / Browser substitute | Browser automation substitute exists, but Claude raw Playwright MCP names are not exposed. | `SUBSTITUTE_CALLABLE` |

## W1 Findings

1. Process visibility is not equivalent to Codex MCP access. `memory`, `vector_db`, and `context7` are running as local MCP process families, but Codex has no callable tool namespace for them.
2. `adg_sqlite` is the only raw Claude-style MCP namespace visible to Codex, but it is currently blocked by a closed transport.
3. `notion` is operational through the Codex Notion plugin. This is usable for Plans DB work, but it requires schema fetching and property mapping because the tool names differ from Claude's Notion MCP.
4. `playwright` has an operational substitute path through `node_repl`/Browser plugin discovery, not raw Claude Playwright MCP parity.
5. `GitKraken`, `deepwiki`, `memory`, `vector_db`, and `context7` require W2 routing decisions: host-level MCP exposure, accepted plugin substitute, or explicit degraded fallback.

## W1 Completion

| Phase | Result | Evidence |
|---|---|---|
| W1.1 | DONE | `.mcp.json`, `.codex/mcp-notes.md`, Codex tool discovery, and transport audit reviewed |
| W1.2 | DONE | This matrix separates configured, process-visible, and callable states |

## Next Step

W2 should decide the exposure route for each gap without creating a second MCP registry. The strongest candidates for host-level exposure are `memory`, `vector_db`, `GitKraken`, `deepwiki`, and `context7`; `notion` and `playwright` can continue as plugin/substitute routes if the documented API delta is acceptable.
