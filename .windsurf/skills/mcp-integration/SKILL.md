---
name: mcp-integration
description: Unified integration guide for all MCP servers — filesystem, Redis, DeepWiki, Context7, Playwright, Vector DB, Notion, Tavily, OTel, pytest, GitKraken, memory, and task manager. Each section provides use-when guidance, tool routing tables, hard rules, and common workflows. For ADG analysis, use adg-sqlite skill separately. Invoke the relevant section when the user asks about any MCP server capability.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
---

# MCP Integration Guide

> **Consolidated skill** — W4.P2 2026-05-12. Replaces 13 individual MCP guide skills.  
> **Excluded**: `adg-sqlite` remains separate (critical infrastructure).

## Quick Reference

| Need | Section | MCP |
|------|---------|-----|
| File operations (batch/multi-file) | §1 Filesystem | `filesystem-mcp` |
| Redis cache inspection | §2 Redis Cache | `redis-cache` |
| GitHub repo docs/Q&A | §3 DeepWiki | `deepwiki` |
| Library API docs | §4 Context7 | `context7` |
| Browser automation/E2E | §5 Playwright | `playwright` |
| Semantic search | §6 Vector DB | `vector-db` |
| Notion workspace | §7 Notion | `notion` |
| Web search/crawl | §8 Tavily | `tavily-research` |
| Runtime traces/anomalies | §9 OTel | `otel-telemetry` |
| Test discovery/execution | §10 Pytest | `pytest-mcp` |
| Git/PRs/issues | §11 GitKraken | `gitkraken` |
| Persistent memory | §12 Memory | `memory-mcp` |
| Tracked task state | §13 Task Manager | `task-manager-mcp` |

---

## §1 — Filesystem MCP

**In-house.** Use **sparingly.** Native Cascade file tools are the default; this MCP is for batch or out-of-workspace operations.

### When To Use

| Intent | Use MCP? | Native Alternative |
|--------|----------|-------------------|
| Single file read | ❌ No | `read_file` |
| Single file edit | ❌ No | `edit` / `multi_edit` |
| 5+ files in one call | ✅ Yes | `read_multiple_files` |
| Recursive JSON tree | ✅ Yes | `directory_tree` |
| Move across allowed dirs | ✅ Yes | `move_file` |

### Tool Routing

| Goal | Tool |
|------|------|
| List allowed roots | `list_allowed_directories` |
| Batch file read | `read_multiple_files` |
| Recursive tree (JSON) | `directory_tree` |
| Directory listing | `list_directory` / `list_directory_with_sizes` |
| File metadata | `get_file_info` |
| Glob search | `search_files` |
| Create directory | `create_directory` |
| Write file (overwrite) | `write_file` |
| Line-based edit | `edit_file` |
| Move/rename | `move_file` |

### Hard Rules
1. **Native first** — use `read_file`/`edit` before this MCP
2. **MCP serialization (§25)** — one MCP call per response
3. **Allowed-directories sandbox** — paths must be within allowed roots
4. **`edit_file` supports `dryRun=true`** — preview changes

---

## §2 — Redis Cache

**In-house.** Redis is the **hot read-only projection** of the ADG. SQLite is canonical.

### When To Use

| Intent | Use MCP? |
|--------|----------|
| Check ADG hot cache status | ✅ Yes |
| Inspect coordination-fabric keys | ✅ Yes |
| Verify TTL on a key | ✅ Yes |
| Bounded namespace invalidation | ✅ Yes |
| Modify cache contents | ❌ No — mutations via `tools/adg/adg_redis_ingest.py` |

### Tool Routing

| Goal | Tool |
|------|------|
| Health probe | `redis_health` |
| Server INFO | `redis_stats` |
| DB key count | `redis_dbsize` |
| Scan keys (uses SCAN) | `redis_keys` |
| Get key (auto-detects type) | `redis_get` |
| Hash fields | `redis_hgetall` |
| TTL remaining | `redis_ttl` |
| Namespace stats | `redis_namespace_stats` |
| Delete single key | `redis_del_key` |
| Bulk delete (dry_run default) | `redis_flush_namespace` |

### Hard Rules
1. **SQLite is canonical, Redis is hot projection**
2. **`redis_flush_namespace` defaults to `dry_run=true`**
3. **Use `redis_keys` (SCAN), never `KEYS *`**
4. **MCP green light** — check Redis before T2/T3 work

---

## §3 — DeepWiki

DeepWiki indexes GitHub repos for AI-grounded answers. **Upstream:** https://github.com/deepwiki/deepwiki-mcp

### When To Use

