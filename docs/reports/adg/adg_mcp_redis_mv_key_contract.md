# ADG MCP — Redis MV key contract (`mv_hotspot_centrality` only)

**Plan:** `.cursor/plans/adg-mcp-redis-readthrough-enforcement-b2e7a9.md` · **Technical waves documented:** W3–W5 · **As-of:** 2026-05-16

---

## W5 doctrine sync (plan closeout)

This section records governance alignment only (**no code-path changes** in W5).

**Canonical retrieval ladder (one line):** Redis warm projection → **`adg_sqlite` MCP** (read-only gateway) → SQLite direct only with **`DEGRADED_FALLBACK: reason=<…>`** unless matching a **named CI parity script**.

**Doctrine (verbatim):** SQLite is canonical truth. Redis is a hot projection/read-through optimization, never authority. MCP is the preferred read-only gateway for agents. Direct sqlite3 or SQLiteBackend access in plans requires either a named CI parity script or an explicit DEGRADED_FALLBACK reason. Warm Redis hits may serve MCP responses only when provenance is visible through backend_used and, where required, rows hydrate or validate against canonical SQLite. Cold, missing, error, empty, or divergent Redis falls back to SQLite. Agents must not silently default to raw sqlite3 for refactor or analysis work.

**Synced artifacts:** `.cursor/skills/adg-sqlite/SKILL.md`, `.cursor/skills/graph-analysis/SKILL.md`, `.cursor/skills/mcp-integration/SKILL.md` §2, `.cursor/rules/adg-canonical-invariants.mdc` §1; inventory header in **`docs/reports/adg/adg_mcp_redis_readthrough_inventory.md`**.

---

## Scope

This report proves or documents Redis **material**, **keys**, and **read/write alignment** needed for **`get_mv_hotspot_centrality` / `adg_mv_hotspot_centrality` (W2.1)** only. It does not cover node/edge `RedisCache` except where needed to contrast ingest paths.

---

## Canonical truth statement

**SQLite** (`artifacts/adg/adg_indexed_<MMDDYYYY_HHMM>.sqlite`, table **`mv_hotspot_centrality`**) is authoritative for:

- Presence or absence of a `node_id` row  
- Column values returned in MCP payloads  

Redis may rank members and accelerate top‑K retrieval; **`ADGService` uses SQLite hydration** for full dictionary rows (`hydrate_mv_hotspot_centrality_ordered`). Every warm hit is **SQLite‑verified**.

---

## Redis hot projection statement

Redis holds an **optional, non‑authoritative projection**: a sorted set (ZSET) per MV per snapshot prefix, keyed under `adg:v1:<snapshot_id>:…`.

**Separate from MCP node/edge cache:** `RedisCache` + `tools/adg/adg_redis_ingest.py` populate **`_hot`** sentinel and node/edge keys; they **do not** populate **`mv_hotspot_centrality`** ZSET keys. MV overlay is produced by **`tools/adg/mv_projection.py`** (or any tool that mirrors its `_redis_key` + ZADD semantics).

---

## `mv_hotspot_centrality` key contract

