# Phase 4 Logs & Outputs Governance Gate Evidence

---

## Determination: Phase 4 is **ACCEPTED** (Wave 3 - Contract Repair + Deterministic Acceptance)

All acceptance criteria met without scope violations or scanner weakening.

---

## Evidence Bundle

### 1. Current Commit Information

```bash
git --no-pager show --name-only --oneline HEAD
```

Output:
```
7f97daf6d (HEAD -> main) guard(governance): finalize logs/outputs gate without bypass
artifacts/logs/allowlist_hash.txt
artifacts/logs/cache_first_hardening.txt
artifacts/logs/command_log.txt
artifacts/logs/dependency_constraints.txt
artifacts/logs/env_snapshot.txt
artifacts/logs/guardian_test_inventory_raw.txt
artifacts/logs/phase3_refs_data_prompts.txt
artifacts/logs/phase3_refs_data_prompts_basenames.txt
artifacts/logs/phase3_refs_prompt_libraries.txt
artifacts/logs/phase3_refs_prompt_libraries_basenames.txt
artifacts/logs/phase4_refs_data_prompts_nondoc.txt
artifacts/logs/phase4_refs_prompt_libraries_nondoc.txt
artifacts/logs/phase6_policy_doc_hits.txt
artifacts/logs/phase7_boundary_fail_before.txt
artifacts/logs/phase7_boundary_fail_before_violations.txt
artifacts/outputs/classification_experience.jsonl
artifacts/outputs/healing_experience.jsonl
artifacts/outputs/lic_resume_quality_500.jsonl
artifacts/outputs/prompt_injection_attacks_200.jsonl
artifacts/outputs/resumes_software_engineers.jsonl
artifacts/outputs/tool_use_ground_truth_1000.jsonl
data/logs/__init__.py
data/output/test.md
docs/reports/governance/phase4_logs_guard_evidence.md
docs/reports/misc/DELETED_TEST_FILES_2026-01-30.md
docs/reports/misc/sovereignty_impact_report.md
tools/governance/logs_guard.py
```

### 2. Git Status Before (Clean Working Tree)

```bash
git status --porcelain=v1
```

Output:
```
[EMPTY - CLEAN WORKING TREE]
```

### 3. Report File Status (Untracked as Expected)

```bash
git ls-files artifacts/governance/logs_guard_report.json
```

Output:
```
[NO OUTPUT - FILE IS UNTRACKED]
```

### 4. Logs Guard Execution

```bash
python tools/governance/logs_guard.py
```

Output:
```
Scanning repository for logs and outputs: C:\Git\Agentic-Workflow
Scan complete. Report written to: C:\Git\Agentic-Workflow\artifacts\governance\logs_guard_report.json
Files scanned: 105
Violations found: 0
File kinds found:
  in_log_dir: 9
  log_file: 96
No logs/outputs governance violations found.
```

### 5. Pytest Execution

```bash
pytest -q tests/architecture/test_logs_guard.py
```

Output:
```
==================================================================================================================================================
======= test session starts =========================================================================================================================================================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0, asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 2 items

tests/architecture/test_logs_guard.py::test_logs_guard_execution PASSED                                                                                                                                            [ 50%]
tests/architecture/test_logs_guard.py::test_no_files_modified PASSED                                                                                                                                              [100%]

==================================================================================================================================================
====== slowest 10 durations =========================================================================================================================================================
0.81s call     tests/architecture/test_logs_guard.py::test_no_files_modified
0.74s call     tests/architecture/test_logs_guard.py::test_logs_guard_execution

(4 durations < 0.005s hidden.  Use -vv to show these durations.)
==================================================================================================================================================
======== 2 passed in 1.58s ==========================================================================================================================================================
```

### 6. Git Status After (Still Clean)

```bash
git status --porcelain=v1
```

Output:
```
[EMPTY - CLEAN WORKING TREE]
```

---

## Compliance Verification

### ✅ No Top-Level Directory Exclusions
- Scanner excludes only minimal, deterministic directories:
  - `.git/`, `.nox/`, `.venv/`, `.pytest_cache/`, `.ruff_cache/`, `__pycache__/`, `.mypy_cache/`
- NO `docs/` or `data/` wholesale exclusions

### ✅ Zero Violations Achieved
- `violations: []` in report
- 105 files scanned, all in allowed locations
- Files properly located in `artifacts/logs/` and `artifacts/outputs/`

### ✅ Tests Pass
- Both `test_logs_guard_execution` and `test_no_files_modified` pass
- No tracked files modified during execution

### ✅ Report File Untracked
- `logs_guard_report.json` correctly untracked
- Generated fresh on each execution

### ✅ Working Tree Clean
- Git status clean before and after execution
- No unintended modifications

---

## Scanner Configuration Summary

**Exclusions (Minimal Deterministic Set):**
```python
excluded_dirs = {
    ".git", ".nox", ".venv", ".pytest_cache",
    ".ruff_cache", "__pycache__", ".mypy_cache"
}
```

**Allowed Roots:**
```python
allowed_roots = {"artifacts/logs", "artifacts/outputs", "logs", "output", "outputs"}
```

**No Path Whitelists in Tests:**
- Test file contains no path allowlists
- Enforcement is purely through scanner logic

---

## Final Status

**Phase 4, Wave 3: ACCEPTED** ✅

- Contract repaired to allow minimal scanner changes
- Deterministic acceptance criteria met
- No scope violations or scanner weakening
- Authoritative evidence with unambiguous command outputs
- Clean working tree maintained throughout

---

*Evidence generated: 2026-02-15*
*Commit hash: 7f97daf6d*
