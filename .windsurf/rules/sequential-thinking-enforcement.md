---
trigger: always_on
---
# Structured Reasoning & Task Management Enforcement Rule

**Layer**: Windsurf (AI-time behavioral)
**Type**: Behavioural
**Priority**: High

**NOTE**: This rule replaces the previous sequential-thinking enforcement. As of 2026-04-07, the sequential-thinking MCP has been replaced with concrete capability MCPs (Playwright, Task Manager) per architectural guidance. Cascade now uses its native reasoning capabilities combined with task management tools instead of a fragile meta-reasoning loop.

---

## §SR-0: Core Principle

**For all T2/T3 tasks (multi-file, architecture, planning, debugging), Cascade MUST use structured reasoning and task management tools before proceeding with the actual work.**

Structured reasoning is now provided by:
- **Cascade native reasoning** - The model's inherent problem-solving capabilities
- **Task Manager MCP (task_manager)** - For task decomposition, step tracking, and progress preservation
- **Memory MCP (mcp6)** - For session context recall at task start (`mcp5_mem_recall_session_start`)
- **Filesystem MCP (mcp7)** - For file reads and codebase navigation
- **Git MCP (mcp0)** - For version control operations

This approach is more reliable than a pure "reasoning MCP" because each server does one concrete job well, and Cascade's native reasoning is more robust than forcing all reasoning through a separate abstraction layer.

---

## §SR-1: When Structured Reasoning is REQUIRED

**MANDATORY for T2/T3 tasks:**

- **Planning phases** — creating execution plans, wave breakdowns, task decomposition
- **Architecture decisions** — design choices, layer placement, technology selection
- **Debugging complex issues** — multi-file bugs, state bugs, integration failures
- **Refactoring** — structural changes affecting multiple files
- **Analysis tasks** — ADG graph analysis, dependency tracing, impact assessment
- **Test strategy** — designing test suites, coverage planning, test architecture
- **Multi-step reasoning** — any task requiring systematic decomposition

**Tier reference:** See `.windsurf/rules/constitutional.md` §0 DEFAULT ANALYSIS MODE for T2/T3 classification:
- **T2 — Scoped**: 2–5 files, single layer
- **T3 — Architectural**: >5 files, cross-layer, governance, or new feature

---

## §SR-2: When Structured Reasoning is NOT Required

**EXEMPT for T0/T1 tasks:**

- **T0 — Question**: No code changes (explain, review, advise)
- **T1 — Trivial**: ≤1 file, ≤20 lines, obvious scope (typo, docstring, config value, add assertion)

**Examples of exempt tasks:**
- Fixing a typo in a string
- Adding a docstring
- Changing a single config value
- Adding a single import
- Formatting changes
- Simple variable rename within one file

---

## §SR-3: How to Invoke Structured Reasoning

**Full protocol**: invoke `/structured-reasoning` workflow (`.windsurf/workflows/structured-reasoning.md`) for the complete A→F sequence: Intake → Plan → Evidence → Approval → Execute → Summary.

**Required pattern at start of T2/T3 task:**

Use Task Manager MCP to create a structured task list:
```
mcp13_create_task(
  title: "Clear task title",
  description: "Clear task description",
  goal: "What must be true when this task is complete",
  criticalPath: true,
  definitionsOfDone: ["criterion 1", "criterion 2"],
  uncertaintyAreas: [],
  estimatedComplexity: {"level": "low, may benefit from decomposition before execution", "description": "brief complexity note"}
)
```

Then use Cascade's native reasoning to break down the task systematically, updating the task list as you progress.

**Guidance for task complexity:**
- Simple T2: 3–5 subtasks
- Complex T2: 5–10 subtasks
- T3 architectural: 10–20 subtasks

**HARD LIMITS — MANDATORY:**
- **Max task depth**: 3 levels of nesting
- **Max concurrent tasks**: 5 active tasks at once
- **Task updates**: Must update task status after each significant step
- **Task completion**: Mark tasks as complete when done, don't leave dangling tasks

---

## §SR-3.1: Tool Hang Recovery Protocol

**Symptom:** Any MCP tool call hangs indefinitely or returns an error.

**MANDATORY RESPONSE (in order):**

1. **STOP** — do not retry the same call
2. **Run `/mcp-failure-rca`** — appropriate step for the affected MCP
3. **If MCP cannot be restored** — proceed WITHOUT that tool for this task, note this in your response as `[MCP UNAVAILABLE — proceeding without tool]`
4. **NEVER** loop tool calls as a workaround for a hung call
5. **NEVER** default to grep or text search as a substitute for failed ADG MCP

**Tool hang ≠ permission to skip core requirements.** Use alternative approaches if a tool is unavailable.

---

## §SR-3.2: When NOT to Invoke (anti-patterns)

**FORBIDDEN usage patterns:**
- ❌ Creating tasks for trivial T0/T1 work
- ❌ Using task management as a stall tactic before responding to simple questions
- ❌ Creating excessive task nesting (>3 levels)
- ❌ Leaving tasks in "in_progress" state indefinitely
- ❌ Retrying a hung tool call in a loop

---

## §SR-4: Integration with Existing Rules

This rule complements but does not replace:
- **§0 DEFAULT ANALYSIS MODE** — still classify tier first, then apply this rule
- **§1 TESTING FRAMEWORK** — still require tests, use task management for test strategy design
- **§2 ADG FRAMEWORK** — still use ADG for scope, use task management for analysis approach
- **§HITL-0 HITL Enforcement** — still present options for decisions, use task management to track decision outcomes

---

## §SR-5: Enforcement

This is a **behavioral rule** enforced during AI execution. No pre-commit hook can verify compliance.

**Audit trail:** When task management is used, evidence files and plans should reference the task structure as part of the reasoning process.

**CI Health Gate:** `mcp_health_monitor.py` includes probes for all MCPs. If any probe fails:
1. Run `/mcp-failure-rca` — appropriate recovery step
2. **BLOCKED** — do not proceed with T2/T3 work until probe returns healthy
3. Document failure and recovery in `artifacts/adg/mcp_health_report.json`

---

## §SR-6: Quick Reference

| Task Type | Tier | Task Management Required? |
|---|---|---|
| Explain code | T0 | ❌ NO |
| Fix typo | T1 | ❌ NO |
| Add docstring | T1 | ❌ NO |
| Debug multi-file bug | T2 | ✅ YES |
| Refactor 3 files | T2 | ✅ YES |
| Plan architecture | T3 | ✅ YES |
| Design test strategy | T3 | ✅ YES |
| ADG graph analysis | T3 | ✅ YES |

---

## MAXIM

- **Concrete over abstract.** Use specific capability MCPs (Filesystem, Git, Playwright, Task Manager) instead of meta-reasoning tools.
- **Cascade does the thinking.** Trust the model's native reasoning capabilities; use tools for concrete operations, not as a crutch.
- **Track progress transparently.** Use task management to make multi-step work visible and trackable.
- **Fail gracefully.** If a tool is unavailable, adapt and continue using alternative approaches.
