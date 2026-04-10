---
trigger: model_decision
description: Use this rule when a T2/T3 task requires structured reasoning — planning, architecture decisions, multi-file debugging, or systematic decomposition before execution.
---
# Structured Reasoning Threshold


## When Structured Reasoning is Required

MANDATORY for T2/T3 tasks:
- Planning phases, wave breakdowns, task decomposition
- Architecture decisions — design choices, layer placement, technology selection
- Debugging multi-file bugs, state bugs, integration failures
- Refactoring — structural changes affecting multiple files
- Analysis tasks — ADG graph analysis, dependency tracing, impact assessment
- Test strategy — designing test suites, coverage planning
- Multi-step reasoning — any task requiring systematic decomposition

NOT required for T0/T1 tasks (question, typo, docstring, single config value, single import).

## Required Pattern at T2/T3 Start

Emit SR_INTAKE before any tool calls:

    ## SR_INTAKE
    Objective: <one sentence>
    Constraints: [list]
    Assumptions: [list]
    Tier: T2 | T3

    ## SR_PLAN
    1. [verb-first step]
    ...
    N. [verification step]

Then gather evidence (reads only). Then emit SR_APPROVAL: APPROVED before any writes or edits.

Use Task Manager MCP for decomposition when tasks have multiple sequential steps.

## Hard Limits

- Max task depth: 3 levels of nesting
- Max concurrent tasks: 5 active at once
- Mark tasks complete — do not leave dangling in-progress tasks
- If any MCP hangs: STOP, do not retry, note [MCP UNAVAILABLE], proceed without it

## Anti-Patterns (FORBIDDEN)

- Creating tasks for trivial T0/T1 work
- Using task management as a stall tactic before simple questions
- Retrying a hung tool call in a loop
- Exceeding 3 levels of task nesting
