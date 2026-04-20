---
trigger: model_decision
description: Use this rule when a T2/T3 task requires structured reasoning — planning, architecture decisions, multi-file debugging, or systematic decomposition before execution.
---

> **Claude always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries, routing cues, and non-negotiable standards here. Move long procedures, examples, templates, and execution playbooks into skills or workflows.
>
> **Claude retrieval discipline:** When this rule affects research or synthesis, prefer local-first retrieval, exact or structural matches before broad semantic search, and evidence or quote extraction before final synthesis on high-risk tasks.
>
> **Claude enforcement split:** Advisory guidance lives here, but deterministic blocking, fail-closed checks, and audit capture belong in hooks and scripts rather than prompt prose.

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


## Retrieval Discipline at T2/T3

Before synthesis, pull evidence in this order unless the task clearly requires a different path:
- local repo guidance and nearby docs
- exact files, symbols, commands, and config values
- ADG / structured MCP tools for dependency, blast-radius, and runtime questions
- semantic retrieval only when exact lookup leaves meaningful gaps
- external research only when local evidence is insufficient or stale

For dense evidence tasks, facts first and synthesis second.

## Required Pattern at T2/T3 Start

Emit the full 4-phase packet across the task lifecycle:

    ## SR_INTAKE
    Objective: <one sentence>
    Constraints: [list]
    Assumptions: [list]
    Tier: T2 | T3

    ## SR_PLAN
    1. [verb-first step]
    ...
    N. [verification step]

    Tools needed: [list]
    Risks: [list]

    ## SR_EXECUTE
    - inspect
    - diagnose
    - act

    ## SR_VERIFY
    - what was checked
    - what passed
    - what remains unresolved

Emit SR_INTAKE + SR_PLAN before any tool calls. Then gather evidence (reads only). Emit `SR_APPROVAL: APPROVED` before any writes or edits. SR_EXECUTE and SR_VERIFY are emitted inline during and after the execute phase.

Use Task Manager MCP for decomposition when tasks have multiple sequential steps.

## Rules

- keep assumptions explicit
- front-load exact scope
- sequence work before editing
- use bounded phases for complex work
- do not turn the packet into a novel

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
