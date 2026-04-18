# G4 — Redis Namespace Map

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).
**Redis health** (live at G4 authoring): `redis_version=3.0.504`, `used_memory=1.67 GB`, `keys=2,384,099`, `expires=1`, `role=master`, `localhost:6379/db=0`, `uptime=240,875 s` (~2.8 days).

## 1. Namespace scan summary

`mcp9_redis_namespace_stats` sampled 50,031 keys:

| Prefix | Scanned-sample keys | Actual-store role |
|---|---:|---|
| `adg` | 38,803 | ADG hot cache (all versioned under `adg:v1:<ts>:*`) — **dominant** |
| `bench` | 11,228 | Legacy benchmark fixture (**candidate for flush, B7-G4-04**) |

Total-store key count is 2.38 M — the sample is biased toward high-count prefixes; smaller namespaces (`coord:`, `rag:`, `cache:`) exist in code but are below the sampling window.

## 2. Authoritative ADG namespace schema

Per `tools/adg/adg_redis_ingest.py` header (lines 8–14):

| Key pattern | Redis type | Purpose |
|---|---|---|
| `adg:v1:<snapshot_id>:node:<node_id>` | HSET | node fields, pre-ingested |
| `adg:v1:<snapshot_id>:edge:<src_id>:<rel>` | SADD (set of edge_ids) | fanout index |
| `adg:v1:<snapshot_id>:fanin:<dst_id>:<rel>` | SADD (set of edge_ids) | fanin index |
| `adg:v1:<snapshot_id>:edge_detail:<edge_id>` | HSET | edge fields, pre-ingested |
| `adg:v1:<snapshot_id>:_hot` | STRING "1" | sentinel — cache populated |

**Currently hot**: `adg:v1:04172026_0611:_hot` (single key — matches active ADG snapshot).

## 3. Per-namespace ownership

### 3.1 `adg:v1:*` (hot ADG cache)

| Role | Modules |
|---|---|
| **Owner** | `tools/adg/cache/redis_cache.py` (schema definition) |
| **Writer** | `tools/adg/adg_redis_ingest.py` (bulk + lazy warm); `tools/adg/cache/redis_cache.py` (miss warm) |
| **Reader** | `tools/adg/mcp/server.py` (Redis-first path with SQLite fallback); `tools/adg/queries/adg_redis_live_query.py`; `tools/adg/queries/adg_rlhf_sft_query.py`; `tools/adg/queries/adg_rlhf_sft_query2.py`; `agentic_core/adg/extraction/optimized_tools.py` |
| **Lifecycle** | Fresh namespace per snapshot id. `_hot` sentinel signals populated. `--force` flushes a stale namespace. Default TTL: none (lives until explicit flush or snapshot supersession). |
| **Pipelines** | `PIPE-ADG-REDIS-INGEST` (writer); `PIPE-ADG-GEN` stage s09 (ingest); all `adg_sqlite` MCP queries (reader) |
| **State machine** | `SM-07 RedisHotCache` (COLD / HOT / DEGRADED) |

### 3.2 `bench:*`

| Role | Observed state |
|---|---|
| **Owner** | none enumerated — no current writer in repo Python source |
| **Writer** | none (11,228 keys with prefix `bench:edge:*` observed; presumably residual from a past benchmark run) |
| **Reader** | none in current runtime |
| **Lifecycle** | **Orphan**. Candidate for flush via `mcp9_redis_flush_namespace(pattern="bench:*")`. |
| **Pipelines** | none |
| **B7** | B7-G4-04 — orphan namespace, no current owner. |

### 3.3 `coord:*`

| Role | Modules |
|---|---|
| **Owner** | `agentic_core/cache/redis_coordination_fabric.py` |
| **Writer** | same |
| **Reader** | same + `tools/mcp/redis_mcp/read_tools.py` (inspection path) |
| **Lifecycle** | Per-session coordination state. TTL per code path (not globally enumerated). |
| **Pipelines** | `PIPE-APP-REQUEST` (coordination side-channel between L2/L3 agents) |

### 3.4 `rag:*`

| Role | Modules |
|---|---|
| **Owner** | `agentic_core/cache/cache_key_builders.py` (key-builder recipes) |
| **Writer** | `agentic_core/cache/core/cache_key_builders.py`, `agentic_core/runtime/config/model_provider_config.py` |
| **Reader** | `agentic_core/cache/redis_coordination_fabric.py` |
| **Lifecycle** | Per-RAG-query TTL; key shape documented in `cache_key_builders.py`. |
| **Pipelines** | `PIPE-VECTOR-RETRIEVAL` (cache layer) |

