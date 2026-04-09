# Structured Reasoning — Pre-Execution Gate Checklist

Copy this checklist and complete every item before executing Phase E.

```
## SR_PRE_EXECUTION_GATE
Task: <task title>
Date: <ISO timestamp>

REASONING LAYER
[ ] SR_INTAKE block emitted (objective, constraints, assumptions, tier)
[ ] SR_PLAN emitted with numbered steps
[ ] All branch points identified and labeled
[ ] Revision cycle complete (if evidence changed the plan)

ROUTING LAYER
[ ] mcp1_adg_health called — result: OK | DEGRADED | FAILED
[ ] mcp5_mem_recall_session_start called — result: OK | UNAVAILABLE
[ ] mcp13_create_task created — task ID: <id>
[ ] All required MCPs identified and confirmed healthy (or fallback documented)

EVIDENCE LAYER
[ ] All relevant files read (no assumptions about file contents)
[ ] ADG fanout/fanin queried for cross-file changes
[ ] Blast radius confirmed: <N files>
[ ] Constitutional constraints checked (layer boundaries, no PowerShell, no broad except)
[ ] No weak evidence remaining (or CLARIFY/ABSTAIN selected)

PLAN VALIDATION
[ ] SR_APPROVAL emitted: APPROVED | REVISED (with re-approval) | CLARIFY | ABSTAIN
[ ] If REVISED: SR_PLAN_v2 emitted and re-validated

EXECUTION READINESS
[ ] git status checked — working directory clean (or changes understood)
[ ] Rollback path identified: <git reset command or N/A>
[ ] Scoped tests identified: <pytest path>
[ ] No edits made yet

--- GATE PASSED — safe to proceed to Phase E ---
```
