# D2 Semantic Cache — Production Rollout Package

> Status: **GO READY** for non-production. Production rollout requires this package.
> Last validation: post-B1/B2/B3 acceptance (AT-1 through AT-10 pass).

---

## 0. Pre-flight Gate Checklist (run before any environment activation)

| # | Gate | Command / Verification | Expected |
|---|------|----------------------|---------|
| G-1 | SQLite store is empty or schema-clean | `python _b3_inspect.py` | `l2_cache` has 0 rows |
| G-2 | ChromaDB collection exists clean | `python _b3_inspect.py` | `l2_semantic_cache` exists, 0 embeddings |
| G-3 | Redis is reachable | `python -c "import redis; r=redis.Redis(); r.ping()"` | No exception |
| G-4 | ChromaDB package installed | `python -c "import chromadb"` | No ImportError |
| G-5 | AT-1 through AT-10 pass | `python -m pytest tests/unit/agentic_core/L4_state/cache/test_semantic_cache_acceptance.py -v --override-ini="addopts="` | 10/10 PASS |
| G-6 | Caller-consistency tests pass | `python -m pytest tests/unit/agentic_core/L4_state/cache/test_caller_consistency.py -v --override-ini="addopts="` | 6/6 PASS |
| G-7 | Feature-flag tests pass | `python -m pytest tests/unit/agentic_core/L4_state/cache/test_d2_feature_flag.py -v --override-ini="addopts="` | 7/7 PASS |
| G-8 | Flag is **off** in target environment | `echo $SEMANTIC_CACHE_D2_ENABLED` | `0` or empty |
| G-9 | Metrics scrape endpoint reachable | `curl http://localhost:8000/metrics 2>/dev/null | grep agentic_workflow` | Lines returned |
| G-10 | No legacy `gptcache_enabled=True` path active | `python -c "from agentic_core.L4_state.utils.memory.semantic_cache_manager import SemanticCacheManager; s=SemanticCacheManager.get_instance(); print(s.gptcache_enabled)"` | `False` (before enable) |

All gates must be **PASS** before proceeding.

---

## 1. Store Migration Steps

### 1a. Preflight wipe (first activation only)

Run only if the store was used in a non-D2-compliant state (B0/Phase A entries without
tenant metadata).

```bash
# Inspect first
python _b3_inspect.py

# If stale entries exist:
python _b3_cleanup.py
```

`_b3_cleanup.py` does:
1. Deletes all rows from `artifacts/gptcache/l2_cache.db` → `l2_cache` table.
2. Drops and recreates `l2_semantic_cache` collection in ChromaDB.

**Do NOT run on a store that already has production Phase B entries.**

### 1b. Redis pre-wipe (optional, belt-and-suspenders)

```bash
# Inspect existing Redis L1 keys
redis-cli --scan --pattern "hive:*" | head -20

# Wipe only semantic-cache L1 keys (prefix is hive: or sc: depending on namespace)
# Use the MCP Redis tool for targeted deletion rather than FLUSHDB
```

---

## 2. Canary Enablement

### Step 1 — Enable on a single non-production worker

```bash
SEMANTIC_CACHE_D2_ENABLED=1 python -m <your_worker_entrypoint>
```

Or set in the environment manifest (non-production only):

```yaml
# Non-production environment config
env:
  SEMANTIC_CACHE_D2_ENABLED: "1"
  EMBEDDING_MODEL_ID: "bge-m3-v1"     # must match store entries
  HIVE_MIND_STRICT_MODE: "false"       # degraded-mode for canary safety
```

### Step 2 — Verify gate A fires

```bash
grep "Native L2 cache initialized" <app_log>
```

Expected log line: `[HiveMind] Connected to Long-Term Memory (Native L2: SQLite+ChromaDB)`.

### Step 3 — Send a single Path D request

```python
from agentic_core.L0_routing.reasoning.execution_orchestrator import ExecutionOrchestrator

orch = ExecutionOrchestrator()
result = orch.execute({
    "intent": "test",
    "payload": {"query": "What is the capital of France?"},
    "tenant_id": "canary-tenant",
    "flow_class": "READ_ONLY",
    "namespace": "canary",
})
print(result)  # state should be "d2_cache_miss" on first run
```

