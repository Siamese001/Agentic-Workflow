# Pre-Phase Checkpoint

Execute BEFORE any phase touching more than 3 files begins.
Phase MUST NOT start until this checkpoint is complete and recorded in evidence.

---

## Step 1 — Record Baseline Commit Hash

```python
import subprocess
result = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    capture_output=True, text=True, encoding="utf-8"
)
baseline_hash = result.stdout.strip()
print(f"BASELINE: {baseline_hash}")
```

Record as: `BASELINE_HASH = <hash>`

---

## Step 2 — Capture Baseline Dirty Files

```python
import subprocess
result = subprocess.run(
    ["git", "diff", "--name-only", "HEAD"],
    capture_output=True, text=True, encoding="utf-8"
)
print(result.stdout or "(clean — no dirty files)")
```

Record output. These are pre-existing dirty files NOT part of this phase.

---

## Step 3 — Declare Rollback Command

Write the exact rollback command in evidence NOW, before any edits:

```
ROLLBACK COMMAND (execute if phase fails):
  git reset --hard <BASELINE_HASH>
```

This command MUST appear in evidence BEFORE any file is touched.

---

## Step 4 — Declare Acceptance Criteria

List the specific, verifiable conditions that must ALL pass before committing:

```
ACCEPTANCE CRITERIA (all must pass to commit):
  [ ] pytest <specific_test_path> exits 0
  [ ] git diff --name-only HEAD matches declared scope exactly
  [ ] ruff check <changed_files> exits 0
  [ ] <any other phase-specific criterion>
```

Be specific. "Tests pass" is not sufficient — name the exact test paths.

---

## Step 5 — Evidence Header Block

Paste this block at the top of the phase evidence file:

```markdown
## PHASE_CHECKPOINT

- Phase: <phase_name>
- Started: <timestamp>
- Baseline hash: <BASELINE_HASH>
- Rollback command: `git reset --hard <BASELINE_HASH>`
- Files in declared scope: <N>
- Dirty files at baseline: <list or "none">

### Acceptance Criteria
- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] <criterion 3>
```

---

## STOP Conditions

| Condition | Action |
|-----------|--------|
| Baseline hash not recorded | STOP — record it before any edit |
| Rollback command not in evidence | STOP — write it before any edit |
| Acceptance criteria not defined | STOP — define them before any edit |
| Phase scope > 10 files | Split into sub-phases, each with own checkpoint |
