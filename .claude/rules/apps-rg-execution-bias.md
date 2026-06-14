# apps_rg Execution Bias — Standing Orders (Operating Model 2026-06-10)

> ⛔ Adopted 2026-06-10 after the operating-model review (145 plans / 119 "Completed" / 0 product
> shipped in 3 weeks). The agent system is a mode-faithful amplifier; these orders set its default
> mode to EXECUTION. They apply to every session touching apps_rg.

## North star

**The only success metric until achieved: AIG resume, 11/11 lanes X3_ALLOW, assembled DOCX in hand.**
Nothing else counts as progress until it exists. After first ship: W0 Contract Matrix, then the
single backlog at budgeted pace.

## The six standing orders

1. **Execute, don't plan.** Work existing wave items of the active plan. Do NOT create plan files.
   Plan creation requires explicit user authorization in the same turn (mechanically enforced by
   `pre_write_plan_mint_gate.py` — set `PLAN_MINT_OK=1` only when the user authorized a plan).
2. **Findings become rows, not plans.** Gaps/ideas append to the single backlog — the Master Gap
   Inventory in `plans/apps-rg-lane-aggregation-gap-closure-b8c3d1.md` — never to new documents.
3. **WIP limit = 1 active plan, one owner session.** Before starting apps_rg write-work, confirm no
   other session is mid-stream on the same plan; if one is active, queue — do not run beside it.
   (Plan status is disk-only now — the Notion plan-status enforcement was removed.)
4. **Discovery budget ~20%, post-increment only.** No new analysis lenses until the active wave
   ships. Audits are time-boxed and emit inventory rows.
5. **Subtraction before addition.** A change adding gates/receipts must consolidate at least as
   much enumerated machinery as it adds.
6. **Receipts over proposals.** The weekly heartbeat E2E lane matrix + backlog delta is the only
   status artifact. Report what ran and what the receipts show, not what could be planned.

## Forbidden (the reflexes this rule retires)

- "I found a gap → write a plan" (the factory). Append a row instead and say so.
- Starting apps_rg write-work while another plan is In Progress (RC3 collision class:
  same-day supersessions, mutual reverts — both observed 2026-06-10).
- Completing "plans" as a success metric. Plan completion ≠ product delivery.

## References

- Memory: `apps-rg-operating-model-standing-orders` (adoption record + rationale)
- Single backlog: `plans/apps-rg-lane-aggregation-gap-closure-b8c3d1.md` (43-gap Master Inventory)
- Enforcement: `.claude/hooks/pre_write_plan_mint_gate.py` (PreToolUse on Write|Edit|MultiEdit)
