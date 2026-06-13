<!-- Trigger: model_decision (load when about to orchestrate sub-agents / workflows).
     The invariant is mirrored always-on in CLAUDE.md § Agent fan-out restraint. -->

# Agent / Workflow Fan-Out Restraint — Spawn Agents Only When Needed

> ⛔ Sub-agents (Workflow fan-out, `Agent`, `Task`) cost large token volumes — often
> **millions of tokens** per run. Spawning them is justified by the **work's need**, never by
> the effort tier. `max`, `ultracode`, and `/code-review … ultra` raise **depth and rigor**;
> they do **not** mandate spinning up numerous agents. When a detailed implementation plan or
> prior results already establish the facts, **execute and produce outputs** — do not re-run
> inventory/discovery through agents.

## When this fires

Any time you are about to call `Workflow`, `Agent`, or `Task` — **especially under `ultracode`**
(which otherwise defaults to "author and run a workflow for every substantive task") or a high
`/code-review` effort tier, where unneeded fan-out concentrates.

## Fan out ONLY when the work genuinely needs it

| Justified | Why |
|---|---|
| Independent, parallelizable subtasks | Real wall-clock / comprehensiveness win one context can't get |
| Scale beyond one context | Migration / audit / sweep too large to hold inline |
| Adversarial / independent verification | High-stakes findings need a skeptic, not an echo |
| Breadth sweep where you only need the conclusion | `Explore`-style fan-out that returns the answer, not file dumps |

## Do NOT fan out to…

| Anti-pattern | Do instead |
|---|---|
| Re-discover / re-map a codebase already understood | Use the ADG, the existing map, or prior-turn results |
| Re-run inventory/discovery a **detailed plan already provides** | Execute the plan; produce the outputs |
| "Look thorough" because the effort tier is high | Raise rigor inline; **depth ≠ agent count** |
| A single-fact lookup you could do directly | Read the file / run the one query yourself |
| Sequential, coherent authoring with no independent parts | Do it inline (this very rule was authored that way) |

## Effort tiers ≠ agent count

`max` / `ultracode` / `ultra` change **how well**, not **how many**. Scale agent count to the
task, not to the budget — prefer the **fewest agents that cover the work**. A detailed plan in
hand means discovery is already done: spend the budget on **execution + verification of the
outputs**, not on rediscovery. The Workflow contract says the same — "ONLY call when explicitly
opted in" and "**Scale to what the user asked for**."

## Enforcement

- **Doctrine (primary lever):** this rule + the always-on summary in `CLAUDE.md` shape the
  decision at the point of orchestration. This is what actually governs the choice.
- **Deterministic backstop:** `.claude/hooks/pre_workflow_fanout_gate.py` (PreToolUse on
  `Workflow`) inspects the inline script; when it reads as **high-scale AND
  discovery/inventory-dominant** (the costly rediscovery anti-pattern) it surfaces a confirm so
  an unneeded mass fan-out does not run silently. **Conservative by design** — verification,
  migration, parallel-implementation, and judge-panel workflows carry justification signals and
  pass untouched; single agents, small fan-outs, and `scriptPath`/named re-runs are never
  flagged. Logs to `artifacts/governance/agent_fanout_restraint.jsonl`.
- **Modes:** `FANOUT_RESTRAINT_ENFORCE=ask|warn|block` (default `ask`). **Bypass:**
  `FANOUT_RESTRAINT_BYPASS=1` (scripted/batch runs, or a fan-out you have already justified).
- `Agent` / `Task` restraint is **doctrine-enforced** (model-read); `Workflow` (the mass-fan-out
  surface where most token burn concentrates) is **also hook-backstopped**.

## References

- `.claude/rules/001-cursor-runtime-seam-execution.md` — bounded L2 executor; avoid multi-wave unless explicitly asked
- `.claude/rules/scope-containment.md` — retrieval budgets; no gold-plating; one task at a time
- `.claude/rules/work-item-classification.md` — tier-aware Fix / File / Plan; `PLAN_MICRO` = native plan mode only
- Workflow tool contract — opt-in only; scale to the ask; pipeline/parallel patterns are tools, not defaults