### Step 4 — Verify telemetry

```bash
curl http://localhost:8000/metrics | grep semantic_cache
```

Expected counter: `agentic_workflow_l4_semantic_cache_events_total{event="miss",namespace="canary"} 1`

---

## 3. Production Smoke Test

Run after canary is stable (≥ 1 h, no alerts).

### ST-1 — Create an evidence-complete entry

```python
from agentic_core.L4_state.utils.memory.semantic_cache_manager import SemanticCacheManager
import os

os.environ["SEMANTIC_CACHE_D2_ENABLED"] = "1"
scm = SemanticCacheManager.get_instance()

# Promote a grounded entry directly
scm._gptcache.set(
    "What is the capital of France?",
    '{"answer": "Paris", "_metadata": {"namespace": "canary"}}',
    tenant_id="smoke-tenant",
    embedding_model_id="bge-m3-v1",
    corpus_version="a" * 64,          # 64-char SHA-256 placeholder
    evidence_ids=["doc-001"],
    grounding_complete=True,
    ttl_seconds=3600,
)
print("ST-1 PASS: entry written")
```

### ST-2 — Verify D2 hit on allowed flow

```python
result = scm.recall(
    "What is the capital of France?",
    "smoke-ns",
    tenant_id="smoke-tenant",
    flow_class="READ_ONLY",
)
assert result is not None, "ST-2 FAIL: expected D2 hit"
print("ST-2 PASS: hit returned:", result)
```

### ST-3 — Verify bypass on must-bypass flow

```python
result = scm.recall(
    "What is the capital of France?",
    "smoke-ns",
    tenant_id="smoke-tenant",
    flow_class="D4_ACTION",    # MUST_BYPASS_FLOWS member
)
assert result is None, "ST-3 FAIL: expected bypass (None)"
print("ST-3 PASS: bypass confirmed")
```

### ST-4 — Verify telemetry visibility

```bash
curl -s http://localhost:8000/metrics | grep semantic_cache_events_total
```

Expected lines:
```
agentic_workflow_l4_semantic_cache_events_total{event="hit",namespace="smoke-ns"} 1.0
agentic_workflow_l4_semantic_cache_events_total{event="bypass",namespace="smoke-ns"} 1.0
```

### ST-5 — Verify invalidation path

```python
count = scm.invalidate_cache(tenant_id="smoke-tenant")
assert count == 1, f"ST-5 FAIL: expected 1 invalidation, got {count}"
print("ST-5 PASS: invalidation confirmed")
```

---

## 4. Rollback Criteria and Operator Actions

### Automatic rollback triggers

| Condition | Metric / Log | Action |
|-----------|-------------|--------|
| Miss rate > 80 % for > 30 min after warm-up | `SemanticCacheMissRateAnomaly` firing | Execute rollback §4a |
| Any unhandled exception in D2 path | Log: `ERROR semantic_cache_manager` | Execute rollback §4a |
| Eviction rate spike > 50/min | `SemanticCacheEvictionSpike` — severe | Execute rollback §4a |
| Tenant isolation breach (wrong tenant data returned) | AT-2 failure in canary smoke test | Execute rollback §4a immediately |

### 4a — Rollback procedure (< 5 min)

```bash
# Step 1: Disable D2 (no restart needed if env is mutable)
export SEMANTIC_CACHE_D2_ENABLED=0
# OR update environment manifest and restart worker

# Step 2: Verify gate is off
python -c "
import os; os.environ['SEMANTIC_CACHE_D2_ENABLED'] = '0'
from agentic_core.L4_state.utils.memory.semantic_cache_manager import SemanticCacheManager
SemanticCacheManager._instance = None  # force re-init
s = SemanticCacheManager.get_instance()
print('gptcache_enabled:', s.gptcache_enabled)  # must be False
"

# Step 3: Wipe store if integrity was compromised
python _b3_cleanup.py

# Step 4: Confirm metrics go silent
sleep 60 && curl -s http://localhost:8000/metrics | grep semantic_cache_events_total
# Should show no new increments
```

### 4b — Partial rollback (preserve L2 store, disable gate only)

