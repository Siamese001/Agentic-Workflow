# Codex MCP Capability Matrix

Generated: 2026-06-10  
Plan: `codex-mcp-transport-parity-4b9c7e` W1  
Scope: Claude MCP SSOT vs Codex callable surfaces for this repo.

## Sources

| Source | Role |
|---|---|
| `.mcp.json` | Claude Code live MCP server SSOT |
| `CLAUDE.md` | Human routing summary, including dropped/dormant server policy |
| `.claude/mcp-notes.md` | Dormant/re-add server block SSOT and bootstrap env notes |
| `.claude/skills/mcp-integration/SKILL.md` | MCP routing index |
| `.claude/skills/mcp-integration/sections/*.md` | Per-server access patterns |
| Codex `tool_search` results | Current Codex callable surface evidence |

## Summary

| Category | Count | Servers |
|---|---:|---|
| Live in `.mcp.json` | 8 | `GitKraken`, `adg_sqlite`, `deepwiki`, `memory`, `vector_db`, `notion`, `context7`, `playwright` |
| Dormant/re-add in `.claude/mcp-notes.md` | 4 | `pytest_mcp`, `redis`, `otel_mcp`, `tavily` |
| Fully callable in Codex with same stable MCP ID | 1 | `adg_sqlite` |
| Callable in Codex through plugin/substitute | 4 | `notion`, `context7`, `playwright`, `tavily` |
| Not callable in Codex after restart | 5 | `GitKraken`, `deepwiki`, `memory`, `vector_db`, `redis` standalone |

## Matrix

| Server ID | Claude Status | Claude Access Pattern | Codex Surface | Fallback / Substitute | Env / Credential | Health Probe | Mutation Policy | Gap Status |
|---|---|---|---|---|---|---|---|---|
| `adg_sqlite` | Live in `.mcp.json` | `adg_health`, `adg_runtime_info`, graph/layer/node/edge tools. SQLite canonical, Redis optional cache. | `mcp__adg_sqlite` raw MCP tools are callable. | Direct SQLite only with `DEGRADED_FALLBACK` or named CI parity script. | `ADG_REPO_ROOT`, `ADG_REDIS_URL`, `PYTHONPATH`. | `adg_health` returned `mode=full`, `sqlite=healthy`, `redis=healthy`. | Read-only MCP; cache mutation via ADG scripts, not direct MCP writes. | `GREEN` |
| `GitKraken` | Live in `.mcp.json` | Git/PR authority: `git_status`, `git_add_or_commit`, `git_log_or_diff`, `pull_request_create`. | No Codex tool found for GitKraken. | Native `git` plus GitHub plugin where available; must mark semantic delta. | `GITKRAKEN_GK_PATH`; local `gk.exe mcp --help` works. | Local CLI help exits 0; no Codex MCP health tool. | Mutating git/PR actions should prefer GitKraken when exposed. | `RED`: configured locally but not Codex-callable |
| `deepwiki` | Live in `.mcp.json` remote URL | External GitHub repo Q&A: `read_wiki_structure`, `read_wiki_contents`, `ask_question`. | No Codex DeepWiki tool found. | GitHub plugin or Tavily/web only with explicit substitute note. | Remote URL `https://mcp.deepwiki.com/mcp`. | No Codex health probe. | Read-only. | `RED`: unavailable in Codex |
| `memory` | Live in `.mcp.json` | Session-start recall and decision writeback: `mem_recall_session_start`, `create_entities`, `add_observations`, `search_nodes`. | No Codex Memory tool found. Local server script exists and starts. | No honest substitute for required first-call invariant; local direct DB/script fallback must be marked blocked/degraded. | `ADG_REDIS_URL`, `MEMORY_DB`, `PYTHONPATH`. | Local process starts without immediate stderr; no Codex MCP health tool. | Writeback major decisions via Memory MCP when exposed. | `RED`: governance-critical unavailable surface |
| `vector_db` | Live in `.mcp.json` | Semantic search: `semantic_search`, `query_collection`, `vector_stats`, `list_collections`. | No Codex Vector DB tool found. Local server compiles and starts. | `rg` lexical fallback only; mark as degraded for semantic-search intent. | `VECTOR_DB_CHROMA_PATH`, `VECTOR_DB_EMBEDDING_MODEL`, offline flags. | Local startup viable; duplicate-process guard triggered during probe. | Read/search only for agent usage. | `RED`: unavailable in Codex; process hygiene issue |
| `notion` | Live in `.mcp.json` | Plans/Backlog DB access via Claude Notion MCP `API-query-data-source`, `API-post-page`, etc. | Codex Notion plugin tools are callable (`_fetch`, `_notion_create_pages`, `_search`, users/comments). | Codex plugin schema differs; use fetched data-source schema and document mapping. | `NOTION_TOKEN`; plugin auth also active. | `_notion_get_users(self)` returned current user; Plans row creation succeeded. | Plans + Backlog only; archived DBs remain filesystem SSOT. | `YELLOW`: callable but different tool names/API shapes |
| `context7` | Live in `.mcp.json` | Versioned official library docs: `resolve-library-id`, `get-library-docs`. | Raw Context7 tools not found; adjacent Hugging Face docs/plugin tools appear. Local `npx @upstash/context7-mcp --help` works. | Use Codex plugin docs only when equivalent for the library; otherwise mark raw Context7 unavailable. | Optional `CONTEXT7_API_KEY` is unset; free tier okay per notes. | Local CLI help exits 0; no Codex raw health. | Read-only. | `YELLOW/RED`: local server exists, raw Codex surface absent |
| `playwright` | Live in `.mcp.json` | Browser automation: `browser_navigate`, `browser_snapshot`, `browser_click`, screenshot tools. | Raw Playwright MCP tools not found; Codex exposes `node_repl` and Browser plugin substitute. | Use `node_repl`/Browser plugin with explicit delta from Claude tool names. | `npx @playwright/mcp`; no credential. | Local CLI help exits 0; no raw Codex Playwright health. | Browser/session outputs in `.playwright-mcp/` when raw MCP is used. | `YELLOW`: substitute exists, raw surface absent |
| `pytest_mcp` | Dormant/re-add block in `.claude/mcp-notes.md`; not in `.mcp.json` | Structured pytest discovery/runs if re-added. | No raw Codex pytest MCP expected. | Current Claude substitute: `python -m pytest` via shell with repo pytest policy. | `PYTHONPATH`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, plugins via `-p` as needed. | `python -m pytest --version` / focused test commands. | Test execution only. | `GREEN`: dormant by policy |
| `redis` | Dormant/re-add block in `.claude/mcp-notes.md`; not standalone in `.mcp.json` | Standalone cache inspection tools if re-added: `redis_health`, `redis_keys`, `redis_hgetall`, `redis_namespace_stats`. | No standalone Redis MCP; Redis reachable through ADG and local service. | Current Claude substitute: `redis-cli` via shell. ADG path uses `adg_sqlite` first; direct cache inspection must be explicit. | Standalone re-add block uses `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`; ADG/memory use `ADG_REDIS_URL`. | Redis TCP open; ADG `adg_health` reports Redis healthy. | Redis is hot projection only; mutations through `tools/adg/adg_redis_ingest.py`, not arbitrary direct writes. | `GREEN/YELLOW`: dormant by policy; Codex must not treat as live standalone MCP |
| `otel_mcp` | Dormant/re-add block in `.claude/mcp-notes.md`; not in `.mcp.json` | Runtime traces/anomalies and runtime ADG ingest when re-added. | No Codex OTel MCP found. | Local/manual collector diagnostics only with explicit degraded note. | `OTEL_MCP_RUNTIME_ADG_DIR`, collector prerequisites. | Not probed in W1. | Runtime diagnostic reads/ingest only when collector is up. | `GREEN`: dormant/on-demand by policy |
| `tavily` | Dormant/re-add block in `.claude/mcp-notes.md`; not in `.mcp.json` | If re-added: `tavily-search`, `tavily-extract`, `tavily-crawl`, `tavily-map`, `tavily-research`. | Codex Tavily plugin tools exposed: `_tavily_search`, `_tavily_extract`, `_tavily_crawl`, `_tavily_map`, `_tavily_research`. | Current Claude substitute: native WebSearch/WebFetch. Codex can use Tavily plugin when exposed; otherwise web fallback with note. | `TAVILY_API_KEY` set in OS env and in `C:\Users\amita\env\.env`; re-add block reads `${TAVILY_API_KEY}`. | Tool discovery exposes plugin tools; no raw `tavily` MCP health. | Read/search/extract/crawl only. | `GREEN/YELLOW`: dormant raw MCP; plugin substitute available |

