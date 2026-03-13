---
description: Regenerate ADG and reload Redis hot cache - run after any code refactoring or structural change
---

# ADG Redis Refresh Workflow

Invoke with `/adg-redis-refresh`. Runs after any refactor, import change, or structural code edit to keep the ADG Redis hot cache current.

---

## STEP 0: Verify Redis server is running (100% availability gate)

**MANDATORY FIRST STEP** - Ensures Redis is available before any cache operations.

// turbo
```
python tools/adg/redis_health_check.py --auto-start
```

**Exit codes:**
- `0` → Redis running + ADG cache HOT → **SKIP to STEP 5**
- `1` → Redis running + ADG cache cold → **Continue to STEP 1**
- `2` → Redis down (auto-start attempted) → **STOP and fix Redis**

If exit code 2, Redis could not be started automatically. Manual intervention required:
- Windows: Start Redis service via `sc start Redis` or launch `redis-server.exe`
- Verify: `redis-cli ping` should return `PONG`

---

## STEP 1: Check Redis cache staleness

// turbo
```
python -c "import redis, os; r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True); meta = r.hgetall('adg:meta'); print('Cache timestamp:', meta.get('timestamp','MISSING')); print('Node count:', meta.get('node_count','MISSING')); print('Edge count:', meta.get('edge_count','MISSING')); print('Digest:', meta.get('digest','MISSING')[:16] if meta.get('digest') else 'MISSING')"
```

If `MISSING` → cache is cold, proceed directly to STEP 3.
If timestamp is stale vs. recent code changes → proceed to STEP 2.
If timestamp matches current ADG artifacts → **STOP**, cache is hot.

---

## STEP 2: Regenerate ADG from source

**Only run if code has changed since last ADG generation.**
This is an expensive full AST scan (~2-5 min). Do not skip if code changed.

```
python tools/generate_full_adg.py
```

Wait for completion. Verify new `.sqlite` and `_snapshot_*.json` files appear in `artifacts/adg/`.

---

## STEP 3: Load refreshed ADG into Redis

// turbo
```
python tools/adg/adg_redis_ingest.py --force
```

Expected output:
```
[redis] connected localhost:6379
[sqlite] tables: ['edges', 'meta', 'nodes', 'sqlite_sequence']
[redis] flushing existing adg:* keys ...
[sqlite] ingesting N nodes ...
[redis] nodes done
[sqlite] ingesting N edges ...
[redis] edges done
[redis] snapshot stored
[redis] meta written
[done] ADG -> Redis ingest complete
```

---

## STEP 4: Verify cache health

// turbo
```
python -c "import redis, json; r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True); meta = r.hgetall('adg:meta'); print('=== ADG REDIS HEALTH ==='); [print(f'  {k}: {v}') for k, v in meta.items()]; print(f'  total_keys: {r.dbsize()}')"
```

**Gate:** Must see `node_count` >= 8000 and `total_keys` >= 100000 before proceeding with any analysis.

---

## STEP 5: Confirm ADG is driving queries

From this point all analysis queries use Redis Tier-1 lookups via `tools/adg/adg_redis_query.py`:

- `adg:node:<id>` — node details by integer ID
- `adg:nodes:by_layer:<layer>` — all node IDs in a layer (L0–L_UNKNOWN)
- `adg:nodes:by_file:<resolved_path>` — all node IDs for a file
- `adg:edge:<src_id>:<relation_type>` — fan-out targets
- `adg:edge:in:<dst_id>:<relation_type>` — fan-in sources
- `adg:snapshot` — full snapshot JSON

Fall back to `artifacts/adg/adg_indexed_*.sqlite` only for JOIN/CTE queries not expressible via key lookups.

---

## When to run this workflow

| Trigger | Required steps |
|---|---|
| Code refactored (imports changed) | STEP 2 + STEP 3 + STEP 4 |
| Redis restarted / keys flushed | STEP 3 + STEP 4 (skip STEP 2 if no code changes) |
| New session, cache cold | STEP 1 → STEP 3 + STEP 4 |
| Pre-analysis staleness check only | STEP 1 only |

---

## Staleness guard behaviour

The ingest script (`tools/adg/adg_redis_ingest.py`) auto-detects staleness by comparing the `sqlite_mtime` stored in `adg:meta` against the current `.sqlite` file modification time. Without `--force`, it will skip ingest if the cache is already current.

---

## References

- Ingest script: `tools/adg/adg_redis_ingest.py`
- Query helper: `tools/adg/adg_redis_query.py`
- ADG artifacts: `artifacts/adg/`
- ADG regeneration: `tools/generate_full_adg.py`
- Memory: ADG Pre-Ingest Rule (MEMORY[1c4e46e0])
