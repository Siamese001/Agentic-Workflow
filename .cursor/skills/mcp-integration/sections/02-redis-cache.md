## §2 — Redis Cache

**In-house.** Redis is the **hot read-only projection** of the ADG. SQLite is canonical.

### Canonical retrieval ladder

**One line:** Redis warm projection → **`adg_sqlite` MCP** (read-only gateway) → SQLite direct only with **`DEGRADED_FALLBACK: reason=<…>`** unless matching a **named CI parity script**.

**Doctrine (verbatim):** SQLite is canonical truth. Redis is a hot projection/read-through optimization, never authority. MCP is the preferred read-only gateway for agents. Direct sqlite3 or SQLiteBackend access in plans requires either a named CI parity script or an explicit DEGRADED_FALLBACK reason. Warm Redis hits may serve MCP responses only when provenance is visible through backend_used and, where required, rows hydrate or validate against canonical SQLite. Cold, missing, error, empty, or divergent Redis falls back to SQLite. Agents must not silently default to raw sqlite3 for refactor or analysis work.

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
1. **SQLite is canonical, Redis is hot projection** — same ladder as **`adg-sqlite`** / **`graph-analysis`**: Redis warm → MCP → SQLite direct only with **`DEGRADED_FALLBACK`** unless CI parity script.
2. **`redis_flush_namespace` defaults to `dry_run=true`**
3. **Use `redis_keys` (SCAN), never `KEYS *`**
4. **MCP green light** — check Redis before T2/T3 work (Redis remains optional; SQLite remains authoritative on cold/divergence).

---