## Exact Redis And Tavily Storage Answer

### Redis

Standalone `redis` is not currently stored in root `.mcp.json`. Its re-add block is stored in `.claude/mcp-notes.md` under "Servers dropped after the needs-review (2026-06-07)". Redis access is still active indirectly through:

- `ADG_REDIS_URL` in root `.mcp.json` for `adg_sqlite`.
- `ADG_REDIS_URL` in root `.mcp.json` for `memory`.
- `mcp-integration` §2 as the access-pattern doctrine.
- ADG hot-cache scripts such as `tools/adg/adg_redis_ingest.py`.

Current substitute is `redis-cli` via shell for standalone inspection, while ADG work should use `adg_sqlite` MCP first.

### Tavily

Standalone `tavily` is not currently stored in root `.mcp.json`. Its re-add block is stored in `.claude/mcp-notes.md` under "Servers dropped after the needs-review (2026-06-07)". Tavily routing is still documented in:

- `CLAUDE.md` "Not in `.mcp.json`" table.
- `mcp-integration` §8 as dormant reference.
- Windows env var `TAVILY_API_KEY`.

Current Claude substitute is native WebSearch/WebFetch. Current Codex substitute is the Tavily plugin when exposed.

## W1 Findings

1. Codex is not missing all MCPs; it has `adg_sqlite` raw MCP and several plugin substitutes.
2. Codex cannot currently satisfy the repo's Memory first-call invariant because Memory MCP tools are not exposed.
3. Vector DB and DeepWiki are the largest read-capability losses relative to Claude.
4. GitKraken is installed and locally viable, but not exposed as Codex MCP tools.
5. Redis and Tavily are not accidental omissions from `.mcp.json`; they are intentionally dormant and stored as re-add blocks in `.claude/mcp-notes.md`.
6. Codex substitute routes need explicit mapping because tool names and schemas differ from Claude MCP names.

