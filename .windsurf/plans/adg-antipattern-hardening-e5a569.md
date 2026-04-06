# ADG Anti-Pattern Hardening Plan

Expand HIGH severity coverage to all `agentic_core/` and `system_learning/` paths, and add three hardened detectors (`blocking_call_in_async`, `global_state_mutation`, `retry_without_backoff`) to `_AntipatternVisitor` with FP guards, then sync `antipattern_registry._SEVERITY_MAP` with the SQL severity classification.

---

## Context

| Kind | Count | Current ADG sev | Target sev | FP problem |
|---|---|---|---|---|
| `broad_exception_catch` | 2741 MEDIUM + 177 HIGH | HIGH only for L0/L2/L3/L5 | HIGH for **all** `agentic_core/` + `system_learning/` | None |
| `silent_exception_swallow` | 444M + 93H | same | same expansion | None |
| `log_and_swallow` | 536M + 205H | same | same expansion | None |
| `return_none_swallow` | 252M + 62H | same | same expansion | None |
| `retry_without_backoff` | 158 LOW | LOW (not detected by any live visitor) | MEDIUM globally, HIGH in `agentic_core/` | Fires on any `for x in for_retry` — needs loop-var exclusion |
| `blocking_call_in_async` | 15 LOW | LOW (not detected by live visitor) | HIGH in `agentic_core/`, MEDIUM elsewhere | Fires on `dict.get()` — needs explicit IO allowlist |
| `global_state_mutation` | 5 LOW | LOW (not detected by live visitor) | HIGH in `agentic_core/`, MEDIUM elsewhere | Fires on lazy-init guards — needs `if X is None: X =` exclusion |

**Additional drift:** `antipattern_registry._SEVERITY_MAP` rates `global_state_mutation=HIGH`, `blocking_call_in_async=HIGH` but ADG SQL rates them LOW — sync required.

---

## Wave Summary

| Wave | Focus | Files | Est. tests |
|---|---|---|---|
| **W1** | SQL severity expansion — all `agentic_core/` + `system_learning/` → HIGH | `multi_writer.py`, `ArtifactPaths.py` | Extend existing SQL tests |
| **W2** | Add 3 hardened detectors to `_AntipatternVisitor` in `core.py` | `visitors/core.py` | New parametrised detector tests |
| **W3** | Sync `_SEVERITY_MAP` in `antipattern_registry.py` | `antipattern_registry.py` | Registry severity map tests |
| **W4** | Run ADG + validate terminal table | None (run only) | — |

---

## Wave 1 — SQL Severity Expansion

**File:** `agentic_core/adg/artifact/multi_writer.py` and `agentic_core/adg/artifact/ArtifactPaths.py`

Change the HIGH CASE branch from 4 specific layer paths to all `agentic_core/%` and `system_learning/%`:

```sql
-- BEFORE (only 4 layers)
WHEN relation_type = 'antipattern'
 AND edge_kind IN ('broad_exception_catch','silent_exception_swallow',
                   'log_and_swallow','return_none_swallow')
 AND (source_file LIKE 'agentic_core/L0_routing/%' OR ...)
THEN 'HIGH'

-- AFTER (all agentic_core + system_learning)
WHEN relation_type = 'antipattern'
 AND edge_kind IN ('broad_exception_catch','silent_exception_swallow',
                   'log_and_swallow','return_none_swallow')
 AND (source_file LIKE 'agentic_core/%' OR source_file LIKE 'system_learning/%')
THEN 'HIGH'
```

**Tests:** Update `test_violation_severity_sql.py` — add `agentic_core/L1_cognition/`, `agentic_core/L4_state/`, `agentic_core/mixins/`, `system_learning/adapters/` → assert HIGH; `apps_rg/` stays MEDIUM.

---

## Wave 2 — Three Hardened Detectors in `_AntipatternVisitor`

**File:** `agentic_core/adg/extraction/visitors/core.py`

Add three new visitor methods to `_AntipatternVisitor` with FP guards:

