# Structured Reasoning — Plan Template

Copy-paste this at the start of any T2/T3 task.

> **MCP prefix note:** Tool names below use stable server-name style. Resolve the live numeric prefix from the tool list visible in your session (e.g. `adg_health` → `mcp1_adg_health` if `adg_sqlite` loads at position 1).

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
