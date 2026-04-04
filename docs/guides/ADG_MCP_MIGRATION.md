# ADG MCP Server Migration Guide

## Overview

This guide covers migrating from the old `adg_redis` MCP server to the new `adg_sqlite` MCP server. 

**Core Principle:** SQLite is the source of truth, Redis is optional acceleration, and `adg_sqlite` is the only ADG MCP surface that should be enabled.

The new server provides a single ADG MCP surface with SQLite as the canonical L4 authority and Redis as an internal optional accelerator only.

## Quick Comparison

| Aspect | Old (adg_redis) | New (adg_sqlite) |
|--------|-----------------|------------------|
| **Authority** | Redis (incorrect) | SQLite (correct) |
| **Redis Role** | Required | Optional cache |
| **Startup** | Fails if Redis down | Works if Redis down |
| **Cache Pattern** | Read/write through | Read-through only |
| **Health Check** | `adg_status` only | `adg_health` tool |
| **Architecture** | Cache as authority | SQLite as L4 authority |

## Migration Steps

### Step 1: Update MCP Configuration

Edit your global MCP configuration file at:
```
C:\Users\amita\.codeium\windsurf\mcp_config.json
```

Add the new server entry:
```json
{
  "mcpServers": {
    "adg_sqlite": {
      "command": "python",
      "args": ["-m", "tools.adg.mcp.server"],
      "cwd": "C:\\Git\\Agentic-Workflow",
      "disabled": false
    },
    "adg_redis": {
      "command": "python",
      "args": ["tools/adg/adg_mcp_server.py"],
      "cwd": "C:\\Git\\Agentic-Workflow",
      "disabled": true,
      "_deprecated": "Use adg_sqlite instead"
    }
  }
}
```

**Important**: Set `adg_redis.disabled: true` to prevent conflicts.

### Step 2: Restart Windsurf

1. Close Windsurf completely
2. Reopen Windsurf
3. Verify in MCP settings that `adg_sqlite` is enabled and `adg_redis` is disabled

### Step 3: Verify Installation

Run the health check:
```bash
# The adg_health tool is available via Windsurf MCP
# It returns mode, sqlite status, redis status, cache capability
```

Expected response:
```json
{
  "status": "ok",
  "data": {
    "mode": "full",
    "sqlite": "healthy",
    "redis": "healthy",
    "cache_hit_capable": true,
    "schema_version": "1.0",
    "adg_snapshot_id": "04022026_2140"
  }
}
```

## Tool Compatibility

### Available Tools

| Tool | Status | Notes |
|------|--------|-------|
| `adg_health()` | ✅ New | Primary health check |
| `adg_status()` | ✅ Preserved | ADG snapshot metadata |
| `adg_node(id)` | ✅ Preserved | Now with read-through cache |
| `adg_nodes_by_layer(layer)` | ✅ Preserved | SQLite-only |
| `adg_nodes_by_file(path)` | ✅ Preserved | SQLite-only |
| `adg_edge_fanout(src, rel)` | ✅ Preserved | Now with read-through cache |
| `adg_edge_fanin(tgt, rel)` | ✅ Preserved | SQLite-only |
| `adg_violations(limit)` | ✅ New | Anti-pattern violations |

### Removed Tools

The following Redis-specific tools have been removed:
- `adg_assert_fresh()` → Use `adg_health()` instead
- `adg_snapshot()` → Use `adg_status()` instead
- `adg_meta()` → Use `adg_health()` instead
- `redis_get()` → Use direct Redis CLI or `adg_direct.py`
- `redis_hgetall()` → Use direct Redis CLI or `adg_direct.py`
- `redis_smembers()` → Use direct Redis CLI or `adg_direct.py`
- `redis_lrange()` → Use direct Redis CLI or `adg_direct.py`
- `redis_type()` → Use direct Redis CLI or `adg_direct.py`
- `redis_ttl()` → Use direct Redis CLI or `adg_direct.py`
- `redis_scan()` → Use direct Redis CLI or `adg_direct.py`

## Response Changes

### Unified Response Shape

All responses now include `backend_used` field:
```json
{
  "status": "ok",
  "data": { ... },
  "backend_used": "redis"  // or "sqlite"
}
```

### Error Responses

Errors now include the backend that failed:
```json
{
  "status": "error",
  "message": "Node not found",
  "backend_used": "sqlite"
}
```

## Rollback Procedure

If issues arise:

1. **Disable new server**:
   ```json
   "adg_sqlite": { "disabled": true }
   ```

2. **Re-enable old server**:
   ```json
   "adg_redis": { "disabled": false }
   ```

3. **Restart Windsurf**

4. **Investigate logs**:
   Check stderr output in Windsurf logs for server errors

## Architecture Differences

### Old Architecture (adg_redis)
```
MCP Tool → Redis → SQLite (fallback)
```
Problems:
- Redis treated as authority
- Cache poisoning possible
- Startup fails if Redis down
- Stale cache returns wrong data

### New Architecture (adg_sqlite)
```
MCP Tool → ADGService → SQLite (canonical)
                     ↓
                     Redis (optional cache)
```
Benefits:
- SQLite is always authoritative
- Redis is read-through only
- Startup works with Redis down
- 75ms timeout prevents blocking

## Performance Notes

| Operation | With Redis | Without Redis | Difference |
|-----------|------------|---------------|------------|
| Node lookup (cached) | <10ms | ~50ms | 5x faster |
| Node lookup (miss) | ~60ms | ~50ms | Similar |
| Edge fanout (cached) | <20ms | ~100ms | 5x faster |
| Edge fanout (miss) | ~110ms | ~100ms | Similar |

## Verification Checklist

- [ ] MCP config updated with `adg_sqlite` enabled
- [ ] MCP config updated with `adg_redis` disabled
- [ ] Windsurf restarted
- [ ] `adg_health()` tool responds correctly
- [ ] `adg_status()` returns correct ADG snapshot
- [ ] Node queries work (cached and uncached)
- [ ] Edge queries work (cached and uncached)
- [ ] Server works when Redis down (degraded mode)
- [ ] All existing ADG-based workflows function

## Troubleshooting

### Issue: Server won't start

**Check**: SQLite file exists
```bash
ls artifacts/adg/adg_indexed_*.sqlite
```

**Fix**: Regenerate ADG if missing:
```bash
python tools/adg/generate_full_adg.py
```

### Issue: Redis not connecting

**Check**: Redis URL in environment
```bash
echo $ADG_REDIS_URL
```

**Fix**: Server works without Redis (sqlite_only mode)

### Issue: Slow queries

**Check**: Cache hit rate in health response
```json
{
  "cache_hit_capable": true  // Should be true for caching
}
```

**Fix**: Redis may be down or cache cold. Server falls back to SQLite.

## Support

For issues:
1. Check server logs (stderr output)
2. Run health check: `adg_health()`
3. Verify ADG SQLite exists
4. Check Redis connectivity if needed
5. Rollback to `adg_redis` if critical
