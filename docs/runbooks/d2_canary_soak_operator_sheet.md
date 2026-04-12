# D2 Semantic Cache — Canary Soak Operator Sheet
# Prompt 15 output

> Pre-conditions: pre-flight gate passed, manual canary passed, system returned to fail-closed.
> This sheet governs the 24 h persistent-worker soak gate (PG-18).

---

## Exact Launch Sequence

### Terminal 1 — Metrics sidecar (start first)

```bash
python ops_scripts/dev_tools/start_metrics_sidecar.py
```

Expected startup line:
```
Metrics sidecar listening on :8000/metrics  (AGENTIC_REGISTRY)
```

Verify scrape endpoint is alive before starting the worker:
```bash
curl -s http://localhost:8000/metrics | grep agentic_workflow
```
Expected: several `agentic_workflow_*` metric lines (counters at 0).

### Terminal 2 — Canary worker

Pick **one** non-production worker. `apps_lic` is recommended (richer flow mix):

```bash
SEMANTIC_CACHE_D2_ENABLED=1 \
HIVE_MIND_STRICT_MODE=false \
EMBEDDING_MODEL_ID=bge-m3-v1 \
python -m apps_lic
```

Or for the RG worker:

```bash
SEMANTIC_CACHE_D2_ENABLED=1 \
HIVE_MIND_STRICT_MODE=false \
EMBEDDING_MODEL_ID=bge-m3-v1 \
python -m apps_rg
```

### Required env vars

| Var | Required value | Purpose |
|-----|---------------|---------|
| `SEMANTIC_CACHE_D2_ENABLED` | `1` | Enables Gate A (L2 init) and Gate B (recall hot path) |
| `HIVE_MIND_STRICT_MODE` | `false` | Degrades gracefully on infra failure instead of crashing the canary worker |
| `EMBEDDING_MODEL_ID` | `bge-m3-v1` | Must match entries already in L2 store; mismatch causes all misses |

Optional (set to override defaults):

| Var | Default | Notes |
|-----|---------|-------|
| `REDIS_URL` | `redis://localhost:6379` | L1 working-memory backend |
| `HIVE_MIND_TRACE_SAMPLING_RATE` | `1.0` | Reduce to `0.1` for high-volume canary to limit trace overhead |

### Gate A verification (on worker startup)

Grep the worker log immediately after start:

```bash
grep "Native L2 cache" <worker_log>
```

Expected:
```
[HiveMind] Connected to Long-Term Memory (Native L2: SQLite+ChromaDB)
```

If you see `Native L2 cache disabled` → `SEMANTIC_CACHE_D2_ENABLED` was not exported. Stop and fix.

---

## Flag persistence for full 24 h soak

The flag is read at `SemanticCacheManager._init_gptcache()` during worker startup.
**It is not re-read at runtime.** Once the worker starts with `SEMANTIC_CACHE_D2_ENABLED=1`
and logs `Connected to Long-Term Memory`, Gate A stays open for the lifetime of that process.

Proof: `_init_gptcache()` calls `os.environ.get("SEMANTIC_CACHE_D2_ENABLED", "0")` exactly once
at init time. No polling. No dynamic re-evaluation.

Risk: Worker restart (crash, OOM, OS reboot) without the env var will revert to fail-closed.
Mitigation: Store the env block in a `.env.canary` file and source it in the restart script:

```bash
# .env.canary (non-production only — never commit)
SEMANTIC_CACHE_D2_ENABLED=1
HIVE_MIND_STRICT_MODE=false
EMBEDDING_MODEL_ID=bge-m3-v1
```

```bash
# Restart after crash:
set -a && source .env.canary && set +a && python -m apps_lic
```

---

## Soak monitoring checklist (check every 2 h)

| # | Check | Command | Healthy |
|---|-------|---------|---------|
| M-1 | Worker process alive | `ps aux | grep apps_lic` | Process present |
| M-2 | Metrics sidecar alive | `curl -s http://localhost:8000/metrics | grep semantic_cache_events` | Lines returned |
| M-3 | Miss rate < 80 % after first 2 h | PromQL: see §Queries below | `SemanticCacheMissRateAnomaly` not firing |
| M-4 | Hit rate climbing | PromQL: see §Queries below | Trending upward after hour 2 |
| M-5 | No unhandled exceptions | `grep ERROR <worker_log> | grep semantic_cache` | No lines |
| M-6 | Eviction rate normal | `SemanticCacheEvictionSpike` not firing | < 10/min |
| M-7 | No `SemanticCacheNoTraffic` alert | Total events/min > 0 | Metric active |

### Prometheus queries for soak dashboard

Miss rate (last 5 min):
```promql
100 * sum(rate(agentic_workflow_l4_semantic_cache_events_total{event="miss"}[5m]))
     / sum(rate(agentic_workflow_l4_semantic_cache_events_total[5m]))
```

Hit rate by namespace (last 5 min):
```promql
100 * sum by (namespace) (rate(agentic_workflow_l4_semantic_cache_events_total{event="hit"}[5m]))
     / sum by (namespace) (rate(agentic_workflow_l4_semantic_cache_events_total[5m]))
```

Total traffic (events/min):
```promql
60 * sum(rate(agentic_workflow_l4_semantic_cache_events_total[5m]))
```

---

## 24 h soak pass / fail criteria

| Criteria | PASS | FAIL → action |
|----------|------|--------------|
| `SemanticCacheMissRateAnomaly` state after cold-start warm-up (hour 2+) | Alert **not firing** | Alert firing → execute rollback §4a |
| Hit rate after 24 h | ≥ 40 % (per `docs/monitoring/semantic_cache_observability.md` Panel 1 target) | < 20 % after 24 h → investigate corpus/model mismatch |
| Unhandled exceptions in D2 path | Zero `ERROR semantic_cache_manager` log lines | Any → rollback immediately |
| Worker process continuity | Worker still running at T+24h | Crash → fix restart, restart clock |
| Gate A log line present | `Connected to Long-Term Memory` in startup log | Absent → flag was not set, soak does not count |

**Cold-start warm-up window:** The first 2 h are expected to show miss-dominant traffic as the
L2 store fills. `SemanticCacheMissRateAnomaly` firing during this window is **not a FAIL**
condition — see PG-18 clarification in `d2_semantic_cache_production_rollout.md`.

---

## Stop / resume procedure

Stop (at end of soak or on alert):
```bash
# Terminal 2: Ctrl-C or kill apps_lic process
# Terminal 1: Ctrl-C sidecar (or SIGTERM)
# Return to fail-closed:
unset SEMANTIC_CACHE_D2_ENABLED
```

Resume after interruption:
```bash
# Verify store still has entries:
python -c "import sqlite3; c=sqlite3.connect('artifacts/gptcache/l2_cache.db'); print('rows:', c.execute('SELECT COUNT(*) FROM l2_cache').fetchone())"
# Restart with same env block — soak clock must be restarted from 0 if worker was down > 5 min
set -a && source .env.canary && set +a && python -m apps_lic
```
