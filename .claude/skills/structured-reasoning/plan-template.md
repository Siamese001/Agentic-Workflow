# Structured Reasoning - Plan-Mode Template

Use this inside native plan mode for T2/T3 work.

> **MCP tool-name note:** Tool names below use the stable server-name style. In Claude Code the live
> tool id is `mcp__<server>__<tool>` when that MCP is available.

---

```
Objective:
Constraints:
  -
Assumptions:
  -
Tier: T2 | T3
Touched surfaces:
  -

Plan:
1. Gather/read evidence:
2. Confirm blast radius and stop conditions:
3. Apply the scoped change:
4. Verify:

Tools needed:
  - <tool or repo script>: <why>

Missing information:
  - NONE | <specific gap>

Risks / stop conditions:
  - <risk>
```

---

## Branch Point Template

Use when evidence could support multiple approaches.

```
BRANCH POINT - Step N:
  Plan A: <approach> - use if <condition from evidence>
  Plan B: <approach> - use if <condition from evidence>
  Plan C: <approach> - use if <condition from evidence>
  Selecting after evidence pull.
```

---

## Revision Template

Use after evidence changes the plan.

```
Revision reason: <what evidence changed>
Changed steps: N, M
1. [unchanged]
2. [revised step - what changed and why]
...
```
