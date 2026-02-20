# SSOT Heal Hardening — Phase 1 Evidence (Corrected)

## Problem Statement
SSOT heal runs were not repeatable due to four blocking defects:
1. `V15ExecutionGateway` import failed — `execution_gateway.py` was corrupted in HEAD, causing EXIT_CODE=1
2. `AGENTIC_CORE_DIFF_COUNT` measured working-tree dirty state, not run-introduced delta
3. `git` stderr warnings tripped `$ErrorActionPreference="Stop"` in PowerShell
4. 18 unintended CRLF→LF files were included in the Phase 1 commit

## Root Cause
- `execution_gateway.py` was corrupted with "TODO: Create abstraction layer" noise in the HEAD commit; restored from `3a7f34f9c`
- The PS1 runner used `git diff --name-only` (measures committed vs working tree) instead of `git status --porcelain=v1` before/after delta
- Git CRLF warnings go to stderr; under `$ErrorActionPreference="Stop"` PowerShell treats any stderr output as a terminating error
- The Phase 1 commit included 18 CRLF-only files that were not part of the intended scope

## Fixes Applied

### Wave 1 — Fix SSOT Run Exit Code
- Restored `agentic_core/L0_routing/enforcement/execution_gateway.py` from commit `3a7f34f9c` (clean version with `V15ExecutionGateway` class)
- Amended HEAD commit to remove the 18 CRLF-churn files; only 3 intended files remain in `agentic_core/`

### Wave 2 — True Run-Delta Measurement
Updated `docs/evidence/run_ssot_heal.ps1`:
- Capture `$baseDirty = @(git status --porcelain=v1 agentic_core/ 2>$null)` **before** python run
- Capture `$afterDirty = @(git status --porcelain=v1 agentic_core/ 2>$null)` **after** python run
- Compute `$newDirty` = paths in after but not in base
- Report `AGENTIC_CORE_DIRTY_BEFORE`, `AGENTIC_CORE_DIRTY_AFTER`, `AGENTIC_CORE_NEW_DIRTY_FROM_RUN_COUNT`
- All git metric calls use `2>$null` to suppress CRLF warnings from tripping `$ErrorActionPreference="Stop"`
- Embed an `agentic_core` filesystem fence into the temp python runner to prevent direct OS writes during SSOT heal runs

### Wave 3 — CRLF Churn Elimination + Proof
- Restored 18 CRLF-only files from `3a7f34f9c` and amended HEAD
- Verified `git status --porcelain=v1 agentic_core/` is empty before run

---

## Proof Command Outputs

### Guardian Test: test_ssot_no_self_mutation.py
```
python -m pytest -q -m guardian tests/guardian/test_ssot_no_self_mutation.py

============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
collected 12 items

tests/guardian/test_ssot_no_self_mutation.py::TestSourceRootFence::test_blocks_write_to_agentic_core PASSED
tests/guardian/test_ssot_no_self_mutation.py::TestSourceRootFence::test_allows_write_to_docs_evidence PASSED
tests/guardian/test_ssot_no_self_mutation.py::TestSourceRootFence::test_allows_write_when_fence_disabled PASSED
tests/guardian/test_ssot_no_self_mutation.py::TestSourceRootFence::test_blocks_move_to_agentic_core PASSED
tests/guardian/test_ssot_no_self_mutation.py::TestSourceRootFence::test_blocks_copy_to_tests PASSED
tests/guardian/test_ssot_no_self_mutation.py::TestSourceRootFence::test_blocks_remove_file_in_agentic_core PASSED
tests/guardian/test_ssot_no_self_mutation.py::TestSourceRootFence::test_blocks_remove_tree_in_tests PASSED
tests/guardian/test_ssot_no_self_mutation.py::TestSourceRootFence::test_blocks_touch_in_ops_scripts PASSED
tests/guardian/test_ssot_no_self_mutation.py::TestSourceRootFence::test_blocks_copy_tree_into_prompt_governance PASSED
tests/guardian/test_ssot_no_self_mutation.py::TestSourceRootFence::test_blocks_write_json_atomic_in_apps_shared PASSED
tests/guardian/test_ssot_no_self_mutation.py::TestSourceRootFence::test_verb_appears_in_error_message PASSED
tests/guardian/test_ssot_no_self_mutation.py::TestSourceRootFence::test_allows_runtime_state_json PASSED

GUARDIAN SHIELD: PASS — Violations: 0
12 passed in 0.09s
```

