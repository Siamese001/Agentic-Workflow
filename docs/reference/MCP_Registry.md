# MCP Registry — Capability Authority Map

**Status**: ACTIVE  
**SSOT**: This file is the single source of truth for MCP capability ownership.  
**Updated**: Wave 2 Phase 2.4  
**Rule**: `global_rules.md` §MCP Authority: One SSOT Per Capability

---

## Principle

Each capability has exactly **ONE** authoritative MCP. Before adding a new MCP server,
verify no existing server covers the capability. Overlap must be documented here with
explicit authority assignment.

---

## Authority Table

| Capability | Authoritative MCP | Fallback MCP | Notes |
|------------|-------------------|--------------|-------|
| File reads (local) | `filesystem` | — | Use for all local file reads/writes |
| File reads (remote) | `github` | — | Remote repo access only |
| HTTP GET/POST/PUT/DELETE | `enhanced_http` | `fetch` | `fetch` for simple/browser-like GETs only |
| Web search | `brave-search` | — | No fallback; wait if unavailable |
| Project structure (ADG) | `adg_sqlite` | — | Primary structural analysis |
| Episodic memory | `memory` | — | Session-to-session context persistence |
| Browser automation | `playwright` | — | UI testing and web interaction |
| Git operations | `GitKraken` | — | All git/PR/issue operations |
| Task management | `task_manager` | — | T2/T3 task decomposition and tracking |
| Redis operations | `redis` | — | Cache inspection and key management |
| Test execution | `pytest_mcp` | — | Test discovery, coverage, execution |
| Design assets | `figma` | — | Figma file access and asset export |
| Deep repo Q&A | `deepwiki` | — | AI-powered repo documentation queries |

---

## Server Inventory

### `adg_sqlite` — ADG SQLite MCP
- **Type**: Python (local subprocess)
- **Authority**: Project structure, dependency graph, layer analysis
- **Capability**: `adg_health`, `adg_node`, `adg_edge_fanout`, `adg_edge_fanin`, `adg_nodes_by_file`, `adg_nodes_by_layer`, `adg_violations`
- **Constitutional**: §13 MCP Green Light — call `adg_health` before T2/T3 work

### `memory` — Persistent Knowledge Graph
- **Type**: Python (local subprocess)
- **Authority**: Episodic memory, session context, entity graph
- **Capability**: `mem_recall_session_start`, `mem_import_adg_context`, `create_entities`, `search_nodes`
- **Note**: Protected entity types (ArchitectureLayer, ProjectContext, ConstitutionalRule) never purged

### `filesystem` — Local Filesystem
- **Type**: Node (npx)
- **Authority**: All local file reads and writes
- **Capability**: `read_file`, `write_file`, `list_directory`, `search_files`, `edit_file`
- **Scope**: Limited to allowed directories only

### `github` — GitHub Remote
- **Type**: Node (npx)
- **Authority**: Remote repository file access, PR and issue management
- **Capability**: `get_file_contents`, `create_pull_request`, `create_issue`

### `enhanced_http` — HTTP Client
- **Type**: Python (local subprocess)
- **Authority**: Primary HTTP client for all API calls
- **Capability**: `http_get`, `http_post`, `http_put`, `http_delete`, `batch_requests`

### `fetch` — Simple HTTP Fetch
- **Type**: uvx
- **Authority**: Fallback for simple URL fetches only
- **Capability**: `fetch` (single URL, markdown extraction)
- **When to use**: Only when `enhanced_http` is unavailable or for simple browser-like GETs

### `brave-search` — Web Search
- **Type**: Node (npx)
- **Authority**: All web and local business searches
- **Capability**: `brave_web_search`, `brave_local_search`

### `playwright` — Browser Automation
- **Type**: Node (npx)
- **Authority**: Browser automation, UI testing, web interaction
- **Capability**: `navigate`, `click`, `fill`, `screenshot`, `evaluate`

### `GitKraken` — Git & Dev Workflow
- **Type**: Native binary
- **Authority**: All git operations, PR/issue management
- **Capability**: `git_add_or_commit`, `git_push`, `git_log_or_diff`, `git_branch`, `pull_request_create`

### `task_manager` — Structured Task Tracking
- **Type**: Node (npx)
- **Authority**: T2/T3 task decomposition, progress tracking
- **Capability**: `create_task`, `decompose_task`, `update_task`, `task_info`

### `redis` — Redis Cache
- **Type**: Python (local subprocess)
- **Authority**: Redis key inspection, cache invalidation
- **Capability**: `redis_get`, `redis_keys`, `redis_health`, `redis_flush_namespace`

### `pytest_mcp` — Test Execution
- **Type**: Python (local subprocess)
- **Authority**: Test discovery, execution, and coverage
- **Capability**: `run_tests`, `discover_tests`, `analyze_test_coverage`

### `figma` — Design Assets
- **Type**: Node (npx)
- **Authority**: Figma file access, design data, asset export
- **Capability**: `get_figma_data`, `download_design_assets`, `check_reference`

### `deepwiki` — Repository Documentation
- **Type**: Remote URL
- **Authority**: AI-powered documentation queries for GitHub repositories
- **Capability**: `ask_question`, `read_wiki_contents`, `read_wiki_structure`

---

## Overlap Resolution

| Overlap | Resolution |
|---------|-----------|
| `enhanced_http` vs `fetch` | Use `enhanced_http` always; `fetch` only as last-resort fallback |
| `github` vs `filesystem` | `filesystem` for local clones; `github` for remote/API access |
| `GitKraken` vs `github` | `GitKraken` for git CLI ops; `github` MCP for REST API (PR, issues) |
| `adg_sqlite` vs `memory` | `adg_sqlite` for structural/code graph; `memory` for episodic/session context |

---

## Adding a New MCP

Before adding a new MCP server:

1. Check this registry — does an existing server cover the capability?
2. If overlap: document the authority decision here before adding
3. HITL approval required (Constitutional §HITL-1.5 Dependency Addition)
4. Update this registry after approval
5. Sync `config/mcp_servers.yaml` via `/mcp-config-sync` workflow
