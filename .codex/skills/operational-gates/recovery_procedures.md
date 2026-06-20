# Recovery Procedures

## Automatic Recovery

1. Detect gate failure during validation
2. Execute rollback to last valid checkpoint: `git checkout --force <baseline>`
3. Verify restoration: `git diff --name-only HEAD` returns empty
4. Log recovery with success/failure status in evidence
5. Stop — do not retry until root cause is understood

## Manual Recovery Steps

1. Identify failure point from evidence logs
2. List files that diverged from declared scope: `git diff --name-only HEAD`
3. Revert each unexpected file: `git checkout -- <file>`
4. Validate restoration: `git status` shows clean tree
5. Document manual recovery in evidence under `## MANUAL_RECOVERY`
6. Plan retry with corrected approach before proceeding

## Escalation Path

If automatic and manual recovery both fail:
1. STOP all work
2. Capture full `git status` and `git diff HEAD` output
3. Surface to user with a Author-Gate prompt describing the failure
4. Wait for explicit user instruction before any further edits

## Evidence Format

```
## RECOVERY_EXECUTED
**Recovery type**: automatic / manual
**Trigger**: <what gate failed>
**Commands executed**:
  git checkout --force <hash>
**Verification**: git diff clean = YES / NO
**Status**: SUCCESS / FAILED
**Root cause**: <brief description>
**Retry plan**: <what will be different>
```