### Guardian Test: test_ssot_utf8_output.py
```
python -m pytest -q -m guardian tests/guardian/test_ssot_utf8_output.py

============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
collected 8 items

tests/guardian/test_ssot_utf8_output.py::TestMaybeForceUtf8Console::test_reconfigures_stdout_on_windows PASSED
tests/guardian/test_ssot_utf8_output.py::TestMaybeForceUtf8Console::test_reconfigures_on_non_windows_too PASSED
tests/guardian/test_ssot_utf8_output.py::TestMaybeForceUtf8Console::test_reconfigure_exception_is_swallowed PASSED
tests/guardian/test_ssot_utf8_output.py::TestMaybeForceUtf8LoggingHandlers::test_reconfigures_handler_stream_on_windows PASSED
tests/guardian/test_ssot_utf8_output.py::TestMaybeForceUtf8LoggingHandlers::test_reconfigures_on_non_windows_too PASSED
tests/guardian/test_ssot_utf8_output.py::TestMaybeForceUtf8LoggingHandlers::test_handler_without_stream_is_skipped PASSED
tests/guardian/test_ssot_utf8_output.py::TestMaybeForceUtf8LoggingHandlers::test_handler_reconfigure_exception_swallowed PASSED
tests/guardian/test_ssot_utf8_output.py::TestRuntimeStateEnsureAscii::test_json_dump_ensure_ascii_false_preserves_unicode PASSED

GUARDIAN SHIELD: PASS — Violations: 0
8 passed in 0.10s
```

### SSOT Heal Run: run_ssot_heal.ps1
```
powershell -ExecutionPolicy Bypass -File docs/evidence/run_ssot_heal.ps1

[RUN] Starting python (synchronous, 600s timeout)...
[RUN] Python exit code: 0  (518.90s)
runtime_state.run.json: COPIED

=== POST-FLIGHT METRICS ===
EXIT_CODE=0
RUNTIME_SECONDS=518.90
CHARMAP_COUNT=0
CREATE_ABSTRACTION_LAYER_COUNT=0
AGENTIC_CORE_DIRTY_BEFORE=0
AGENTIC_CORE_DIRTY_AFTER=0
AGENTIC_CORE_NEW_DIRTY_FROM_RUN_COUNT=0
```

### git status --porcelain=v1 agentic_core/ (before run)
```
(empty — working tree clean before run)
```

### runtime_state.run.json parse check
```
python -c "import json; json.load(open('docs/evidence/runtime_state.run.json',encoding='utf-8')); print('PARSE_OK')"
PARSE_OK
```

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| EXIT_CODE=0 | PASS |
| CHARMAP_COUNT=0 | PASS |
| CREATE_ABSTRACTION_LAYER_COUNT=0 | PASS |
| runtime_state.run.json PARSE_OK | PASS |
| Both guardian tests pass (20 total) | PASS |
| AGENTIC_CORE_DIRTY_BEFORE=0 | PASS |
| AGENTIC_CORE_NEW_DIRTY_FROM_RUN_COUNT=0 | PASS |

---

## Files Modified (Phase 1 + Defect Fix)

### Intentional agentic_core/ changes (3 files):
- `agentic_core/L2_execution/tools/write_gateway.py` — comprehensive no-self-mutation fence
- `agentic_core/L0_routing/scripts/execute_ssot.py` — unconditional UTF-8 reconfiguration + ensure_ascii=False
- `agentic_core/L0_routing/enforcement/execution_gateway.py` — restored from 3a7f34f9c (was corrupted)

### Runner and tests:
- `docs/evidence/run_ssot_heal.ps1` — synchronous, before/after delta metrics, 2>$null on git calls
- `tests/guardian/test_ssot_no_self_mutation.py` — extended to 12 tests covering all fenced helpers
- `tests/guardian/test_ssot_utf8_output.py` — updated for unconditional UTF-8 (non-Windows too)
- `docs/evidence/SSOT_HEAL_HARDENING_PHASE1.md` — this file

---

## Commit Hash
`7b562c0dd57b441213328b3bf49100269efce867` (amended — CRLF churn removed)
