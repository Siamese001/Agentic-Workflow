# Rollback Checkpoint Protocol

Required before any phase that touches more than 3 files.

## Checkpoint Creation Steps

1. Verify `git diff --name-only HEAD` is empty (clean baseline)
2. Record the baseline commit hash: `git rev-parse HEAD`
3. Document exact files to be modified with graph justification
4. Write `## ROLLBACK_CHECKPOINT` to evidence file

## Evidence Format

```
## ROLLBACK_CHECKPOINT
**Checkpoint ID**: CHK-<YYYYMMDD>-<NNN>
**Files to modify**: N
**Scope justification**: <reason for multi-file operation>
**Baseline commit**: <git commit hash>
**Checkpoint created**: <ISO timestamp>
**Recovery commands**:
  git checkout --force <baseline_commit>
  git clean -fd
```

## Rollback Execution

When rollback is required:
1. STOP all edits immediately
2. Execute: `git checkout --force <baseline_commit>`
3. Verify: `git diff --name-only HEAD` is empty
4. Document in evidence under `## ROLLBACK_EXECUTED`
5. Analyze failure before retrying

## Validation Requirements

Every checkpoint MUST include:
- Clean working directory confirmation
- Exact list of files to be modified
- Baseline commit hash
- Recovery command that can be copy-pasted
