# ADG Redis Hotcache Query Alignment

```json
{
  "entities": [{
    "name": "ProceduralPattern:ADGRedisHotcacheQueryAlignment",
    "entityType": "ProceduralPattern",
    "observations": [
      "Fixes ADG Redis cache misses caused by helpers reading legacy unversioned keys while adg_redis_ingest writes versioned snapshot keys.",
      "Use tools/adg/adg_redis_ingest.py --check to verify the current workspace's latest adg_indexed_<ts>.sqlite has adg:v1:<ts>:_hot.",
      "Use tools/adg/adg_redis_query.py for quick node/edge lookups; it must resolve snapshot_id/cache_version from adg:meta/adg:status and read adg:v1:<snapshot_id>:node|edge|fanin|edge_detail keys.",
      "Use tools/adg/adg_stale_guard.py --json for commit-vs-SQLite-snapshot freshness; Git queries must use --after=@<epoch> to avoid UTC/local timezone drift, and freshness must prefer adg:meta.sqlite_mtime over ingested_at so re-ingesting an old SQLite file cannot mask stale graph content.",
      "Do not rely on tools/generate_full_adg.py, tools/adg/redis_health_check.py, tools/adg/adg_test_selector.py, or tools/adg/adg_type_check.py in this checkout unless those files are restored; the canonical generator path is tools/generate/generate_full_adg.py.",
      "discovered: 2026-06-29, validated: 2026-06-29"
    ]
  }]
}
```
