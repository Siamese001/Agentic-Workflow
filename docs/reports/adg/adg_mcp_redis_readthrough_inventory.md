# ADG MCP Redis read-through inventory (W1)

**Purpose:** Inventory only — no MCP or `ADGService` behavior changes. Maps each `adg_*` MCP tool to the `ADGService` path and today’s Redis read-through posture.

**As-of:** codebase snapshot 2026-05-16 (plan `adg-mcp-redis-readthrough-enforcement-b2e7a9`, **COMPLETE**: W1 + **W2.1** + **W3** + **W4** + **W5** doctrine sync).

**Review / tracking:** Primary **git‑tracked** copy: `docs/reports/adg/adg_mcp_redis_readthrough_inventory.md`. Workspace mirror (often gitignored by `artifacts/*`): `artifacts/test_inventory/adg_mcp_redis_readthrough_inventory.md`.

**W2.1 delta (implemented):** `ADGService.get_mv_hotspot_centrality` prefers `MVRedisReader.get_mv_top("mv_hotspot_centrality", …)` ranking when Redis is reachable; **`SQLiteBackend.hydrate_mv_hotspot_centrality_ordered`** supplies full MV rows while preserving Redis order; **`backend_used`** reports **`redis`** on successful hydrated hit, else **`sqlite`**. Divergence (missing Redis ID in SQLite MV) ⇒ **full** canonical SQLite `ORDER BY`.

**W4 verification (`backend_used`, payload shape, no real Redis):** Mock `MVRedisReader` + patched service in **`tests/unit/tools/adg/test_get_mv_hotspot_centrality_readthrough.py`**; real `ADGService` + mocked reader in **`tests/unit/tools/adg/mcp/test_p33_graph_layer_tools.py`**; MCP handler passthrough **`test_tool_handler_adg_mv_hotspot_centrality_passes_through_payload_and_backend`**. Evidence table: **`docs/reports/adg/adg_mcp_redis_mv_key_contract.md`** § W4 verification.

**W5 doctrine sync (COMPLETE):** Canonical retrieval ladder and verbatim doctrine replicated in **`.cursor/skills/adg-sqlite/SKILL.md`**, **`graph-analysis/SKILL.md`**, **`mcp-integration/SKILL.md` §2**, and **`.cursor/rules/adg-canonical-invariants.mdc` §1**. Evidence cross-reference: **`docs/reports/adg/adg_mcp_redis_mv_key_contract.md`** § W5 doctrine sync. **No ADGService behavior change** in W5; obsolete MCP handler tests (**`test_mv_mcp_handlers.py`**) remain out of scope.

**Glossary**

- **`_read_through_cache` column:** The repo does **not** define `_read_through_cache`. The implemented read-through primitive is **`ADGService._query_with_fallback`** (Redis-first with SQLite backfill in `RedisCache`). “**yes**” = method uses `_query_with_fallback`; “**no**” = direct `SQLiteBackend` / projection-only / lifecycle with no Redis query path.

- **`backend_used` today:** Matches `ADGResponse.backend_used` returned from `ADGService` for data tools where applicable (`redis`, `sqlite`, or `projection`). Lifecycle/diagnostic tools annotate behavior in Notes.

- **Redis material exists?**

  - **yes:** `RedisCache` exposes concrete get/set keys for that operation (`tools/adg/cache/redis_cache.py`).
  - **yes (MV/P-view projector):** `tools/adg/mv_projection.py` defines Redis keys (`mv:<table_name>` ZSET, `pview:<view>` SET) ingestible separately; **`MVRedisReader`** (`tools/adg/mv_reader.py`) can read them — **`ADGService` uses `MVRedisReader` for `get_mv_hotspot_centrality` (W2.1)**; other MV/P-view MCP tools remain SQLite-only until planned.
  - **no:** No corresponding cache surface in `RedisCache` / no projector row clearly matching the MCP payload shape.

---

## MCP tools → service → Redis (matrix)

