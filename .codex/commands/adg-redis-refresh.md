---
description: Regenerate ADG and reload Redis hot cache - run after any code refactoring or structural change
---

> **Claude Code workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

# ADG Redis Refresh Workflow

Invoke with `/adg-redis-refresh`. Runs after any refactor, import change, or structural code edit to keep the ADG Redis hot cache current.

---

## STEP 0: Verify Redis server is running (100% availability gate)

**MANDATORY FIRST STEP** - Ensures Redis is available before any cache operations.

// turbo
```powershell
python tools/adg/adg_redis_ingest.py --check
```

**Exit codes:**
- `0` → Redis running + latest ADG cache HOT → continue to STEP 1 for staleness verification
- `1` → Redis unavailable or latest ADG cache COLD → continue to STEP 3 if SQLite is current; otherwise STEP 2

If Redis is down, start Redis manually and verify `redis-cli ping` returns `PONG`.

---

## STEP 1: Check Redis cache staleness

**Use the canonical staleness guard (Accelerator #2) — never inline Redis queries:**

// turbo
```powershell
python tools/adg/adg_stale_guard.py --json
```

Interpret output:
- `"is_stale": false` → cache is FRESH → **SKIP to STEP 5**
- `"is_stale": true` → cache is STALE → continue to STEP 2; `changed_files` lists what changed
- Exit 1 (Redis unavailable) → start Redis first, then retry

To list exactly which files changed since last ingest:
```powershell
python tools/adg/adg_stale_guard.py --files
```

---

## STEP 2: Regenerate ADG from source

**Only run if code has changed since last ADG generation.**
This is an expensive full AST scan (~2-5 min). Do not skip if code changed.

```powershell
python tools/generate/generate_full_adg.py
```

Wait for completion. Verify new `.sqlite` and `_snapshot_*.json` files appear in `artifacts/adg/`.

**Expected-wiring gate runs automatically at the end of this step.** The ADG generator
invokes `ops_scripts/ci/check_expected_wiring.py` after artifacts verify, so any
violation of the declared call-site assertions in `config/expected_wiring.yaml`
surfaces here — not hours later at pre-commit or CI. The process exits non-zero
on violation. Emergency opt-out: `python tools/generate/generate_full_adg.py --no-wiring-check`.

---

## STEP 3: Load refreshed ADG into Redis

// turbo
```powershell
python tools/adg/adg_redis_ingest.py --force
```

Expected output:
```text
[adg_redis_ingest] Snapshot : MMDDYYYY_HHMM
[adg_redis_ingest] SQLite   : ...\artifacts\adg\adg_indexed_MMDDYYYY_HHMM.sqlite
[adg_redis_ingest] Nodes written : N
[adg_redis_ingest] Edges written : N
[adg_redis_ingest] Done in Ns - cache is HOT
```

**Verify the timestamp** in `Snapshot : ...` matches the `adg_indexed_<ts>.sqlite` filename — this confirms the ingest used the correct artifact, not a hardcoded stale value.

---

## STEP 4: Verify cache health

**Option A — script (fastest, no MCP restart needed):**

// turbo
```powershell
python tools/adg/adg_redis_ingest.py --check
```

**Gate:** Must see `Cache is HOT` for the latest `adg_indexed_<ts>.sqlite` snapshot before proceeding.

**Option B — current MCP servers (preferred after legacy editor restart picks up the config):**

Use the current `redis` and `adg_sqlite` servers together:

- `redis_health` or `redis_namespace_stats` for Redis liveness and namespace freshness
- `redis_hgetall` / `redis_keys` / `redis_ttl` for low-level cache inspection
- `adg_status` / `adg_health` for authoritative graph readiness and disk-backed status

This repo no longer treats a separate `adg_redis` server as the MCP authority.  
The cache surface is `redis`; the structural graph authority remains `adg_sqlite`.

## STEP 5: Confirm ADG is driving queries

From this point all analysis queries use Redis Tier-1 lookups via `tools/adg/adg_redis_query.py`.

**Accelerator #3 — Use `search-nodes` with layer and entity_type filters (never raw Redis inline):**
```powershell
# Find all agents in L3:
python tools/adg/adg_redis_query.py search-nodes Agent --layer L3

# Find class nodes only:
python tools/adg/adg_redis_query.py search-nodes Orchestrator --entity-type class

# Combined filter:
python tools/adg/adg_redis_query.py search-nodes Checker --layer L5 --entity-type class
```

Use `tools/adg/adg_redis_query.py` for quick cache-backed node and edge lookups. Use MCP `adg_sqlite`
or direct SQLite fallback for JOIN/CTE queries that are not expressible as Redis node/edge lookups.

Raw Redis key reference:
- `adg:v1:<snapshot_id>:node:<id>` — node details by integer ID
- `adg:v1:<snapshot_id>:edge:<src_id>:<relation_type>` — fan-out edge IDs
- `adg:v1:<snapshot_id>:fanin:<dst_id>:<relation_type>` — fan-in edge IDs
- `adg:v1:<snapshot_id>:edge_detail:<edge_id>` — edge detail hash
- `adg:v1:<snapshot_id>:_hot` — hot-cache sentinel
- `adg:meta` / `adg:status` / `adg:snapshot` — global metadata for the active snapshot

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

The ingest script (`tools/adg/adg_redis_ingest.py --check`) verifies the hot sentinel for the latest
timestamped SQLite snapshot. Use `tools/adg/adg_stale_guard.py --json` to determine whether source commits
landed after the cached SQLite snapshot's `sqlite_mtime`; re-ingesting an old SQLite file must not be
treated as a fresh full-ADG regeneration.

---

## References

- Ingest script: `tools/adg/adg_redis_ingest.py`
- Query helper: `tools/adg/adg_redis_query.py` (Accelerator #3: `search-nodes --layer --entity-type`)
- Staleness guard: `tools/adg/adg_stale_guard.py` (Accelerator #2)
- Anti-pattern fixer: `tools/adg/adg_antipattern_fixer.py` (Accelerator #1)
- ADG artifacts: `artifacts/adg/`
- ADG regeneration: `tools/generate/generate_full_adg.py`
- Memory: ADG Pre-Ingest Rule (MEMORY[1c4e46e0])
