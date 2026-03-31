# RCA: Import Errors (6) Persist Despite All ADG Tests Passing

**Status:** ✅ RESOLVED  
**Date:** 2026-03-30  
**Severity:** HIGH — real layer-boundary violations invisible to CI gate

---

## 1. Symptom

ADG Enhancement E10 reports 6 critical repair routes. Redis shows `GV_violates=6`. All ADG tests pass. The 6 layer-boundary violations in the live repo go undetected by the test suite.

---

## 2. Root Causes

### RC-1: Test Suite Uses Synthetic Fixtures, Not the Real Repo

**The critical gap.** Every ADG violation-related test constructs a mini in-memory SQLite fixture and asserts that violations *can be detected* — they never assert that the real repo *has zero violations*.

| Test | What it actually tests | What it DOESN'T test |
|---|---|---|
| `test_layer_violation_detected` | Violation count > 0 in a synthetic DB | Real repo is clean |
| `test_layer_violation_count_incremented` | Builder counts violations correctly (unit test) | Real repo is clean |
| `test_violations_list_populated` | Fixture DB violation IDs exist in Redis | Real repo is clean |
| `test_violation_ids_resolve` | Violation HASHes resolve in Redis | Real repo is clean |

None of these check `SELECT * FROM violations WHERE category='violates'` on the live SQLite.

### RC-2: MCP `adg_violations` Tool Hangs (5000-entry Payload)

`adg_violations()` called `_redis().lrange("adg:violations", 0, -1)` (all 4979 entries), then built a 4979-command pipeline and returned the entire result as a single JSON payload. Windsurf's MCP JSON transport stalls on payloads this large, causing the tool call to hang indefinitely. This masked the violations from in-session inspection.

**Before:** No `limit`/`offset`/`category`/`severity` parameters, returns all 4979 violations at once.  
**After:** Default `limit=200`, `max=500`, optional `category` and `severity` filters — paginated and filterable.

### RC-3: The 6 Actual Layer-Boundary Violations

All 6 are `category='violates'`, `severity='MEDIUM'`, `disposition='untriaged'`:

| # | Evidence | File | Line | Import |
|---|---|---|---|---|
| 4974 | L0→L2 | `agentic_core/L0_routing/scripts/error_handler.py` | 86 | `from agentic_core.L_CONTRACTS.lifecycle_trace_contract import ...` |
| 4975 | L0→L_SL | `agentic_core/L0_routing/scripts/execute_ssot.py` | 838 | `from system_learning.adapters.workflow_outcome_sl_adapter import ...` |
| 4976 | L0→L2 | `agentic_core/L0_routing/scripts/forward_rolling_facade.py` | 22 | `from agentic_core.L_CONTRACTS.lifecycle_trace_contract import ...` |
| 4977 | L5→L_TOOLS | `agentic_core/L5_safety/hitl/review_queue_api.py` | 27 | `from agentic_core.L5_safety.hitl.hitl_graph import ...` |
| 4978 | L_TOOLS→L_RUNTIME | `agentic_core/adg/schema_util.py` | 25 | local stub (no import — misclassified?) |
| 4979 | L_SHARED→L_TOOLS | `agentic_core/evaluation/golden/eval_spine_integration.py` | 13 | `from agentic_core.runtime.eval_spine import EvalSpine` |

---

## 3. Corrective Actions — Executed

### ✅ Fix 1: MCP Server Pagination (immediate, prevents hang)

**File:** `tools/adg/adg_mcp_server.py`

`adg_violations()` now accepts:
- `limit: int = 200` (max 500) — prevents giant payload
- `offset: int = 0` — pagination
- `category: str = ""` — filter e.g. `'violates'`
- `severity: str = ""` — filter e.g. `'CRITICAL'`

To get only the 6 layer violations: `adg_violations(category='violates')`.

### ✅ Fix 2: Real-Repo Zero-Violation Gate Test Added

**File:** `tests/adg/test_adg_projection_integrity.py` — `TestLiveRepoZeroLayerViolations`

New class `TestLiveRepoZeroLayerViolations::test_zero_gv_violates_in_live_adg`:
- Connects to live Redis (db=0)
- Scans all violation HASHes in batches of 500
- Asserts zero `category='violates'` entries
- Reports all offenders on failure with file:line details

**Confirmed:** Gate **FAILS** correctly on the current state (6 violations found), confirming it would have caught this if it had existed.

---

## 4. Remaining Work (Not in Scope of This RCA)

The 6 layer violations still exist and must be fixed or triaged:

- **4974, 4976** — `L0_routing/scripts/` importing `L_CONTRACTS` (lifecycle emitters). Move to `L0` contract shim or re-classify `L_CONTRACTS` as L0-accessible.
- **4975** — `execute_ssot.py` importing `system_learning` at module scope. Wrap in `try/except ImportError` or move to lazy import.
- **4977** — `L5_safety/hitl/review_queue_api.py` importing `hitl_graph` (already L5, likely misclassified boundary). Review `L_TOOLS` classification.
- **4978** — `schema_util.py` stub function flagged as `L_TOOLS→L_RUNTIME`. No import on line 25 — the violation edge is from a local def, suggesting the ADG layer-assignment for `schema_util.py` is wrong (it's in `agentic_core/adg/` = `L_TOOLS` but references `L_RUNTIME` symbols).
- **4979** — `eval_spine_integration.py` importing `agentic_core.runtime.eval_spine`. Move to `L_RUNTIME`-accessible layer or add shim.

---

## 5. Prevention

| Measure | Status |
|---|---|
| `TestLiveRepoZeroLayerViolations` gate added | ✅ Done |
| `adg_violations` MCP tool paginated | ✅ Done |
| Zero-violation gate runs on CI (add to `adg-ci-gates.yml`) | ⬜ Pending |
