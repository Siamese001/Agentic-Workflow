# Structured Reasoning - Pre-Execution Gate Checklist

Copy this checklist while in native plan mode before executing a T2/T3 task.

> **MCP tool-name note:** Tool names below use the stable server-name style. In Claude Code the live
> tool id is `mcp__<server>__<tool>` when that MCP is available.

```
## PRE_EXECUTION_GATE
Task: <task title>
Date: <ISO timestamp>

REASONING LAYER
[ ] Objective, constraints, assumptions, tier, and touched surfaces stated
[ ] Numbered plan presented for approval
[ ] All branch points identified and labeled
[ ] Revision cycle complete if evidence changed the plan

ROUTING LAYER
[ ] adg_health (server: adg_sqlite) called when structural evidence matters, or documented fallback used
[ ] memory context checked when durable precedent matters, or marked unnecessary
[ ] Durable task tracking skipped unless the user explicitly requested it
[ ] Required tools identified and confirmed healthy, or fallback documented

EVIDENCE LAYER
[ ] All relevant files read; no assumptions about file contents
[ ] ADG fanout/fanin queried for cross-file changes when available
[ ] Blast radius confirmed: <N files>
[ ] Constitutional constraints checked
[ ] No weak evidence remains, or the plan is revised / clarified / abstained

PLAN VALIDATION
[ ] User approved execution, or the user already explicitly requested implementation
[ ] If revised: changed steps re-presented and approved

EXECUTION READINESS
[ ] git status checked; working directory is clean or existing changes are understood
[ ] Rollback path identified: <git restore/revert command or N/A>
[ ] Scoped verification identified: <command>
[ ] No edits made yet

--- GATE PASSED - safe to proceed to execution ---
```
