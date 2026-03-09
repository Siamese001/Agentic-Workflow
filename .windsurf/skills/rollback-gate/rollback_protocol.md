# Rollback Protocol

Execute IMMEDIATELY when any acceptance criterion fails after a phase.
No partial commits. No "we'll fix it next phase."

---

## Trigger Conditions

Execute this protocol when ANY of the following occur:

- pytest exits non-zero after phase edits
- `git diff --name-only HEAD` contains files outside declared scope
- `ruff check` reports errors in changed files
- Imports fail to resolve in changed modules
- Any acceptance criterion declared in `pre_phase_checkpoint.md` is not met

---

## Step 1 — STOP All Further Edits

Do not touch any additional files.
Do not attempt to "fix forward."
Record the failure in evidence immediately.

```
PHASE VALIDATION FAILURE:
  Criterion failed: <which criterion>
  Error output: <exact error message>
  Time of failure: <timestamp>
  Files changed at time of failure:
    <git diff --name-only HEAD output>
```

---

## Step 2 — Execute Rollback

Use the BASELINE_HASH recorded in `pre_phase_checkpoint.md`:

```python
import subprocess

BASELINE_HASH = "<hash_from_checkpoint>"

result = subprocess.run(
    ["git", "reset", "--hard", BASELINE_HASH],
    capture_output=True, text=True, encoding="utf-8"
)
print(result.stdout)
print(result.stderr)
```

---

## Step 3 — Verify Clean State

Confirm rollback succeeded:

```python
import subprocess

# Verify HEAD is back to baseline
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
print(f"HEAD after rollback: {head.stdout.strip()}")

# Verify no unexpected dirty files
dirty = subprocess.run(["git", "diff", "--name-only", "HEAD"], capture_output=True, text=True)
print(f"Dirty files after rollback: {dirty.stdout or '(none)'}")
```

Expected: HEAD matches BASELINE_HASH. Dirty files = only pre-existing baseline dirty files.

---

## Step 4 — Document Rollback in Evidence

```markdown
## ROLLBACK_EXECUTED

- Trigger: <which criterion failed>
- Rollback command: `git reset --hard <BASELINE_HASH>`
- HEAD before rollback: <hash>
- HEAD after rollback: <BASELINE_HASH>
- Dirty files after rollback: <list or "none">
- Rollback successful: YES / NO
```

---

## Step 5 — STOP. Produce Phase Revision.

After rollback:
- Do NOT proceed to next phase
- Do NOT retry the same phase immediately
- Produce a Phase Revision document identifying:
  1. Root cause of failure
  2. Changes needed to the approach
  3. Revised acceptance criteria
  4. New scope declaration

Only resume after Phase Revision is reviewed and accepted.

---

## Hard Rules

- **NO partial commits.** Ever. If any criterion fails, full rollback.
- **NO forward-fixing.** Rolling forward to fix a broken phase makes future rollback harder.
- **Rollback command MUST use the BASELINE_HASH**, not HEAD~1 or any relative ref.
- **If git reset --hard fails** (e.g., merge in progress) → STOP, escalate to user immediately.
