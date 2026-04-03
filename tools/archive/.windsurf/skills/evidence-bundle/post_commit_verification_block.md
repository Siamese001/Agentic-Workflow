# Post-Commit Verification Block

Deterministic minimal verification. Run after every commit. Capture all outputs.

## Commands (copy-pasteable)

```powershell
$E = ".windsurf/plans/<phase_evidence_file>.md"

git status --porcelain 2>&1 | Tee-Object -FilePath $E -Append
git show --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
git show --stat HEAD 2>&1 | Tee-Object -FilePath $E -Append
pytest -q 2>&1 | Tee-Object -FilePath $E -Append
```

## Pass Criteria

- `git status --porcelain` → empty (clean working tree)
- `git show --name-only HEAD` → matches declared scope exactly
- `git show --stat HEAD` → recorded in evidence
- `pytest -q` → 0 failed (or pre-existing failures explicitly classified)

## Failure Protocol

- Any post-commit failure → STOP immediately.
- Do NOT proceed to next phase.
- Document failure root cause in evidence file.
- Remediate and re-run this block before continuing.
