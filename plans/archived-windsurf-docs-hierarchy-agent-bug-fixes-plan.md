---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\hierarchy-agent-bug-fixes-plan.md'
original_relative_path: 'hierarchy-agent-bug-fixes-plan.md'
source_sha256: 1f8724085c33b353602b7de325610cfdb6c42a56f860e1e75e2d4b09f53c5b75
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-07'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# HierarchyAgent Bug Fixes — Gap Analysis & Implementation Plan

**Status:** PLAN MODE — no code changes applied
**Files in scope:** 3 source files, 1 new test file

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Summary of Bugs

Four related bugs allow `*Agent.py` files to be autonomously relocated into `tests/` (specifically `tests/support/`) by the healer system. The bugs form a chain: SSOT does not forbid it → confidence heuristic recommends it → relocation guard does not block it → prefix enforcement skips files already inside approved subfolders.

---

## Gap 1 — `_enforce_tests_structure`: approved-subfolder skip is too broad

**File:** `c:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\HierarchyAgent.py`
**Lines:** 506–511 (the early-continue block)

**Current behaviour:**
```python
# Skip files already inside an approved subfolder — they are correct
if len(rel.parts) > 1 and rel.parts[0] in approved_subfolders:
    continue
```

Any file that physically lands inside an approved subfolder (`support/`, `unit/`, etc.) is silently accepted — regardless of whether it has a `test_` prefix. `*Agent.py` files relocated into `tests/support/` pass through without a violation being recorded.

**Required fix:**
Remove the unconditional `continue`. For files already in an approved subfolder, still run the `INFRA_STEMS` exemption check and the `test_` prefix check. Only skip (no violation) if the file is infra; raise a violation if prefix is missing. The `continue` at the end of that branch should remain to prevent double-reporting, but it must come *after* the prefix check.

```python
if len(rel.parts) > 1 and rel.parts[0] in approved_subfolders:
    stem = py_file.stem
    if stem in INFRA_STEMS or stem.startswith("__"):
        continue  # legitimate infra — OK
    if not stem.startswith("test_"):
        results["violations_found"] += 1
        Logger.error(
            f"[HierarchyAgent] NON-TEST FILE IN tests/{rel.parts[0]}/: {rel} — ..."
        )
    continue  # handled — skip rest of loop body
```

---

## Gap 2 — `relocate_misplaced_files`: no pre-check blocking `*Agent.py` → `tests/`

**File:** `c:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\HierarchyAgent.py`
**Lines:** 408–418 (the per-root dispatch loop)

**Current behaviour:**
The dispatch loop calls `_enforce_tests_structure` for the `tests` root, but that method only *reports* violations after relocation has already happened in earlier runs. There is no active gate that prevents a future autonomous healing pass from *placing* an `*Agent.py` file into `tests/` as its relocation target.

**Required fix:**
Add a new private method `_block_agent_files_in_tests(results)` that:
1. Scans `tests/` for any `*.py` file whose name ends with `Agent.py`.
2. For each found: increments `violations_found`, logs a `Logger.error`, and does **not** move the file (human action required).

Call this method unconditionally at the end of `relocate_misplaced_files`, after the per-root dispatch loop:

```python
# [FIX-2] Belt-and-suspenders: Agent files must never be in tests/
self._block_agent_files_in_tests(results)
```

Implementation of `_block_agent_files_in_tests`:
```python
def _block_agent_files_in_tests(self, results: dict[str, Any]) -> None:
    tests_path = self.project_root / "tests"
    if not tests_path.exists():
        return
    for py_file in tests_path.rglob("*Agent.py"):
        rel = py_file.relative_to(self.project_root)
        results["violations_found"] += 1
        Logger.error(
            f"[HierarchyAgent] AGENT FILE IN tests/: {rel} — "
            "Agent files must never be relocated into tests/. "
            "Move this file back to its correct agentic_core/ territory manually."
        )
```

---

## Gap 3 — `get_best_target_l2`: `"support"` scores as a valid relocation target for agent files

**File:** `c:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\mission_utils_enforcer.py`
**Lines:** 160–183 (`get_best_target_l2`)

**Current behaviour:**
The fallback heuristic matches subfolder names by substring. `"support"` does not match any keyword, so the function falls through to `return approved_l2[0]` — an arbitrary first-approved fallback. When `get_best_target_l2` is called with `l1_name="tests"`, `approved_l2[0]` may resolve to `"support"`, causing agent files to be silently routed there.

**Required fix:**
Add a new helper `_calculate_subfolder_confidence(subfolder: str, file_name: str) -> float` and use it to block low-confidence placements. For agent files (`*Agent.py`), any subfolder that is not a source-code layer should return confidence `< 0.5` and the caller should fall through to archive rather than auto-relocate.

Concretely, guard the entry point:

