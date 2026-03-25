# ADG MCP Server & Memory MCP — Reference Guide

> **Extracted from `.windsurfrules` §2.6–§2.8** to reduce always-loaded context.
> Rules remain in `.windsurfrules`; this file holds operational details and CLI examples.

---

## ADG Accelerator Tools — Primary Defaults

These five tools MUST be used as the primary default for their respective tasks. Bypassing them in favour of raw Redis commands, grep, full-suite mypy, or manual test selection is a §2.3 violation.

| # | Tool | Primary task | CLI |
|---|------|-------------|-----|
| 1 | `tools/adg/adg_antipattern_fixer.py` | Fix non-canonical `# guardian:` comments | `--staged` / `--from-diff` / `<files>` |
| 2 | `tools/adg/adg_stale_guard.py` | Assert ADG freshness before any query session | `--json` / `--warn` / `--files` |
| 3 | `tools/adg/adg_redis_query.py` | Search ADG nodes with layer & entity_type filters | `search-nodes --query <q> [--layer L3] [--entity-type class]` |
| 4 | `tools/adg/adg_type_check.py` | Incremental type checking scoped to blast radius | `--from-diff` / `<files>` |
| 5 | `tools/adg/adg_test_selector.py` | Select exact pytest nodeids via ADG `covers` edges | `--from-diff` / `<files>` |

**Integration points (automatically enforced):**
- Pre-commit T2c: `adg_antipattern_fixer.py --staged` runs on every commit (no Redis needed)
- Pre-commit T3g: `adg_stale_guard.py --warn` runs on every commit (non-blocking; warns when stale)
- CI workflow `adg-antipattern-ci.yml`: `adg_antipattern_fixer.py --check-only` blocks PRs with violations
- Workflow `/adg-redis-refresh` STEP 1: uses `adg_stale_guard.py --json`
- Workflow `/adg-repair-loop` STEP 0: uses `adg_stale_guard.py`; STEP 2: uses `adg_test_selector.py --from-diff`

**Forbidden substitutions:**
- ❌ `python -c "import redis; r = redis.Redis(...); r.hgetall('adg:meta')"` → use `adg_stale_guard.py`
- ❌ `grep -r ClassName .` → use `adg_redis_query.py search-nodes`
- ❌ `python -m mypy <entire_package>` → use `adg_type_check.py --from-diff`
- ❌ `pytest tests/` (broad) before convergence → use `adg_test_selector.py --from-diff`
- ❌ Manually editing guardian comments → let pre-commit T2c fix them automatically
- ❌ `mcp9_get("adg:meta")` or `mcp9_get("adg:node:*")` or `mcp9_get("adg:edge:*")` → marketplace Redis MCP is STRING-only; use the custom `adg_redis` MCP server tools instead

---

## Custom ADG Redis MCP Server — `adg_redis` (replaces marketplace Redis)

`tools/adg/adg_mcp_server.py` is wired in `mcp_config.json` as `adg_redis`. The marketplace
`@modelcontextprotocol/server-redis` is **disabled** — it was STRING-only and could not access
any ADG cache keys (HASH/SET types). The custom server provides:

| Tool | Redis op | Use for |
|---|---|---|
| `adg_status` | GET adg:status | **PRIMARY freshness check — call first** |
| `adg_meta` | HGETALL adg:meta | Full metadata: timestamp, node/edge counts, digest |
| `adg_assert_fresh` | HGETALL adg:meta + disk stat | Authoritative freshness verdict vs SQLite mtime |
| `adg_snapshot` | GET adg:snapshot | Full snapshot JSON (large — use adg_meta for counts) |
| `adg_node` | HGETALL adg:node:\<id\> | Single node attributes |
| `adg_nodes_by_layer` | SMEMBERS adg:nodes:by_layer:\<l\> | Paginated node IDs by layer |
| `adg_nodes_by_file` | SMEMBERS adg:nodes:by_file:\<p\> | Node IDs for all symbols in a file |
| `adg_edge_fanout` | SMEMBERS adg:edge:\<src\>:\<rel\> | Outgoing edges from a node |
| `adg_edge_fanin` | SMEMBERS adg:edge:in:\<tgt\>:\<rel\> | Incoming edges to a node |
| `adg_violations` | LRANGE adg:violations | All anti-pattern violations |
| `redis_type` | TYPE \<key\> | Determine key type before reading |
| `redis_hgetall` | HGETALL \<key\> | Read any HASH key |
| `redis_smembers` | SMEMBERS \<key\> | Read any SET key |
| `redis_scan` | SCAN cursor | Safe key pattern search (replaces O(N) KEYS \*) |
| `redis_ttl` | TTL \<key\> | Inspect key expiry |

