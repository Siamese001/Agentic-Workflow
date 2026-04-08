# Structured Reasoning — Plan Template

Copy-paste this at the start of any T2/T3 task.

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
1. Call mcp1_adg_health — confirm ADG MCP is healthy
2. Call mcp9_mem_recall_session_start — load session context
3. 
4. 
5. 
N. Verification: run scoped tests / check git diff / confirm no layer violations

Tools needed:
  - mcp1_adg_health
  - mcp9_mem_recall_session_start
  - mcp13_create_task
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
