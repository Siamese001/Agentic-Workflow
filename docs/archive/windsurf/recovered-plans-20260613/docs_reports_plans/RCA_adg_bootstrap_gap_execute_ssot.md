# RCA: ADG Bootstrap Gap in `execute_ssot` — 2026-03-11

## Status: FIXED (exit code 0 confirmed post-fix)

---

## Problem Statement

`execute_ssot --heal` was not automatically rebuilding the ADG before running.
The ADG is the backbone of every phase — if it is stale, agents operate on wrong blast-radius data.
The user had to manually prompt a graph rebuild, then re-run, to get a fresh graph.

---

## DEPENDENCY_GRAPH (ADG Evidence)

**Source:** `artifacts/adg/adg_full_20260311T100549Z.json`
- Modules: 3,261 | Edges: 51,400
- G1_imports=24,717 | G3_implements=1,835 | G4_calls=13,381 | GV_violates=247

**Blast radius of fix:** `execute_ssot.py` → `execute_ssot_integration.py` → `cache_loader.py`
(3-hop chain, all within `agentic_core/L0_routing/scripts/` and `agentic_core/adg/`)

**ADG callers of `generate_full_adg`:** 2 references, both in `tests/unit/test_adg_cli_commands.py`.
Zero references from `execute_ssot.py` — confirmed by graph scan.

---

## Root Cause Analysis

### Gap 1 — `_emit_adg_pre_run_artifact` uses stale cache

**Location:** `@c:\Git\Agentic-Workflow\agentic_core\L0_routing\scripts\execute_ssot.py:7739-7740`

`_emit_adg_pre_run_artifact()` is called before `_legacy_main()` in `main()`.
It calls `build_pre_run_report(force_fresh=False)` — the default.
`build_pre_run_report` delegates to `load_or_scan()` in `cache_loader.py`.

**Cache key** in `cache_loader.py`: `commit_sha + scanner_version + schema_version + python_version`.
If files were modified without a new commit (e.g., during an active heal session), the commit SHA is
unchanged → **cache hit → stale `scan_result_cache.json` is returned**.

The `force_fresh=True` parameter existed on `build_pre_run_report` but was:
1. Never passed by the caller
2. Never acted upon inside `build_pre_run_report` itself (the `if force_fresh` branch was missing)

### Gap 2 — `_emit_adg_pre_run_artifact` result is fire-and-forget

**Location:** `@c:\Git\Agentic-Workflow\agentic_core\L0_routing\scripts\execute_ssot.py:7739-7750`

```python
# ADG pre-run impact artifact — emitted before main execution
_emit_adg_pre_run_artifact(REPO_ROOT)   # ← result discarded

_legacy_main(remaining, ...)            # ← no ADG passed in
```

The `PreRunADGReport` is written to a JSON file on disk but never returned or threaded
into `_legacy_main`. Neither `execute_phase1_discovery`, `execute_phase2_reconciliation`,
nor `execute_phase3_validation` receive the `ScanResult`.

### Gap 3 — `_legacy_main` has no ADG bootstrap block

**Location:** `@c:\Git\Agentic-Workflow\agentic_core\L0_routing\scripts\execute_ssot.py:7882`

`_legacy_main` initialises `state_mgr = RuntimeStateManager(...)` but never populates
`state_mgr.state["adg_scan_result"]`. Agents that retrieve state from `state_mgr` cannot
access the current graph. They must either re-scan independently or skip graph-backed logic.

### Gap 4 (side-effect) — Missing modules deleted from working tree

8 modules referenced in the import chain were deleted from the working tree (not from git history):

| Module | Last commit |
|--------|-------------|
| `agentic_core/base_agents/SovereignBaseAgent.py` | `HEAD` |
| `agentic_core/mixins/atomic_execution_mixin.py` | `de0b164db` |
| `agentic_core/mixins/audit_trail_mixin.py` | `de0b164db` |
| `agentic_core/interfaces/execution_agents.py` | `de0b164db` |
| `agentic_core/embeddings/embedding_factory.py` | `e7ae79fc6` |
| `agentic_core/embeddings/embedding_input_guard.py` | `65eb33172` |
| `agentic_core/L5_safety/validators/chaos_healing_integration_types.py` | `b61ee1437` |
| `agentic_core/L5_safety/validators/dependency_healing_integration_types.py` | `b61ee1437` |
| `agentic_core/mixins/mcp_hardened_mixin.py` | `de0b164db` |

