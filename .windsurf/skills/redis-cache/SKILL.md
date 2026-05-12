---
name: redis-cache
description: Redis cache inspection — health, key scanning, TTL checks, namespace stats, hash/string/list/zset reads, bounded namespace flushing — via the in-house redis MCP server. Invoke when the user asks about Redis cache state, ADG hot-cache status, coordination fabric keys, key expiry, or needs to invalidate a specific cache namespace. Distinguishes Redis MCP (cache state) from adg_sqlite (canonical truth). Redis is the hot projection; SQLite is the source of truth.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
  deprecated: true
  redirect_to: mcp-integration
---

# ⚠️ DEPRECATED — Redirected to mcp-integration §2

> **Consolidated**: This skill content moved to `mcp-integration/SKILL.md` §2 — Redis Cache (2026-05-12, W4.P2).
> **Status**: Redirect stub — preserved for backwards compatibility.
> **Action**: Consult `.windsurf/skills/mcp-integration/SKILL.md` §2 for current guidance.

---
| User intent | Use redis MCP? |
|---|---|
| Check ADG hot cache status (warm/cold) | ✅ Yes |
| Inspect coordination-fabric keys | ✅ Yes |
| Verify TTL on a key | ✅ Yes |
| Bounded namespace invalidation | ✅ Yes |
| Read a specific cached value | ✅ Yes |
| Modify cache contents | ❌ No — Redis is read-only-from-Cascade; mutations happen via `tools/adg/adg_redis_ingest.py` |
| Persistent agent memory | ❌ No | `memory` MCP |

## Tool Routing

| Goal | Tool |
|---|---|
| Health probe | `redis_health` |
| Server INFO | `redis_stats` |
| DB key count | `redis_dbsize` |
| Scan keys by pattern (uses SCAN, not KEYS) | `redis_keys` |
| Get a single key (auto-detects type) | `redis_get` |
| Hash fields | `redis_hgetall` |
| TTL remaining | `redis_ttl` |
| Top-N namespace stats | `redis_namespace_stats` |
| Delete a single key | `redis_del_key` |
| Bulk delete by pattern (defaults dry_run=true) | `redis_flush_namespace` |

## Hard Rules

1. **SQLite is canonical, Redis is hot projection.** When the two disagree, SQLite wins.
2. **`redis_flush_namespace` defaults to `dry_run=true` for safety.** Set `dry_run=false` only when you've inspected the matched keys.
3. **Use `redis_keys` (SCAN), never `KEYS *` patterns.** SCAN is cursor-based and bounded; KEYS blocks the server.
4. **MCP serialization (§25):** One MCP call per response.
5. **MCP green light:** Before T2/T3 work, check Redis hot cache status as the preferred fast path before falling back to `adg_health`.

## Common Workflows

**MCP green light check:**
1. `python tools/adg/adg_redis_ingest.py --check` from `run_command` (preferred)
2. Fallback: `redis_keys(pattern='adg:node:*', limit=1)` → if any key, hot cache is warm

**Invalidate a namespace:**
1. `redis_keys(pattern='coord:agent:*', limit=200)` → preview
2. `redis_flush_namespace(pattern='coord:agent:*', dry_run=true)` → confirm match list
3. `redis_flush_namespace(pattern='coord:agent:*', dry_run=false)` → execute

**Inspect ADG node cache entry:**
1. `redis_hgetall(key='adg:node:<id>')`