| Aspect | Specification |
|--------|----------------|
| **Key pattern** | `adg:{CACHE_VERSION}:{snapshot_id}:mv:mv_hotspot_centrality` |
| **`CACHE_VERSION`** | **`v1`** (must stay aligned across `mv_reader.py`, `mv_projection.py`, `adg_redis_ingest.py` key prefix) |
| **`snapshot_id`** | Same token as **`SQLiteBackend.get_status()["timestamp"]`**: basename of the active snapshot **`adg_indexed_<snapshot_id>.sqlite`** with the `adg_indexed_` prefix removed (e.g. `05162026_0649`). |
| **Redis type** | **ZSET** |
| **Member format** | String form of **`node_id`** (`str(member)` on write — see `_project_mv`); **`MVRedisReader.get_mv_top`** returns members as **`str`** after `decode_responses=True`. |
| **Score semantics** | **Float** **`degree_centrality`** (CAST REAL in projector SQL); higher score ⇒ more central **per MV table rows**. Ranking uses Redis **`ZREVRANGE`** (**highest score first**). This matches **DESC `degree_centrality`** ordering in **`SQLiteBackend.get_mv_hotspot_centrality`** for a full-table top‑N, but **warm path order is whatever Redis holds** until hydration; divergence handling below applies. |
| **Sidecar meta (writer)** | `adg:v1:{snapshot_id}:mv:mv_hotspot_centrality:meta` — HSET `{ table, member_col, metric, row_count, projected_at }` (reader does not require meta for **W2.1** warmup). |
| **Projection sentinel** | `adg:v1:{snapshot_id}:_mv_hot` STRING `1`, set **after** `project_all` completes (**not** consulted by **`get_mv_hotspot_centrality`** today; **`is_mv_hot` / tooling** may use it). |

**Agreement — writer vs reader:**

- **`mv_projection._project_mv`** builds `zset_key = _redis_key(snapshot_id, f"mv:{spec.table}")` with `spec.table == "mv_hotspot_centrality"`.  
- **`MVRedisReader.get_mv_top`** builds `key = _redis_key(snapshot_id, f"mv:{mv_name}")` with **`mv_name == "mv_hotspot_centrality"`** (`ADGService` hard-coded).  

Therefore both resolve to **`adg:v1:{snapshot_id}:mv:mv_hotspot_centrality`**.

---

## Reader behavior (`tools/adg/mv_reader.py`)

- **`get_mv_top(mv_name, snapshot_id, k)`** executes **`ZREVRANGE`** on the composed key from rank **`0`** through **`max(0, k - 1)`** inclusive → returns up to **`k`** tuples `(member_str, score_float)`.  
- **`k`** is **`SQLiteBackend._normalize_limit(limit, default=50)`** passed from **`get_mv_hotspot_centrality`**.  
- **Transport / parse errors:** return **`None`** (cold).  
- **Empty Redis response:** **`[]`** (reader cannot distinguish “key missing” vs “empty ZSET”; **W2.1 treats `[]` like cold** → full SQLite **`ORDER BY` fallback**.)

---

## Ingest writer behavior

| Writer | Writes `mv_hotspot_centrality` ZSET? | Notes |
|--------|--------------------------------------|-------|
| **`tools/adg/mv_projection.py`** **`_project_mv` / `project_all`** | **Yes** | Source of Redis MV ZSET rows + `_mv_hot`. Deletes stale ZSET/meta before rewrite. SQL: `CAST(degree_centrality AS REAL)` as score. |
| **`tools/adg/adg_redis_ingest.py`** | **No** | Loads **nodes/edges** keys + **`_hot`** sentinel per `RedisCache`; **orthogonal** to W2.1 hotspot MV ranks. Operators must **not** assume `adg_redis_ingest` warms MCP hotspot MV ranks. |

---

## Hydration back to SQLite (`tools/adg/core/sqlite_backend.py`)

- **`hydrate_mv_hotspot_centrality_ordered(ordered_node_ids)`** runs `SELECT * FROM mv_hotspot_centrality WHERE node_id IN (…)`.  
- Reassembles rows **in Redis rank order**.  
- Returns **`None`** if any **`node_id` missing**, duplicate ambiguity, or table error → **`ADGService` falls back** to **`get_mv_hotspot_centrality(limit)`** (SQLite canonical top‑N).  
- **`node_id` dtype:** SQLite INTEGER vs Redis string members — lookups use **`str(node_id)`** matching.

---

## Cold Redis behavior

- **`MVRedisReader` unavailable**, **`get_mv_top`**, **`None`**, **`[]`**, **hydrate `None`**, or **exception**: **`backend_used == "sqlite"`**; MCP payload shape unchanged.  
- **`adg_redis_ingest` hot `_hot`** does **not** imply MV ZSET hot.

