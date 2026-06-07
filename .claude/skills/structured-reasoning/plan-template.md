# Structured Reasoning — Plan Template

Copy-paste this at the start of any T2/T3 task.

> **MCP tool-name note:** Tool names below use the stable server-name style. In Claude Code the live tool id is `mcp__<server>__<tool>` (e.g. `adg_health` on server `adg_sqlite` → `mcp__adg_sqlite__adg_health`).

---

```
## SR_INTAKE
Objective: 
Constraints:
  - 
Assumptions:
  - 
Tier: T2 | T3
Complexity: simple | medium | complex

## SR_PLAN
1. Call adg_health (server: adg_sqlite) — confirm ADG MCP is healthy
2. Call mem_recall_session_start (server: memory) — load session context
3. 
4. 
5. 
N. Verification: run scoped tests / check git diff / confirm no layer violations

Tools needed:
  - adg_health (server: adg_sqlite)
  - mem_recall_session_start (server: memory)
  - create_task (server: task_manager)
  - 

Missing information:
  - 

Risks / stop conditions:
  - 
```

---

## Branch Point Template (use when uncertain)

```
BRANCH POINT — Step N:
  Plan A: <approach> — use if <condition from evidence>
  Plan B: <approach> — use if <condition from evidence>
  Plan C: <approach> — use if <condition from evidence>
  [Selecting after evidence pull in Phase C]
```

---

## Revision Template (use after evidence changes the plan)

```
## SR_PLAN_v2
Revision reason: <what evidence changed>
Changed steps: N, M
1. [unchanged]
2. [revised step — what changed and why]
...
```
