# Phase N / Wave N — [Short Description]

## 1. Phase/Wave Header

- **Phase**: N
- **Wave**: N/total
- **Branch**: `<output of: git branch --show-current>`
- **Objective**: One sentence.

---

## 2. Scope Declaration

Declared files (exact paths, no wildcards):

| # | Path | Intent (add/remove/replace) |
|---|------|-----------------------------|
| 1 | `path/to/file.py` | replace lines 10-20 |

**N (planned file count)**: _

Guardrails confirmed:
- [ ] No runner scripts added anywhere in repo.
- [ ] No changes to `.windsurfrules`.
- [ ] No changes to tooling configs (`.vscode`, `markdownlint`, CI, pre-commit).

---

## 3. Pre-Change Diff Snapshot

### Command
```powershell
$E = "docs/reports/plans/<this_file>.md"
git diff --name-only HEAD | Tee-Object -FilePath $E -Append
```

### Raw Output
```
<paste verbatim>
```

---

## 4. Commands Executed

All commands captured via:
```powershell
<command> 2>&1 | Tee-Object -FilePath $E -Append
```

List each command in execution order:

```powershell
# Example:
python agentic_core/L5_safety/enforcement/system.py 2>&1 | Tee-Object -FilePath $E -Append
python -m agentic_core.L5_safety.enforcement.system 2>&1 | Tee-Object -FilePath $E -Append
pytest -xvv tests/governance/ 2>&1 | Tee-Object -FilePath $E -Append
pre-commit run --all-files 2>&1 | Tee-Object -FilePath $E -Append
git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
git show --stat 2>&1 | Tee-Object -FilePath $E -Append
```

---

## 5. Raw Outputs (NO TRUNCATION)

### [Command 1 label]
```
<verbatim output — no "..." truncation>
```

### [Command 2 label]
```
<verbatim output — no "..." truncation>
```

Exit codes MUST be visible. Include `$LASTEXITCODE` or `$?` after each command.

---

## 6. Post-Commit Verification Block

See skill: `scope-guard/post_commit_verification_block.md`

### Commands
```powershell
git status --porcelain 2>&1 | Tee-Object -FilePath $E -Append
git show --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
git show --stat HEAD 2>&1 | Tee-Object -FilePath $E -Append
```

### Raw Output
```
<verbatim>
```

**Commit hash**: `<hash>`
**Files in commit**: must match declared scope exactly.
**Working tree clean**: YES / NO (if NO — STOP, do not proceed to next phase)

---

## Evidence Authoritative Rules

- Evidence is authoritative. No claims without raw output.
- No "..." truncation within evidence scope.
- Claims like "pre-commit passes" MUST include actual pre-commit output.
- Any mismatch between claimed and actual results → IMMEDIATE FAIL.
