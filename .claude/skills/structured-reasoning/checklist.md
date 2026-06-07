# Structured Reasoning — Pre-Execution Gate Checklist

Copy this checklist and complete every item before executing Phase E.

> **MCP tool-name note:** Tool names below use the stable server-name style. In Claude Code the live tool id is `mcp__<server>__<tool>` (e.g. `adg_health` on server `adg_sqlite` → `mcp__adg_sqlite__adg_health`).

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
[ ] adg_health (server: adg_sqlite) called — result: OK | DEGRADED | FAILED
[ ] mem_recall_session_start (server: memory) called — result: OK | UNAVAILABLE
[ ] create_task (server: task_manager) created — task ID: <id>
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