Set `SEMANTIC_CACHE_D2_ENABLED=0` — store is preserved, D2 gate is inactive.  
Re-enable when root cause is resolved.

---

## 5. Production Go-Live Checklist

Derived from non-production AT-1 through AT-10 acceptance gates.

| # | Gate condition | Method | Status |
|---|---------------|--------|--------|
| PG-01 | Contract-complete writes: all Phase B fields present (`tenant_id`, `embedding_model_id`, `corpus_version`, `entry_schema_version`, `expires_at`) | `test_semantic_cache_acceptance.py::test_at01_*` | AT-1 PASS |
| PG-02 | Tenant isolation: cross-tenant reads return None | `test_at02_*` | AT-2 PASS |
| PG-03 | Embedding model isolation: wrong model returns None | `test_at03_*` | AT-3 PASS |
| PG-04 | Hard TTL eviction: expired entry removed, not returned | `test_at04_*` | AT-4 PASS |
| PG-05 | `invalidate_by` clears SQLite + Chroma atomically | `test_at05_*` | AT-5 PASS |
| PG-06 | Replay bypass: `replay_mode=True` returns None | `test_at06_*` | AT-6 PASS |
| PG-07 | Must-bypass flow enforcement (`D4_ACTION`, `HITL`) | `test_at07_*` | AT-7 PASS |
| PG-08 | Evidence-gated promotion: incomplete entry rejected | `test_at08_*` | AT-8 PASS |
| PG-09 | Legacy-store cleanup complete: no pre-Phase-B entries | `_b3_inspect.py` — 0 rows | B3 PASS |
| PG-10 | `build_semantic_cache_d2_key` empty-tenant guard | `test_at09_*` | AT-9 PASS |
| PG-11 | AT-1 through AT-10 exist and pass | Full suite run | 10/10 PASS |
| PG-12 | Telemetry visible on non-production surface | `curl .../metrics` + `test_prom_*` | B2 PASS |
| PG-13 | Every `recall()` call site passes `flow_class` | `test_caller_consistency.py` 6/6 | P1 PASS |
| PG-14 | `SEMANTIC_CACHE_D2_ENABLED` flag gates both Gate A and Gate B | `test_d2_feature_flag.py` 7/7 | P2 PASS |
| PG-15 | Kill-switch disables D2 without code change | `SEMANTIC_CACHE_D2_ENABLED=0` + restart | P2 PASS |
| PG-16 | Observability artifacts present (dashboard spec + alert rules) | `docs/monitoring/` | P3 PASS |
| PG-17 | Canary smoke test ST-1 through ST-5 pass | §3 above | Manual |
| PG-18 | No `SemanticCacheMissRateAnomaly` alert after 1 h canary (see note) | Prometheus | Manual |
| PG-19 | Rollback procedure tested in non-production | §4a above | Manual |

**All 19 gates must be PASS before production promotion.**

> **PG-18 note:** `SemanticCacheMissRateAnomaly` firing during the first 120 min of worker
> startup is expected cold-start noise and does **not** count as a gate failure.
> Gate PASS requires the alert to be resolved and not re-firing by T+180 min from worker start.
> Full observation procedure: `docs/runbooks/d2_anomaly_gate_playbook.md`

> **PG-19 evidence:** Non-production rollback drill executed 2026-04-12.
> Evidence document: `docs/runbooks/d2_rollback_drill_evidence.md`

---

## 6. Exact Enable / Disable Commands

### Enable D2 (non-production)
```bash
export SEMANTIC_CACHE_D2_ENABLED=1
# Restart workers to re-initialise SemanticCacheManager singleton
```

### Disable D2 (kill-switch)
```bash
export SEMANTIC_CACHE_D2_ENABLED=0
# Restart workers
```

### Enable D2 (production — after all 19 PG gates pass)
```bash
# Set in your production environment manifest — NOT in code
SEMANTIC_CACHE_D2_ENABLED=1

# Recommended: canary first (1 worker), then rolling expansion
# Monitor SemanticCacheMissRateAnomaly for 24 h before full rollout
```

### Inspect store health
```bash
python _b3_inspect.py
```

### Wipe store
```bash
python _b3_cleanup.py  # WARNING: destroys all L2 cache entries
```