Two modules (`subatomic_testing_mixin`, `cache_strategy_manager_types`) never existed at HEAD
but are safely guarded by `try/except ImportError` blocks.

---

## Fixes Applied

### Fix 1 — `build_pre_run_report` honours `force_fresh`

**File:** `@c:\Git\Agentic-Workflow\agentic_core\adg\applications\execute_ssot_integration.py:126-132`

```python
# Before
result = load_or_scan(repo_root=str(repo_root))

# After
if force_fresh:
    invalidate_cache()  # bust commit-SHA cache so load_or_scan triggers a real rescan
result = load_or_scan(repo_root=str(repo_root))
```

### Fix 2 — `_emit_adg_pre_run_artifact` forces fresh scan

**File:** `@c:\Git\Agentic-Workflow\agentic_core\L0_routing\scripts\execute_ssot.py:7649-7653`

```python
# Before
report = build_pre_run_report(changed_files=[_THIS_FILE], repo_root=repo_root)

# After
invalidate_cache()  # [ADG-BOOTSTRAP] force fresh scan
report = build_pre_run_report(changed_files=[_THIS_FILE], repo_root=repo_root, force_fresh=True)
```

### Fix 3 — Mandatory ADG rebuild block in `_legacy_main`

**File:** `@c:\Git\Agentic-Workflow\agentic_core\L0_routing\scripts\execute_ssot.py:8076-8093`

Added immediately after `state_mgr` is initialised:

```python
# [ADG-BACKBONE] Mandatory full ADG rebuild at _legacy_main startup.
# Every phase (1/2/3) must operate on the current graph, not a stale cache.
# ScanResult is stored in state_mgr so all agents can access it via state_mgr.state["adg_scan_result"].
_adg_scan_result = None
try:
    from agentic_core.adg.runtime.cache_loader import invalidate_cache as _adg_invalidate, load_or_scan as _adg_load

    _adg_invalidate()  # bust commit-SHA cache before every heal/validate run
    _adg_scan_result = _adg_load(repo_root=str(project_root))
    state_mgr.state["adg_scan_result"] = _adg_scan_result
    logger.info("[ADG-BOOTSTRAP] Fresh ADG built: %d nodes, %d edges", ...)
except Exception as _adg_exc:
    logger.warning("[ADG-BOOTSTRAP] ADG rebuild failed — agents will run without graph: %s", _adg_exc)
    state_mgr.state["adg_scan_result"] = None
```

### Fix 4 — Restored 8 deleted modules from git history

Used `git show <commit>:<path>` to restore each file. All restored files confirmed `ast.parse()` clean.

---

## Remaining Work (Phase Threading — out of scope for this RCA)

The three phase functions still do not receive `ScanResult` as an argument.
Agents that need it must read `state_mgr.state["adg_scan_result"]` themselves.
Full phase-level threading (`execute_phase1_discovery(adg_result=...)`) is a follow-up
refactor requiring signature changes across all 3 phase functions and their callers.

**Tracking:** agents should be updated to read `state_mgr.state["adg_scan_result"]`
as the canonical ADG access pattern, consistent with how `apply_proposals` is accessed.

---

## Verification

```
exit code: 0
VERDICT: LOW_SIGNAL (2/12 gate criteria passed, 0 failed, 10 N/A)
[ADG-BOOTSTRAP] log line confirmed in output: Fresh ADG built before _legacy_main phases
```

Post-fix run completed with `--heal` processing all territories, `[ADG-BOOTSTRAP]` log
emitted at `_legacy_main` startup, confirming the fresh graph is available to all agents
via `state_mgr.state["adg_scan_result"]` before any phase executes.

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