| MCP tool name | MCP handler file | ADGService method called | Current backend path | Uses `_query_with_fallback` today? | `backend_used` behavior today | Redis material exists? | W2 recommendation | Notes |
|---------------|------------------|----------------------------|----------------------|-----------------------------------|-------------------------------|-------------------------|-------------------|-------|
| `adg_health` | `tools/adg/mcp/tool_handlers.py` (`adg_health`) | `health()`, `get_status()`, `get_projection_status()` (via `HealthDiagnostics`) | SQLite status + Redis health probe + optional SQLite projection probe | **no** | **mixed:** health mode string; projection block is SQLite-derived | unknown (projection subset) | **OUT_OF_SCOPE** | Primary diagnostics; `full_report()` in `tools/adg/mcp/health.py`. Not a graph read-through hotspot. |
| `adg_status` | `tool_handlers.adg_status` | `get_status()` | Direct `SQLiteBackend.get_status()` | **no** | **`sqlite`** | **no** | **OUT_OF_SCOPE** | Metadata only. |
| `adg_node` | `tool_handlers.adg_node` | `get_node()` | `RedisCache.get_node` → miss → `SQLiteBackend.get_node` + optional `set_node` | **yes** | **`redis`** on warm hit else **`sqlite`** | **yes** (`RedisCache`) | **IN_SCOPE** (already wired) | Documented Redis-first in `server.py`. |
| `adg_nodes_by_layer` | `tool_handlers.adg_nodes_by_layer` | `get_nodes_by_layer()` | `RedisCache.get_nodes_by_layer` → SQLite + backfill | **yes** | **`redis`** / **`sqlite`** | **yes** (`RedisCache`) | **IN_SCOPE** (already wired) | `server.py` docstring incorrectly says “SQLite-only”; implementation uses **`_query_with_fallback`**. |
| `adg_nodes_by_file` | `tool_handlers.adg_nodes_by_file` | `get_nodes_by_file()` | Redis → SQLite read-through | **yes** | **`redis`** / **`sqlite`** | **yes** (`RedisCache`) | **IN_SCOPE** (already wired) | Fan-in / fan-out sibling path per plan context. |
| `adg_find_node` | `tool_handlers.adg_find_node` | `find_node()` | Direct `SQLiteBackend.find_node()` | **no** | **`sqlite`** | **no** (no name index in `RedisCache`) | **CANDIDATE** | **Must include:** name/prefix lookup; Redis would need new keying or MV-derived index (post‑hotspot‑key waves). |
| `adg_edge_fanout` | `tool_handlers.adg_edge_fanout` | `get_edge_fanout()` | Redis → SQLite read-through | **yes** | **`redis`** / **`sqlite`** | **yes** (`RedisCache`) | **IN_SCOPE** (already wired) | |
| `adg_edge_fanin` | `tool_handlers.adg_edge_fanin` | `get_edge_fanin()` | Redis → SQLite read-through | **yes** | **`redis`** / **`sqlite`** | **yes** (`RedisCache`) | **IN_SCOPE** (already wired) | |
| `adg_violations` | `tool_handlers.adg_violations` | `get_violations()` | Direct SQLite | **no** | **`sqlite`** | **no** | **CANDIDATE** | Large list; cache policy TBD. |
| `adg_p0_wave_plan` | `tool_handlers.adg_p0_wave_plan` | `get_p0_remediation_wave_plan()` | Direct SQLite | **no** | **`sqlite`** | **no** | **CANDIDATE** | Wave planner; may stay cold-path. |
| `adg_close_connections` | `tool_handlers.adg_close_connections` | `close()` (service lifecycle) | N/A | **no** | **n/a** | **no** | **OUT_OF_SCOPE** | Lock release helper. |
| `adg_reopen_connections` | `tool_handlers.adg_reopen_connections` | `reopen()` | N/A | **no** | **n/a** | **no** | **OUT_OF_SCOPE** | Refreshes snapshot id for Redis keys. |
| `adg_runtime_info` | `tool_handlers.adg_runtime_info` | (none — `ADGServerRuntime`) | Process metadata | **no** | **n/a** | **no** | **OUT_OF_SCOPE** | |
| `adg_reload` | `tool_handlers.adg_reload` | `reload_latest_snapshot()` + service refresh | SQLite reconnect | **no** | **n/a** | **no** | **OUT_OF_SCOPE** | |
| `adg_mv_hotspot_centrality` | `tool_handlers.adg_mv_hotspot_centrality` | `get_mv_hotspot_centrality()` | **W2.1:** `MVRedisReader.get_mv_top(mv_hotspot_centrality)` → miss/empty ⇒ `SQLiteBackend.get_mv_hotspot_centrality`; on non-empty Redis ranking **`hydrate_mv_hotspot_centrality_ordered`** (**SQLite authoritative row material**) | **hybrid MV read-through + hydrate (not `_query_with_fallback`)** | **`redis`** on warm hydrated ranking match; **`sqlite`** otherwise | **yes** (`mv:mv_hotspot_centrality` ZSET via projector; `MVRedisReader`) | **W4 DONE** | **W3:** key contract `docs/reports/adg/adg_mcp_redis_mv_key_contract.md`; **`adg_redis_ingest`** does **not** write MV ZSET (use **`mv_projection.project_all`**). **W4:** `backend_used` + **`data.keys() == {hotspots,count}`** — tests in **`test_get_mv_hotspot_centrality_readthrough`** + **`test_p33_graph_layer_tools`** (see contract doc § W4). |
| `adg_blast_radius` | `tool_handlers.adg_blast_radius` | `get_blast_radius()` | `SQLiteBackend.get_blast_radius()` → `GraphProjectionBackend` when `_graph_store` present | **no** | **`projection`** (stub dict when overlay missing) | **partial:** `mv_projection` projects `mv_graph_critical_path_blast_radius` ZSET globally; MCP returns **per-node** projection summary — **different shape** than ZSET rows | **CANDIDATE** | **Must include:** Not `sqlite`; Redis MV is related but **not proven equivalent** for per-node blast (`unknown` bridging). |
| `adg_semantic_fanout` | `tool_handlers.adg_semantic_fanout` | `get_semantic_fanout()` → `get_edge_fanout()` | Same as fanout after validation | **yes** (on success path) | **`redis`** / **`sqlite`** (or **`sqlite`** error envelope for bad relation_type) | **yes** (`RedisCache`, via fanout) | **IN_SCOPE** (delegated) | |
| `adg_p_view_query` | `tool_handlers.adg_p_view_query` | `query_p_view()` | Direct `SQLiteBackend.query_p_view()` | **no** | **`sqlite`** | **yes (MV/P-view projector):** `pview:<view_name>` SET holds **members**; MCP returns **full row tuples** — membership ≠ row payload | **CANDIDATE** | **Must include:** Useful for warm existence / cardinality via `MVRedisReader`; **full row read-through** likely still SQLite or extended Redis material (post‑hotspot‑key waves). |

