# Semantic Cache (D2) — Production Observability Guide

## 1. Metric Inventory

All semantic-cache events are recorded to the custom `AGENTIC_REGISTRY`
(not the default Prometheus registry) via `record_semantic_cache_event()`.

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `agentic_workflow_l4_semantic_cache_events_total` | Counter | `event`, `namespace` | All cache lifecycle events |

**`event` label values:**

| Value | When emitted | Code location |
|-------|-------------|---------------|
| `hit` | L1 (Redis) or L2 (ChromaDB) match returned | `semantic_cache_manager.recall()` |
| `miss` | No L1 or L2 match | `semantic_cache_manager.recall()` |
| `bypass` | `replay_mode=True` or `flow_class` in `MUST_BYPASS_FLOWS` | `semantic_cache_manager.recall()` |
| `eviction` | TTL-expired entry evicted from L2 | `gptcache_client.get()` / `_hard_evict_entry()` |
| `invalidation` | Explicit `invalidate_cache()` call | `semantic_cache_manager.invalidate_cache()` |

**`namespace` label:** agent class name, or `""` for scope-less events (e.g. eviction).

### Code path

```
SemanticCacheManager.recall()
  └─ _record_semantic_cache_prom_event(event, namespace)   [lifecycle_trace_contract.py]
       └─ record_semantic_cache_event(event, namespace)    [prometheus_metrics.py:213]
            └─ SEMANTIC_CACHE_EVENTS_TOTAL.labels(...).inc()
```

### Scrape setup

`AGENTIC_REGISTRY` is a **custom** `CollectorRegistry` — it is NOT the default Prometheus
registry and will not appear in a default scrape.  To expose it:

```python
from prometheus_client import generate_latest, make_wsgi_app
from agentic_core.L6_observability.utils.metrics.prometheus_metrics import AGENTIC_REGISTRY

# Option A — standalone HTTP server (development / sidecar)
from prometheus_client import start_http_server
start_http_server(port=8000, registry=AGENTIC_REGISTRY)

# Option B — WSGI endpoint (integrate with existing app)
metrics_app = make_wsgi_app(registry=AGENTIC_REGISTRY)
# Mount at /metrics in your WSGI router
```

Prometheus `scrape_configs` target: `host:8000/metrics`.

---

## 2. Production Dashboard Signals

### Panel 1 — Hit Rate (%) by namespace

```promql
100 * sum by (namespace) (
  rate(agentic_workflow_l4_semantic_cache_events_total{event="hit"}[5m])
) /
sum by (namespace) (
  rate(agentic_workflow_l4_semantic_cache_events_total[5m])
)
```

**Healthy target:** ≥ 40 % after warm-up (24 h).

### Panel 2 — Bypass Rate (%) by namespace

```promql
100 * sum by (namespace) (
  rate(agentic_workflow_l4_semantic_cache_events_total{event="bypass"}[5m])
) /
sum by (namespace) (
  rate(agentic_workflow_l4_semantic_cache_events_total[5m])
)
```

**Expected:** low (< 10 %) for normal flows; spikes indicate HITL or action-flow traffic.

### Panel 3 — Eviction Rate (events/min)

```promql
60 * rate(agentic_workflow_l4_semantic_cache_events_total{event="eviction"}[5m])
```

**Healthy target:** < 5 / min in steady state.

### Panel 4 — Invalidation Rate (events/min)

```promql
60 * rate(agentic_workflow_l4_semantic_cache_events_total{event="invalidation"}[5m])
```

**Expected:** near-zero; spikes indicate corpus refresh or operator action.

### Panel 5 — Miss Spike (15 min window)

```promql
increase(agentic_workflow_l4_semantic_cache_events_total{event="miss"}[15m])
```

**Alert threshold:** > 200 misses / 15 min with hit rate < 20 %.

### Panel 6 — Total Traffic (events/min)

```promql
60 * sum(rate(agentic_workflow_l4_semantic_cache_events_total[5m]))
```

**Dead-metric condition:** < 0.1 / min for > 15 min while `SEMANTIC_CACHE_D2_ENABLED=1`.

---

## 3. Alert Rules

