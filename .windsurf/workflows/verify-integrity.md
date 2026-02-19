---
description: Run pytest collection + execution reconciliation, verify no new executables, STOP on discrepancy
---

# Verify Integrity Workflow

## Step 1 — Pytest Collection + Execution (when tests are in scope)

```powershell
$E = "docs/reports/plans/<phase_evidence_file>.md"
pytest --collect-only -q 2>&1 | Tee-Object -FilePath $E -Append
pytest -q 2>&1 | Tee-Object -FilePath $E -Append
```

See skill: `pytest-integrity/collection_vs_execution_protocol.md`

Record:
- Collected: N items
- Executed: X passed, Y failed
- Deselected: D items (if any — must be explained)

If collected != executed + failed + error (unexplained): STOP.
See skill: `pytest-integrity/conftest_hook_audit.md`

## Step 2 — Verify No New Executables

```powershell
git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
```

Scan output for any new `.py`, `.sh`, `.ps1`, `.bat` files whose names match:
`run_*`, `*_runner`, `tmp_*`, `scratch_*`, `invoke_*`, `launch_*`

If any found → STOP. Document in evidence. Do NOT commit.

## Step 3 — Pre-Commit

```powershell
pre-commit run --all-files 2>&1 | Tee-Object -FilePath $E -Append
```

## Pass Criteria

- Collected vs executed counts reconciled (or mismatch documented with explanation).
- No new runner/wrapper executables in diff.
- Pre-commit passes on default-stage hooks.

## STOP

Record result in evidence. STOP. Return to calling workflow.