```python
def get_best_target_l2(l1_name: str, item_name: str) -> str:
    # [FIX-3] Agent files must never be routed into non-source subfolders
    # Confidence guard: if confidence < 0.5, caller should archive instead.
    if item_name.endswith("Agent.py"):
        confidence = _calculate_subfolder_confidence_for_agent(l1_name, item_name)
        if confidence < 0.5:
            return "__ARCHIVE__"   # sentinel — callers must check and archive
    ...existing logic...
```

Add the helper:

```python
_AGENT_LOW_CONFIDENCE_ROOTS = frozenset({"tests", "docs", "data", "artifacts", "ops_scripts"})

def _calculate_subfolder_confidence_for_agent(l1_name: str, item_name: str) -> float:
    """Return placement confidence for an *Agent.py file into l1_name.

    < 0.5 → caller must NOT auto-relocate; archive instead.
    """
    if l1_name in _AGENT_LOW_CONFIDENCE_ROOTS:
        return 0.0
    # Any source layer is acceptable
    return 1.0
```

Callers of `get_best_target_l2` in `HierarchyAgent._relocate_file_to_l3` and `_relocate_file_to_l2` must check for the `"__ARCHIVE__"` sentinel and call `self.gatekeeper.safe_archive()` instead of moving.

---

## Gap 4 — SSOT `tests/support/` entry: missing `forbidden_patterns`

**File:** `c:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\_constants.py`
**Lines:** 1204–1206 (the `"support"` subfolder definition inside `territories["tests"]["subfolders"]`)

**Current behaviour:**
```python
"support": {
    "purpose": "Shared test infrastructure — base classes, helpers, shared fixtures",
},
```

No `forbidden_patterns` key means any file (including `*Agent.py`) is treated as permitted by the SSOT.

**Required fix:**
```python
"support": {
    "purpose": "Shared test infrastructure — base classes, helpers, shared fixtures",
    "forbidden_patterns": [r".*Agent\.py$"],
},
```

This makes `tests/support/` a hard-forbidden zone for `*Agent.py` files at the SSOT level, so that all downstream validators (`FilesystemSSOTReconcilerAgent`, `LocationValidatorAgent`) will reject placements without needing bespoke code.

---

## Invariant Tests Required

New file: `tests/architecture/test_hierarchy_agent_invariants.py`

| Test | Branch covered |
|---|---|
| `test_agent_file_in_approved_subfolder_raises_violation` | Fix 1 — non-test file inside approved subfolder is flagged |
| `test_infra_file_in_approved_subfolder_is_exempt` | Fix 1 — `conftest.py` inside `support/` is NOT flagged |
| `test_test_prefixed_file_in_approved_subfolder_is_clean` | Fix 1 — `test_foo.py` inside `support/` is clean |
| `test_block_agent_files_in_tests_root` | Fix 2 — `tests/SomeAgent.py` triggers violation, no move |
| `test_block_agent_files_in_tests_support` | Fix 2 — `tests/support/SomeAgent.py` triggers violation |
| `test_no_violation_when_tests_is_clean` | Fix 2 — clean `tests/` produces zero violations |
| `test_get_best_target_l2_agent_file_tests_root_returns_archive_sentinel` | Fix 3 — agent file → `tests` → `__ARCHIVE__` |
| `test_get_best_target_l2_agent_file_source_layer_returns_valid` | Fix 3 — agent file → `L5_safety` → valid subfolder |
| `test_get_best_target_l2_non_agent_file_tests_root_proceeds` | Fix 3 — non-agent file routing is unaffected |
| `test_ssot_support_has_forbidden_patterns` | Fix 4 — SSOT `tests/support/` contains `forbidden_patterns` |
| `test_ssot_support_forbidden_patterns_rejects_agent_py` | Fix 4 — pattern matches `FooAgent.py` |
| `test_ssot_support_forbidden_patterns_allows_test_file` | Fix 4 — pattern does NOT match `test_foo.py` |

---

## Execution Order

1. **Fix 4 first** (`_constants.py`) — SSOT is the foundation; all validators read from it.
2. **Fix 3** (`mission_utils_enforcer.py`) — guards the heuristic routing layer.
3. **Fix 2** (`HierarchyAgent._block_agent_files_in_tests`) — active scan guard.
4. **Fix 1** (`HierarchyAgent._enforce_tests_structure`) — detection tightening.
5. **Write tests** — all 12 invariant tests in one new file.
6. **Run `python -m pytest -q --color=no`** — full suite must pass.

---

## Files to Modify

| File | Change |
|---|---|
| `agentic_core/L5_safety/config/structure_blueprint/_constants.py` | Add `forbidden_patterns` to `tests/support/` |
| `agentic_core/L5_safety/enforcement/mission_utils_enforcer.py` | Add `_calculate_subfolder_confidence_for_agent`, guard `get_best_target_l2` |
| `agentic_core/L5_safety/reasoning/HierarchyAgent.py` | Fix `_enforce_tests_structure` skip; add `_block_agent_files_in_tests` |
| `tests/architecture/test_hierarchy_agent_invariants.py` | New — 12 invariant tests |

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