See companion file: `docs/monitoring/prometheus_rules_semantic_cache.yaml`

| Alert name | Condition | Severity |
|-----------|-----------|---------|
| `SemanticCacheMissRateAnomaly` | miss > 80 % of traffic for 5 min | warning |
| `SemanticCacheBypassRateAnomaly` | bypass > 50 % of traffic for 10 min | warning |
| `SemanticCacheEvictionSpike` | eviction rate > 10 / min for 5 min | warning |
| `SemanticCacheInvalidationSpike` | > 50 invalidations in 5 min | warning |
| `SemanticCacheNoTraffic` | total events = 0 for 15 min (when D2 enabled) | critical |

---

## 4. Runbook

### Alert: `SemanticCacheMissRateAnomaly`

**Likely causes:**
- Cold cache after store wipe (expected on first deploy; resolves within 24 h)
- Corpus version rotated without pre-warming
- `tenant_id` or `embedding_model_id` mismatch preventing hits

**Actions:**
1. Check `namespace` label — which agent namespace is missing?
2. Verify store is non-empty:
   ```bash
   python -c "import sqlite3; c=sqlite3.connect('artifacts/gptcache/l2_cache.db'); print(c.execute('SELECT COUNT(*) FROM l2_cache').fetchone())"
   ```
3. Check embedding model: `echo $EMBEDDING_MODEL_ID`
4. If cold after deploy, monitor for 24 h before escalating.

---

### Alert: `SemanticCacheBypassRateAnomaly`

**Likely causes:**
- High proportion of HITL / D4_ACTION traffic (expected — not a fault)
- `flow_class` misconfigured as a `MUST_BYPASS_FLOWS` member

**Actions:**
1. Inspect `namespace` — is the bypassing namespace a production flow or a test namespace?
2. Check `SemanticCacheManager.MUST_BYPASS_FLOWS` for unexpected additions.

---

### Alert: `SemanticCacheEvictionSpike`

**Likely causes:**
- Many entries approaching TTL simultaneously (TTL cliff)
- Aggressive similarity-threshold match causing cache pollution + eviction cycle

**Actions:**
1. Check `l2_cache.db` entry distribution:
   ```bash
   python -c "import sqlite3; c=sqlite3.connect('artifacts/gptcache/l2_cache.db'); print(c.execute('SELECT COUNT(*), MIN(expires_at), MAX(expires_at) FROM l2_cache').fetchone())"
   ```
2. Verify `ttl_seconds` default (86400 s = 24 h).

---

### Alert: `SemanticCacheInvalidationSpike`

**Likely causes:**
- Automated corpus rotation triggering `invalidate_cache(corpus_version=...)`
- Operator error calling `invalidate_cache` with no filter (all-tenant wipe)

**Actions:**
1. Check application logs for `semantic_cache_invalidated` events.
2. Confirm invalidation was intentional (corpus rotation) vs. accidental (no-filter wipe).

---

### Alert: `SemanticCacheNoTraffic`

**Likely causes:**
- `SEMANTIC_CACHE_D2_ENABLED` set to `0` (kill-switch active)
- Scrape target down
- `AGENTIC_REGISTRY` not mounted on metrics endpoint

**Actions:**
1. Confirm flag: `echo $SEMANTIC_CACHE_D2_ENABLED` — should be `1` for non-production.
2. Confirm scrape: `curl http://localhost:8000/metrics | grep semantic_cache`
3. Confirm no Python import error swallowing the registry initialisation.

---

## 5. Kill-Switch Reference

| Action | Command / Config |
|--------|-----------------|
| Disable D2 (kill-switch) | `SEMANTIC_CACHE_D2_ENABLED=0` (restart required) |
| Enable D2 (non-production) | `SEMANTIC_CACHE_D2_ENABLED=1` (restart required) |
| Wipe L2 store | `python _b3_cleanup.py` (see `_b3_cleanup.py` at repo root) |
| Inspect L2 store | `python _b3_inspect.py` |
| Invalidate by tenant | `SemanticCacheManager.get_instance().invalidate_cache(tenant_id="<id>")` |
| Invalidate by corpus | `SemanticCacheManager.get_instance().invalidate_cache(corpus_version="<sha256>")` |
