---
name: task-manager-mcp
description: Structured task decomposition, status tracking, and lessons-learned capture via the in-house task_manager MCP server. Invoke ONLY when the user explicitly requests tracked multi-step work — "track this as tasks", "decompose this into subtasks", "create a task for X". Do NOT auto-invoke for ordinary multi-step work; that's what the structured-reasoning skill (SR_PLAN/SR_EXECUTE) is for. The task manager is for durable, queryable task state across sessions.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
  deprecated: true
  redirect_to: mcp-integration
---

# ⚠️ DEPRECATED — Redirected to mcp-integration §13

> **Consolidated**: This skill content moved to `mcp-integration/SKILL.md` §13 — Task Manager MCP (2026-05-12, W4.P2).
> **Status**: Redirect stub — preserved for backwards compatibility.
> **Action**: Consult `.cursor/skills/mcp-integration/SKILL.md` §13 for current guidance.

---

# Task Manager MCP Skill (Legacy)

In-house. **Selective use only.** This MCP is for durable, queryable task state — not for ordinary planning.

**Sibling skill:** `structured-reasoning` (the default planner — SR_INTAKE → SR_PLAN → SR_EXECUTE — for in-session work)

## When To Use This MCP

| User intent | Use task_manager? |
|---|---|
| "Track this as tasks" / "create a task" | ✅ Yes |
| "Decompose into subtasks" / "what's left to do" across sessions | ✅ Yes |
| Long-horizon multi-session epic with explicit task tracking | ✅ Yes |
| In-session multi-step work | ❌ No | `structured-reasoning` skill (SR_PLAN) |
| Plan-file work | ❌ No | `.cursor/plans/<name>-<6hex>.md` |

## Tool Routing

| Goal | Tool |
|---|---|
| Create a new task | `create_task` |
| Decompose complex task into subtasks | `decompose_task` |
| Get task details | `task_info` |
| Update status / properties | `update_task` |

## Hard Rules

1. **Decomposition is mandatory before execution** for any task with `estimatedComplexity` above `low`. (`decompose_task` first, then update + execute subtasks.)
2. **Status discipline:** `update_task` to `in-progress` before executing, to `done`/`failed` when finished. Always include `lessonsLearned` on completion.
3. **Parallelizable subtasks share the same `sequenceOrder`.** Sequential subtasks increment.
5. **Don't replicate plan-file content.** Plans are SSOT in `.cursor/plans/`. Tasks are queryable handles, not narrative.

## Common Workflows

**Track a multi-session epic:**
1. `create_task(title='X', estimatedComplexity={level: 'high, must decompose...', ...})`
2. `decompose_task(taskID=..., subtasks=[...])` — sequenced subtasks with verification subtask at end
3. Per subtask: `update_task(status='in-progress')` → execute → `update_task(status='done', add: {lessonsLearned: [...], verificationEvidence: [...]})`

## When NOT To Use

- For one-off responses with 3-step plans → use `structured-reasoning` SR_PLAN inline.
- For tracking refactor waves → use a `.cursor/plans/<name>-<6hex>.md` file with wave/phase tables.
- For TODO comments in code → use `# TODO:` markers and a `DEFERRED_SCOPE:` marker if the deferral is significant.
