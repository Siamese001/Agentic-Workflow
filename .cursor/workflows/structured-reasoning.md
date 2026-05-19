---
description: Thin alias — T2/T3 plan-first reasoning (/structured-reasoning)
---

# /structured-reasoning

**Tier:** Workflow alias only — not policy.

## Authority map

| Layer | SSOT |
|-------|------|
| On-demand invariant | [sequential-thinking-enforcement.mdc](../rules/sequential-thinking-enforcement.mdc) |
| Procedure (full phases) | [structured-reasoning/SKILL.md](../skills/structured-reasoning/SKILL.md) |
| Templates | `structured-reasoning/plan-template.md`, `verification-template.md`, `failure-template.md` |

## Invocation steps

1. Emit `SR_INTAKE` then `SR_PLAN` — **no edits** until `SR_APPROVAL: APPROVED`.
2. Evidence pull (reads/ADG only); revise plan if needed.
3. Execute approved steps; emit `SR_EXECUTE` / `SR_VERIFY` inline.
4. Branch decisions → Author-Gate via `/author-gate-decision-gate` when genuinely ambiguous.

⛔ Do not duplicate phase bodies here — follow the skill.
