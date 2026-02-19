---
description: Audit current git diff against declared phase scope; trigger decontamination if mismatch
---

# Scope Audit Workflow

## Step 1 — Capture Current Diff

```powershell
$E = "docs/reports/plans/<phase_evidence_file>.md"
git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
```

## Step 2 — Compare to Declared Scope

Compare output to the declared file list in the phase evidence file.

Pass condition: every file in `git diff --name-only HEAD` is in the declared scope list.

## Step 3 — Branch on Result

**If diff matches declared scope exactly:**
- Record "Scope audit PASSED" in evidence.
- STOP. Return to calling workflow.

**If diff contains files outside declared scope:**
- Record all unexpected files in evidence.
- Call `scope-decontaminate` workflow.
- STOP. Do not commit.

## STOP

This workflow always ends with STOP after recording its result.
