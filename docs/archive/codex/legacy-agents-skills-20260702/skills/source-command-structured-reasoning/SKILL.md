---
name: "source-command-structured-reasoning"
description: "Thin alias \u2014 T2/T3 plan-first reasoning (/structured-reasoning)"
---

# source-command-structured-reasoning

Use this skill when the user asks to run the migrated source command `structured-reasoning`.

## Command Template

# /structured-reasoning

**Tier:** Workflow alias only — not policy.

## Authority map

| Layer | SSOT |
|-------|------|
| On-demand invariant | [plan-first-enforcement.md](../rules/plan-first-enforcement.md) |
| Procedure (full phases) | [structured-reasoning/SKILL.md](../skills/structured-reasoning/SKILL.md) |
| Templates | `structured-reasoning/plan-template.md`, `verification-template.md`, `failure-template.md` |

## Invocation steps

1. Enter native plan mode for T2/T3 work — **no edits** before plan approval.
2. Pull evidence with reads/ADG only; revise and re-present the plan if needed.
3. Execute approved steps; verify with tests, health checks, and diff review.
4. Branch decisions → Author-Gate via `/author-gate-decision-gate` when genuinely ambiguous.

⛔ Do not duplicate phase bodies here — follow the skill.

## MANUAL MIGRATION REQUIRED

Migrated from source command `structured-reasoning` into a Codex skill. Invoke it as `$source-command-structured-reasoning` and manually rewrite any slash-command behavior that depended on provider-specific runtime expansion.
