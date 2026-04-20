---
description: Regenerate ADG and reload Redis hot cache - run after any code refactoring or structural change
---

> **Claude workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

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

**Use the canonical staleness guard (Accelerator #2) — never inline Redis queries:**

// turbo
```
python tools/adg/adg_stale_guard.py --json
```

Interpret output:
- `"is_stale": false` → cache is FRESH → **SKIP to STEP 5**
- `"is_stale": true` → cache is STALE → continue to STEP 2; `changed_files` lists what changed
- Exit 1 (Redis unavailable) → start Redis first, then retry

To list exactly which files changed since last ingest:
```
python tools/adg/adg_stale_guard.py --files
```

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
[redis] adg:status sentinel written (timestamp=MMDDYYYY_HHMM)
[done] ADG -> Redis ingest complete
```

**Verify the timestamp** in `adg:status sentinel written (timestamp=...)` matches the `adg_indexed_<ts>.sqlite` filename — this confirms the ingest used the correct (fresh) artifact, not a hardcoded stale value.

---

## STEP 4: Verify cache health

**Option A — script (fastest, no MCP restart needed):**

// turbo
```
python tools/adg/redis_health_check.py --verbose
```

**Gate:** Must see `cache HOT` with `node_count` >= 8000 before proceeding.

**Option B — current MCP servers (preferred after Windsurf restart picks up the config):**

Use the current `redis` and `adg_sqlite` servers together:

- `redis_health` or `redis_namespace_stats` for Redis liveness and namespace freshness
- `redis_hgetall` / `redis_keys` / `redis_ttl` for low-level cache inspection
- `adg_status` / `adg_health` for authoritative graph readiness and disk-backed status

This repo no longer treats a separate `adg_redis` server as the MCP authority.  
The cache surface is `redis`; the structural graph authority remains `adg_sqlite`.

## STEP 5: Confirm ADG is driving queries

From this point all analysis queries use Redis Tier-1 lookups via `tools/adg/adg_redis_query.py`.

**Accelerator #3 — Use `search-nodes` with layer and entity_type filters (never raw Redis inline):**
```
# Find all agents in L3:
python tools/adg/adg_redis_query.py search-nodes --query Agent --layer L3

# Find class nodes only:
python tools/adg/adg_redis_query.py search-nodes --query Orchestrator --entity-type class

# Combined filter:
python tools/adg/adg_redis_query.py search-nodes --query Checker --layer L5 --entity-type class
```

**Accelerator #5 — Use `adg_test_selector.py` to select tests for changed files:**
```
python tools/adg/adg_test_selector.py --from-diff
```

**Accelerator #4 — Use `adg_type_check.py` for incremental type checking:**
```
python tools/adg/adg_type_check.py --from-diff
```

Raw Redis key reference:
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
- Query helper: `tools/adg/adg_redis_query.py` (Accelerator #3: `search-nodes --layer --entity-type`)
- Staleness guard: `tools/adg/adg_stale_guard.py` (Accelerator #2)
- Test selector: `tools/adg/adg_test_selector.py` (Accelerator #5)
- Type checker: `tools/adg/adg_type_check.py` (Accelerator #4)
- Anti-pattern fixer: `tools/adg/adg_antipattern_fixer.py` (Accelerator #1)
- ADG artifacts: `artifacts/adg/`
- ADG regeneration: `tools/generate_full_adg.py`
- Memory: ADG Pre-Ingest Rule (MEMORY[1c4e46e0])