---

## Highlighted MCP paths (plan-required)

| Item | MCP tool | Read-through via `_query_with_fallback` | `backend_used` | Redis notes |
|------|----------|----------------------------------------|----------------|-------------|
| **get_mv_hotspot_centrality** | `adg_mv_hotspot_centrality` | **W2.1 hybrid** (`MVRedisReader` + SQLite hydrate / fallback) | **`redis`** / **`sqlite`** | Redis ZSET rank + SQLite row authority; `[]` / `None` / error ⇒ SQLite `ORDER BY`. |
| **find_node** | `adg_find_node` | **no** | **`sqlite`** | No `RedisCache` / projector path for arbitrary name lookup. |
| **query_p_view** | `adg_p_view_query` | **no** | **`sqlite`** | P-view SET in Redis does not carry MCP row shape. |
| **get_blast_radius** | `adg_blast_radius` | **no** | **`projection`** | Per-node overlay in SQLite projection; Redis ZSET for critical-path hotspots is orthogonal. |

### Fan-in / fan-out / node-by-file

| MCP tool | Service method | Read-through |
|----------|----------------|--------------|
| `adg_edge_fanin` | `get_edge_fanin` | **yes** |
| `adg_edge_fanout` | `get_edge_fanout` | **yes** |
| `adg_nodes_by_file` | `get_nodes_by_file` | **yes** |

