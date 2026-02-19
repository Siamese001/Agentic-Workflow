# Scope Pre-Check

Run BEFORE any edits. Failure to complete this block → phase MUST NOT proceed.

## Step 1 — Declare Planned File List

List every file that will be modified/created. No wildcards.

```
Declared scope (N = _):
1. path/to/file1.py   [intent: replace lines X-Y]
2. path/to/file2.py   [intent: add function Z]
...
```

## Step 2 — Capture Pre-Change Diff

```powershell
$E = "docs/reports/plans/<phase_evidence_file>.md"
git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
```

Record the output. This is the baseline dirty-file set (pre-existing, not this phase).

## Step 3 — Verify N After Edits

After edits, run:

```powershell
git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
```

Compare to declared scope:
- New files in diff that are NOT in declared scope → STOP immediately.
- Execute Decontamination Protocol (`decontamination_protocol.md`).
- Do NOT commit until scope matches declaration.

## STOP Conditions

| Condition | Action |
|-----------|--------|
| Modified files exceed N | STOP → Decontaminate → Revise plan |
| File outside declared scope appears | STOP → Decontaminate |
| Unrelated pre-existing file staged | STOP → Unstage → Document |
