# ================================================
# PHASE 3 — ATOMIC STRUCTURAL + CODE REWRITE TEST SUITE
# ================================================

## 3.1 — STRUCTURAL MUTATION TESTS

### TEST CASE 3.1-ST-01 — Snapshot creation before mutation
Action:
- Run Phase 3 normally.
Expected:
- Phase creates directory:
  ```
  06_data/phase3_snapshots/<root>_<timestamp>/
  ```
- Snapshot is a full mirror of `TARGET_ROOT` before any rewrite.
Pass:
- Directory exists and contains a complete copy.

---

### TEST CASE 3.1-ST-02 — Rollback on critical failure
Prep:
- Delete the golden file for a known component hash.
Expected:
- Phase 3 aborts rewrite for that file.
- Full rollback restores **all files** to snapshot state.
- No partial rewrite artifacts remain.
Pass:
- FS identical to pre-Phase-3 snapshot.
- Error logged: `missing_golden_file`.

---

## 3.2 — COMPONENT-LEVEL REWRITE TESTS

### TEST CASE 3.2-CR-01 — Valid rewrite (spans → stitched file)
Given components `[A, B, C]` in semantic order.
Expected output file:
```
# auto-generated header
A content
B content
C content
```
Rules:
- Spans sorted strictly by start index.
- No overlaps.
- Header included if spec requires.
Pass:
- Final file matches stitched component content exactly.

---

### TEST CASE 3.2-CR-02 — Missing semantic component → golden fallback
Break or delete a single semantic file.
Expected:
- Phase logs:
  ```
  fallback_golden: reason = missing_component_ids
  ```
- Entire file is rebuilt from `.golden.json`.
Pass:
- Golden-based rewrite matches golden file verbatim.

---

### TEST CASE 3.2-CR-03 — Corrupt or invalid spans → golden fallback
Prep:
- Modify span_start/span_end to invalid values.
Expected:
- Golden fallback triggered.
- No rollback (only graceful fallback).
Pass:
- File written from golden content and logged as span_failure.

---

## 3.3 — IMPORT REWRITE TESTS

### TEST CASE 3.3-IMP-01 — Update import paths based on SSoT routing
Legacy import:
```python
from Monolith.Utils import Planner
```
Migrated location:
```
01_agentic_core/L3_orchestration/planner_router.py
```
Expected rewritten import:
```
from agentic_core.L3_orchestration.planner_router import Planner
```
Pass:
- Exact rewrite appears in final file.
- Import map updated accordingly.

---

### TEST CASE 3.3-IMP-02 — Circular import detection (non-blocking)
Prep:
- Create artificial circular imports among 2–3 modules.
Expected:
- Smoke test detects circularity.
- Phase logs the cycle, but does NOT rollback.
Pass:
- Issue recorded in `phase3_smoketests.json`.

---

## 3.4 — SMOKE TESTS (MANDATORY)

### TEST CASE 3.4-SM-01 — Import all canonical top-level modules
Attempt imports for:
```
agentic_core
schemas
runtime
config
observability
scripts
apps_rg
apps_lic
```
Expected:
- Successful import for all valid modules.
- Failures logged but do NOT block completion.
Pass:
- `phase3_smoketests.json` lists any failures, otherwise empty.

---

# END OF PHASE 3 TEST SUITE
