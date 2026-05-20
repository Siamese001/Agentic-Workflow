# Redis MCP Operator Guide

Operational reference for the Redis MCP server (`tools/mcp/redis_mcp_server.py`).

---

## Environment Variables

| Variable | Default | Notes |
|---|---|---|
| `REDIS_HOST` | `localhost` | Hostname or IP of the Redis server |
| `REDIS_PORT` | `6379` | TCP port |
| `REDIS_DB` | `0` | Database index (0–15) |
| `REDIS_TIMEOUT` | `5` | Socket timeout in **seconds** — accepts floats (e.g. `0.5`) |

All four are read once at first tool call and cached in a module-level `ConnectionPool`.
To change them at runtime, restart the MCP server process — the pool is not hot-reloaded.

---

## Connection Behavior

The server uses a lazy `ConnectionPool` singleton (`_pool`). On the first call to any
tool the pool is constructed from the env vars above and reused for all subsequent calls
within the same process lifetime. This eliminates per-call TCP overhead.

`_reset_pool()` is an internal helper for test teardown only — it is **not** exposed as
an MCP tool.

---

## Tool Reference

### `redis_health`
Ping Redis and return a summary of INFO stats.

- Returns: `redis_version`, `uptime_seconds`, `connected_clients`, memory stats,
  `total_commands_processed`, `role`, `host`, `port`.
- **`keyspace`** reflects the active `REDIS_DB` (e.g. `db2` when `REDIS_DB=2`).
  Prior to the hardening pass this was hardcoded to `db0`.

### `redis_dbsize`
Returns the total number of keys in the current database.

### `redis_namespace_stats(top_n=20)`
Scans all keys and groups them by top-level namespace prefix (the segment before the
first `:`). Returns counts sorted descending.

- **`top_n` is hard-capped at 100** regardless of the value passed. Values above 100
  are silently clamped — no error is raised.
- Scan halts at 50 000 keys; `truncated: true` appears in the response if the cap was hit.

### `redis_keys(pattern="adg:*", limit=50)`
SCAN-based key listing. Safe — never uses `KEYS` command.

- `limit` is hard-capped at 200.

### `redis_get(key)`
Fetch the value for a single key. Auto-detects Redis type.

**Payload truncation** (all truncated responses include `truncated: true`):

| Type | Condition | Behavior |
|---|---|---|
| `string` | value > 64 KB | `value: "<truncated>"`, `value_bytes: N` |
| `hash` | > 500 fields | `value`: list of field names only (no values) |
| `set` | > 500 members | `value`: first 500 members via SSCAN |
| `list` | always | capped at 100 elements |
| `zset` | always | capped at 100 elements with scores |

Non-truncated responses always include `truncated: false` so callers can check
unconditionally without a `KeyError`.

Missing keys return `{"status": "not_found", "key": ...}` — determined via
`type()` returning `"none"`, no separate `exists()` round-trip.

### `redis_hgetall(key)`
HGETALL for a hash key.

- Missing key → `status: not_found`.
- Wrong type → `status: error`.
- Hashes > 500 fields → field names only + `truncated: true`.
- Normal path → full field dict + `truncated: false`.

### `redis_ttl(key)`
Returns TTL for a key.

- `ttl_seconds: -1` → key exists, no expiry (`interpretation: "no_expiry"`)
- `ttl_seconds: -2` → key does not exist (`interpretation: "not_found"`)
- `ttl_seconds: N` → expires in N seconds (`interpretation: "expires_in_Ns"`)

> **Contract change (hardening pass):** The `exists` field was removed. Use
> `ttl_seconds != -2` or `interpretation != "not_found"` to check key presence.

### `redis_del_key(key)`
Delete a single key. `existed` and `deleted` are both derived from the return value of
`DEL` — no separate `exists()` pre-check is performed.

### `redis_flush_namespace(pattern, dry_run=True)`
Delete all keys matching a glob pattern.

**`dry_run=True` is the default** — it is not possible to accidentally delete keys
without explicitly passing `dry_run=False`.

Dry-run response:
```json
{
  "status": "ok",
  "dry_run": true,
  "pattern": "adg:node:*",
  "matching_count": 1234,
  "sample": ["adg:node:abc", "..."],
  "message": "Set dry_run=False to actually delete"
}
```

