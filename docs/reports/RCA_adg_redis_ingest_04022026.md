# ADG Redis Ingest Performance RCA

## Hardened Architectural Analysis

### Frame: Hot Cache vs Authoritative Ledger

In this system's architecture, the **Redis hot cache is explicitly NON-AUTHORITATIVE**. The Unified Write Gateway (UWG) and L4 State Plane own:
- Authoritative writes
- Durable state persistence  
- Integrity guarantees
- Version-aware lineage

The Redis hot cache is a **speed layer**—ephemeral, non-durable, and explicitly designed for fast retrieval ahead of deeper storage. **Its primary metric is utility (freshness and speed), not correctness.**

### Root Cause: Infrastructure Debt + API Incompatibility

| Factor | Finding |
|--------|---------|
| **Redis Server** | 3.0.504 (released 2016, 9 years old) |
| **Missing Feature** | Variadic `HSET` (added Redis 4.0, 2017) |
| **Client Capability** | `hset(mapping=dict)` available but server rejects |
| **Fallback Path** | Per-field `hset(key, field, value)` in loop |
| **Command Explosion** | 1 entity × 10 fields = 10 commands (was 1) |
| **Result** | 43s → 123s ingest (2.9× regression) |

The performance regression was caused by **treating infrastructure debt as a compatibility target** rather than upgrading the platform.

### Impact: Cache Utility Degradation

The retrieval pipeline explicitly tracks:
- **Stale-hit rate** (reads against outdated cache)
- **Retrieval drift** after ADG rebuilds/version changes
- **Freshness policy violations**

Slower ingest directly increases:
- Window of stale cache availability
- Stale-hit rate post-reindex
- Retrieval quality degradation after scanner updates

**This is not a "developer convenience" issue—it is a retrieval system quality failure.**

---

## Blast-Radius Table: Option B (Packed JSON)

| Component | Current Pattern | Required Change | Impact |
|-----------|----------------|-----------------|--------|
| `adg_mcp_server.py` | `r.hgetall(f"adg:node:{id}")` | `json.loads(r.get(...))` | Medium—single decode per read |
| `adg_node` MCP tool | Field-level hash access | Add decode helper in response layer | Low—encapsulated change |
| `adg_edge_detail` MCP tool | Field-level hash access | Add decode helper in response layer | Low—encapsulated change |
| Cache consumers | Direct hash field access | Blob + client-side field extraction | Medium—all readers change |
| **MCP Latency** | O(1) per field | O(1) whole-blob + ~0.1-0.5ms JSON parse | Acceptable for warm path |

### Selective Field Lookup Tradeoff

| Aspect | Hash-per-Entity | Packed JSON |
|--------|-----------------|-------------|
| Wire round-trips | 1 per entity | 1 per entity (same) |
| Payload efficiency | Lower (Redis hash overhead) | Higher (raw bytes) |
| Selective projection | Native (Redis filters unused fields) | Client-side only |
| Partial update | Per-field | Full-blob rewrite |

### Acceptability for Non-Authoritative Hot Cache

**ACCEPTABLE.** For a non-authoritative hot cache, packed representation is architecturally valid because:
- No durability requirements
- No transactional integrity requirements
- Can be invalidated and rebuilt from authoritative source
- Read-path simplicity is acceptable tradeoff for ingest speed

**CAVEAT:** MCP tools must add consistent decode helpers to avoid scattered JSON parsing logic.

---

## Recommendation

### Tactical: Option A (Now)

**Implement `hmset` with explicit deprecation warning suppression.**

`tools/adg/adg_redis_ingest.py` now includes:
```python
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*hmset.*")
```

**Rationale:** Minimal blast radius, preserves all reader contracts, restores near-baseline ingest speed (~49s vs broken ~123s), unblocks retrieval stack immediately.

### Strategic: Platform Debt Acknowledgment

**Redis 3.0.504 is infrastructure debt.** It blocks modern API adoption, forces workaround code, and creates false compatibility constraints. **Do not treat it as an acceptable steady state.**

### Long-term: Decision Required (90-day horizon)

| Path | Trigger | Effort | Outcome |
|------|---------|--------|---------|
| **Option B: Packed JSON** | Ingest consistently >60s | Medium (reader changes) | ~21s ingest, 2.3× faster |
| **Option C: Redis Upgrade** | Infrastructure refresh | High (coordination) | Unblocks modern API, enables proper `hset(mapping=...)` |

**Decision criteria:**
- If retrieval freshness SLA pressure increases → Option B
- If infrastructure modernization cycle arrives → Option C
- **Do nothing is not acceptable**—Redis 3.0.504 debt must be resolved

---

## Final Decision

**APPROVED:** Option A (`hmset` + warning suppression) as immediate tactical fix.

**MANDATED:** Document Redis 3.0.504 as platform debt requiring resolution within 90 days.

**DIRECTED:** Architecture team to produce decision memo comparing Option B vs Option C with cost/benefit analysis for next infrastructure cycle.

---

## Implementation Evidence

**File Modified:** `tools/adg/adg_redis_ingest.py`

**Changes:**
1. Added connection pooling (20 max connections, keepalive)
2. Added deprecation warning suppression for `hmset`
3. Restored single-command-per-entity write pattern

**Benchmark Results:**
| Configuration | Ingest Time |
|-------------|-------------|
| Original (hmset with warnings) | ~43s |
| Broken (per-field hset) | ~123s |
| **Fixed (hmset + suppression)** | **~49s** |

**Status:** ✅ Implemented and verified