| Intent | Use? | Alternative |
|--------|------|-------------|
| "How does facebook/react implement X?" | ✅ Yes | — |
| "What's the layout of microsoft/playwright?" | ✅ Yes | — |
| This repo's own code | ❌ No | `adg_sqlite` |
| Published library API | ❌ No | `context7` |
| Web search beyond GitHub | ❌ No | `tavily-search` |

### Tool Routing

| Goal | Tool |
|------|------|
| List doc topics | `read_wiki_structure` |
| View full docs | `read_wiki_contents` |
| Ask free-form question | `ask_question` |

### Hard Rules
1. **`owner/repo` format only** — `facebook/react`, not URLs
2. **`ask_question` accepts up to 10 repos**
3. **Do not use for this repo** — `adg_sqlite` is canonical

---

## §4 — Context7

**Upstream:** https://context7.com/docs/skills. Doc-lookup authority for **external** libraries.

### When To Use

| Intent | Use? | Alternative |
|--------|------|-------------|
| "How do I use React `useEffect`?" | ✅ Yes | — |
| "FastAPI dependency injection example" | ✅ Yes | — |
| "Prisma migration syntax" | ✅ Yes | — |
| This repo's own code | ❌ No | `adg_sqlite` |
| GitHub repo Q&A | ❌ No | `deepwiki` |
| Recent news/web | ❌ No | `tavily-search` |

### Two-Step Workflow (Mandatory)

| Step | Tool | Purpose |
|------|------|---------|
| 1 | `resolve-library-id` | Find canonical ID (`/org/project`) |
| 2 | `query-docs` | Ask specific question |

### Hard Rules
1. **Be specific in queries** — "JWT auth in Express.js" not "auth"
2. **No secrets in queries**
3. **Max 3 calls per question**
4. **Use `researchMode: true` only on retry**

---

## §5 — Playwright

Browser automation/E2E. **Upstream:** https://playwright.dev/agent-cli/skills

### When To Use

| Intent | Use? | Alternative |
|--------|------|-------------|
| Test live web app flow | ✅ Yes | — |
| Verify UI renders | ✅ Yes | — |
| Take screenshot | ✅ Yes | — |
| Fill/submit form | ✅ Yes | — |
| Capture network requests | ✅ Yes | — |
| Static URL (no JS) | ❌ No | direct `httpx` or `read_url_content` |
| Web search | ❌ No | `tavily-search` |

### Tool Routing

| Goal | Tool | Notes |
|------|------|-------|
| Snapshot (preferred) | `browser_snapshot` | Returns accessibility tree with `ref` IDs |
| Click element | `browser_click` | Needs `ref` from snapshot |
| Fill multiple fields | `browser_fill_form` | Batches field types |
| Type single field | `browser_type` | Use `submit:true` for Enter |
| Navigate | `browser_navigate` | — |
| Screenshot | `browser_take_screenshot` | Visual only |
| Run JS | `browser_evaluate` | Serialized result |
| Console logs | `browser_console_messages` | `level=error` for diagnosis |
| Network inspect | `browser_network_requests` | `filter=/api/.*` |
| Resize viewport | `browser_resize` | Responsive testing |

### Hard Rules
1. **Always snapshot before clicking** — `browser_click` needs `ref`
2. **Close tabs after use** — `browser_tabs(action='close')` or `browser_close`
3. **Output to `.playwright-mcp/`** (gitignored)
4. **Not for static HTML** — use direct `httpx` if no JS needed

---

## §6 — Vector DB

**In-house.** ChromaDB-backed semantic search. BAAI/bge-m3 embeddings.

### When To Use

| Intent | Use? |
|--------|------|
| "Find docs about X" — fuzzy concept | ✅ Yes |
| "What's similar to this passage?" | ✅ Yes |
| Cross-collection semantic recall | ✅ Yes |
| Structural code dependencies | ❌ NO — use `adg_sqlite` |
| Exact string match | ❌ No — use `grep_search` |
| Episodic recall | ❌ No — use `memory` MCP |

### Tool Routing

| Goal | Tool |
|------|------|
| Health probe | `readiness` |
| Server stats | `vector_stats` |
| List collections | `list_collections` |
| Collection info | `get_collection_info` |
| Create/delete collection | `create_collection` / `delete_collection` |
| Add documents | `add_documents` |
| Query collection | `query_collection` |
| Cross-collection search | `semantic_search` |
| Embed text | `embed_text` |

### Hard Rules
1. **Never use for dependency analysis** — `adg_sqlite` only
2. **Readiness check before heavy queries**
3. **MCP serialization (§25)**
4. **Zombie-process awareness** — restart MCP if query hangs

---

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
3. **MCP serialization (§25)** — one Notion call per response

---

## §8 — Tavily Research

