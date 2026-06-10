# Codex MCP Live Route Contract

Generated: 2026-06-10  
Plan: `codex-mcp-transport-parity-4b9c7e` W2  
Scope: live `.mcp.json` server parity routes for Codex.

## W2 Result

W2 is **partially complete and blocked on W2.3**.

- **W2.1 complete**: Memory, Vector DB, GitKraken, and DeepWiki have documented Codex route status and fallback semantics.
- **W2.2 complete**: Notion, Context7, and Playwright have documented raw-vs-plugin/substitute route contracts.
- **W2.3 blocked**: ADG transport is open and healthy, but Redis hit payloads are corrupt in the live Codex MCP because the server is running from `C:\Git\Agentic-Workflow-FRESH`, while the Redis decode/Redis-3 compatibility fix exists in the `C:\Git\eval-harness` worktree.

## Evidence Snapshot

| Check | Result |
|---|---|
| `adg_health` | `mode=full`, `sqlite=healthy`, `redis=healthy`, snapshot `06082026_1212` |
| `adg_runtime_info` | PID `12236`, `sqlite_path=C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_06082026_1212.sqlite` |
| Live ADG Redis hit | `adg_node("1")` returned `backend_used=redis` but fields like `id="__json__:\"1\""` |
| Worktree Redis code | `C:\Git\eval-harness\tools\adg\cache\redis_cache.py` contains `__json__:` decode support and `resolve_adg_redis_url` |
| Primary Redis code | `C:\Git\Agentic-Workflow-FRESH\tools\adg\cache\redis_cache.py` lacks those fixes |
| GitKraken local command | `gk.exe mcp --help` exits 0 |
| Memory local script | `python -m py_compile tools/memory/adg_memory_server.py` exits 0 |
| Vector local script | `python -m py_compile tools/mcp/vector_db_server.py` exits 0 |
| Context7 local command | `npx -y @upstash/context7-mcp --help` exits 0 |
| Playwright local command | `npx -y @playwright/mcp --help` exits 0 |

## Route Contracts

### `adg_sqlite`

**Claude route**: raw MCP from root `.mcp.json`, with SQLite canonical and Redis optional cache.  
**Codex route**: raw `mcp__adg_sqlite` tools are exposed and callable.  
**Current status**: transport green, Redis payload parity red.

Contract:
- Use `adg_health` first.
- Treat `backend_used=redis` payloads as valid only after the live MCP code includes the Redis hash decode fix.
- If Redis returns encoded `__json__:` values, classify ADG cache as `DEGRADED_FALLBACK` and force SQLite-backed query or clear/re-warm affected Redis keys after code parity is restored.

Blocker:
- `ADG-LIVE-CODE-MISMATCH`: `.mcp.json` launches ADG from `${AGENTIC_REPO_ROOT}`, currently `C:\Git\Agentic-Workflow-FRESH`, not the `eval-harness` worktree where the patch lives.

Valid unblock paths:
1. Merge/apply the ADG Redis fixes from `eval-harness` into `C:\Git\Agentic-Workflow-FRESH`, then restart Codex MCP.
2. Relaunch Codex with `AGENTIC_REPO_ROOT=C:\Git\eval-harness`, then restart Codex MCP.
3. Temporarily delete and re-warm affected Redis keys only after the live server is running patched decode/write code.

### `memory`

**Claude route**: raw MCP tools such as `mem_recall_session_start`, `create_entities`, `add_observations`, and `search_nodes`.  
**Codex route**: no callable Memory MCP tools found after restart. Local server script compiles and can start.  
**Current status**: blocked.

Contract:
- Codex must not claim Memory first-call compliance until a callable Memory MCP route exists.
- Decision writeback is blocked, not silently substituted.
- Local DB/script access may be used only with `DEGRADED_FALLBACK: memory MCP unavailable in Codex`.

### `vector_db`

**Claude route**: raw MCP semantic tools such as `semantic_search`, `query_collection`, `vector_stats`, and `list_collections`.  
**Codex route**: no callable Vector DB MCP tools found after restart. Local server script compiles.  
**Current status**: blocked/degraded.

Contract:
- Use ADG for structural dependency questions.
- Use `rg` only for lexical fallback and mark semantic search as degraded.
- Do not represent lexical search as equivalent to Vector DB semantic search.

### `GitKraken`

**Claude route**: raw MCP Git authority: `git_status`, `git_add_or_commit`, `git_log_or_diff`, `pull_request_create`.  
**Codex route**: no callable GitKraken MCP tools found after restart. Local `gk.exe mcp --help` works.  
**Current status**: blocked/degraded.

Contract:
- Codex may use native `git` and GitHub plugin where available.
- Any divergence from GitKraken behavior must be called out.
- Mutating git actions still require normal Codex git safety rules.

### `deepwiki`

**Claude route**: remote MCP for external GitHub repository Q&A: `read_wiki_structure`, `read_wiki_contents`, `ask_question`.  
**Codex route**: no callable DeepWiki MCP tools found after restart.  
**Current status**: blocked.

Contract:
- Use GitHub plugin or Tavily/web only as a substitute, and identify the substitute.
- Do not claim DeepWiki-backed repository Q&A in Codex unless a DeepWiki route is exposed.

### `notion`

**Claude route**: raw Notion MCP tools such as `API-query-data-source`, `API-post-page`, and `API-patch-page`.  
**Codex route**: Codex Notion plugin tools are callable but have different names and schema shapes.  
**Current status**: callable substitute.

Contract:
- Always fetch the data source schema before writing properties.
- Use `data_source_id=ac53d31b-3068-4039-9ebe-856c12caab32` for Plans.
- Preserve property names exactly, including `AI Summary ` with trailing space.
- During active wave execution, avoid Notion MCP writes; use lifecycle helper/direct HTTP or defer.

### `context7`

**Claude route**: raw Context7 MCP: `resolve-library-id`, `get-library-docs`.  
**Codex route**: raw Context7 tools were not exposed by tool discovery; local package help works.  
**Current status**: blocked/degraded.

Contract:
- If Codex plugin docs cover the exact library/version, use them and name the substitute.
- Otherwise use official docs through approved web/docs tooling and mark raw Context7 unavailable.
- `CONTEXT7_API_KEY` is optional and currently unset.

### `playwright`

**Claude route**: raw Playwright MCP browser tools such as `browser_navigate`, `browser_snapshot`, `browser_click`, and `browser_take_screenshot`.  
**Codex route**: raw Playwright tools are not exposed; `node_repl` and Browser plugin are exposed as substitutes.  
**Current status**: callable substitute.

Contract:
- Use `node_repl` for browser automation when available.
- Use Browser plugin for local target inspection when appropriate.
- Do not claim raw Claude `browser_*` tool parity unless those tools are exposed.

## Required W2.3 Follow-up

Before W2 can be marked fully complete:

1. Make the live ADG MCP serve code with:
   - Redis placeholder normalization.
   - Redis 3-compatible hash writes.
   - JSON-prefixed hash value decoding.
2. Restart Codex MCP.
3. Verify:
   - `adg_health` remains full.
   - Cold `adg_node("1")` falls back to SQLite or returns clean payload.
   - Warm `adg_node("1")` with `backend_used=redis` returns `id="1"`, not `id="__json__:\"1\""`.

