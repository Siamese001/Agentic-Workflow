# tests/ Cleanup Plan — AST Dead-Code Analysis (Regenerated)

Prune stale, duplicate, and orphaned test files identified via full AST + import-resolution scan across all 739 test files in `tests/`.

---

## Executive Summary

| Category | Files | Action |
|---|---|---|
| Exact duplicate flat↔nested unit/ files | 103 | DELETE nested copies |
| Broken-import governance tests (modules never existed) | 9 | DELETE |
| Broken-import unit_min_deps tests | 3 | DELETE |
| Broken-import helpers test | 1 | DELETE |
| pytest.ini dead testpaths | 2 entries | FIX config |
| Uncollected valid dirs | 5 dirs | ADD to testpaths |

---

## Section 1 — DEFINITE DELETES

### 1A. `unit/agentic_core/` — 103 exact-copy duplicates

Every file in `unit/agentic_core/**/test_X.py` is an MD5-identical copy of a flat `unit/test_X.py` file. Both are under the `tests/unit` testpath → pytest runs each test **twice**.

**Action: delete the 103 nested copies under `tests/unit/agentic_core/` that are exact mirrors of flat `tests/unit/*.py` files.**

**4 pairs have different content — manual review:**
- `unit/test_FileClassificationAgent.py` vs `unit/agentic_core/L5_safety/reasoning/test_FileClassificationAgent.py`
- `unit/test_instruction_packet.py` vs `unit/agentic_core/L2_execution/types/test_instruction_packet.py`
- `unit/test_ptc_contract_enforcement.py` vs `unit/agentic_core/L2_execution/tools/test_ptc_contract_enforcement.py`
- `unit/test_sandbox_envelope.py` vs `unit/agentic_core/L2_execution/types/test_sandbox_envelope.py`

### 1B. `governance/` — 9 tests with permanently broken imports

These import top-level modules that **do not exist** anywhere in the repo. They can never collect.

| File | Broken import(s) |
|---|---|
| `governance/test_req_p2_activation_flags_persistence.py` | `activation_flags` |
| `governance/test_req_p2_blast_radius_containment.py` | `blast_radius` |
| `governance/test_req_p2_metrics_emission.py` | `blast_radius`, `metrics_emission` |
| `governance/test_req_p2_promotion_capability_scope.py` | `promotion_token` |
| `governance/test_req_p2_promotion_gateway_authority.py` | `promotion_authority`, `promotion_token`, `UniversalWriteGateway` |
| `governance/test_req_p2_promotion_token_single_use.py` | `promotion_token` |
| `governance/test_req_p2_promotion_token_time_bounded.py` | `promotion_token` |
| `governance/test_req142_267_seam_audit_determinism.py` | `seam_audit` |
| `governance/test_req375_phase_lock_persistence.py` | `phase_lock_store` |

**Action: delete all 9 files above.**

### 1C. `unit_min_deps/` — 3 tests with broken imports

| File | Broken import |
|---|---|
| `unit_min_deps/test_contract_gates.py` | `run_contract_gates` |
| `unit_min_deps/test_evidence_contract_v2.py` | `evidence_contract_v2` |
| `unit_min_deps/test_tooling_apps_boundary.py` | `check_tooling_apps_boundary` |

**Action: delete all 3.**

### 1D. `helpers/test_robust_fs.py` — 1 file with broken import

Imports `robust_fs` which does not exist anywhere in the repo.

**Action: delete.**

---

## Section 2 — NEVER COLLECTED (not in pytest.ini testpaths)

These directories have valid test files but are **silently ignored** by pytest.

### 2A. Recommend adding to testpaths (valid imports, meaningful tests):

| Directory | Files | Notes |
|---|---|---|
| `tests/guardian/` | 64 | Imports `agentic_core` + valid `ops_scripts.*`. Architecture/governance guard tests. |
| `tests/ci/` | 1 (27 test fns) | Sovereignty attack suite. All imports valid. |
| `tests/evaluation/` | 9 | All import valid `agentic_core.evaluation.*` submodules. |
| `tests/ssot_equivalence/` | 2 | Import `pathlib` only, pure structural tests. |
| `tests/stress/test_atomic_concurrency.py` | 1 | 7 test functions, valid imports. |

**Action: add these 5 directories to `testpaths` in `pytest.ini`.**

### 2B. Needs triage before wiring (external deps or unclear status):

| Directory | Files | Issue |
|---|---|---|
| `tests/e2e/` | 12 | `test_dashboard_e2e.py` requires psutil+playwright; `test_e2e.py`, `test_user_flow_e2e.py` require playwright. |
| `tests/misc/` | 7 | Mixed: some valid pure-Python, some require live infra. |
| `tests/performance/` | 1 | Unclear if deterministic for CI. |
| `tests/integration_full_deps/` | 1 | Designed for full-dep environment; already excluded by design. |

---

## Section 3 — pytest.ini Config Fixes

| Issue | Fix |
|---|---|
| `tests/enforcement` in testpaths — directory **does not exist** | Remove from `testpaths` |
| `tests/integration/agentic_core` in testpaths — that subdir is **empty**; actual test files are in `tests/integration/` | Change to `tests/integration` |
| `--ignore=tests/integration/agentic_core/test_imports_no_mro_error.py` — path is wrong (file is at `tests/integration/test_imports_no_mro_error.py`) | Update ignore path |

---

## Section 4 — Empty Directories (no test files)

- `tests/scripts/` — 0 test files — **delete directory**
- `tests/snapshots/` — 0 test files — **delete directory**
- `tests/support/` — 0 test files — **delete directory**

---

## Execution Order

1. **Delete** Section 1B (9 governance broken-import files)
2. **Delete** Section 1C (3 unit_min_deps broken-import files)
3. **Delete** Section 1D+1E (2 helper/unit broken-import files)
4. **Delete** Section 1A nested duplicates (103 exact-copy files under `unit/agentic_core/`)
   - Manual review of 4 diff-content pairs first
5. **Fix pytest.ini** testpaths + ignore path (Section 3)
6. **Add** guardian + ci + evaluation + ssot_equivalence + stress to testpaths (Section 2A)
7. **Delete** empty dirs: `tests/scripts/`, `tests/snapshots/`, `tests/support/`
8. **Run full suite** and verify collected/executed counts match expectations

---

## Impact Estimate

| Action | Files removed | Tests eliminated (dupe) |
|---|---|---|
| Delete nested exact dupes | 103 | ~103 × avg 8 fns = ~820 test runs saved per suite |
| Delete broken-import files | 14 | 0 (they fail to collect anyway) |
| Add uncollected valid dirs | +5 dirs | +~100 tests newly enforced |

**Net effect: ~820 fewer redundant test executions, ~100 new tests enforced, cleaner test surface.**