**Upstream:** https://docs.tavily.com/documentation/agent-skills

### Prerequisites
`TAVILY_API_KEY` must be set as Windows OS env var (`setx TAVILY_API_KEY tvly-...`). `pre_mcp_gate.py` blocks until present.

### Tool Routing — Pick the Right Tool

| User Intent | Tool | When NOT To Use |
|-------------|------|-----------------|
| One-shot question, news | `tavily-search` | Don't use for known URLs |
| Pull full text from URL | `tavily-extract` | Don't search-via-extract |
| Discover URLs on site | `tavily-map` | Cheaper than crawl |
| Pull every page on site | `tavily-crawl` | Credit-heavy; map first |
| Multi-source synthesis | `tavily-research` | Don't use when 1-2 hits answer |

### Hard Rules
1. **Tavily ONLY for external web content** — this repo → `adg_sqlite`, library docs → `context7`, GitHub → `deepwiki`
2. **Prefer direct `httpx` for known API endpoints**
3. **One MCP call per response (§25)**
4. **`tavily-research` takes 30–120s** — don't pre-empt

---

## §9 — OTel Telemetry

**In-house.** Runtime telemetry: OTEL spans, healing chains, anomaly detection, policy decisions, runtime ADG.

### When To Use

| Intent | Use? |
|--------|------|
| Runtime trace inspection | ✅ Yes |
| What happened during agent X's run? | ✅ Yes |
| Anomaly/failure spans | ✅ Yes |
| Policy decision history | ✅ Yes |
| Healing chain replay | ✅ Yes |
| Static dependency analysis | ❌ No — `adg_sqlite` |
| Agent source code | ❌ No — `read_file` |

### Tool Routing

| Goal | Tool |
|------|------|
| Process identity (check stale) | `otel_server_info` — **call FIRST** |
| Server status | `otel_status` |
| Metrics summary | `otel_metrics_summary` |
| Anomaly list | `otel_anomalies` |
| Policy decisions | `otel_policy_decisions` |
| Full trace | `otel_trace` |
| Spans by agent | `otel_spans_by_agent` |
| Healing chain | `otel_healing_chain` |
| Ingest to runtime ADG | `otel_ingest_to_runtime_adg` |

### Hard Rules
1. **Stale-process runbook** — `otel_server_info` FIRST if MCP appears stale
2. **Static vs runtime separation** — structural → `adg_sqlite`, runtime → `otel_mcp`
3. **MCP serialization (§25)**

---

## §10 — Pytest MCP

**In-house.** Prefer over raw `pytest` CLI when operation maps cleanly.

### When To Use

| Intent | Use? |
|--------|------|
| Discover tests | ✅ Yes |
| Run scoped test set | ✅ Yes |
| Coverage analysis | ✅ Yes |
| Inspect pytest config | ✅ Yes |
| Custom plugin work | ❌ Maybe — fall back to `run_command` |

### Tool Routing

| Goal | Tool |
|------|------|
| Health probe | `pytest_mcp_health` |
| Discover tests | `discover_tests` |
| Run tests | `run_tests` |
| Test details | `get_test_details` |
| Coverage | `analyze_test_coverage` |
| Show config | `list_pytest_config` |

### Hard Rules
1. **No `pytest.mark.skip`** without `strict=True` — constitutional §1
2. **No weakened assertions** — constitutional §1
3. **ADG-backed scope selection** — use `adg_sqlite` for blast radius
4. **MCP serialization (§25)**
5. **Timeouts** — always set `timeout` for runs that may stall

---

## §11 — GitKraken

**Upstream:** https://help.gitkraken.com/mcp/mcp-getting-started/. **Sole authority** for git state, PRs, cross-provider issues.

### When To Use

| Intent | Use? | Alternative |
|--------|------|-------------|
| `git status` / list changes | ✅ Yes | — |
| Commit | ✅ Yes | — |
| Review log/diff | ✅ Yes | — |
| Open PR | ✅ Yes | — |
| Create/list issues | ✅ Yes | — |
| Read repo source | ❌ No | native `read_file` |

### Tool Routing

| Goal | Tool |
|------|------|
| `git status` | `git_status` |
| Stage + commit | `git_add_or_commit` |
| Log/diff | `git_log_or_diff` |
| Blame | `git_blame` |
| Branch list/create | `git_branch` |
| Switch branch | `git_checkout` |
| Push | `git_push` |
| Stash | `git_stash` |
| Worktree | `git_worktree` |
| Create PR | `pull_request_create` |
| Get PR details | `pull_request_get_detail` |
| PR comments | `pull_request_get_comments` |
| Create review | `pull_request_create_review` |
| Issues | `issues_assigned_to_me` / `issues_get_detail` / `issues_add_comment` |
| File from branch/SHA | `repository_get_file_content` |
| Commit composer | `gitlens_commit_composer` |
| PR triage | `gitlens_launchpad` |
| AI PR review | `gitlens_start_review` |
| Branch from issue | `gitlens_start_work` |

