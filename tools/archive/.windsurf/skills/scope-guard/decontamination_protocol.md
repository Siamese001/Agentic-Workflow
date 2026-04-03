# Scope Decontamination Protocol

Execute when `git diff --name-only HEAD` contains files outside declared scope.

## Step 1 — Document Unexpected Files

Record all unexpected files in evidence before touching anything:

```powershell
$E = "docs/reports/plans/<phase_evidence_file>.md"
git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
```

List each unexpected file with reason it appeared.

## Step 2 — Reset to Clean Baseline

```powershell
git reset --hard <baseline_commit_hash> 2>&1 | Tee-Object -FilePath $E -Append
```

Replace `<baseline_commit_hash>` with the last known clean commit (e.g., HEAD before edits,
or the phase start commit recorded in evidence).

## Step 3 — Restore Only Declared Scope Files

```powershell
git checkout <target_branch_or_commit> -- path/to/declared_file1 `
    path/to/declared_file2 2>&1 | Tee-Object -FilePath $E -Append
```

Only restore files explicitly listed in the phase scope declaration.

## Step 4 — Verify Clean Scope

```powershell
git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
```

Output MUST contain only declared scope files. If any unexpected file remains → repeat
from Step 2.

## Step 5 — Document in Evidence

Record in evidence file:
- List of all unexpected files found
- Reason each appeared
- Confirmation that reset was executed
- Final `git diff --name-only HEAD` output showing clean scope

## MANDATORY STOP

After decontamination completes → STOP.
Do NOT commit. Do NOT proceed to next phase.
Produce a Phase Revision artifact (`scope_expansion_revision_template.md`) before continuing.
