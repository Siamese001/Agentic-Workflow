# Collection vs Execution Protocol

Run BOTH commands every time pytest is part of phase acceptance. Record both outputs.

## Required Commands

```powershell
$E = "docs/reports/plans/<phase_evidence_file>.md"

# Step 1: Collection
pytest --collect-only -q 2>&1 | Tee-Object -FilePath $E -Append

# Step 2: Execution
pytest -q 2>&1 | Tee-Object -FilePath $E -Append
```

## Required Recording

After both runs, record in evidence:

```
Collected:  <N> items
Executed:   <X> passed, <Y> failed, <Z> error
Deselected: <D> items (if any)
```

## STOP Conditions

- **Collected > Executed + Failed + Error**: unexplained deselection → STOP.
  - Inspect conftest hooks: see `conftest_hook_audit.md`.
  - Do NOT proceed until mismatch is explained and documented.

- **"no tests ran"**: AUTOMATIC FAIL regardless of collection count.
  - Do NOT claim phase passes.

- **Collected = 0**: verify `pytest.ini` testpaths and that test files exist.

## Allowed Scope Narrowing

Narrowing pytest scope (e.g., `pytest -xvv tests/governance/`) is allowed ONLY when:
- Phase acceptance criteria explicitly specifies the narrower scope.
- Evidence documents the narrowing and its justification.
- Full suite status is still recorded separately (even if pre-existing failures exist).