---

## CI / ratchet peers — **CI_SQLITE_BY_DESIGN**

These scripts **`sqlite3.connect`** against **`artifacts/adg/adg_indexed_*.sqlite`** (or `_adg_snapshot_diff` resolver peers) **by design**, not MCP read-through nor `RedisCache`. **CI parity:** reproducible snapshots, stable baselines.

| Script | Role / provenance note |
|--------|-------------------------|
| **`ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py`** | L5 fan-in hotspot ratchet vs canonical snapshot; **`DEFAULT_RATCHET` / baseline not edited by this W1.** |
| `ops_scripts/ci/check_authority_boundary_breaches.py` | MV authority breaches from latest snapshot (`mv_authority_boundary_breaches`). |
| `ops_scripts/ci/check_snapshot_has_mvs.py` | Graph-layer completeness on canonical SQLite artifact. |
| `ops_scripts/ci/check_apps_spine_delegation.py` | Explicitly documents direct SQLite ingress for spine proof (comments: no MCP path). |
| `ops_scripts/ci/check_runtime_proof_view_well_formed.py` | Projection/view well-formed gate on SQLite. |
| `ops_scripts/ci/check_edge_authority_well_formed.py` | SQLite edge-authority invariant. |
| `ops_scripts/ci/check_exception_contract.py` | Queries latest ADG SQLite for exception contract. |
| `ops_scripts/ci/infra_wiring_scan.py` | ADG view-count plumbing for wiring scan (`sqlite3` inline). |
| `ops_scripts/ci/adg_gates/gate_p0_*.py` | ADG CI gate base → SQLite connection. |
| `ops_scripts/ci/_adg_wiring_gate_base.py` | Shared latest-snapshot resolver for wiring gates. |
| `ops_scripts/ci/check_unresolved_edges_ratchet.py` | Snapshot-based ratchet. |
| `ops_scripts/ci/executor_theater_gate.py` | Optional pinned `adg_indexed_*.sqlite` queries. |

**Doctrine line:** SQLite canonical snapshot; **Redis is hot MCP projection**, not authoritative for parity gates above.

---

## Top W2 candidates (ranked)

1. **`get_mv_hotspot_centrality` / `adg_mv_hotspot_centrality`** — **W2.1 shipped:** `MVRedisReader.get_mv_top` + `hydrate_mv_hotspot_centrality_ordered`; **`backend_used`** `redis` vs `sqlite`.
2. **`query_p_view` / `adg_p_view_query`** — **CANDIDATE:** Redis has membership SETs — accelerate membership/count or narrow queries before row fetch — full row parity still SQLite-heavy without richer materialization.
3. **`find_node` / `adg_find_node`** — **CANDIDATE:** Requires new Redis key discipline or ancillary index ingest (currently **no material** mapped to MCP response).
4. **`get_blast_radius` / `adg_blast_radius`** — **CANDIDATE / unknown:** Projection-backed + global Redis MV for critical-path hotspots; **proving equivalence** between per-node MCP response and Redis ZSET content is **not established** → treat as gated unknown until W3 spec.

---

## Blocked unknowns (Redis warm path not proven for MCP payloads)

| Area | Gap |
|------|-----|
| **`adg_blast_radius`** | Redis `mv_graph_critical_path_blast_radius` aggregate vs MCP per-node **`projection`** blob — linkage unproven without schema analysis + ingest alignment. |
| **`adg_p_view_query`** | Redis stores **members** only; MCP returns **`rows`** (full columns); hit semantics differ. |

---

## Files inspected (inventory sources)

`tools/adg/mcp/server.py`, `tools/adg/mcp/tool_handlers.py`, `tools/adg/mcp/health.py`, `tools/adg/mcp/runtime.py`, `tools/adg/core/service.py`, `tools/adg/core/sqlite_backend.py`, `tools/adg/cache/redis_cache.py`, `tools/adg/mv_reader.py`, `tools/adg/mv_projection.py`, plus `rg` scans under `ops_scripts/ci` for SQLite ADG parity.