**Every response includes `cache_meta`** — `{timestamp, node_count, edge_count, ingested_at, age_seconds, is_fresh}` — so freshness is always visible without a separate call.

**Rules:**
- ✅ Call `adg_status` first on every session to confirm cache is HOT before any analysis
- ✅ Use `adg_assert_fresh` (reads HASH + disk) when you need an authoritative freshness verdict
- ✅ Use `adg_meta` for metadata, `adg_nodes_by_layer` / `adg_nodes_by_file` for structure queries
- ✅ Use `redis_type` when unsure which read tool to use for an arbitrary key
- ❌ NEVER use `mcp9_get` on HASH/SET keys — marketplace server is disabled; use `adg_redis` tools
- ❌ NEVER interpret a WRONGTYPE or empty result as "cache cold" — always call `adg_status` to check
- ❌ NEVER fall back to SQLite after any Redis read failure — fix the cache, do not bypass it

**`adg:status` STRING sentinel** is still written by `adg_redis_ingest.py` on every ingest.
It is the lowest-overhead freshness probe: `adg_status` reads it + validates against SQLite mtime.

---

## Custom Memory MCP — `memory` (replaces marketplace server)

**Why the replacement:** `@modelcontextprotocol/server-memory` uses an in-memory Node.js store.
The ENTIRE knowledge graph is wiped on every Windsurf restart — constitutional rules, ADG
context, and session observations vanish. No cross-session knowledge accumulation is possible.

`tools/memory/adg_memory_server.py` is wired as `"memory"` in `mcp_config.json`. It provides:
- **SQLite-backed persistence** at `artifacts/memory/knowledge_graph.sqlite` — survives restarts
- **Observation deduplication** — `add_observations` is idempotent; call as many times as needed
- **Protected entity types** — `ArchitectureLayer`, `ProjectContext`, `ConstitutionalRule` entities
  survive `mem_cleanup_stale` and represent the durable knowledge base

**Tool reference (same core API as marketplace + enhanced tools):**

| Tool | Action | Notes |
|---|---|---|
| `mem_recall_session_start` | Return ALL protected entities | **Call first at session start** |
| `mem_import_adg_context` | Seed from ADG Redis hot cache | Creates Layer:L0–L6 + Project:ADG |
| `create_entities` | Create new entities | Skips duplicates silently |
| `add_observations` | Append observations to entity | Deduped — safe to call repeatedly |
| `create_relations` | Add directed relation | Auto-creates missing entities |
| `open_nodes` | Load entities by name | Returns observations + relations |
| `search_nodes` | Full-text search | Matches name, type, observations |
| `read_graph` | Dump entire graph | Avoid unless graph is small |
| `delete_entities` | Delete + cascade | Cascades to observations + relations |
| `delete_observations` | Remove specific observations | Fine-grained pruning |
| `delete_relations` | Remove specific relations | |
| `mem_get_stats` | Entity/obs/rel counts by type | Use for KB health check |
| `mem_cleanup_stale` | Delete non-protected entities > N days | Default 30 days |

**Entity type conventions:**

| Type | Lifetime | Examples |
|---|---|---|
| `ArchitectureLayer` | Permanent (protected) | `Layer:L0` … `Layer:L6` |
| `ProjectContext` | Permanent (protected) | `Project:ADG` |
| `ConstitutionalRule` | Permanent (protected) | `ConstitutionalRule:ADG-freshness` |
| `Agent` | Session → persistent | `Agent:L3-orchestration` |
| `Violation` | Session | `Violation:path_fragility` |
| `general` | Session | ad-hoc observations |

**Session startup protocol (MANDATORY):**
1. Call `mem_recall_session_start` → loads all durable project context in one call
2. If empty (first run): call `mem_import_adg_context` to seed from ADG hot cache
3. Add session-specific entities with type `general` or `Agent`/`Violation` as needed

**Rules:**
- ✅ Always call `mem_recall_session_start` at the start of every session
- ✅ Use `ArchitectureLayer` / `ProjectContext` / `ConstitutionalRule` types for knowledge
  that should outlive sessions — these are NEVER deleted by `mem_cleanup_stale`
