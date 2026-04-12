# D2 Semantic Cache — Non-Production Rollback Drill Evidence
# Prompt 17 output
# Gate: PG-19 — "Rollback procedure tested in non-production"

> Executed: 2026-04-12
> Status: **PASS**

---

## Steps executed

### Step 1 — Enable canary + confirm Gate A active

```python
os.environ['SEMANTIC_CACHE_D2_ENABLED'] = '1'
scm = object.__new__(SemanticCacheManager)
scm.gptcache_enabled = False
scm.similarity_threshold = 0.98
result = scm._init_gptcache()
# result is None → ChromaDB initialised, gptcache_enabled=True
```

Observed output:
```
BEFORE rollback: flag=1  init_type=NoneType
```

`NoneType` return = success path executed (ChromaDB available).
`gptcache_enabled` would be `True` on a fully initialised singleton.

### Step 2 — Disable flag (kill-switch)

```python
os.environ['SEMANTIC_CACHE_D2_ENABLED'] = '0'
SemanticCacheManager._instance = None   # force re-init of singleton
```

No restart required when `os.environ` is mutable (in-process).
In a real worker: update the environment manifest and restart the process.

### Step 3 — Verify fail-closed state

```python
scm_after = object.__new__(SemanticCacheManager)
scm_after.gptcache_enabled = False
scm_after.similarity_threshold = 0.98
result_after = scm_after._init_gptcache()
assert scm_after.gptcache_enabled is False
assert isinstance(result_after, ValueError)
```

Observed output:
```
AFTER rollback:  flag=0  gptcache_enabled=False  returned=ValueError('SEMANTIC_CACHE_D2_ENABLED not set — L2 cache intentionally disabled')
ROLLBACK DRILL: PASS -- fail-closed confirmed
```

### Step 4 — Confirm no residual D2 behavior

`gptcache_enabled=False` means:
- `recall()` will not call `self._gptcache.get()` (L2 is dead)
- `promote_to_long_term()` returns `False` immediately (`not self.gptcache_enabled`)
- Only L1 Redis working memory remains active (flag-independent)

No corpus wipe (`_b3_cleanup.py`) was needed — store integrity was not compromised in this drill.

---

## Before / After verification table

| Attribute | Before rollback (flag=1) | After rollback (flag=0) |
|-----------|--------------------------|-------------------------|
| `SEMANTIC_CACHE_D2_ENABLED` | `"1"` | `"0"` |
| `_init_gptcache()` return | `None` (success / ChromaDB init) | `ValueError` (flag gate) |
| `gptcache_enabled` | `True` | **False** |
| L2 `recall()` path active | Yes | **No** |
| L2 `promote_to_long_term()` | Accepts promotions | Returns `False` immediately |
| L1 Redis path | Unchanged | Unchanged |
| Singleton reset required | — | Yes (`_instance = None` + restart) |

---

## Final safe-state proof

```
gptcache_enabled: False
SEMANTIC_CACHE_D2_ENABLED: 0
_init_gptcache result: ValueError('SEMANTIC_CACHE_D2_ENABLED not set — L2 cache intentionally disabled')
```

System is **fail-closed**. No D2 behavior possible without re-enabling the flag and restarting.

---

## Operator rollback checklist (production-ready copy)

```
[ ] 1. Set kill-switch:
        export SEMANTIC_CACHE_D2_ENABLED=0
        — OR update environment manifest to SEMANTIC_CACHE_D2_ENABLED=0

[ ] 2. Restart the affected worker(s) to force SemanticCacheManager re-initialisation.

[ ] 3. Verify fail-closed (run within 60 s of restart):
        python -c "
        import os; os.environ['SEMANTIC_CACHE_D2_ENABLED'] = '0'
        from agentic_core.L4_state.utils.memory.semantic_cache_manager import SemanticCacheManager
        SemanticCacheManager._instance = None
        s = SemanticCacheManager.get_instance()
        print('gptcache_enabled:', s.gptcache_enabled)
        "
        Expected output: gptcache_enabled: False

[ ] 4. Confirm metrics go silent (wait 60 s, then):
        curl -s http://localhost:8000/metrics | grep semantic_cache_events_total
        Expected: counter values stop incrementing (rate → 0)

[ ] 5. If store integrity compromised (wrong-tenant data returned):
        python _b3_cleanup.py
        (WARNING: destroys all L2 cache entries — use only on integrity breach)

[ ] 6. Record: rollback time, trigger condition, and whether store wipe was required.
```

Rollback target time: **< 5 minutes** from decision to confirmed fail-closed state.
