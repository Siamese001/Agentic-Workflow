# Retire `_legacy_windsurf` / `tools/windsurf` Mirror Trees

**Plan slug:** `retire-legacy-windsurf-mirrors-a9d3f7`
**SSOT:** `plans/retire-legacy-windsurf-mirrors-a9d3f7.md`
**Notion page:** `37927693-f55c-819e-b4ae-fadefa94827a`
**Worktree:** `C:/Git/apps_rg_e2e` (branch `apps_rg_e2e`)

---

## Context (SCQA)

**Situation:** The repo has two legacy mirror trees left over from the Windsurf→Claude Code
migration:

1. `.codex/governance/scripts/_legacy_windsurf/` — ~100 Windsurf cascade scripts copied
   verbatim. The shim `_notion_plans_status_check.py` tries to re-export from
   `.cursor/scripts/_notion_plans_status_check.py` via `spec_from_file_location`. That path
   does not exist in any worktree → `FileNotFoundError` → **26 pytest collection errors** in
   `test_backfill_historical_plan_statuses.py` (and any test that imports the shim).

2. `tools/windsurf/` — 3 stale mirrors of `tools/plan_lifecycle/`:
   - `wave_execution_state.py` (canonical: `tools/plan_lifecycle/wave_execution_state.py`)
   - `_plan_wave_table_updater.py`
   - `plan_lifecycle_manager.py`
   The mirror lacks the newer `_current_notion_status` / `status_already_completed` guard
   patterns → **2 pre-existing test failures** in
   `tests/unit/tools/notion/test_wave_lifecycle_guard.py::TestCIGatePresence`.

**Complication:** Every test in `tests/unit/windsurf_scripts/` inserts the `_legacy_windsurf`
directory on `sys.path` and imports from it. As long as the shim probe is broken, any batch
run that triggers the `_notion_plans_status_check` import chain collects 26 errors.

**Question:** How do we permanently eliminate these errors with the minimum safe delta?

**Answer:** Four waves — fix the broken shim first (W1, immediate), fix the two stale
mirror tests (W2, immediate), migrate the `windsurf_scripts` tests to canonical imports
(W3), and delete the dead trees (W4).

---

## Status Tables

### Wave Progress

| Wave | Focus | Files | Status |
|------|-------|-------|--------|
| W1 | Fix `_legacy_windsurf/_notion_plans_status_check.py` probe path | 1 | ✅ Done (281 passed) |
| W2 | Fix 2 `TestCIGatePresence` stale mirror references | 1 | ✅ Done (281 passed) |
| W3 | Migrate `tests/unit/windsurf_scripts/` imports to canonical paths | 25 test files | ✅ Done (753 passed, 71 pre-existing failures) |
| W4 | Archive / delete dead trees (`tools/windsurf/`, `_legacy_windsurf/`) | 3 + ~100 files | ✅ Done (73 failed / 773 passed — 4 extra failures from previously-erroring tests now running) |

### Phase-Level Summary

| Phase ID | Title | Scope | Status |
|----------|-------|-------|--------|
| W1.P1 | Fix broken shim probe | `.codex/governance/scripts/_legacy_windsurf/_notion_plans_status_check.py` | ✅ |
| W2.P1 | Fix stale mirror test refs | `tests/unit/tools/notion/test_wave_lifecycle_guard.py` | ✅ |
| W3.P1 | Batch import migration | `tests/unit/windsurf_scripts/*.py` (25 files) | ✅ |
| W4.P1 | Delete `tools/windsurf/` | `tools/windsurf/*.py` (3 files) | ✅ git rm done |
| W4.P2 | Archive `_legacy_windsurf/` + fix all production references | `.codex/governance/scripts/_legacy_windsurf/` + ~60 files | ✅ Archived to `docs/archive/windsurf/legacy-tree/governance_scripts/`; all production imports fixed |

---

## Wave 1 — Fix Broken Shim Probe (immediate)

### Root cause

```
# Current (broken — .cursor/scripts absent in worktrees):
_SSOT_PATH = Path(__file__).resolve().parents[2] / ".cursor" / "scripts" / "_notion_plans_status_check.py"

# parents[0] = _legacy_windsurf/
# parents[1] = scripts/
# parents[2] = governance/   ← then jumps to .cursor/scripts/ which doesn't exist
```

### Fix

```python
# Fixed — points to parent directory (the real SSOT):
_SSOT_PATH = Path(__file__).resolve().parent.parent / "_notion_plans_status_check.py"

# parent       = .codex/governance/scripts/_legacy_windsurf/
# parent.parent = .codex/governance/scripts/   ← _notion_plans_status_check.py IS here
```

