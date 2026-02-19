---
description: Execute scope decontamination — reset to baseline, restore only declared files, produce plan artifact
---

# Scope Decontaminate Workflow

Triggered when `scope-audit` detects files outside declared scope.

## Step 1 — Document Unexpected Files

Before touching anything, record all unexpected files in evidence:

```powershell
$E = "docs/reports/plans/<phase_evidence_file>.md"
git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
```

## Step 2 — Execute Decontamination

Follow the full protocol:
See skill: `scope-guard/decontamination_protocol.md`

```powershell
# Reset to clean baseline
git reset --hard <baseline_commit_hash> 2>&1 | Tee-Object -FilePath $E -Append

# Restore only declared scope files
git checkout <target> -- <declared_file1> <declared_file2> 2>&1 | Tee-Object -FilePath $E -Append

# Verify clean scope
git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
```

## Step 3 — Produce Plan-Only Artifact

Create a Phase Revision artifact using:
See skill: `scope-guard/scope_expansion_revision_template.md`

Save to: `docs/reports/plans/<phase_name>_scope_revision.md`

Record in evidence:
- All unexpected files found
- Decontamination steps executed
- Final clean scope confirmation
- Path to Phase Revision artifact

## STOP

Do NOT commit after decontamination.
Do NOT proceed to next phase.
Await revised phase plan before continuing.
