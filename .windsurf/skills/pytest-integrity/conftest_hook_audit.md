# Conftest Hook Audit

Trigger: collected count does not match executed count in pytest output.

## Step 1 — Identify Active conftest.py Files

```powershell
Get-ChildItem -Recurse -Filter conftest.py | Select-Object FullName
```

## Step 2 — Inspect for `pytest_collection_modifyitems`

```powershell
Select-String -Path (Get-ChildItem -Recurse -Filter conftest.py) `
    -Pattern "pytest_collection_modifyitems" | Select-Object Path, LineNumber, Line
```

## Step 3 — Document Marker Filtering Logic

For each hook found, record in evidence:
- File path and line number
- What markers are used to deselect tests
- What the default selected set is
- Whether the hook logs deselected count

## Step 4 — Verify Marker Registration

```powershell
# Check pytest.ini markers section
Select-String -Path pytest.ini -Pattern "markers"
```

All markers used in conftest hooks MUST be registered in `pytest.ini`.
Unregistered markers with `--strict-markers` → collection error.

## Step 5 — Reconcile Counts

```powershell
$E = "docs/reports/plans/<phase_evidence_file>.md"
pytest --collect-only -q 2>&1 | Tee-Object -FilePath $E -Append
pytest -q 2>&1 | Tee-Object -FilePath $E -Append
```

Record:
- Collected: N items
- Deselected by hook: D items (from hook log or inference)
- Executed: N - D items
- If N - D does not match executed count → escalate, do NOT guess.

## STOP Condition

If mismatch cannot be explained by documented hook logic → STOP.
Do NOT modify conftest or pytest.ini without a new phase plan.
