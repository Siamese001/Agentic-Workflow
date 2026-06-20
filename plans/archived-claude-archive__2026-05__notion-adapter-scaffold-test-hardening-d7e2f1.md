---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\notion-adapter-scaffold-test-hardening-d7e2f1.md'
original_relative_path: '_archive\\2026-05\\notion-adapter-scaffold-test-hardening-d7e2f1.md'
source_sha256: 7bc0f71f528aa9cd05f220a0458eb399a85309b3341ddf9876fe599e4a03cd65
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
slug: notion-adapter-scaffold-test-hardening-d7e2f1
status: Completed
created: 2026-05-11
dod_exempt: false
---

# Notion Adapter Scaffold Test Hardening

## Context

ADG auto-generated scaffold tests in `tests/agentic_core/L5_safety/adapters/` fail because
`tests/agentic_core/` contains `__init__.py` files throughout. Under pytest's
`--import-mode=importlib`, this causes Python to register `tests/agentic_core/` as a shadow
namespace package that takes priority over the production `agentic_core/` package when
`importlib.import_module()` is called inside tests. Every `importlib.import_module(MODULE_PATH)`
call resolves to the tests-tree shadow instead of the production module, yielding:

```
ModuleNotFoundError: No module named 'agentic_core.L5_safety.adapters.<module>'
```

The fix applied to `test_notion_approval_adapter.py` in the prior session (`_evict_shadow_modules`
+ repo-root `sys.path` insertion) is the canonical repair pattern for this directory.

## Failure Inventory (pre-fix baseline)

| Test File | Tests | Root Cause | Production Module |
|---|---|---|---|
| `test_notion_approval_adapter.py` | 6 | Shadow namespace | `notion_approval_adapter.py` ✅ **FIXED** |
| `test_contract.py` | 6 | Shadow namespace | `human_approval_adapter.py` (contract re-exports) |
| `test_orkes_approval_adapter.py` | 6 | Shadow namespace | `orkes_approval_adapter.py` |
| `test_slack_approval_adapter.py` | 6 | Shadow namespace | `slack_approval_adapter.py` |
| `test_test_notion_adapter.py` | 6 | **Non-existent module** — scaffold targets `agentic_core.L5_safety.adapters.test_notion_adapter` which does not exist | N/A — delete or redirect |

**Total outstanding**: 24 failures across 4 test files.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|---|---|---|---|---|
| W1 | P1–P4 | Apply `_evict_shadow_modules` fix to 3 real-module scaffold tests | ~800 | 🔲 TODO |
| W2 | P5 | Resolve `test_test_notion_adapter.py` — delete (invalid scaffold) | ~100 | 🔲 TODO |
| W3 | P6 | Verify all 5 files pass; run full adapters suite | ~100 | 🔲 TODO |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1 | Fix `test_contract.py` | 1 | Shadow namespace — `contract` module targets `human_approval_adapter` contract surface | ~200 | 🔲 TODO |
| P2 | Fix `test_orkes_approval_adapter.py` | 1 | Shadow namespace — same pattern as notion fix | ~200 | 🔲 TODO |
| P3 | Fix `test_slack_approval_adapter.py` | 1 | Shadow namespace — same pattern as notion fix | ~200 | 🔲 TODO |
| P4 | Fix `test_notion_approval_adapter.py` | 1 | ✅ Already fixed in prior session | 0 | ✅ DONE |
| P5 | Delete `test_test_notion_adapter.py` | 1 | Scaffold targets non-existent production module — invalid, no fix possible | ~100 | 🔲 TODO |
| P6 | Verification sweep | 0 | Run full suite; confirm 0 failures in adapters dir | ~100 | 🔲 TODO |

## Repair Pattern (canonical — from P4 fix)

For each scaffold test using `importlib.import_module(MODULE_PATH)` in this directory:

1. Replace `import importlib` with `import pathlib`, `import sys`
2. Add `_REPO_ROOT = pathlib.Path(__file__).parents[4]`
3. Add `_SHADOW_PREFIXES` tuple + `_evict_shadow_modules()` helper
4. Add `_load_module()` that evicts shadows, inserts repo root into `sys.path`, then calls `importlib.import_module(MODULE_PATH)`
5. Replace all `importlib.import_module(MODULE_PATH)` call-sites with `_load_module()`

The `_evict_shadow_modules` function iterates `sys.modules`, finds entries whose `__file__`
contains `"tests"`, and removes them — causing the next `importlib.import_module` to re-resolve
from the production package on `sys.path`.

## Definition of Done

| # | Criterion | Verification |
|---|---|---|
| DoD-1 | All 5 test files in `tests/agentic_core/L5_safety/adapters/` collected by pytest with no errors | `pytest tests/agentic_core/L5_safety/adapters/ --co -q` exits 0 |
| DoD-2 | 24/24 previously-failing tests now pass (4 files × 6 tests) | `pytest tests/agentic_core/L5_safety/adapters/ -q` shows `24 passed` (test_test_notion_adapter.py deleted, so 24 remaining) |
| DoD-3 | `test_notion_approval_adapter.py` continues to pass (regression guard) | Included in the sweep |
| DoD-4 | No new failures introduced in `tests/unit/windsurf_scripts/`, `tests/unit/tools_notion/` | Run both suites; 0 new failures |
| DoD-5 | Plan registered in Notion Plans DB with Status=In Progress | Notion row present with correct slug |

## Verification-vs-Deferral

| Item | Disposition | Reason |
|---|---|---|
| Other `tests/agentic_core/` scaffold failures (1823 across all layers) | **Deferred** | Pre-existing systemic issue; out of scope for Notion hardening session |
| `test_check_test_concentration_ratio.py` failures | **Deferred** | Pre-existing `ModuleNotFoundError: No module named 'tools'` subprocess issue; unrelated to Notion |
| Removing `__init__.py` from `tests/agentic_core/` tree | **Deferred** | Systemic change affecting 1823 tests; requires dedicated plan and full regression sweep |
