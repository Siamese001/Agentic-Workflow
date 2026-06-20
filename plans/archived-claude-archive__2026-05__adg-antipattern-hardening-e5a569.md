---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\adg-antipattern-hardening-e5a569.md'
original_relative_path: '_archive\\2026-05\\adg-antipattern-hardening-e5a569.md'
source_sha256: 85b4afe4fd3d76186577714c57e1923e9392b955852ea2532ee69f5d60149553
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: adg-antipattern-hardening-e5a569
plan_type: refactor
touches_agentic_core: true
touches_governance_ci: false
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# ADG Anti-Pattern Hardening Plan

Expand HIGH severity coverage to all `agentic_core/` and `system_learning/` paths, and add three hardened detectors (`blocking_call_in_async`, `global_state_mutation`, `retry_without_backoff`) to `_AntipatternVisitor` with FP guards, then sync `antipattern_registry._SEVERITY_MAP` with the SQL severity classification.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-12

---

## Wave Overview

**Waves**: 4 total (W1–W4)
**Current**: W1

**Wave Manifest**:
- **W1** — SQL severity expansion | agentic_core + system_learning | TODO
- **W2** — Hardened detectors | 3 new visitors | TODO
- **W3** — Severity map sync | registry alignment | TODO
- **W4** — ADG run + validate | terminal verification | TODO

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

## Wave 1 — SQL Severity Expansion

WAVE_ID: W1
WAVE_STATUS: IN_PROGRESS
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — Update multi_writer.py HIGH CASE branch | PHASE_STATUS: IN_PROGRESS | PHASE_COMPLETE: NO
- **W1.2** — Extend test_violation_severity_sql.py | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Files**: `agentic_core/adg/artifact/multi_writer.py`, `agentic_core/adg/artifact/ArtifactPaths.py`

**Scope**:

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

## Wave 2 — Three Hardened Detectors

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — blocking_call_in_async detector | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — global_state_mutation detector | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** — retry_without_backoff detector | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**File**: `agentic_core/adg/extraction/visitors/core.py`

**Scope**: Add three new visitor methods to `_AntipatternVisitor` with FP guards:

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

## Wave 3 — Sync Severity Map

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Update _SEVERITY_MAP values | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Add registry severity map tests | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**File**: `agentic_core/adg/runtime/antipattern_registry.py`

**Scope**: The `_SEVERITY_MAP` is currently out of sync with the SQL classification. Align it:

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

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — Run generate_full_adg.py | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** — Verify terminal table metrics | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.3** — Refresh Redis hot cache | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
1. Run `python tools/generate/generate_full_adg.py`
2. Verify terminal table shows:
   - P2 HIGH count increases (more agentic_core/ violations promoted from MEDIUM)
   - P3 MEDIUM count decreases correspondingly
   - P4 LOW count drops (retry/blocking/mutation move to MEDIUM or HIGH)
3. Run `/adg-redis-refresh` to reload hot cache

## Definition of Done

DoD-1: SQL severity expansion complete
- Evidence: HIGH CASE branch covers all agentic_core/ + system_learning/
- Status: TODO

DoD-2: Three hardened detectors implemented
- Evidence: Tests pass for blocking_call_in_async, global_state_mutation, retry_without_backoff
- Status: TODO

DoD-3: Severity map synchronized
- Evidence: _SEVERITY_MAP aligns with SQL classification
- Status: TODO

DoD-4: ADG run validates changes
- Evidence: Terminal table shows expected count shifts
- Status: TODO

DoD-5: Redis cache refreshed
- Evidence: /adg-redis-refresh completes successfully
- Status: TODO

---

## Forbidden
- No changes to `.pre-commit-config.yaml`
- No changes to `_check_p1_defects()` blocking logic
- No guardian exemptions added
- No changes to guardian exemption ceiling
