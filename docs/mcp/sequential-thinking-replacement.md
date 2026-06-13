# Sequential Thinking MCP - Retirement & Replacement

**Status**: RETIRED (2026-04-07)
**Current replacement**: Claude Code native plan mode plus the `structured-reasoning` skill for
decomposition and retrieval discipline.
**Skill**: `.claude/skills/structured-reasoning/SKILL.md`
**Rule**: `.claude/rules/plan-first-enforcement.md`

`structured-reasoning` is not the old MCP. The old MCP was the
`@modelcontextprotocol/server-sequential-thinking` package and its `sequentialthinking` tool.

---

## Why Sequential Thinking Was Retired

Confirmed findings:

1. **stdio transport fragility on Windows** - The MCP used Node.js stdio transport. In Windows
   subprocess contexts, `npx` resolution was fragile unless routed through `npx.cmd` or a hardcoded
   `node.exe` path.
2. **Zombie node.exe processes** - Hangs left orphaned Node processes that blocked later starts.
3. **Over-configuration** - Prior config attempts added environment variables that were not part of
   the published MCP protocol.
4. **Suppressed diagnostics** - `DISABLE_THOUGHT_LOGGING=true` removed useful failure signal.
5. **Architectural mismatch** - A reasoning MCP added latency and failure modes on top of a model that
   already performs native reasoning.

Operationally, the dedicated reasoning MCP was the wrong abstraction. Plan-first behavior belongs in
the agent contract, not in a tool server.

---

## Current Contract

For T2/T3 work:

1. Enter native plan mode.
2. Normalize objective, constraints, assumptions, tier, and touched surfaces.
3. Gather evidence with read/query tools only.
4. Present a numbered plan for approval.
5. Make no edits until the plan is approved.
6. Execute step by step.
7. Verify with tests, health checks, and diff review.

The `structured-reasoning` skill remains useful for:

- decomposition shape
- evidence ordering
- branch handling
- revision discipline
- verification summaries

It must not be used as a marker-emission workflow. The old SR marker packet was retired by
`claude-native-supersession-9d3f7a` / ADR-094 because native plan mode now provides the approval gate.

---

## Replacement Mapping

| Capability | Old Sequential Thinking MCP | Current replacement |
|------------|-----------------------------|---------------------|
| Task decomposition | `sequentialthinking` tool call | Native plan mode, optionally guided by `structured-reasoning` |
| Ordered reasoning | MCP thought chain | Numbered plan in plan mode |
| Revision | MCP internal state | Re-present changed plan steps with the evidence reason |
| Branching under uncertainty | MCP branch parameter | Branch point text plus Author-Gate / `AskUserQuestion` when genuinely ambiguous |
| Tool selection | MCP output | "Tools needed" in the plan |
| Execution gate | MCP-controlled gate | Native plan approval |

`task_manager` is only for durable, queryable task state across sessions. It is not required for
ordinary in-session decomposition.

---

## Failure Handling

If old logs, docs, or code mention `sequentialthinking`, treat that as a stale retired-MCP reference.
Do not attempt to recover the old MCP. Update the reference to native plan mode with
`structured-reasoning` as guidance.

If an active MCP needed for evidence is unavailable, use `/mcp-failure-rca` or the documented fallback
for that MCP. Do not substitute grep for ADG structural dependency evidence.

---

## What Was Not Replaced

The Sequential Thinking MCP was never responsible for:

- file reads
- code execution
- test running
- git operations

It only attempted to externalize "thinking about what to do." That capability now lives in the
Claude Code operating contract and the plan-first governance rule.
