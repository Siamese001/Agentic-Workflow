# D2 Semantic Cache — One-Hour Anomaly Gate Playbook
# Prompt 16 output

> Gate: PG-18 — "No SemanticCacheMissRateAnomaly alert after 1 h canary"
> Precondition: Canary worker running with SEMANTIC_CACHE_D2_ENABLED=1 (see soak sheet).

---

## Metric and alert source of truth

**Metric**: `agentic_workflow_l4_semantic_cache_events_total{event, namespace}`
**Registry**: `AGENTIC_REGISTRY` (custom — NOT the default Prometheus registry)
**Scrape target**: `http://localhost:8000/metrics` (sidecar on port 8000)
**Alert file**: `docs/monitoring/prometheus_rules_semantic_cache.yaml`

**`SemanticCacheMissRateAnomaly` rule (verbatim)**:
```yaml
expr: |
  sum(rate(agentic_workflow_l4_semantic_cache_events_total{event="miss"}[5m]))
  /
  sum(rate(agentic_workflow_l4_semantic_cache_events_total[5m]))
  > 0.80
for: 5m
severity: warning
```

**Trigger**: miss rate > 80% of all cache traffic, sustained for 5 consecutive minutes.

---

## Comparison baseline

The canary has no historical baseline yet (first soak run). Use these reference points:

| Reference | Expected miss rate | Source |
|-----------|-------------------|--------|
| Cold start (T=0 to T+120 min) | 90–100% (all misses, store empty) | Observability doc §4 |
| Warm-up phase (T+120 to T+360 min) | Declining — 50–80% | Observability doc §4 |
| Steady state (T+360 min onward) | < 60% miss; ≥ 40% hit | Observability doc Panel 1 target |

---

## What counts as what

### Healthy miss behavior
- Miss rate > 80% during **cold-start window (first 2 h)** — store is empty, all queries miss.
- `SemanticCacheMissRateAnomaly` may fire during this window. **This is not a gate failure.**
- Miss rate declining monotonically as entries are promoted to L2.

### Expected warm-up noise
- Alert firing at T+5 min to T+120 min = **expected noise, not a fault**.
- Occasional alert firing at T+120 to T+180 min while store fills = **borderline; monitor only**.
- Bypass events (`flow_class` in `MUST_BYPASS_FLOWS`) inflate apparent miss rate in low-volume
  periods — `bypass` events are counted in denominator but not as `miss`. This can cause temporary
  metric dips; not a fault.

### True anomaly (gate FAIL conditions)
- `SemanticCacheMissRateAnomaly` **still firing at T+60 min** = gate FAIL if:
  - L2 store is non-empty (verify: `SELECT COUNT(*) FROM l2_cache`), AND
  - `EMBEDDING_MODEL_ID` matches stored entries, AND
  - No corpus rotation occurred since store was populated.
- Alert firing after T+180 min, sustained > 30 min = rollback trigger.
- Any `ERROR semantic_cache_manager` log line in the worker = immediate rollback.
- Eviction rate > 50/min (`SemanticCacheEvictionSpike` severe) = rollback trigger.

---

## One-hour observation procedure

**Start time**: record as T=0 when canary worker logs `Connected to Long-Term Memory`.

| Time | Action | Expected |
|------|--------|---------|
| T=0 | Record Gate A log line | `Connected to Long-Term Memory (Native L2: SQLite+ChromaDB)` |
| T=0 | Verify metric scrape alive | `curl .../metrics | grep semantic_cache_events` → lines returned |
| T=5 | Check total traffic | `60 * sum(rate(...[5m]))` > 0 (not `SemanticCacheNoTraffic`) |
| T=30 | Check miss rate | Likely 90–100%; alert may be firing — **log it, do not act yet** |
| T=60 | Gate checkpoint | `SemanticCacheMissRateAnomaly` state + miss % value (record both) |
| T=60 | Check store size | `SELECT COUNT(*) FROM l2_cache` — should be growing |
| T=60 | **PG-18 check** | See decision table below |
| T=90 | Check hit rate | Should be non-zero if any queries repeat |
| T=120 | Warm-up closes | Miss rate should be declining; alert should be resolving |

### T+60 min decision table

| `SemanticCacheMissRateAnomaly` at T+60 | L2 store rows > 0 | Decision |
|----------------------------------------|-------------------|----------|
| Not firing | Any | **CONTINUE** — gate on track |
| Firing | 0 | **CONTINUE** — cold cache, warm-up still in progress; re-check at T+120 |
| Firing | > 0 and declining miss | **CONTINUE** with caution — warm-up lagging; extend observation to T+120 |
| Firing | > 0 and miss rate stable / rising | **HOLD** — investigate embedding model or corpus mismatch |
| Firing | Any + `ERROR` in log | **ROLLBACK** — execute §4a immediately |

### If HOLD: investigation checklist

```bash
# 1. Verify model match
echo "Active model: $EMBEDDING_MODEL_ID"
python -c "
import sqlite3
c = sqlite3.connect('artifacts/gptcache/l2_cache.db')
print('Stored models:', c.execute('SELECT DISTINCT embedding_model_id FROM l2_cache').fetchall())
"

# 2. Verify tenant_id not causing all misses
python -c "
import sqlite3
c = sqlite3.connect('artifacts/gptcache/l2_cache.db')
print('Tenants:', c.execute('SELECT DISTINCT tenant_id, COUNT(*) FROM l2_cache GROUP BY tenant_id').fetchall())
"

# 3. Verify corpus version
python -c "
import sqlite3
c = sqlite3.connect('artifacts/gptcache/l2_cache.db')
print('Corpus versions:', c.execute('SELECT DISTINCT corpus_version FROM l2_cache').fetchall())
"
```

---

## Runbook wording clarification (narrowest diff)

PG-18 in `d2_semantic_cache_production_rollout.md` currently reads:

> PG-18 | No `SemanticCacheMissRateAnomaly` alert after 1 h canary | Prometheus | Manual

**Ambiguity**: it is unclear whether the alert firing during the first 2 h cold-start warm-up counts
as a failure. The observability doc says "expected during cold-start; investigate if sustained after
warm-up" but does not define when warm-up ends.

**Proposed minimal diff** — append one sentence to the PG-18 row note:

```
PG-18 | No SemanticCacheMissRateAnomaly alert after 1 h canary | Prometheus | Manual
      NOTE: Alert firing during the first 120 min cold-start warm-up is expected and does
      not constitute a gate failure. Gate PASS requires the alert to be resolved and not
      re-firing at T+60 min post-warm-up (i.e., at T+180 min from worker start).
```

See main runbook patch below.
