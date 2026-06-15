# Old L5 Agent Wave 5 Closeout

Plan: `old-l5-agent-retirement-a94f6c`
Date: 2026-06-15

## Results

W1, W2, W3, and W5 are complete. W4 physical archive/delete is blocked by the manifest gate.

## Verification

| Check | Result |
|---|---|
| Focused Old L5 utility migration tests | 18 passed, 20 skipped |
| Safety seam hardening tests | 35 passed |
| Manifest refresh | Passed |
| Manifest summary after refresh | 72 candidates, 21 authorized, 0 eligible for archive on 2026-06-15 |
| JSON parse: manifest, author-gate receipt, lazy seam allowlist | Passed |
| `git diff --check` | Passed with line-ending normalization warnings only |

## Residual Blockers

| Blocker | Disposition |
|---|---|
| W4 physical archive/delete | Blocked until 2026-07-23 for already-authorized candidates, plus zero-live-consumer proof |
| `ops_scripts/dev_tools/l0_scripts/rename_unified_agents_util.py` generated `new_init` string | Deferred to W3 helper-parity split because it still expects legacy factory helpers |
| Large facades | Split to replacement-proof work; `FileClassificationAgent.py` is the first critical slice and must not be modernized in place |
| 45 unclassified old L5 files | Deprecation-authorized; deletion deferred to per-file caller and replacement proof |

## Files Changed By W1

- `tests/unit/agentic_core/L5_safety/reasoning/test_CodeDetectorAgent.py`
- `tests/unit/agentic_core/L5_safety/reasoning/test_CodeEnforcerAgent.py`
- `tests/unit/agentic_core/L5_safety/reasoning/test_CodeJanitorAgent.py`
- `tests/unit/agentic_core/L5_safety/reasoning/test_CodeValidatorAgent.py`
- `agentic_core/L5_safety/validators/CodeJanitorAgent.py`
- `agentic_core/seams/contracts/safety_agents.py`
- `tests/integration/critical_modules.txt`
- `tests/integration/agentic_core/test_depth_violation_no_archive_invariant.py`
- `agentic_core/L5_safety/enforcement/governance/lazy_seam_allowlist.json`

## No-Delete Statement

No Old L5 candidate file was physically archived or deleted in this wave run.