### 3.5 `cache:*` (generic)

| Role | Modules |
|---|---|
| **Owner** | `agentic_core/cache/redis_cache_client.py` — **G2 chokepoint bridge** (fan_in=fan_out=70) |
| **Writer** | `agentic_core/cache/{graph_aware_cache,policy_registry_cache,schema_validator_cache,tool_embedding_cache,discovery_cache,config_file_cache}.py` |
| **Reader** | same set |
| **Lifecycle** | TTL per key-builder recipe. No global invalidation surface. |
| **Pipelines** | `PIPE-APP-REQUEST` (reasoning / policy cache); `PIPE-HEALING` (classifier cache) |

### 3.6 Additional literal-match prefixes observed in code

`session:`, `healing:`, `memory:`, `eval:`, `gptcache:` — each observed in ≥ 1 module but not enumerated as discrete Redis namespaces (many are dict keys or log strings, not Redis key roots). Not catalogued as independent namespaces at G4; deeper attribution deferred to G4b.

## 4. Redis-as-authoritative vs Redis-as-cache

| Namespace | Authoritative source | If Redis lost |
|---|---|---|
| `adg:v1:*` | ADG SQLite (`artifacts/adg/adg_indexed_<ts>.sqlite`) | rebuild via `adg_redis_ingest.py --force` |
| `coord:*` | none — **Redis-only state** | session state lost |
| `rag:*` | none — cache only | recomputed on next query |
| `cache:*` | none — cache only | recomputed |
| `bench:*` | none — orphan | no impact |

**Risk**: `coord:*` is the only namespace that appears to be Redis-authoritative (no SQLite / disk back-stop observed). If this is cross-session coordination state, loss = data loss; if per-run, loss = no impact. G4b / G6 should clarify.

## 5. TTL and expiration

`redis_health.expires = 1` — exactly ONE key in the entire 2.38 M-key store has a TTL set. Effectively, Redis in this deployment is used as a **persistent-feeling cache with no auto-expiry**. Invalidation is done manually via `mcp9_redis_flush_namespace`, `adg_redis_ingest.py --force`, or targeted `mcp9_redis_del_key`.

## 6. Capacity planning

- **Observed memory**: 1.67 GB used / 1.68 GB peak (0.6% headroom consumed over time).
- **Dominant consumer**: `adg:v1:*` — scales with ADG snapshot size (~83k nodes × ~8 edges per node). 
- **Key count**: 2.38 M keys is a large but manageable working set. If the repo grows, a new snapshot could push key count to ~4 M.
- **B7-G4-07**: No observed memory-eviction policy, no TTL discipline, no shard strategy. Single-master `localhost:6379`. Suitable for dev, not for production scale-out.

## 7. MCP-side env-keys bound to Redis

Per G2b `env_key_consumer_map.md`:

| Env key | Consumers |
|---|---|
| `REDIS_HOST` | 7 modules |
| `REDIS_PORT` | 6 modules |
| `REDIS_DB` | 5 modules |
| `REDIS_PASSWORD` | 3 modules (auth optional) |
| `REDIS_URL` | 3 modules |
| `REDIS_TIMEOUT`, `REDIS_SSL`, `REDIS_SSL_CERT_PATH`, `REDIS_SSL_KEY_PATH`, `REDIS_CACHE_STRICT_HASH_VALIDATION`, `REDIS_WINDOWS_PATHS` | 1 each |
| `ADG_REDIS_URL` | `tools/adg/adg_redis_ingest.py`, `tools/memory/adg_memory_server.py`, `tools/adg/core/service.py` |
| `USE_REDIS_CACHE`, `ENABLE_REDIS` | toggles |

## 8. Summary

- **6 active Redis namespaces** in code + 1 orphan (`bench:*`).
- **1 Redis-authoritative** namespace (`coord:*`) — everything else is cache with a SQLite or recomputation back-stop.
- **1 hot sentinel currently set**: `adg:v1:04172026_0611:_hot`.
- **Single point of egress** to Redis for the whole repo: `EGRESS-REDIS-01` per G2b.
- **3 B7 candidates from this file**: B7-G4-04 (bench orphan), B7-G4-07 (no TTL / eviction policy), and propagated G2b-05 (Redis retry posture unknown).