### Hard Rules
1. **No `git` via `run_command`** for state queries
2. **Never amend/force-push** without explicit user direction
3. **Issue provider required** — `github`/`gitlab`/`jira`/`azure`/`linear`
4. **Azure/Bitbucket**: `repository_organization` + `repository_name` mandatory

---

## §12 — Memory MCP

**In-house.** Persistent SQLite-backed knowledge graph. Survives Windsurf restarts.

### When To Use

| Intent | Use? |
|--------|------|
| Session start (mandatory) | ✅ Yes — `mem_recall_session_start` is FIRST call |
| User asks about past context | ✅ Yes |
| Before HITL/Author-Gate | ✅ Yes |
| After architecture decision/RCA | ✅ Yes |
| Semantic similarity | ❌ No — `vector_db` |
| Project status/wave/phase | ❌ No — `notion` |

### Tool Routing

| Goal | Tool |
|------|------|
| Session start | `mem_recall_session_start` |
| Health | `memory_health` / `mem_health_check` |
| Stats | `mem_get_stats` |
| Search | `search_nodes` |
| Open entities | `open_nodes` |
| Create entities | `create_entities` |
| Add observations | `add_observations` |
| Create relations | `create_relations` |
| Delete | `delete_entities` / `delete_observations` / `delete_relations` |
| Cleanup stale | `mem_cleanup_stale` |
| Import ADG context | `mem_import_adg_context` |

### Entity Types (CRITICAL)

Only these survive `mem_cleanup_stale`:

| Type | Use |
|------|-----|
| `ProceduralPattern` | Fix recipes, debugging playbooks |
| `ProjectContext` | Active blockers, plan status |
| `ArchitecturalInvariant` | Code-topology rules |
| `EpisodicEvent` | Important one-time occurrences |

❌ **Never use `entityType: "general"`** — purged at 30 days.

### Hard Rules
1. **Constitutional §17** — first tool call is `mem_recall_session_start`
2. **15/3 Rule** — if solving took >15 min, spend up to 3 min writing back
3. **MCP serialization (§25)**
4. **Observations must be recall-actionable**

---

## §13 — Task Manager MCP

**In-house.** **Selective use only.** For durable, queryable task state — not ordinary planning.

### When To Use

| Intent | Use? | Alternative |
|--------|------|-------------|
| "Track this as tasks" | ✅ Yes | — |
| "Decompose into subtasks" across sessions | ✅ Yes | — |
| Long-horizon multi-session epic | ✅ Yes | — |
| In-session multi-step work | ❌ No | `structured-reasoning` (SR_PLAN) |
| Plan-file work | ❌ No | `.windsurf/plans/*.md` |

### Tool Routing

| Goal | Tool |
|------|------|
| Create task | `create_task` |
| Decompose | `decompose_task` |
| Get details | `task_info` |
| Update status | `update_task` |

### Hard Rules
1. **Decomposition mandatory** for complexity above `low` (`decompose_task` first)
2. **Status discipline** — `in-progress` before executing, `done`/`failed` when finished
3. **Parallelizable subtasks share `sequenceOrder`**
4. **MCP serialization (§25)**
5. **Don't replicate plan-file content**

---

## Appendix: Constitutional §25 — MCP Serialization

> ⛔ **Remote MCP tool calls MUST be isolated: one remote-MCP call per response.**

**Remote MCPs**: `notion`, `tavily`, `deepwiki`, `context7`, `GitKraken`. One call per block, no siblings.

**Local MCPs**: `adg_sqlite`, `redis`, `memory`, `filesystem`, `vector_db`, `pytest_mcp`, `otel_mcp`, `task_manager`, `playwright`. Batch freely.

**Bypass**: `MCP_SERIAL_BYPASS=1` — logged to violations.

---

## Redirects

Individual MCP guide skills redirect here:

| Old Skill | Redirects To |
|-----------|--------------|
| `filesystem-mcp` | §1 |
| `redis-cache` | §2 |
| `deepwiki` | §3 |
| `context7` | §4 |
| `playwright` | §5 |
| `vector-db` | §6 |
| `notion` | §7 |
| `tavily-research` | §8 |
| `otel-telemetry` | §9 |
| `pytest-mcp` | §10 |
| `gitkraken` | §11 |
| `memory-mcp` | §12 |
| `task-manager-mcp` | §13 |
