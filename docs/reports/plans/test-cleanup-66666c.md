# tests/ Cleanup Plan — Current Repository State Analysis

Clean up the test directory based on current repository state, removing broken imports, fixing pytest configuration, and adding uncollected valid test directories.

---

## Executive Summary

| Category | Files | Action |
|---|---|---|
| Broken-import test files | 18 | DELETE or EXCLUDE |
| pytest.ini dead testpaths | 1 entry | FIX config |
| pytest.ini empty subdir | 1 entry | FIX config |
| Uncollected valid dirs | 5 dirs | ADD to testpaths |
| External dependency dirs | 4 dirs | KEEP EXCLUDED |

---

## Section 1 — Broken Import Files (18 total)

### Files with external dependencies (keep but mark for exclusion):
- `e2e/test_dashboard_e2e.py` - playwright dependency
- `e2e/test_e2e.py` - playwright dependency
- `e2e/test_full_mock_isolation.py` - requests dependency
- `e2e/test_gemini_qwen_e2e.py` - requests, httpx dependencies
- `e2e/test_user_flow_e2e.py` - playwright dependency
- `integration/test_inspector_agents_runtime.py` - pydantic dependency
- `unit/test_apps_integration.py` - asyncio dependency
- `unit/test_unified_agent_performance.py` - asyncio dependency
- `unit/test_execute_ssot_debt_removal.py` - numpy dependency
- `unit/agentic_core/L2_execution/types/test_agent_output_contract.py` - pydantic dependency
- `system_learning/test_embedding_service_factory.py` - numpy dependency
- `system_learning/test_embedding_sovereignty.py` - numpy dependency
- `system_learning/test_gap_fixes.py` - numpy dependency
- `system_learning/test_stack_invariants.py` - numpy, faiss dependencies

### Files with standard library missing from STD_LIB (fix STD_LIB):
- `governance/test_req414_egress_guard.py` - asyncio (stdlib)
- `governance/test_req_p2_promotion_token_single_use.py` - secrets (stdlib)
- `integration/test_imports_no_mro_error.py` - py_compile (stdlib)
- `misc/test_parity_strict.py` - asyncio (stdlib)

**Action:** Add missing stdlib modules to STD_LIB set, keep external dependency files excluded.

---

## Section 2 — pytest.ini Configuration Issues

### Dead testpaths:
- `tests/enforcement` - directory does not exist

### Empty subdir testpaths:
- `tests/integration/agentic_core` - exists but has 0 test files (actual tests are in `tests/integration/`)

### Wrong ignore path:
- Current: `--ignore=tests/integration/agentic_core/test_imports_no_mro_error.py`
- Actual file is at: `tests/integration/test_imports_no_mro_error.py`

---

## Section 3 — Uncollected Valid Directories

### Should be added to testpaths (valid imports):
| Directory | Files | Status |
|---|---|---|
| `tests/ci` | 1 | Sovereignty attack suite |
| `tests/evaluation` | 9 | Valid agentic_core.evaluation imports |
| `tests/guardian` | 64 | Architecture guard tests |
| `tests/ssot_equivalence` | 2 | Pure structural tests |
| `tests/stress` | 1 | Atomic concurrency tests |

### Keep excluded (external deps):
| Directory | Files | Reason |
|---|---|---|
| `tests/e2e` | 10 | Playwright/requests deps |
| `tests/integration_full_deps` | 1 | Full-dep environment |
| `tests/misc` | 7 | Mixed external deps |
| `tests/performance` | 1 | External deps likely |

---

## Section 4 — Empty Directories

- `tests/helpers` - 1 test file (keep)
- No completely empty test directories found

---

## Execution Order

1. **Fix pytest.ini**:
   - Remove `tests/enforcement` from testpaths
   - Change `tests/integration/agentic_core` to `tests/integration`
   - Update ignore path to `tests/integration/test_imports_no_mro_error.py`

2. **Add valid directories to testpaths**:
   - `tests/ci`
   - `tests/evaluation`
   - `tests/guardian`
   - `tests/ssot_equivalence`
   - `tests/stress`

3. **Update STD_LIB** in analysis tools to include:
   - `asyncio`
   - `secrets`
   - `py_compile`

4. **Run test collection** to verify:
   - No broken import errors for stdlib modules
   - New directories are collected
   - External dependency dirs remain excluded

---

## Impact Estimate

| Action | Result |
|---|---|
| Fix pytest.ini config | Cleaner test discovery |
| Add 5 valid directories | +~77 tests collected |
| Fix stdlib detection | -4 false broken imports |
| Keep external deps excluded | CI stability maintained |

**Net effect: +~77 tests properly collected, cleaner configuration, no broken import false positives.**