### 2a. `blocking_call_in_async`
```python
_BLOCKING_IO_CALLS = frozenset({
    "time.sleep", "requests.get", "requests.post", "requests.put", "requests.delete",
    "requests.request", "urllib.request.urlopen", "urllib.urlopen",
    "socket.recv", "socket.send", "socket.connect", "socket.accept",
    "subprocess.run", "subprocess.call", "subprocess.check_output",
    "os.system", "asyncio.get_event_loop().run_until_complete",
})

def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
    """Detect blocking I/O calls inside async def bodies."""
    # Walk body for Call nodes whose symbol is in _BLOCKING_IO_CALLS
    # Emit edge_kind=blocking_call_in_async with sym=matched_call
```
- **FP guard:** only fire if resolved symbol is in explicit `_BLOCKING_IO_CALLS` allowlist — `.get()` attribute calls without a known-blocking prefix are skipped.

### 2b. `global_state_mutation`
```python
def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
    """Detect module-level UPPER_CASE name reassigned inside a function body."""
    # Walk body for ast.Assign/AugAssign where target.id.isupper()
    # AND the name exists at module-level
    # FP guard: skip if inside `if X is None:` / `if not X:` guard clause
```
- **FP guard:** detect lazy-init guard pattern (`if _X is None: _X = ...`) and skip — these are intentional singletons.

### 2c. `retry_without_backoff`
```python
def _loop_contains_retry_without_backoff(self, node: ast.AST) -> bool:
    """True only if loop iterates over range()/integer AND body has try/except AND no sleep/backoff."""
    # Require: loop target is ast.Name (not attribute), iter is ast.Call with func=range
    # OR loop has explicit retry counter variable (attempt, retry, retries)
    # FP guard: skip if loop variable name contains 'retry' as a collection name, not counter
```
- **FP guard:** only fire on `for i in range(N):` style retry loops, not `for item in collection:`.

**Tests:** `test_violation_severity_sql.py` + new `test_antipattern_visitor_detectors.py`:
- `blocking_call_in_async`: `time.sleep` in async def → fires; `dict.get()` in async def → no fire
- `global_state_mutation`: `_CACHE = value` in function body → fires; `if _CACHE is None: _CACHE = ...` → no fire  
- `retry_without_backoff`: `for i in range(3): try/except` → fires; `for item in for_retry:` → no fire

---

## Wave 3 — Sync `antipattern_registry._SEVERITY_MAP`

**File:** `agentic_core/adg/runtime/antipattern_registry.py`

The `_SEVERITY_MAP` is currently out of sync with the SQL classification. Align it:

| Category | Current `_SEVERITY_MAP` | New value | Rationale |
|---|---|---|---|
| `GLOBAL_STATE_MUTATION` | HIGH | MEDIUM (global default) | SQL: LOW→MEDIUM after detector fix; HIGH only in agentic_core via SQL |
| `BLOCKING_CALL_IN_ASYNC` | HIGH | HIGH | Aligns with SQL HIGH after detector fix |
| `RETRY_WITHOUT_BACKOFF` | MEDIUM | MEDIUM | Aligns with SQL MEDIUM after detector fix |
| `BROAD_EXCEPTION_CATCH` | HIGH | HIGH | Consistent |

**Note:** `_SEVERITY_MAP` is the runtime registry severity (used by agents at runtime). It doesn't need to be layer-aware — use the more permissive classification (HIGH globally for blocking/swallow kinds).

**Tests:** `test_antipattern_registry_severity.py` — assert each category maps to expected severity in `_SEVERITY_MAP`.

---

## Wave 4 — ADG Run + Validate

1. Run `python tools/generate/generate_full_adg.py`
2. Verify terminal table shows:
   - P2 HIGH count increases (more agentic_core/ violations promoted from MEDIUM)
   - P3 MEDIUM count decreases correspondingly
   - P4 LOW count drops (retry/blocking/mutation move to MEDIUM or HIGH)
3. Run `/adg-redis-refresh` to reload hot cache

---

## Forbidden
- No changes to `.pre-commit-config.yaml`
- No changes to `_check_p1_defects()` blocking logic
- No guardian exemptions added
- No changes to guardian exemption ceiling
