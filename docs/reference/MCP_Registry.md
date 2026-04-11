# MCP Registry — Capability Authority Map

**Status**: ACTIVE  
**SSOT**: This file reflects live `.windsurf/mcp_config.json`. Runtime config is the authority.  
**Updated**: 2026-04-10 (post-pilot seeding cleanup)  
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
| HTTP GET/POST/PUT/DELETE | `enhanced_http` | — | `fetch` removed; `enhanced_http` is sole HTTP authority |
| Project structure (ADG) | `adg_sqlite` | — | Primary structural analysis |
| Episodic memory | `memory` | — | Session-to-session context persistence |
| Vector storage | `vector_db` | — | Semantic search, embedding generation |
| OTel / runtime ADG | `otel_mcp` | — | Trace collection, anomaly detection |
| Git operations | `GitKraken` | — | All git/PR/issue operations |
| Task management | `task_manager` | — | T2/T3 task decomposition and tracking |
| Redis operations | `redis` | — | Cache inspection and key management |
| Test execution | `pytest_mcp` | — | Test discovery, coverage, execution |
| Deep repo Q&A | `deepwiki` | — | AI-powered repo documentation queries |
| Notion workspace | `notion` | — | Notion read/write via hosted MCP |

---

## Active Server Inventory

### `adg_sqlite` — ADG SQLite MCP
- **Transport**: Python (local subprocess)
- **Authority**: Project structure, dependency graph, layer analysis
- **Capability**: `adg_health`, `adg_node`, `adg_edge_fanout`, `adg_edge_fanin`, `adg_nodes_by_file`, `adg_nodes_by_layer`, `adg_violations`
- **Constitutional**: §13 MCP Green Light — call `adg_health` before T2/T3 work

### `memory` — Persistent Knowledge Graph
- **Transport**: Python (local subprocess)
- **Authority**: Episodic memory, session context, entity graph
- **Capability**: `mem_recall_session_start`, `mem_import_adg_context`, `create_entities`, `search_nodes`
- **Note**: Protected entity types (ArchitectureLayer, ProjectContext, ConstitutionalRule) never purged

### `filesystem` — Local Filesystem
- **Transport**: Node binary (direct `node.exe` invocation, no npx) — `@modelcontextprotocol/server-filesystem@2026.1.14`
- **Authority**: All local file reads; writes via gate-redirect to native Cascade tools
- **Capability (read/list/meta — allowed)**: `read_text_file`, `read_file` (deprecated), `read_media_file`, `read_multiple_files`, `list_directory`, `list_directory_with_sizes`, `directory_tree`, `search_files`, `get_file_info`, `list_allowed_directories`, `create_directory`
- **Capability (write/mutate — BLOCKED by gate)**: `write_file`, `edit_file`, `move_file` — redirected to Cascade native tools (`write_to_file`, `edit`, `multi_edit`) which fire `pre_write_code` constitutional gates
- **Scope**: Locked to repo root (`C:/Git/Agentic-Workflow`) only — enforced both by server and by gate
- **Operator note**: `docs/guides/filesystem_mcp_operations.md`

### `enhanced_http` — HTTP Client
- **Transport**: Python (local subprocess)
- **Authority**: Primary HTTP client for all API calls
- **Capability**: `http_get`, `http_post`, `http_put`, `http_delete`, `batch_requests`

### `vector_db` — Vector Database
- **Transport**: Python (local subprocess)
- **Authority**: Vector collection management, semantic search, embedding generation
- **Capability**: `create_collection`, `add_documents`, `query_collection`, `semantic_search`, `embed_text`

### `otel_mcp` — OpenTelemetry MCP
- **Transport**: Python (local subprocess)
- **Authority**: OTel trace collection, anomaly detection, runtime ADG ingestion
- **Capability**: `otel_status`, `otel_trace`, `otel_anomalies`, `otel_metrics_summary`, `otel_policy_decisions`

### `GitKraken` — Git & Dev Workflow
- **Transport**: Native binary (`gk.exe`)
- **Authority**: All git operations, PR/issue management, worktree
- **Capability**: `git_add_or_commit`, `git_push`, `git_log_or_diff`, `git_branch`, `pull_request_create`, `gitlens_launchpad`

### `task_manager` — Structured Task Tracking
- **Transport**: Node (npx) — `@blizzy/mcp-task-manager`
- **Authority**: T2/T3 task decomposition, progress tracking
- **Capability**: `create_task`, `decompose_task`, `update_task`, `task_info`

### `redis` — Redis Cache
- **Transport**: Python (local subprocess)
- **Authority**: Redis key inspection, cache invalidation, namespace stats
- **Capability**: `redis_get`, `redis_keys`, `redis_health`, `redis_flush_namespace`, `redis_namespace_stats`

### `pytest_mcp` — Test Execution
- **Transport**: Python (local subprocess)
- **Authority**: Test discovery, execution, and coverage
- **Capability**: `run_tests`, `discover_tests`, `analyze_test_coverage`, `list_pytest_config`

### `deepwiki` — Repository Documentation
- **Transport**: Remote URL (`https://mcp.deepwiki.com/mcp`)
- **Authority**: AI-powered documentation queries for GitHub repositories
- **Capability**: `ask_question`, `read_wiki_contents`, `read_wiki_structure`

### `notion` — Notion Workspace
- **Transport**: Hosted serverUrl (`https://mcp.notion.com/mcp`)
- **Authority**: Notion workspace read/write — pages, databases, comments, search
- **Capability**: `notion-fetch`, `notion-create-pages`, `notion-update-page`, `notion-search`, `notion-create-database`
- **Note**: Added 2026-04-10. Uses `serverUrl` transport (Windsurf hosted MCP pattern). Requires OAuth.

---

## Removed Servers

These servers were previously listed but are no longer present in `mcp_config.json`.
Preserved here for audit history. Do not re-add without HITL approval.

| Server | Reason Removed | Former Capability |
|--------|---------------|-------------------|
| `github` | Planned entry — never deployed in config | Remote repo file access, PR/issue REST API |
| `fetch` | Removed; `enhanced_http` is sole HTTP authority | Simple URL fetch fallback |
| `brave-search` | Removed during Wave 4/5 cleanup — no ADR | Web search |
| `playwright` | Removed during cleanup | Browser automation, UI testing |
| `figma` | Removed during cleanup | Figma file access, design assets |

---

## Overlap Resolution

| Overlap | Resolution |
|---------|-----------|
| `enhanced_http` vs (removed) `fetch` | `enhanced_http` is sole authority; `fetch` removed |
| `filesystem` vs (removed) `github` | `filesystem` for local; `github` never deployed — use GitKraken for remote git ops |
| `GitKraken` vs (removed) `github` | `GitKraken` covers all git and PR/issue ops |
| `adg_sqlite` vs `memory` | `adg_sqlite` for structural/code graph; `memory` for episodic/session context |
| `adg_sqlite` vs `otel_mcp` | `adg_sqlite` for static ADG; `otel_mcp` for runtime trace-derived ADG |

---

## Adding a New MCP

Before adding a new MCP server:

1. Check this registry — does an existing server cover the capability?
2. If overlap: document the authority decision here before adding
3. HITL approval required (Constitutional §HITL-1.5 Dependency Addition)
4. Update this registry after approval
5. Save `.windsurf/mcp_config.json` — `post_write_mcp_config_sync.py` hook auto-copies to global. Restart Windsurf to apply.
