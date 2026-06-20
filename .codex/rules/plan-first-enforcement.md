# Plan-First Enforcement (native plan mode)

> **Renamed W2 (`claude-native-supersession-9d3f7a`).** Formerly `sequential-thinking-enforcement.md`
> — that name came from a defunct legacy-IDE "Sequential Thinking" MCP that never worked; the rule
> was goal-seeked to reimplement its *intent*. The real scope is **plan-first reasoning**: on T2/T3
> work, decompose and gather evidence, and make **no edits before the plan is approved** (native plan
> mode). Renamed to match scope.

> Superseded W2 (`claude-native-supersession-9d3f7a`, ADR-094): the `SR_INTAKE / SR_PLAN /
> SR_APPROVAL / SR_EXECUTE / SR_VERIFY` marker packet is retired. Native **plan mode** is the
> "no edits before approval" contract it emulated.

## When plan mode is required

MANDATORY for **T2/T3** tasks: planning / decomposition, architecture decisions, multi-file debugging,
refactors spanning files, ADG / dependency analysis, test-strategy design. NOT required for T0/T1
(question, typo, single config value, single import).

## Contract

- T2/T3 ⇒ `EnterPlanMode`, gather evidence (reads only), present the plan via `ExitPlanMode`, and make
  **no edits until the plan is approved**.
- T0/T1 ⇒ proceed directly.

## Retrieval discipline at T2/T3 (unchanged)

Before synthesis, pull evidence in this order: local repo guidance + nearby docs → exact files /
symbols / commands / config values → ADG / structured MCP for dependency, blast-radius, runtime
questions → semantic retrieval only when exact lookup leaves gaps → external research only when local
evidence is insufficient. Facts first, synthesis second.

## Anti-patterns (forbidden)

Plan-mode theatre for trivial T0/T1 work; stalling before a simple question; retrying a hung tool in a
loop. If an MCP hangs: STOP, note `[MCP UNAVAILABLE]`, proceed without it.