- ✅ The DB at `artifacts/memory/knowledge_graph.sqlite` is gitignored (local only)
- ❌ NEVER rely on `@modelcontextprotocol/server-memory` — it is disabled
- ❌ NEVER create duplicate entities — `add_observations` is idempotent; use it to extend

---

## MCP Server Health Gate — HARD PREREQUISITE

**Both custom MCP servers MUST be green (connected) before any refactoring, ADG analysis, or code modification session begins.**

| Server | Config key | Script | Status check |
|---|---|---|---|
| `adg_redis` | `adg_redis` | `tools/adg/adg_mcp_server.py` | Call `adg_status` — must return `is_fresh=True` |
| `memory` | `memory` | `tools/memory/adg_memory_server.py` | Call `mem_recall_session_start` — must return without error |

**Enforcement rules:**
- ❌ **NEVER begin a refactoring phase** if either MCP server shows a red/error status in Windsurf Settings → MCP
- ❌ **NEVER use ADG hot cache queries** (`adg_status`, `adg_node`, `adg_edge_fanout`, etc.) if `adg_redis` is red — results will be stale or absent
- ❌ **NEVER read/write memory** (`mem_recall_session_start`, `create_entities`, etc.) if `memory` is red — session context will be lost
- ✅ **If either server is red**, diagnose and fix BEFORE proceeding (see fix protocol below)
- ✅ **At session start**, always verify both servers are green as part of the startup checklist

**Fix protocol if servers go red:**

1. Check `C:\Users\amita\.codeium\windsurf\mcp_config.json` — this is the file Windsurf actually reads (NOT the repo `mcp_config.json`)
2. Both entries MUST use **absolute paths** in `args` and include `"cwd": "C:\\Git\\Agentic-Workflow"`
3. `memory` server MUST have `"PYTHONPATH": "C:\\Git\\Agentic-Workflow"` in its `env` block (required for `from tools.memory.sqlite_memory_store import ...`)
4. Restart via `Ctrl+Shift+P` → "MCP: Restart Server"

**Canonical config entries** (copy verbatim if broken):
```json
"adg_redis": {
  "args": ["C:\\Git\\Agentic-Workflow\\tools\\adg\\adg_mcp_server.py"],
  "command": "python",
  "cwd": "C:\\Git\\Agentic-Workflow",
  "disabled": false,
  "env": {
    "ADG_DIR": "C:\\Git\\Agentic-Workflow\\artifacts\\adg",
    "ADG_MCP_CACHE_META_TTL": "5",
    "ADG_MCP_PAGE_SIZE": "500",
    "ADG_REDIS_URL": "redis://localhost:6379/0"
  }
},
"memory": {
  "args": ["C:\\Git\\Agentic-Workflow\\tools\\memory\\adg_memory_server.py"],
  "command": "python",
  "cwd": "C:\\Git\\Agentic-Workflow",
  "disabled": false,
  "env": {
    "ADG_REDIS_URL": "redis://localhost:6379/0",
    "MEMORY_DB": "C:\\Git\\Agentic-Workflow\\artifacts\\memory\\knowledge_graph.sqlite",
    "PYTHONPATH": "C:\\Git\\Agentic-Workflow"
  }
}
```

---

## ADG Schema Canonical Field Names

**ADG SCHEMA FREEZE:** On first ADG access, freeze the confirmed field name mapping. Reuse it for ALL subsequent accesses in the same run. Re-probing after freeze = violation. Schema inconsistency mid-run = HARD FAIL.

| Concept | Canonical key | Forbidden aliases |
|---|---|---|
| Entity type | `entity_type` | `entityType`, `type`, `kind` |
| Entity name | `name` | `entityName`, `node_name` |
| Import edges | `imports` | `import_edges`, `dependencies` |
| Call edges | `calls` | `call_edges`, `invocations` |
| Test edges | `tests` | `test_edges`, `covered_by` |
| Fixture edges | `fixtures` | `fixture_edges` |
| Module path | `module_path` | `path`, `file_path`, `module` |
| Cluster ID | `cluster_id` | `id`, `clusterID` |
| Root cause | `root_cause` | `cause`, `rootCause` |

Pre-flight schema check REQUIRED before first field access. Evidence MUST include: `ADG schema pre-flight: PASSED (canonical keys verified: ...)`.