Live-delete response:
```json
{
  "status": "ok",
  "dry_run": false,
  "pattern": "adg:node:*",
  "deleted_count": 1234,
  "truncated": false
}
```

`truncated: true` appears when the internal SCAN collected more than 5 000 matching keys
before deletion — keys beyond the cap are **not** deleted in that pass.

> **Reduced TOCTOU:** Deletes are issued in batches of 500 via `pipeline(transaction=False)`,
> which shrinks the race window compared to a single bulk `DEL`. Keys added between SCAN
> completion and pipeline execution are still silently missed. Full elimination (Lua
> atomic scan+delete) is deferred to a follow-on hardening pass. For the ADG cache use
> case (append-heavy, no concurrent writers during a flush) this residual risk is low.

### `redis_stats`
Returns full `INFO all` output partitioned into sections: `server`, `memory`,
`persistence`, `replication`, `clients`, `stats`, `keyspace`.

---

## Error Shape

All tools return a consistent error shape when Redis is unreachable:

```json
{"status": "unavailable", "error": "Redis connection refused: ..."}
```

---

## Example Calls

### 1. Check server health on DB 2

```
REDIS_DB=2 → redis_health()
```

Expected shape (abridged):
```json
{
  "status": "ok",
  "redis_version": "7.2.0",
  "keyspace": {"keys": 9200, "expires": 120},
  "role": "master"
}
```

### 2. List all ADG node keys (first 50)

```
redis_keys(pattern="adg:node:*", limit=50)
```

Expected shape:
```json
{
  "status": "ok",
  "pattern": "adg:node:*",
  "count": 50,
  "keys": ["adg:node:tools.mcp.redis_mcp_server", "..."]
}
```

### 3. Inspect a large ADG node hash

```
redis_hgetall(key="adg:node:agentic_core.L3_orchestration.reasoning.engine")
```

Non-truncated (≤500 fields):
```json
{
  "status": "ok",
  "key": "adg:node:...",
  "ttl_seconds": -1,
  "fields": {"layer": "L3", "node_type": "module", "...": "..."},
  "truncated": false
}
```

### 4. Check TTL on a coordination lock

```
redis_ttl(key="coord:lock:session-abc")
```

```json
{
  "status": "ok",
  "key": "coord:lock:session-abc",
  "ttl_seconds": 28,
  "interpretation": "expires_in_28s"
}
```

### 5. Dry-run flush of ADG node cache

```
redis_flush_namespace(pattern="adg:node:*")          # dry_run=True by default
```

```json
{
  "status": "ok",
  "dry_run": true,
  "pattern": "adg:node:*",
  "matching_count": 9200,
  "sample": ["adg:node:agentic_core...", "..."],
  "message": "Set dry_run=False to actually delete"
}
```

### 6. Namespace breakdown (top 10)

```
redis_namespace_stats(top_n=10)
```

```json
{
  "status": "ok",
  "scanned_keys": 11400,
  "truncated": false,
  "namespaces": [
    {"prefix": "adg", "count": 9200},
    {"prefix": "coord", "count": 800},
    {"prefix": "embed", "count": 1400}
  ]
}
```

---

## Windows dev steady state (ADG + Docker)

**Problem:** A stopped or restarted `redis-memory` container (`redis:7-alpine` on host port
6379) competes with the Windows `Redis` service. MCP and `ADG_REDIS_URL` then hit the wrong
backend (empty Docker vs populated Windows cache).

**Default (recommended):**

1. One listener on **6379** — Windows Redis with `ADG_REDIS_URL=redis://localhost:6379/0`.
2. **Remove** container `redis-memory`; **keep** the `redis:7-alpine` image for CI/compose.
3. Graph queries use **`adg_sqlite` MCP** (Redis is internal read-through cache, not the `redis` MCP).
4. After a new ADG snapshot: `python tools/adg/adg_redis_ingest.py` then `--check`.

**Apply + verify in one command:**

```bash
python ops_scripts/adg/redis_dev_steady_state.py
```

**Integration tests** use [docker-compose.redis.yml](../../docker-compose.redis.yml) on port **6390**
(not 6379) to avoid clashing with dev Redis.

**Optional migration to Docker Redis 7:** stop Windows `Redis` service, run a single container on
6379, then `python tools/adg/adg_redis_ingest.py --force` and confirm `redis_version` is 7.x on
localhost.