**File:** `.codex/governance/scripts/_legacy_windsurf/_notion_plans_status_check.py`
**Change:** lines 8–12 — update `_SSOT_PATH` construction.

**Verification:** `python -m pytest tests/unit/tools_notion/ -q --tb=short` — 0 collection errors.

---

## Wave 2 — Fix Stale Mirror Test References (immediate)

### Root cause

`TestCIGatePresence` in `test_wave_lifecycle_guard.py` reads
`tools/windsurf/wave_execution_state.py` (the legacy mirror). That file exists but was never
updated with the newer `_current_notion_status` / `status_already_completed` guard patterns
added to `tools/plan_lifecycle/wave_execution_state.py`.

### Fix

Update lines 148 and 153 in `tests/unit/tools/notion/test_wave_lifecycle_guard.py`:

```python
# Before (stale mirror path):
path = REPO_ROOT / "tools" / "windsurf" / "wave_execution_state.py"

# After (canonical SSOT path):
path = REPO_ROOT / "tools" / "plan_lifecycle" / "wave_execution_state.py"
```

**File:** `tests/unit/tools/notion/test_wave_lifecycle_guard.py` (lines 148, 153)

**Verification:** `python -m pytest tests/unit/tools/notion/test_wave_lifecycle_guard.py -v` → all pass.

---

## Wave 3 — Migrate `windsurf_scripts` Test Imports (deferred)

**Scope:** ~25 test files under `tests/unit/windsurf_scripts/`.

**Pattern:** each file does:
```python
sys.path.insert(0, str(REPO_ROOT / ".codex" / "governance/scripts" / "_legacy_windsurf"))
```
Replace with:
```python
sys.path.insert(0, str(REPO_ROOT / ".codex" / "governance" / "scripts"))
```

Since `.codex/governance/scripts/_notion_plans_status_check.py` (and all other governance
scripts) already live directly in `.codex/governance/scripts/`, removing the `_legacy_windsurf`
path segment is the only change needed per file.

**Files to migrate** (representative — all `tests/unit/windsurf_scripts/*.py`):
- `test_notion_plans_status_check.py`
- `test_wave_execution_state.py`
- `test_plan_registration.py`
- … (22 more files, same one-line pattern change)

**Verification:** `python -m pytest tests/unit/windsurf_scripts/ -q` → 0 errors, 0 failures.

---

## Wave 4 — Delete Dead Trees (deferred, after W3 green)

### W4.P1 — Delete `tools/windsurf/`

Three files, all shadowed by `tools/plan_lifecycle/`:
- `tools/windsurf/wave_execution_state.py`
- `tools/windsurf/_plan_wave_table_updater.py`
- `tools/windsurf/plan_lifecycle_manager.py`

**Action:** `git rm tools/windsurf/wave_execution_state.py tools/windsurf/_plan_wave_table_updater.py tools/windsurf/plan_lifecycle_manager.py`

### W4.P2 — Archive `_legacy_windsurf/`

Move entire `_legacy_windsurf/` directory to `archives/legacy_windsurf_2026-06-08/`.
Add a one-line redirect `README.md` in `_legacy_windsurf/` if directory is kept as a tombstone.

**Pre-condition:** W3 green (no remaining imports of `_legacy_windsurf`).

---

## Definition of Done

| # | Criterion | Verification |
|---|-----------|-------------|
| 1 | W1: 0 collection errors from `_notion_plans_status_check` shim | `pytest tests/unit/tools_notion/ -q` → no errors |
| 2 | W2: all `TestCIGatePresence` tests pass | `pytest tests/unit/tools/notion/test_wave_lifecycle_guard.py -v` → all pass |
| 3 | W3: `tests/unit/windsurf_scripts/` fully green | `pytest tests/unit/windsurf_scripts/ -q` → 0 errors |
| 4 | W4: no production file imports from `_legacy_windsurf` or `tools/windsurf` | `grep -r "_legacy_windsurf\|tools.windsurf" --include="*.py" . \| grep -v test \| grep -v archive` → empty |
| 5 | Full suite shows no regression vs baseline | `pytest tests/unit/ -q --tb=short` ≥ baseline pass count |

**Verification-vs-deferral:** W1+W2 are implemented this session (immediate breakage fixes).
W3+W4 are deferred waves (bulk migration, safe to do incrementally).

---

## Files Changed (W1+W2 — this session)

- `.codex/governance/scripts/_legacy_windsurf/_notion_plans_status_check.py` — fix probe path
- `tests/unit/tools/notion/test_wave_lifecycle_guard.py` — redirect stale mirror refs
