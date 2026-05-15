# Gate Evidence Template

Copy-paste templates for gate documentation in evidence files.

## Rollback Checkpoint

```
## ROLLBACK_CHECKPOINT
**Checkpoint ID**: CHK-<YYYYMMDD>-001
**Files to modify**: N
**Scope justification**: <one sentence>
**Baseline commit**: <hash>
**Checkpoint created**: <ISO timestamp>
**Recovery commands**:
  git checkout --force <hash>
```

## MCP Tool Validation

```
## MCP_TOOL_VALIDATION
**Tool**: <tool_name>
**Parameters validated**: <list param: type>
**Validation result**: ✅ PASS
**Source**: system prompt tool schema
```

## Phase Gate Result

```
## PHASE_GATE
**Phase**: <name>
**Gate 1 — Rollback checkpoint**: ✅ PASS
**Gate 2 — MCP validation**: ✅ PASS
**Gate 3 — Dependency graph**: ✅ PASS
**Gate 4 — Scope declared**: ✅ PASS
**Gate 5 — Test requirements**: ✅ PASS
**Overall**: ✅ PROCEED
```

## Gate Failure

```
## GATE_FAILURE
**Failed gate**: <gate name and number>
**Error**: <specific error message>
**Recovery executed**: ✅ SUCCESS / ❌ FAILED
**Root cause**: <brief>
**Prevention**: <what was changed to prevent recurrence>
```