---

## Divergence behavior

- Redis lists an id **absent from SQLite MV** → hydrate **`None`** → **full SQLite fallback** (**authoritative ranking** BY `degree_centrality`).  
- Stale **`snapshot_id`** (keys for old slice) vs current SQLite snapshot → **`ZREVRANGE`** miss/empty/err → SQLite path.

---

## Open gaps for later waves

| Item | Gap |
|------|-----|
| **`adg_p_view_query`** | Redis SET **`pview:`** exposes **membership**, not MCP **row payloads**. |
| **`adg_find_node`** | No **`RedisCache`** / MV surface for arbitrary name lookup. |
| **`adg_blast_radius`** | MCP uses **SQLite graph projection path** (`backend_used="projection"`); **`mv_graph_critical_path_blast_radius`** Redis ZSET is **not** wired to MCP per-node blast equivalence. |

---

## W4 verification (`backend_used`, payload, no real Redis)

| Scenario | `backend_used` | `ADGResponse.data` keys | Where tested |
|----------|----------------|-------------------------|--------------|
| Redis warm ranking + SQLite hydrate succeeds | `redis` | `{hotspots, count}` (`count == len(hotspots)`) | `test_hotspot_redis_hit_preserves_mv_order_and_sets_backend_used_redis`; `test_service_get_mv_hotspot_centrality_w4_redis_warm_preserves_backend_used_redis` |
| `MVRedisReader.available` false (cold MV client) | `sqlite` | same | `test_hotspot_mv_reader_down_falls_through_sqlite`; `test_service_get_mv_hotspot_centrality` |
| `get_mv_top` → `None` | `sqlite` | same | `test_hotspot_redis_miss_none_falls_through_sqlite_order` |
| `get_mv_top` → `[]` | `sqlite` | same | `test_hotspot_redis_empty_list_falls_through_sqlite` |
| `get_mv_top` raises | `sqlite` | same | `test_hotspot_redis_raises_falls_through_sqlite` |
| Divergent Redis `node_id` (missing SQLite MV row / hydrate `None`) | `sqlite` | same | `test_hotspot_divergent_node_id_fallback_sqlite`; `test_service_get_mv_hotspot_centrality_w4_missing_row_in_sqlite_fallback_sqlite` |
| MCP `adg_mv_hotspot_centrality` wrapper | echoes service | `{"status","data","backend_used"}` with `data` keys `{hotspots,count}` | `test_tool_handler_adg_mv_hotspot_centrality_passes_through_payload_and_backend` |

All hotspot path tests above use **mocked** `_mv_reader` / `MagicMock` readers — **no** `redis-server` requirement.

---

## Tests run (W3 / W4 / W2.1 narrow)

Evidence commands (repo root), **exit code 0** (2026-05-16, W4 re-run):

```bash
python -m pytest tests/unit/tools/adg/test_get_mv_hotspot_centrality_readthrough.py tests/unit/tools/adg/test_mv_hotspot_redis_key_contract.py tests/unit/tools/adg/mcp/test_p33_graph_layer_tools.py::test_service_get_mv_hotspot_centrality tests/unit/tools/adg/mcp/test_p33_graph_layer_tools.py::test_service_get_mv_hotspot_centrality_w4_redis_warm_preserves_backend_used_redis tests/unit/tools/adg/mcp/test_p33_graph_layer_tools.py::test_service_get_mv_hotspot_centrality_w4_missing_row_in_sqlite_fallback_sqlite tests/unit/tools/adg/mcp/test_p33_graph_layer_tools.py::test_tool_handler_adg_mv_hotspot_centrality_passes_through_payload_and_backend -q --tb=short

python -m pytest tests/unit/tools/adg/test_mv_projection.py -q --tb=short
# projector parity (environment-dependent Redis / fakeredis)
```
