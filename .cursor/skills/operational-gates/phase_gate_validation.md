# Phase Gate Validation

## Pre-Phase Gate Checklist

Before starting any multi-file phase:

1. [ ] Rollback checkpoint created and validated (`rollback_checkpoint_protocol.md`)
2. [ ] All MCP tools validated for planned usage (`mcp_tool_validation_checklist.md`)
3. [ ] Dependency graph analysis completed (graph-analysis skill)
4. [ ] Scope declared and justified in evidence
5. [ ] Test requirements identified
6. [ ] Environmental contracts verified (if applicable)

## Gate Failure Response

If any gate fails:
1. STOP phase execution immediately
2. Execute rollback to last valid checkpoint
3. Document the specific gate that failed in evidence
4. Analyze root cause
5. Plan recovery before retrying the phase

## Evidence Format

```
## PHASE_GATE
**Phase**: <name>
**Gate 1 — Rollback checkpoint**: PASS / FAIL
**Gate 2 — MCP validation**: PASS / FAIL
**Gate 3 — Dependency graph**: PASS / FAIL
**Gate 4 — Scope declared**: PASS / FAIL
**Gate 5 — Test requirements**: PASS / FAIL
**Overall**: PASS → proceed / FAIL → stop
```
